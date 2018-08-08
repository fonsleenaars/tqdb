"""
Main functions to parse the full Titan Quest Database.

"""
import glob
import logging
import os
import time

from tqdb import storage
from tqdb.constants import resources
from tqdb.dbr import parse, read
from tqdb.utils import images
from tqdb.utils.core import get_affix_table_type


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

        # Assign the table types to this affix:
        if dbr not in affix_tables or len(affix_tables[dbr]) == 17:
            # Affix can occur on all equipment:
            affix['equipment'] = 'all'
        else:
            affix['equipment'] = ','.join(affix_tables[dbr])

        # Add affixes to their respective pre- or suffix list:
        affixType = 'prefixes' if 'Prefix' in affix['tag'] else 'suffixes'
        affixTag = affix.pop('tag')

        # Either add the affix or add its properties as an alternative
        if affixTag in affixes[affixType]:
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
