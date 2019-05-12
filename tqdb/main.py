"""
Main functions to parse the full Titan Quest Database.

"""
import glob
import logging
import os
import re
import string
import time

from tqdb import storage
from tqdb.constants import resources
from tqdb.dbr import parse, read
from tqdb.utils import images
from tqdb.utils.text import texts
from tqdb.utils.core import get_affix_table_type, is_duplicate_affix


def parse_affixes():
    """
    Parse all the Titan Quest affixes.

    Affixes are the pre- and suffixes that are applied to weapons.
    These affixes add properties to the equipment, these properties,
    the affix names and the equipment they can be applied to is
    indexed and parsed in this function.

    """
    timer = time.clock()

    files = []
    for resource in resources.AFFIX_TABLES:
        table_files = resources.DB / resource
        files.extend(glob.glob(str(table_files), recursive=True))

    # The affix tables will determine what gear an affix can be applied to.
    affix_tables = {}
    for dbr in files:
        table = read(dbr)

        # Use the filename to determine what equipment this table is for:
        file_name = os.path.basename(dbr).split('_')
        table_type = get_affix_table_type(file_name[0])

        # For each affix in this table, create an entry:
        for field, affix_dbr in table.items():
            if not field.startswith('randomizerName') or not table_type:
                continue

            affix_dbr = str(affix_dbr)
            if affix_dbr not in affix_tables:
                affix_tables[affix_dbr] = [table_type]
            elif table_type not in affix_tables[affix_dbr]:
                affix_tables[affix_dbr].append(table_type)

    files = []
    for resource in resources.AFFIXES:
        affix_files = resources.DB / resource
        files.extend(glob.glob(str(affix_files), recursive=True))

    affixes = {'prefixes': {}, 'suffixes': {}}
    for dbr in files:
        affix = parse(dbr)

        # Skip affixes without properties (first one will be empty):
        if not affix['properties']:
            continue

        # Skip the incorrect 'of the Mammoth' prefix entry:
        if 'prefix' in dbr and affix['tag'] == 'tagPrefix145':
            continue

        # Assign the table types to this affix:
        if dbr not in affix_tables:
            # Affix can occur on all equipment:
            affix['equipment'] = 'none'
        else:
            affix['equipment'] = ','.join(affix_tables[dbr])

        # Add affixes to their respective pre- or suffix list.
        if 'Prefix' in affix['tag'] and 'suffix' not in dbr:
            affixType = 'prefixes'
        else:
            affixType = 'suffixes'

        affixTag = affix.pop('tag')

        # Either add the affix or add its properties as an alternative
        if affixTag in affixes[affixType]:
            # Skip duplicate affix properties:
            if is_duplicate_affix(affixes[affixType][affixTag], affix):
                continue
            affixes[affixType][affixTag]['properties'].append(
                affix['properties'])
        else:
            # Place the affix properties into a list that can be extended by
            # alternatives during this parsing.
            affix['properties'] = [affix['properties']]
            affixes[affixType][affixTag] = affix

    # Log and reset the timer:
    logging.info(f'Parsed affixes in {time.clock() - timer} seconds.')

    return affixes


def parse_equipment():
    """
    Parse all wearable Titan Quest equipment.

    The wearable equipment is indexed and sorted by equipment type. These
    categories are defined by the Class property of each piece of equipment
    which is mapped to the 'category' key in the parsed result.

    """
    timer = time.clock()

    files = []
    for resource in resources.EQUIPMENT:
        equipment_files = resources.DB / resource

        # Exclude all files in 'old' and 'default'
        files.extend([
            equipment_file
            for equipment_file
            in glob.glob(str(equipment_files), recursive=True)
            if not (
                '\\old' in equipment_file or
                '\\default' in equipment_file or
                # Rhodian and Electrum sling don't drop:
                '\\1hranged\\u_e_02.dbr' in equipment_file or
                '\\1hranged\\u_n_05.dbr' in equipment_file
            )
        ])

    items = {}
    for dbr in files:
        parsed = parse(dbr)
        try:
            # Organize the equipment based on the category
            category = parsed.pop('category')

            # Skip items without rarities
            if 'classification' not in parsed:
                continue

            # Save the bitmap and remove the bitmap key
            images.save_bitmap(parsed, category, 'output/graphics/')
        except KeyError:
            # Skip equipment that couldn't be parsed:
            continue

        # Pop off the properties key off any item without properties:
        if 'properties' in parsed and not parsed['properties']:
            parsed.pop('properties')

        # Now save the parsed item in the category:
        if category and category in items:
            items[category].append(parsed)
        elif category:
            items[category] = [parsed]

    # Log the timer:
    logging.info(f'Parsed equipment in {time.clock() - timer} seconds.')

    return items


def parse_creatures():
    """
    Parse all creatures (bosses and heroes) in Titan Quest.

    Parsing the bosses and heroes is mostly about parsing their loot tables
    to create an index of what they can drop. This index will work two ways,
    the first being a complete list of items that the monster can drop and the
    reverse being added to each individual item's loot table so it can be
    sorted.

    """
    timer = time.clock()

    files = []
    for resource in resources.CREATURES:
        boss_files = resources.DB / resource
        files.extend(glob.glob(str(boss_files), recursive=True))

    creatures = {}
    for dbr in files:
        parsed = parse(dbr)

        try:
            # Don't include common monsters
            # XXX - Should 'Champion' be added?
            if parsed['classification'] not in ['Quest', 'Hero', 'Boss']:
                continue

            # Store the monster by its tag:
            creatures[parsed['tag']] = parsed
        except KeyError:
            # Skip creatures without tags
            continue

    # Log the timer:
    logging.info(f'Parsed creatures in {time.clock() - timer} seconds.')

    return creatures


def parse_quests():
    """
    Parse the Titan Quest quest rewards.

    The quest rewards are indexed by creating a text readable version of the
    QST files located in the Resources/Quests.arc file. The rewards are
    extracted by only retrieving rewards prefixed with item[] tags.

    """
    timer = time.clock()

    # Regex to find item rewards
    REWARD = re.compile(
        r'item\[(?P<index>[0-9])\](.{0,1})'
        r'(?P<file>'
        'records'
        r'[\\||\/]'
        r'(xpack[2|3]?[\\||\/])?'
        'quests'
        r'[\\||\/]'
        'rewards'
        r'[\\||\/]'
        r'([^.]+)\.dbr'
        r')'
    )

    # Regex to find the title tag
    TITLE = re.compile(r'titletag(?P<tag>[^\s]*)')

    files = glob.glob(resources.QUESTS)
    quests = {}

    for qst in files:
        with open(qst, 'rb') as quest:
            # Read the content as printable characters only:
            content = ''.join(
                c for c in
                # Lower case and convert to utf-8
                quest.read().decode('utf-8', errors='ignore').lower()
                if c in string.printable
            )

        # Find the title and skip this file if none is found:
        title_tag = TITLE.search(content)
        if not title_tag or not title_tag.group('tag'):
            continue

        # Grab the quest title tag
        tag = title_tag.group('tag')
        if tag not in quests:
            # Initialize three difficulties:
            quests[tag] = {
                'name': texts.get(tag),
                'rewards': [{}, {}, {}],
            }

        # Parsed reward files (so we don't duplicate):
        parsed = []

        # Add all the rewards to the quest:
        for match in REWARD.finditer(content):
            # The index in the item[index] tag determines the difficulty:
            difficulty = int(match.group('index'))
            reward_file = match.group('file')

            # Store the file or move on if we've already parsed it
            if reward_file not in parsed:
                parsed.append(reward_file)
            else:
                continue

            # Prepend the path with the database path:
            rewards = parse(resources.DB / reward_file)

            # Skip quests where the rewards aren't items:
            if 'loot_table' not in rewards:
                continue

            # Either set the chance or add it to a previous chance:
            for item, chance in rewards['loot_table'].items():
                if item in quests[tag]['rewards'][difficulty]:
                    quests[tag]['rewards'][difficulty][item] += chance
                else:
                    quests[tag]['rewards'][difficulty][item] = chance

        # Don't save quests without item rewards:
        if not any(reward for reward in quests[tag]['rewards']):
            quests.pop(tag)

    # Turn all chances into percentages:
    for tag, quest in quests.items():
        for index, difficulty in enumerate(quest['rewards']):
            for item, chance in difficulty.items():
                # Format into 4 point precision percentages:
                quests[tag]['rewards'][index][item] = (
                    float('{0:.4f}'.format(chance * 100)))

    # Log the timer:
    logging.info(f'Parsed quest rewards in {time.clock() - timer} seconds.')

    return quests


def parse_sets():
    """
    Parse the Titan Quest equipment sets.

    The equipment sets are indexed and their properties are the set
    bonuses you receive for wearing multiple set pieces at once.

    """
    timer = time.clock()

    files = []
    for resource in resources.SETS:
        set_files = resources.DB / resource
        files.extend(glob.glob(str(set_files), recursive=True))

    sets = {}
    for dbr in files:
        parsed = parse(dbr)

        try:
            # Add the set by its tag to the dictionary of sets:
            sets[parsed['tag']] = parsed
        except KeyError:
            # Skip sets with no tag:
            continue

    # Log the timer:
    logging.info(f'Parsed sets in {time.clock() - timer} seconds.')

    return sets


def parse_skills():
    """
    Clean up the indexed skills during parsing.

    While parsing, all other functions will add to the skills variable in the
    storage module. This dictionary just needs to be cleaned up a little by
    removing the 'path' property of each skill, which was used during parsing
    but is no longer required for output.

    """
    skills = storage.skills.copy()
    for skill in skills.values():
        # Pop the 'path' property, it was used during parsing to ensure correct
        # skill tag references for requipment.
        skill.pop('path')

    return skills
