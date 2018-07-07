"""
All functions related to storage while parsing the TQ DB.

"""
db = {}
skills = {}


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
        if '-' not in haystack:
            continue

        prefix, suffix = haystack.split('-')
        if prefix == needle and int(suffix) >= result:
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
    # Retrieve the tag for the skill, or fall back to 'unnamed'.
    skill_tag = skill.get('tag', 'unnamed')

    if skill_tag in skills and skills[skill_tag]['path'] != skill['path']:
        if '-' in skill_tag:
            prefix, _ = skill_tag.split('-')
            skill_tag = f'{prefix}-{duplicate_suffix(prefix)}'
        else:
            skill_tag = f'{skill_tag}-{duplicate_suffix(skill_tag)}'

        # Set the unique tag:
        skill['tag'] = skill_tag

    # Store the skill
    skills[skill_tag] = skill

    # Return this (now definitely unique) tag.
    return skill_tag
