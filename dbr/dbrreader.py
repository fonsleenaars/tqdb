from .constants import *
import math
import os
import re


class DBRReader:
    '''Class that parses DBR files'''

    def __init__(self, dbr, tags, allow_recursion=True):
        self.dbr = dbr
        self.properties = {}
        self.tiered = []
        self.parsed = {}
        self.tags = tags

        # Parsing Sets and Equipment can lead to infinite
        # recursion, this will disable that:
        self.allow_recursion = allow_recursion

        # Open the DBR and prepare the properties
        try:
            self.file = open(dbr)
            self.prepare_properties()
        except (FileNotFoundError, TypeError):
            self.dbr = ''

        # Set the class type
        if(CLASS in self.properties):
            self.parsed[TYPE] = self.properties[CLASS]

    def parse(self):
        # Determine what kind of file is being parsed and run it
        if(SET_NAME in self.properties):
            self.parse_set()
        elif TYPE not in self.parsed:
            self.parse_base()
        elif self.parsed[TYPE] in TYPE_EQUIPMENT:
            self.parse_equipment()
        elif self.parsed[TYPE] in TYPE_RELIC:
            self.parse_relic()
        elif self.parsed[TYPE] in TYPE_SCROLL:
            self.parse_scroll()
        elif self.parsed[TYPE] in TYPE_SKILL_BUFF_REF:
            self.parse_skill_buff()
        elif self.parsed[TYPE] in TYPE_SKILL_PET_REF:
            self.parse_skill_pet()
        elif self.parsed[TYPE] in TYPE_SKILL_SPAWN:
            self.parse_skill_spawn()
        elif self.parsed[TYPE] in TYPE_SKILL:
            self.parse_skill()
        elif self.parsed[TYPE] in TYPE_LOOT_TABLE:
            self.parse_loot_table()
        else:
            # Also parse base case if no other match was found:
            self.parse_base()

    # -------------------------------------------------------------------------
    #
    #                   PARSE FUNCTIONS START BELOW
    #
    # -------------------------------------------------------------------------

    def parse_base(self):
        # Parsed properties are a list (because they're tiered)
        if(self.tiered):
            self.parsed[PROPERTIES] = []
            for index, tier in enumerate(self.tiered):
                # Prepare the next properties list:
                self.parsed[PROPERTIES].insert(index, {})

                # Parse the properties
                self.parse_character(index)
                self.parse_defensive(index)
                self.parse_item_skill_augment(index)
                self.parse_offensive(index)
                self.parse_petbonus(index)
                self.parse_racial(index)
                self.parse_retaliation(index)
                self.parse_skill_properties(index)
        else:
            # Prepare the properties
            self.parsed[PROPERTIES] = {}

            # Parse the properties
            self.parse_character()
            self.parse_defensive()
            self.parse_item_skill_augment()
            self.parse_offensive()
            self.parse_petbonus()
            self.parse_racial()
            self.parse_retaliation()
            self.parse_skill_properties()

    def parse_character(self, tier=-1):
        '''Parse the character DBR parameters'''

        # Set the properties to parse (tiered or non-tiered):
        properties = self.tiered[tier] if tier >= 0 else self.properties

        result = {}
        # Parse character bonuses (only absolutes and modifiers)
        for prop, output in CHARACTER_FIELDS.items():
            field = PREFIX_CHAR + prop

            format_absolute = output.get(TXT_FABS, FORMAT_INT_SIGNED)
            format_modifier = output.get(TXT_FMOD, FORMAT_MOD)
            text_absolute = output.get(TXT_ABS)
            text_modifier = output.get(TXT_MOD, text_absolute)
            value_absolute = float(properties.get(field, 0))
            value_modifier = float(properties.get(field + SUFFIX_MOD, 0))

            if value_absolute:
                result[field] = format_absolute.format(value_absolute) + (
                                text_absolute)
            if value_modifier:
                result[field + SUFFIX_MOD] = format_modifier.format(
                                             value_modifier) + (
                                             text_modifier)

        # Parse requirement reductions
        for prop, output in REQUIREMENT_FIELDS.items():
            field = PREFIX_CHAR + prop + SUFFIX_RED
            if field in properties:
                result[field] = FORMAT_REDUCTION.format(
                                float(properties[field])) + output

        # Append the character results to the properties:
        if tier == -1:
            self.parsed[PROPERTIES].update(result)
        else:
            self.parsed[PROPERTIES][tier].update(result)

    def parse_cost(self):
        if ITEM_COST in self.properties:
            # Cost prefix of this item is determined by its class
            cost_prefix = self.properties[CLASS].split('_')[1]
            cost_prefix = cost_prefix[0:1].lower() + cost_prefix[1:]

            # Open cost file
            cost_reference = self.get_reference_dbr(self.properties[ITEM_COST])
            with open(cost_reference) as cost_file:
                # Grab the cost equations:
                cost_lines = [line.rstrip(',\n') for line in cost_file]
                cost_properties = dict([(k, v) for k, v
                                       in (dict(properties.split(',')
                                           for properties
                                           in cost_lines)).items()
                                       if self.property_isset(v)])

                # Grab the item level (it's a variable in the equations)
                itemLevel = self.parsed[ITEM_LEVEL]
                for requirement in REQUIREMENTS:
                    # Create the equation key
                    equation_key = cost_prefix + requirement + SUFFIX_EQUATION

                    if equation_key in cost_properties:
                        equation = cost_properties[equation_key]

                        # Set the possible parameters in the equation:
                        totalAttCount = len(self.parsed[PROPERTIES])
                        itemLevel = self.parsed[ITEM_LEVEL]

                        # Evaluate the equation to determine the requirement
                        self.parsed[PREFIX_REQ + requirement] = (
                            math.ceil(eval(equation)))

    def parse_defensive(self, tier=-1):
        '''Parse the defensive DBR parameters'''

        # Set the properties to parse (tiered or non-tiered):
        properties = self.tiered[tier] if tier >= 0 else self.properties

        result = {}
        # Parse defensive bonuses:
        for prop, output in DEFENSIVE_FIELDS.items():
            field = PREFIX_DEF + prop

            # Setup the output chances, format, texts, and values
            chance_absolute = int(float(
                properties.get(field + SUFFIX_CHANCE, 0)))
            chance_duration = int(float(
                properties.get(field + SUFFIX_DCHANCE, 0)))
            chance_modifier = int(float(
                properties.get(field + SUFFIX_MCHANCE, 0)))
            format_absolute = output.get(TXT_FABS, FORMAT_INT)
            format_modifier = output.get(TXT_FMOD, FORMAT_MOD)
            format_range = output.get(TXT_FRANGE, FORMAT_RANGE)
            text_absolute = output.get(TXT_ABS)
            text_duration = output.get(TXT_DUR, text_absolute)
            text_modifier = output.get(TXT_MOD, text_absolute)

            value = float(properties.get(field, 0))
            value_duration = float(properties.get(field + SUFFIX_DUR, 0))
            value_modifier = float(properties.get(field + SUFFIX_MOD, 0))

            if value:
                absolute = format_absolute.format(value) + text_absolute
                result[field] = ([chance_absolute, absolute]
                                 if chance_absolute
                                 else absolute)
            if value_duration:
                duration = FORMAT_INT.format(value_duration) + text_absolute
                result[field + SUFFIX_DUR] = ([chance_duration, duration]
                                              if chance_duration
                                              else duration)
            if value_modifier:
                modifier = format_modifier.format(value_modifier) + (
                           text_modifier)
                result[field + SUFFIX_MOD] = ([chance_modifier, modifier]
                                              if chance_modifier
                                              else modifier)

        # Append the defensive results to the properties:
        if tier == -1:
            self.parsed[PROPERTIES].update(result)
        else:
            self.parsed[PROPERTIES][tier].update(result)

    def parse_equipment(self):
        '''Parse the DBR file as an equipment file'''

        # Grab item rarity and check it against required:
        self.parsed[ITEM_CLASSIFICATION] = (
            self.properties.get(ITEM_CLASSIFICATION, None))

        if self.parsed[ITEM_CLASSIFICATION] not in ITEM_RARITIES:
            return

        # Set item level, tag & name
        self.parsed[ITEM_LEVEL] = int(self.properties.get(ITEM_LEVEL, 0))
        self.parsed[ITEM_TAG] = self.properties.get(ITEM_TAG, None)
        self.parsed[ITEM_NAME] = (self.tags[self.parsed[ITEM_TAG]]
                                  if self.parsed[ITEM_TAG] in self.tags
                                  else '')

        # Check if the item is part of a set:
        if ITEM_SET in self.properties:
            # Parse the set file
            set_file = self.get_reference_dbr(self.properties[ITEM_SET])
            item_set = DBRReader(set_file, self.tags, False)
            item_set.parse()

            self.parsed[ITEM_SET] = item_set.parsed[SET_TAG]

        # Initialize the properties and parse them:
        self.parsed[PROPERTIES] = {}
        self.parse_character()
        self.parse_defensive()
        self.parse_item_skill_augment()
        self.parse_offensive()
        self.parse_petbonus()
        self.parse_racial()
        self.parse_retaliation()
        self.parse_skill_properties()
        self.parse_cost()

    def parse_item_skill_augment(self, tier=-1):
        '''Parse the item bsaed skill augment DBR parameters'''

        # Set the properties to parse (tiered or non-tiered):
        properties = self.tiered[tier] if tier >= 0 else self.properties

        result = {}

        # Parse skills that are granted
        if ITEM_SKILL in properties:
            # Grab the skill file:
            skill_file = self.get_reference_dbr(properties[ITEM_SKILL])
            skill = DBRReader(skill_file, self.tags)
            skill.parse()

            if PROPERTIES in skill.parsed:
                result[ITEM_SKILL] = skill.parsed

        # Parse skills that are augmented:
        for augment_name, augment_level in SKILL_AUGMENT_FIELDS.items():
            if augment_name not in properties:
                continue

            # Grab the skill file:
            skill_file = self.get_reference_dbr(properties[augment_name])
            skill = DBRReader(skill_file, self.tags)
            skill.parse()

            if PROPERTIES in skill.parsed:
                skill_level = int(self.properties[augment_level])
                skill.parsed[augment_level] = skill_level
                result[augment_name] = skill.parsed

        # Parse augment to all skills:
        if SKILL_AUGMENT_ALL in properties:
            result[SKILL_AUGMENT_ALL] = SKILL_AUGMENT_ALL_FORMAT.format(
                                            properties[SKILL_AUGMENT_ALL])

        # Append the item skill results to the properties:
        if tier == -1:
            self.parsed[PROPERTIES].update(result)
        else:
            self.parsed[PROPERTIES][tier].update(result)

    def parse_loot_table(self):
        bonuses = []
        bonus_files = {}
        weights = {}

        # Parse the possible completion bonuses:
        for field, value in self.properties.items():
            if LOOT_RANDOMIZER_NAME in field:
                number = re.search(r'\d+', field).group()
                bonus_files[number] = value
            if LOOT_RANDOMIZER_WEIGHT in field:
                number = re.search(r'\d+', field).group()
                weights[number] = int(value)

        # Add all the weights together to determined % later
        total_weight = sum(weights.values())
        for field, value in bonus_files.items():
            if field in weights:
                bonus_file = self.get_reference_dbr(value)
                bonus = DBRReader(bonus_file, self.tags)
                bonus.parse()

                # Append the parsed bonus with its chance:
                bonuses.append({
                    BONUS_CHANCE: float('{0:.2f}'.format(
                        (weights[field] / total_weight) * 100)),
                    BONUS: bonus.parsed[PROPERTIES]})

        # Set all parsed bonuses
        self.parsed[BONUS] = bonuses

    def parse_offensive(self, tier=-1):
        '''Parse the offensive DBR parameters'''

        # Set the properties to parse (tiered or non-tiered):
        properties = self.tiered[tier] if tier >= 0 else self.properties

        result = {}
        chance_properties = []
        chance_key = PREFIX_OFF + SUFFIX_GCHANCE
        chance_value = int(float(properties.get(chance_key, 0)))
        chance_isset = chance_key in properties

        offensive_fields = {
            **OFFENSIVE_FIELDS,
            **OFFENSIVE_DUR_DMG_FIELDS,
            **OFFENSIVE_DUR_EFF_FIELDS}

        for prop, output in offensive_fields.items():
            field = PREFIX_OFF + prop

            # Setup the output chances, format, texts, and values
            chance_absolute = int(float(
                properties.get(field + SUFFIX_CHANCE, 0)))
            chance_modifier = int(float(
                properties.get(field + SUFFIX_MCHANCE, 0)))
            chance_global = properties.get(field + SUFFIX_GLOBAL, 0)
            chance_xor = properties.get(field + SUFFIX_XOR, 0)

            # Format and texts are decided by the type of output:
            format_absolute = (output.get(TXT_FABS, FORMAT_INT)
                               if isinstance(output, dict)
                               else FORMAT_INT)
            format_modifier = (output.get(TXT_FMOD, FORMAT_MOD)
                               if isinstance(output, dict)
                               else FORMAT_MOD)
            format_range = (output.get(TXT_FRANGE, FORMAT_RANGE)
                            if isinstance(output, dict)
                            else FORMAT_RANGE)
            text_absolute = (output.get(TXT_ABS)
                             if isinstance(output, dict)
                             else output)
            text_modifier = (output.get(TXT_MOD, text_absolute)
                             if isinstance(output, dict)
                             else output)

            value_min = float(properties.get(field + SUFFIX_MIN, 0))
            value_max = float(properties.get(field + SUFFIX_MIN, 0))
            value_modifier = float(properties.get(field + SUFFIX_MOD, 0))

            # Duration fields will only be relevant for non-absolute properties
            if prop not in OFFENSIVE_FIELDS:
                duration_min = float(
                    properties.get(field + SUFFIX_DURMIN, 0))
                duration_max = float(
                    properties.get(field + SUFFIX_DURMAX, 0))
                duration_mod = float(
                    properties.get(field + SUFFIX_DURMOD, 0))

                # Check if text fields need duration modifiers appended:
                if duration_mod:
                    text_absolute += FORMAT_DUR_IMP.format(duration_mod)
                    text_modifier += FORMAT_DUR_IMP.format(duration_mod)

                # Duration damage fields need to multiply damages by duration
                if prop in OFFENSIVE_DUR_DMG_FIELDS and (
                   value_min and duration_min):
                    # The min damage value is always the same:
                    value_min = value_min * duration_min

                    # If there's no max damage, but there is a max duration
                    # just multiply the min damage by the max duration:
                    if duration_max and not value_max:
                        value_max = value_min * duration_max
                        duration_max = 0
                    # Last option, if the max value is also set, multiply
                    # by min duration:
                    elif value_max:
                        value_max = value_max * duration_min

                    # Append the duration 'over x second(s)' suffix to absolute
                    text_absolute += FORMAT_DUR_OVER.format(duration_min)
                elif prop in OFFENSIVE_DUR_EFF_FIELDS and duration_min:
                    # Append the duration 'for x second(s)' suffix to absolute
                    text_absolute += FORMAT_DUR_FOR.format(duration_min)

            # Format values now that durations are taken into account
            absolute = (format_range(value_min, value_max)
                        if value_max and value_max > value_min
                        else format_absolute.format(value_min)) + (
                        text_absolute)
            modifier = format_modifier.format(value_modifier) + (
                       text_modifier)

            # Check if XOR is set for this field:
            if chance_xor:
                chance_key = PREFIX_OFF + SUFFIX_GCHANCE + SUFFIX_XOR

            # Check if "multiple choice" chance is set:
            if chance_global:
                if value_modifier:
                    # Append modifier damage to chance properties:
                    chance_properties.append(modifier)

                    if chance_xor and value_min:
                        # Normal case: both modifier and absolute
                        # damages can be chanced based.
                        if prop not in OFFENSIVE_FIELDS:
                            chance_properties.append(absolute)
                        # Edge case: for absolute offensive fields, the
                        # absolute property will be a general property
                        # if it's set while the modifier is chanced
                        else:
                            result[field] = absolute

                # Edge case: Physical and Piercing damage are never chance
                # based (absolute values only)
                elif ((prop == DMG_PHYS and
                       PREFIX_WEAPON in self.parsed[TYPE]) or
                      (prop == DMG_PIERCE)):
                    result[field] = absolute
                else:
                    # Append flat (or range) damage to chances:
                    chance_properties.append(absolute)
            else:
                if value_modifier:
                    # Add modifier as general property
                    result[field + SUFFIX_MOD] = ([chance_modifier, modifier]
                                                  if chance_modifier
                                                  else modifier)
                if value_min:
                    # Add flat damage (or range) as a general property
                    result[field] = ([chance_absolute, absolute]
                                     if chance_absolute
                                     else absolute)

        # Edge case: ManaBurn, set apart and follow a different format
        # than that of the other fields in the offensive template:
        mb_chance = int(properties.get(STAT_MP_BURN + SUFFIX_GLOBAL, 0))
        mb_min = float(properties.get(STAT_MP_BURN_MIN, 0))
        mb_max = float(properties.get(STAT_MP_BURN_MAX, 0))
        mb_ratio = float(properties.get(STAT_MP_BURN_RATIO, 0))

        if mb_min:
            mb_value = (FORMAT_RANGE.format(mb_min, mb_max)
                        if mb_max > mb_min
                        else FORMAT_INT.format(mb_min))

            # Append the text and drain ratio, if set.
            # TXT_MOD key here used for the ratio text
            mb_value += OFFENSIVE_MB_FIELD[TXT_ABS] + (
                        OFFENSIVE_MB_FIELD[TXT_MOD].format(mb_ratio)
                        if mb_ratio else '')

            # Append the mana burn to the chance properties,
            # or general properties:
            if mb_chance:
                chance_properties.append(mb_value)
            else:
                result[STAT_MP_BURN] = mb_value

        # Now append teh chance properties if they exist:
        if chance_isset:
            chance_properties.insert(0, chance_value)
            result[chance_key] = chance_properties

        # Append the offensive results to the properties:
        if tier == -1:
            self.parsed[PROPERTIES].update(result)
        else:
            self.parsed[PROPERTIES][tier].update(result)

    def parse_petbonus(self, tier=-1):
        '''Parse the pet bonus DBR parameters'''

        # Set the properties to parse (tiered or non-tiered):
        properties = self.tiered[tier] if tier >= 0 else self.properties

        if DBR_PET_BONUS in properties:
            # Parse the pet bonus file
            pet_bonus_file = self.get_reference_dbr(properties[DBR_PET_BONUS])
            pet_bonus = DBRReader(pet_bonus_file, self.tags)
            pet_bonus.parse()

            # Append the pet bonus
            if tier == -1:
                self.parsed[PROPERTIES][DBR_PET_BONUS] = (
                    pet_bonus.parsed[PROPERTIES])
            else:
                self.parsed[PROPERTIES][tier][DBR_PET_BONUS] = (
                    pet_bonus.parsed[PROPERTIES])

    def parse_racial(self, tier=-1):
        '''Parse the racial bonus DBR parameters'''

        # Set the properties to parse (tiered or non-tiered):
        properties = self.tiered[tier] if tier >= 0 else self.properties

        if STAT_RACE not in properties:
            return

        result = {}
        bonus_list = properties[STAT_RACE].split(';')
        for prop, output in RACIAL_FIELDS.items():
            field = PREFIX_RACE + prop

            if field not in properties:
                continue

            # Start with an empty list for this bonus:
            result[field] = []
            values = properties[field].split(';')

            for i in range(0, len(bonus_list)):
                result[field].append(output.format(float(values[0])
                                     if len(bonus_list)
                                     else value[i],
                                     bonus_list[i]))

        if tier == -1:
            self.parsed[PROPERTIES].update(result)
        else:
            self.parsed[PROPERTIES][tier].update(result)

    def parse_relic(self):
        '''Parse the DBR file as a relic file'''

        # Grab the file name and split it:
        file_name = os.path.basename(self.dbr).split('_')

        # Set the relic specfic properties:
        self.parsed[RELIC_TAG] = self.properties[DESCRIPTION]
        self.parsed[RELIC_NAME] = self.tags[self.parsed[RELIC_TAG]]
        self.parsed[DESCRIPTION] = self.tags[self.properties[ITEM_TEXT]]
        self.parsed[DIFFICULTY] = DIFFICULTIES[int(file_name[0][1:]) - 1]
        self.parsed[ACT] = file_name[1]

        # Parsed properties are a list (because they're tiered)
        self.parsed[PROPERTIES] = []
        for index, tier in enumerate(self.tiered):
            # Prepare the next properties list:
            self.parsed[PROPERTIES].insert(index, {})

            # Parse the relic properties
            self.parse_character(index)
            self.parse_defensive(index)
            self.parse_offensive(index)
            self.parse_retaliation(index)
            self.parse_skill_properties(index)

        self.parse_cost()

        # Parse completion bonuses and set it:
        bonus_file = self.get_reference_dbr(self.properties[BONUS_TABLE])
        bonus = DBRReader(bonus_file, self.tags)
        bonus.parse()
        self.parsed[BONUS] = bonus.parsed.get(BONUS, [])

    def parse_retaliation(self, tier=-1):
        '''Parse the retaliation DBR parameters'''

        # Set the properties to parse (tiered or non-tiered):
        properties = self.tiered[tier] if tier >= 0 else self.properties

        result = {}
        chance_properties = []
        chance_key = PREFIX_RETAL + SUFFIX_GCHANCE
        chance_value = int(float(properties.get(chance_key, 0)))
        chance_isset = chance_key in properties

        retaliation_fields = {
            **RETALIATION_FIELDS,
            **RETALIATION_DUR_DMG_FIELDS,
            **RETALIATION_DUR_EFF_FIELDS}

        for prop, output in retaliation_fields.items():
            field = PREFIX_RETAL + prop

            # Setup the output chances, format, texts, and values
            chance_absolute = int(float(
                properties.get(field + SUFFIX_CHANCE, 0)))
            chance_modifier = int(float(
                properties.get(field + SUFFIX_MCHANCE, 0)))
            chance_global = properties.get(field + SUFFIX_GLOBAL, 0)
            chance_xor = properties.get(field + SUFFIX_XOR, 0)

            # Format and texts are decided by the type of output:
            format_absolute = (output.get(TXT_FABS, FORMAT_INT)
                               if isinstance(output, dict)
                               else FORMAT_INT)
            format_modifier = (output.get(TXT_FMOD, FORMAT_MOD)
                               if isinstance(output, dict)
                               else FORMAT_MOD)
            format_range = (output.get(TXT_FRANGE, FORMAT_RANGE)
                            if isinstance(output, dict)
                            else FORMAT_RANGE)
            text_absolute = (output.get(TXT_ABS)
                             if isinstance(output, dict)
                             else output)
            text_modifier = (output.get(TXT_MOD, text_absolute)
                             if isinstance(output, dict)
                             else output)

            value_min = float(properties.get(field + SUFFIX_MIN, 0))
            value_max = float(properties.get(field + SUFFIX_MIN, 0))
            value_modifier = float(properties.get(field + SUFFIX_MOD, 0))

            # Duration fields will only be relevant for non-absolute properties
            if prop not in RETALIATION_FIELDS:
                duration_min = float(
                    properties.get(field + SUFFIX_DURMIN, 0))
                duration_max = float(
                    properties.get(field + SUFFIX_DURMAX, 0))
                duration_mod = float(
                    properties.get(field + SUFFIX_DURMOD, 0))

                # Check if text fields need duration modifiers appended:
                if duration_mod:
                    text_absolute += FORMAT_DUR_IMP.format(duration_mod)
                    text_modifier += FORMAT_DUR_IMP.format(duration_mod)

                # Duration damage fields need to multiply damages by duration
                if prop in RETALIATION_DUR_DMG_FIELDS and (
                   value_min and duration_min):
                    # The min damage value is always the same:
                    value_min = value_min * duration_min

                    # If there's no max damage, but there is a max duration
                    # just multiply the min damage by the max duration:
                    if duration_max and not value_max:
                        value_max = value_min * duration_max
                        duration_max = 0
                    # Last option, if the max value is also set, multiply
                    # by min duration:
                    elif value_max:
                        value_max = value_max * duration_min

                    # Append the duration 'over x second(s)' suffix to absolute
                    text_absolute += FORMAT_DUR_OVER.format(duration_min)
                elif prop in RETALIATION_DUR_EFF_FIELDS and duration_min:
                    # Append the duration 'for x second(s)' suffix to absolute
                    text_absolute += FORMAT_DUR_FOR.format(duration_min)

            # Format values now that durations are taken into account
            absolute = (format_range(value_min, value_max)
                        if value_max and value_max > value_min
                        else format_absolute.format(value_min)) + (
                        text_absolute)
            modifier = format_modifier.format(value_modifier) + (
                       text_modifier)

            # Check if XOR is set for this field:
            if chance_xor:
                chance_key = PREFIX_RETAL + SUFFIX_GCHANCE + SUFFIX_XOR

            # Check if "multiple choice" chance is set:
            if chance_global:
                if value_modifier:
                    # Append modifier damage to chance properties:
                    chance_properties.append(modifier)

                    if chance_xor and value_min:
                        # Normal case: both modifier and absolute
                        # damages can be chanced based.
                        if prop not in RETALIATION_FIELDS:
                            chance_properties.append(absolute)
                        # Edge case: for absolute retaliation fields, the
                        # absolute property will be a general property
                        # if it's set while the modifier is chanced
                        else:
                            result[field] = absolute
                else:
                    # Append flat (or range) damage to chances:
                    chance_properties.append(absolute)
            else:
                if value_modifier:
                    # Add modifier as general property
                    result[field + SUFFIX_MOD] = ([chance_modifier, modifier]
                                                  if chance_modifier
                                                  else modifier)
                if value_min:
                    # Add flat damage (or range) as a general property
                    result[field] = ([chance_absolute, absolute]
                                     if chance_absolute
                                     else absolute)

        # Now append the chance properties if they exist:
        if chance_isset:
            chance_properties.insert(0, chance_value)
            result[chance_key] = chance_properties

        # Append the retaliation results to the properties:
        if tier == -1:
            self.parsed[PROPERTIES].update(result)
        else:
            self.parsed[PROPERTIES][tier].update(result)

    def parse_scroll(self):
        '''Parse the DBR file as a scroll file'''
        self.parsed[ITEM_TAG] = self.properties[DESCRIPTION]
        self.parsed[ITEM_NAME] = self.tags[self.parsed[ITEM_TAG]]
        self.parsed[DESCRIPTION] = self.tags[self.properties[ITEM_TEXT]]

    def parse_set(self):
        self.parsed[SET_TAG] = self.properties.get(SET_NAME, '')
        self.parsed[SET_NAME] = self.tags[self.parsed[SET_TAG]]

        self.parsed[PROPERTIES] = []
        for index, tier in enumerate(self.tiered):
            # Prepare the next properties list:
            self.parsed[PROPERTIES].insert(index, {})

            # Parse the properties
            self.parse_character(index)
            self.parse_defensive(index)
            self.parse_offensive(index)
            self.parse_retaliation(index)
            self.parse_skill_properties(index)

        # Parse members:
        if self.allow_recursion:
            self.parsed[SET_MEMBERS] = []
            for member in self.properties[SET_MEMBERS].split(';'):
                if EQUIPMENT not in member.lower():
                    continue

                # Grab the member file and only extract name:
                member_file = self.get_reference_dbr(member)
                member = DBRReader(member_file, self.tags)
                member.parse()

                if(ITEM_NAME in member.parsed):
                    member_tag = member.parsed[ITEM_NAME]
                    self.parsed[SET_MEMBERS].append({
                        ITEM_TAG: member.parsed[ITEM_TAG],
                        ITEM_NAME: member.parsed[ITEM_NAME]})

        # Pop off the first element of the properties (1 set item)
        if(len(self.parsed[PROPERTIES]) > 1):
            if(not self.parsed[PROPERTIES][0]):
                self.parsed[PROPERTIES].pop(0)

    def parse_skill(self):
        '''Parse the DBR file as a skill file'''

        # Set the skill specfic properties:
        if SKILL_DISPLAY in self.properties:
            self.parsed[SKILL_TAG] = self.properties[SKILL_DISPLAY]

            # Convert tag to text if possible
            if self.parsed[SKILL_TAG] in self.tags:
                self.parsed[SKILL_DISPLAY] = self.tags[self.parsed[SKILL_TAG]]

        if SKILL_DESC in self.properties and (
                self.properties[SKILL_DESC] in self.tags):
            self.parsed[DESCRIPTION] = self.tags[self.properties[SKILL_DESC]]
        elif FILE_DESCRIPTION in self.properties:
            self.parsed[DESCRIPTION] = self.properties[FILE_DESCRIPTION]

        # Keep track of the skill path (this will determine the key)
        self.parsed[PATH] = re.sub(r'[\ \\]', '_', self.dbr).lower()

        # Parsed properties are a list (because they're tiered)
        self.parsed[PROPERTIES] = []
        for index, tier in enumerate(self.tiered):
            # Prepare the next properties list:
            self.parsed[PROPERTIES].insert(index, {})

            # Parse the skill properties
            self.parse_character(index)
            self.parse_defensive(index)
            self.parse_offensive(index)
            self.parse_petbonus(index)
            self.parse_racial(index)
            self.parse_retaliation(index)
            self.parse_skill_properties(index)

    def parse_skill_buff(self):
        '''Parse the DBR reference skill buff file'''

        # Parse the buff file
        skill_buff_file = self.get_reference_dbr(
                            self.properties[DBR_BUFF_SKILL])
        skill_buff = DBRReader(skill_buff_file, self.tags)
        skill_buff.parse()

        # Set the known properties
        self.parsed = skill_buff.parsed
        self.parsed[PATH] = re.sub(r'[\ \\]', '_', self.dbr).lower()

    def parse_skill_pet(self):
        '''Parse the DBR reference pet modifier file'''

        # Parse the pet file
        skill_pet_file = self.get_reference_dbr(
                            self.properties[DBR_PET_SKILL])
        skill_pet = DBRReader(skill_pet_file, self.tags)
        skill_pet.parse()

        # Set the known properties
        self.parsed = skill_pet.parsed
        self.parsed[PATH] = re.sub(r'[\ \\]', '_', self.dbr).lower()

    def parse_skill_properties(self, tier=-1):
        '''Parses skill property DBR parameters'''

        # Set the properties to parse (tiered or non-tiered):
        properties = self.tiered[tier] if tier >= 0 else self.properties

        result = {}
        for prop, output in SKILL_PROPERTY_FIELDS.items():
            field = PREFIX_SKILL + prop

            # Setup the output chances, format, texts, and values
            chance_absolute = int(float(
                properties.get(field + SUFFIX_CHANCE, 0)))
            # format_absolute = (output.get(TXT_FABS, FORMAT_INT)
            #                    if isinstance(output, dict)
            #                    else FORMAT_INT)
            # text_absolute = (output.get(TXT_ABS)
            #                  if isinstance(output, dict)
            #                  else output)
            value_absolute = float(properties.get(field, 0))
            absolute = output.format(value_absolute)

            if value_absolute:
                result[field] = ([chance_absolute, absolute]
                                 if chance_absolute
                                 else absolute)

        # Append the skill results to the properties:
        if tier == -1:
            self.parsed[PROPERTIES].update(result)
        else:
            self.parsed[PROPERTIES][tier].update(result)

    def parse_skill_spawn(self):
        '''Parse the DBR reference spawning file'''

        # Set the known properties
        self.parsed[SKILL_TAG] = self.properties[SKILL_DISPLAY]
        self.parsed[SKILL_DISPLAY] = self.tags[self.parsed[SKILL_TAG]]
        self.parsed[DESCRIPTION] = (self.tags[self.properties[SKILL_DESC]]
                                    if SKILL_DESC in self.properties
                                    else '')
        self.parsed[PATH] = re.sub(r'[\ \\]', '_', self.dbr).lower()

        # Only set time to live it's it exists (otherwise it's infinite)
        if PET_TTL in self.properties:
            self.parsed[PET_TTL] = self.properties[PET_TTL]

    # -------------------------------------------------------------------------
    #
    #                   HELPER FUNCTIONS START BELOW
    #
    # -------------------------------------------------------------------------

    def get_reference_dbr(self, new_dbr):
        '''Return full path for a DBR file referenced in
        a DBR file, by using the current full path'''
        try:
            # Lowercase the new DBR
            new_dbr = new_dbr.lower()

            # Create the reference
            dbr_ref = self.dbr[:self.dbr.index(new_dbr.split('\\')[0])] + (
                   new_dbr)

            # Quick check to avoid infinite recursion (new reference = self)
            return dbr_ref if self.dbr != dbr_ref else None
        except ValueError:
            return None

    def prepare_properties(self):

        # DBR file into a list of lines
        lines = [line.rstrip(',\n') for line in self.file]

        # Parse line into a dictionary of key, value properties:
        self.properties = dict([(k, v) for k, v in (dict(properties.split(',')
                               for properties in lines)).items()
                               if self.property_isset(v)])

        # Parse into tiered properties as well, if applicable
        tiered_properties = (dict([(key, value.split(';'))
                             for key, value
                             in self.properties.items()
                             if ';' in value]))

        # If there are no tiered propreties, return here
        if not tiered_properties:
            return

        # Check occurences where value is set, but first iteration
        # is 0% chance:
        chance_zeroes = {}
        for key, value in tiered_properties.items():
            if(SUFFIX_CHANCE in key and float(value[0]) == 0):
                # Store the prefix to check on another iteration
                chance_zeroes[key[0:key.index(SUFFIX_CHANCE)]] = len(value)

        # Find longest list of split fields:
        tiers = len(tiered_properties[max(tiered_properties,
                                      key=lambda
                                      x:len(tiered_properties[x]))])

        # Now add all non-tiered properties:
        tiered_properties.update(dict([(key, value)
                                 for key, value
                                 in self.properties.items()
                                 if ';' not in value]))

        # Check the edge case mentioned above
        for prefix, total in chance_zeroes.items():
            for key, value in tiered_properties.items():
                if (SUFFIX_CHANCE not in key and prefix in key and not
                   isinstance(value, list)):
                    # Fix the first occurance by seting it to zero
                    # and repeating the normal value for the others
                    tiered_properties[key] = (['0.000000'] +
                                              ([value] * (total - 1)))

        self.tiered = []
        for i in range(0, tiers):
            tier = {}

            # Setup the current tier
            for key, value in tiered_properties.items():
                if key == STAT_RACE:
                    tier[key] = (';'.join(value)
                                 if isinstance(value, list)
                                 else value)
                elif not isinstance(value, list):
                    tier[key] = value
                elif i < len(value) and self.property_isset(value[i]):
                    tier[key] = value[i]

            # Append this tier
            self.tiered.append(tier)

    def property_isset(self, property):
            try:
                float(property)
                return float(property) != 0
            except:
                return True
