"""
All functions related to storage while parsing the TQ DB.

"""

db = {}
skills = {}
# The tag each stored skill record was given, by its path:
skill_tags = {}


def duplicate_suffix(needle):
    """
    Find the next suffix for an existing prefix in skill storage.

    For example:
        prefix = 'skillName1'
        storage = {'skillName1': ....}

        # Return 1 because the new tag will be 'skillName1-1'
        return 1

    """
    result = 1

    for haystack in skills.keys():
        prefix, _, suffix = haystack.rpartition("-")
        if prefix == needle and suffix.isdigit() and int(suffix) >= result:
            result += 1

    return result


def store_skill(skill):
    """
    Store a skill and return a unique tag.

    A skill is stored by its tag but its path is used to check if any
    duplicates exist, since the tag is not fully unique.

    For example, the tag tagSkillName185 resolves to Barrage for its friendly
    name, but there's a monster skill and a skill in the Earth tree that both
    use this tag.

    """
    # One record, one tag: a record stored before keeps the tag it got,
    # whatever tag this dict carries (a buff wrapper carries its buff's).
    if skill["path"] in skill_tags:
        skill["tag"] = skill_tags[skill["path"]]
        return skill["tag"]

    # Retrieve the tag for the skill, or fall back to 'unnamed'.
    skill_tag = skill.get("tag", "unnamed")

    if skill_tag in skills:
        # A tag that already carries a suffix (a wrapper copies its buff's)
        # gets the next one for the same prefix; a hyphen in the tag itself
        # ("Cave-in", "Extend-o-neck") is not a suffix.
        prefix, _, suffix = skill_tag.rpartition("-")
        if not (prefix and suffix.isdigit()):
            prefix = skill_tag
        skill_tag = f"{prefix}-{duplicate_suffix(prefix)}"

    # Set the unique tag:
    skill["tag"] = skill_tag

    # Store the skill
    skills[skill_tag] = skill
    skill_tags[skill["path"]] = skill_tag

    # Return this (now definitely unique) tag.
    return skill_tag


def reset():
    """
    Reset the storage.

    This is used when parsing multiple locales.

    """
    global db, skills, skill_tags
    db = {}
    skills = {}
    skill_tags = {}
