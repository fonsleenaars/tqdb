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
        self.template = templates_by_path[self.get_template_path()]

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
                    parser_map[parser.get_template_path()] = parser()
                except TypeError:
                    # Skip TQDBParser itself (TypeError because of abstracts)
                    continue

    return parser_map


parsers = load_parsers()
