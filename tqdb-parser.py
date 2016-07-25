import json
import glob
import pprint
import re
import argparse
import os
import subprocess

from dbr_parser import *

# Parse command line call
parser = argparse.ArgumentParser(description='TQ:IT Database parser')
parser.add_argument('dir',
                    help=('Directory that the database.arz is '
                          'extracted to'))
parser.add_argument('-rarity',
                    default='Rare,Epic,Legendary,Magical',
                    help=('Comma separated list of the possible rarities: '
                          'Rare,Epic,Legendary,Magical'))
parser.add_argument('-bitmap',
                    help=('Directory that the item textures are '
                          'extracted to'))

# Grab the arguments:
args = parser.parse_args()
db_dir = os.path.join(args.dir, '')
rarity = args.rarity.split(',')
bmp_dir = os.path.join(args.bitmap, '') if args.bitmap else ''

# Load the equipment files
equipment_files = glob.glob(db_dir + "\\records\\item\\equipment*\\**\\*.dbr",
                            recursive=True)
equipment_files.extend(
    glob.glob(
        db_dir + "\\records\\xpack\\item\\equipment*\\**\\*.dbr",
        recursive=True))

# Load the relic files
relic_files = glob.glob(db_dir + "\\records\\item\\relics\\*.dbr")
relic_files.extend(glob.glob(db_dir + "\\records\\xpack\\item\\relics\\*.dbr"))
relic_files.extend(glob.glob(db_dir + "\\records\\item\\animalrelics\\*.dbr"))
relic_files.extend(glob.glob(db_dir + "\\records\\xpack\\item\\charms\\*.dbr"))

# Load the scroll, artifact & formulae:
scroll_files = glob.glob(db_dir + "\\records\\xpack\\item\\scrolls\\*.dbr")
artifact_files = glob.glob(db_dir + ("\\records\\xpack\\item\\artifacts"
                                     "\\*.dbr"))
formulae_files = glob.glob(db_dir + ("\\records\\xpack\\item\\artifacts"
                                     "\\arcaneformulae\\*.dbr"))

# Difficulties for relics:
difficulties = ["Normal", "Epic", "Legendary"]
requirements = ["Strength", "Dexterity", "Intelligence", "Level"]
artifact_difficulties = {'e': 'Epic', 'l': 'Legendary', 'n': 'Normal'}

# Filter on rarity:
if not rarity:
    rarity = ['Rare', 'Epic', 'Legendary', 'Magical']

# Prepare directory
if bmp_dir and not os.path.exists('./output/uibitmaps'):
    os.makedirs('./output/uibitmaps')


# Load the tags
with open('output/tags.json', 'r') as tags_file:
    tags = json.load(tags_file)

items = dict()
for equipment_file in equipment_files:
    with open(equipment_file) as equipment:
        # DBR file into a list of lines
        lines = [line.rstrip(',\n') for line in equipment]

        # Parse line into a dictionary of key, value properties:
        item_properties = dict([(k, v) for k, v in (dict(properties.split(',')
                               for properties in lines)).items()
                               if has_numeric_value(v)])

        # Check required keys:
        if not all(k in item_properties for k in ("itemNameTag", "itemLevel")):
            continue

        if('itemClassification' not in item_properties or
            ('itemClassification' in item_properties and
                item_properties['itemClassification'] not in rarity)):
            continue

        new_item = dict()
        new_item['tag'] = item_properties['itemNameTag']
        new_item['name'] = tags[item_properties['itemNameTag']]
        new_item['level'] = item_properties['itemLevel']
        new_item['classification'] = item_properties['itemClassification']

        try:
            new_item['properties'] = parse_properties(item_properties)
        except KeyError as e:
            print(item_properties)

        if 'characterBaseAttackSpeedTag' in item_properties:
            new_item['attackSpeed'] = (
                item_properties
                    ['characterBaseAttackSpeedTag']
                    [len('CharacterAttackSpeed'):])

        # Parse pet bonuses:
        if 'petBonusName' in item_properties:
            # Open pet bonus file
            with open(db_dir + item_properties['petBonusName']) as pet_file:
                pet_lines = [line.rstrip(',\n') for line in pet_file]
                pet_properties = dict([(k, v) for k, v
                                      in (dict(properties.split(',')
                                          for properties in pet_lines)).items()
                                      if has_numeric_value(v)])
                pet_bonus = parse_properties(pet_properties)
                new_item['properties']['petBonusName'] = pet_bonus

        # Grab the set DBR if it exists
        if 'itemSetName' in item_properties:
            # Open set file
            with open(db_dir + item_properties['itemSetName']) as set_file:
                set_lines = [line.rstrip(',\n') for line in set_file]
                set_properties = dict([(k, v) for k, v
                                      in (dict(properties.split(',')
                                          for properties
                                          in set_lines)).items()
                                      if has_numeric_value(v)])
                new_item['set'] = set_properties['setName']

        # Calculate requirements where needed
        if 'itemCostName' in item_properties:
            cost_prefix = item_properties['Class'].split('_')[1]
            cost_prefix = cost_prefix[0:1].lower() + cost_prefix[1:]

            # Open cost file
            with open(db_dir + item_properties['itemCostName']) as cost_file:
                cost_lines = [line.rstrip(',\n') for line in cost_file]
                cost_properties = dict([(k, v) for k, v
                                       in (dict(properties.split(',')
                                           for properties
                                           in cost_lines)).items()
                                       if has_numeric_value(v)])

                itemLevel = item_properties['itemLevel']

                for requirement in requirements:
                    equation_prefix = cost_prefix + requirement + 'Equation'
                    if(equation_prefix in cost_properties):
                        equation = cost_properties[equation_prefix]

                        # Set the possible parameters in the equation:
                        totalAttCount = len(new_item['properties'])
                        itemLevel = int(new_item['level'])
                        new_item['requirement' + requirement] = (
                            round(eval(equation)))

        if(item_properties['Class'] in items):
            items[item_properties['Class']].append(new_item)
        else:
            items[item_properties['Class']] = [new_item]

        # Check bitmap:
        if bmp_dir and 'bitmap' in item_properties:
            bitmap = str(bmp_dir + item_properties['bitmap'])
            command = ['utils/textureviewer/TextureViewer.exe', bitmap,
                       'output/uibitmaps/' + new_item['tag'] + '.png']
            subprocess.run(command,
                           stdout=subprocess.PIPE,
                           stderr=subprocess.PIPE)

for relic_file in relic_files:
    with open(relic_file) as relic:
        # DBR file into a list of lines
        lines = [line.rstrip(',\n') for line in relic]

        # Parse line into a dictionary of key, value properties:
        item_properties = dict([(k, v) for k, v in (dict(properties.split(',')
                               for properties in lines)).items()
                               if has_numeric_value(v)])

        # Parse the difficulty and act from the filename:
        file_meta = os.path.basename(relic_file).split('_')

        new_item = dict()
        new_item['tag'] = item_properties['description']
        new_item['name'] = tags[item_properties['description']]
        new_item['description'] = tags[item_properties['itemText']]
        new_item['properties'] = parse_tiered_properties(item_properties)
        new_item['difficulty'] = difficulties[int(file_meta[0][1:]) - 1]
        new_item['act'] = file_meta[1]

        # Parse the possible completion bonuses:
        completion_bonuses = list()
        try:
            with open(db_dir + item_properties['bonusTableName'])
            as relic_bonus:
                relic_bonus_lines = [line.rstrip(',\n') for line
                                     in relic_bonus]
                relic_bonus_properties = dict([(k, v) for k, v
                                              in (dict(properties.split(',')
                                                  for properties
                                                  in relic_bonus_lines))
                                              .items()
                                              if has_numeric_value(v)])

                bonuses = dict()
                weights = dict()
                for field, value in relic_bonus_properties.items():
                    if 'randomizerName' in field:
                        number = re.search(r'\d+', field).group()
                        bonuses[number] = value
                    if 'randomizerWeight' in field:
                        number = re.search(r'\d+', field).group()
                        weights[number] = int(value)

                total_weight = sum(weights.values())

                for field, value in bonuses.items():
                    if field in weights:
                        with open(db_dir + value) as bonus:
                            bonus_lines = [line.rstrip(',\n') for line
                                           in bonus]
                            bonus_properties =
                            dict([(k, v) for k, v
                                  in (dict(properties.split(',') for properties
                                      in bonus_lines)).items()
                                  if has_numeric_value(v)])

                            completion_bonus = dict()
                            completion_bonus['chance'] = '{0:.2f}'.format(
                                (weights[field] / total_weight) * 100)
                            completion_bonus['bonus'] = parse_properties(
                                bonus_properties)

                            completion_bonuses.append(completion_bonus)

                new_item['bonus'] = completion_bonuses
        except FileNotFoundError:
            new_item['bonus'] = []

        if(item_properties['Class'] in items):
            items[item_properties['Class']].append(new_item)
        else:
            items[item_properties['Class']] = [new_item]

        # Check bitmap:
        if bmp_dir and 'relicBitmap' in item_properties:
            bitmap = str(bmp_dir + item_properties['relicBitmap'])
            command = ['utils/textureviewer/TextureViewer.exe', bitmap,
                       'output/uibitmaps/' + new_item['tag'] + '.png']
            subprocess.run(command,
                           stdout=subprocess.PIPE,
                           stderr=subprocess.PIPE)

for scroll_file in scroll_files:
    with open(scroll_file) as scroll:
        # DBR file into a list of lines
        lines = [line.rstrip(',\n') for line in scroll]

        # Parse line into a dictionary of key, value properties:
        item_properties = dict([(k, v) for k, v in (
            dict(properties.split(',') for properties in lines)).items()
            if has_numeric_value(v)])

        new_item = dict()
        new_item['tag'] = item_properties['description']
        new_item['name'] = tags[item_properties['description']]
        new_item['description'] = tags[item_properties['itemText']]

        # Grab skill
        scroll_skill = skills[item_properties['skillName'].lower().replace(
            '\\', '_').replace(' ', '_')]
        if 'properties' in scroll_skill:
            scroll_meta = os.path.basename(scroll_file).split('_')
            scroll_skill_index = int(scroll_meta[0][1:2]) - 1 if (
                'x' not in scroll_meta[0]) else 0

            new_item['properties'] = (
                scroll_skill['properties'][scroll_skill_index]
                if len(scroll_skill['properties']) > scroll_skill_index
                else scroll_skill['properties'][0])

        if(item_properties['Class'] in items):
            items[item_properties['Class']].append(new_item)
        else:
            items[item_properties['Class']] = [new_item]

        # Check bitmap:
        if bmp_dir and 'bitmap' in item_properties:
            bitmap = str(bmp_dir + item_properties['bitmap'])
            command = ['utils/textureviewer/TextureViewer.exe', bitmap,
                       'output/uibitmaps/' + new_item['tag'] + '.png']
            subprocess.run(command,
                           stdout=subprocess.PIPE,
                           stderr=subprocess.PIPE)

# for artifact_file in artifact_files:
#   with open(artifact_file) as artifact:
#       #DBR file into a list of lines
#       lines = [line.rstrip(',\n') for line in artifact]

#       #Parse line into a dictionary of key, value properties:
#       item_properties = dict([(k,v) for k,v in (dict(properties.split(',')
#       for properties in lines)).items()  if has_numeric_value(v)])

#       #Parse the difficulty and act from the filename:
#       file_meta = os.path.basename(artifact_file).split('_')

#       new_item = dict()
#       new_item['tag'] = item_properties['description']
#       new_item['name'] = tags[item_properties['description']]
#       new_item['classification'] = item_properties['artifactClassification']
#       new_item['difficulty'] = artifact_difficulties[file_meta[1]]

#       #Check bitmap:
#       if bmp_dir and  'artifactBitmap' in item_properties:
#           bitmap = str(bmp_dir + item_properties['artifactBitmap'])
#           command = ['utils/textureviewer/TextureViewer.exe', bitmap,
#                      'output/uibitmaps/' + new_item['tag'] + '.png']
#           subprocess.run(command)


with open('output/items.json', 'w') as items_file:
    json.dump(items, items_file)

print('Items were stored in items.json in the output folder')
if bmp_dir:
    print('Converted bitmaps were saved to output/uibitmaps')
