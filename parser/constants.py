# Global constants (all DBR files have these)
CLASS = 'Class'
TEMPLATE = 'templateName'

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
PREFIX_CHAR = 'character'
PREFIX_DEF = 'defensive'
PREFIX_HUNT = 'Hunting'
PREFIX_JEWEL = 'Jewelry'
PREFIX_MELEE = 'Melee'
PREFIX_OFF = 'offensive'
PREFIX_PROJ = 'projectile'
PREFIX_RACE = 'racial'
PREFIX_RETAL = 'retaliation'
PREFIX_SKILL = 'skill'
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
SUFFIX_DUR = 'Duration'
SUFFIX_GLOBAL = 'Global'
SUFFIX_MAX = 'Max'
SUFFIX_MIN = 'Min'
SUFFIX_MOD = 'Modifier'
SUFFIX_RED = 'Reduction'
SUFFIX_DURMIN = SUFFIX_DUR + SUFFIX_MIN
SUFFIX_DURMAX = SUFFIX_DUR + SUFFIX_MAX
SUFFIX_GCHANCE = SUFFIX_GLOBAL + SUFFIX_CHANCE
SUFFIX_MCHANCE = SUFFIX_MOD + SUFFIX_CHANCE

# Format constants
FORMAT_DUR_FOR = ' for {0:.1f} Second(s)'
FORMAT_DUR_IMP = ' with +{0:.0f}% Improved Duration'
FORMAT_DUR_OVER = ' over {0:.1f} Second(s)'
FORMAT_INT = '{0:.0f}'
FORMAT_INT_SIGNED = '{0:+.0f}'
FORMAT_MOD = '{0:+.0f}%'
FORMAT_RANGE = '{0:.0f} ~ {1:.0f}'
FORMAT_RANGE_DEC = '{0:.1f} ~ {1:.1f}'
FORMAT_REDUCTION = '-{0:.0f}%'

# Item constants
ITEM = 'item'
ITEM_CLASSIFICATION = ITEM + 'Classification'
ITEM_COST = ITEM + 'CostName'
ITEM_LEVEL = ITEM + 'Level'
ITEM_SET = ITEM + 'SetName'
ITEM_TAG = ITEM + 'NameTag'

# Stat constants (Character)
STAT_C_STR = 'Strength'
STAT_C_DEX = 'Dexterity'
STAT_C_INT = 'Intelligence'
STAT_C_HP = 'Life'
STAT_C_HP_REGEN = STAT_HP + 'Regen'
STAT_C_MP = 'Mana'
STAT_C_MP_REGEN = STAT_MP + 'Regen'
STAT_C_MP_RESERVED = STAT_MP + 'LimitReserve'
STAT_C_MP_RES_RED = STAT_MP_RESERVED + SUFFIX_RED
STAT_C_EXP = 'IncreasedExperience'
STAT_C_ATK_SPD = 'AttackSpeed'
STAT_C_RUN_SPD = 'RunSpeed'
STAT_C_CST_SPD = 'SpellCastSpeed'
STAT_C_TOT_SPD = 'TotalSpeed'
STAT_C_OA = 'OffensiveAbility'
STAT_C_DA = 'DefensiveAbility'
STAT_C_SHIELD_REC = 'DefensiveBlockRecovery' + SUFFIX_RED
STAT_C_ENERGY_ABSORB = 'EnergyAbsorptionPercent'
STAT_C_DODGE = 'DodgePercent'
STAT_C_DEFLECT = 'DeflectProjectile'

# Stat constants (defensive)
STAT_D_PROT = 'Protection'
STAT_D_ABS = 'Absorption'
STAT_D_DIS = 'Disruption'
STAT_D_ELE = 'ElementalResistance'
STAT_D_HP = PREFIX_SLOW + PREFIX_HP + 'Leach'
STAT_D_MP = PREFIX_SLOW + PREFIX_MP + 'Leach'
STAT_D_BLOCK = 'Block' + SUFFIX_MOD
STAT_D_REFL = 'Reflect'

# Stat constants (offensive)
STAT_O_RATIO = 'PierceRatio'
STAT_O_BONUS = 'Bonus' + DMG_PHYS
STAT_O_RED = 'PercentCurrentLife'
STAT_O_VAMP = 'LifeLeech'
STAT_O_OFF_RED = 'Offensive' + SUFFIX_RED
STAT_O_DEF_RED = 'Defensive' + SUFFIX_RED
STAT_O_TDR_ABS = DMG_TOTAL + SUFFIX_RED + 'Absolute'
STAT_O_TDR_PCT = DMG_TOTAL + SUFFIX_RED + 'Percent'
STAT_O_TRD_ABS = 'TotalResistance' + SUFFIX_RED + 'Absolute'
STAT_O_TRD_PCT = 'TotalResistance' + SUFFIX_RED + 'Percent'
STAT_O_FUMBLE = 'Fumble'
STAT_O_RFUMBLE = 'Projectile' + STAT_O_FUMBLE
