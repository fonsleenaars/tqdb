import logging

from tqdb import dbr as DBRParser
from tqdb.parsers.main import TQDBParser
from tqdb.utils.text import texts


class SkillBaseParser(TQDBParser):
    """
    Parser for `templatebase/skill_base.tpl`.

    """
    FILE = 'FileDescription'
    DESC = 'skillBaseDescription'
    NAME = 'skillDisplayName'

    # These fields aren't a part of the skill_base.tpl template, but rather
    # are used by multiple skill templates. Instead of implementing a lot of
    # template parsers that each do almost the same thing, the one thing they
    # have in common is that they all include skill_base.tpl.
    FIELDS = [
        'skillActiveDuration',
        'skillActiveLifeCost',
        'skillActiveManaCost',
        'skillCooldownTime',
        'skillLifeBonus',
        'skillManaCost',
        'skillProjectileNumber',
        'skillTargetAngle',
        'skillTargetNumber',
        'skillTargetRadius',
    ]

    # Damage absorption fields:
    ABSORPTIONS = [
        'damageAbsorption',
        'damageAbsorptionPercent',
    ]

    # Damage absorption qualifier types:
    QUALIFIERS = {
        'bleedingDamageQualifier': 'tagQualifyingDamageBleeding',
        'coldDamageQualifier': 'tagQualifyingDamageCold',
        'elementalDamageQualifier': 'tagQualifyingDamageElemental',
        'fireDamageQualifier': 'tagQualifyingDamageFire',
        'lifeDamageQualifier': 'tagQualifyingDamageLife',
        'lightningDamageQualifier': 'tagQualifyingDamageLightning',
        'pierceDamageQualifier': 'tagQualifyingDamagePierce',
        'physicalDamageQualifier': 'tagQualifyingDamagePhysical',
        'poisonDamageQualifier': 'tagQualifyingDamagePoison',
    }

    def __init__(self):
        super().__init__()

    def get_priority(self):
        """
        Assign the lowest priority to this parser so that all parsers have run
        before the properties are indexed by skill level in this parser.

        """
        return TQDBParser.LOWEST_PRIORITY

    @staticmethod
    def get_template_path():
        return f'{TQDBParser.base}\\templatebase\\skill_base.tpl'

    def parse(self, dbr, dbr_file, result):
        """
        Parse the base properties of a skill.

        These properties include the skillDisplayName, its friendly display
        name (the property returns a tag), and the maximum level of a skill.

        """
        # Store the path to this skill, it is used in tqdb.storage to ensure
        # all tags are unique.
        result['path'] = dbr_file

        if self.NAME in dbr:
            # The tag is the skillDisplayName property
            result['tag'] = dbr[self.NAME]

            # Now try to find a friendly name for the tag:
            result['name'] = texts.get(result['tag'])

            if result['name'] == result['tag']:
                # If the tag wasn't returned, a friendly name weas found:
                logging.warning(f'No skill name found for {result["tag"]}')
        else:
            logging.warning(f'No skillDisplayName found in {dbr_file}')

        if self.DESC in dbr and texts.has(dbr[self.DESC]):
            # Also load the description, if it's known:
            result['description'] = texts.get(dbr[self.DESC])
        elif self.FILE in dbr:
            # Use the FileDescription instead:
            result['description'] = dbr['FileDescription']

        # Check the shared fields for values:
        max_level = dbr.get('skillUltimateLevel', dbr.get('skillMaxLevel'))
        is_singular = max_level == 1

        for field in self.FIELDS:
            for index in range(max_level):
                itr_dbr = TQDBParser.extract_values(dbr, field, index)

                if field not in itr_dbr:
                    continue

                # Insert this skill property
                value = texts.get(field).format(itr_dbr[field])
                TQDBParser.insert_value(
                    field, value, is_singular, result)

        # Check the damage absorption skill properties:
        for field in self.ABSORPTIONS:
            for index in range(max_level):
                itr_dbr = TQDBParser.extract_values(dbr, field, index)

                if field not in itr_dbr:
                    continue

                # Add 'skill' prefix and capitalize first letter:
                field_prefixed = 'skill' + field[:1].upper() + field[1:]
                value = itr_dbr[field]

                # Find qualifier damage type(s):
                damage_types = ', '.join([
                    texts.get(text_key)
                    for dmg_type, text_key in self.QUALIFIERS.items()
                    if dmg_type in dbr])

                if damage_types:
                    TQDBParser.insert_value(
                        field_prefixed,
                        f'{texts.get(field_prefixed).format(value)} '
                        f'({damage_types})',
                        is_singular,
                        result)
                else:
                    # If there is no qualifier, it's all damage:
                    TQDBParser.insert_value(
                        field_prefixed,
                        texts.get(field_prefixed).format(value),
                        is_singular,
                        result)

        # After all skill properties have been set, index them by level:
        properties = [{} for i in range(max_level)]

        # Insert the existing properties by adding them to the correct tier:
        for field, values in result['properties'].items():
            for index in range(max_level):
                # Each value is either a list or a flat value to repeat:
                if isinstance(values, list):
                    # Skip properties that extend beyond the max_level
                    if index >= len(values):
                        continue
                    properties[index][field] = values[index]
                else:
                    properties[index][field] = values

        # Now set the reindexed properties:
        result['properties'] = properties


class SkillBuffParser(TQDBParser):
    """
    Parser for all templates that just reference a buff.

    """
    BUFF = 'buffSkillName'

    def __init__(self):
        super().__init__()

    @staticmethod
    def get_template_path():
        return [
            f'{TQDBParser.base}\\skill_attackbuffradius.tpl',
            f'{TQDBParser.base}\\skill_attackbuff.tpl',
            f'{TQDBParser.base}\\skill_attackprojectiledebuf.tpl',
            f'{TQDBParser.base}\\skill_buffradius.tpl',
            f'{TQDBParser.base}\\skill_buffradiustoggled.tpl',
            f'{TQDBParser.base}\\skill_buffother.tpl',
            f'{TQDBParser.base}\\skillsecondary_buffradius.tpl',
        ]

    def parse(self, dbr, dbr_file, result):
        """
        Parse the referenced buff skill, and pass that back as this result.

        """
        if self.BUFF in dbr:
            # Now set our result as the result of the buff being parsed:
            result.update(DBRParser.parse(dbr[self.BUFF]))


class SkillModifierParser(TQDBParser):
    """
    Parser for `skill_modifier.tpl`.

    """
    FIELD = 'projectilePiercing'

    def __init__(self):
        super().__init__()

    @staticmethod
    def get_template_path():
        return f'{TQDBParser.base}\\skill_modifier.tpl'

    def parse(self, dbr, dbr_file, result):
        """
        Parse the "% Chance to pass through enemies" property.

        """
        if self.FIELD in dbr:
            result['properties'][self.FIELD] = [
                texts.get(self.FIELD).format(value)
                for value in dbr[self.FIELD]]


class SkillPetModifier(TQDBParser):
    """
    Parser for `skillsecondary_petmodifier.tpl`.

    """
    PET_SKILL = 'petSkillName'

    def __init__(self):
        super().__init__()

    @staticmethod
    def get_template_path():
        return f'{TQDBParser.base}\\skillsecondary_petmodifier.tpl'

    def parse(self, dbr, dbr_file, result):
        """
        Parse the referenced pet skill, and pass that back as this result.

        """
        if self.PET_SKILL in dbr:
            # Now set our result as the result of the pet skill being parsed:
            result.update(DBRParser.parse(dbr[self.PET_SKILL]))


class SkillPassiveOnLifeBuffSelfParser(TQDBParser):
    """
    Parser for `skill_passiveonlifebuffself.tpl`.

    """
    FIELD = 'lifeMonitorPercent'

    def __init__(self):
        super().__init__()

    @staticmethod
    def get_template_path():
        return f'{TQDBParser.base}\\skill_passiveonlifebuffself.tpl'

    def parse(self, dbr, dbr_file, result):
        """
        Parse the "activated when health drops below ...%" property.

        """
        if self.FIELD in dbr:
            result['properties'][self.FIELD] = [
                texts.get(self.FIELD).format(value)
                for value in dbr[self.FIELD]]


class SkillProjectileBaseParser(TQDBParser):
    """
    Parser for `templatebase/skill_projectilebase.tpl`

    """
    FIELDS = [
        'projectileExplosionRadius',
        'projectileFragmentsLaunchNumber',
        'projectileLaunchNumber',
        'projectilePiercingChance',
    ]

    def __init__(self):
        super().__init__()

    @staticmethod
    def get_template_path():
        return f'{TQDBParser.base}\\templatebase\\skill_projectilebase.tpl'

    def parse(self, dbr, dbr_file, result):
        """
        Parse the projectile properties.

        """


class SkillRefreshCooldownParser(TQDBParser):
    """
    Parser for `skill_refreshcooldown.tpl`.

    Note: the only skill that implements this seems to be Renewal from Nature.

    """
    FIELD = 'refreshTime'

    def __init__(self):
        super().__init__()

    @staticmethod
    def get_template_path():
        return f'{TQDBParser.base}\\skill_refreshcooldown.tpl'

    def parse(self, dbr, dbr_file, result):
        """
        Parse the refresh cooldown property.

        """
        if self.FIELD in dbr:
            result['properties'][self.FIELD] = [
                texts.get(self.FIELD).format(value)
                for value in dbr[self.FIELD]]


class SkillWeaponAttackParser(TQDBParser):
    """
    Parser for `templatebase\skill_wpattack.tpl.tpl`.

    """
    FIELD = 'skillChanceWeight'

    def __init__(self):
        super().__init__()

    @staticmethod
    def get_template_path():
        return f'{TQDBParser.base}\\templatebase\\skill_wpattack.tpl'

    def parse(self, dbr, dbr_file, result):
        """
        Parse the "Chance to be used" property.

        """
        if self.FIELD in dbr:
            result['properties'][self.FIELD] = [
                texts.get(self.FIELD).format(value)
                for value in dbr[self.FIELD]]


# class SkillSpawnParser():
#     """
#     Parser for skills that spawn pets, constructs or other summons.

#     """
#     def __init__(self, dbr, props, strings):
#         self.dbr = dbr
#         self.strings = strings
#         self.props = props

#     @classmethod
#     def keys(cls):
#         return [
#             'Skill_AttackProjectileSpawnPet',
#             'Skill_DefensiveGround',
#             'Skill_DefensiveWall',
#             'Skill_SpawnPet']

#     def parse(self):
#         from tqdb.parsers.main import parser

#         # Grab generic skill data from the first list of properties
#         skill = self.props[0]

#         result = {}
#         result['tag'] = skill['skillDisplayName']
#         result['name'] = self.strings.get(result['tag'], result['tag'])
#         result['description'] = (self.strings[skill['skillBaseDescription']]
#                                  if 'skillBaseDescription' in skill
#                                  else '')

#         result['path'] = format_path(self.dbr.replace(resources.DB, ''))
#         result['summons'] = []

#         # Prepare utility parser
#         util = UtilityParser(self.dbr, self.props, self.strings)

#         # Run both tiered and non-tiered summons:
#         tiers = self.props if len(self.props) > 1 else [skill]
#         for tier in tiers:
#             # Parse the summon reference:
#             spawn = parser.parse(util.get_reference_dbr(tier['spawnObjects']))

#             # Only set time to live it's it exists (otherwise it's infinite)
#             if 'spawnObjectsTimeToLive' in tier:
#                 spawn['spawnObjectsTimeToLive'] = (
#                     self.strings['spawnObjectsTimeToLive'].format(
#                         float(tier['spawnObjectsTimeToLive'])))

#             if 'petLimit' in tier:
#                 spawn['petLimit'] = (
#                     self.strings['skillPetLimit'].format(
#                         int(tier['petLimit'])))

#             if 'skillManaCost' in tier:
#                 spawn['skillManaCost'] = (
#                     self.strings['skillManaCost'].format(
#                         int(float(tier['skillManaCost']))))

#             # Save the skills and the summon:
#             result['summons'].append(spawn)

#         return result
