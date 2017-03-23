"""
Field classes for the TQDB parsers.

"""
CHANCE = 'ChanceOfTag'
DOT_SINGLE = 'offensiveSingleFormatTime'
EOT_SINGLE = 'offensiveFixedSingleFormatTime'
IMPRV_TIME = 'ImprovedTimeFormat'


class CharacterBase:
    """
    The base character field class.

    """
    def __init__(self, props, field, strings):
        self.field = field
        self.parsed = {}
        self.strings = strings

        # Parse values:
        self.val = float(props.get(field, 0))
        self.mod = int(float(props.get(field + 'Modifier', 0)))

    def parse(self):
        field = self.field
        strings = self.strings

        if self.val:
            self.parsed[field] = strings[field].format(self.val)

        if self.mod:
            field_mod = field + 'Modifier'
            self.parsed[field_mod] = strings[field_mod].format(self.mod)

        return self.parsed


class DefensiveBase:
    """
    The base defensive field class.

    """
    def __init__(self, props, field, strings):
        self.field = field
        self.parsed = {}
        self.strings = strings

        # Parse values:
        self.chance = int(float(props.get(field + 'Chance', 0)))
        self.mod = int(float(props.get(field + 'Modifier', 0)))
        self.mod_chance = int(float(props.get(field + 'ModifierChance', 0)))

        # TotalSpeed is the only field with 'Resistance' suffix for its value:
        if field == 'defensiveTotalSpeed':
            self.val = float(props.get(field + 'Resistance', 0))
        else:
            self.val = float(props.get(field, 0))

    def parse(self):
        field = self.field
        strings = self.strings

        if self.val:
            formatted = strings[field].format(self.val)

            if self.chance:
                formatted = strings[CHANCE].format(self.chance) + formatted

            self.parsed[field] = formatted

        if self.mod:
            formatted = strings[field + 'Modifier'].format(self.mod)

            if self.mod_chance:
                formatted = strings[CHANCE].format(self.mod_chance) + formatted

            self.parsed[field + 'Modifier'] = formatted

        return self.parsed


class OffensiveBase:
    """
    The base offensive field class.

    """
    def __init__(self, props, field, strings):
        self.field = field
        self.parsed = {}
        self.strings = strings

        # Parse values
        self.chance = int(float(props.get(field + 'Chance', 0)))
        self.min = float(props.get(field + 'Min', 0))
        self.max = float(props.get(field + 'Max', 0))

        # Parse booleans:
        self.is_global = props.get(field + 'Global', 0) == '1'
        self.is_xor = props.get(field + 'XOR', 0) == '1'


class OffensiveAbsolute(OffensiveBase):
    """
    The absolute offensive damage class.

    There is no duration on these fields.
    """
    def __init__(self, props, field, strings):
        super().__init__(props, field, strings)

        # Add modifier chances:
        self.mod = int(float(props.get(field + 'Modifier', 0)))
        self.mod_chance = int(float(props.get(field + 'ModifierChance', 0)))

    def parse(self):
        field = self.field
        strings = self.strings

        if self.min:
            formatted = (strings[field + 'Ranged'].format(self.min, self.max)
                         if self.max > self.min and field + 'Ranged' in strings
                         else strings[field].format(self.min))

            if self.chance and not self.is_xor:
                formatted = strings[CHANCE].format(self.chance) + formatted

            self.parsed[field] = formatted

        if self.mod:
            formatted = strings[field + 'Modifier'].format(self.mod)

            if self.mod_chance and not self.is_xor:
                formatted = strings[CHANCE].format(self.mod_chance) + formatted

            self.parsed[field + 'Modifier'] = formatted

        return self.parsed


class OffensiveDOT(OffensiveAbsolute):
    """
    The damage over time offensive damage class.

    The duration fields impact the damage done.
    """
    def __init__(self, props, field, strings):
        super().__init__(props, field, strings)

        # Add DOT fields:
        self.duration_max = float(props.get(field + 'DurationMax', 0))
        self.duration_min = float(props.get(field + 'DurationMin', 0))
        self.duration_mod = float(props.get(field + 'DurationModifier', 0))

    def parse(self):
        field = self.field
        strings = self.strings

        if self.min:
            # Recalculate min/max damage if a duration is set:
            if self.duration_min:
                self.min *= self.duration_min

                if self.duration_max and not self.max:
                    self.max = self.min * self.duration_max
                elif self.max:
                    self.max *= self.duration_min

            # Resulting string is either flat or ranged value:
            formatted = (strings[field + 'Ranged'].format(self.min, self.max)
                         if self.max > self.min else
                         strings[field].format(self.min))

            # Add a suffix "over x Seconds" if appropriate:
            if self.duration_min:
                formatted += strings[DOT_SINGLE].format(self.duration_min)

            if self.chance and not self.is_xor:
                formatted = strings[CHANCE].format(self.chance) + formatted

            self.parsed[field] = formatted

        if self.mod or self.duration_mod:
            formatted = strings[field + 'Modifier'].format(self.mod)

            if self.duration_mod:
                formatted += strings[IMPRV_TIME].format(self.duration_mod)

            if self.mod_chance and not self.is_xor:
                formatted = strings[CHANCE].format(self.mod_chance) + formatted

            self.parsed[field + 'Modifier'] = formatted

        return self.parsed


class OffensiveEOT(OffensiveAbsolute):
    """
    The effect over time offensive damage class.

    The duration fields determines the effect duration.
    """
    def __init__(self, props, field, strings):
        super().__init__(props, field, strings)

        # Add DOT fields:
        self.duration_max = float(props.get(field + 'DurationMax', 0))
        self.duration_min = float(props.get(field + 'DurationMin', 0))
        self.duration_mod = float(props.get(field + 'DurationModifier', 0))

    def parse(self):
        field = self.field
        strings = self.strings

        if self.min:
            # Resulting string is either flat or ranged value:
            formatted = (strings[field + 'Ranged'].format(self.min, self.max)
                         if self.max > self.min else
                         strings[field].format(self.min))

            # Add a suffix "for x Seconds" if appropriate:
            if self.duration_min:
                formatted += strings[EOT_SINGLE].format(self.duration_min)

            if self.chance and not self.is_xor:
                formatted = strings[CHANCE].format(self.chance) + formatted

            self.parsed[field] = formatted

        if self.mod or self.duration_mod:
            formatted = strings[field + 'Modifier'].format(self.mod)

            if self.duration_mod:
                formatted += strings[IMPRV_TIME].format(self.duration_mod)

            if self.mod_chance and not self.is_xor:
                formatted = strings[CHANCE].format(self.mod_chance) + formatted

            self.parsed[field + 'Modifier'] = formatted

        return self.parsed


class SkillPropertyBase():
    """
    The skill property class.

    """
    def __init__(self, props, field, strings):
        self.field = field
        self.parsed = {}
        self.strings = strings

        # Parse values
        self.chance = int(float(props.get(field + 'Chance', 0)))
        self.val = float(props.get(field, 0))
        self.min = int(float(props.get(field + 'Min', 0)))
        self.max = int(float(props.get(field + 'Max', 0)))

    def parse(self):
        field = self.field
        strings = self.strings

        if self.val > 0.01 or self.min:
            formatted = (strings[field + 'Ranged'].format(self.min, self.max)
                         if self.max > self.min and field + 'Ranged' in strings
                         else strings[field].format(self.val))

            if self.chance:
                formatted = strings[CHANCE].format(self.chance) + formatted

            self.parsed[field] = formatted

        return self.parsed
