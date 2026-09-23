"""
Damage over time, as the game's tooltip shows it: the record's Min and Max
are damage per second, multiplied by DurationMin only. DurationMax never
scales the damage; it only turns the time into a range when it is set and
differs from DurationMin. Effects over time show their time the same way.

"""

import pytest

from tqdb import dbr

RINGS = "database/records/item/equipmentring"


@pytest.mark.parametrize(
    "ring, field, expected",
    [
        # DurationMax differs from DurationMin: the time is a range.
        (
            "fixture_ring_dot_duration_range",
            "offensiveSlowBleeding",
            "45 to 90 Seeping Harm across 3.0 - 6.0 Ticks",
        ),
        # No Max and DurationMin 1: a single amount, DurationMax only in the time.
        (
            "fixture_ring_dot_one_second",
            "offensiveSlowCold",
            "5 Rime Harm across 1.0 - 3.0 Ticks",
        ),
        # Max happens to equal Min * DurationMin: Max is still per second,
        # and DurationMax does not scale it.
        (
            "fixture_ring_dot_max_is_min_times_duration",
            "offensiveSlowCold",
            "15 to 45 Rime Harm across 3.0 - 6.0 Ticks",
        ),
        (
            "fixture_ring_dot_range",
            "offensiveSlowCold",
            "15 to 30 Rime Harm across 3.0 Ticks",
        ),
        (
            "fixture_ring_dot_single",
            "offensiveSlowCold",
            "15 Rime Harm across 3.0 Ticks",
        ),
    ],
)
def test_damage_over_time(fixture_data, ring, field, expected):
    item = dbr.parse(fixture_data / RINGS / f"{ring}.dbr")

    assert item["properties"][field] == expected


@pytest.mark.parametrize(
    "ring, expected",
    [
        # DurationMax differs from DurationMin: the time is a range.
        ("fixture_ring_eot_duration_range", "40.0% Stride Loss lasting 3.0 - 5.0 Ticks"),
        ("fixture_ring_eot_single", "40.0% Stride Loss lasting 3.0 Ticks"),
    ],
)
def test_effect_over_time(fixture_data, ring, expected):
    """An effect's time follows the same rule as damage over time's."""
    item = dbr.parse(fixture_data / RINGS / f"{ring}.dbr")

    assert item["properties"]["offensiveSlowRunSpeed"] == expected


@pytest.mark.parametrize(
    "ring, field, expected",
    [
        # Durations that keep changing past the last Min add levels; the
        # trailing repeat of 4 does not.
        (
            "fixture_ring_dot_duration_levels",
            "offensiveSlowCold",
            [
                "10 to 20 Rime Harm across 2.0 Ticks",
                "15 to 30 Rime Harm across 3.0 Ticks",
                "20 to 40 Rime Harm across 4.0 Ticks",
            ],
        ),
        (
            "fixture_ring_eot_duration_levels",
            "offensiveSlowRunSpeed",
            [
                "40.0% Stride Loss lasting 2.0 - 3.0 Ticks",
                "40.0% Stride Loss lasting 3.0 - 4.0 Ticks",
                "40.0% Stride Loss lasting 4.0 - 5.0 Ticks",
            ],
        ),
        # A duration padded past Min with its last value adds no level.
        (
            "fixture_ring_dot_duration_constant_tail",
            "offensiveSlowCold",
            [
                "15 Rime Harm across 3.0 Ticks",
                "30 Rime Harm across 3.0 Ticks",
            ],
        ),
    ],
)
def test_duration_levels(fixture_data, ring, field, expected):
    """Durations longer than Min are read for as long as they change."""
    item = dbr.parse(fixture_data / RINGS / f"{ring}.dbr")

    assert item["properties"][field] == expected
