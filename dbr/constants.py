# Global constants (all DBR files have these)
CLASS = 'Class'
PROPERTIES = 'properties'

# Class Types
CLASS_TYPE = 'class'
CLASS_TYPE_EQUIPMENT = [
    'ArmorJewelry_Ring',
    'ArmorJewelry_Jewelry',
    'ArmorProtective_Head',
    'ArmorProtective_Forearm',
    'ArmorProtective_UpperBody',
    'ArmorProtective_LowerBody',
    'WeaponMelee_Axe',
    'WeaponMelee_Mace',
    'WeaponMelee_Sword',
    'WeaponHunting_Bow',
    'WeaponHunting_Spear',
    'WeaponMagical_Staff',
    'WeaponArmor_Shield'
]

CLASS_TYPE_RELIC = [
    'ItemRelic',
    'ItemCharm'
]

CLASS_TYPE_SCROLL = [
    'OneShot_Scroll'
]

CLASS_TYPE_SKILL = 'Skill_'

# Damage constants
DMG_BLEED = 'Bleeding'
DMG_COLD = 'Cold'
DMG_ELEM = 'Elemental'
DMG_FIRE = 'Fire'
DMG_LIGHT = 'Lightning'
DMG_PHYS = 'Physical'
DMG_PIERCE = 'Pierce'
DMG_POISON = 'Poison'
DMG_TOTAL = 'TotalDamage'
DMG_VIT = 'Life'

# Prefixes
PREFIX_ARMOR = 'Armor'
PREFIX_AUGMENT = 'augment'
PREFIX_BASE = 'Base'
PREFIX_BUFF = 'buff'
PREFIX_CHAR = 'character'
PREFIX_DEF = 'defensive'
PREFIX_HUNT = 'Hunting'
PREFIX_JEWEL = 'Jewelry'
PREFIX_MELEE = 'Melee'
PREFIX_OFF = 'offensive'
PREFIX_PET = 'pet'
PREFIX_PROJ = 'projectile'
PREFIX_RACE = 'racial'
PREFIX_RETAL = 'retaliation'
PREFIX_SKILL = 'skill'
PREFIX_SHIELD = 'Shield'
PREFIX_SLOW = 'Slow'
PREFIX_WEAPON = 'Weapon'

# STATUSSES
STATUS_CONF = 'Confusion'
STATUS_CONV = 'Convert'
STATUS_FEAR = 'Fear'
STATUS_FREE = 'Freeze'
STATUS_PETR = 'Petrify'
STATUS_STUN = 'Stun'
STATUS_SLEEP = 'Sleep'
STATUS_TAUNT = 'Taunt'
STATUS_TRAP = 'Trap'

# Suffixes
SUFFIX_CHANCE = 'Chance'
SUFFIX_DRAIN = 'Drain'
SUFFIX_DUR = 'Duration'
SUFFIX_GLOBAL = 'Global'
SUFFIX_MAX = 'Max'
SUFFIX_MIN = 'Min'
SUFFIX_MOD = 'Modifier'
SUFFIX_RATIO = 'Ratio'
SUFFIX_RED = 'Reduction'
SUFFIX_DURMIN = SUFFIX_DUR + SUFFIX_MIN
SUFFIX_DURMAX = SUFFIX_DUR + SUFFIX_MAX
SUFFIX_DURMOD = SUFFIX_DUR + SUFFIX_MOD
SUFFIX_DCHANCE = SUFFIX_DUR + SUFFIX_CHANCE
SUFFIX_GCHANCE = SUFFIX_GLOBAL + SUFFIX_CHANCE
SUFFIX_MCHANCE = SUFFIX_MOD + SUFFIX_CHANCE
SUFFIX_XOR = 'XOR'

# Format constants
FORMAT_DUR_FOR = ' for {0:.1f} Second(s)'
FORMAT_DUR_IMP = ' with +{0:.0f}% Improved Duration'
FORMAT_DUR_OVER = ' over {0:.1f} Second(s)'
FORMAT_FLOAT = '{0:.1f}'
FORMAT_INT = '{0:.0f}'
FORMAT_INT_SIGNED = '{0:+.0f}'
FORMAT_MOD = '{0:+.0f}%'
FORMAT_RANGE = '{0:.0f} ~ {1:.0f}'
FORMAT_RANGE_DEC = '{0:.1f} ~ {1:.1f}'
FORMAT_REDUCTION = '-{0:.0f}%'

# Skill constants
SKILL_AUGMENT_ALL = PREFIX_AUGMENT + 'AllLevel'
SKILL_DISPLAY = PREFIX_SKILL + 'DisplayName'
SKILL_NAME = 'SkillName'
SKILL_LEVEL = 'SkillLevel'
SKILL_MAST_NAME = 'MasteryName'
SKILL_MAST_LEVEL = 'MasteryLevel'
SKILL_DURATION = 'ActiveDuration'
SKILL_CD = 'CooldownTime'
SKILL_CD_RED = SKILL_CD + SUFFIX_RED
SKILL_COST = 'ManaCost'
SKILL_COST_RED = SKILL_COST + SUFFIX_RED
SKILL_PROJ_MOD = 'ProjectileSpeedModifier'
SKILL_RADIUS = 'TargetRadius'
# SKILL_TAG = PREFIX_SKILL + 'Tag'

# TEMPS:
SKILL_TAG = 'tag'
SKILL_DNAME = 'name'

# DBR reference constants
DBR_BUFF_SKILL = PREFIX_BUFF + SKILL_NAME
DBR_PET_BONUS = PREFIX_PET + 'BonusName'
DBR_PET_SKILL = PREFIX_PET + SKILL_NAME

# Item constants
ITEM = 'item'
ITEM_CLASSIFICATION = ITEM + 'Classification'
ITEM_COST = ITEM + 'CostName'
ITEM_LEVEL = ITEM + 'Level'
ITEM_SET = ITEM + 'SetName'
ITEM_TAG = ITEM + 'NameTag'
ITEM_SKILL = ITEM + SKILL_NAME

# Projectile constants
PROJ_NUMBER = PREFIX_PROJ + 'LaunchNumber'
PROJ_PIERCE = PREFIX_PROJ + 'PiercingChance'

# Racial constants
RACE_DMG_ABS = 'BonusAbsoluteDamage'
RACE_DEF_ABS = 'BonusAbsoluteDefense'
RACE_DMG_PCT = 'BonusPercentDamage'
RACE_DEF_PCT = 'BonusPercentDefense'

# Stat constants (global)
STAT_HP = 'Life'
STAT_HP_REGEN = STAT_HP + 'Regen'
STAT_MP = 'Mana'
STAT_MP_REGEN = STAT_MP + 'Regen'
STAT_MP_RES = STAT_MP + 'LimitReserve'
STAT_MP_RES_RED = STAT_MP_RES + SUFFIX_RED
STAT_MP_BURN = PREFIX_OFF + STAT_MP + 'Burn'
STAT_MP_BURN_MIN = STAT_MP_BURN + SUFFIX_DRAIN + SUFFIX_MIN
STAT_MP_BURN_MAX = STAT_MP_BURN + SUFFIX_DRAIN + SUFFIX_MAX
STAT_MP_BURN_RATIO = STAT_MP_BURN + 'Damage' + SUFFIX_RATIO
STAT_ENERGY = 'Energy'
STAT_ENERGY_ABSORB = STAT_ENERGY + 'AbsorptionPercent'
STAT_STR = 'Strength'
STAT_DEX = 'Dexterity'
STAT_INT = 'Intelligence'
STAT_ATK_SPD = 'AttackSpeed'
STAT_RUN_SPD = 'RunSpeed'
STAT_CST_SPD = 'SpellCastSpeed'
STAT_TOT_SPD = 'TotalSpeed'
STAT_OA = 'OffensiveAbility'
STAT_DA = 'DefensiveAbility'
STAT_RACE = PREFIX_RACE + 'BonusRace'

# Stat constants (Character)
STAT_EXP = 'IncreasedExperience'
STAT_SHIELD_REC = 'DefensiveBlockRecovery' + SUFFIX_RED
STAT_DODGE = 'DodgePercent'
STAT_DEFLECT = 'DeflectProjectile'

# Stat constants (defensive)
STAT_PROT = 'Protection'
STAT_ABS = 'Absorption'
STAT_DIS = 'Disruption'
STAT_ELE = 'ElementalResistance'
STAT_HP_LEECH = PREFIX_SLOW + STAT_HP + 'Leach'
STAT_MP_LEECH = PREFIX_SLOW + STAT_ENERGY + 'Leach'
STAT_BLOCK = 'Block'
STAT_REFL = 'Reflect'

# Stat constants (offensive)
STAT_RATIO = DMG_PIERCE + SUFFIX_RATIO
STAT_BONUS = 'Bonus' + DMG_PHYS
STAT_RED = 'PercentCurrentLife'
STAT_VAMP = 'LifeLeech'
STAT_OFF_RED = 'Offensive' + SUFFIX_RED
STAT_DEF_RED = 'Defensive' + SUFFIX_RED
STAT_TDR_ABS = DMG_TOTAL + SUFFIX_RED + 'Absolute'
STAT_TDR_PCT = DMG_TOTAL + SUFFIX_RED + 'Percent'
STAT_TRR_ABS = 'TotalResistance' + SUFFIX_RED + 'Absolute'
STAT_TRR_PCT = 'TotalResistance' + SUFFIX_RED + 'Percent'
STAT_FUMBLE = 'Fumble'
STAT_RFUMBLE = 'Projectile' + STAT_FUMBLE

# DBR Key list (dictionaries)
TXT_ABS = 'text_absolute'
TXT_DUR = 'text_duration'
TXT_MOD = 'text_modifier'
TXT_FABS = 'format_absolute'
TXT_FMOD = 'format_modifier'
TXT_FRANGE = 'format_range'

CHARACTER_FIELDS = {
    STAT_STR: {
        TXT_ABS: ' Strength'},
    STAT_DEX: {
        TXT_ABS: ' Dexterity'},
    STAT_INT: {
        TXT_ABS: ' Intelligence'},
    STAT_HP: {
        TXT_ABS: ' Health'},
    STAT_MP: {
        TXT_ABS: ' Energy'},
    STAT_EXP: {
        TXT_ABS: '% Increased Experience'},
    STAT_ATK_SPD: {
        TXT_ABS: ' Attack Speed'},
    STAT_RUN_SPD: {
        TXT_ABS: ' Movement Speed'},
    STAT_CST_SPD: {
        TXT_ABS: ' Casting Speed'},
    STAT_TOT_SPD: {
        TXT_ABS: ' Total Speed'},
    STAT_HP_REGEN: {
        TXT_ABS: ' Health Regeneration per second',
        TXT_MOD: ' Health Regeneration',
        TXT_FABS: '{0:+.1f}'},
    STAT_MP_REGEN: {
        TXT_ABS: ' Energy Regeneration per second',
        TXT_MOD: ' Energy Regeneration',
        TXT_FABS: '{0:+.1f}'},
    STAT_OA: {
        TXT_ABS: ' Offensive Ability'},
    STAT_DA: {
        TXT_ABS: ' Defensive Ability'},
    STAT_SHIELD_REC: {
        TXT_ABS: '% Shield Recovery Time'},
    STAT_ENERGY_ABSORB: {
        TXT_ABS: ' Absorption of Spell Energy',
        TXT_FABS: FORMAT_MOD},
    STAT_DODGE: {
        TXT_ABS: ' Chance to Dodge Attacks',
        TXT_FABS: FORMAT_MOD},
    STAT_DEFLECT: {
        TXT_ABS: ' Chance to Avoid Projectiles',
        TXT_FABS: FORMAT_MOD},
    STAT_MP_RES: {
        TXT_ABS: ' Energy Reserved'},
    STAT_MP_RES_RED: {
        TXT_ABS: ' less Energy Reserver'}
}

REQUIREMENT_FIELDS = {
    SUFFIX_GLOBAL + 'Req': ' Reduction to all Requirements',
    PREFIX_WEAPON + STAT_STR: ' Strength Requirement for all Weapons',
    PREFIX_WEAPON + STAT_DEX: ' Dexterity Requirement for all Weapons',
    PREFIX_WEAPON + STAT_INT: ' Intelligence Requirement for all Weapons',
    PREFIX_MELEE + STAT_STR: ' Strength Requirement for Melee Weapons',
    PREFIX_MELEE + STAT_DEX: ' Dexterity Requirement for Melee Weapons',
    PREFIX_MELEE + STAT_INT: ' Intelligence Requirement for Melee Weapons',
    PREFIX_HUNT + STAT_STR: ' Strength Requirement for Hunting Weapons',
    PREFIX_HUNT + STAT_DEX: ' Dexterity Requirement for Hunting Weapons',
    PREFIX_HUNT + STAT_INT: ' Intelligence Requirement for Hunting Weapons',
    PREFIX_SHIELD + STAT_STR: ' Strength Requirement for Shields',
    PREFIX_SHIELD + STAT_DEX: ' Dexterity Requirement for Shields',
    PREFIX_SHIELD + STAT_INT: ' Intelligence Requirement for Shields',
    PREFIX_ARMOR + STAT_STR: ' Strength Requirement for Armor',
    PREFIX_ARMOR + STAT_DEX: ' Dexterity Requirement for Armor',
    PREFIX_ARMOR + STAT_INT: ' Intelligence Requirement for Armor',
    PREFIX_JEWEL + STAT_STR: ' Strength Requirement for Jewelry',
    PREFIX_JEWEL + STAT_DEX: ' Dexterity Requirement for Jewelry',
    PREFIX_JEWEL + STAT_INT: ' Intelligence Requirement for Jewelry',
    'Level': ' Player Level Requirement for Items'
}

DEFENSIVE_FIELDS = {
    STAT_PROT: {
        TXT_ABS: ' Armor',
        TXT_MOD: '% Armor Protection',
        TXT_FMOD: FORMAT_INT_SIGNED},
    STAT_ABS: {
        TXT_ABS: '% Armor Absorption'},
    DMG_PHYS: {
        TXT_ABS: '% Physical Resistance',
        TXT_DUR: '% Reduction in Physical Duration'},
    DMG_PIERCE: {
        TXT_ABS: '% Pierce Resistance'},
    DMG_FIRE: {
        TXT_ABS: '% Fire Resistance',
        TXT_DUR: '% Reduction in Burn Duration'},
    DMG_COLD: {
        TXT_ABS: '% Cold Resistance',
        TXT_DUR: '% Reduction in Frostburn Duration'},
    DMG_LIGHT: {
        TXT_ABS: '% Lightning Resistance',
        TXT_DUR: '% Reduction in Electrical Burn Duration'},
    DMG_POISON: {
        TXT_ABS: '% Poison Duration',
        TXT_DUR: '% Reduction in Poison Duration'},
    DMG_VIT: {
        TXT_ABS: '% Vitality Damage Resistance',
        TXT_DUR: '% Reduction in Vitality Decay Duration'},
    STAT_DIS: {
        TXT_ABS: '% Skill Disruption Resistance'},
    STAT_ELE: {
        TXT_ABS: '% Elemental Resistance'},
    PREFIX_SLOW + STAT_HP_LEECH: {
        TXT_ABS: '% Life Leech Resistance',
        TXT_DUR: '% Reduction in Life Leech Duration'},
    PREFIX_SLOW + STAT_MP_LEECH: {
        TXT_ABS: '% Energy Leech Resistance',
        TXT_DUR: '% Reduction in Energy Leech Duration'},
    DMG_BLEED: {
        TXT_ABS: '% Bleeding Resistance',
        TXT_DUR: '% Reduction in Bleeding Duration'},
    STAT_BLOCK: {
        TXT_ABS: ' Damage',
        TXT_MOD: '% Shield Block',
        TXT_FABS: 'Block ' + FORMAT_INT,
        TXT_FMOD: FORMAT_INT_SIGNED},
    STAT_REFL: {
        TXT_ABS: '% Damage Reflected'},
    STATUS_CONF: {
        TXT_ABS: '% Reduced Confusion Duration (Pet/Trap Only)'},
    STATUS_TAUNT: {
        TXT_ABS: '% Protection from Taunting (Pet/Trap Only)'},
    STATUS_FEAR: {
        TXT_ABS: '% Reduced Fear Duration (Pet/Trap Only)'},
    STATUS_CONV: {
        TXT_ABS: '% Protection Mind Control Duration (Pet/Trap Only)'},
    STATUS_TRAP: {
        TXT_ABS: '% Reduced Entrapment Duration'},
    STATUS_PETR: {
        TXT_ABS: '% Reduced Petrify Duration'},
    STATUS_FREE: {
        TXT_ABS: '% Reduced Freeze Duration'},
    STATUS_STUN: {
        TXT_ABS: '% Stun Resistance'},
    STATUS_SLEEP: {
        TXT_ABS: '% Sleep Resistance'}
}

OFFENSIVE_FIELDS = {
    PREFIX_BASE + DMG_COLD: {
        TXT_ABS: ' Base Cold Damage'},
    PREFIX_BASE + DMG_FIRE: {
        TXT_ABS: ' Base Fire Damage'},
    PREFIX_BASE + DMG_LIGHT: {
        TXT_ABS: ' Base Lightning Damage'},
    PREFIX_BASE + DMG_POISON: {
        TXT_ABS: ' Base Poison Damage'},
    PREFIX_BASE + DMG_VIT: {
        TXT_ABS: ' Base Vitality Damage'},
    STAT_RATIO: {
        TXT_ABS: '% Piercing',
        TXT_MOD: ' Piercing'},
    STAT_BONUS: {
        TXT_ABS: ' Bonus Damage'},
    DMG_PHYS: {
        TXT_ABS: ' Damage',
        TXT_MOD: ' Physical Damage'},
    DMG_PIERCE: {
        TXT_ABS: ' Pierce Damage'},
    DMG_COLD: {
        TXT_ABS: ' Cold Damage'},
    DMG_FIRE: {
        TXT_ABS: ' Fire Damage'},
    DMG_LIGHT: {
        TXT_ABS: ' Lightning Damage'},
    DMG_POISON: {
        TXT_ABS: ' Poison Damage'},
    DMG_VIT: {
        TXT_ABS: ' Vitality Damage'},
    STAT_RED: {
        TXT_ABS: "% Reduction to Enemy's Health"},
    STAT_DIS: {
        TXT_ABS: ' second(s) of Skill Disruption',
        TXT_FABS: FORMAT_FLOAT,
        TXT_FRANGE: FORMAT_RANGE_DEC},
    STAT_VAMP: {
        TXT_ABS: '% of Attack damage converted to Health'},
    DMG_ELEM: {
        TXT_ABS: ' Elemental Damage'},
    DMG_TOTAL: {
        TXT_ABS: ' Total Damage'}
}

OFFENSIVE_MB_FIELD = {
    TXT_ABS: '% Energy Drained',
    TXT_MOD: ' ({0:.0f}% Energy Drained Causes Damage)'
}

OFFENSIVE_DUR_DMG_FIELDS = {
    PREFIX_SLOW + DMG_PHYS: ' Crush Damage',
    PREFIX_SLOW + DMG_BLEED: ' Bleeding Damage',
    PREFIX_SLOW + DMG_COLD: ' Frostburn Damage',
    PREFIX_SLOW + DMG_FIRE: ' Burn Damage',
    PREFIX_SLOW + DMG_LIGHT: ' Electrical Burn Damage',
    PREFIX_SLOW + DMG_POISON: ' Poison Damage',
    PREFIX_SLOW + DMG_VIT: ' Vitality Decay',
    PREFIX_SLOW + STAT_HP_LEECH: ' Life Leech',
    PREFIX_SLOW + STAT_MP_LEECH: ' Energy Leech'
}

OFFENSIVE_DUR_EFF_FIELDS = {
    PREFIX_SLOW + STAT_TOT_SPD: {
        TXT_ABS: '% Slowed'},
    PREFIX_SLOW + STAT_ATK_SPD: {
        TXT_ABS: '% Slower Attack'},
    PREFIX_SLOW + STAT_CST_SPD: {
        TXT_ABS: '% Slow Casting'},
    PREFIX_SLOW + STAT_RUN_SPD: {
        TXT_ABS: '% Slower Movement',
        TXT_MOD: ' Slow Movement'},
    PREFIX_SLOW + STAT_OA: {
        TXT_ABS: '% Reduced Offensive Ability'},
    PREFIX_SLOW + STAT_DA: {
        TXT_ABS: '% Reduced Defensive Ability'},
    PREFIX_SLOW + STAT_OFF_RED: {
        TXT_ABS: '% Reduced Physical Damage'},
    PREFIX_SLOW + STAT_DEF_RED: {
        TXT_ABS: ' Reduced Armor'},
    STAT_TDR_PCT: {
        TXT_ABS: '% Reduced Damage'},
    STAT_TDR_ABS: {
        TXT_ABS: ' Reduced Damage'},
    STAT_TRR_PCT: {
        TXT_ABS: '% Reduced Resistance'},
    STAT_TRR_ABS: {
        TXT_ABS: ' Reduced Resistance'},
    STAT_FUMBLE: {
        TXT_ABS: '% Chance to Fumble attacks'},
    STAT_RFUMBLE: {
        TXT_ABS: '% Chance of Impaired Aim'},
    STATUS_CONF: {
        TXT_ABS: ' second(s) of Confusion'},
    STATUS_FEAR: {
        TXT_ABS: ' second(s) of Fear'},
    STATUS_CONV: {
        TXT_ABS: ' second(s) of Mind Control'},
    STATUS_TRAP: {
        TXT_ABS: ' second(s) of Immobilization'},
    STATUS_PETR: {
        TXT_ABS: ' second(s) of Petrify'},
    STATUS_FREE: {
        TXT_ABS: ' second(s) of Freeze'},
    STATUS_STUN: {
        TXT_ABS: ' second(s) of Stun',
        TXT_MOD: ' Stun Duration'},
    STATUS_SLEEP: {
        TXT_ABS: ' second(s) of Sleep'}
}

PROJECTILE_FIELDS = {
    PROJ_NUMBER: ' Projectiles',
    PROJ_PIERCE: '% Chance to Pass Through Enemies'
}

RACIAL_FIELDS = {
    RACE_DMG_ABS: '+{0:.0f} Damage to {1}',
    RACE_DEF_ABS: '{0:.0f} Less Damage from {1}',
    RACE_DEF_PCT: '{0:.0f}% Less Damage from {1}',
    RACE_DMG_PCT: '+{0:.0f}% Damage to {1}'
}

RETALIATION_FIELDS = {
    DMG_PHYS: {
        TXT_ABS: ' Damage Retaliation',
        TXT_MOD: ' Physical Damage Retaliation'},
    DMG_PIERCE: {
        TXT_ABS: ' Piercing Retaliation',
        TXT_MOD: ' Pierce Damage Retaliation'},
    DMG_COLD: {
        TXT_ABS: ' Cold Retaliation',
        TXT_MOD: ' Frostburn Retaliation'},
    DMG_FIRE: {
        TXT_ABS: ' Fire Retaliation',
        TXT_MOD: ' Burn Retaliation'},
    DMG_LIGHT: {
        TXT_ABS: ' Lightning Retaliation',
        TXT_MOD: ' Lightning Retaliation'},
    DMG_POISON: {
        TXT_ABS: ' Poison Retaliation',
        TXT_MOD: ' Poison Retaliation'},
    DMG_VIT: {
        TXT_ABS: ' Vitality Damage Retaliation',
        TXT_MOD: ' Vitality Damage Retaliation'},
    STATUS_STUN: {
        TXT_ABS: ' second(s) of Stun',
        TXT_FABS: FORMAT_FLOAT,
        TXT_MOD: ' Stun Retaliation'},
    STAT_RED: {
        TXT_ABS: '% Health Reduction Retaliation'},
    DMG_ELEM: {
        TXT_ABS: ' Elemental Retaliation'}
}

RETALIATION_DUR_DMG_FIELDS = {
    PREFIX_SLOW + DMG_PHYS: ' Wound Retaliation',
    PREFIX_SLOW + DMG_BLEED: ' Bleeding Damage Retaliation',
    PREFIX_SLOW + DMG_COLD: ' Frostburn Retaliation',
    PREFIX_SLOW + DMG_FIRE: ' Burn Retaliation',
    PREFIX_SLOW + DMG_LIGHT: ' Electrical Burn Retaliation',
    PREFIX_SLOW + DMG_POISON: ' Poison Retaliation',
    PREFIX_SLOW + DMG_VIT: ' Vitality Decay Retaliation',
    PREFIX_SLOW + STAT_HP_LEECH: ' Life Leech Retaliation',
    PREFIX_SLOW + STAT_MP_LEECH: ' Energy Leech Retaliation',
}

RETALIATION_DUR_EFF_FIELDS = {
    PREFIX_SLOW + STAT_ATK_SPD: '% Slower Attack Retaliation',
    PREFIX_SLOW + STAT_CST_SPD: '% Slow Casting Retaliation',
    PREFIX_SLOW + STAT_RUN_SPD: '% Slower Movement Retaliation',
    PREFIX_SLOW + STAT_OA: '% Reduced Offensive Ability Retaliation',
    PREFIX_SLOW + STAT_DA: '% Reduced Defensive Ability Retaliation',
    PREFIX_SLOW + STAT_OFF_RED: ' Damage Reduction Retaliation'
}

SKILL_AUGMENT_FIELDS = {
    PREFIX_AUGMENT + SKILL_NAME + '1':
        PREFIX_AUGMENT + SKILL_LEVEL + '1',
    PREFIX_AUGMENT + SKILL_NAME + '2':
        PREFIX_AUGMENT + SKILL_LEVEL + '2',
    PREFIX_AUGMENT + SKILL_MAST_NAME + '1':
        PREFIX_AUGMENT + SKILL_MAST_LEVEL + '1',
    PREFIX_AUGMENT + SKILL_MAST_NAME + '2':
        PREFIX_AUGMENT + SKILL_MAST_LEVEL + '2'
}

SKILL_GRANTS_FIELD = 'Grants skill: '
SKILL_AUGMENT_FORMAT = '+{0} to {1}'
SKILL_AUGMENT_ALL_FORMAT = '+{0} to All Skills'

SKILL_PROPERTY_FIELDS = {
    SKILL_DURATION: FORMAT_INT + ' Second Duration',
    SKILL_CD: FORMAT_INT + ' Second(s) Recharge',
    SKILL_CD_RED: FORMAT_REDUCTION + ' Recharge',
    SKILL_COST: FORMAT_INT + ' Energy Cost',
    SKILL_COST_RED: FORMAT_REDUCTION + ' Energy Cost',
    SKILL_PROJ_MOD: FORMAT_MOD + ' Increase in Projectile Speed',
    SKILL_RADIUS: FORMAT_INT + ' Meter Radius'
}
