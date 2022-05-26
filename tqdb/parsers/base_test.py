"""
Coverage and functional tests for all the base parsers.

"""
from tqdb.parsers import base
from tqdb.templates import templates_by_path

# These fields are always allowed
GLOBAL_ALLOWED = [
    "ActorName",
    "Class",
    "FileDescription",
]


def is_allowed(field, allowed):
    """
    Check if a field is in the allowed list.

    This utility method used to compose lists that are checked.

    """
    return field in allowed or field in GLOBAL_ALLOWED


def is_suffixed(suffixes, field, allowed):
    """
    Check field for a suffix.

    Check if a field has a specific suffix where its base is in the allowed
    list.

    For example if the suffix is 'Modifier', the following situation is valid:

    field = 'characterStrengthModifier'
    allowed = ['characterStrength']

    Returns True

    """
    # If it's a simple string, check for a suffix
    if not isinstance(suffixes, list) and field.endswith(suffixes):
        return field[: -len(suffixes)] in allowed

    # Since there are multiple suffixes, track the combined result:
    result = False

    # If there are multiple suffixes to check, loop over them:
    for suffix in suffixes:
        if field.endswith(suffix):
            result = result or field[: -len(suffix)] in allowed

    # If any suffix was found to have a valid base field, the result will be
    # True, if none were found, it'll be False:
    return result


def test_character_template_variables():
    """
    Test variable coverage for `parameters_character.tpl`.

    """
    allowed = base.ParametersCharacterParser.FIELDS + [
        # Base attack speed (tag) is parsed manually
        "characterBaseAttackSpeed",
        "characterBaseAttackSpeedTag",
    ]

    def is_covered_variable(field):
        """
        Check if a character field is covered during parsing.

        """

        # Check for a regularly allowed field
        if is_allowed(field, allowed):
            return True

        # Check if it might be a modifier field:
        if is_suffixed("Modifier", field, allowed):
            return True

        return False

    # Grab the template to check variables for
    template = templates_by_path[base.ParametersCharacterParser.get_template_path()]

    # Iterate over the variables for this parser:
    missing = [variable for variable in template.variables.keys() if not is_covered_variable(variable)]

    assert not missing


def test_defensive_template_variables():
    """
    Test variable coverage for `parameters_defensive.tpl`.

    """
    allowed = base.ParametersDefensiveParser.FIELDS + [
        # The total speed resistance is parsed manually
        "defensiveTotalSpeedResistance",
        # The physical DOT is never used in
        "defensivePhysicalDurationChanceModifier",
    ]

    def is_covered_variable(field):
        """
        Check if a defensive field is covered during parsing.

        """
        # Check for a regularly allowed field
        if is_allowed(field, allowed):
            return True

        # Check if it might be an allowed suffixed field:
        return is_suffixed(["Modifier", "ModifierChance", "Chance"], field, base.ParametersDefensiveParser.FIELDS)

    # Grab the template to check variables for
    template = templates_by_path[base.ParametersDefensiveParser.get_template_path()]

    # Iterate over the variables for this parser:
    missing = [variable for variable in template.variables.keys() if not is_covered_variable(variable)]

    assert not missing


def test_augment_template_variables():
    """
    Test variable coverage for `itemskillaugments.tpl`.

    """
    allowed = (
        list(base.ItemSkillAugmentParser.SKILL_AUGMENTS.keys())
        + list(base.ItemSkillAugmentParser.SKILL_AUGMENTS.values())
        + [
            base.ItemSkillAugmentParser.AUGMENT_ALL,
            base.ItemSkillAugmentParser.SKILL_LEVEL,
            base.ItemSkillAugmentParser.SKILL_NAME,
            # This field isn't used in TQDB
            "itemSkillAutoController",
        ]
    )

    def is_covered_variable(field):
        """
        Check if a item skill augment field is covered during parsing.

        """
        # Check for a regularly allowed field
        return is_allowed(field, allowed)

    # Grab the template to check variables for
    template = templates_by_path[base.ItemSkillAugmentParser.get_template_path()]

    # Iterate over the variables for this parser:
    missing = [variable for variable in template.variables.keys() if not is_covered_variable(variable)]

    assert not missing


def test_offensive_template_variables():
    """
    Test variable coverage for `parameters_offensive/retaliation.tpl`

    """
    allowed = list(base.ParametersOffensiveParser.FIELDS.keys()) + [
        # Global retaliation and offensive chances are parsed manually:
        "offensiveGlobalChance",
        "retaliationGlobalChance",
        # Mana burn is parsed entirely manually
        "offensiveManaBurnDrainMin",
        "offensiveManaBurnDrainMax",
        "offensiveManaBurnDamageRatio",
        "offensiveManaBurnRatioAdder",
        "offensiveManaBurnRatioAdderChance",
    ]

    def is_covered_variable(field):
        """
        Check if an offensive/retaliation field is covered during parsing.

        """
        # Check for a regularly allowed field
        if is_allowed(field, allowed):
            return True

        # Check if it might be an allowed suffixed field:
        return is_suffixed(
            [
                "Chance",
                "DurationMax",
                "DurationMin",
                "DurationModifier",
                "Global",
                "GlobalChance",
                "Max",
                "Min",
                "Modifier",
                "ModifierChance",
                "XOR",
            ],
            field,
            base.ParametersOffensiveParser.FIELDS,
        )

    # Grab the template to check variables for
    template = templates_by_path[base.ParametersOffensiveParser.get_template_path()]

    # Iterate over the variables for this parser:
    missing = [variable for variable in template.variables.keys() if not is_covered_variable(variable)]

    assert not missing


def test_skill_template_variables():
    """
    Test variable coverage for `parameters_skill.tpl`.

    """
    allowed = base.ParametersSkillParser.FIELDS

    def is_covered_variable(field):
        """
        Check if a skill field is covered during parsing.

        """
        # Check for a regularly allowed field
        if is_allowed(field, allowed):
            return True

        # Check if it might be an allowed suffixed field:
        return is_suffixed(["Modifier", "ModifierChance", "Chance"], field, base.ParametersSkillParser.FIELDS)

    # Grab the template to check variables for
    template = templates_by_path[base.ParametersSkillParser.get_template_path()]

    # Iterate over the variables for this parser:
    missing = [variable for variable in template.variables.keys() if not is_covered_variable(variable)]

    assert not missing
