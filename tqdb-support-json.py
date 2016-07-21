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

skills = dict()
files = glob.glob(db_dir + '\\records\\skills\\*\\*.dbr', recursive=True)
files.extend(glob.glob(db_dir + '\\records\\xpack\\skills\\*\\*.dbr', recursive=True))

for file in files:
	with open(file) as skillData:
		#DBR file into a list of lines
		lines = [line.rstrip(',\n') for line in skillData]

		#Parse line into a dictionary of key, value properties:
		skill_properties = dict([(k,v) for k,v in (dict(properties.split(',') for properties in lines)).items()  if has_numeric_value(v)])

		buff_or_pet = ['buffSkillName', 'petSkillName']
		required = ['skillDisplayName'] + buff_or_pet
		if not any (key in skill_properties for key in required):
			continue

		#Prepare the file key (remove prefix and change all slashes and spaces to _)
		file_key = (file.replace(db_dir + '\\', '')).lower()
		file_key = file_key.replace('\\', '_')
		file_key = file_key.replace(' ', '_')

		#If this file is simply the buff or pet reference, prepare the index:
		if any (key in skill_properties for key in buff_or_pet):
			field = 'buffSkillName' if 'buffSkillName' in skill_properties else 'petSkillName'
			field_value = skill_properties[field].replace('\\', '_').lower()
			field_value = field_value.replace(' ', '_')

			#Check if an index is already prepare by a buff or pet:
			for existingKey, skill in skills.items():
				if any (key in skill for key in buff_or_pet):
					field = 'buffSkillName' if 'buffSkillName' in skill else 'petSkillName'
					if(skill[field] == file_key):
						file_key = existingKey			
			
			if(file_key not in skills):
				skills[file_key] = { field : field_value }
			else:
				skills[file_key][field] = field_value
		else:
			skill_key = file_key

			#Check if an index is already prepare by a buff or pet:
			for existingKey, skill in skills.items():
				if any (key in skill for key in buff_or_pet):
					field = 'buffSkillName' if 'buffSkillName' in skill else 'petSkillName'
					if(skill[field] == file_key):
						skill_key = existingKey

			#If skill isn't stored yet, create a new entry
			if skill_key not in skills:
				skills[skill_key] = dict()

			#Store the properties and tag and name
			if skill_properties['skillDisplayName'] not in tags:
				skills[skill_key]['tag'] = ''
				skills[skill_key]['name'] = skill_properties['skillDisplayName']
			else:
				skills[skill_key]['tag'] = skill_properties['skillDisplayName']
				skills[skill_key]['name'] = tags[skill_properties['skillDisplayName']]

			skills[skill_key]['properties'] = parse_tiered_properties(skill_properties)

			#Store max levels or requirements, if available
			if('skillMasteryLevelRequired' in skill_properties):
				skills[skill_key]['requiredMastery'] 	= skill_properties['skillMasteryLevelRequired']
				skills[skill_key]['skillMaxLevel'] 		= skill_properties['skillMaxLevel']

			if('skillUltimateLevel' in skill_properties):
				skills[skill_key]['skillUltimateLevel'] 	= skill_properties['skillUltimateLevel']

with open('output/skills.json', 'w') as skillsFile:
	json.dump(skills, skillsFile)	

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
			try:
				with open(db_dir + member) as member_file:
					member_lines = [line.rstrip(',\n') for line in member_file]
					member_properties = dict([(k,v) for k,v in (dict(properties.split(',') for properties in member_lines)).items() if has_numeric_value(v)])
					member_tag = member_properties['itemNameTag']
					set_dict['members'].append({ 'tag' : member_tag, 'name' : tags[member_tag] })
			except FileNotFoundError:
				set_dict['members'].append({ 'tag': member, 'name' : 'Could not be found.' })
				
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