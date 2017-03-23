from tqdb.constants import field


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
        for i in range(1, 17):
            name = self.props.get('skillName' + str(i), '')
            level = self.props.get('skillLevel' + str(i), '0')

            # Run a check for difficulty scaling skills, which are tiered:
            level = int(level) if ';' not in level else 0

            # Skip some of the passive skills pets get:
            if name.lower() in field.PET_IGNORE_SKILLS:
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
