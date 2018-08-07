"""
Main entry point for parsers, including the abstract base class.

"""
import abc
import inspect
import pkgutil

from importlib import import_module
from pathlib import Path

from tqdb.templates import templates_by_path


class TQDBParser(metaclass=abc.ABCMeta):
    """
    Abstract parser class.

    This abstract class is used to identify parsers that are used in TQDB
    and will ensure that the necessary methods are implemented.

    """
    # Base that all subclasses use for their template names.
    base = 'database\\templates'

    # Priority constants:
    HIGHEST_PRIORITY = 3
    DEFAULT_PRIORITY = 2
    LOWEST_PRIORITY = 1

    def __init__(self):
        """
        Initialize by setting the template based on its path.

        """
        templates = self.get_template_path()

        if isinstance(templates, list):
            # Load all templates
            self.template = [templates_by_path[t] for t in templates]
        else:
            # Just load the one template
            self.template = templates_by_path[templates]

    def get_priority(self):
        """
        Return the priority for this parser.

        A higher priority value means it will parse the contents earlier in the
        parser loop. If there are 3 parsers found for the template hierarchy,
        the first parser to run will be the one with the highest priority.

        This method is overriden by any subclass that needs to change their
        priority from the default DEFAULT_PRIORITY.

        """
        return self.DEFAULT_PRIORITY

    @abc.abstractstaticmethod
    def get_template_path():
        """
        Returns the template that this parser implements.

        """
        raise NotImplementedError

    @abc.abstractmethod
    def parse(self, dbr, dbr_file, result):
        """
        Parses a specific DBR file and updates the result.

        """
        raise NotImplementedError

    @staticmethod
    def extract_values(dbr, field, index):
        """
        Extract values for a specific field within a DBR.

        Some TQDBParser subclasses will need to iterate over an array of
        variables, all starting with a field name. However, some of these
        variables won't be repeated as many times as others.

        For example:
            offensiveSlowColdMin: [3.0, 6.0, 9.0, 12.0, 15.0]
            offensiveSlowColdDurationMin: [1.0]

        In this case, this index for the iteration should just clone the value
        until it matches the same length.

        """
        result = dbr.copy()

        # First grab all the fields that start with the field prefix:
        fields = dict(
            (k, v) for k, v in dbr.items()
            if k.startswith(field) and isinstance(v, list))

        # Now replace all the field values for this index
        for k, v in fields.items():
            result[k] = (
                # Grab the last possible value for v and repeat it:
                v[len(v) - 1]
                if index >= len(v)
                # Otherwise grab the value at this index:
                else v[index])

            # If this value turned out to be 0 or False, pop it:
            if not result[k]:
                result.pop(k)

        return result

    @staticmethod
    def highest_tier(dbr, properties):
        """
        Find the highest number of tiers within a list of fields.

        For a list of fields, find which field in the DBR has the most
        tiers (tiers are property values separated by semi-colons (;)).

        For example:
            offensiveSlowColdMin,12;13;14,
            offensiveCold,50;60,

        For this set of data, the highest number of tiers is 3.

        """
        fields = [dbr[p] for p in properties if p in dbr]

        return max((
            # If properties are lists, grab their length:
            len(field)
            if isinstance(field, list)
            # Regular properties just have a single tier:
            else 1
            for field in fields),
            # If there aren't any properties, default to 1
            default=1)

    @staticmethod
    def insert_value(field, value, result):
        """
        Insert a value for a parsed field in a DBR.

        The extract_values function in this class allows subclasses to parse
        over an array of values and this function inserts them into the result.

        If the extracted values only have one entry, the result can be inserted
        as text for the property. If the extracted value has more than one
        entry, the results will also be a list.

        For example:
            Input: offensiveSlowColdMin: [3.0]
            Parsed: offensiveSlowCold: 3 Cold Damage
            Output: offensiveSlowCold: 3 Cold Damage

            Input: offensiveSlowColdMin: [3.0, 6.0]
            Parsed: offensiveSlowCold: 6 Cold Damage
            Output: offensiveSlowCold: ['3 Cold Damage', '6 Cold Damage']

        """
        if field not in result['properties']:
            result['properties'][field] = value
            return

        current_field = result['properties'][field]
        if isinstance(current_field, list):
            result['properties'][field].append(value)
        else:
            result['properties'][field] = [current_field, value]


def load_parsers():
    """
    Load all parsers in this module that are subclasses of TQDBParser.

    """
    parser_map = {}

    # Run through all sibling modules
    for (_, name, _) in pkgutil.iter_modules([Path(__file__).parent]):
        # Import the module so we can check its variables, classes, etc.
        module = import_module(f'.{name}', package=__package__)

        for attribute in dir(module):
            parser = getattr(module, attribute)

            # Any subclass of TQDBParser is one that needs to be mapped:
            if inspect.isclass(parser) and issubclass(parser, TQDBParser):
                try:
                    instanced = parser()
                except TypeError:
                    # Skip TQDBParser itself (TypeError because of abstracts)
                    continue

                # Grab all the templates (can also be just one):
                templates = parser.get_template_path()

                if isinstance(templates, list):
                    # Insert all the templates this parser handles
                    parser_map.update(dict(
                        (template, instanced) for template in templates
                    ))
                else:
                    # Insert just the single template the parser handles:
                    parser_map[templates] = instanced

    return parser_map
