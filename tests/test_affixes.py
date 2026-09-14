"""
Affixes: records that share a tag are one affix with alternative property sets.

"""
from tqdb import main


def test_affix_variants_accumulate_as_alternatives(fixture_data):
    affixes = main.parse_affixes()

    assert list(affixes["suffixes"]) == []
    assert list(affixes["prefixes"]) == ["tagPrefixMight"]

    might = affixes["prefixes"]["tagPrefixMight"]
    assert might["name"] == "Mighty"

    # Four records carry the tag. Their property sets accumulate in path
    # order; the fourth repeats the third's and collapses into it.
    assert might["properties"] == [
        {"characterStrength": "+5 Brawn"},
        {"characterStrength": "+10 Brawn"},
        {"characterDexterity": "+5 Finesse", "characterStrength": "+15 Brawn"},
    ]

    # Every other field comes from the first record in path order.
    assert might["levelRequirement"] == 5

    # Equipment is the union of the table types any variant is listed in.
    assert set(might["equipment"].split(",")) == {"armmelee", "ring"}
