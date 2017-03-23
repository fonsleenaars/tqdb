import glob
import json
from tqdb.constants import resources as res
from tqdb.parsers.main import parser
from tqdb.storage import missing
from tqdb.storage import skills


# Prepare DBR files:
equipment_files = []
for equipment_file in res.EQUIPMENT:
    equipment_files.extend(glob.glob(res.DB + equipment_file, recursive=True))

skill_files = []
for skill_file in res.SKILLS:
    skill_files.extend(glob.glob(res.DB + skill_file, recursive=True))

# Parse skills
for i, dbr in enumerate(skill_files):
    skills.update(parser.parse(dbr))

# Parse equipment
equipment = {}
for i, dbr in enumerate(equipment_files):
    parsed, category = parser.parse(dbr, include_type=True)

    # Organize the equipment based on the category (chest armor, necklace, etc)
    if parsed and category and category in equipment:
        equipment[category].append(parsed)
    elif parsed and category:
        equipment[category] = [parsed]

# Gather all data:
data = {
    'equipment': equipment,
    'skills': skills,
}

with open('output/data.json', 'w') as data_file:
    json.dump(data, data_file)

import pprint
pprint.PrettyPrinter().pprint(missing)
