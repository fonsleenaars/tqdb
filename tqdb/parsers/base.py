"""
Base templates that are often included by other templates.

"""
from tqdb import dbr as DBRParser
from tqdb import storage
from tqdb.parsers.main import TQDBParser
from tqdb.utils.text import texts

# Some shared core constants:
CHANCE = 'ChanceOfTag'

IMPRV_TIME = 'ImprovedTimeFormat'
GLOBAL_ALL = 'GlobalChanceOfAllTag'
GLOBAL_PCT = 'GlobalPercentChanceOfAllTag'
GLOBAL_XOR_ALL = 'GlobalChanceOfOneTag'
GLOBAL_XOR_PCT = 'GlobalPercentChanceOfOneTag'

# Damage single value formats
# {%.0f0}
DMG_SINGLE = 'DamageSingleFormat'
# {%.1f0}
DMG_SINGLE_DECIMAL = 'DamageInfluenceSingleFormat'

# Damage range value formats
# {%.0f0} ~ {%.0f1}
DMG_RANGE = 'DamageRangeFormat'
# {%.1f0} ~ {%.1f1}
DMG_RANGE_DECIMAL = 'DamageInfluenceRangeFormat'

# Damage over/for time formats
# over {%.1f0} - {%.1f1} Seconds
DOT_RANGE = 'DamageRangeFormatTime'
# over {%.1f0} Seconds
DOT_SINGLE = 'DamageSingleFormatTime'
# for {%.1f0} - {%.1f1} Seconds
DFT_RANGE = 'DamageFixedRangeFormatTime'
# for {%.1f0} Seconds
DFT_SINGLE = 'DamageFixedSingleFormatTime'


class ParametersCharacterParser(TQDBParser):
    """
    Parser for `templatebase/parameters_character.tpl`.

    """
    FIELDS = [
        'characterArmorStrengthReqReduction',
        'characterArmorDexterityReqReduction',
        'characterArmorIntelligenceReqReduction',
        'characterAttackSpeedModifier',
        'characterDefensiveAbility',
        'characterDefensiveBlockRecoveryReduction',
        'characterDeflectProjectile',
        'characterDexterity',
        'characterDodgePercent',
        'characterEnergyAbsorptionPercent',
        'characterGlobalReqReduction',
        'characterHuntingStrengthReqReduction',
        'characterHuntingDexterityReqReduction',
        'characterHuntingIntelligenceReqReduction',
        'characterIncreasedExperience',
        'characterIntelligence',
        'characterJewelryStrengthReqReduction',
        'characterJewelryDexterityReqReduction',
        'characterJewelryIntelligenceReqReduction',
        'characterLevelReqReduction',
        'characterLife',
        'characterLifeRegen',
        'characterOffensiveAbility',
        'characterMana',
        'characterManaLimitReserve',
        'characterManaLimitReserveReduction',
        'characterManaRegen',
        'characterMeleeStrengthReqReduction',
        'characterMeleeDexterityReqReduction',
        'characterMeleeIntelligenceReqReduction',
        'characterRunSpeed',
        'characterShieldStrengthReqReduction',
        'characterShieldDexterityReqReduction',
        'characterShieldIntelligenceReqReduction',
        'characterSpellCastSpeed',
        'characterStaffStrengthReqReduction',
        'characterStaffDexterityReqReduction',
        'characterStaffIntelligenceReqReduction',
        'characterStrength',
        'characterTotalSpeed',
        'characterWeaponStrengthReqReduction',
        'characterWeaponDexterityReqReduction',
        'characterWeaponIntelligenceReqReduction',
    ]

    def __init__(self):
        super().__init__()

    def get_priority(self):
        """
        Override this parsers priority to set as highest.

        """
        return TQDBParser.HIGHEST_PRIORITY

    @staticmethod
    def get_template_path():
        return f'{TQDBParser.base}\\templatebase\\parameters_character.tpl'

    def parse(self, dbr, dbr_file, result):
        """
        Parse the character properties.

        """
        for field in self.FIELDS:
            # Find whether the flat, modifier, or both fields are present:
            mod = f'{field}Modifier'

            iterations = max(
                len(dbr[field]) if field in dbr else 0,
                len(dbr[mod]) if mod in dbr else 0,
                0)

            # Boolean to indicate if a single value is being inserted:
            is_singular = iterations == 1

            # Now iterate as many times as is necessary for this field:
            for index in range(iterations):
                # Create a new copy of the DBR with the values for this index:
                itr_dbr = TQDBParser.extract_values(dbr, field, index)

                if field in itr_dbr:
                    # Insert the flat (+...) version:
                    TQDBParser.insert_value(
                        field, texts.get(field).format(itr_dbr[field]),
                        is_singular, result)
                if mod in itr_dbr:
                    # Insert the modifier (+...%) version:
                    TQDBParser.insert_value(
                        mod, texts.get(mod).format(itr_dbr[mod]),
                        is_singular, result)


class ParmatersDefensiveParser(TQDBParser):
    """
    Parser for `templatebase/parameters_defensive.tpl`.

    """
    FIELDS = [
        'defensiveAbsorption',
        'defensiveBleeding',
        'defensiveBleedingDuration',
        'defensiveBlockModifier',
        'defensiveConfusion',
        'defensiveConvert',
        'defensiveCold',
        'defensiveColdDuration',
        'defensiveDisruption',
        'defensiveElementalResistance',
        'defensiveFear',
        'defensiveFire',
        'defensiveFireDuration',
        'defensiveFreeze',
        'defensiveLife',
        'defensiveLifeDuration',
        'defensiveLightning',
        'defensiveLightningDuration',
        'defensiveManaBurnRatio',
        'defensivePercentCurrentLife',
        'defensivePetrify',
        'defensivePhysical',
        'defensivePhysicalDuration',
        'defensivePierce',
        'defensivePierceDuration',
        'defensivePoison',
        'defensivePoisonDuration',
        'defensiveProtection',
        'defensiveReflect',
        'defensiveSlowLifeLeach',
        'defensiveSlowLifeLeachDuration',
        'defensiveSlowManaLeach',
        'defensiveSlowManaLeachDuration',
        'defensiveSleep',
        'defensiveStun',
        'defensiveTaunt',
        'defensiveTotalSpeed',
        'defensiveTrap',
    ]

    def __init__(self):
        super().__init__()

    def get_priority(self):
        """
        Override this parsers priority to set as highest.

        """
        return TQDBParser.HIGHEST_PRIORITY

    @staticmethod
    def get_template_path():
        return f'{TQDBParser.base}\\templatebase\\parameters_defensive.tpl'

    def parse(self, dbr, dbr_file, result):
        """
        Parse the defensive properties.

        """
        for field in self.FIELDS:
            # Find whether the flat, modifier, or both fields are present:
            mod = f'{field}Modifier'

            iterations = max(
                len(dbr[field]) if field in dbr else 0,
                len(dbr[mod]) if mod in dbr else 0,
                1)

            # Boolean to indicate if a single value is being inserted:
            is_singular = iterations == 1

            # Now iterate as many times as is necessary for this field:
            for index in range(iterations):
                # Create a new copy of the DBR with the values for this index:
                itr_dbr = TQDBParser.extract_values(dbr, field, index)

                # defensiveTotalSpeed has a 'Resistance' suffix for its value.
                if field == 'defensiveTotalSpeed':
                    field_value = itr_dbr.get(f'{field}Resistance', 0)
                else:
                    field_value = itr_dbr.get(field, 0)

                if field_value:
                    # Parse the flat (+...) version:
                    chance = itr_dbr.get(f'{field}Chance', 0)
                    value = texts.get(field).format(field_value)

                    if chance:
                        # Prefix the
                        value = texts.get(CHANCE).format(chance) + value

                    TQDBParser.insert_value(field, value, is_singular, result)
                if mod in itr_dbr:
                    # Add the modifier (%) version of the field:
                    chance = itr_dbr.get(f'{mod}Chance', 0)
                    value = texts.get(mod).format(itr_dbr[mod])

                    if chance:
                        # Prefix the
                        value = texts.get(CHANCE).format(chance) + value

                    TQDBParser.insert_value(mod, value, is_singular, result)


class ItemSkillAugmentParser(TQDBParser):
    """
    Parser for `templatebase/itemskillaugments.tpl`.

    """
    # DBR constants used by this parser
    AUGMENT_ALL = 'augmentAllLevel'
    SKILL_LEVEL = 'itemSkillLevel'
    SKILL_NAME = 'itemSkillName'

    # Texts used by this parser
    TXT_GRANT = 'Grants skill: Level {0:d} {1:s}'
    TXT_GRANT_LVL1 = 'Grants skill: {0:s}'
    TXT_ALL_INC = 'ItemAllSkillIncrement'
    TXT_MASTERY_INC = 'ItemMasteryIncrement'
    TXT_SKILL_INC = 'ItemSkillIncrement'

    # Skill augments (+# to Skill or Mastery)
    SKILL_AUGMENTS = {
        'augmentSkillName1': 'augmentSkillLevel1',
        'augmentSkillName2': 'augmentSkillLevel2',
        'augmentMasteryName1': 'augmentMasteryLevel1',
        'augmentMasteryName2': 'augmentMasteryLevel2',
    }

    def __init__(self):
            super().__init__()

    def get_priority(self):
        """
        Override this parsers priority to set as highest.

        """
        return TQDBParser.HIGHEST_PRIORITY

    @staticmethod
    def get_template_path():
        return f'{TQDBParser.base}\\templatebase\\itemskillaugment.tpl'

    def parse(self, dbr, dbr_file, result):
        """
        Parse skill augments, mastery augments, and item granted skills.

        """
        self._parse_skill_grant(dbr, result)

        # Parse skills that are augmented:
        for name, level in self.SKILL_AUGMENTS.items():
            # Skip skills without both the name and level set:
            if name not in dbr or level not in dbr:
                continue

            skill = DBRParser.parse(dbr[name])
            # Store the skill, which will ensure a unique tag:
            skill_tag = storage.store_skill(skill)
            level = dbr[level]

            # Skill format is either ItemSkillIncrement or ItemMasteryIncrement
            skill_format = (self.TXT_SKILL_INC
                            if 'Mastery' not in skill['name']
                            else self.TXT_MASTERY_INC)

            result['properties'][name] = {
                'tag': skill_tag,
                'name': texts.get(skill_format).format(level, skill['name']),
            }

        # Parse augment to all skills:
        if self.AUGMENT_ALL in dbr:
            level = dbr[self.AUGMENT_ALL]
            result['properties'][self.AUGMENT_ALL] = (
                texts.get(self.TXT_ALL_INC).format(level))

    def _parse_skill_grant(self, dbr, result):
        """
        Parse a granted skill.

        """
        # Skip files without both granted skill name and level:
        if self.SKILL_NAME not in dbr or self.SKILL_LEVEL not in dbr:
            return

        level = dbr[self.SKILL_LEVEL]
        skill = DBRParser.parse(dbr[self.SKILL_NAME])

        if 'name' not in skill:
            return

        # Store the skill, which will ensure a unique tag:
        skill_tag = storage.store_skill(skill)

        # Now add the granted skill to the item:
        result['properties'][self.SKILL_NAME] = {
            'tag': skill_tag,
            'level': level,
        }


class ParametersOffensiveParser(TQDBParser):
    """
    Parser for `templatebase/parameters_offensive.tpl`.

    """
    # A few constants to indicate the type of parsing needed
    ABSOLUTE = 'absolute'
    DOT = 'damageOverTime'
    EOT = 'effectOverTime'
    MANA = 'mana'

    FIELDS = {
        'offensiveBaseCold': ABSOLUTE,
        'offensiveBaseFire': ABSOLUTE,
        'offensiveBaseLife': ABSOLUTE,
        'offensiveBaseLightning': ABSOLUTE,
        'offensiveBasePoison': ABSOLUTE,
        'offensiveBonusPhysical': ABSOLUTE,
        'offensiveCold': ABSOLUTE,
        'offensiveConfusion': EOT,
        'offensiveConvert': EOT,
        'offensiveDisruption': EOT,
        'offensiveElemental': ABSOLUTE,
        'offensiveFear': EOT,
        'offensiveFire': ABSOLUTE,
        'offensiveFreeze': EOT,
        'offensiveFumble': EOT,
        'offensiveManaBurn': MANA,
        'offensiveLife': ABSOLUTE,
        'offensiveLifeLeech': ABSOLUTE,
        'offensiveLightning': ABSOLUTE,
        'offensivePercentCurrentLife': ABSOLUTE,
        'offensivePhysical': ABSOLUTE,
        'offensivePierce': ABSOLUTE,
        'offensivePierceRatio': ABSOLUTE,
        'offensivePoison': ABSOLUTE,
        'offensivePetrify': EOT,
        'offensiveProjectileFumble': EOT,
        'offensiveSleep': EOT,
        'offensiveSlowAttackSpeed': EOT,
        'offensiveSlowBleeding': DOT,
        'offensiveSlowCold': DOT,
        'offensiveSlowDefensiveAbility': EOT,
        'offensiveSlowDefensiveReduction': EOT,
        'offensiveSlowFire': DOT,
        'offensiveSlowLife': DOT,
        'offensiveSlowLifeLeach': DOT,
        'offensiveSlowLightning': DOT,
        'offensiveSlowManaLeach': DOT,
        'offensiveSlowOffensiveAbility': EOT,
        'offensiveSlowOffensiveReduction': EOT,
        'offensiveSlowPhysical': DOT,
        'offensiveSlowPoison': DOT,
        'offensiveSlowRunSpeed': EOT,
        'offensiveSlowSpellCastSpeed': EOT,
        'offensiveSlowTotalSpeed': EOT,
        'offensiveStun': EOT,
        'offensiveTotalDamage': ABSOLUTE,
        'offensiveTotalDamageReductionAbsolute': EOT,
        'offensiveTotalDamageReductionPercent': EOT,
        'offensiveTotalResistanceReductionAbsolute': EOT,
        'offensiveTotalResistanceReductionPercent': EOT,
        'offensiveTrap': EOT,
        'retaliationCold': ABSOLUTE,
        'retaliationElemental': ABSOLUTE,
        'retaliationFire': ABSOLUTE,
        'retaliationLife': ABSOLUTE,
        'retaliationLightning': ABSOLUTE,
        'retaliationPercentCurrentLife': ABSOLUTE,
        'retaliationPhysical': ABSOLUTE,
        'retaliationPierce': ABSOLUTE,
        'retaliationPierceRatio': ABSOLUTE,
        'retaliationPoison': ABSOLUTE,
        'retaliationSlowAttackSpeed': EOT,
        'retaliationSlowBleeding': DOT,
        'retaliationSlowCold': DOT,
        'retaliationSlowDefensiveAbility': EOT,
        'retaliationSlowFire': DOT,
        'retaliationSlowLife': DOT,
        'retaliationSlowLifeLeach': DOT,
        'retaliationSlowLightning': DOT,
        'retaliationSlowManaLeach': DOT,
        'retaliationSlowOffensiveAbility': EOT,
        'retaliationSlowOffensiveReduction': EOT,
        'retaliationSlowPhysical': DOT,
        'retaliationSlowRunSpeed': EOT,
        'retaliationSlowPoison': DOT,
        'retaliationSlowSpellCastSpeed': EOT,
        'retaliationStun': ABSOLUTE,
    }

    def __init__(self):
        super().__init__()

    def get_priority(self):
        """
        Override this parsers priority to set as highest.

        """
        return TQDBParser.HIGHEST_PRIORITY

    @staticmethod
    def get_template_path():
        # Note: technically this parser is also handling:
        # - parameters_retaliation.tpl and
        # - parameters_weaponsbonusoffensive.tpl
        return f'{TQDBParser.base}\\templatebase\\parameters_offensive.tpl'

    @classmethod
    def format(cls, field_type, field, min, max):
        """
        Format a specific field.

        A field is formatted by determining the numeric format and appending
        the text specific for that field.

        """
        if max > min:
            if field_type == cls.EOT:
                # Effect damage is done in seconds, so add a decimal
                value = texts.get(DMG_RANGE_DECIMAL).format(min, max)
            else:
                # DOT and regular damage is flat, so no decimals:
                value = texts.get(DMG_RANGE).format(min, max)
        else:
            if field_type == cls.EOT:
                # Effect damage is done in seconds, so add a decimal
                value = texts.get(DMG_SINGLE_DECIMAL).format(min)
            else:
                # DOT and regular damage is flat, so no decimals:
                value = texts.get(DMG_SINGLE).format(min)

        return f'{value}{texts.get(field)}'

    def parse(self, dbr, dbr_file, result):
        """
        Parse an offensive/retaliation field.

        For each field, depending on the group it's in, this function will need
        to check both the absolute (flat increase) and modifier (% increase)
        versions as well as possible effects or damage durations.

        Args:
            field (str): Field name, as listed in the FIELDS list

        """
        # Set the result and prepare the global stores:
        self.result = result
        self.offensive = {}
        self.offensiveXOR = False
        self.retaliation = {}
        self.retaliationXOR = False

        for field, field_type in self.FIELDS.items():
            # Find whether the flat, modifier, or both fields are present:
            min = (f'{field}Min'
                   if field != 'offensiveManaBurn'
                   # Mana burn is the only field that differs from the rest
                   else 'offensiveManaBurnDrainMin')
            mod = f'{field}Modifier'

            iterations = max(
                len(dbr[min]) if min in dbr else 0,
                len(dbr[mod]) if mod in dbr else 0,
                0)

            self.is_singular = iterations == 1

            # Now iterate as many times as is necessary for this field:
            for index in range(iterations):
                # Create a new copy of the DBR with the values for this index:
                itr_dbr = TQDBParser.extract_values(dbr, field, index)

                if min in itr_dbr:
                    # Parse the flat (+...) version:
                    self.parse_flat(field, field_type, itr_dbr)
                if mod in itr_dbr:
                    # Parse the modifier (+...%) version
                    self.parse_modifier(field, field_type, itr_dbr)

        # Now add the global chance tags if they're set:
        offensive_key = 'offensiveGlobalChance'
        if offensive_key in dbr and self.offensive:
            # Skip 0 chance globals altogether
            chances = [chance for chance in dbr[offensive_key] if chance]

            for index, chance in enumerate(chances):
                self.parse_global(
                    offensive_key,
                    # The global chance for the offensive properties
                    chance,
                    # If any global offensive properties are XOR-ed:
                    self.offensiveXOR,
                    # The dictionary of global offensive properties
                    self.offensive,
                    # Index of this global chance
                    index)

        retaliation_key = 'retaliationGlobalChance'
        if retaliation_key in dbr and self.retaliation:
            # Skip 0 chance globals altogether
            chances = [chance for chance in dbr[retaliation_key] if chance]

            for index, chance in enumerate(chances):
                self.parse_global(
                    retaliation_key,
                    # The global chance for the offensive properties
                    chance,
                    # If any global offensive properties are XOR-ed:
                    self.retaliationXOR,
                    # The dictionary of global offensive properties
                    self.retaliation,
                    # Index of this global chance
                    index)

    def parse_global(self, key, chance, xor, all_fields, index):
        """
        Add a global chance for properties.

        This is where multiple properties can be triggered by a chance, like

        10% Chance for one of the following:
            - ...
            - ...
        """
        # Grab the value for this index from the global stores:
        fields = dict(
            (k, v[index])
            if index < len(v)
            # If this value isn't repeated, grab the last value
            else (k, v[len(v) - 1])
            for k, v in all_fields.items())

        # Check if the XOR was set for any field:
        if xor:
            value = {
                'chance': (
                    texts.get(GLOBAL_XOR_ALL)
                    if chance == 100
                    else texts.get(GLOBAL_XOR_PCT).format(chance)),
                'properties': fields,
            }
        else:
            value = {
                'chance': (
                    texts.get(GLOBAL_ALL).format('')
                    if chance == 100
                    else texts.get(GLOBAL_PCT).format(chance)),
                'properties': self.offensive,
            }

        # Insert the value normally
        TQDBParser.insert_value(key, value, self.is_singular, self.result)

    def parse_flat(self, field, field_type, dbr):
        """
        Parse a flat increase in an offensive attribute.

        """
        # Prepare some keys that will determine the flat or flat range:
        chance = dbr.get(f'{field}Chance', 0)
        min = dbr.get(f'{field}Min', 0)
        max = dbr.get(f'{field}Max', min)
        is_xor = dbr.get(f'{field}XOR', False)
        is_global = dbr.get(f'{field}Global', False)

        # Optional pre/suffix for chance and duration damage/effects:
        prefix = ''
        suffix = ''

        if field_type == self.MANA:
            # The mana burn suffixes are kind of derpy:
            chance = dbr.get('offensiveManaBurnChance', 0)
            min = dbr.get('offensiveManaBurnDrainMin', 0)
            max = dbr.get('offensiveManaBurnDrainMax', 0)
            is_xor = dbr.get(f'{field}XOR', False)
            ratio = dbr.get('offensiveManaBurnDamageRatio', 0)

            if ratio:
                suffix = texts.get('offensiveManaBurnRatio').format(ratio)

            # Reset the field to what's used in texts.
            field = 'offensiveManaDrain'
        elif field_type == self.DOT:
            duration_min = dbr.get(f'{field}DurationMin', 0)
            duration_max = dbr.get(f'{field}DurationMax', 0)

            if duration_min:
                min *= duration_min
                suffix = texts.get(DOT_SINGLE).format(duration_min)

                if duration_max and max == min:
                    max = min * duration_max
                elif max:
                    max *= duration_min
        elif field_type == self.EOT:
            duration_min = dbr.get(f'{field}DurationMin', 0)

            if duration_min:
                suffix = texts.get(DFT_SINGLE).format(duration_min)

        # Format the value based on its field type and values:
        value = self.format(field_type, field, min, max)

        if chance and not is_xor:
            prefix = texts.get(CHANCE).format(chance)

        if not is_global:
            # Insert the value normally
            TQDBParser.insert_value(
                field,
                f'{prefix}{value}{suffix}',
                self.is_singular,
                self.result)
        elif field.startswith('offensive'):
            # Add this field to the global offensive list
            self.offensive[field] = (
                [f'{prefix}{value}{suffix}']
                if field not in self.offensive
                else self.offensive[field] + [f'{prefix}{value}{suffix}'])
            if is_xor:
                self.offensiveXOR = True
        elif field.startswith('retaliation'):
            # Add this field to the global retaliation list
            self.retaliation[field] = (
                [f'{prefix}{value}{suffix}']
                if field not in self.retaliation
                else self.retaliation[field] + [f'{prefix}{value}{suffix}'])
            if is_xor:
                self.retaliationXOR = True

    def parse_modifier(self, field, field_type, dbr):
        """
        Parse a percentage increase in an offensive attribute.

        """
        field_mod = f'{field}Modifier'

        chance = dbr.get(f'{field_mod}Chance', 0)
        mod = dbr.get(field_mod, 0)
        is_xor = dbr.get(f'{field}XOR', False)
        is_global = dbr.get(f'{field}Global', False)

        # Optional pre/suffix for chance and duration damage/effects:
        prefix = ''
        suffix = ''

        if field_type in [self.DOT, self.EOT]:
            # Add the possible duration field:
            duration_mod = dbr.get(f'{field}DurationModifier', 0)

            if duration_mod:
                suffix = texts.get(IMPRV_TIME).format(duration_mod)

        value = texts.get(field_mod).format(mod)
        if chance and not is_xor:
            prefix = texts.get(CHANCE).format(chance)

        if not is_global:
            # Insert the value normally
            TQDBParser.insert_value(
                field_mod,
                f'{prefix}{value}{suffix}',
                self.is_singular,
                self.result)
        elif field.startswith('offensive'):
            # Add this field to the global offensive list
            self.offensive[field_mod] = (
                [f'{prefix}{value}{suffix}']
                if field_mod not in self.offensive
                else self.offensive[field_mod] + [f'{prefix}{value}{suffix}']
            )
        elif field.startswith('retaliation'):
            # Add this field to the global retaliation list
            self.retaliation[field_mod] = (
                [f'{prefix}{value}{suffix}']
                if field_mod not in self.retaliation
                else self.retaliation[field_mod] + [f'{prefix}{value}{suffix}']
            )


class ParametersSkillParser(TQDBParser):
    """
    Parser for `templatebase/parameters_skill.tpl`.

    """
    FIELDS = [
        'skillCooldownReduction',
        'skillManaCostReduction',
        'skillProjectileSpeedModifier',
    ]

    def __init__(self):
        super().__init__()

    def get_priority(self):
        """
        Override this parsers priority to set as highest.

        """
        return TQDBParser.HIGHEST_PRIORITY

    @staticmethod
    def get_template_path():
        return f'{TQDBParser.base}\\templatebase\\parameters_skill.tpl'

    def parse(self, dbr, dbr_file, result):
        """
        Parse skill properties.

        """
        for field in self.FIELDS:
            if field not in dbr:
                continue

            is_singular = len(dbr[field]) == 1

            # Now iterate as many times as is necessary for this field:
            for index, val in enumerate(dbr[field]):
                # Create a new copy of the DBR with the values for this index:
                itr_dbr = TQDBParser.extract_values(dbr, field, index)

                ranged = f'{field}Ranged'
                chance = itr_dbr.get(f'{field}Chance', 0)
                min = itr_dbr.get(f'{field}Min', 0)
                max = itr_dbr.get(f'{field}Max', 0)

                # Prepare an optional prefix:
                prefix = ''

                # Skip any field that has a negligible value
                if val <= 0.01 and not min:
                    continue

                if max > min and texts.has(ranged):
                    value = texts.get(ranged).format(min, max)
                else:
                    value = texts.get(field).format(val)

                if chance:
                    prefix = texts.get(CHANCE).format(chance)

                TQDBParser.insert_value(
                    field, f'{prefix}{value}', is_singular, result)


class PetBonusParser(TQDBParser):
    """
    Parser for `templatebase/petbonusinc.tpl`.

    """
    NAME = 'petBonusName'

    def __init__(self):
        super().__init__()

    @staticmethod
    def get_template_path():
        return f'{TQDBParser.base}\\templatebase\\petbonusinc.tpl'

    def parse(self, dbr, dbr_file, result):
        """
        Parse a possible skill bonus for a pet.

        These bonuses are things like:
            - 15 Vitality Damage
            - +5% Vitality Damage

        """
        if self.NAME in dbr:
            # Parse the pet bonus and add it:
            pet_bonus = DBRParser.parse(dbr[self.NAME])

            properties = (
                # If a tiered property set is found, return the first entry
                pet_bonus['properties'][0]
                if isinstance(pet_bonus['properties'], list)
                # Otherwise just return the list
                else pet_bonus['properties'])

            # Don't allow nested petBonus properties
            # One example of this is the Spear of Nemetona
            if 'petBonus' in properties:
                properties.pop('petBonus')

            # Set the properties of the bonus as the value for this field:
            result['properties']['petBonus'] = properties


class RacialBonusParser(TQDBParser):
    """
    Parser for `templatebase/racialbonus.tpl`.

    """
    FIELDS = [
        'racialBonusAbsoluteDamage',
        'racialBonusAbsoluteDefense',
        'racialBonusPercentDamage',
        'racialBonusPercentDefense',
    ]

    RACE = 'racialBonusRace'

    def __init__(self):
        super().__init__()

    def get_priority(self):
        """
        Override this parsers priority to set as highest.

        """
        return TQDBParser.HIGHEST_PRIORITY

    @staticmethod
    def get_template_path():
        return f'{TQDBParser.base}\\templatebase\\racialbonus.tpl'

    def parse(self, dbr, dbr_file, result):
        """
        Parse the possible racial damage bonuses.TQDBParser

        """
        if self.RACE not in dbr:
            return

        races = []
        for race in dbr[self.RACE]:
            if race == 'Beastman':
                races.append('Beastmen')
            elif race != 'Undead' and race != 'Magical':
                races.append(race + 's')
            else:
                races.append(race)

        for field in self.FIELDS:
            if field not in dbr:
                continue

            # Bonuses can be applied to multiple races, so keep a list:
            result['properties'][field] = []
            values = dbr[field]

            for i in range(0, len(races)):
                # Either append unique value or same if none is available:
                result['properties'][field].append(
                    texts.get(field).format(
                        # Damage number
                        values[0] if len(races) else values[i],
                        # Name of the race
                        races[i]))
