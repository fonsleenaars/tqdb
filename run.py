import json
import glob
from tqdb.constants import resources as res
from tqdb.parsers.boss import BossLootParser
from tqdb.parsers.equipment import SetParser
from tqdb.parsers.main import parser
from tqdb.parsers.util import format_path
from tqdb.storage import equipment, skills

# Prepare DBR files:
affix_files = []
for affix_file in res.AFFIXES:
    affix_files.extend(glob.glob(res.DB + affix_file, recursive=True))

affix_table_files = []
for table_file in res.AFFIX_TABLES:
    affix_table_files.extend(glob.glob(res.DB + table_file, recursive=True))

boss_files = []
for boss_file in res.CREATURES:
    boss_files.extend(glob.glob(res.DB + boss_file, recursive=True))

equipment_files = []
for equipment_file in res.EQUIPMENT:
    equipment_files.extend(glob.glob(res.DB + equipment_file, recursive=True))

set_files = []
for set_file in res.SETS:
    set_files.extend(glob.glob(res.DB + set_file, recursive=True))

skill_files = []
for skill_file in res.SKILLS:
    skill_files.extend(glob.glob(res.DB + skill_file, recursive=True))

# Parse affixes
affixes = {'prefixes': {}, 'suffixes': {}}
for dbr in affix_files:
    affix = parser.parse(dbr)

    # Add affixes to their respective pre- or suffix list:
    affixType = 'prefixes' if 'Prefix' in affix['tag'] else 'suffixes'
    affixTag = affix['tag']

    # Remove the tag property now
    del(affix['tag'])

    # Either add the affix or add its properties as an alternative
    if affixTag in affixes:
        affixes[affixType][affixTag]['options'].extend(affix['options'])
    else:
        affixes[affixType][affixTag] = affix

# Parse skills
for dbr in skill_files:
    skills.update(parser.parse(dbr))

# Parse equipment
items = {}
for dbr in equipment_files:
    parsed, category = parser.parse(dbr, include_type=True)

    # The equipment files have some unwanted files, check for classification:
    if not parsed or 'classification' not in parsed:
        continue

    # Add to the global equipment list:
    equipment[format_path(dbr.replace(res.DB, ''))] = parsed

    # Organize the equipment based on the category (chest armor, necklace, etc)
    if category and category in items:
        items[category].append(parsed)
    elif category:
        items[category] = [parsed]

# Parse sets:
sets = {}
for dbr in set_files:
    set_tag, set_parsed = SetParser(dbr).parse()

    # Add this set to all set items:
    for item_tag in set_parsed['items']:
        # Find the item:
        for haystack in items.values():
            needle = list(filter(lambda x: x['tag'] == item_tag, haystack))
            if needle:
                needle[0]['set'] = set_tag

    sets[set_tag] = set_parsed

bosses = {}
for dbr in boss_files:
    bossTag, boss = BossLootParser(dbr).parse()

    # Add new bosses:
    if (bossTag and bossTag not in bosses) or (
            bossTag in bosses and not bosses[bossTag]['chest']):
        bosses[bossTag] = boss

# Gather all data:
data = {
    'affix': affixes,
    'equipment': items,
    'sets': sets,
    'skills': skills,
    'bosses': bosses,
}

with open('output/data.json', 'w') as data_file:
    json.dump(data, data_file)
