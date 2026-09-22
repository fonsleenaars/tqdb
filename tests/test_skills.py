"""
Skills: every skill carries the record it was parsed from, a buff wrapper's
record is its own, and one record has one tag.

"""

import copy
from pathlib import Path

from tqdb import dbr, main, storage

BOLT = "database/records/skills/fixture/hero_bolt.dbr"
AURA_HERO = "database/records/creature/monster/fixture/hero_aura_40.dbr"


def test_buff_wrapper_record_is_its_own(fixture_data):
    # The hero lists two wrapper skills of one buff. Each wrapper shows the
    # buff's name and properties but is its own record, as the hero
    # references it; the buff itself is referenced by nobody.
    creature = dbr.parse(fixture_data / AURA_HERO)
    skills = main.parse_skills()

    by_record = {skill["record"]: tag for tag, skill in skills.items()}
    assert "skills/fixture/aura_a" in by_record
    assert "skills/fixture/aura_b" in by_record
    assert "skills/fixture/aura_buff" not in by_record

    a, b = skills[by_record["skills/fixture/aura_a"]], skills[by_record["skills/fixture/aura_b"]]
    assert a["name"] == b["name"] == "Fixture Aura"
    assert a["properties"] == b["properties"]
    assert set(creature["abilities"][0]) == {a["tag"], b["tag"]}


def test_one_record_has_one_tag(fixture_data):
    tag = "tagSkillFixtureAura"
    assert storage.store_skill({"tag": tag, "path": Path("skills/one.dbr")}) == tag
    assert storage.store_skill({"tag": tag, "path": Path("skills/two.dbr")}) == f"{tag}-1"
    # A fresh dict for a record already stored keeps that record's tag,
    # whichever tag it carries itself:
    assert storage.store_skill({"tag": tag, "path": Path("skills/two.dbr")}) == f"{tag}-1"
    assert storage.store_skill({"tag": f"{tag}-1", "path": Path("skills/one.dbr")}) == tag
    # A wrapper carries its buff's tag, suffix included, and a hyphen in
    # the tag itself is not a suffix:
    assert storage.store_skill({"tag": f"{tag}-1", "path": Path("skills/three.dbr")}) == f"{tag}-2"
    assert storage.store_skill({"tag": "Cave-in", "path": Path("skills/four.dbr")}) == "Cave-in"
    assert storage.store_skill({"tag": "Cave-in", "path": Path("skills/five.dbr")}) == "Cave-in-1"


def test_every_skill_carries_its_record(fixture_data):
    main.parse_creatures()
    skills = main.parse_skills()

    bolt = skills["tagSkillFixtureBolt"]
    assert bolt["record"] == "skills/fixture/hero_bolt"
    assert "path" not in bolt
    assert all("record" in skill for skill in skills.values())


def test_collector_does_not_mutate_cached_records(fixture_data):
    main.parse_creatures()
    before = copy.deepcopy(dbr.parse(fixture_data / BOLT))

    main.parse_skills()

    assert dbr.parse(fixture_data / BOLT) == before
