"""
All functions related to storage while parsing the TQ DB.

"""
db = {}
skills = {}


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
        # The tag exists, but the path is different, so this is a new skill.
        tag_pieces = skill_tag.split('-')
        skill_tag = (
            # First duplicate, add a -1
            f'{skill_tag}-1'
            if len(tag_pieces) == 1
            # More duplicates exist, increment numeric suffix
            else f'{skill_tag}-{int(tag_pieces[1]) + 1}')

        # Set the newly suffixed tag:
        skill['tag'] = skill_tag

    # Store the skill
    skills[skill_tag] = skill

    # Return this (now definitely unique) tag.
    return skill_tag
