import json
import glob
import argparse
import os
import re
import sys

from dbr import DBRReader, TXTReader
from dbr.constants import *

# Parse command line call
argparser = argparse.ArgumentParser(description='TQ:IT Database parser')
argparser.add_argument('db',
                       help=('Directory that the database.arz is '
                             'extracted to'))
argparser.add_argument('text',
                       help='Directory that the text_en.arc is extracted to')

# Grab the arguments:
args = argparser.parse_args()
db_dir = os.path.join(args.db, '')
text_dir = os.path.join(args.text, '')


# Progress function:
# Credit: http://stackoverflow.com/a/13685020
def cli_progress(label,  i, end_val, bar_length=20):
    percent = float(i) / (end_val - 1)
    hashes = '#' * int(round(percent * bar_length))
    spaces = ' ' * (bar_length - len(hashes))

    if i == end_val - 1:
        print("\r{0:25} [{1}] DONE".format(label, hashes + spaces))
    else:
        # Write out the progress
        progress = int(round(percent * 100))
        sys.stdout.write("\r{0:25} [{1}] {2}%".format(label,
                                                      hashes + spaces,
                                                      progress))
        sys.stdout.flush()

# Load tags
tags = {}
for index, tag_file in enumerate(FILES_TAGS):
    txt = TXTReader(text_dir + tag_file)
    tags.update(txt.properties)
    cli_progress("Loading tags", index, len(FILES_TAGS))

# Index items (equipment, relics, scrolls, artifacts, formulae)
equipment_files = []
for index, equipment_file in enumerate(FILES_EQUIPMENT):
    equipment_files.extend(glob.glob(db_dir + equipment_file, recursive=True))
    cli_progress("Loading equipment", index, len(FILES_EQUIPMENT))

# Index set files:
set_files = []
for index, set_file in enumerate(FILES_SETS):
    set_files.extend(glob.glob(db_dir + set_file))
    cli_progress("Loading sets", index, len(FILES_SETS))

# Index skills
skill_files = []
for index, skill_file in enumerate(FILES_SKILLS):
    cli_progress("Loading skills", index, len(FILES_SKILLS))
    skill_files.extend(glob.glob(db_dir + skill_file, recursive=True))

items = []
cli_progress("Parsing equipment", 0, len(equipment_files))
for index, equipment_file in enumerate(equipment_files):
    # Create a new DBRReader object and pass along the tags
    equipment = DBRReader(equipment_file, tags)

    # First check: TYPE should be set:
    if not equipment.parsed[TYPE]:
        cli_progress("Parsing equipment", index, len(equipment_files))
        continue

    # Now fully parse the file
    equipment.parse()

    # Skip items without tags
    if (ITEM_TAG not in equipment.parsed and
       RELIC_TAG not in equipment.parsed):
        cli_progress("Parsing equipment", index, len(equipment_files))
        continue

    # Append parsed item:
    items.append(equipment.parsed)

    cli_progress("Parsing equipment", index, len(equipment_files))

sets = {}
cli_progress("Parsing sets", 0, len(set_files))
for index, set_file in enumerate(set_files):
    # Create a new DBRReader object and pass along the tags
    item_set = DBRReader(set_file, tags)
    item_set.parse()

    # If this set has no members; skip it:
    if len(item_set.parsed[SET_MEMBERS]) == 0:
        cli_progress("Parsing sets", index, len(set_files))
        continue

    # Grab the item tag and remove it from the properties:
    item_tag = item_set.parsed[ITEM_SET_TAG]
    del(item_set.parsed[ITEM_SET_TAG])

    # Store the new item set with its tag being the key
    sets[item_tag] = item_set.parsed

    cli_progress("Parsing sets", index, len(set_files))

skills = {}

# First run through the equipment and extract granted skills and
# augmented skills. Then runt hrough the skill files and add
# the skills that aren't added yet:
dir_prefix = re.sub(r'[\ \\]', '_', db_dir).lower()
for index, item in enumerate(items):

    # Only parse items with PROPERTIES
    if PROPERTIES not in item:
        cli_progress("Parsing item skills", index, len(items))
        continue

    # Check granted skills
    if ITEM_SKILL in item[PROPERTIES]:

        # Extract the skill:
        skill = item[PROPERTIES][ITEM_SKILL]
        skill_path = skill[PATH].replace(dir_prefix, '')

        # Replace the skill with a reference
        item[PROPERTIES][ITEM_SKILL] = {
            PATH: skill_path,
            SKILL_DISPLAY: skill[SKILL_DISPLAY]
        }

        # Remove the path reference and set it as a key:
        del(skill[PATH])
        skills[skill_path] = skill

    # Check augmented skills
    for augment_name, augment_level in SKILL_AUGMENT_FIELDS.items():
        if augment_name not in item[PROPERTIES]:
            continue

        # Extract the skill:
        skill = item[PROPERTIES][augment_name]
        skill_path = skill[PATH].replace(dir_prefix, '')

        # Replace the skill with a reference
        item[PROPERTIES][augment_name] = {
            PATH: skill_path,
            SKILL_DISPLAY: skill[SKILL_DISPLAY],
            augment_level: skill[augment_level]
        }

        # Remove the path reference and set it as a key:
        del(skill[augment_level])
        del(skill[PATH])
        skills[skill_path] = skill

    cli_progress("Parsing item skills", index, len(items))

# Now append any missing skills:
for index, skill_file in enumerate(skill_files):
    # Grab the path (and then remove the directory prefixes)
    skill_path = re.sub(r'[\ \\]', '_', skill_file).lower()
    skill_path = skill_path.replace(dir_prefix, '')

    if skill_path in skills:
        cli_progress("Parsing skills", index, len(skill_files))
        continue

    skill = DBRReader(skill_file, tags)
    skill.parse()

    # Make sure the path (key) is set, then remove it from the values
    if PATH in skill.parsed:
        del(skill.parsed[PATH])
        skills[skill_path] = skill.parsed

    cli_progress("Parsing skills", index, len(skill_files))


# Done; write JSON to files
print("Done parsing, writing to JSON")
with open('output/new.json', 'w') as items_file:
    json.dump(items, items_file)

with open('output/sets-new.json', 'w') as sets_file:
    json.dump(sets, sets_file)

with open('output/skills-new.json', 'w') as skills_file:
    json.dump(skills, skills_file)
print("Output written to /output directory")
