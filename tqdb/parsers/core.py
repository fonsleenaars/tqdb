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

    @staticmethod
    def get_template_path():
        return f'{TQDBParser.base}\\templatebase\\parameters_character.tpl'

    @classmethod
    def parse(cls, dbr, result):
        """
        Parse the character properties.

        """
        for field in cls.FIELDS:
            if field in dbr:
                # Add the absolute version of the field:
                values = [
                    texts.get(field).format(value)
                    for value in dbr[field]]

                result['properties'][field] = (
                    values[0] if len(values) == 1 else values)

            field_mod = f'{field}Modifier'
            if field_mod in dbr:
                # Add the modifier (%) version of the field:
                values = [
                    texts.get(field_mod).format(value)
                    for value in dbr[field_mod]]

                result['properties'][field_mod] = (
                    values[0] if len(values) == 1 else values)


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

    @staticmethod
    def get_template_path():
        return f'{TQDBParser.base}\\templatebase\\parameters_offensive.tpl'

    @classmethod
    def parse(cls, dbr, result):
        """
        Parse the character properties.

        """
        for field, parsing_type in cls.FIELDS.items():
            if parsing_type == cls.ABSOLUTE:
                cls.parse_absolute(field, dbr, result)
            elif parsing_type == cls.DOT:
                cls.parse_absolute(field, dbr, result)
            elif parsing_type == cls.EOT:
                cls.parse_eot(field, dbr, result)
            elif parsing_type == cls.MANA:
                cls.parse_mana(field, dbr, result)

    @classmethod
    def parse_absolute(cls, field, dbr, result):
        """
        Parse the regular, absolute variant of a damage type.

        """
        # Ranged key is used to format a range of damage - ie. 16 ~ 24
        ranged = f'{field}Ranged'

        # Prepare some keys based on the field:
        chance = f'{field}Chance'
        max = f'{field}Max'
        min = f'{field}Min'
        mod = f'{field}Modifier'
        mod_chance = f'{mod}Chance'
        xor = f'{field}XOR'

        if min in dbr:
            min_values = dbr[min]
            max_values = dbr[max] if max in dbr else min_values
            values = []

            # Because we need to track two values (min and max dmg) we need
            # to iterate over all the values and track the index:
            for index, min_value in enumerate(min_values):
                max_value = max_values[index]

                if max_value > min_value and texts.has(ranged):
                    # Add the range of damage
                    value = texts.get(ranged).format(min_value, max_value)
                else:
                    # Add the flat damage
                    value = texts.get(field).format(min_value)

                if chance in dbr:
                    # Prefix the value with the chance text:
                    chance_value = dbr[chance][index]
                    value = texts.get(CHANCE).format(chance_value) + value

                values.append(value)

            result['properties'][field] = (
                values[0] if len(values) == 1 else values)

        if mod in dbr:
            values = []

            for index, mod_value in enumerate(dbr[mod]):
                # Set the modifier (+%) value
                value = texts.get(mod).format(mod_value)

                if mod_chance in dbr and xor not in dbr:
                    # Prefix  the value with the chance text:
                    chance_value = dbr[mod_chance][index]
                    value = texts.get(CHANCE).format(chance_value) + value

                values.append(value)

            result['properties'][mod] = (
                values[0] if len(values) == 1 else values)

    @classmethod
    def parse_dot(cls, field, dbr, result):
        """
        Parse the damage over time variant of a damage type.

        """
        # Ranged key is used to format a range of damage - ie. 16 ~ 24
        ranged = f'{field}Ranged'

        # Prepare some keys based on the field:
        chance = f'{field}Chance'
        dur_max = f'{field}DurationMax'
        dur_min = f'{field}DurationMin'
        dur_mod = f'{field}DurationModifier'
        max = f'{field}Max'
        min = f'{field}Min'
        mod = f'{field}Modifier'
        mod_chance = f'{mod}Chance'
        xor = f'{field}XOR'

        if min in dbr:
            min_values = dbr[min]
            max_values = dbr[max] if max in dbr else min_values
            values = []

            # Because we need to track two values (min and max dmg) we need
            # to iterate over all the values and track the index:
            for index, min_value in enumerate(min_values):
                max_value = max_values[index]

                # Recalculate min/max damage if a duration is set:
                if dur_min in dbr:
                    min_value *= dbr[dur_min][index]

                    if dur_max in dbr and max not in dbr:
                        max_value *= dbr[dur_max][index]
                    elif max in dbr:
                        max_value *= dbr[dur_min][index]

                if max_value > min_value:
                    # Add the range of damage
                    value = texts.get(ranged).format(min_value, max_value)
                else:
                    # Add the flat damage
                    value = texts.get(field).format(min_value)

                # Check again if duration is set, this time to add a suffix:
                if dur_min in dbr:
                    value += texts.get(DOT_SINGLE).format(dbr[dur_min][index])

                if chance in dbr:
                    # Prefix the value with the chance text:
                    chance_value = dbr[chance][index]
                    value = texts.get(CHANCE).format(chance_value) + value

                values.append(value)

            result['properties'][field] = (
                values[0] if len(values) == 1 else values)

        if mod in dbr or dur_mod in dbr:
            values = []

            for index, mod_value in enumerate(dbr[mod]):
                # Set the modifier (+%) value
                value = texts.get(mod).format(mod_value)

                if dur_mod in dbr:
                    value += texts.get(IMPRV_TIME).format(dbr[dur_mod][index])

                if mod_chance in dbr and xor not in dbr:
                    # Prefix  the value with the chance text:
                    chance_value = dbr[mod_chance][index]
                    value = texts.get(CHANCE).format(chance_value) + value

                values.append(value)

            result['properties'][mod] = (
                values[0] if len(values) == 1 else values)

    @classmethod
    def parse_eot(cls, field, dbr, result):
        """
        Parse the effect over time variant of a damage type.

        Note: this method is almost identical to parse_dot, with the exception
        of a different suffix, and the min and max values are not multiplied by
        the durations.

        """
        # Ranged key is used to format a range of damage - ie. 16 ~ 24
        ranged = f'{field}Ranged'

        # Prepare some keys based on the field:
        chance = f'{field}Chance'
        dur_min = f'{field}DurationMin'
        dur_mod = f'{field}DurationModifier'
        max = f'{field}Max'
        min = f'{field}Min'
        mod = f'{field}Modifier'
        mod_chance = f'{mod}Chance'
        xor = f'{field}XOR'

        if min in dbr:
            min_values = dbr[min]
            max_values = dbr[max] if max in dbr else min_values
            values = []

            # Because we need to track two values (min and max dmg) we need
            # to iterate over all the values and track the index:
            for index, min_value in enumerate(min_values):
                max_value = max_values[index]

                if max_value > min_value:
                    # Add the range of damage
                    value = texts.get(ranged).format(min_value, max_value)
                else:
                    # Add the flat damage
                    value = texts.get(field).format(min_value)

                # Check again if duration is set, this time to add a suffix:
                if dur_min in dbr:
                    value += texts.get(EOT_SINGLE).format(dbr[dur_min][index])

                if chance in dbr:
                    # Prefix the value with the chance text:
                    chance_value = dbr[chance][index]
                    value = texts.get(CHANCE).format(chance_value) + value

                values.append(value)

            result['properties'][field] = (
                values[0] if len(values) == 1 else values)

        if mod in dbr or dur_mod in dbr:
            values = []

            for index, mod_value in enumerate(dbr[mod]):
                # Set the modifier (+%) value
                value = texts.get(mod).format(mod_value)

                if dur_mod in dbr:
                    value += texts.get(IMPRV_TIME).format(dbr[dur_mod][index])

                if mod_chance in dbr and xor not in dbr:
                    # Prefix  the value with the chance text:
                    chance_value = dbr[mod_chance][index]
                    value = texts.get(CHANCE).format(chance_value) + value

                values.append(value)

            result['properties'][mod] = (
                values[0] if len(values) == 1 else values)

    @classmethod
    def parse_mana(cls, field, dbr, result):
        """
        Parse the unique mana damage type.

        """
        # Prepare some keys based on the field:
        chance = f'{field}Chance'
        max = f'{field}DrainMax'
        min = f'{field}DrainMin'
        ratio = f'{field}DamageRatio'
        is_global = f'{field}Global'

        if min in dbr:
            min_values = dbr[min]
            max_values = dbr[max] if max in dbr else min_values
            values = []

            # Because we need to track two values (min and max dmg) we need
            # to iterate over all the values and track the index:
            for index, min_value in enumerate(min_values):
                max_value = max_values[index]

                if max_value > min_value:
                    # Add the range of damage
                    value = (texts.get('offensiveManaDrainRanged')
                             .format(min_value, max_value))
                else:
                    # Add the flat damamge
                    value = texts.get('offensiveManaDrain').format(min_value)

                if ratio in dbr:
                    value += (texts.get('offensiveManaBurnRatio')
                              .format(dbr[ratio][index]))

                if chance in dbr and is_global not in dbr:
                    # Prefix the value with the chance text:
                    chance_value = dbr[chance][index]
                    value = texts.get(CHANCE).format(chance_value) + value

                values.append(value)

            result['properties'][field] = (
                values[0] if len(values) == 1 else values)
