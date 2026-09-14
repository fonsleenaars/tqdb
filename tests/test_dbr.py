"""
Record parsing: the memo cache is keyed by record and by references.

"""
from tqdb import dbr

SCROLL = "database/records/xpack/item/scrolls/01_ember.dbr"


def test_parse_is_memoized_per_record(fixture_data):
    first = dbr.parse(fixture_data / SCROLL)
    again = dbr.parse(fixture_data / SCROLL)

    assert again is first


def test_parse_is_memoized_per_references(fixture_data):
    """
    A record parsed with one set of references (today: the creature level a
    loot table is evaluated for) must not be handed to a caller passing
    another set.

    """
    at_ten = dbr.parse(fixture_data / SCROLL, {"level": 10})
    at_twenty = dbr.parse(fixture_data / SCROLL, {"level": 20})
    at_ten_again = dbr.parse(fixture_data / SCROLL, {"level": 10})
    without = dbr.parse(fixture_data / SCROLL)

    assert at_ten is not at_twenty
    assert at_ten_again is at_ten
    assert without is not at_ten
