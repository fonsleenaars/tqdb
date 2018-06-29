# import argparse
import glob
import json
import logging
import os
import time

from tqdb import storage
from tqdb.constants import resources
from tqdb.dbr import parse, read
from tqdb.utils import images
from tqdb.utils.core import get_affix_table_type
# from tqdb.utils.core import FullPaths
# from tqdb.utils.core import is_dir
# from tqdb.utils.core import pluck
# from tqdb.utils.core import print_progress

# Directory preparations for logging
# if not os.path.exists('logs'):
#     os.makedirs('logs')
# Configure logging:
# LOG_FILENAME = os.path.join(
#     'logs',
#     datetime.now().strftime('tqdb_%Y%m%d-%H%M%S.log'))
# Disable any DEBUG logging from PIL:
logging.getLogger('PIL').setLevel(logging.WARNING)
logging.basicConfig(
    # filename=LOG_FILENAME,
    level=logging.INFO,
    format='%(asctime)s %(message)s',
    datefmt='%H:%M')

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

timer = time.clock()
###############################################################################
#                                   AFFIXES                                   #
###############################################################################
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
        affix['equipment'] = 'All equipment'
    else:
        affix['equipment'] = ', '.join(affix_tables[dbr])

    # Add affixes to their respective pre- or suffix list:
    affixType = 'prefixes' if 'Prefix' in affix['tag'] else 'suffixes'
    affixTag = affix.pop('tag')

    # Either add the affix or add its properties as an alternative
    if affixTag in affixes[affixType]:
        affixes[affixType][affixTag]['properties'].append(affix['properties'])
    else:
        # Place the affix properties into a list that can be extended by
        # alternatives during this parsing.
        affix['properties'] = [affix['properties']]
        affixes[affixType][affixTag] = affix

data['affix'] = affixes

# Log and reset the timer:
logging.info(f'Parsed affixes in {time.clock() - timer} seconds.')
timer = time.clock()

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

# Store the equipment to output to JSON
data['equipment'] = items

# Log and reset the timer:
logging.info(f'Parsed equipment in {time.clock() - timer} seconds.')
timer = time.clock()

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

# Store the sets to output to JSON
data['sets'] = sets

# Log and reset the timer:
logging.info(f'Parsed sets in {time.clock() - timer} seconds.')
timer = time.clock()

##############################################################################
#                                 SKILLS                                     #
##############################################################################

# The skills have been stored by their path while indexing equipment.
# In order to reference and store them by tag, iterate over all the entries and
# use or create a unique tag, then update the references in equipment files.
skills = storage.skills.copy()

for skill in skills.values():
    # Pop the 'path' property, it was used during parsing to ensure correct
    # skill tag references for requipment.
    skill.pop('path')

# Store the skills to output to JSON
data['skills'] = skills

###############################################################################
#                                    OUTPUT                                   #
###############################################################################
print('Writing output to files...')
images.SpriteCreator('output/graphics/', 'output')

with open('output/data.json', 'w') as data_file:
    json.dump(data, data_file, sort_keys=True)
