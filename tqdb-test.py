import json
import glob
import argparse
import os

from dbr import DBRReader
from dbr.constants import *

# Parse command line call
argparser = argparse.ArgumentParser(description='TQ:IT Database parser')
argparser.add_argument('dir',
                       help=('Directory that the database.arz is '
                             'extracted to'))
argparser.add_argument('-rarity',
                       default='Rare,Epic,Legendary,Magical',
                       help=('Comma separated list of the possible rarities: '
                             'Rare,Epic,Legendary,Magical'))

# Grab the arguments:
args = argparser.parse_args()
db_dir = os.path.join(args.dir, '')
rarity = args.rarity.split(',')

# Load the equipment files
equipment_files = glob.glob(
    db_dir + "\\records\\item\\equipment*\\**\\*.dbr", recursive=True)
equipment_files.extend(glob.glob(
    db_dir + "\\records\\xpack\\item\\equipment*\\**\\*.dbr", recursive=True))

# Filter on rarity:
if not rarity:
    rarity = ['Rare', 'Epic', 'Legendary', 'Magical']

items = []

try:
    with open('output/skills.json', 'r') as skillsFile:
        skills = json.load(skillsFile)
except FileNotFoundError:
    skills = {}

for equipment_file in equipment_files:
    equipment = DBRReader(equipment_file, skills)
    equipment.parse()

    if equipment.parsed.get(ITEM_CLASSIFICATION, None) not in rarity:
        continue

    items.append(equipment.parsed)

# Store the json
with open('output/new.json', 'w') as items_file:
    json.dump(items, items_file)
