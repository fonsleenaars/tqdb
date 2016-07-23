import glob
import json
import argparse
import os

from dbr_parser import *

#Parse command line call 
parser = argparse.ArgumentParser(description='Create supporting JSON to parse all Titan Quest equipment into a single file.')
parser.add_argument('text', type=str, help='Directory that the text_en.arc is extracted to')
parser.add_argument('records', type=str, help='Directory that the database.arz is extracted to')
args = parser.parse_args()
text_dir = os.path.join(args.text, '')
db_dir = os.path.join(args.records, '')

#Files to include in the tag dictionary:
tag_files = [
	text_dir + '\\commonequipment.txt',
	text_dir + '\\monsters.txt',
	text_dir + '\\skills.txt',
	text_dir + '\\uniqueequipment.txt',
	text_dir + '\\xcommonequipment.txt',
	text_dir + '\\xmonsters.txt',
	text_dir + '\\xuniqueequipment.txt',
	text_dir + '\\xskills.txt'	
]

#Prepare the tag dictionary
tags = dict()

for tag_file in tag_files:
	with open(tag_file, encoding='utf16', errors='ignore') as file:
		# Read the file and parse the tags into key, values:
		lines = [str(line.rstrip('\n')) for line in file]
		tags.update(dict(properties.split('=') for properties in lines if(properties != '' and properties[0] != '/')))

#Output all tags to JSON
with open('output/tags.json', 'w') as tagsFile:
	json.dump(tags, tagsFile)

skill_files = [
	'\\skills\\defensive\\*.dbr',
	'\\skills\\earth\\*.dbr',
	'\\skills\\hunting\\*.dbr',
	'\\skills\\item skills\\*.dbr',
	'\\skills\\nature\\*.dbr',
	'\\skills\\spirit\\*.dbr',
	'\\skills\\stealth\\*.dbr',
	'\\skills\\storm\\*.dbr',
	'\\skills\\warfare\\*.dbr',
	'\\xpack\\skills\\artifactskills\\*.dbr',
	'\\xpack\\skills\\dream\\*.dbr',
	'\\xpack\\skills\\equipment skills\\*.dbr',
	'\\xpack\\skills\\scroll skills\\*.dbr'
]

skills = dict()
files = []
for skill_file in skill_files:
	files.extend(glob.glob(db_dir + '\\records' + skill_file, recursive=True))

files = [ file for file in files if "\\old\\" not in file ]

#Prepare some reference values:
buff_or_pet = ['buffSkillName', 'petSkillName']
spawned 	= ['spawnObjects']
all_refs	= buff_or_pet + spawned

#First iterate over all the files and map all normal skills, and reference files (buffs, petskills, summons)
for file in files:
	with open(file) as skill_data:
		#DBR file into a list of lines
		lines = [line.rstrip(',\n') for line in skill_data]

		#Parse line into a dictionary of key, value properties:
		skill_properties = dict([(k,v) for k,v in (dict(properties.split(',') for properties in lines)).items() if has_numeric_value(v)])
		skill_name = skill_properties['skillDisplayName'] if 'skillDisplayName' in skill_properties else None
		skill_desc = skill_properties['skillBaseDescription'] if 'skillBaseDescription' in skill_properties else None
		
		if not skill_name and not skill_desc and not any (key in skill_properties for key in all_refs) and not 'scroll' in file:
			continue

		file_key = file.replace(db_dir + '\\', '').lower().replace('\\', '_').replace(' ', '_')
		#If this file is simply the buff or pet reference, prepare the index:
		if 'buffSkillName' in skill_properties:
			buff_key = skill_properties['buffSkillName'].replace(db_dir + '\\', '').lower().replace('\\', '_').replace(' ', '_')
			if(file_key not in skills):
				skills[file_key] = { 'buffSkillName' : buff_key }
			else:
				skills[file_key]['buffSkillName'] = buff_key
		elif 'petSkillName' in skill_properties and file_key not in skills:
			pet_skill_key = skill_properties['petSkillName'].replace(db_dir + '\\', '').lower().replace('\\', '_').replace(' ', '_')
			skills[pet_skill_key] = {}
		elif skill_name and 'spawnObjects' in skill_properties:
			spawn_file = skill_properties['spawnObjects']

			skills[file_key] = dict()
			if ';' in spawn_file:
				skills[file_key]['tag'] = skill_properties['skillDisplayName'] if skill_name else ''
				skills[file_key]['name'] = tags[skill_properties['skillDisplayName']] if skill_name in tags else skill_name
			else:
				skills[file_key]['spawnObjects'] = spawn_file
				skills[file_key]['spawnObjectsTimeToLive'] = skill_properties.get('spawnObjectsTimeToLive', '')
		else:
			#Check if this file key is set as a buffSkillName:
			file_key = next((key for key, skill in skills.items() if 'buffSkillName' in skill and skill['buffSkillName'] == file_key), file_key)
			
			if file_key not in skills:
				skills[file_key] = {}

			#Store the properties and tag and name
			skills[file_key]['tag'] = skill_name if skill_name in tags else ''
			skills[file_key]['name'] = tags.get(skill_name, '')
			skills[file_key]['description'] = tags[skill_desc] if skill_desc in tags else skill_desc
			skills[file_key]['properties'] = parse_tiered_properties(skill_properties)

			#Store max levels or requirements, if available
			if 'skillMasteryLevelRequired' in skill_properties:
				skills[file_key]['skillMasteryLevelRequired'] = skill_properties['skillMasteryLevelRequired']

			if 'skillMaxLevel' in skill_properties:
				skills[file_key]['skillMaxLevel'] = skill_properties['skillMaxLevel']

			if 'skillUltimateLevel' in skill_properties:
				skills[file_key]['skillUltimateLevel'] = skill_properties['skillUltimateLevel']

#Now iterate through the list and fetch any buffs/petskills/spawns:
for file_key, skill in skills.items():
	if 'tag' in skill:
		continue

	if  'spawnObjects' in skill and ';' not in skill['spawnObjects']:
		skill_field = skill['spawnObjects']

		#Open reference files for spawning:
		with open(db_dir + skill_field) as spawn_file:
			#DBR file into a list of lines
			lines = [line.rstrip(',\n') for line in spawn_file]

			#Parse line into a dictionary of key, value properties:
			skill_properties = dict([(k,v) for k,v in (dict(properties.split(',') for properties in lines)).items()  if has_numeric_value(v)])
			skill_name = skill_properties['description']
			if skill_name not in tags:
				continue

			skill['tag'] = skill_properties['description']
			skill['name'] = tags[skill_properties['description']]

			if 'specialAttackSkillName' in skill_properties:
				with open(db_dir + skill_properties['specialAttackSkillName']) as special_attack:
					#DBR file into a list of lines
					attack_lines = [line.rstrip(',\n') for line in special_attack]

					#Parse line into a dictionary of key, value properties:
					attack_properties = dict([(k,v) for k,v in (dict(properties.split(',') for properties in attack_lines)).items()  if has_numeric_value(v)])

					skill['properties'] = parse_tiered_properties(attack_properties)


	# elif any (key in skill for key in buff_or_pet):
	# 	skill_field = 'buffSkillName' if 'buffSkillName' in skill else 'petSkillName'

	# 	try:
	# 		with open(db_dir + skill[skill_field]) as skill_file:
	# 			#DBR file into a list of lines
	# 			lines = [line.rstrip(',\n') for line in skill_file]

	# 			#Parse line into a dictionary of key, value properties:
	# 			skill_properties = dict([(k,v) for k,v in (dict(properties.split(',') for properties in lines)).items()  if has_numeric_value(v)])

	# 			if 'skillDisplayName' in skill_properties:
	# 				skill_name = skill_properties['skillDisplayName'];
	# 				if skill_name not in tags:
	# 					continue

	# 				skill['tag'] = skill_name
	# 				skill['name'] = tags[skill_name]
	# 			if 'skillBaseDescription' in skill_properties:
	# 				skill_description = skill_properties['skillBaseDescription']
	# 				skill['description'] = tags[skill_description] if skill_description in tags else skill_description

	# 			skill['properties'] = parse_tiered_properties(skill_properties)
	# 	except FileNotFoundError:
	# 		continue

# #Remove all skill entries that don't have a key:
# result = { k:v for k,v in skills.items() if 'tag' in v and v['tag'] }

with open('output/skills.json', 'w') as skills_file:
	json.dump(skills, skills_file)	

#Prepare the set dictionary
sets = dict()

#Load the sets
files = glob.glob(db_dir + '\\records\\item\\sets\\*.dbr')
files.extend(glob.glob(db_dir + '\\records\\xpack\\item\\sets\\*.dbr'))

for file in files: 
	with open(file) as setData:
		#DBR file into a list of lines
		lines = [line.rstrip(',\n') for line in setData]

		#Parse line into a dictionary of key, value properties:
		set_properties = dict([(k,v) for k,v in (dict(properties.split(',') for properties in lines)).items()  if has_numeric_value(v)])

		set_dict = dict()
		set_dict['name'] = tags[set_properties['setName']]

		#Add members
		set_dict['members'] = []
		for member in set_properties['setMembers'].split(';'):
			if 'equipment' not in member.lower():
				continue;

			try:
				with open(db_dir + member) as member_file:
					member_lines = [line.rstrip(',\n') for line in member_file]
					member_properties = dict([(k,v) for k,v in (dict(properties.split(',') for properties in member_lines)).items() if has_numeric_value(v)])
					member_tag = member_properties['itemNameTag']
					set_dict['members'].append({ 'tag' : member_tag, 'name' : tags[member_tag] })
			except FileNotFoundError:
				set_dict['members'].append({ 'tag': member, 'name' : 'Could not be found.' })

		#If this set has no members; remove it:
		if len(set_dict['members']) == 0:
			continue;
				
		#Add set bonuses
		set_dict['bonuses'] = parse_tiered_properties(set_properties)

		if(len(set_dict['bonuses']) > 1):
			if(not set_dict['bonuses'][0]):
				set_dict['bonuses'].pop(0)

		#Add set to sets dictionary
		sets[set_properties['setName']] = set_dict

#Output all sets to JSON
with open('output/sets.json', 'w') as setsFile:
	json.dump(sets, setsFile)