from tqdb import dbr as DBRParser
from tqdb.parsers.main import TQDBParser
from tqdb.parsers.base import ParametersOffensiveParser


class MonsterSkillManager(TQDBParser):
    """
    Parser for `templatebase\\monsterskillmanager.tpl`.

    """
    # Skills to ignore when parsing pet buffs/skills:
    IGNORE_SKILLS = [
        f'data\\database\\records{skill}' for skill in [
            'skills\\monster skills\\passive_totaldamageabsorption01.dbr',
            '\\skills\\monster skills\\defense\\armor_passive.dbr',
            '\\skills\\monster skills\\defense\\banner_debuff.dbr',
            '\\skills\\monster skills\\defense\\trap_resists.dbr',
            '\\skills\\monster skills\\defense\\resist_undead.dbr',
            '\\skills\\monster skills\\defense_undeadresists.dbr',
            '\\skills\\boss skills\\boss_conversionimmunity.dbr',
        ]]

    PROJECTILES = 'projectileLaunchNumber'

    def __init__(self):
        super().__init__()

    @staticmethod
    def get_template_path():
        return f'{TQDBParser.base}\\templatebase\\monsterskillmanager.tpl'

    def hash_properties(self, properties):
        """
        Return a string of properties.

        """
        return '&'.join([
            f'{key}={properties[key]}'
            for key in sorted(properties.keys())
            # projectileLaunchNumber is ignored in this hash because it is the
            # one key that's messing up Scroll of the Breaking Wheel, which has
            # three identical skills except for its launch projectiles.
            if key != self.PROJECTILES
        ])

    def parse(self, dbr, dbr_file, result):
        """
        Parse all the abilities a monster has.

        """
        result['abilities'] = []

        # Parse all the normal skills (17 max):
        for i in range(1, 18):
            nameTag = f'skillName{i}'
            levelTag = f'skillLevel{i}'

            # Skip unset skills or skills that are to be ignored:
            if (nameTag not in dbr or levelTag not in dbr or
                    str(dbr[nameTag]).lower() in self.IGNORE_SKILLS):
                continue

            skill = DBRParser.parse(dbr[nameTag])

            if not skill['properties']:
                continue

            # Check if this skill already exists, based on an exact match
            # of its properties:
            if any(self.hash_properties(skill['properties'][0]) ==
                    self.hash_properties(ability['properties'][0])
                    for ability in result['abilities']):
                continue

            # Initialize the ability with its properties and level
            ability = {
                'level': dbr[levelTag][0],
                'properties': skill['properties'],
            }

            # Only set the name if it's available
            if 'name' in skill:
                ability['name'] = skill['name']

            result['abilities'].append(ability)

        # Now run through the parsed abilities one more time and set the level:
        for ability in result['abilities']:
            level = ability.pop('level')

            try:
                ability['properties'] = ability['properties'][level - 1]
            except IndexError:
                ability['properties'] = ability['properties'][-1]

        return result


class CharacterParser(TQDBParser):
    """
    Parser for `character.tpl`.

    """
    MAX = 'handHitDamageMax'
    MIN = 'handHitDamageMin'

    def __init__(self):
        super().__init__()

    @staticmethod
    def get_template_path():
        return f'{TQDBParser.base}\\character.tpl'

    def parse(self, dbr, dbr_file, result):
        """
        Parse a character's properties.

        """
        if self.MIN not in dbr:
            return

        dmg_min = dbr[self.MIN]
        dmg_max = dbr[self.MAX]

        # Set the damage this summon does as a property:
        result['properties']['offensivePhysical'] = (
            ParametersOffensiveParser.format(
                ParametersOffensiveParser.ABSOLUTE,
                'offensivePhysical',
                dmg_min,
                dmg_max))
