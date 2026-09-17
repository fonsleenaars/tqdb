"""
Skills: every skill carries the record it was parsed from.

"""
import copy

from tqdb import dbr, main

BOLT = "database/records/skills/fixture/hero_bolt.dbr"


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
