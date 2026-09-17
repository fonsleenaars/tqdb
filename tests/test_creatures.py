"""
Creatures: one entry per tag with a variant per record, the canonical record
chosen by level, and loot and chest unioned over the variants.

"""
import copy
import logging
from pathlib import Path

import pytest

from tqdb import dbr, main, storage
from tqdb.parsers import creatures

FIXTURE = "creature/monster/fixture/"
RECORDS = "database/records/"

# The fixture tag has no entry in the hand-maintained boss chest table, so
# the chest tests supply one.
CHESTS = {
    "tagMonsterFixture": [
        "",
        "records/item/containers/boss/fixture_epic.dbr",
        "records/item/containers/boss/fixture_legendary.dbr",
    ]
}


@pytest.fixture
def fixture_chests(monkeypatch):
    monkeypatch.setattr(creatures, "CHESTS", CHESTS)


def parsed(fixture_data, name):
    return dbr.parse(fixture_data / RECORDS / FIXTURE / f"{name}.dbr")


@pytest.mark.parametrize(
    "path",
    [
        "xpack4/creatures/monster/zz_dev/qa folder/banditchina_piratecaptain.dbr",
        "xpack4/creatures/monster/zz_dev/ancient_forest_48.dbr",
        "xpack/creatures/monster/zzdev/z_dev01.dbr",
        "xpack/creatures/monster/bosses/05_hades/old/boss_hades_50_old.dbr",
        "xpack4/creatures/monster/yaoguai/x4_sq401_monster_hero_yaoguaibrute_83_a_old.dbr",
        "xpack/creatures/monster/bosses/05_hades/credits_hades.dbr",
        "xpack/creatures/monster/ascacophus/credits_ringlesstree.dbr",
        "xpack/creatures/monster/bosses/05_hades/hades_test.dbr",
        "creature/monster/rumormonsters/egypt/qs_sandwraith_stuntdouble.dbr",
        # Scylla's records carry the Lernean Hydra's tag; the props in
        # Typhon's arena carry his.
        "xpack3/creatures/monster/bosses/xboss_scylla_49.dbr",
        "xpack3/creatures/monster/bosses/xboss_scylla_52.dbr",
        "xpack3/creatures/monster/bosses/xboss_scylla_55.dbr",
        "creature/monster/questbosses/typhon_bones.dbr",
        "creature/monster/questbosses/typhon_chains.dbr",
    ],
)
def test_development_and_shared_tag_records_are_excluded(path):
    assert main.creature_exclusion("/data/" + RECORDS + path)
    # The rule sees the record identity, whatever the spelling of the path.
    assert main.creature_exclusion(Path("data\\database\\records\\" + path.replace("/", "\\").upper()))


@pytest.mark.parametrize(
    "path",
    [
        "creature/monster/questbosses/boss_hydra_66.dbr",
        "creature/monster/questbosses/boss_titan_typhon_42.dbr",
        # The named exclusions are exact, not prefixes.
        "xpack3/creatures/monster/bosses/xboss_scylla_49_summon.dbr",
        # A name that merely contains "old" is not a superseded record.
        "creature/monster/golden/goldenfleece_boldrik_12.dbr",
    ],
)
def test_other_records_are_kept(path):
    assert main.creature_exclusion("/data/" + RECORDS + path) is None


def test_excluded_records_are_never_parsed_and_are_logged(fixture_data, caplog):
    """
    The record under old/ and the one named *test* share the fixture tag and
    would both sort before the real records; they are skipped before parsing.

    """
    with caplog.at_level(logging.DEBUG, logger="root"):
        creature = main.parse_creatures()["tagMonsterFixture"]

    records = [variant["record"] for variant in creature["variants"]]
    assert FIXTURE + "old/hero_5" not in records
    assert FIXTURE + "hero_test" not in records
    assert not any(key[0] in (FIXTURE + "old/hero_5", FIXTURE + "hero_test") for key in storage.db)
    assert FIXTURE + "old/hero_5" in caplog.text
    assert FIXTURE + "hero_test" in caplog.text


@pytest.mark.parametrize(
    "shipped, normalized",
    [
        ([10, 30, 50], [10, 30, 50]),
        # The Normal level repeated: the record spawns from the last repeat on.
        ([66, 66, 66], [None, None, 66]),
        ([30, 30, 50], [None, 30, 50]),
        # Zero is no spawn, before the heuristic looks at the array.
        ([0, 0, 80], [None, None, 80]),
        ([0, 35], [None, 35, 35]),
        # A single value is that level everywhere; padding is not a repetition.
        ([34], [34, 34, 34]),
        ([1], [1, 1, 1]),
    ],
)
def test_normalize_level(shipped, normalized):
    assert creatures.normalize_level(shipped) == normalized


def test_level_is_normalized_per_record(fixture_data):
    """
    A short level array repeats its last value, 0 becomes null, then the
    repeated-level heuristic blanks the difficulties the record does not
    spawn in. A difficulty without a level has no properties or abilities,
    and all three arrays always have three entries.

    """
    normal = parsed(fixture_data, "hero_normal_10")
    assert normal["level"] == [10, 30, 50]
    assert [tier["characterLife"] for tier in normal["properties"]] == ["100 Vigor", "300 Vigor", "500 Vigor"]
    assert normal["abilities"] == [
        {"tagSkillFixtureBolt": 1},
        {"tagSkillFixtureBolt": 2, "tagSkillFixtureNova": 4},
        {"tagSkillFixtureBolt": 3, "tagSkillFixtureNova": 4},
    ]

    # charLevel 0;35: padded to [0, 35, 35], the zero becomes null.
    epic = parsed(fixture_data, "hero_epic_35")
    assert epic["level"] == [None, 35, 35]
    assert epic["properties"][0] == {}
    assert epic["properties"][1] == {
        "characterLife": "350 Vigor",
        "characterMana": "35 Focus",
        "defensivePhysical": "25% Blunt Ward",
    }
    assert epic["properties"][2] == epic["properties"][1]
    assert epic["abilities"] == [{}, {"tagSkillFixtureBolt": 4}, {"tagSkillFixtureBolt": 4}]

    # charLevel 55;55;55: a repeated Normal level means Legendary only.
    legendary = parsed(fixture_data, "hero_legendary_55")
    assert legendary["level"] == [None, None, 55]
    assert legendary["properties"][:2] == [{}, {}]
    assert legendary["properties"][2]["characterLife"] == "550 Vigor"
    assert legendary["abilities"] == [{}, {}, {"tagSkillFixtureBolt": 5}]

    # No skills at all still gives three tiers.
    twin = parsed(fixture_data, "hero_legendary_55b")
    assert twin["level"] == [None, None, 55]
    assert twin["abilities"] == [{}, {}, {}]


def test_ability_tiers_are_distinct_objects(fixture_data):
    """
    A skill the record gains in Epic (skillLevel 0;4;4) stays out of the
    Normal tier even when it is the first skill listed, and every tier is
    its own dict.

    """
    normal = parsed(fixture_data, "hero_normal_10")

    assert "tagSkillFixtureNova" not in normal["abilities"][0]
    assert normal["abilities"][0] is not normal["abilities"][1]
    assert normal["abilities"][1] is not normal["abilities"][2]


def test_variants_are_ordered_by_level_then_record(fixture_data):
    creature = main.parse_creatures()["tagMonsterFixture"]

    # Null sorts after any number; the two Legendary-only records tie on
    # level and fall back to their record, compared bytewise.
    assert creature["variants"] == [
        {"record": FIXTURE + "hero_normal_10", "level": [10, 30, 50]},
        {"record": FIXTURE + "hero_epic_35", "level": [None, 35, 35]},
        {"record": FIXTURE + "hero_legendary_55", "level": [None, None, 55]},
        {"record": FIXTURE + "hero_legendary_55b", "level": [None, None, 55]},
    ]

    # The first variant is canonical and supplies the scalar fields, the
    # level, the properties and the abilities; there is no top-level record.
    canonical = parsed(fixture_data, "hero_normal_10")
    for field in ("tag", "name", "race", "classification", "level", "properties", "abilities"):
        assert creature[field] == canonical[field]
    assert creature["name"] == "Fixture Hero"
    assert set(creature) == {
        "tag",
        "name",
        "race",
        "classification",
        "level",
        "properties",
        "abilities",
        "loot",
        "variants",
    }


def test_loot_and_chest_are_unions_over_variants(fixture_data, fixture_chests):
    """
    Every item any variant can drop in a difficulty, with the chance of the
    first variant in order that gives it a chance above zero; an item at zero
    in every variant keeps the canonical's zero.

    Loot is evaluated per record as the game's arrays say, so the
    Legendary-only record contributes in every difficulty (its one-element
    level array repeats), and the Epic record contributes nothing at Normal
    (its level there is 0).

    """
    creature = main.parse_creatures()["tagMonsterFixture"]

    assert creature["loot"] == [
        # Canonical: ember 1.0, frost 0.0 (a chance below 0.00005 rounds to
        # zero); spark only from the Legendary-only record.
        {"tagScrollEmber": 1.0, "tagScrollFrost": 0.0, "tagScrollSpark": 1.0},
        # Frost is zero in the canonical and 0.25 in the Epic record; spark
        # comes from the Epic record, which precedes the Legendary one.
        {"tagScrollEmber": 1.0, "tagScrollFrost": 0.25, "tagScrollSpark": 0.5},
        {"tagScrollEmber": 1.0, "tagScrollFrost": 0.25, "tagScrollSpark": 0.5},
    ]
    assert creature["chest"] == [
        {},
        {"tagScrollEmber": 0.25, "tagScrollSpark": 0.75},
        {"tagScrollSpark": 1.0},
    ]

    # The unions are new objects, never a cached record's dict.
    cached = [parsed(fixture_data, name) for name in ("hero_normal_10", "hero_epic_35", "hero_legendary_55")]
    for index in range(3):
        for record in cached:
            assert creature["loot"][index] is not record["loot"][index]
            assert creature["chest"][index] is not record["chest"][index]


def test_collector_does_not_mutate_cached_records(fixture_data, fixture_chests):
    names = ("hero_normal_10", "hero_epic_35", "hero_legendary_55", "hero_legendary_55b")
    before = {name: copy.deepcopy(parsed(fixture_data, name)) for name in names}

    main.parse_creatures()

    for name in names:
        assert parsed(fixture_data, name) == before[name]
