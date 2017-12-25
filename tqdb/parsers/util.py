import logging
import math
import re
from tqdb.constants import field as fc
from tqdb.parsers import fields
from tqdb.storage import skills


def format_path(path):
    try:
        return re.sub(r'[\ \\]', '_', path).lower()
    except TypeError:
        logging.warning(f'Error formatting {path}')
        return None


class UtilityParser:
    """
    Utility functions for the DBR parsers.

    """
    def __init__(self, dbr, props, strings):
        """
        Initialize the UtilityParser.

        """
        from tqdb.parsers.main import parser

        self.dbr = dbr
        self.props = props
        self.parser = parser
        self.result = {}
        self.strings = strings

    def parse_character(self):
        """
        Parse the character properties.

        """
        props = self.props

        for key, field in fc.CHARACTER.items():
            # Parse and add the property according to its field class:
            self.result.update(field(props, key, self.strings).parse())

        # Separately check the 'characterBaseAttackSpeedTag' for weapons:
        if (props.get('Class', '').startswith('Weapon') and
                'Shield' not in props['Class']):
            self.result['characterAttackSpeed'] = self.strings[(
                props['characterBaseAttackSpeedTag'][:1].lower() +
                props['characterBaseAttackSpeedTag'][1:]
            )]

    def parse_damage(self):
        """
        Parse the offensive and retaliation properties.

        """
        props = self.props
        strings = self.strings

        offensive = {}
        retaliation = {}
        for key, field in fc.DAMAGE.items():
            dmg_field = field(props, key, strings)

            # Parse and add the property according to its field class:
            if key.startswith('offensive'):
                offensive[key] = dmg_field
            else:
                retaliation[key] = dmg_field

        # Check offensive global chances:
        key = 'offensiveGlobalChance'
        chance = int(float(props.get(key, 0)))
        self.parse_global(chance, key, offensive)

        # Check retaliation global chances:
        key = 'retaliationGlobalChance'
        chance = int(float(props.get(key, 0)))
        self.parse_global(chance, key, retaliation)

    def parse_defense(self):
        """
        Parse the defensive properties.

        """
        for key, field in fc.DEFENSE.items():
            # Parse and add the property according to its field class:
            self.result.update(field(self.props, key, self.strings).parse())

    def parse_global(self, chance, key, global_items):
        """
        Parse the global chance properties.

        """
        global_properties = {}
        xor = False

        for prop, field in global_items.items():
            parsed = field.parse()
            if not field.is_global:
                self.result.update(parsed)
                continue

            # Any global field being XOR makes them all XOR:
            if not xor and field.is_xor:
                xor = True

            if field.mod:
                # Modifier's always global based if it's set
                global_properties[field.field + 'Modifier'] = (
                    parsed[field.field + 'Modifier'])
                if (xor and field.min and
                        fc.DAMAGE[field.field] !=
                        fields.OffensiveAbsolute):
                    # Add absolute value to global:
                    global_properties[field.field] = parsed[field.field]
                elif xor and field.min:
                    # Add absolute value to regular properties, without chance:
                    field.chance = 0
                    parsed = field.parse()
                    self.result[field.field] = parsed[field.field]
            elif 'Pierce' in field.field and 'retaliation' not in field.field:
                # Add absolute value to regular properties, without chance:
                field.chance = 0
                parsed = field.parse()
                self.result[field.field] = parsed[field.field]
            else:
                global_properties.update(parsed)

        # If any global properties are set, add the global chance:
        if chance and global_properties:
            if xor:
                self.result[key] = {
                    'chance': (
                        fc.GLOBAL_XOR_ALL if chance == 100
                        else self.strings[fc.GLOBAL_XOR_PCT].format(chance)),
                    'properties': global_properties
                }
            else:
                self.result[key] = {
                    'chance': (
                        fc.GLOBAL_ALL if chance == 100
                        else self.strings[fc.GLOBAL_PCT].format(chance)),
                    'properties': global_properties
                }

    def parse_item_skill_augment(self):
        """
        Parse properties that augment or grant skills.

        """
        props = self.props

        if 'itemSkillName' in props and 'itemSkillLevel' in props:
            level = int(props['itemSkillLevel'])

            skill_path = format_path(props['itemSkillName'])
            if skill_path not in skills:
                skill = self.parser.parse(
                    self.get_reference_dbr(props['itemSkillName']))
                # Add skill the the collection
                skills[skill_path] = skill
            else:
                skill = skills[skill_path]

            if 'tag' not in skill:
                logging.warning(f'No tag found in {skill_path}')
            else:
                self.result['itemSkillName'] = {
                    'tag': skill['tag'],
                    'name': (fc.ITEM_SKILL.format(level, skill['name'])
                             if level > 1
                             else fc.ITEM_SKILL_LVL1.format(skill['name'])),
                    'level': level,
                }

        # Parse skills that are augmented:
        for name, level in fc.SKILL_AUGMENTS.items():
            if name not in props or level not in props:
                continue

            skill_path = format_path(props[name])
            if skill_path not in skills:
                skill = self.parser.parse(self.get_reference_dbr(props[name]))
            else:
                skill = skills[skill_path]

            # Skill format is either ItemSkillIncrement or ItemMasteryIncrement
            skill_format = ('ItemSkillIncrement'
                            if 'Mastery' not in skill['name']
                            else 'ItemMasteryIncrement')

            self.result[name] = {
                'tag': skill['tag'],
                'name': self.strings[skill_format].format(
                    int(props[level]), skill['name'])
            }

        # Parse augment to all skills:
        if 'augmentAllLevel' in props:
            self.result['augmentAllLevel'] = (
                self.strings['ItemAllSkillIncrement'].format(
                    int(props['augmentAllLevel'])))

    def parse_pet_bonus(self, tier=-1):
        """
        Parse properties that grant pet bonuses.

        """
        props = self.props
        if 'petBonusName' in props:
            bonus = self.parser.parse(
                self.get_reference_dbr(props['petBonusName']),
                allow_generic=True
            )['properties']

            self.result['petBonus'] = (
                bonus
                if tier == -1 or not isinstance(bonus, list)
                else bonus[tier])

    def parse_racial(self):
        """
        Parse racial bonuses (+ dmg vs ...).

        """
        props = self.props
        if 'racialBonusRace' not in props:
            return

        races_singular = props['racialBonusRace'].split(';')
        races = []
        for race in races_singular:
            if race == 'Beastman':
                races.append('Beastmen')
            elif race != 'Undead' and race != 'Magical':
                races.append(race + 's')
            else:
                races.append(race)

        for prop in fc.RACIAL:
            if prop not in props:
                continue

            # Bonuses can be applied to multiple races, so keep a list:
            self.result[prop] = []
            values = props[prop].split(';')

            for i in range(0, len(races)):
                # Either append unique value or same if none is available:
                self.result[prop].append(
                    self.strings[prop].format(
                        float(values[0]) if len(races)
                        else values[i], races[i]))

    def parse_requirements(self):
        """
        Parse stat and level requirements for items.

        """
        reqs = {}
        props = self.props

        # Check regular requirements first:
        for requirement in fc.REQUIREMENTS:
            req = requirement.lower() + 'Requirement'
            if req in props:
                reqs[req] = props[req]

        if 'itemCostName' in props:
            # Cost prefix of this props is determined by its class
            cost_prefix = props['Class'].split('_')[1]
            cost_prefix = cost_prefix[:1].lower() + cost_prefix[1:]

            # Read cost file
            cost_properties = self.parser.reader.read(
                self.get_reference_dbr(props['itemCostName']))[0]

            # Grab the props level (it's a variable in the equations)
            for requirement in fc.REQUIREMENTS:
                # Create the equation key
                equation_key = cost_prefix + requirement + 'Equation'
                req = requirement.lower() + 'Requirement'

                if equation_key in cost_properties and req not in reqs:
                    equation = cost_properties[equation_key]

                    # Set the possible parameters in the equation:
                    variables = {
                        'itemLevel': int(props.get('itemLevel', 0)),
                        'totalAttCount': len(self.result),
                    }

                    # Eval the equation:
                    reqs[req] = math.ceil(eval(equation, {}, variables))

        return reqs

    def parse_skill_properties(self):
        """
        Parse skill properties.

        """
        props = self.props
        for key, field in fc.SKILL_PROPERTIES.items():
            # Parse and add the property according to its field class:
            self.result.update(field(props, key, self.strings).parse())

        # Check the damage absorption skill properties:
        if 'damageAbsorption' in props or 'damageAbsorptionPercent' in props:
            field = ('damageAbsorption'
                     if 'damageAbsorption' in props
                     else 'damageAbsorptionPercent')
            value = int(float(props[field]))

            # Add 'skill' prefix and capitalize first letter:
            field_prefixed = 'skill' + field[:1].upper() + field[1:]

            # Find qualifier damage type:
            for prop, damage in fc.QUALIFIERS.items():
                if prop in props and props[prop]:
                    # Add the damage absorption value and dmg type:
                    self.result[field_prefixed] = (
                        self.strings[field].format(value, damage))

            # If there is no qualifier, it's all damage:
            if field_prefixed not in self.result:
                self.result[field_prefixed] = (
                    self.strings[field].format(value, 'All'))

    def get_reference_dbr(self, new_dbr):
        # Lowercase the new DBR
        new_dbr = new_dbr.lower()

        # Create the reference
        dbr_ref = self.dbr[:self.dbr.index(new_dbr.split('\\')[0])] + (new_dbr)

        # Quick check to avoid infinite recursion (new reference = self)
        return dbr_ref if self.dbr != dbr_ref else None
