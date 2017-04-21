from tqdb.constants import resources
from tqdb.parsers.util import format_path
from tqdb.parsers.util import UtilityParser


class SkillParser():
    """
    Parser for skill files.

    """
    def __init__(self, dbr, props, strings):
        self.dbr = dbr
        self.props = props
        self.strings = strings

    @classmethod
    def keys(cls):
        return [
            'Skill_AttackChain',
            'Skill_AttackProjectile',
            'Skill_AttackProjectileAreaEffect',
            'Skill_AttackProjectileBurst',
            'Skill_AttackProjectileFan',
            'Skill_AttackProjectileRing',
            'Skill_AttackRadius',
            'Skill_AttackRadiusLightning',
            'Skill_AttackSpell',
            'Skill_AttackSpellChaos',
            'Skill_AttackWave',
            'Skill_AttackWeapon',
            'Skill_AttackWeaponBlink',
            'Skill_AttackWeaponCharge',
            'Skill_AttackWeaponRangedSpread',
            'Skill_Buff',
            'Skill_BuffAttackRadiusToggled',
            'Skill_BuffSelfColossus',
            'Skill_BuffSelfDuration',
            'Skill_BuffSelfImmobilize',
            'Skill_BuffSelfToggled',
            'Skill_DispelMagic',
            'Skill_DropProjectileTelekinesis',
            'Skill_GiveBonus',
            'Skill_Mastery',
            'Skill_Modifier',
            'Skill_OnHitAttackRadius',
            'Skill_Passive',
            'Skill_PassiveOnHitBuffSelf',
            'Skill_PassiveOnLifeBuffSelf',
            'Skill_ProjectileModifier',
            'Skill_RefreshCooldown',
            'Skill_WPAttack_BasicAttack',
            'Skill_WeaponPool_BasicAttack',
            'Skill_WeaponPool_ChargedFinale',
            'Skill_WeaponPool_ChargedLinear',
            'SkillBuff_Contageous',
            'SkillBuff_Debuf',
            'SkillBuff_DebufFreeze',
            'SkillBuff_DebufTrap',
            'SkillBuff_Passive',
            'SkillBuff_PassiveShield',
            'SkillSecondary_AttackRadius',
            'SkillSecondary_ChainBonus',
            'SkillSecondary_ChainLightning']

    def parse(self):
        # Grab generic skill data from the first list of properties
        skill = self.props[0]

        result = {}
        if 'skillDisplayName' in skill:
            result['tag'] = skill['skillDisplayName']
            if result['tag'] in self.strings:
                result['name'] = self.strings[result['tag']]

        if ('skillBaseDescription' in skill and
                skill['skillBaseDescription'] in self.strings):
            result['description'] = self.strings[(
                skill['skillBaseDescription'])]
        elif 'FileDescription' in skill:
            result['description'] = skill['FileDescription']

        # Remove the database prefix and format the path:
        path = format_path(self.dbr.replace(resources.DB, ''))
        result['path'] = path

        if len(self.props) > 1:
            result['properties'] = []
            for index, props in enumerate(self.props):
                util = UtilityParser(self.dbr, props, self.strings)
                util.parse_character()
                util.parse_damage()
                util.parse_defense()
                util.parse_pet_bonus(index)
                util.parse_racial()
                util.parse_skill_properties()

                result['properties'].append(util.result)

            # Check if there's an ultimate level set, if so, cap the tiers.
            if 'skillUltimateLevel' in skill:
                ultimate = int(skill['skillUltimateLevel'])
                if len(result['properties']) > ultimate:
                    result['properties'] = result['properties'][:ultimate - 1]
        else:
            util = UtilityParser(self.dbr, skill, self.strings)
            util.parse_character()
            util.parse_damage()
            util.parse_defense()
            util.parse_pet_bonus()
            util.parse_racial()
            util.parse_skill_properties()

            result['properties'] = util.result

        # Now parse the requirements:
        result.update(util.parse_requirements())

        return result


class SkillBuffParser():
    """
    Parser for buffs that reference their skills.

    """
    def __init__(self, dbr, props, strings):
        self.dbr = dbr
        self.strings = strings
        # Buffs are never tiered, grab first item from list:
        self.props = props[0]

    @classmethod
    def keys(cls):
        return [
            'Skill_AttackBuff',
            'Skill_AttackBuffRadius',
            'Skill_AttackProjectileDebuf',
            'Skill_BuffRadius',
            'Skill_BuffRadiusToggled',
            'Skill_BuffOther',
            'SkillSecondary_BuffRadius',
            'SkillSecondary_PetModifier']

    def parse(self):
        from tqdb.parsers.main import parser

        skill_ref = (self.props['buffSkillName']
                     if 'buffSkillName' in self.props
                     else self.props['petSkillName'])

        # Parse the referenced skill:
        util = UtilityParser(self.dbr, self.props, self.strings)
        result = parser.parse(util.get_reference_dbr(skill_ref))

        # Remove the database prefix and format the path:
        result['path'] = format_path(self.dbr.replace(resources.DB, ''))

        return result


class SkillSpawnParser():
    """
    Parser for skills that spawn pets, constructs or other summons.

    """
    def __init__(self, dbr, props, strings):
        self.dbr = dbr
        self.strings = strings
        self.props = props

    @classmethod
    def keys(cls):
        return [
            'Skill_AttackProjectileSpawnPet',
            'Skill_DefensiveGround',
            'Skill_DefensiveWall',
            'Skill_SpawnPet']

    def parse(self):
        from tqdb.parsers.main import parser

        # Grab generic skill data from the first list of properties
        skill = self.props[0]

        result = {}
        result['tag'] = skill['skillDisplayName']
        result['name'] = self.strings.get(result['tag'], result['tag'])
        result['description'] = (self.strings[skill['skillBaseDescription']]
                                 if 'skillBaseDescription' in skill
                                 else '')

        result['path'] = format_path(self.dbr.replace(resources.DB, ''))
        result['summons'] = []

        # Prepare utility parser
        util = UtilityParser(self.dbr, self.props, self.strings)

        # Run both tiered and non-tiered summons:
        tiers = self.props if len(self.props) > 1 else [skill]
        for tier in tiers:
            # Parse the summon reference:
            spawn = parser.parse(util.get_reference_dbr(tier['spawnObjects']))

            # Only set time to live it's it exists (otherwise it's infinite)
            if 'spawnObjectsTimeToLive' in tier:
                spawn['spawnObjectsTimeToLive'] = (
                    self.strings['spawnObjectsTimeToLive'].format(
                        float(tier['spawnObjectsTimeToLive'])))

            if 'petLimit' in tier:
                spawn['petLimit'] = (
                    self.strings['skillPetLimit'].format(
                        int(tier['petLimit'])))

            if 'skillManaCost' in tier:
                spawn['skillManaCost'] = (
                    self.strings['skillManaCost'].format(
                        int(float(tier['skillManaCost']))))

            # Save the skills and the summon:
            result['summons'].append(spawn)

        return result


class SkillTreeParser():
    """
    Parser for skill files.

    """
    def __init__(self, dbr, props, strings):
        from tqdb.parsers.main import parser

        self.dbr = dbr
        self.parser = parser
        self.strings = strings

        # Skill trees are never tiered, grab first item from list:
        self.props = props[0]

    @classmethod
    def keys(cls):
        return ['SkillTree']

    def parse(self):
        result = {}

        util = UtilityParser(self.dbr, self.props, self.strings)
        for prop, dbr in self.props.items():
            if 'skillName' in prop:
                skill = self.parser.parse(util.get_reference_dbr(dbr))

                if not skill:
                    continue

                # Use the path as a key and remove it from the skill
                skill_path = skill['path']
                del(skill['path'])
                result[skill_path] = skill

        return result
