from .constants import *


class DBRReader:
    '''Class that parses DBR files'''

    def __init__(self, dbr, skills):
        self.dbr = dbr
        self.properties = {}
        self.parsed = {}
        self.skills = skills

        try:
            self.file = open(dbr)
        except OSError:
            self.file = None

    def parse(self):
        if not self.file:
            return False

        # DBR file into a list of lines
        lines = [line.rstrip(',\n') for line in self.file]

        # Parse line into a dictionary of key, value properties:
        self.properties = dict([(k, v) for k, v in (dict(properties.split(',')
                               for properties in lines)).items()
                               if self.property_isset(v)])

        # Set the class type
        self.parsed[CLASS_TYPE] = self.properties.get(CLASS, '')

        # Determine what kind of file is being parsed:
        if(self.parsed[CLASS_TYPE] in CLASS_TYPE_EQUIPMENT):
            self.parse_equipment()
        elif(self.parsed[CLASS_TYPE] in CLASS_TYPE_RELIC):
            self.parse_relic()
        elif(self.parsed[CLASS_TYPE] in CLASS_TYPE_SCROLL):
            self.parse_scroll()
        elif(CLASS_TYPE_SKILL in self.parsed[CLASS_TYPE]):
            self.parse_skill()
        else: 
            self.parse_base()

    def parse_base(self):
        '''Parse the DBR file as a non-Classed file'''
        self.parsed[PROPERTIES] = {}
        self.parse_character()
        self.parse_defensive()
        self.parse_offensive()
        self.parse_retaliation()
        self.parse_skill_properties()

    def parse_equipment(self):
        '''Parse the DBR file as an equipment file'''

        # Based on the class, call the respective parse:
        self.parsed[ITEM_CLASSIFICATION] = (
            self.properties.get(ITEM_CLASSIFICATION, None))
        self.parsed[ITEM_LEVEL] = int(self.properties.get(ITEM_LEVEL, 0))
        self.parsed[ITEM_TAG] = self.properties.get(ITEM_TAG, None)

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

    def parse_relic(self):
        '''Parse the DBR file as a relic file'''

    def parse_scroll(self):
        '''Parse the DBR file as a scroll file'''

    def parse_skill(self):
        '''Parse the DBR file as a skill file'''

    def parse_character(self):
        '''Parse the character DBR parameters'''

        result = {}

        # Parse character bonuses (only absolutes and modifiers)
        for prop, output in CHARACTER_FIELDS.items():
            field = PREFIX_CHAR + prop

            format_absolute = output.get(TXT_FABS, FORMAT_INT_SIGNED)
            format_modifier = output.get(TXT_FMOD, FORMAT_MOD)
            text_absolute = output.get(TXT_ABS)
            text_modifier = output.get(TXT_MOD, text_absolute)
            value_absolute = float(self.properties.get(field, 0))
            value_modifier = float(self.properties.get(field + SUFFIX_MOD, 0))

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
            if field in self.properties:
                result[field] = FORMAT_REDUCTION.format(
                                float(self.properties[field])) + output

        # Append the character results to the properties:
        self.parsed[PROPERTIES].update(result)

    def parse_defensive(self):
        '''Parse the defensive DBR parameters'''
        result = {}

        for prop, output in DEFENSIVE_FIELDS.items():
            field = PREFIX_DEF + prop

            # Setup the output chances, format, texts, and values
            chance_absolute = int(float(
                self.properties.get(field + SUFFIX_CHANCE, 0)))
            chance_duration = int(float(
                self.properties.get(field + SUFFIX_DCHANCE, 0)))
            chance_modifier = int(float(
                self.properties.get(field + SUFFIX_MCHANCE, 0)))
            format_absolute = output.get(TXT_FABS, FORMAT_INT)
            format_modifier = output.get(TXT_FMOD, FORMAT_MOD)
            format_range = output.get(TXT_FRANGE, FORMAT_RANGE)
            text_absolute = output.get(TXT_ABS)
            text_duration = output.get(TXT_DUR, text_absolute)
            text_modifier = output.get(TXT_MOD, text_absolute)

            value = float(self.properties.get(field, 0))
            value_duration = float(self.properties.get(field + SUFFIX_DUR, 0))
            value_modifier = float(self.properties.get(field + SUFFIX_MOD, 0))

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
        self.parsed[PROPERTIES].update(result)

    def parse_item_skill_augment(self):
        result = {}

        if ITEM_SKILL in self.properties:

            # TODO: Fix tihs into a single line:
            skill_tag = self.properties[ITEM_SKILL].replace('\\', '_').lower()
            skill_tag = skill_tag.replace(' ', '_')

            # Find the skill:
            skill = self.find_skill(skill_tag)

            if skill:
                # Add skill json:
                result[ITEM_SKILL] = {
                    SKILL_TAG: skill[SKILL_TAG],
                    SKILL_DISPLAY: SKILL_GRANTS_FIELD + skill[SKILL_DNAME]
                }

        for augment_name, augment_level in SKILL_AUGMENT_FIELDS.items():
            if augment_name not in self.properties:
                continue

            # TODO: Fix tihs into a single line:
            skill_tag = self.properties[augment_name].lower()
            skill_tag = skill_tag.replace('\\', '_').replace(' ', '_')
            skill_level = self.properties[augment_level]

            # Find the skill:
            skill = self.find_skill(skill_tag)

            if not skill:
                continue

            result[augment_name] = {
                SKILL_TAG: skill[SKILL_TAG],
                SKILL_DISPLAY: SKILL_AUGMENT_FORMAT.format(
                                    skill_level, skill[SKILL_DNAME])
            }

        if SKILL_AUGMENT_ALL in self.properties:
            result[SKILL_AUGMENT_ALL] = SKILL_AUGMENT_ALL_FORMAT.format(
                                            self.properties[SKILL_AUGMENT_ALL])

        # Append the item skill results to the properties:
        self.parsed[PROPERTIES].update(result)

    def parse_offensive(self):
        '''Parse the offensive DBR parameters'''

        result = {}
        chance_properties = []
        chance_key = PREFIX_OFF + SUFFIX_GCHANCE
        chance_value = int(float(self.properties.get(chance_key, 0)))
        chance_isset = chance_key in self.properties

        offensive_fields = {
            **OFFENSIVE_FIELDS,
            **OFFENSIVE_DUR_DMG_FIELDS,
            **OFFENSIVE_DUR_EFF_FIELDS}

        for prop, output in offensive_fields.items():
            field = PREFIX_OFF + prop

            # Setup the output chances, format, texts, and values
            chance_absolute = int(float(
                self.properties.get(field + SUFFIX_CHANCE, 0)))
            chance_modifier = int(float(
                self.properties.get(field + SUFFIX_MCHANCE, 0)))
            chance_global = self.properties.get(field + SUFFIX_GLOBAL, 0)
            chance_xor = self.properties.get(field + SUFFIX_XOR, 0)

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

            value_min = float(self.properties.get(field + SUFFIX_MIN, 0))
            value_max = float(self.properties.get(field + SUFFIX_MIN, 0))
            value_modifier = float(self.properties.get(field + SUFFIX_MOD, 0))

            # Duration fields will only be relevant for non-absolute properties
            if prop not in OFFENSIVE_FIELDS:
                duration_min = float(
                    self.properties.get(field + SUFFIX_DURMIN, 0))
                duration_max = float(
                    self.properties.get(field + SUFFIX_DURMAX, 0))
                duration_mod = float(
                    self.properties.get(field + SUFFIX_DURMOD, 0))

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
                elif ((prop == DMG_PHYS and SUFFIX_WEAPON in self.classType) or
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
        mb_chance = int(self.properties.get(STAT_MP_BURN + SUFFIX_GLOBAL, 0))
        mb_min = float(self.properties.get(STAT_MP_BURN_MIN, 0))
        mb_max = float(self.properties.get(STAT_MP_BURN_MAX, 0))
        mb_ratio = float(self.properties.get(STAT_MP_BURN_RATIO, 0))

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
        self.parsed[PROPERTIES].update(result)

    def parse_petbonus(self):
        '''Parse the pet bonus DBR parameters'''
        if DBR_PET_BONUS in self.properties:
            # Parse the pet bonus file
            pet_bonus_file = self.get_reference_dbr(
                             self.properties[DBR_PET_BONUS])
            pet_bonus = DBRReader(pet_bonus_file, self.skills)
            pet_bonus.parse()

            # Append the bonus
            self.parsed[PROPERTIES][DBR_PET_BONUS] = (
                pet_bonus.parsed[PROPERTIES])

    def parse_racial(self):
        '''Parse the racial bonus DBR parameters'''

        if STAT_RACE not in self.properties:
            return

        result = {}
        bonus_list = self.properties[STAT_RACE].split(';')
        for prop, output in RACIAL_FIELDS.items():
            field = PREFIX_RACE + prop

            if field not in self.properties:
                continue

            # Start with an empty list for this bonus:
            result[field] = []
            values = self.properties[field].split(';')

            for i in range(0, len(bonus_list)):
                result[field].append(output.format(float(values[0])
                                     if len(bonus_list)
                                     else value[i],
                                     bonus_list[i]))

    def parse_retaliation(self):
        '''Parse the retaliation DBR parameters'''

        result = {}
        chance_properties = []
        chance_key = PREFIX_RETAL + SUFFIX_GCHANCE
        chance_value = int(float(self.properties.get(chance_key, 0)))
        chance_isset = chance_key in self.properties

        retaliation_fields = {
            **RETALIATION_FIELDS,
            **RETALIATION_DUR_DMG_FIELDS,
            **RETALIATION_DUR_EFF_FIELDS}

        for prop, output in retaliation_fields.items():
            field = PREFIX_RETAL + prop

            # Setup the output chances, format, texts, and values
            chance_absolute = int(float(
                self.properties.get(field + SUFFIX_CHANCE, 0)))
            chance_modifier = int(float(
                self.properties.get(field + SUFFIX_MCHANCE, 0)))
            chance_global = self.properties.get(field + SUFFIX_GLOBAL, 0)
            chance_xor = self.properties.get(field + SUFFIX_XOR, 0)

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

            value_min = float(self.properties.get(field + SUFFIX_MIN, 0))
            value_max = float(self.properties.get(field + SUFFIX_MIN, 0))
            value_modifier = float(self.properties.get(field + SUFFIX_MOD, 0))

            # Duration fields will only be relevant for non-absolute properties
            if prop not in RETALIATION_FIELDS:
                duration_min = float(
                    self.properties.get(field + SUFFIX_DURMIN, 0))
                duration_max = float(
                    self.properties.get(field + SUFFIX_DURMAX, 0))
                duration_mod = float(
                    self.properties.get(field + SUFFIX_DURMOD, 0))

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
        self.parsed[PROPERTIES].update(result)

    def parse_skill_properties(self):
        result = {}

        '''Parses skill property DBR parameters'''
        for prop, output in SKILL_PROPERTY_FIELDS.items():
            field = PREFIX_SKILL = prop

            # Setup the output chances, format, texts, and values
            chance_absolute = int(float(
                self.properties.get(field + SUFFIX_CHANCE, 0)))
            format_absolute = (output.get(TXT_FABS, FORMAT_INT)
                               if isinstance(output, dict)
                               else FORMAT_INT)
            text_absolute = (output.get(TXT_ABS)
                             if isinstance(output, dict)
                             else output)
            value_absolute = float(self.properties.get(field, 0))
            absolute = format_absolute.format(value_absolute) + (
                       text_absolute)

            if value_absolute:
                result[field] = ([chance_absolute, absolute]
                                 if chance_absolute
                                 else absolute)

        # Append the skill results to the properties:
        self.parsed[PROPERTIES].update(result)

    def get_reference_dbr(self, new_dbr):
        ''' Return path to new file by replacing the last part.
        Example self.dbr will be:
        C:/Users/Fons/TQDB/Records/Items/foo/bar
        and the new_dbr will be
        Records/Items/foo/waz
        The result will be
         C:/Users/Fons/Records/Items/foo/waz'''
        try:
            new_dbr = new_dbr.lower()
            return self.dbr[:self.dbr.index(new_dbr.split('\\')[0])] + new_dbr
        except ValueError:
            return None

    def find_skill(self, needle):
        ''' Test if a skill is set in the known skill list, either
        the actual skill name or a reference pet or buff skill name'''

        # Check if needle is the key in the skill list
        if needle in self.skills:
            return self.skills[needle]

        # Check if the needle is a buff or pet reference
        for key, haystack in self.skills.items():
            if haystack.get(DBR_BUFF_SKILL, None) == needle:
                return haystack.get(DBR_BUFF_SKILL)
            elif haystack.get(DBR_PET_SKILL, None) == needle:
                return haystack.get(DBR_PET_SKILL)

        return False

    def property_isset(self, property):
        try:
            float(property)
            return float(property) != 0
        except:
            return True
