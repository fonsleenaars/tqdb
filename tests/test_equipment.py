"""
Equipment requirements: a record's own nonzero requirement wins per field;
every field it leaves at zero comes from the cost equations, read from the
record's `itemCostName` or, without one, from the engine's default cost file
(`gameengine.dbr` names `records/game/itemcost.dbr`).

"""

from tqdb import dbr

RINGS = "database/records/item/equipmentring"


def test_static_fields_win_and_the_engine_default_fills_the_rest(fixture_data):
    """
    No `itemCostName`: strength and level are the record's, dexterity and
    intelligence come from `records/game/itemcost.dbr` at item level 20.

    """
    ring = dbr.parse(fixture_data / RINGS / "fixture_ring_static.dbr")

    assert ring["strengthRequirement"] == 77
    assert ring["levelRequirement"] == 9
    assert ring["dexterityRequirement"] == 40
    assert ring["intelligenceRequirement"] == 50


def test_static_field_wins_over_the_record_cost_file(fixture_data):
    """
    With an `itemCostName`: strength is the record's, the other three come
    from that cost file, not from the engine default.

    """
    ring = dbr.parse(fixture_data / RINGS / "fixture_ring_static_cost.dbr")

    assert ring["strengthRequirement"] == 77
    assert ring["dexterityRequirement"] == 130
    assert ring["intelligenceRequirement"] == 140
    assert ring["levelRequirement"] == 60


def test_no_static_fields_all_come_from_the_engine_default(fixture_data):
    ring = dbr.parse(fixture_data / RINGS / "fixture_ring_10.dbr")

    assert ring["strengthRequirement"] == 20
    assert ring["dexterityRequirement"] == 30
    assert ring["intelligenceRequirement"] == 40
    assert ring["levelRequirement"] == 10
