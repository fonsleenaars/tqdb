"""
Core templates that are often included by other templates.

"""
from tqdb.parsers.main import TQDBParser
from tqdb.utils.text import texts

# Some shared core constants:
CHANCE = 'ChanceOfTag'


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
    FIELDS = [
        'offensiveBaseCold',
        'offensiveBaseFire',
        'offensiveBaseLife',
        'offensiveBaseLightning',
        'offensiveBasePoison',
        'offensiveBonusPhysical',
        'offensiveCold',
        'offensiveConfusion',
        'offensiveConvert',
        'offensiveDisruption',
        'offensiveElemental',
        'offensiveFear',
        'offensiveFire',
        'offensiveFreeze',
        'offensiveFumble',
        'offensiveManaBurn',
        'offensiveLife',
        'offensiveLifeLeech',
        'offensiveLightning',
        'offensivePercentCurrentLife',
        'offensivePhysical',
        'offensivePierce',
        'offensivePierceRatio',
        'offensivePoison',
        'offensivePetrify',
        'offensiveProjectileFumble',
        'offensiveSleep',
        'offensiveSlowAttackSpeed',
        'offensiveSlowBleeding',
        'offensiveSlowCold',
        'offensiveSlowDefensiveAbility',
        'offensiveSlowDefensiveReduction',
        'offensiveSlowFire',
        'offensiveSlowLife',
        'offensiveSlowLifeLeach',
        'offensiveSlowLightning',
        'offensiveSlowManaLeach',
        'offensiveSlowOffensiveAbility',
        'offensiveSlowOffensiveReduction',
        'offensiveSlowPhysical',
        'offensiveSlowPoison',
        'offensiveSlowRunSpeed',
        'offensiveSlowSpellCastSpeed',
        'offensiveSlowTotalSpeed',
        'offensiveStun',
        'offensiveTotalDamage',
        'offensiveTotalDamageReductionAbsolute',
        'offensiveTotalDamageReductionPercent',
        'offensiveTotalResistanceReductionAbsolute',
        'offensiveTotalResistanceReductionPercent',
        'offensiveTrap',
        'retaliationCold',
        'retaliationElemental',
        'retaliationFire',
        'retaliationLife',
        'retaliationLightning',
        'retaliationPercentCurrentLife',
        'retaliationPhysical',
        'retaliationPierce',
        'retaliationPierceRatio',
        'retaliationPoison',
        'retaliationSlowAttackSpeed',
        'retaliationSlowBleeding',
        'retaliationSlowCold',
        'retaliationSlowDefensiveAbility',
        'retaliationSlowFire',
        'retaliationSlowLife',
        'retaliationSlowLifeLeach',
        'retaliationSlowLightning',
        'retaliationSlowManaLeach',
        'retaliationSlowOffensiveAbility',
        'retaliationSlowOffensiveReduction',
        'retaliationSlowPhysical',
        'retaliationSlowRunSpeed',
        'retaliationSlowPoison',
        'retaliationSlowSpellCastSpeed',
        'retaliationStun',
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
            # Ranged key is used to format a range of damage - ie. 16 ~ 24
            ranged = f'{field}Ranged'

            # Prepare some keys based on the field:
            chance = f'{field}Chance'
            max = f'{field}Max'
            min = f'{field}Min'
            mod = f'{field}Modifier'
            mod_chance = f'{mod}Chance'
            xor = f'{mod}XOR'

            if min in dbr:
                min_values = dbr[min]
                max_values = dbr[max]
                values = []

                # Because we need to track two values (min and max dmg) we need
                # to iterate over all the values and track the index:
                for index, min_value in enumerate(min_values):
                    max_value = max_values[index]

                    if max_value > min_value:
                        # Add the range of damage
                        values.append(texts.get(ranged).format(
                            min_value, max_value))
                    else:
                        # Add the flat daamge
                        values.append(texts.get(field).format(min_value))

                if chance in dbr:
                    # Prefix all the values with the chance text:
                    values = [
                        texts.get(CHANCE).format(chance) + value
                        for value in values]

                result['properties'][field] = (
                    values[0] if len(values) == 1 else values)

            if mod in dbr:
                values = [texts.get(mod).format(value) for value in dbr[mod]]

                if mod_chance in dbr and not dbr[xor]:
                    # Prefix all the values with the chance text:
                    values = [
                        texts.get(CHANCE).format(dbr[mod_chance]) + value
                        for value in values]

                result['properties'][mod] = (
                    values[0] if len(values) == 1 else values)