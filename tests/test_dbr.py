"""
Record parsing: the memo cache is keyed by record and by references.

"""
from pathlib import Path

from tqdb import dbr

SCROLL = "database/records/xpack/item/scrolls/01_ember.dbr"


def test_record_is_the_lowercase_path_under_records():
    assert dbr.record("/data/database/records/Item/Foo Bar.dbr") == "item/foo bar"
    assert dbr.record(Path("data/database/records/item/x.dbr")) == "item/x"
    assert dbr.record("data\\database\\records\\item\\x.dbr") == "item/x"

    # Exactly one extension comes off, so the double extension stays distinct.
    assert dbr.record("data/database/records/item/x.dbr.dbr") == "item/x.dbr"

    # A dangling reference outside the records tree keeps its own identity.
    assert dbr.record("/data/database/Nothing") == "/data/database/nothing"


def test_parse_is_memoized_per_record(fixture_data):
    first = dbr.parse(fixture_data / SCROLL)
    again = dbr.parse(fixture_data / SCROLL)

    assert again is first


def test_parse_is_memoized_per_record_not_per_spelling(fixture_data):
    """
    Callers spell the same record as a Path, as a str from glob, and with
    the game's mixed case; all three are one cache entry.

    """
    first = dbr.parse(fixture_data / SCROLL)

    assert dbr.parse(str(fixture_data / SCROLL)) is first
    assert dbr.parse(str(fixture_data / SCROLL).upper()) is first


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
