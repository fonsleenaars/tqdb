import json
import glob
import argparse
import pprint
import os
import re
import subprocess
import sys

from tqdb import *
from tqdb.constants import *

# Parse command line call
argparser = argparse.ArgumentParser(description='TQ:IT Database parser')
argparser.add_argument('db',
                       help=('Directory that the database.arz is '
                             'extracted to'))
argparser.add_argument('text',
                       help='Directory that the text_en.arc is extracted to')

argparser.add_argument('textures',
                       help='Directory that the textures are extracted to')

# Grab the arguments:
args = argparser.parse_args()
db_dir = os.path.join(args.db, '')
text_dir = os.path.join(args.text, '')
tex_dir = os.path.join(args.textures, '')
graphics_dir = 'output/graphics/'

# Determine directory prefix (remove spaces and lowercase it)
dir_prefix = re.sub(r'[\ \\]', '_', db_dir).lower()


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


# Bitmap function
def save_bitmap(item):
    bitmap = ''
    tag = ''

    # Check what kind of bitmap exists:
    if BITMAP_ARTIFACT in item:
        bitmap = item[BITMAP_ARTIFACT]
        tag = item[ARTIFACT_TAG]

        # Now remove the bitmap from the item:
        del(item[BITMAP_ARTIFACT])
    elif BITMAP_ITEM in item:
        bitmap = item[BITMAP_ITEM]
        tag = item[ITEM_TAG]

        # Now remove the bitmap from the item:
        del(item[BITMAP_ITEM])

    # Run the texture viewer if a bitmap and tag are set:
    if bitmap and tag and os.path.isfile(tex_dir + bitmap):
        command = ['utils/textureviewer/TextureViewer.exe',
                   tex_dir + bitmap,
                   graphics_dir + tag + '.png']
        subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

# Prepare directory
if not os.path.exists('./' + graphics_dir):
    os.makedirs('./' + graphics_dir)

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
skills = {}
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
       RELIC_TAG not in equipment.parsed and
       ARTIFACT_TAG not in equipment.parsed):
        cli_progress("Parsing equipment", index, len(equipment_files))
        continue

    # Append parsed item:
    items.append(equipment.parsed)

    # Save a bitmap, if it's set:
    save_bitmap(equipment.parsed)

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

# Run through all items to parse the granted/augmented skills:
for index, item in enumerate(items):

    # Check PROPERTIES:
    if PROPERTIES in item:
        # Check granted skills
        if (ITEM_SKILL in item[PROPERTIES] and
                SKILL_DISPLAY in item[PROPERTIES][ITEM_SKILL]):
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

    # Check skills with skillName:
    elif SKILL_NAME_LOWER in item:
        # Extract the skill:
        skill = item[SKILL_NAME_LOWER]
        skill_path = skill[PATH].replace(dir_prefix, '')

        # Replace the skill with a reference
        item[SKILL_NAME_LOWER] = skill_path

        # Remove the path reference and set it as a key:
        del(skill[PATH])
        skills[skill_path] = skill

    # Update progress
    cli_progress("Parsing item skills", index, len(items))

# Parse mastery skills
mastery_skills = []
for index, skill_file in enumerate(skill_files):

    # Parse the skill tree, which will result a list of skills:
    skill_tree = DBRReader(skill_file, tags)
    skill_tree.parse()

    # Append the skills
    mastery_skills.extend(skill_tree.parsed[SKILLS])

    for skill in skill_tree.parsed[SKILLS]:
        if PATH not in skill:
            print(skill)

    cli_progress("Parsing skill trees", index, len(skill_files))

# Parse skills from mastery trees:
for index, skill in enumerate(mastery_skills):

    # Grab the path (and then remove the directory prefixes)
    skill_path = skill[PATH].replace(dir_prefix, '')

    # Check if skill has already been parsed
    if skill_path in skills:
        cli_progress("Organizing skills", index, len(mastery_skills))
        continue

    # Make sure the path (key) is set, then remove it from the values
    if PATH in skill:
        del(skill[PATH])
        skills[skill_path] = skill

    cli_progress("Organizing mastery skills", index, len(mastery_skills))

# Parse pet/summon skills:
pet_skills = dict()
index = 0
for skill_path, skill in skills.items():

    # Only parse summon/pet skills:
    if PET_OBJECT not in skill:
        cli_progress("Organizing pet skills", index, len(skills))
        index += 1
        continue

    pets = skill[PET_OBJECT]
    for pet in pets:
        if (SKILLS not in pet and PET_SPECIAL not in pet and
                PET_INIT_SKILL not in pet):
            continue

        for pet_skill in pet[SKILLS]:
            pet_skill_name = pet_skill[SKILL_NAME_LOWER].lower()
            pet_skill_path = DBRReader.format_path(pet_skill_name)

            # Update skill reference
            pet_skill[SKILL_NAME_LOWER] = pet_skill_path

            # Skip already parsed skills
            if pet_skill_path in pet_skills:
                continue

            # Parse the pet skill:
            pet_skill_parsed = DBRReader(db_dir + pet_skill_name, tags)
            pet_skill_parsed.parse()

            # Update pet skill reference and append to skills list:
            pet_skills[pet_skill_path] = pet_skill_parsed.parsed
            del(pet_skills[pet_skill_path][PATH])

        # Parse the special pet skill:
        if PET_SPECIAL in pet:
            pet_skill_name = pet[PET_SPECIAL].lower()
            pet_skill_path = DBRReader.format_path(pet_skill_name)

            # Update skill reference
            pet[PET_SPECIAL] = pet_skill_path

            # Skip already parsed skills
            if pet_skill_path in pet_skills:
                continue

            # Parse the pet skill:
            pet_skill_parsed = DBRReader(db_dir + pet_skill_name, tags)
            pet_skill_parsed.parse()

            # Update pet skill reference and append to skills list:
            pet_skills[pet_skill_path] = pet_skill_parsed.parsed
            del(pet_skills[pet_skill_path][PATH])

        # Parse the initial pet skill:
        if PET_INIT_SKILL in pet:
            pet_skill_name = pet[PET_INIT_SKILL].lower()
            pet_skill_path = DBRReader.format_path(pet_skill_name)

            # Update skill reference
            pet[PET_INIT_SKILL] = pet_skill_path

            # Skip already parsed skills
            if pet_skill_path in pet_skills:
                continue

            # Parse the pet skill:
            pet_skill_parsed = DBRReader(db_dir + pet_skill_name, tags)
            pet_skill_parsed.parse()

            # Update pet skill reference and append to skills list:
            pet_skills[pet_skill_path] = pet_skill_parsed.parsed
            del(pet_skills[pet_skill_path][PATH])

    cli_progress("Organizing pet skills", index, len(skills))
    index += 1

# Move over the pet skills into the skill dictionary:
skills.update(pet_skills)

# Done; write JSON to files
print("Done parsing, writing to JSON")
with open('output/items.json', 'w') as items_file:
    json.dump(items, items_file)

with open('output/sets.json', 'w') as sets_file:
    json.dump(sets, sets_file)

with open('output/skills.json', 'w') as skills_file:
    json.dump(skills, skills_file)

# Done writing, create sprite:
print("JSON output finished, creating sprites")
sprite = SpriteCreator(graphics_dir, './output')

print("Output written to /output directory")
