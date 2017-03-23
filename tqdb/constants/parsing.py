"""
All constants required for parsing.

"""
from tqdb.parsers import equipment
from tqdb.parsers import crafts
from tqdb.parsers import skills
from tqdb.parsers import summons

# Dictionary to map keys to specialized parsers:
PARSERS = {
    equipment.ArmorWeaponParser: equipment.ArmorWeaponParser.keys(),
    equipment.JewelryParser: equipment.JewelryParser.keys(),
    crafts.ArtifactParser: crafts.ArtifactParser.keys(),
    crafts.CharmRelicParser: crafts.CharmRelicParser.keys(),
    crafts.FormulaParser: crafts.FormulaParser.keys(),
    crafts.ScrollParser: crafts.ScrollParser.keys(),
    skills.SkillBuffParser: skills.SkillBuffParser.keys(),
    skills.SkillParser: skills.SkillParser.keys(),
    skills.SkillSpawnParser: skills.SkillSpawnParser.keys(),
    skills.SkillTreeParser: skills.SkillTreeParser.keys(),
    summons.SummonParser: summons.SummonParser.keys(),
}

# Difficulty constants:
DIFFICULTIES = {
    'n': 'Normal',
    'e': 'Epic',
    'l': 'Legendary',
}
DIFF_LIST = [
    DIFFICULTIES['n'],
    DIFFICULTIES['e'],
    DIFFICULTIES['l'],
]

# PropertyTable constants:
PT_ADD_CUSTOM = [
    ['damageAbsorption', '{%.0f0} ({%s1}) Damage Absorption'],
    ['damageAbsorptionPercent', '{%.0f0} ({%s1}) Damage Absorption'],
    ['retaliationStun', ' second(s) of Stun retaliation'],
    ['projectileExplosionRadius', '{%.0f0} Meter Radius'],
    ['projectileFragmentsLaunchNumber', '{%.0f0} Fragments'],
    ['projectileFragmentsLaunchNumberRanged',
        '{%.0f0} - {%.0f0} Fragments'],
    ['projectileLaunchNumber', '{%.0f0} Projectile(s)'],
    ['skillActiveDuration', '{%.0f0} Second Duration'],
    ['skillChanceWeight', '{%.0f0}% Chance to be Used'],
    ['skillCooldownTime', '{%.1f0} Second(s) Recharge'],
    ['skillManaCost', '{%.0f0} Energy Cost'],
    ['skillProjectileNumber', '{%.0f0} Projectile(s)'],
    ['skillTargetNumber', '{%.0f0} Target Maximum'],
    ['skillTargetRadius', '{%.0f0} Meter Radius'],
]

PT_ADD_CUSTOM_FROM_PROPS = [
    ['ChanceOfTag', 'ChanceOfTag'],
    ['characterGlobalReqReduction', 'CharcterItemGlobalReduction'],
    ['defensiveTotalSpeed', 'TotalSpeedResistance'],
    ['GlobalPercentChanceOfAllTag', 'GlobalPercentChanceOfAllTag'],
    ['GlobalPercentChanceOfOneTag', 'GlobalPercentChanceOfOneTag'],
    ['ImprovedTimeFormat', 'ImprovedTimeFormat'],
    ['ItemAllSkillIncrement', 'ItemAllSkillIncrement'],
    ['lifeMonitorPercent', 'LifeMonitorPercent'],
    ['offensiveBaseLife', 'tagDamageBaseVitality'],
    ['offensiveSlowDefensiveReductionModifier',
     'DamageDurationDefensiveReduction'],
    ['projectilePiercing', 'ProjectilePiercingChance'],
    ['projectilePiercingChance', 'ProjectilePiercingChance'],
    ['refreshTime', 'SkillRefreshTime'],
    ['skillActiveLifeCost', 'ActiveLifeCost'],
    ['skillActiveManaCost', 'ActiveManaCost'],
]

PT_ADD_CUSTOM_FROM_TABLE = [
    ['characterDeflectProjectile', 'characterDeflectProjectiles'],
    ['defensiveAbsorption', 'defensiveAbsorptionModifier'],
    ['defensiveProtection', 'defensiveAbsorptionProtection'],
    ['defensiveSlowLifeLeach', 'defensiveLifeLeach'],
    ['defensiveSlowLifeLeachDuration', 'defensiveLifeLeachDuration'],
    ['defensiveSlowManaLeach', 'defensiveManaLeach'],
    ['defensiveSlowManaLeachDuration', 'defensiveManaLeachDuration'],
    ['offensiveFumble', 'offensiveSlowFumble'],
    ['offensiveProjectileFumble', 'offensiveSlowProjectileFumble'],
    ['offensivePierceRatio', 'offensiveBasePierceRatio'],
    ['spawnObjectsTimeToLive', 'skillPetTimeToLive'],
]

PT_REPLACEMENTS = [{
    # Character prefix
    'type': 'replace',
    'find': 'Character',
    'replace': 'character',
}, {
    'type': 'regex',
    'find': r'DamageModifier(.*)',
    'replace': r'offensive\1Modifier',
}, {
    'type': 'regex',
    'find': r'DamageDurationModifier(.*)',
    'replace': r'offensiveSlow\1Modifier',
},  {
    # DamageDuration prefix
    'type': 'replace',
    'find': 'DamageDuration',
    'replace': 'offensiveSlow',
}, {
    # Damage prefix
    'type': 'replace',
    'find': 'Damage',
    'replace': 'offensive',
}, {
    # Defense prefix
    'type': 'replace',
    'find': 'Defense',
    'replace': 'defensive',
}, {
    # Racial prefix
    'type': 'replace',
    'find': 'Racial',
    'replace': 'racial',
}, {
    'type': 'regex',
    'find': r'RetaliationModifier(.*)',
    'replace': r'retaliation\1Modifier',
}, {
    'type': 'regex',
    'find': r'RetaliationDurationModifier(.*)',
    'replace': r'retaliationSlow\1Modifier',
},  {
    # RetaliationDuration prefix
    'type': 'replace',
    'find': 'RetaliationDuration',
    'replace': 'retaliationSlow',
}, {
    # Retaliation prefix
    'type': 'replace',
    'find': 'Retaliation',
    'replace': 'retaliation',
}, {
    # Skill prefix
    'type': 'replace',
    'find': 'Skill',
    'replace': 'skill',
}]

PT_VALUE_OLD = (
    r'{(?P<pre_signed>\-?\+?)%'
    r'(?P<post_signed>\+?)'
    r'(?P<decimals>\.?[0-9]?)'
    r'(?P<type>[a-z])(?P<arg>[0-9])}'
)
PT_VALUE_NEW = '{{{arg}:{pre_signed}{post_signed}{decimals}{type}}}'
