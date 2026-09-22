"""
Affixes: records that share a tag are one affix with one variant per record.

"""

import copy

from tqdb import dbr, main

MIGHT = "item/lootmagicalaffixes/prefix/default/character_might_"


def test_one_variant_per_record_ordered_by_level_then_record(fixture_data):
    affixes = main.parse_affixes()

    assert list(affixes["suffixes"]) == []
    assert list(affixes["prefixes"]) == ["tagPrefixMight"]

    might = affixes["prefixes"]["tagPrefixMight"]
    assert might["name"] == "Mighty"

    # Four records carry the tag: one variant each, ordered by level
    # requirement and then by record. _01 sorts first by path but not by
    # level; _03 and _04 differ only in their path and are not merged.
    assert might["variants"] == [
        {
            "record": MIGHT + "02",
            "levelRequirement": 5,
            "equipment": "armmelee,ring",
            "properties": {"characterStrength": "+5 Brawn"},
        },
        {
            "record": MIGHT + "01",
            "levelRequirement": 15,
            "equipment": "armmelee",
            "properties": {"characterStrength": "+10 Brawn"},
        },
        {
            "record": MIGHT + "03",
            "levelRequirement": 25,
            "equipment": "ring",
            "properties": {"characterDexterity": "+5 Finesse", "characterStrength": "+15 Brawn"},
        },
        {
            "record": MIGHT + "04",
            "levelRequirement": 25,
            "equipment": "ring",
            "properties": {"characterDexterity": "+5 Finesse", "characterStrength": "+15 Brawn"},
        },
    ]


def test_legacy_fields_are_projections_of_the_variants(fixture_data):
    might = main.parse_affixes()["prefixes"]["tagPrefixMight"]

    assert might["properties"] == [variant["properties"] for variant in might["variants"]]
    assert might["levelRequirement"] == 5
    assert might["equipment"] == "armmelee,ring"
    assert set(might) == {"name", "variants", "properties", "levelRequirement", "equipment"}


def test_collector_does_not_mutate_cached_records(fixture_data):
    record = fixture_data / "database/records" / (MIGHT + "01.dbr")
    before = copy.deepcopy(dbr.parse(record))

    main.parse_affixes()

    assert dbr.parse(record) == before
