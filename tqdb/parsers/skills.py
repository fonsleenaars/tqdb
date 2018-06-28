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
    # 'lifeMonitorPercent',   # 1 file: skill_passiveonlifebuffself.tpl
    # 'projectilePiercing',   # 1 file: skill_modifier.tpl
    # 'refreshTime',          # 1 file: skill_refreshcooldown.tpl
    # 'skillChanceWeight',    # 1 file: templatebase\skill_wpattack.tpl

    def __init__(self):
        super().__init__()

    @staticmethod
    def get_template_path():
        return f'{TQDBParser.base}\\templatebase\\skill_base.tpl'

    def parse(self, dbr, dbr_file, result):
        """
        Parse the base properties of a skill.

        These properties include the skillDisplayName, its friendly display
        name (the property returns a tag), and the maximum level of a skill.

        """
        if self.NAME in dbr:
            # The tag is the skillDisplayName property
            result['tag'] = dbr[self.NAME]

            # Now try to find a friendly name for the tag:
            result['name'] = texts.tag(result['tag'])

            if result['name'] == result['tag']:
                # If the tag wasn't returned, a friendly name weas found:
                logging.warning(f'No skill name found for {result["tag"]}')
        else:
            logging.debug('No skillDisplayName found')

        if self.DESC in dbr and texts.has_tag(dbr[self.DESC]):
            # Also load the description, if it's known:
            result['description'] = texts.tag(dbr[self.DESC])
        elif self.FILE in dbr:
            # Use the FileDescription instead:
            result['description'] = dbr['FileDescription']

        # Check the shared fields for values:
        max_level = dbr.get('skillUltimateLevel', dbr.get('skillMaxLevel'))
        is_singular = max_level == 1

        for index in range(max_level):
            # Create a new copy of the DBR with the values for this index:
            itr_dbr = self._prepare_values(dbr, index)

            for field in self.FIELDS:
                if field not in itr_dbr:
                    continue

                # Insert this skill property
                TQDBParser.insert_value(
                    field, itr_dbr[field], is_singular, result)

    def _prepare_values(self, dbr, index):
        """
        Internal functions to iterate over all the shared fields.

        Create a dictionary by going through all the shared fields and grabbing
        the value at the index given.

        """
        itr_dbr = {}
        for field in self.FIELDS:
            itr_dbr.update(TQDBParser.extract_values(dbr, field, index))

        return itr_dbr


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


class SkillPetModifier(TQDBParser):
    """
    Parser for `templatebase/skillsecondary_petmodifier.tpl`.

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


# class SkillTreeParser():
#     """
#     Parser for skill files.

#     """
#     def __init__(self, dbr, props, strings):
#         from tqdb.parsers.main import parser

#         self.dbr = dbr
#         self.parser = parser
#         self.strings = strings

#         # Skill trees are never tiered, grab first item from list:
#         self.props = props[0]

#     @classmethod
#     def keys(cls):
#         return ['SkillTree']

#     def parse(self):
#         result = {}

#         util = UtilityParser(self.dbr, self.props, self.strings)
#         for prop, dbr in self.props.items():
#             if 'skillName' in prop:
#                 skill = self.parser.parse(util.get_reference_dbr(dbr))

#                 if not skill:
#                     continue

#                 # Use the path as a key and remove it from the skill
#                 skill_path = skill['path']
#                 del(skill['path'])
#                 result[skill_path] = skill

#         return result
