"""
Constants required by the field classes.

"""
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
