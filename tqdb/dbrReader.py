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
        elif self.parsed[TYPE] in TYPE_ARTIFACT:
            self.parse_artifact()
        elif self.parsed[TYPE] in TYPE_ARTIFACT_FORMULA:
            self.parse_formula()
        elif self.parsed[TYPE] in TYPE_EQUIPMENT:
            self.parse_equipment()
        elif self.parsed[TYPE] in TYPE_LOOT_AFFIX:
            self.parse_loot_affix()
        elif self.parsed[TYPE] in TYPE_LOOT_TABLE:
            self.parse_loot_table()
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
        elif self.parsed[TYPE] in TYPE_SKILL_TREE:
            self.parse_skilltree()
        elif self.parsed[TYPE] in TYPE_SKILL_PETSUMMONS:
            self.parse_summon()
        else:
            # Also parse base case if no other match was found:
            self.parse_base()

    # -------------------------------------------------------------------------
    #
    #                   PARSE FUNCTIONS START BELOW
    #
    # -------------------------------------------------------------------------

    def parse_artifact(self):
        '''Parse the DBR file as an artifact file'''

        # Grab the file name and split it:
        file_name = os.path.basename(self.dbr).split('_')
        if file_name[0] not in DIFFICULTIES_DICT:
            return

        # Set the artifact properties
        self.parsed[TAG] = self.properties[DESCRIPTION]
        self.parsed[NAME] = self.tags[self.parsed[TAG]]
        self.parsed[CLASSIFICATION] = (self.properties
                                       [ARTIFACT_CLASSIFICATION])
        self.parsed[ARTIFACT_DROP] = DIFFICULTIES_DICT[file_name[0]]

        # Set the bitmap if it exists
        if BITMAP_ARTIFACT in self.properties:
            self.parsed[BITMAP_ARTIFACT] = self.properties[BITMAP_ARTIFACT]

        # Parse the artifact properties:
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
        self.parse_cost()

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
        # Check regular requirements first:
        for requirement in REQUIREMENTS:
            req = requirement.lower() + SUFFIX_REQ
            if req in self.properties:
                self.parsed[req] = self.properties[req]

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

                        # Only overwrite if not set yet:
                        req = requirement.lower() + SUFFIX_REQ
                        if req not in self.parsed:
                            # Eval the equation:
                            self.parsed[req] = (
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

            # Edge case defensiveTotalSpeedResistance:
            value_resistance = float(properties.get(field + SUFFIX_RES, 0))

            if value:
                absolute = format_absolute.format(value) + text_absolute
                result[field] = ([chance_absolute, absolute]
                                 if chance_absolute
                                 else absolute)
            if value_duration:
                duration = FORMAT_INT.format(value_duration) + text_duration
                result[field + SUFFIX_DUR] = ([chance_duration, duration]
                                              if chance_duration
                                              else duration)
            if value_modifier:
                modifier = format_modifier.format(value_modifier) + (
                           text_modifier)
                result[field + SUFFIX_MOD] = ([chance_modifier, modifier]
                                              if chance_modifier
                                              else modifier)

            if value_resistance:
                absolute = format_absolute.format(value_resistance) + (
                           text_absolute)
                result[field] = ([chance_absolute, absolute]
                                 if chance_absolute
                                 else absolute)

        # Append the defensive results to the properties:
        if tier == -1:
            self.parsed[PROPERTIES].update(result)
        else:
            self.parsed[PROPERTIES][tier].update(result)

    def parse_equipment(self):
        '''Parse the DBR file as an equipment file'''

        # Grab item rarity and check it against required:
        self.parsed[CLASSIFICATION] = (
            self.properties.get(ITEM_CLASSIFICATION, None))

        if self.parsed[CLASSIFICATION] not in ITEM_RARITIES:
            return

        # If item is a MI, add when it drops:
        if(self.parsed[CLASSIFICATION] == ITEM_RARE):
            file_name = os.path.basename(self.dbr).split('_')

            # Skip MI's without indicator of when they drop
            if len(file_name) < 2 or file_name[1] not in DIFFICULTIES_DICT:
                return

            self.parsed[ITEM_MI_DROP] = DIFFICULTIES_DICT[file_name[1]]

        # Set item level, tag & name
        self.parsed[ITEM_LEVEL] = int(self.properties.get(ITEM_LEVEL, 0))
        self.parsed[TAG] = self.properties.get(ITEM_TAG, None)
        self.parsed[NAME] = self.tags.get(self.parsed[TAG], '')

        # Fix for {} appearing in MI names:
        if(self.parsed[NAME]):
            self.parsed[NAME] = re.sub(r'\{[^)]*\}', '', self.parsed[NAME])

        # Set attack speed for weapons:
        if (ATK_SPD_TAG in self.properties and
           PREFIX_WEAPON in self.parsed[TYPE] and
           PREFIX_SHIELD not in self.parsed[TYPE]):
            # Grab attack speed tag:
            attackSpeed = (self.properties[ATK_SPD_TAG]
                                          [len(ATK_SPD_PRE):])

            # Format attack speed (put space between capitalized words):
            self.parsed[ATK_SPD] = re.sub(r"(\w)([A-Z])", r"\1 \2",
                                          attackSpeed)

        # Check if the item is part of a set:
        if ITEM_SET in self.properties:
            # Parse the set file
            set_file = self.get_reference_dbr(self.properties[ITEM_SET])
            item_set = DBRReader(set_file, self.tags, False)
            item_set.parse()

            self.parsed[ITEM_SET] = item_set.parsed[TAG]

        # Set the bitmap if it exists
        if BITMAP_ITEM in self.properties:
            self.parsed[BITMAP_ITEM] = self.properties[BITMAP_ITEM]

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

    def parse_formula(self):
        '''Parse the DBR file as a formula file'''

        # All formula's need an artifact to create:
        if ARTIFACT_NAME not in self.properties:
            return

        # Grab the artifact it will create:
        artifact_file = self.get_reference_dbr(self.properties[ARTIFACT_NAME])
        artifact = DBRReader(artifact_file, self.tags)
        artifact.parse()

        # Set the artifact tag and name for this formula:
        self.parsed[TAG] = artifact.parsed[TAG]
        self.parsed[NAME] = artifact.parsed[NAME]
        self.parsed[CLASSIFICATION] = artifact.parsed[CLASSIFICATION]

        # Parse the cost
        self.parse_cost()

        # Grab the reagents (ingredients):
        for index, prop in enumerate(FORMULA_REAGENT_TAGS):
            reagent_file = self.get_reference_dbr(
                                self.properties[prop])
            reagent = DBRReader(reagent_file, self.tags)
            reagent.parse()

            reagent_name = FORMULA_REAGENT_NAMES[index]

            # Add the reagent (relic, scroll or artifact)
            self.parsed[reagent_name] = reagent.parsed[TAG]

            # Add the name, from the tags list:
            self.parsed[reagent_name + 'Name'] = self.tags[
                                                    self.parsed[reagent_name]]

        # Set the bitmap if it exists
        if BITMAP_FORMULA in self.properties:
            self.parsed[BITMAP_FORMULA] = self.properties[BITMAP_FORMULA]

        # Add the potential completion bonuses
        bonus_file = self.get_reference_dbr(self.properties[FORMULA_BONUS])
        bonus = DBRReader(bonus_file, self.tags)
        bonus.parse()
        self.parsed[BONUS] = bonus.parsed.get(BONUS, [])

    def parse_item_skill_augment(self, tier=-1):
        '''Parse the item based skill augment DBR parameters'''

        # Set the properties to parse (tiered or non-tiered):
        properties = self.tiered[tier] if tier >= 0 else self.properties

        result = {}

        # Parse skills that are granted
        if ITEM_SKILL in properties:
            # Grab the skill file:
            skill_file = self.get_reference_dbr(properties[ITEM_SKILL])
            skill = DBRReader(skill_file, self.tags)
            skill.parse()

            if ITEM_SKILL_LEVEL in properties:
                skill.parsed[SKILL_LEVEL_LOWER] = int(self.properties
                                                      [ITEM_SKILL_LEVEL])

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

    def parse_loot_affix(self):
        self.parsed[TAG] = self.properties.get(LOOT_RANDOMIZER_NAME, None)
        self.parsed[NAME] = self.tags.get(self.parsed[TAG], '')

        # After setting the tag for the affix; just parse it as a base case
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

    def parse_loot_table(self):
        bonuses = []
        bonus_files = {}
        weights = {}

        # Parse the possible completion bonuses:
        for field, value in self.properties.items():
            if RANDOMIZER_NAME in field:
                number = re.search(r'\d+', field).group()
                bonus_files[number] = value
            if RANDOMIZER_WEIGHT in field:
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
            value_max = float(properties.get(field + SUFFIX_MAX, 0))
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
            absolute = (format_range.format(value_min, value_max)
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
                    result[field + SUFFIX_MOD + SUFFIX_GLOBAL] = modifier

                    if chance_xor and value_min:
                        # Normal case: both modifier and absolute
                        # damages can be chanced based.
                        if prop not in OFFENSIVE_FIELDS:
                            result[field + SUFFIX_GLOBAL] = absolute
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
                    result[field + SUFFIX_GLOBAL] = absolute
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
                result[STAT_MP_BURN + SUFFIX_GLOBAL] = mb_value
            else:
                result[STAT_MP_BURN] = mb_value

        # Now append teh chance properties if they exist:
        if chance_isset:
            result[chance_key] = chance_value

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
            if prop not in properties:
                continue

            # Start with an empty list for this bonus:
            result[prop] = []
            values = properties[prop].split(';')

            for i in range(0, len(bonus_list)):
                result[prop].append(output.format(float(values[0])
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
        self.parsed[TAG] = self.properties[DESCRIPTION]
        self.parsed[NAME] = self.tags[self.parsed[TAG]]
        self.parsed[DESCRIPTION] = self.tags[self.properties[ITEM_TEXT]]
        self.parsed[DIFFICULTY] = DIFFICULTIES[int(file_name[0][1:]) - 1]
        self.parsed[ACT] = file_name[1]

        # Set the bitmap if it exists
        if BITMAP_RELIC in self.properties:
            self.parsed[BITMAP_RELIC] = self.properties[BITMAP_RELIC]

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
            self.parse_racial(index)

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
            value_max = float(properties.get(field + SUFFIX_MAX, 0))
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
            absolute = (format_range.format(value_min, value_max)
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
                    result[field + SUFFIX_MOD + SUFFIX_GLOBAL] = modifier

                    if chance_xor and value_min:
                        # Normal case: both modifier and absolute
                        # damages can be chanced based.
                        if prop not in RETALIATION_FIELDS:
                            result[field + SUFFIX_GLOBAL] = absolute
                        # Edge case: for absolute retaliation fields, the
                        # absolute property will be a general property
                        # if it's set while the modifier is chanced
                        else:
                            result[field] = absolute
                else:
                    # Append flat (or range) damage to chances:
                    result[field + SUFFIX_GLOBAL] = absolute
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
            result[chance_key] = chance_value

        # Append the retaliation results to the properties:
        if tier == -1:
            self.parsed[PROPERTIES].update(result)
        else:
            self.parsed[PROPERTIES][tier].update(result)

    def parse_scroll(self):
        '''Parse the DBR file as a scroll file'''
        self.parsed[TAG] = self.properties[DESCRIPTION]
        self.parsed[NAME] = self.tags[self.parsed[TAG]]
        self.parsed[DESCRIPTION] = self.tags[self.properties[ITEM_TEXT]]

        # Parse the cost
        self.parse_cost()

        # Set the bitmap if it exists
        if BITMAP_ITEM in self.properties:
            self.parsed[BITMAP_ITEM] = self.properties[BITMAP_ITEM]

        # Grab the skill file:
        skill_file = self.get_reference_dbr(self.properties[SKILL_NAME_LOWER])
        skill = DBRReader(skill_file, self.tags)
        skill.parse()

        # Set the parsed skill as the scroll skill:
        self.parsed[SKILL_NAME_LOWER] = skill.parsed

    def parse_set(self):
        self.parsed[TAG] = self.properties.get(SET_NAME, '')
        self.parsed[NAME] = self.tags[self.parsed[TAG]]

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

        # Parse members (recursion check to prevent infinite member/set loop)
        if self.allow_recursion:
            self.parsed[SET_MEMBERS] = []
            for member in self.properties[SET_MEMBERS].split(';'):
                # Grab the member file and only extract name:
                member_file = self.get_reference_dbr(member)
                member = DBRReader(member_file, self.tags)
                member.parse()

                if(NAME in member.parsed):
                    member_tag = member.parsed[NAME]
                    self.parsed[SET_MEMBERS].append({
                        TAG: member.parsed[TAG],
                        NAME: member.parsed[NAME]})

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
        self.parsed[PATH] = DBRReader.format_path(self.dbr)

        if self.tiered:
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

            # Check if there's an ultimate level set, if so, cap the
            # tiers at that level:
            if SKILL_ULT in self.properties:
                skill_ult = int(self.properties[SKILL_ULT])

                if len(self.parsed[PROPERTIES]) > skill_ult:
                    self.parsed[PROPERTIES] = (self.parsed[PROPERTIES]
                                                          [:skill_ult - 1])
        else:
            # Parse properties normally:
            self.parsed[PROPERTIES] = {}

            # Parse the skill properties
            self.parse_character()
            self.parse_defensive()
            self.parse_offensive()
            self.parse_petbonus()
            self.parse_racial()
            self.parse_retaliation()
            self.parse_skill_properties()

    def parse_skill_buff(self):
        '''Parse the DBR reference skill buff file'''

        # Parse the buff file
        skill_buff_file = self.get_reference_dbr(
                            self.properties[DBR_BUFF_SKILL])
        skill_buff = DBRReader(skill_buff_file, self.tags)
        skill_buff.parse()

        # Set the known properties
        self.parsed = skill_buff.parsed
        self.parsed[PATH] = DBRReader.format_path(self.dbr)

    def parse_skill_pet(self):
        '''Parse the DBR reference pet modifier file'''

        # Parse the pet file
        skill_pet_file = self.get_reference_dbr(
                            self.properties[DBR_PET_SKILL])
        skill_pet = DBRReader(skill_pet_file, self.tags)
        skill_pet.parse()

        # Set the known properties
        self.parsed = skill_pet.parsed
        self.parsed[PATH] = DBRReader.format_path(self.dbr)

    def parse_skill_properties(self, tier=-1):
        '''Parses skill property DBR parameters'''

        # Set the properties to parse (tiered or non-tiered):
        properties = self.tiered[tier] if tier >= 0 else self.properties

        result = {}

        # Merge projectile & skill property fields:
        skill_property_fields = {
            **SKILL_PROPERTY_FIELDS,
            **PROJECTILE_FIELDS}
        for prop, output in skill_property_fields.items():
            # Setup the output chances, format, texts, and values
            chance = int(float(properties.get(prop + SUFFIX_CHANCE, 0)))
            value_min = int(float(properties.get(prop + SUFFIX_MIN, 0)))
            value_max = int(float(properties.get(prop + SUFFIX_MAX, 0)))
            value = float(properties.get(prop, 0))

            # Determine text output:
            if value > 0.01 or value_min:
                text = (output.format(value_min, value_max)
                        if value_min
                        else output.format(value))

                result[prop] = ([chance, text] if chance else text)

        # Last property to parse: Skill damage absorption (qualified)
        if SKILL_ABS in properties or SKILL_ABS_PCT in properties:
            field = SKILL_ABS if SKILL_ABS in properties else SKILL_ABS_PCT
            value = int(float(properties[field]))

            # Find qualifier damage type:
            for prop, qualifier in SKILL_QUALIFIER_FIELDS.items():
                if prop in properties and properties[prop]:
                    # Add the damage absorption
                    result[field] = SKILL_ABSORPTION_FORMAT[field].format(
                        value, qualifier)

            # If there is no qualifier, it's all damage:
            if field not in result:
                result[field] = SKILL_ABSORPTION_FORMAT[field].format(
                    value, 'All')

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
        self.parsed[PATH] = DBRReader.format_path(self.dbr)
        self.parsed[PET_OBJECT] = []

        # Run both tiered and non-tiered summons:
        spawn_tiers = self.tiered if self.tiered else [self.properties]
        for index, tier in enumerate(spawn_tiers):
            pet_result = {}

            # Parse the summon reference:
            spawn_file = self.get_reference_dbr(tier[PET_OBJECT])
            spawn = DBRReader(spawn_file, self.tags)
            spawn.parse()

            # Only set time to live it's it exists (otherwise it's infinite)
            if PET_TTL in tier:
                spawn.parsed[PET_TTL] = PET_TTL_TEXT.format(
                                            int(float(tier[PET_TTL])))

            if PET_LIMIT in tier:
                spawn.parsed[PET_LIMIT] = PET_LIMIT_TEXT.format(
                                            int(tier[PET_LIMIT]))

            if SKILL_COST in tier:
                spawn.parsed[SKILL_COST] = (SKILL_PROPERTY_FIELDS
                                            [SKILL_COST].format(
                                                int(float(tier[SKILL_COST]))))

            # Save the skills and the summon:
            del(spawn.parsed[TYPE])
            self.parsed[PET_OBJECT].append(spawn.parsed)

    def parse_skilltree(self):
        '''Parse a skill tree and set the skills found in there'''

        skills = []
        for prop, dbr in self.properties.items():
            if SKILL_NAME_LOWER in prop:
                skill_file = self.get_reference_dbr(dbr)
                skill = DBRReader(skill_file, self.tags)
                skill.parse()

                skills.append(skill.parsed)

        self.parsed[SKILLS] = skills

    def parse_summon(self):
        '''Parse the DBR referenced summon'''

        # Set HP/MP values as a list, in case there's difficult scaling:
        spawn_hp = self.properties.get(PREFIX_CHAR + STAT_HP, '0')
        if(spawn_hp != '0'):
            # Format the HP value to include text:
            spawn_hp = [int(float(hp)) for hp in spawn_hp.split(';')]
            spawn_hp_val = spawn_hp[0] if len(spawn_hp) == 1 else spawn_hp

            # Set the HP as a property
            self.parsed[PREFIX_CHAR + STAT_HP] = (
                str(spawn_hp_val) + CHARACTER_FIELDS[STAT_HP][TXT_ABS])

        # Set the min/max damage:
        damage_min = int(float(self.properties.get(PET_DMG + SUFFIX_MIN, 0)))
        damage_max = int(float(self.properties.get(PET_DMG + SUFFIX_MAX, 0)))
        if damage_min:
            self.parsed[PET_DMG] = (FORMAT_RANGE.format(damage_min, damage_max)
                                    if damage_max and damage_max > damage_min
                                    else damage_min) + ' Damage'

        self.parsed[SKILLS] = []
        # Parse all the normal skills:
        for i in range(1, PET_SKILL_NUM):
            name = self.properties.get(SKILL_NAME_LOWER + str(i), '')
            level = self.properties.get(SKILL_LEVEL_LOWER + str(i), '0')

            # Run a check for difficulty scaling skills, which are tiered:
            level = int(level) if ';' not in level else 0

            # Skip some of the passive skills pets get:
            if name.lower() in DBR_IGNORE:
                continue

            if name and level:
                self.parsed[SKILLS].append({
                    SKILL_NAME_LOWER: name,
                    SKILL_LEVEL_LOWER: level})

        # Parse initial skill:
        if PET_INIT_SKILL in self.properties:
            self.parsed[PET_INIT_SKILL] = self.properties[PET_INIT_SKILL]

        if PET_SPECIAL in self.properties:
            self.parsed[PET_SPECIAL] = self.properties[PET_SPECIAL]

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
                elif i >= len(value):
                    tier[key] = value[len(value) - 1]

            # Append this tier
            self.tiered.append(tier)

    def property_isset(self, property):
            try:
                float(property)
                return float(property) != 0
            except:
                return True

    @classmethod
    def format_path(cls, path):
        return re.sub(r'[\ \\]', '_', path).lower()
