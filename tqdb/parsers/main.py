import abc
import inspect
import pkgutil

from importlib import import_module
from pathlib import Path


class TQDBParser(metaclass=abc.ABCMeta):
    """
    Abstract parser class.

    This abstract class is used to identify parsers that are used in TQDB
    and will ensure that the necessary methods are implemented.

    """
    @staticmethod
    def get_template_name():
        """
        Returns the template that this parser implements.

        """

    @classmethod
    def parse(cls, dbr, result):
        """
        Parses a specific DBR file and updates the result.

        """


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
                # Grab the name of the template this parser implements
                template_name = parser.get_template_name()

                if not template_name:
                    continue
                parser_map[template_name]: parser

    return parser_map


parsers = load_parsers()
