import argparse
import glob
import json
import logging
import os
from datetime import datetime
from tqdb.constants import resources as res
from tqdb.parsers.equipment import SetParser
from tqdb.parsers.main import parser
from tqdb.storage import equipment, skills
from tqdb.utils.core import FullPaths
from tqdb.utils.core import index_equipment
from tqdb.utils.core import is_dir
from tqdb.utils.core import pluck
from tqdb.utils.core import print_progress
from tqdb.utils.images import SpriteCreator

# Configure logging:
LOG_FILENAME = os.path.join(
    'logs',
    datetime.now().strftime('tqdb_%Y%m%d-%H%M%S.log'))
logging.basicConfig(
    filename=LOG_FILENAME,
    level=logging.WARNING,
    format='%(asctime)s %(message)s',
    datefmt='%H:%M')

# Directory preparations:
if not os.path.exists('output/graphics'):
    os.makedirs('output/graphics')

# Parse command line call
argparser = argparse.ArgumentParser(description='TQ:IT Database parser')
argparser.add_argument(
    '-d',
    '--dir',
    help='Specify a file or directory to parse',
    action=FullPaths,
    type=is_dir)
argparser.add_argument(
    '-c',
    '--categories',
    nargs='+',
    help=('Specify the categories to parse. You can choose from: affixes, '
          'bosses, equipment, sets, skills'))

# Grab the arguments:
args = argparser.parse_args()

categories = set()
files = []
data = {}

# Determine which files are required:
print('Determining what files are required...')
if args.categories:
    categories.update(args.categories)
elif not args.dir:
    categories.update([
        'affixes',
        'bosses',
        'equipment-basic',
        'equipment',
        'sets',
        'skills',
    ])
if args.dir or 'bosses' in categories or 'sets' in categories:
    categories.add('equipment-basic')
if args.dir or 'equipment' in categories:
    categories.update(['equipment-basic', 'skills'])

###############################################################################
#                                  SKILLS                                     #
###############################################################################
if 'skills' in categories:
    for skill_file in res.SKILLS:
        files.extend(glob.glob(res.DB + skill_file, recursive=True))

    for index, dbr in enumerate(files):
        print_progress("Parsing skills", index, len(files))
        skills.update(parser.parse(dbr))

    data['skills'] = skills

###############################################################################
#                                   AFFIXES                                   #
###############################################################################
if 'affixes' in categories:
    files = []
    for affix_file in res.AFFIXES:
        files.extend(glob.glob(res.DB + affix_file, recursive=True))

    affixes = {'prefixes': {}, 'suffixes': {}}
    for index, dbr in enumerate(files):
        print_progress("Parsing affixes", index, len(files))
        affix = parser.parse(dbr)

        # Skip affixes without bonuses (first one will be empty):
        if not affix['options'][0]:
            continue

        # Add affixes to their respective pre- or suffix list:
        affixType = 'prefixes' if 'Prefix' in affix['tag'] else 'suffixes'
        affixTag = affix['tag']

        # Remove the tag property now
        del(affix['tag'])

        # Either add the affix or add its properties as an alternative
        if affixTag in affixes[affixType]:
            affixes[affixType][affixTag]['options'].extend(affix['options'])
        else:
            affixes[affixType][affixTag] = affix

    files = []
    for table_file in res.AFFIX_TABLES:
        files.extend(glob.glob(res.DB + table_file, recursive=True))

    data['affix'] = affixes

###############################################################################
#                                 EQUIPMENT                                   #
###############################################################################
items = {}
if 'equipment-basic' in categories:
    files = []
    for equipment_file in res.EQUIPMENT_BASE:
        files.extend(glob.glob(res.DB + equipment_file, recursive=True))

    items2, equipment2 = index_equipment(
        files, parser, 'weapons, jewelry, armor')
    items.update(items2)
    equipment.update(equipment2)

if 'equipment' in categories:
    files = []
    for equipment_file in res.EQUIPMENT_EXT:
        files.extend(glob.glob(res.DB + equipment_file, recursive=True))

    items2, equipment2 = index_equipment(
        files, parser, 'charms, relics, scrolls, artifacts')
    items.update(items2)
    equipment.update(equipment2)

if 'equipment-basic' in categories or 'equipment' in categories:
    data['equipment'] = items

###############################################################################
#                                    BOSSES                                   #
###############################################################################
if 'bosses' in categories:
    files = []
    for boss_file in res.CREATURES:
        files.extend(glob.glob(res.DB + boss_file, recursive=True))

    bosses = {}
    for index, dbr in enumerate(files):
        print_progress("Parsing boss loot", index, len(files))

        parsed = parser.parse(dbr)
        if not parsed:
            continue

        bossTag, boss = pluck(parsed, 'tag', 'result')

        # Add new bosses:
        if (bossTag and bossTag not in bosses) or (
                bossTag in bosses and
                'chest' in bosses[bossTag] and
                not bosses[bossTag]['chest']):
            bosses[bossTag] = boss

    data['bosses'] = bosses

###############################################################################
#                                      SETS                                   #
###############################################################################
if 'sets' in categories:
    files = []
    for set_file in res.SETS:
        files.extend(glob.glob(res.DB + set_file, recursive=True))

    sets = {}
    for index, dbr in enumerate(files):
        print_progress("Parsing sets", index, len(files))
        set_tag, set_parsed = pluck(SetParser(dbr).parse(), 'tag', 'set')

        if not set_parsed:
            continue

        # Add this set to all set items:
        for item_tag in set_parsed['items']:
            # Find the item:
            for v in items.values():
                needle = list(filter(lambda x: x['tag'] == item_tag, v))
                if needle:
                    needle[0]['set'] = set_tag

        sets[set_tag] = set_parsed

    data['sets'] = sets

###############################################################################
#                      SPECIFIC DIR OR FILE                                   #
###############################################################################
if args.dir is not None:
    # If a single file was specified; only set that:
    if os.path.isfile(args.dir):
        files = [os.path.join(args.dir)]
    else:
        directory = os.path.join(args.dir, '**\\*.dbr')
        print(f'Loading all DBR files in {directory}')
        files = glob.glob(directory, recursive=True)

    data = []
    for index, dbr in enumerate(files):
        print_progress("Parsing directory", index, len(files))
        parsed = parser.parse(dbr)

        if parsed:
            parsed['file'] = dbr
            data.append(parsed)

###############################################################################
#                                    OUTPUT                                   #
###############################################################################
print('Writing output to files...')
SpriteCreator('output/graphics/', 'output')

with open('output/data.json', 'w') as data_file:
    json.dump(data, data_file)
