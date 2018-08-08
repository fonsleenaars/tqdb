"""
All summons and pet parsers.

"""
from tqdb import dbr as DBRParser
from tqdb import storage
from tqdb.parsers.main import TQDBParser
from tqdb.parsers.base import ParametersOffensiveParser


class MonsterSkillManager(TQDBParser):
    """
    Parser for `templatebase\\monsterskillmanager.tpl`.

    """
    # Skills to ignore when parsing pet buffs/skills:
    IGNORE_SKILLS = list(
        f'data\\database\\records{skill}' for skill in [
            'skills\\monster skills\\passive_totaldamageabsorption01.dbr',
            '\\skills\\monster skills\\defense\\armor_passive.dbr',
            '\\skills\\monster skills\\defense\\banner_debuff.dbr',
            '\\skills\\monster skills\\defense\\trap_resists.dbr',
            '\\skills\\monster skills\\defense\\resist_undead.dbr',
            '\\skills\\monster skills\\defense_undeadresists.dbr',
            '\\skills\\boss skills\\boss_conversionimmunity.dbr',
        ]) + [
            # Breaking wheel has its skill three times for some reason:
            'data\\database\\records\\xpack\\skills\\scroll skills\\pets\\'
            'all_breakingwheel_bladeattack2.dbr',
            'data\\database\\records\\xpack\\skills\\scroll skills\\pets\\'
            'all_breakingwheel_bladeattack3.dbr',
        ]

    PROJECTILES = 'projectileLaunchNumber'

    def __init__(self):
        super().__init__()

    @staticmethod
    def get_template_path():
        return [
            f'{TQDBParser.base}\\templatebase\\monsterskillmanager.tpl',
            # For some reason the doppel summon template does not extend the
            # regular monsterskillmanager, but has its own:
            f'{TQDBParser.base}\\templatebase\\doppelskillmanager.tpl',
        ]

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

            # Store the skill, which will ensure a unique tag:
            skill_tag = storage.store_skill(skill)
            level = dbr[levelTag][0]

            # Append the stored skill to the ability list (level > 0)
            if level:
                result['abilities'].append({
                    'tag': skill_tag,
                    'level': level,
                })


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
        dmg_max = dbr.get(self.MAX, dmg_min)

        # Set the damage this character does as a property:
        result['properties']['offensivePhysical'] = (
            ParametersOffensiveParser.format(
                ParametersOffensiveParser.ABSOLUTE,
                'offensivePhysical',
                dmg_min,
                dmg_max))
