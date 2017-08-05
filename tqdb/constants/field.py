"""
Constants required by the field classes.

"""
from tqdb.parsers import fields

# Character properties
CHARACTER = {
    'characterArmorStrengthReqReduction': fields.CharacterBase,
    'characterArmorDexterityReqReduction': fields.CharacterBase,
    'characterArmorIntelligenceReqReduction': fields.CharacterBase,
    'characterAttackSpeedModifier': fields.CharacterBase,
    'characterDefensiveAbility': fields.CharacterBase,
    'characterDefensiveBlockRecoveryReduction': fields.CharacterBase,
    'characterDeflectProjectile': fields.CharacterBase,
    'characterDexterity': fields.CharacterBase,
    'characterDodgePercent': fields.CharacterBase,
    'characterEnergyAbsorptionPercent': fields.CharacterBase,
    'characterGlobalReqReduction': fields.CharacterBase,
    'characterHuntingStrengthReqReduction': fields.CharacterBase,
    'characterHuntingDexterityReqReduction': fields.CharacterBase,
    'characterHuntingIntelligenceReqReduction': fields.CharacterBase,
    'characterIncreasedExperience': fields.CharacterBase,
    'characterIntelligence': fields.CharacterBase,
    'characterJewelryStrengthReqReduction': fields.CharacterBase,
    'characterJewelryDexterityReqReduction': fields.CharacterBase,
    'characterJewelryIntelligenceReqReduction': fields.CharacterBase,
    'characterLevelReqReduction': fields.CharacterBase,
    'characterLife': fields.CharacterBase,
    'characterLifeRegen': fields.CharacterBase,
    'characterOffensiveAbility': fields.CharacterBase,
    'characterMana': fields.CharacterBase,
    'characterManaLimitReserve': fields.CharacterBase,
    'characterManaLimitReserveReduction': fields.CharacterBase,
    'characterManaRegen': fields.CharacterBase,
    'characterMeleeStrengthReqReduction': fields.CharacterBase,
    'characterMeleeDexterityReqReduction': fields.CharacterBase,
    'characterMeleeIntelligenceReqReduction': fields.CharacterBase,
    'characterRunSpeed': fields.CharacterBase,
    'characterShieldStrengthReqReduction': fields.CharacterBase,
    'characterShieldDexterityReqReduction': fields.CharacterBase,
    'characterShieldIntelligenceReqReduction': fields.CharacterBase,
    'characterSpellCastSpeed': fields.CharacterBase,
    'characterStaffStrengthReqReduction': fields.CharacterBase,
    'characterStaffDexterityReqReduction': fields.CharacterBase,
    'characterStaffIntelligenceReqReduction': fields.CharacterBase,
    'characterStrength': fields.CharacterBase,
    'characterTotalSpeed': fields.CharacterBase,
    'characterWeaponStrengthReqReduction': fields.CharacterBase,
    'characterWeaponDexterityReqReduction': fields.CharacterBase,
    'characterWeaponIntelligenceReqReduction': fields.CharacterBase,
}

# Offensive and retaliation properties:
DAMAGE = {
    'offensiveBaseCold': fields.OffensiveAbsolute,
    'offensiveBaseFire': fields.OffensiveAbsolute,
    'offensiveBaseLife': fields.OffensiveAbsolute,
    'offensiveBaseLightning': fields.OffensiveAbsolute,
    'offensiveBasePoison': fields.OffensiveAbsolute,
    'offensiveBonusPhysical': fields.OffensiveAbsolute,
    'offensiveCold': fields.OffensiveAbsolute,
    'offensiveConfusion': fields.OffensiveEOT,
    'offensiveConvert': fields.OffensiveEOT,
    'offensiveDisruption': fields.OffensiveEOT,
    'offensiveElemental': fields.OffensiveAbsolute,
    'offensiveFear': fields.OffensiveEOT,
    'offensiveFire': fields.OffensiveAbsolute,
    'offensiveFreeze': fields.OffensiveEOT,
    'offensiveFumble': fields.OffensiveEOT,
    'offensiveManaBurn': fields.OffensiveMana,
    'offensiveLife': fields.OffensiveAbsolute,
    'offensiveLifeLeech': fields.OffensiveAbsolute,
    'offensiveLightning': fields.OffensiveAbsolute,
    'offensivePercentCurrentLife': fields.OffensiveAbsolute,
    'offensivePhysical': fields.OffensiveAbsolute,
    'offensivePierce': fields.OffensiveAbsolute,
    'offensivePierceRatio': fields.OffensiveAbsolute,
    'offensivePoison': fields.OffensiveAbsolute,
    'offensivePetrify': fields.OffensiveEOT,
    'offensiveProjectileFumble': fields.OffensiveEOT,
    'offensiveSleep': fields.OffensiveEOT,
    'offensiveSlowAttackSpeed': fields.OffensiveEOT,
    'offensiveSlowBleeding': fields.OffensiveDOT,
    'offensiveSlowCold': fields.OffensiveDOT,
    'offensiveSlowDefensiveAbility': fields.OffensiveEOT,
    'offensiveSlowDefensiveReduction': fields.OffensiveEOT,
    'offensiveSlowFire': fields.OffensiveDOT,
    'offensiveSlowLife': fields.OffensiveDOT,
    'offensiveSlowLifeLeach': fields.OffensiveDOT,
    'offensiveSlowLightning': fields.OffensiveDOT,
    'offensiveSlowManaLeach': fields.OffensiveDOT,
    'offensiveSlowOffensiveAbility': fields.OffensiveEOT,
    'offensiveSlowOffensiveReduction': fields.OffensiveEOT,
    'offensiveSlowPhysical': fields.OffensiveDOT,
    'offensiveSlowPoison': fields.OffensiveDOT,
    'offensiveSlowRunSpeed': fields.OffensiveEOT,
    'offensiveSlowSpellCastSpeed': fields.OffensiveEOT,
    'offensiveSlowTotalSpeed': fields.OffensiveEOT,
    'offensiveStun': fields.OffensiveEOT,
    'offensiveTotalDamage': fields.OffensiveAbsolute,
    'offensiveTotalDamageReductionAbsolute': fields.OffensiveEOT,
    'offensiveTotalDamageReductionPercent': fields.OffensiveEOT,
    'offensiveTotalResistanceReductionAbsolute': fields.OffensiveEOT,
    'offensiveTotalResistanceReductionPercent': fields.OffensiveEOT,
    'offensiveTrap': fields.OffensiveEOT,
    'retaliationCold': fields.OffensiveAbsolute,
    'retaliationElemental': fields.OffensiveAbsolute,
    'retaliationFire': fields.OffensiveAbsolute,
    'retaliationLife': fields.OffensiveAbsolute,
    'retaliationLightning': fields.OffensiveAbsolute,
    'retaliationPercentCurrentLife': fields.OffensiveAbsolute,
    'retaliationPhysical': fields.OffensiveAbsolute,
    'retaliationPierce': fields.OffensiveAbsolute,
    'retaliationPierceRatio': fields.OffensiveAbsolute,
    'retaliationPoison': fields.OffensiveAbsolute,
    'retaliationSlowAttackSpeed': fields.OffensiveEOT,
    'retaliationSlowBleeding': fields.OffensiveDOT,
    'retaliationSlowCold': fields.OffensiveDOT,
    'retaliationSlowDefensiveAbility': fields.OffensiveEOT,
    'retaliationSlowFire': fields.OffensiveDOT,
    'retaliationSlowLife': fields.OffensiveDOT,
    'retaliationSlowLifeLeach': fields.OffensiveDOT,
    'retaliationSlowLightning': fields.OffensiveDOT,
    'retaliationSlowManaLeach': fields.OffensiveDOT,
    'retaliationSlowOffensiveAbility': fields.OffensiveEOT,
    'retaliationSlowOffensiveReduction': fields.OffensiveEOT,
    'retaliationSlowPhysical': fields.OffensiveDOT,
    'retaliationSlowRunSpeed': fields.OffensiveEOT,
    'retaliationSlowPoison': fields.OffensiveDOT,
    'retaliationSlowSpellCastSpeed': fields.OffensiveEOT,
    'retaliationStun': fields.OffensiveAbsolute,
}

# Defensive properties
DEFENSE = {
    'defensiveAbsorption': fields.DefensiveBase,
    'defensiveBleeding': fields.DefensiveBase,
    'defensiveBleedingDuration': fields.DefensiveBase,
    'defensiveBlock': fields.DefensiveBase,
    'defensiveConfusion': fields.DefensiveBase,
    'defensiveConvert': fields.DefensiveBase,
    'defensiveCold': fields.DefensiveBase,
    'defensiveColdDuration': fields.DefensiveBase,
    'defensiveDisruption': fields.DefensiveBase,
    'defensiveElementalResistance': fields.DefensiveBase,
    'defensiveFear': fields.DefensiveBase,
    'defensiveFire': fields.DefensiveBase,
    'defensiveFireDuration': fields.DefensiveBase,
    'defensiveFreeze': fields.DefensiveBase,
    'defensiveLife': fields.DefensiveBase,
    'defensiveLifeDuration': fields.DefensiveBase,
    'defensiveLightning': fields.DefensiveBase,
    'defensiveLightningDuration': fields.DefensiveBase,
    'defensiveManaBurnRatio': fields.DefensiveBase,
    'defensivePercentCurrentLife': fields.DefensiveBase,
    'defensivePetrify': fields.DefensiveBase,
    'defensivePhysical': fields.DefensiveBase,
    'defensivePhysicalDuration': fields.DefensiveBase,
    'defensivePierce': fields.DefensiveBase,
    'defensivePierceDuration': fields.DefensiveBase,
    'defensivePoison': fields.DefensiveBase,
    'defensivePoisonDuration': fields.DefensiveBase,
    'defensiveProtection': fields.DefensiveBase,
    'defensiveReflect': fields.DefensiveBase,
    'defensiveSlowLifeLeach': fields.DefensiveBase,
    'defensiveSlowLifeLeachDuration': fields.DefensiveBase,
    'defensiveSlowManaLeach': fields.DefensiveBase,
    'defensiveSlowManaLeachDuration': fields.DefensiveBase,
    'defensiveSleep': fields.DefensiveBase,
    'defensiveStun': fields.DefensiveBase,
    'defensiveTaunt': fields.DefensiveBase,
    'defensiveTotalSpeed': fields.DefensiveBase,
    'defensiveTrap': fields.DefensiveBase,
}

# Global chance properties:
GLOBAL_ALL = 'Chance of: '
GLOBAL_PCT = 'GlobalPercentChanceOfAllTag'
GLOBAL_XOR_ALL = 'Chance for one of the following: '
GLOBAL_XOR_PCT = 'GlobalPercentChanceOfOneTag'

# Item granted skills:
ITEM_SKILL = 'Grants skill: Level {0:d} {1:s}'
ITEM_SKILL_LVL1 = 'Grants skill: {0:s}'

# Equipable loot for monsters:
EQUIPABLE_LOOT = [
    'Head',
    'Torso',
    'LowerBody',
    'Forearm',
    'Finger1',
    'Finger2',
    'RightHand',
    'LeftHand',
    'Misc1',
    'Misc2',
    'Misc3']

# Skills to ignore when parsing pet buffs/skills:
PET_IGNORE_SKILLS = [
    'records\\skills\\monster skills\\passive_totaldamageabsorption01.dbr',
    'records\\skills\\monster skills\\defense\\armor_passive.dbr',
    'records\\skills\\monster skills\\defense\\banner_debuff.dbr',
    'records\\skills\\monster skills\\defense\\trap_resists.dbr',
    'records\\skills\\monster skills\\defense\\resist_undead.dbr',
    'records\\skills\\monster skills\\defense_undeadresists.dbr',
    'records\\skills\\boss skills\\boss_conversionimmunity.dbr']

# Damage qualifier types:
QUALIFIERS = {
    'bleedingDamageQualifier': 'Bleeding',
    'coldDamageQualifier': 'Cold',
    'elementalDamageQualifier': 'Elemental',
    'fireDamageQualifier': 'Fire',
    'lifeDamageQualifier': 'Vitality',
    'lightningDamageQualifier': 'Lightning',
    'pierceDamageQualifier': 'Pierce',
    'physicalDamageQualifier': 'Physical',
    'poisonDamageQualifier': 'Poison',
}

# Racial properties:
RACIAL = [
    'racialBonusAbsoluteDamage',
    'racialBonusAbsoluteDefense',
    'racialBonusPercentDamage',
    'racialBonusPercentDefense',
]

# Requirement prefixes:
REQUIREMENTS = [
    'Dexterity',
    'Intelligence',
    'Level',
    'Strength',
]

# Skill properties
SKILL_PROPERTIES = {
    'lifeMonitorPercent': fields.SkillPropertyBase,
    'projectileExplosionRadius': fields.SkillPropertyBase,
    'projectileFragmentsLaunchNumber': fields.SkillPropertyBase,
    'projectileLaunchNumber': fields.SkillPropertyBase,
    'projectilePiercing': fields.SkillPropertyBase,
    'projectilePiercingChance': fields.SkillPropertyBase,
    'refreshTime': fields.SkillPropertyBase,
    'skillActiveDuration': fields.SkillPropertyBase,
    'skillActiveLifeCost': fields.SkillPropertyBase,
    'skillActiveManaCost': fields.SkillPropertyBase,
    'skillChanceWeight': fields.SkillPropertyBase,
    'skillCooldownTime': fields.SkillPropertyBase,
    'skillCooldownReduction': fields.SkillPropertyBase,
    'skillLifeBonus': fields.SkillPropertyBase,
    'skillManaCost': fields.SkillPropertyBase,
    'skillManaCostReduction': fields.SkillPropertyBase,
    'skillProjectileNumber': fields.SkillPropertyBase,
    'skillProjectileSpeedModifier': fields.SkillPropertyBase,
    'skillTargetNumber': fields.SkillPropertyBase,
    'skillTargetRadius': fields.SkillPropertyBase,
    'TargetAngle': fields.SkillPropertyBase,
}

# Skill augments (+# to Skill or Mastery)
SKILL_AUGMENTS = {
    'augmentSkillName1': 'augmentSkillLevel1',
    'augmentSkillName2': 'augmentSkillLevel2',
    'augmentMasteryName1': 'augmentMasteryLevel1',
    'augmentMasteryName2': 'augmentMasteryLevel2',
}
