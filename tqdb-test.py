import json
import glob
import argparse
import os

from dbr import DBRReader, TXTReader
from dbr.constants import *

# Parse command line call
argparser = argparse.ArgumentParser(description='TQ:IT Database parser')
argparser.add_argument('db',
                       help=('Directory that the database.arz is '
                             'extracted to'))
argparser.add_argument('text',
                       help='Directory that the text_en.arc is extracted to')
argparser.add_argument('-rarity',
                       default='Rare,Epic,Legendary,Magical',
                       help=('Comma separated list of the possible rarities: '
                             'Rare,Epic,Legendary,Magical'))

# Grab the arguments:
args = argparser.parse_args()
db_dir = os.path.join(args.db, '')
text_dir = os.path.join(args.text, '')

# Load tags
tags = {}
for tag_file in FILES_TAGS:
    txt = TXTReader(text_dir + tag_file)
    tags.update(txt.properties)

with open('output/tags.json', 'w') as tags_file:
    json.dump(tags, tags_file)

# Index items (equipment, relics, scrolls, artifacts, formulae)
equipment_files = []
for equipment_file in FILES_EQUIPMENT:
    equipment_files.extend(glob.glob(db_dir + equipment_file, recursive=True))

# Index set files:
set_files = []
for set_file in FILES_SETS:
    set_files.extend(glob.glob(db_dir + set_file))

# Index skills
skill_files = []
for skill_file in FILES_SKILLS:
    skill_files.extend(glob.glob(db_dir + skill_file, recursive=True))

items = []
for equipment_file in equipment_files:
    # Create a new DBRReader object and pass along the tags
    equipment = DBRReader(equipment_file, tags)

    # First check: TYPE should be set:
    if not equipment.parsed[TYPE]:
        continue

    # Now fully parse the file
    equipment.parse()

    # Skip items without tags
    if (ITEM_TAG not in equipment.parsed and
       RELIC_TAG not in equipment.parsed):
        continue

    # Append parsed item:
    items.append(equipment.parsed)

sets = {}
for set_file in set_files:
    # Create a new DBRReader object and pass along the tags
    item_set = DBRReader(set_file, tags)
    item_set.parse()

    # If this set has no members; skip it:
    if len(item_set.parsed[SET_MEMBERS]) == 0:
        continue

    # Grab the item tag and remove it from the properties:
    item_tag = item_set.parsed[ITEM_SET_TAG]
    del(item_set.parsed[ITEM_SET_TAG])

    # Store the new item set with its tag being the key
    sets[item_tag] = item_set.parsed

# for skill_file in skill_files:
#     try:
#         skill = DBRReader(skill_file, tags)
#         skill.parse()
#     except FileNotFoundError:
#         continue

# Done; write JSON to files
with open('output/new.json', 'w') as items_file:
    json.dump(items, items_file)

with open('output/sets-new.json', 'w') as sets_file:
    json.dump(sets, sets_file)
