from tqdb import dbr as DBRParser
from tqdb.parsers.main import TQDBParser
from tqdb.constants.field import PET_IGNORE_SKILLS


class PetBonusParser(TQDBParser):
    """
    Parser for `templatebase/petbonusinc.tpl`.

    """
    NAME = 'petBonusName'

    def __init__(self):
        super().__init__()

    @staticmethod
    def get_template_path():
        return f'{TQDBParser.base}\\templatebase\\petbonusinc.tpl'

    def parse(self, dbr, dbr_file, result):
        """
        Parse a possible skill bonus for a pet.

        These bonuses are things like:
            - 15 Vitality Damage
            - +5% Vitality Damage

        """
        if self.NAME in dbr:
            # Parse the pet bonus and add it:
            pet_bonus = DBRParser.parse(dbr[self.NAME])

            properties = (
                # If a tiered property set is found, return the first entry
                pet_bonus['properties'][0]
                if isinstance(pet_bonus['properties'], list)
                # Otherwise just return the list
                else pet_bonus['properties'])

            # Don't allow nested petBonus properties
            # One example of this is the Spear of Nemetona
            if 'petBonus' in properties:
                properties.pop('petBonus')

            # Set the properties of the bonus as the value for this field:
            result['properties']['petBonus'] = properties


class SummonParser():
    """
    Parser for summons and pets.

    """
    def __init__(self, dbr, props, strings):
        from tqdb.parsers.main import parser

        self.dbr = dbr
        self.parser = parser
        self.strings = strings

        # Summons themselves are never tiered, grab first item from list:
        self.props = props[0]

    @classmethod
    def keys(cls):
        return [
            'DynamicBarrier',
            'Pet',
            'PetNonScaling']

    def parse(self):
        result = {}

        # Set HP/MP values as a list, in case there's difficult scaling:
        spawn_hp = self.props.get('characterLife', '0')
        if spawn_hp != '0':
            # Format the HP value to include text:
            spawn_hp = [int(float(hp)) for hp in spawn_hp.split(';')]
            spawn_hp_val = spawn_hp[0] if len(spawn_hp) == 1 else spawn_hp

            # Set the HP as a property
            result['characterLife'] = (
                self.strings['characterLife'].format(spawn_hp_val))

        # Set the min/max damage:
        dmg_min = int(float(self.props.get('handHitDamageMin', 0)))
        dmg_max = int(float(self.props.get('handHitDamageMax', 0)))
        if dmg_min:
            result['petDamage'] = (
                self.strings['offensivePhysicalRanged'].format(
                    dmg_min, dmg_max)
                if dmg_max and dmg_max > dmg_min
                else self.strings['offensivePhysical'].format(dmg_min))

        result['skills'] = []

        # Parse all the normal skills (17 max):
        for i in range(1, 18):
            name = self.props.get('skillName' + str(i), '')
            level = self.props.get('skillLevel' + str(i), '0')

            # Run a check for difficulty scaling skills, which are tiered:
            level = int(level) if ';' not in level else 0

            # Skip some of the passive skills pets get:
            if name.lower() in PET_IGNORE_SKILLS:
                continue

            if name and level:
                result['skills'].append({
                    'skillName': name,
                    'skillLevel': level
                })

        # Parse initial skill:
        if 'initialSkillName' in self.props:
            result['initialSkill'] = self.props['initialSkillName']

        if 'specialAttackSkillName' in self.props:
            result['specialSkill'] = self.props['specialAttackSkillName']

        return result
