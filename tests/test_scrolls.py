"""
Scroll records: the drop difficulty comes from the file name prefix.

"""
import pytest

from tqdb import dbr

SCROLLS = "database/records/xpack/item/scrolls"


@pytest.mark.parametrize(
    "prefix, classification, level",
    [
        ("01", "Tier One", 10),
        ("02", "Tier Two", 30),
        ("03", "Tier Three", 50),
    ],
)
def test_scroll_difficulty_from_file_prefix(fixture_data, prefix, classification, level):
    scroll = dbr.parse(fixture_data / SCROLLS / f"{prefix}_ember.dbr")

    assert scroll["classification"] == classification
    assert scroll["tag"] == "tagScrollEmber"
    assert scroll["name"] == "Scroll of Ember"
    assert scroll["description"] == "Kindles a small flame."
    assert scroll["category"] == "OneShot_Scroll"
    assert scroll["levelRequirement"] == level
    assert scroll["bitmap"] == fixture_data / "textures/items/scrolls/ember_64.tex"


def test_scroll_without_difficulty_prefix_is_not_classified(fixture_data):
    """
    The Eternal Embers dungeon consumables use the scroll template but carry
    no difficulty in their file name; they pass through unclassified.

    """
    scroll = dbr.parse(fixture_data / "database/records/item/hcdungeon/x4pot_ember.dbr")

    assert "classification" not in scroll
    assert "tag" not in scroll
    assert scroll["category"] == "OneShot_Scroll"
