import json
import configparser
import glob
import argparse
import pprint
import os
import re
import subprocess
import sys

from shutil import rmtree
from tqdb import *
from tqdb.constants import *


# Bitmap function
def save_bitmap(item):
    bitmap = ''
    tag = item[TAG]

    # Check what kind of bitmap exists:
    if BITMAP_ARTIFACT in item:
        bitmap = item[BITMAP_ARTIFACT]

        # Now remove the bitmap from the item:
        del(item[BITMAP_ARTIFACT])

    elif BITMAP_FORMULA in item:
        # Formula's all share 3 possible icons (lesser, greater, artifact):
        bitmap = item[BITMAP_FORMULA]
        tag = item[CLASSIFICATION].lower()

        del(item[BITMAP_FORMULA])
    elif BITMAP_ITEM in item:
        # If the file already exists, append a counter:
        if (item.get(CLASSIFICATION, None) != ITEM_RARE and
           os.path.isfile(graphics_dir + tag + '.png')):
            # Append the type:
            counter = 1
            images = glob.glob(graphics_dir)
            for image in enumerate(images):
                if tag in images:
                    counter += 1

            tag += '-' + str(counter)

        bitmap = item[BITMAP_ITEM]

        # Now remove the bitmap from the item:
        del(item[BITMAP_ITEM])
    elif BITMAP_RELIC in item:
        bitmap = item[BITMAP_RELIC]

        # Now remove the bitmap from the item:
        del(item[BITMAP_RELIC])

    # Run the texture viewer if a bitmap and tag are set:
    if bitmap and tag and os.path.isfile(tex_dir + bitmap):
        command = ['utils/textureviewer/TextureViewer.exe',
                   tex_dir + bitmap,
                   graphics_dir + tag + '.png']
        subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)


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

# Parse command line call
argparser = argparse.ArgumentParser(description='TQ:IT Database parser')
argparser.add_argument('--clean', action='store_true')

# Grab the arguments:
args = argparser.parse_args()

# Set the directories for the database, resources and textures:
base_dir = os.path.dirname(os.path.realpath(__file__))
data_dir = os.path.join(base_dir, 'data')
db_dir = os.path.join(data_dir, 'database')
txt_dir = os.path.join(data_dir, 'texts')
tex_dir = os.path.join(data_dir, 'textures')
ini_file = os.path.join(base_dir, 'config.ini')

# If the config file doesn't exist yet, create and close it:
if not os.path.isfile(ini_file):
    open(ini_file, 'a').close()

# Try to read the config file:
config = configparser.ConfigParser()
config.read(ini_file)

# Check if key exists:
if 'InstallDirectory' not in config or (
   'titanquest' not in config['InstallDirectory']):
    # Ask for the titan quest install directory
    print('Enter the full path to your Titan Quest Installation.\n'
          'Example: C:\Program Files (x86)\Steam\SteamApps\Common\\'
          'Titan Quest Anniversary Edition')
    installdir = input('Directory: ')

    # Reinitialize the config parser and file:
    configfile = open(ini_file, 'w')
    config = configparser.ConfigParser()

    # Save the install directory in the config
    config['InstallDirectory'] = {'titanquest': installdir}
    config.write(configfile)
    configfile.close()

# Check if the required directories are created and populated:
if args.clean or not (
        os.path.exists(db_dir) and
        os.path.exists(txt_dir) and
        os.path.exists(tex_dir)):

    if args.clean and os.path.exists(data_dir):
        print('Cleaning data directory, this might take a while...')
        rmtree(data_dir)

    # Make the directories and execute extractions:
    os.makedirs(db_dir)
    os.makedirs(txt_dir)
    os.makedirs(os.path.join(tex_dir, 'Items'))
    os.makedirs(os.path.join(tex_dir, 'XPack\\Items'))

    # Grab install directory
    installdir = config['InstallDirectory']['titanquest']

    # Extract database.arz:
    command = ['utils/arzextractor/ARZExtractor.exe',
               os.path.join(installdir, 'database\\database.arz'),
               db_dir]
    subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    # Extract text resources:
    print('Extracting Resource: text files')
    command = [os.path.join(installdir, 'ArchiveTool.exe'),
               os.path.join(installdir, 'Text\\Text_EN.arc'),
               '-extract',
               txt_dir]
    subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    # Extract textures resources:
    print('Extracting Resource: Titan Quest textures')
    command = [os.path.join(installdir, 'ArchiveTool.exe'),
               os.path.join(installdir, 'Resources\\Items.arc'),
               '-extract',
               os.path.join(tex_dir, 'Items')]
    subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    # Extract XPack textures resources:
    print('Extracting Resource: Immortal Throne textures')
    command = [os.path.join(installdir, 'ArchiveTool.exe'),
               os.path.join(installdir, 'Resources\\XPack\\Items.arc'),
               '-extract',
               os.path.join(tex_dir, 'XPack\\Items')]
    subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

graphics_dir = 'output/graphics/'

# Determine directory prefix (remove spaces and lowercase it)
dir_prefix = re.sub(r'[\ \\]', '_', db_dir).lower()

# Prepare directory
if not os.path.exists('./' + graphics_dir):
    os.makedirs('./' + graphics_dir)

# Clean graphics directory:
for file in os.listdir('./' + graphics_dir):
    file_path = os.path.join('./' + graphics_dir, file)
    if(os.path.isfile(file_path)):
        os.unlink(file_path)

# Load tags
tags = {}
for index, tag_file in enumerate(FILES_TAGS):
    txt = TXTReader(os.path.join(txt_dir, tag_file))
    tags.update(txt.properties)
    cli_progress("Loading tags", index, len(FILES_TAGS))

# Index items (equipment, relics, scrolls, artifacts, formulae)
equipment_files = []
for index, equipment_file in enumerate(FILES_EQUIPMENT):
    equipment_files.extend(glob.glob(db_dir + equipment_file, recursive=True))
    cli_progress("Loading equipment", index, len(FILES_EQUIPMENT))

# Load affixes:
affix_files = []
for index, affix_file in enumerate(FILES_AFFIXES):
    affix_files.extend(glob.glob(db_dir + affix_file, recursive=True))
    cli_progress("Loading affixes", index, len(FILES_AFFIXES))

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

    # Skip all '/old/' and '/default/' files:
    if '\\old\\' in equipment_file or '\\default\\' in equipment_file:
        cli_progress("Parsing equipment", index, len(equipment_files))
        continue

    # Create a new DBRReader object and pass along the tags
    equipment = DBRReader(equipment_file, tags)

    # First check: TYPE should be set:
    if not equipment.parsed[TYPE]:
        cli_progress("Parsing equipment", index, len(equipment_files))
        continue

    # Now fully parse the file
    equipment.parse()

    # Skip items without tags
    if (TAG not in equipment.parsed or not equipment.parsed[TAG]):
        cli_progress("Parsing equipment", index, len(equipment_files))
        continue

    existingItems = []

    # Check if a corresponding unique already exists:
    if (CLASSIFICATION in equipment.parsed and
       equipment.parsed[CLASSIFICATION] != ITEM_RARE):
        # Uniques only match if same tag AND same type
        existingItems = list(filter(
                            lambda x: ((x.get(CLASSIFICATION, None) !=
                                        ITEM_RARE) and
                                       x[TAG] == equipment.parsed[TAG] and
                                       x[TYPE] == equipment.parsed[TYPE]),
                            items))

    # Check if a corresponding MI already exists:
    if (CLASSIFICATION in equipment.parsed and
       equipment.parsed[CLASSIFICATION] == ITEM_RARE):
        # MI's only match if same tag AND same difficulty they drop in
        existingItems = list(filter(
                            lambda x: ((x.get(CLASSIFICATION, None) ==
                                        ITEM_RARE) and
                                       x[TAG] == equipment.parsed[TAG] and
                                       (x.get(ITEM_MI_DROP, None) ==
                                        equipment.parsed[ITEM_MI_DROP])),
                            items))

    # Only append new items:
    if not existingItems:
        items.append(equipment.parsed)

        # Save a bitmap, if it's set:
        save_bitmap(equipment.parsed)

    cli_progress("Parsing equipment", index, len(equipment_files))

affixes = {LOOT_PREFIXES: [], LOOT_SUFFIXES: []}
cli_progress("Parsing affixes", 0, len(affix_files))
for index, affix_file in enumerate(affix_files):
    # Create a new DBRReader object and pass along the tags
    affix = DBRReader(affix_file, tags)

    if(TYPE not in affix.parsed or affix.parsed[TYPE] not in TYPE_LOOT_AFFIX):
        cli_progress("Parsing affixes", index, len(affix_files))
        continue

    # Parse the affix now
    affix.parse()

    # Determine if this is a prefix or suffix
    affixType = (LOOT_PREFIXES
                 if LOOT_PREFIX in affix.parsed[TAG].lower()
                 else LOOT_SUFFIXES)

    # Remove unnecessary data:
    del(affix.parsed[TYPE])
    del(affix.parsed[TAG])

    # Check if the affix already exists, if so, append properties
    existingAffixes = list(filter(lambda x: (NAME in x and
                                             x[NAME] == affix.parsed[NAME]),
                                  affixes[affixType]))
    if not existingAffixes:
        affixes[affixType].append(affix.parsed)
    else:
        existingAffix = existingAffixes[0]
        if isinstance(existingAffix[PROPERTIES], list):
            # If a properties list already exists, append the new one
            existingAffix[PROPERTIES].append(affix.parsed[PROPERTIES])
        else:
            # If a properties list does not exist yet, make a list:
            existingAffix[PROPERTIES] = [existingAffix[PROPERTIES],
                                         affix.parsed[PROPERTIES]]

    cli_progress("Parsing affixes", index, len(affix_files))

sets = {}
cli_progress("Parsing sets", 0, len(set_files))
for index, set_file in enumerate(set_files):
    # Create a new DBRReader object and pass along the tags
    set_item = DBRReader(set_file, tags)
    set_item.parse()

    # If this set has no members; skip it:
    if len(set_item.parsed[SET_MEMBERS]) == 0:
        cli_progress("Parsing sets", index, len(set_files))
        continue

    # Change properties, to bonuses:
    set_item.parsed[BONUS] = set_item.parsed[PROPERTIES]
    del(set_item.parsed[PROPERTIES])

    # Grab the item tag and remove it from the properties:
    set_tag = set_item.parsed[TAG]
    del(set_item.parsed[TAG])

    # Store the new item set with its tag being the key
    sets[set_tag] = set_item.parsed

    cli_progress("Parsing sets", index, len(set_files))

# Run through all items to parse the granted/augmented skills:
itemsToCheck = items + affixes[LOOT_PREFIXES] + affixes[LOOT_SUFFIXES]
for index, item in enumerate(itemsToCheck):

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
                SKILL_LEVEL_LOWER: skill.get(SKILL_LEVEL_LOWER, ''),
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
    cli_progress("Parsing item skills", index, len(itemsToCheck))

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

with open('output/affixes.json', 'w') as affixes_file:
    json.dump(affixes, affixes_file)

with open('output/sets.json', 'w') as sets_file:
    json.dump(sets, sets_file)

with open('output/skills.json', 'w') as skills_file:
    json.dump(skills, skills_file)

# Done writing, create sprite:
print("JSON output finished, creating sprites")
sprite = SpriteCreator(graphics_dir, './output')

print("Output written to /output directory")
