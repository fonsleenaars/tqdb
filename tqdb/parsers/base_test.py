"""
Coverage and functional tests for all the base parsers.

"""
import pytest

from tqdb.parsers import base
from tqdb.templates import templates_by_path


@pytest.fixture
def character_parser():
    return base.ParametersCharacterParser()


def test_character_template_variables(character_parser):
    """
    Test variable coverage for `parameters_character.tpl`.

    """
    # Grab the template to check variables for
    template = templates_by_path[character_parser.get_template_path()]

    # Iterate over the variables for this parser:
    missing = [
        variable
        for variable in template.keys()
        if variable not in character_parser.FIELDS]

    assert not missing
