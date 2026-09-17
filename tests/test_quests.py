"""
Quest rewards: a dynamic-weight table is evaluated level-neutral for a quest,
and every quest says per difficulty whether its chances are.

"""
import logging

from tqdb import dbr, main

REWARDS = "database/records/quests/rewards/fixture/"


def table(fixture_data, name, references=None):
    return dbr.parse(fixture_data / REWARDS / f"{name}.dbr", references)


def test_constant_bounds_without_a_level_weight_every_eligible_item_equally(fixture_data):
    loot = table(fixture_data, "constant", {"level": None})

    # The rings at levels 10 to 16 fall within the constant bounds 8 to 20
    # and share defaultWeight; the level-30 ring is out of range.
    assert loot["loot_table"] == {
        "tagRingFixture10": 0.25,
        "tagRingFixture12": 0.25,
        "tagRingFixture14": 0.25,
        "tagRingFixture16": 0.25,
    }
    assert loot["levelNeutral"] is True


def test_numeric_level_applies_the_bell_slope(fixture_data):
    # Target (30 + 30) * 0.4 + 2 = 26: offsets -16 and -14 fall
    # outside the twelve-entry slope and take its last entry (100), -12 and
    # -10 index it from the end (200).
    loot = table(fixture_data, "constant", {"level": 30})
    assert loot["loot_table"] == {
        "tagRingFixture10": 0.16667,
        "tagRingFixture12": 0.16667,
        "tagRingFixture14": 0.33333,
        "tagRingFixture16": 0.33333,
    }
    assert "levelNeutral" not in loot

    # Bounds 26 to 32 around a target of 30 with slope 200;400;600: offsets
    # -3 and 0 give 200, offset 2 gives 600; the level-16 ring is out of range.
    loot = table(fixture_data, "levelled", {"level": 30})
    assert loot["loot_table"] == {
        "tagRingFixture27": 0.2,
        "tagRingFixture30": 0.2,
        "tagRingFixture32": 0.6,
    }
    assert "levelNeutral" not in loot


def test_bounds_that_need_a_level_stay_empty_without_one(fixture_data, caplog):
    with caplog.at_level(logging.INFO, logger="root"):
        loot = table(fixture_data, "levelled", {"level": None})

    assert "loot_table" not in loot
    assert "levelNeutral" not in loot
    assert "levelled" in caplog.text


def test_no_reference_stays_empty_and_logged(fixture_data, caplog):
    with caplog.at_level(logging.INFO, logger="root"):
        loot = table(fixture_data, "constant")

    assert "loot_table" not in loot
    assert "levelNeutral" not in loot
    assert "constant" in caplog.text


def test_master_table_carries_the_level_neutral_flag(fixture_data):
    loot = table(fixture_data, "master", {"level": None})

    assert loot["loot_table"] == {
        "tagRingFixture10": 0.125,
        "tagRingFixture12": 0.125,
        "tagRingFixture14": 0.125,
        "tagRingFixture16": 0.125,
        "tagScrollFrost": 0.5,
    }
    assert loot["levelNeutral"] is True

    assert "levelNeutral" not in table(fixture_data, "fixed", {"level": None})


def test_quest_rewards_are_level_neutral_per_difficulty(fixture_data):
    quest = main.parse_quests()["tagquestfixture"]

    assert quest["name"] == "Fixture Quest"
    assert quest["rewards"] == [
        {
            "tagRingFixture10": 12.5,
            "tagRingFixture12": 12.5,
            "tagRingFixture14": 12.5,
            "tagRingFixture16": 12.5,
            "tagScrollFrost": 50.0,
        },
        {"tagScrollFrost": 100.0},
        {},
    ]
    assert quest["levelNeutral"] == [True, False, False]
    assert set(quest) == {"name", "rewards", "levelNeutral"}
