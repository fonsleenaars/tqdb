import json
import pprint

#Value formatting defaults
val_dur_for 		= ' for {0:.1f} Second(s)'
val_dur_improved	= ' with +{0:.0f}% Improved Duration'
val_dur_over 		= ' over {0:.1f} Second(s)'
val_int 			= '{0:.0f}'
val_int_signed		= '{0:+.0f}'
val_float			= '{0:.1f}'
val_modifier 		= '{0:+.0f}%'
val_range			= '{0:.0f} ~ {1:.0f}'
val_range_dec		= '{0:.1f} ~ {1:.1f}'
val_reduction 		= '-{0:.0f}%'

character_stat_fields = {
	'Strength' : 						{ 'suffix' : ' Strength' },
	'Dexterity' : 						{ 'suffix' : ' Dexterity' },
	'Intelligence' : 					{ 'suffix' : ' Intelligence' },
	'Life' : 							{ 'suffix' : ' Health' },
	'Mana' : 							{ 'suffix' : ' Energy' },
	'IncreasedExperience' :				{ 'suffix' : '% Increased Experience' },
	'AttackSpeed' : 					{ 'suffix' : ' Attack Speed' },
	'RunSpeed' : 						{ 'suffix' : ' Movement Speed' },
	'SpellCastSpeed' : 					{ 'suffix' : ' Casting Speed' },
	'TotalSpeed' :						{ 'suffix' : ' Total Speed' },
	'LifeRegen' : 						{ 'suffix' : ' Health Regeneration per second', 'modifier' : ' Health Regeneration', 'format_flat' : '{0:+.1f}' },
	'ManaRegen' : 						{ 'suffix' : ' Energy Regeneration per second', 'modifier' : ' Energy Regeneration', 'format_flat' : '{0:+.1f}' }, 
	'OffensiveAbility' :				{ 'suffix' : ' Offensive Ability' },
	'DefensiveAbility' : 				{ 'suffix' : ' Defensive Ability' },
	'DefensiveBlockRecoveryReduction' : { 'suffix' : ' Defensive Ability' },
	'EnergyAbsorptionPercent' : 		{ 'suffix' : ' Absorption of Spell Energy', 'format_flat' : '+{0:.0f}%' },
	'DodgePercent' : 					{ 'suffix' : ' Chance to Dodge Attacks', 'format_flat' : '{0:.0f}%' },
	'DeflectProjectile' : 				{ 'suffix' : ' Chance to Avoid Projectiles', 'format_flat' : '{0:.0f}%' },
	'ManaLimitReserve' : 				{ 'suffix' : ' Energy Reserved' },
	'ManaLimitReserveReduction' : 		{ 'suffix' : ' less Energy Reserved' },
}

character_requirement_redux = {
	'GlobalReq' : 				' Reduction to all Requirements',
	'WeaponStrength' : 		' Strength Requirement for all Weapons',
	'WeaponDexterity' : 	' Dexterity Requirement for all Weapons',
	'WeaponIntelligence' : 	' Intelligence Requirement for all Weapons',
	'MeleeStrength' : 		' Strength Requirement for Melee Weapons',
	'MeleeDexterity' : 		' Dexterity Requirement for Melee Weapons',
	'MeleeIntelligence' : 	' Intelligence Requirement for Melee Weapons',
	'HuntingStrength' : 	' Strength Requirement for Hunting Weapons',
	'HuntingDexterity' : 	' Dexterity Requirement for Hunting Weapons',
	'HuntingIntelligence' : ' Intelligence Requirement for Hunting Weapons',
	'ShieldStrength' : 		' Strength Requirement for Shields',
	'ShieldDexterity' : 	' Dexterity Requirement for Shields',
	'ShieldIntelligence' :	' Intelligence Requirement for Shields',
	'ArmorStrength' : 		' Strength Requirement for Armor',
	'ArmorDexterity' : 		' Dexterity Requirement for Armor',
	'ArmorIntelligence' : 	' Intelligence Requirement for Armor',
	'JewelryStrength' : 	' Strength Requirement for Jewelry',
	'JewelryDexterity' : 	' Dexterity Requirement for Jewelry',
	'JewelryIntelligence' : ' Intelligence Requirement for Jewelry',
	'Level'	:				' Player Level Requirement for Items'
}

defensive_absolute = {
	'Protection' : 			{ 'flat' : ' Armor', 'modifier' : '% Armor Protection', 'format_modifier' : val_int_signed },
	'Absorption' : 			{ 'flat' : '% Armor Absorption' },
	'Physical' : 			{ 'flat' : '% Physical Resistance', 'duration' : '% Reduction in Physical Duration', 'duration_modifier' : '% Wound Duration Reduction' },
	'Pierce' : 				{ 'flat' : '% Pierce Resistance' },
	'Fire' : 				{ 'flat' : '% Fire Resistance', 'duration' : '% Reduction in Burn Duration', 'duration_modifier' : '% Burn Duration Reduction' },
	'Cold' : 				{ 'flat' : '% Cold Resistance', 'duration' : '% Reduction in Frostburn Duration', 'duration_modifier' : '% Frostburn Duration Reduction' },
	'Lightning' : 			{ 'flat' : '% Lightning Resistance', 'duration' : '% Reduction in Electrical Burn Duration', 'duration_modifier' : '% Electrical Burn Duration Reduction' },
	'Poison' : 				{ 'flat' : '% Poison Resistance', 'duration' : '% Reduction in Poison Duration', 'duration_modifier' : '% Poison Duration Reduction' },
	'Life' : 				{ 'flat' : '% Vitality Damage Resistance', 'duration' : '% Reduction in Vitality Decay Duration', 'duration_modifier' : '% Vitality Decay Duration Reduction' },
	'Disruption' : 			{ 'flat' : '% Skill Disruption Resistance' },
	'ElementalResistance' :	{ 'flat' : '% Elemental Resistance' },
	'SlowLifeLeach' : 		{ 'flat' : '% Life Leech Resistance', 'duration' : '% Reduction in Life Leech Duration', 'duration_modifier' : '% Life Leech Duration Reduction' },
	'SlowManaLeach' : 		{ 'flat' : '% Energy Leech Resistance', 'duration' : '% Reduction in Energy Leech Duration', 'duration_modifier' : '% Energy Leech Reduction' },
	'Bleeding' : 			{ 'flat' : '% Bleeding Resistance', 'duration' : '% Reduction in Bleeding Duration', 'duration_modifier' : '% Bleeding Duration Reduction' },
	'BlockModifier' : 		{ 'flat' : '% Shield Block', 'format_flat' : val_int_signed, 'format_modifier': val_int_signed },
	'Reflect' :				{ 'flat' : '% Damage Reflected' },
	'Confusion' : 			{ 'flat' : '% Reduced Confusion Duration (Pet/Trap Only)' },
	'Taunt' : 				{ 'flat' : '% Protection from Taunting (Pet/Trap Only)' },
	'Fear' : 				{ 'flat' : '% Reduced Fear Duration (Pet/Trap Only)' },
	'Convert' : 			{ 'flat' : '% Reduced Mind Control Duration (Pet/Trap Only)' },
	'Trap' : 				{ 'flat' : '% Reduced Entrapment Duration' },
	'Petrify' : 			{ 'flat' : '% Reduced Petrify Duration' },
	'Freeze' : 				{ 'flat' : '% Reduced Freeze Duration' },
	'Stun' : 				{ 'flat' : '% Stun Resistance' },
	'Sleep' : 				{ 'flat' : '% Sleep Resistance' }
}

defensive_shield = '{0:.0f}% Chance to Block {1:.0f} Damage'

offensive_absolute_damage = {
	'BaseCold' :			{ 'suffix' : ' Base Cold Damage' },
	'BaseFire' :			{ 'suffix' : ' Base Fire Damage' },
	'BaseLightning' :		{ 'suffix' : ' Base Lightning Damage' },
	'BasePoison' : 			{ 'suffix' : ' Base Poison Damage' },
	'BaseLife' : 			{ 'suffix' : ' Base Vitality Damage' },
	'PierceRatio' : 		{ 'suffix' : '% Piercing', 'modifier': ' Piercing' },
	'BonusPhysical' : 		{ 'suffix' : ' Bonus Damage' },
	'Physical' : 			{ 'suffix' : ' Damage', 'modifier': ' Physical Damage' },
	'Pierce' : 				{ 'suffix' : ' Pierce Damage' },
	'Cold' : 				{ 'suffix' : ' Cold Damage' },
	'Fire' : 				{ 'suffix' : ' Fire Damage' },
	'Poison' : 				{ 'suffix' : ' Poison Damage' },
	'Lightning' : 			{ 'suffix' : ' Lightning Damage' },
	'Life' : 				{ 'suffix' : ' Vitality Damage' },
	'PercentCurrentLife' : 	{ 'suffix' : '% Reduction to Enemy\'s health' },
	'Disruption' : 			{ 'suffix' : ' second(s) of Skill Disruption', 'format_flat' : val_float, 'format_range' : val_range_dec },
	'LifeLeech' : 			{ 'suffix' : '% of Attack damage converted to Health' },
	'Elemental' : 			{ 'suffix' : ' Elemental Damage' },
	'TotalDamage' : 		{ 'suffix' : ' Total Damage' },
}

offensive_duration_damage = {	
	'SlowPhysical' : ' Crush Damage',
	'SlowBleeding' : ' Bleeding Damage',
	'SlowCold' : ' Frostburn Damage',
	'SlowFire' : ' Burn Damage',
	'SlowPoison' : ' Poison Damage',
	'SlowLightning' : ' Electrical Burn Damage',
	'SlowLife' : ' Vitality Decay',
	'SlowLifeLeach' : ' Life Leech',
	'SlowManaLeach' : ' Energy Leech'
}

offensive_duration_effects = {
	'SlowTotalSpeed' 					: '% Slowed',
	'SlowAttackSpeed' 					: '% Slower Attack',
	'SlowSpellCastSpeed' 				: '% Slow Casting',
	'SlowRunSpeed' 						: { 'flat' : '% Slower Movement', 'modifier': ' Slow Movement'},
	'SlowOffensiveAbility' 				: '% Reduced Offensive Ability',
	'SlowDefensiveAbility' 				: '% Reduced Defensive Ability',
	'SlowOffensiveReduction' 			: '% Reduced Physical Damage',
	'SlowDefensiveReduction' 			: ' Reduced Armor',
	'TotalDamageReductionPercent' 		: '% Reduced Damage',	
	'TotalDamageReductionAbsolute'		: ' Reduced Damage',
	'TotalResistanceReductionPercent' 	: '% Reduced Resistance',
	'TotalResistanceReductionAbsolute' 	: ' Reduced Resistance',
	'Fumble' 							: '% Chance to Fumble attacks',
	'ProjectileFumble' 					: '% Chance of Impaired Aim',
	'Convert' 							: ' second(s) of Mind Control',
	'Taunt' 							: ' Taunt',
	'Fear' 								: ' second(s) of Fear',
	'Confusion' 						: ' second(s) of Confusion',
	'Trap' 								: ' second(s) of Immobilization',
	'Freeze' 							: ' second(s) of Freeze',
	'Petrify' 							: ' second(s) of Petrify',
	'Stun' 								: { 'flat' : ' second(s) of Stun', 'modifier' : ' Stun Duration' },
	'Sleep' 							: ' second(s) of Sleep'
}

offensive_mana_drain	  = { 'suffix' : '% Energy Drained', 'ratio' : ' ({0:.0f}% Energy Drained Causes Damage)' }

racialBonusesFields = { 
	'racialBonusAbsoluteDamage' : '+{0:.0f} Damage to {1}', 
	'racialBonusAbsoluteDefense' : '{0:.0f} Less Damage from {1}', 
	'racialBonusPercentDamage' : '+{0:.0f}% Damage to {1}',
	'racialBonusPercentDefense' : '{0:.0f}% Less Damage from {1}'
}

retaliation_absolute_damage = {
	'Physical' : 			{ 'flat' : ' Damage Retaliation', 'modifier' : ' Physical Damage Retaliation' },
	'Pierce' : 				{ 'flat' : ' Piercing Retaliation', 'modifier' : ' Pierce Damage Retaliation' },
	'Cold' : 				{ 'flat' : ' Cold Retaliation', 'modifier' : ' Frostburn Retaliation' },
	'Fire' : 				{ 'flat' : ' Fire Retaliation', 'modifier' : ' Burn Retaliation' },
	'Poison' : 				{ 'flat' : ' Poison Retaliation', 'modifier' : ' Poison Retaliation' },
	'Lightning' : 			{ 'flat' : ' Lightning Retaliation', 'modifier' : ' Lightning Retaliation' },
	'Life' : 				{ 'flat' : ' Vitality Retaliation', 'modifier' : ' Vitality Damage Retaliation' },
	'Stun' :				{ 'flat' : ' second(s) of Stun', 'format_flat' : val_float, 'modifier' : ' Stun Retaliation' },
	'PercentCurrentLife' : 	{ 'flat' : '% Health Reduction Retaliation' },
	'Elemental' : 			{ 'flat' : ' Elemental Retaliation' },
}

retaliation_duration_damage = {
	'SlowPhysical' : ' Wound Retaliation',
	'SlowBleeding' : ' Bleeding Damage Retaliation',
	'SlowCold' : ' Frostburn Retaliation',
	'SlowFire' : ' Burn retaliation',
	'SlowPoison' : ' Poison Retaliation',
	'SlowLightning' : ' Electrical Burn Retaliation',
	'SlowLife' : ' Vitality Decay Retaliation',
	'SlowLifeLeach' : ' Life Leech Retaliation',
	'SlowManaLeach' : ' Energy Leech Retaliation'
}

retaliation_duration_effects = {
	'SlowAttackSpeed' 					: '% Slower Attack Retaliation',
	'SlowSpellCastSpeed' 				: '% Slow Casting Retaliation',
	'SlowRunSpeed' 						: '% Slower Movement Retaliation',
	'SlowOffensiveAbility' 				: '% Reduced Offensive Ability Retaliation',
	'SlowDefensiveAbility' 				: '% Reduced Defensive Ability Retaliation',
	'SlowOffensiveReduction' 			: ' Damage Reduction Retaliation'
}

skill_augment_fields = {
	'augmentSkillName1' : 'augmentSkillLevel1',
	'augmentSkillName2' : 'augmentSkillLevel2',
	'augmentMasteryName1' : 'augmentMasteryLevel1',
	'augmentMasteryName2' : 'augmentMasteryLevel2'
}

skill_parameters_fields = {
	'CooldownTime' :			'{0:.0f} Second(s) Recharge',
	'CooldownReduction' : 		'-{0:.0f}% Recharge',
	'ManaCost' : 				'{0:.0f} Energy Cost',
	'ManaCostReduction' : 		'-{0:.0f}% Energy Cost',
	'ProjectileSpeedModifier' : '{0:.0f}% Increase in Projectile Speed',
	'TargetRadius' :			'{0:.0f} Meter Radius'
}

try:
	with open('output/skills.json', 'r') as skillsFile:
		skills = json.load(skillsFile)	
except FileNotFoundError:
	skills = {}

def has_numeric_value(value):
	try:
		float(value)
		return float(value) != 0
	except:
		return True

def has_pet_or_buff(value, expected):
	if 'buffSkillName' in value and value['buffSkillName'] == expected:
		return True
	elif 'petSkillName' in value and value['petSkillName'] == expected:
		return True

	return False

def parse_properties(properties):
	result = dict()

	#Parse Racial bonuses (damage or damage reduction)
	if('racialBonusRace' in properties):
		racialBonuses = properties['racialBonusRace'].split(';')
		for field, text in racialBonusesFields.items():
			if field not in properties:
				continue

			#Set an empty list
			result[field] = []
			values = properties[field].split(';')

			for i in range(0, len(racialBonuses)):
				result[field].append(text.format(float(values[0] if len(racialBonuses) > len(values) else values[i]), racialBonuses[i]))

	#Parse character stat fields:
	for field, text in character_stat_fields.items():
		field_prefix 	= 'character' + field
		field_value 	= properties[field_prefix] if field_prefix in properties else 0
		modifier_prefix = field_prefix + 'Modifier'
		modifier_value  = properties[modifier_prefix] if modifier_prefix in properties else 0

		#Formats
		format_modifier = val_modifier if 'format_modifier' not in text else text['format_modifier']
		format_flat		= val_int_signed if 'format_flat' not in text else text['format_flat']

		if field_value:
			result[field_prefix] = format_flat.format(float(field_value)) + text['suffix']

		if modifier_value:
			suffix = text['modifier'] if 'modifier' in text else text['suffix']
			result[modifier_prefix] = format_modifier.format(float(modifier_value)) + suffix	

	#Parse character reduction requirements:
	for field, text in character_requirement_redux.items():
		field_prefix = 'character' + field + 'Reduction'
		if field_prefix in properties:
			result[field_prefix] = val_reduction.format(float(properties[field_prefix])) + text

	#Parse granted skills:
	if 'itemSkillName' in properties:
		skillTag = properties['itemSkillName'].replace('\\', '_').lower()
		skillTag = skillTag.replace(' ', '_')

		skillName = ''

		if(skillTag not in skills):
			needle = [v['name'] for k, v in skills.items() if has_pet_or_buff(v, skillTag)]
			skillName = needle[0] if needle else ''
		else:
			skillName = skills[skillTag]['name']
			
		result['itemSkillName'] = { 'tag' : skillTag, 'text' : 'Grants skill: ' + skillName }
	

	#Parse individual skill & mastery skill augments:
	for skill, level in skill_augment_fields.items():
		if skill not in properties:
			continue

		#Create the key 
		skillTag = properties[skill].replace('\\', '_').lower()
		skillTag = skillTag.replace(' ', '_')
		skillName = ''

		if(skillTag not in skills):
			needle = [v['name'] for k, v in skills.items() if has_pet_or_buff(v, skillTag)]
			skillName = needle[0] if needle else ''
		else:
			skillName = skills[skillTag]['name']
			
		result[skill] = { 'tag' : skillTag, 'text' : '+{0} to {1}'.format(properties[level], skillName) }

	#Parse augments to all skills
	if 'augmentAllLevel' in properties:
		result['augmentAllLevel'] = '+{0} to All Skills'.format(properties['augmentAllLevel'])

	#Parse skill parameters (cost/cooldown reduction & projectile speed)
	for field, text in skill_parameters_fields.items():
		field_prefix 			= 'skill' + field
		field_value				= float(properties[field_prefix]) if field_prefix in properties else 0
		field_chance_prefix		= field_prefix + 'Chance'
		field_chance 			= float(properties[field_chance_prefix]) if field_chance_prefix in properties else 0

		if field_value:
			result[field_prefix] = [field_chance, text.format(field_value)] if field_chance else text.format(field_value)

	#Parse offensive chances (chance for more than one outcome)
	offensive_chance = 'offensiveGlobalChance' in properties
	offensive_chance_key = 'offensiveChance'
	offensive_chance_property = ['{0:.0f}'.format(float(properties['offensiveGlobalChance']))] if offensive_chance else []

	#Absolute damage
	for field, text in offensive_absolute_damage.items():
		#Store all relevant fields (or set to 0):
		field_prefix 			= 'offensive' + field
		field_chance_prefix		= field_prefix + 'Chance'
		field_chance 			= float(properties[field_chance_prefix]) if field_chance_prefix in properties else 0
		min_prefix 				= field_prefix + 'Min'
		min_damage				= float(properties[min_prefix]) if min_prefix in properties else 0
		max_prefix 				= field_prefix + 'Max'
		max_damage 				= float(properties[max_prefix]) if max_prefix in properties else 0
		modifier_prefix 		= field_prefix + 'Modifier'
		modifier_damage 		= float(properties[modifier_prefix]) if modifier_prefix in properties else 0
		modifier_chance_prefix 	= field_prefix + 'ModifierChance'
		modifier_chance 		= float(properties[modifier_chance_prefix]) if modifier_chance_prefix in properties else 0

		#Formats
		format_modifier = val_modifier if 'format_modifier' not in text else text['format_modifier']
		format_flat		= val_int if 'format_flat' not in text else text['format_flat']
		format_range	= val_range if 'format_range' not in text else text['format_range']

		suffix 			= text['suffix'];
		suffix_modifier = text['modifier'] if 'modifier' in text else text['suffix']

		if (field_prefix + 'Global') in properties:
			#Flat or % is to be included in % chance trigger:
			if (field_prefix + 'XOR') in properties:
				offensive_chance_key = 'offensiveChanceXOR'

				#One of the following properties will trigger (on % chance):
				if modifier_damage:
					offensive_chance_property.append(format_modifier.format(modifier_damage) + suffix_modifier)

					#If flat damage is also set - it's separate from the chance:
					if min_damage:
						result[field_prefix] = (format_range.format(min_damage, max_damage) if max_damage else format_flat.format(min_damage)) + suffix

				elif max_damage and max_damage > min_damage:
					offensive_chance_property.append(format_range.format(min_damage, max_damage) + suffix)
				else:
					offensive_chance_property.append(format_flat.format(min_damage) + suffix)
			else:
				#All set properties will trigger (on % chance):
				if modifier_damage:
					offensive_chance_property.append(format_modifier.format(modifier_damage) + suffix_modifier)

				#Physical is the only exception, the modifier can be chance based, but flat damage is a base stat
				if (field == 'Physical' and 'Weapon' in properties['Class']) or field == 'Pierce':
					damage = format_range.format(min_damage, max_damage) if max_damage else format_flat.format(min_damage)
					damage += suffix
					result[field_prefix] = [field_chance, damage] if field_chance else damage
				elif max_damage and max_damage > min_damage:
					offensive_chance_property.append(format_range.format(min_damage, max_damage) + suffix)
				else:
					offensive_chance_property.append(format_flat.format(min_damage) + suffix)
		else:
			if modifier_damage:
				modifier_damage = format_modifier.format(modifier_damage) + suffix_modifier
				result[modifier_prefix] = [modifier_chance, modifier_damage] if modifier_chance else modifier_damage

			if min_damage:
				damage = format_range.format(min_damage, max_damage) if max_damage else format_flat.format(min_damage)
				damage += suffix
				result[field_prefix] = [field_chance, damage] if field_chance else damage

	#Mana Burn is separate as it has a different structure:
	drain_prefix 		= 'offensiveManaBurn'
	drain_min_prefix 	= drain_prefix + 'DrainMin'
	drain_min			= float(properties[drain_min_prefix]) if drain_min_prefix in properties else 0
	drain_max_prefix 	= drain_prefix + 'DrainMin'
	drain_max			= float(properties[drain_max_prefix]) if drain_max_prefix in properties else 0
	drain_ratio_prefix	= drain_prefix + 'DamageRatio'
	drain_ratio 		= float(properties[drain_ratio_prefix]) if drain_ratio_prefix in properties else 0

	if drain_min:
		damage = val_range.format(drain_min, drain_max) if drain_max and drain_max > drain_min else val_int.format(drain_min)
		drain_total = damage + offensive_mana_drain['suffix'] + (offensive_mana_drain['ratio'].format(drain_ratio) if drain_ratio else '')

		if (drain_prefix + 'Global') in properties:
			offensive_chance_property.append(drain_total)
		else:
			result[drain_prefix] = drain_total

	
	#Damage over time (combine the damage and reductions):
	offensive_duration = dict(offensive_duration_damage, **offensive_duration_effects)
	for field, text in offensive_duration.items():
		#Store all relevant fields (or set to 0):
		field_prefix 			= 'offensive' + field
		field_chance_prefix		= field_prefix + 'Chance'
		field_chance 			= float(properties[field_chance_prefix]) if field_chance_prefix in properties else 0
		duration_min_prefix		= field_prefix + 'DurationMin'
		duration_min 			= float(properties[duration_min_prefix]) if duration_min_prefix in properties else 0
		duration_max_prefix		= field_prefix + 'DurationMax'
		duration_max 			= float(properties[duration_max_prefix]) if duration_max_prefix in properties else 0
		duration_mod_prefix		= field_prefix + 'DurationModifier'
		duration_mod 			= float(properties[duration_mod_prefix]) if duration_mod_prefix in properties else 0
		min_prefix 				= field_prefix + 'Min'
		min_damage				= float(properties[min_prefix]) if min_prefix in properties else 0
		max_prefix 				= field_prefix + 'Max'
		max_damage 				= float(properties[max_prefix]) if max_prefix in properties else 0
		modifier_prefix 		= field_prefix + 'Modifier'
		modifier_damage 		= float(properties[modifier_prefix]) if modifier_prefix in properties else 0
		modifier_chance_prefix 	= field_prefix + 'ModifierChance'
		modifier_chance 		= float(properties[modifier_chance_prefix]) if modifier_chance_prefix in properties else 0

		#Multiply values by duration if needed:
		if(field in offensive_duration_damage):
			if(min_damage and not max_damage and duration_min and duration_max):
				max_damage = min_damage * duration_max
				min_damage = min_damage * duration_min
				duration_max = 0
			elif(min_damage and not max_damage and duration_min):
				min_damage = min_damage * duration_min
			elif(min_damage and max_damage and duration_min):
				min_damage = min_damage * duration_min
				max_damage = max_damage * duration_min

		#Create the suffixes
		modifier_suffix = text if not isinstance(text, dict) else text['modifier']
		modifier_suffix += val_dur_improved.format(duration_mod) if duration_mod_prefix in properties else ''
		damage_suffix = text if not isinstance(text, dict) else text['flat']
		damage_suffix += val_dur_improved.format(duration_mod) if duration_mod_prefix in properties else ''

		if(field in offensive_duration_damage):
			damage_suffix += val_dur_over.format(duration_min) if duration_min_prefix in properties else ''			
		else:
			damage_suffix += val_dur_for.format(duration_min) if duration_min_prefix in properties else ''

		if (field_prefix + 'Global') in properties:
			#Flat or % is to be included in % chance trigger:
			if (field_prefix + 'XOR') in properties:
				offensive_chance_key = 'offensiveChanceXOR'

				#One of the following properties will trigger (on % chance):
				if modifier_damage:
					offensive_chance_property.append(val_modifier.format(modifier_damage) + modifier_suffix)

					if min_damage:
						offensive_chance_property.append((val_range.format(min_damage, max_damage) if max_damage else val_int.format(min_damage)) + damage_suffix)

				elif max_damage and max_damage > min_damage:
					offensive_chance_property.append(val_range.format(min_damage, max_damage) + damage_suffix)
				else:
					offensive_chance_property.append(val_int.format(min_damage) + damage_suffix)
			else:
				#All set properties will trigger (on % chance):
				if modifier_damage:
					offensive_chance_property.append(val_modifier.format(modifier_damage) + modifier_suffix)

				if max_damage and max_damage > min_damage:
					offensive_chance_property.append(val_range.format(min_damage, max_damage) + damage_suffix)
				else:	
					offensive_chance_property.append(val_int.format(min_damage) + damage_suffix)
		else:
			if modifier_damage:
				modifier_damage = val_modifier.format(modifier_damage) + modifier_suffix
				result[modifier_prefix] = [modifier_chance, modifier_damage] if modifier_chance else modifier_damage

			if min_damage:
				damage = val_range.format(min_damage, max_damage) if max_damage else val_int.format(min_damage)
				damage += damage_suffix
				result[field_prefix] = [field_chance, damage] if field_chance else damage

	if offensive_chance and len(offensive_chance_property) > 1:
		result[offensive_chance_key] = offensive_chance_property

	#Parse retaliation chances (chance for more than one outcome)
	retaliation_chance = 'retaliationGlobalChance' in properties
	retaliation_chance_key = 'retaliationChance'
	retaliation_chance_property = ['{0:.0f}'.format(float(properties['retaliationGlobalChance']))] if retaliation_chance else []

	#Retaliation: Absolute damage
	for field, text in retaliation_absolute_damage.items():
		#Store all relevant fields (or set to 0):
		field_prefix 			= 'retaliation' + field
		field_chance_prefix		= field_prefix + 'Chance'
		field_chance 			= float(properties[field_chance_prefix]) if field_chance_prefix in properties else 0
		min_prefix 				= field_prefix + 'Min'
		min_damage				= float(properties[min_prefix]) if min_prefix in properties else 0
		max_prefix 				= field_prefix + 'Max'
		max_damage 				= float(properties[max_prefix]) if max_prefix in properties else 0
		modifier_prefix 		= field_prefix + 'Modifier'
		modifier_damage 		= float(properties[modifier_prefix]) if modifier_prefix in properties else 0
		modifier_chance_prefix 	= field_prefix + 'ModifierChance'
		modifier_chance 		= float(properties[modifier_chance_prefix]) if modifier_chance_prefix in properties else 0

		#Formats
		format_modifier = val_modifier if 'format_modifier' not in text else text['format_modifier']
		format_flat		= val_int if 'format_flat' not in text else text['format_flat']
		format_range	= val_range if 'format_range' not in text else text['format_range']

		if (field_prefix + 'Global') in properties:
			#Flat or % is to be included in % chance trigger:
			if (field_prefix + 'XOR') in properties:
				retaliation_chance_key = 'retaliationChanceXOR'

				#One of the following properties will trigger (on % chance):
				if modifier_damage:
					retaliation_chance_property.append(format_modifier.format(modifier_damage) + text['modifier'])

					#If flat damage is also set - it's separate from the chance:
					if min_damage:
						result[field_prefix] = (format_range.format(min_damage, max_damage) if max_damage else format_flat.format(min_damage)) + text['flat']

				elif max_damage and max_damage > min_damage:
					retaliation_chance_property.append(format_range.format(min_damage, max_damage) + text['flat'])
				else:
					retaliation_chance_property.append(format_flat.format(min_damage) + text['flat'])
			else:
				#All set properties will trigger (on % chance):
				if modifier_damage:
					retaliation_chance_property.append(format_modifier.format(modifier_damage) + text['modifier'])

				if max_damage and max_damage > min_damage:
					retaliation_chance_property.append(format_range.format(min_damage, max_damage) + text['flat'])
				else:
					retaliation_chance_property.append(format_flat.format(min_damage) + text['flat'])
		else:
			if modifier_damage:
				modifier_damage = format_modifier.format(modifier_damage) + text['modifier']
				result[modifier_prefix] = [modifier_chance, modifier_damage] if modifier_chance else modifier_damage

			if min_damage:
				damage = format_range.format(min_damage, max_damage) if max_damage else format_flat.format(min_damage)
				damage += text['flat']
				result[field_prefix] = [field_chance, damage] if field_chance else damage

	#Retaliation: Damage over time (combine the damage and reductions):
	retaliation_duration = dict(retaliation_duration_damage, **retaliation_duration_effects)
	for field, text in retaliation_duration.items():
		#Store all relevant fields (or set to 0):
		field_prefix 			= 'retaliation' + field
		field_chance_prefix		= field_prefix + 'Chance'
		field_chance 			= float(properties[field_chance_prefix]) if field_chance_prefix in properties else 0
		duration_min_prefix		= field_prefix + 'DurationMin'
		duration_min 			= float(properties[duration_min_prefix]) if duration_min_prefix in properties else 0
		duration_max_prefix		= field_prefix + 'DurationMax'
		duration_max 			= float(properties[duration_max_prefix]) if duration_max_prefix in properties else 0
		min_prefix 				= field_prefix + 'Min'
		min_damage				= float(properties[min_prefix]) if min_prefix in properties else 0
		max_prefix 				= field_prefix + 'Max'
		max_damage 				= float(properties[max_prefix]) if max_prefix in properties else 0

		#Multiply values by duration if needed:
		if(field in offensive_duration_damage):
			if(min_damage and not max_damage and duration_min and duration_max):
				max_damage = min_damage * duration_max
				min_damage = min_damage * duration_min
				duration_max = 0
			elif(min_damage and max_damage and duration_min):
				min_damage = min_damage * duration_min
				max_damage = max_damage * duration_min

		#Create the suffix
		damage_suffix = text

		if(field in retaliation_duration_damage):
			damage_suffix += val_dur_over.format(duration_min) if duration_min_prefix in properties else ''			
		else:
			damage_suffix += val_dur_for.format(duration_min) if duration_min_prefix in properties else ''

		if (field_prefix + 'Global') in properties:
			#Flat or % is to be included in % chance trigger:
			if (field_prefix + 'XOR') in properties:
				retaliation_chance_key = 'retaliationChanceXOR'

				if max_damage and max_damage > min_damage:
					retaliation_chance_property.append(val_range.format(min_damage, max_damage) + damage_suffix)
				else:
					retaliation_chance_property.append(val_int.format(min_damage) + damage_suffix)
			else:
				if max_damage and max_damage > min_damage:
					retaliation_chance_property.append(val_range.format(min_damage, max_damage) + damage_suffix)
				else:	
					retaliation_chance_property.append(val_int.format(min_damage) + damage_suffix)
		elif min_damage:
				damage = val_range.format(min_damage, max_damage) if max_damage else val_int.format(min_damage)
				damage += damage_suffix
				result[field_prefix] = [field_chance, damage] if field_chance else damage

	if retaliation_chance and len(retaliation_chance_property) > 1:
		result[retaliation_chance_key] = retaliation_chance_property

	#Defensive
	for field, text in defensive_absolute.items():
		field_prefix 			= 'defensive' + field
		field_value 			= float(properties[field_prefix]) if field_prefix in properties else 0
		field_chance_prefix		= field_prefix + 'Chance'
		field_chance 			= float(properties[field_chance_prefix]) if field_chance_prefix in properties else 0
		duration_prefix 		= field_prefix + 'Duration'
		duration_value			= float(properties[duration_prefix]) if duration_prefix in properties else 0
		duration_chance_prefix	= field_prefix + 'DurationChance'
		duration_chance			= float(properties[duration_chance_prefix]) if duration_chance_prefix in properties else 0
		modifier_prefix 		= field_prefix + 'Modifier'
		modifier_value	 		= float(properties[modifier_prefix]) if modifier_prefix in properties else 0
		modifier_chance_prefix 	= field_prefix + 'ModifierChance'
		modifier_chance 		= float(properties[modifier_chance_prefix]) if modifier_chance_prefix in properties else 0

		if field_value:
			format_flat = val_int if 'format_flat' not in text else text['format_flat']
			resistance = format_flat.format(field_value) + text['flat']
			result[field_prefix] = [field_chance, resistance] if field_chance else resistance

		if modifier_value:
			#Since skills seem to use modifier - even for flat, check:
			suffix = text['modifier'] if 'modifier' in text else text['flat']

			format_modifier = val_int if 'format_modifier' not in text else text['format_modifier']
			resistance = format_modifier.format(modifier_value) + suffix
			result[modifier_prefix] = [modifier_chance, resistance] if modifier_chance else resistance	

		if duration_value:
			resistance = val_int.format(duration_value) + text['duration']
			result[duration_prefix] = [duration_chance, resistance] if duration_chance else resistance	

	#Defensive: Shield Block:
	if 'defensiveBlock' in properties:
		shieldBlock = float(properties['defensiveBlock'])
		shieldBlockChance = float(properties['defensiveBlockChance'])
		result['shieldBlock'] = defensive_shield.format(shieldBlockChance, shieldBlock)

	return result

def parse_tiered_properties(properties):
	#Tier properties where possible
	tiered_properties = dict([(key, value.split(';')) for key, value in properties.items() if ';' in value])
	
	if not tiered_properties:
		return [parse_properties(properties)]

	#Find longest list of split fields:
	tiers = len(tiered_properties[max(tiered_properties, key=lambda x:len(tiered_properties[x]))])

	#Now add all non-tiered properties:
	tiered_properties.update(dict([(key, value) for key, value in properties.items() if ';' not in value]))

	result = []
	for i in range(0, tiers):
		tier = dict()
		for key, value in tiered_properties.items():
			if key == 'racialBonusRace':
				tier[key] = ';'.join(value) if isinstance(value, list) else value
			elif not isinstance(value, list):
				tier[key] = value
			elif i < len(value) and has_numeric_value(value[i]):
				tier[key] = value[i]

		tier_properties = parse_properties(tier)
		if(tier_properties):
			result.append(tier_properties)

	return result
