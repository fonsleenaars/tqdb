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

    @abc.abstractstaticmethod
    def get_template_path():
        """
        Returns the template that this parser implements.

        """
        raise NotImplementedError

    @abc.abstractmethod
    def parse(self, dbr, result):
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

        return result


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


parsers = load_parsers()
