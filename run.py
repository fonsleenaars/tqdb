# import argparse
import glob
import json
import logging
import os

# from datetime import datetime
from tqdb.constants import resources
# from tqdb.parsers.equipment import SetParser
from tqdb.dbr import parse
from tqdb.utils import images
# from tqdb.utils.core import FullPaths
# from tqdb.utils.core import is_dir
# from tqdb.utils.core import pluck
# from tqdb.utils.core import print_progress

# Directory preparations for logging
# if not os.path.exists('logs'):
#     os.makedirs('logs')
# # Configure logging:
# LOG_FILENAME = os.path.join(
#     'logs',
#     datetime.now().strftime('tqdb_%Y%m%d-%H%M%S.log'))
# logging.basicConfig(
#     filename=LOG_FILENAME,
#     level=logging.WARNING,
#     format='%(asctime)s %(message)s',
#     datefmt='%H:%M')

# Directory preparations for bitmap
if not os.path.exists('output/graphics'):
    os.makedirs('output/graphics')

# # Parse command line call
# argparser = argparse.ArgumentParser(description='TQ:IT Database parser')
# argparser.add_argument(
#     '-d',
#     '--dir',
#     help='Specify a file or directory to parse',
#     action=FullPaths,
#     type=is_dir)
# argparser.add_argument(
#     '-c',
#     '--categories',
#     nargs='+',
#     help=('Specify the categories to parse. You can choose from: affixes, '
#           'equipment, loot, sets, skills'))

# # Grab the arguments:
# args = argparser.parse_args()

# categories = set()
# files = []
data = {}

# Determine which files are required:
# print('Determining what files are required...')
# if args.categories:
#     categories.update(args.categories)
# elif not args.dir:
#     categories.update([
#         'affixes',
#         'loot',
#         'equipment-basic',
#         'equipment',
#         'sets',
#         'skills',
#     ])
# if args.dir or {'loot', 'sets'} & set(categories):
#     categories.add('equipment-basic')
# if args.dir or 'equipment' in categories:
#     categories.update(['equipment-basic', 'skills'])

###############################################################################
#                                  SKILLS                                     #
###############################################################################
# if 'skills' in categories:
#     for skill_file in res.SKILLS:
#         files.extend(glob.glob(res.DB + skill_file, recursive=True))

#     for index, dbr in enumerate(files):
#         print_progress("Parsing skills", index, len(files))
#         skills.update(parser.parse(dbr))

#     data['skills'] = skills

###############################################################################
#                                   AFFIXES                                   #
###############################################################################
# if 'affixes' in categories:
#     files = []
#     for affix_file in res.AFFIXES:
#         files.extend(glob.glob(res.DB + affix_file, recursive=True))

#     affixes = {'prefixes': {}, 'suffixes': {}}
#     for index, dbr in enumerate(files):
#         print_progress("Parsing affixes", index, len(files))
#         affix = parser.parse(dbr)

#         # Skip affixes without bonuses (first one will be empty):
#         if not affix['options'][0]:
#             continue

#         # Add affixes to their respective pre- or suffix list:
#         affixType = 'prefixes' if 'Prefix' in affix['tag'] else 'suffixes'
#         affixTag = affix['tag']

#         # Remove the tag property now
#         del(affix['tag'])

#         # Either add the affix or add its properties as an alternative
#         if affixTag in affixes[affixType]:
#             affixes[affixType][affixTag]['options'].extend(affix['options'])
#         else:
#             affixes[affixType][affixTag] = affix

#     files = []
#     for table_file in res.AFFIX_TABLES:
#         files.extend(glob.glob(res.DB + table_file, recursive=True))

#     data['affix'] = affixes

###############################################################################
#                                 EQUIPMENT                                   #
###############################################################################
files = []
for resource in resources.EQUIPMENT:
    equipment_files = resources.DB / resource

    # Extend the equipment list, but exclude all files in 'old' and 'default'
    files.extend([
        equipment_file
        for equipment_file
        in glob.glob(str(equipment_files), recursive=True)
        if not ('\\old' in equipment_file or '\\default' in equipment_file)
    ])

items = {}
for dbr in files:
    logging.debug(f'Parsing {dbr}')
    parsed = parse(dbr)

    # Skip equipment that couldn't be parsed:
    if not parsed or 'classification' not in parsed or 'name' not in parsed:
        continue

    # Organize the equipment based on the category
    category = parsed.pop('category')

    # Save the bitmap and remove the bitmap key
    if not images.save_bitmap(parsed, category, 'output/graphics/'):
        # Skip any item that has no bitmap/image:
        continue

    # Now save the parsed item in the category:
    if category and category in items:
        items[category].append(parsed)
    elif category:
        items[category] = [parsed]

data['equipment'] = items

###############################################################################
#                                    LOOT                                     #
###############################################################################
# if 'loot' in categories:
#     files = []
#     for boss_file in res.CREATURES:
#         files.extend(glob.glob(res.DB + boss_file, recursive=True))

#     bosses = {}
#     for index, dbr in enumerate(files):
#         print_progress("Parsing boss loot", index, len(files))

#         parsed = parser.parse(dbr)
#         if not parsed or 'tag' not in parsed:
#             continue

#         bossTag, boss = pluck(parsed, 'tag', 'result')

#         # Add new bosses:
#         if (bossTag and bossTag not in bosses) or (
#                 bossTag in bosses and
#                 'chest' in bosses[bossTag] and
#                 not bosses[bossTag]['chest']):
#             bosses[bossTag] = boss

#     data['bosses'] = bosses

#     quests = {}

###############################################################################
#                                      SETS                                   #
###############################################################################
files = []
for resource in resources.SETS:
    set_files = resources.DB / resource
    files.extend(glob.glob(str(set_files), recursive=True))

sets = {}
for dbr in files:
    logging.debug(f'Parsing {dbr}')
    parsed = parse(dbr)

    # Skip sets with no tag:
    if 'tag' not in parsed:
        continue

    # Add the set by its tag to the dictionary of sets:
    sets[parsed['tag']] = parsed

data['sets'] = sets


###############################################################################
#                                    OUTPUT                                   #
###############################################################################
print('Writing output to files...')
images.SpriteCreator('output/graphics/', 'output')

with open('output/data.json', 'w') as data_file:
    json.dump(data, data_file, sort_keys=True)
