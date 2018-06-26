"""
Core templates that are often included by other templates.

"""
from tqdb.parsers.main import TQDBParser
from tqdb.utils.text import texts

# Some shared core constants:
CHANCE = 'ChanceOfTag'
DOT_SINGLE = 'offensiveSingleFormatTime'
EOT_SINGLE = 'offensiveFixedSingleFormatTime'
IMPRV_TIME = 'ImprovedTimeFormat'
GLOBAL_ALL = 'Chance of: '
GLOBAL_PCT = 'GlobalPercentChanceOfAllTag'
GLOBAL_XOR_ALL = 'Chance for one of the following: '
GLOBAL_XOR_PCT = 'GlobalPercentChanceOfOneTag'


class ParametersCharacter(TQDBParser):
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

    @staticmethod
    def get_template_path():
        return f'{TQDBParser.base}\\templatebase\\parameters_character.tpl'

    def parse(self, dbr, result):
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

            # Now iterate as many times as is necessary for this field:
            for index in range(iterations):
                # Create a new copy of the DBR with the values for this index:
                itr_dbr = dict(
                    (k, v[index])
                    if k.startswith(field) and isinstance(v, list)
                    else (k, v)
                    for k, v in dbr.items())

                if field in dbr:
                    # Parse the flat (+...) version:
                    result['properties'][field] = (
                        texts.get(field).format(itr_dbr[field]))
                if mod in dbr:
                    result['properties'][mod] = (
                        texts.get(mod).format(itr_dbr[mod]))


class ParmatersDefensive(TQDBParser):
    """
    Parser for `templatebase/parameters_defensive.tpl`.

    """
    FIELDS = [
        'defensiveAbsorption',
        'defensiveBleeding',
        'defensiveBleedingDuration',
        'defensiveBlock',
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

    @staticmethod
    def get_template_path():
        return f'{TQDBParser.base}\\templatebase\\parameters_defensive.tpl'

    def parse(self, dbr, result):
        """
        Parse the defensive properties.

        """
        for field in self.FIELDS:
            # Find whether the flat, modifier, or both fields are present:
            mod = f'{field}Modifier'

            iterations = max(
                len(dbr[field]) if field in dbr else 0,
                len(dbr[mod]) if mod in dbr else 0,
                0)

            # Now iterate as many times as is necessary for this field:
            for index in range(iterations):
                # Create a new copy of the DBR with the values for this index:
                itr_dbr = dict(
                    (k, v[index])
                    if k.startswith(field) and isinstance(v, list)
                    else (k, v)
                    for k, v in dbr.items())

                if field in dbr:
                    # Parse the flat (+...) version:
                    chance = itr_dbr.get(f'{field}Chance', 0)
                    value = texts.get(field).format(itr_dbr[field])

                    if chance:
                        # Prefix the
                        value = texts.get(CHANCE).format(chance) + value

                    result['properties'][field] = value
                if mod in dbr:
                    # Add the modifier (%) version of the field:
                    chance = itr_dbr.get(f'{mod}Chance', 0)
                    value = texts.get(field).format(itr_dbr[mod])

                    if chance:
                        # Prefix the
                        value = texts.get(CHANCE).format(chance) + value

                    result['properties'][field] = value


class ParametersOffensive(TQDBParser):
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

    @staticmethod
    def get_template_path():
        # Note: technically this parser is also handling:
        # - parameters_retaliation.tpl and
        # - parameters_weaponsbonusoffensive.tpl
        return f'{TQDBParser.base}\\templatebase\\parameters_offensive.tpl'

    def parse(self, dbr, result):
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

            # Now iterate as many times as is necessary for this field:
            for index in range(iterations):
                # Create a new copy of the DBR with the values for this index:
                itr_dbr = dict(
                    (k, v[index])
                    if k.startswith(field) and isinstance(v, list)
                    else (k, v)
                    for k, v in dbr.items())

                if min in dbr:
                    # Parse the flat (+...) version:
                    self.parse_flat(field, field_type, itr_dbr)
                if mod in dbr:
                    # Parse the modifier (+...%) version
                    self.parse_modifier(field, field_type, itr_dbr)

        # Now add the global chance tags if they're set:
        offensive_key = 'offensiveGlobalChance'
        if offensive_key in dbr and self.offensive:
            for chance in dbr[offensive_key]:
                self.parse_global(
                    offensive_key,
                    # The global chance for the offensive properties
                    chance,
                    # If any global offensive properties are XOR-ed:
                    self.offensiveXOR,
                    # The dictionary of global offensive properties
                    self.offensive)

        retaliation_key = 'retaliationGlobalChance'
        if retaliation_key in dbr and self.retaliation:
            for chance in dbr[offensive_key]:
                self.parse_global(
                    retaliation_key,
                    # The global chance for the offensive properties
                    chance,
                    # If any global offensive properties are XOR-ed:
                    self.retaliationXOR,
                    # The dictionary of global offensive properties
                    self.retaliation)

    def parse_global(self, key, chance, xor, fields):
        """
        Add a global chance for properties.

        This is where multiple properties can be triggered by a chance, like

        10% Chance for one of the following:
            - ...
            - ...
        """
        # Check if the XOR was set for any field:
        if xor:
            self.result['properties'][key] = {
                'chance': (
                    GLOBAL_XOR_ALL if chance == 100
                    else texts.get(GLOBAL_XOR_PCT).format(chance)),
                'properties': fields,
            }
        else:
            self.result['properties'][key] = {
                'chance': (
                    GLOBAL_ALL if chance == 100
                    else texts.get(GLOBAL_PCT).format(chance)),
                'properties': self.offensive,
            }

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
                suffix = texts.get(EOT_SINGLE).format(duration_min)

        # Ranged key is used when retrieving the attribute friendly text
        ranged = f'{field}Ranged'

        if max > min and texts.has(ranged):
            # Add the range of damage
            value = texts.get(ranged).format(min, max)
        else:
            # Add the flat damage
            value = texts.get(field).format(min)

        if chance and not is_xor:
            prefix = texts.get(CHANCE).format(chance)

        if not is_global:
            self.result['properties'][field] = f'{prefix}{value}{suffix}'
        elif field.startswith('offensive'):
            self.offensive[field] = f'{prefix}{value}{suffix}'
            if is_xor:
                self.offensiveXOR = True
        elif field.startswith('retaliation'):
            self.retaliation[field] = f'{prefix}{value}{suffix}'
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

        if mod:
            value = texts.get(field_mod).format(mod)
        if chance and not is_xor:
            prefix = texts.get(CHANCE).format(chance)

        if not is_global:
            self.result['properties'][field_mod] = f'{prefix}{value}{suffix}'
        elif field.startswith('offensive'):
            self.offensive[field_mod] = f'{prefix}{value}{suffix}'
        elif field.startswith('retaliation'):
            self.retaliation[field_mod] = f'{prefix}{value}{suffix}'