import logging
import math
import os
import re

from tqdb import dbr as DBRParser
from tqdb.parsers.main import TQDBParser
from tqdb.parsers.util import format_path
from tqdb.parsers.util import UtilityParser
from tqdb.storage import equipment
from tqdb.utils.text import texts


class ItemEquipmentParser(TQDBParser):
    """
    Parser for `templatebase/itemequipment.tpl`.

    """
    # The prefixes for the types of requirements for items:
    REQUIREMENTS = [
        'Dexterity',
        'Intelligence',
        'Level',
        'Strength',
    ]

    # Regex to remove the {} prefixes in Monster Infrequents:
    MI_NAME_PREFIX = re.compile(r'\{[^)]*\}')

    def __init__(self):
        super().__init__()

    @staticmethod
    def get_template_path():
        return f'{TQDBParser.base}\\templatebase\\itemequipment.tpl'

    def parse(self, dbr, result):
        # If no tag exists, skip parsing:
        if 'itemNameTag' not in dbr:
            return

        # Set the known item properties:
        tag = dbr['itemNameTag']
        result.update({
            'bitmap': dbr.get('bitmap', None),
            'itemLevel': dbr['itemLevel'],
            'name': self.MI_NAME_PREFIX.sub('', texts.tag(tag)),
            'tag': tag,
        })

        # Although Requirements themselves are a part of ItemBase.tpl, the
        # itemCostName property (equation based requirements) are a part of
        # this parser, so they're added on here instead.
        requirements = {}
        for requirement in self.REQUIREMENTS:
            key = requirement.lower() + 'Requirement'
            if key in dbr:
                requirements[key] = dbr[key]

        if 'itemCostName' in dbr:
            # Cost prefix of this props is determined by its class
            cost_prefix = dbr['Class'].split('_')[1]
            cost_prefix = cost_prefix[:1].lower() + cost_prefix[1:]

            # Read cost file
            cost_properties = DBRParser.read(dbr['itemCostName'])

            # Grab the props level (it's a variable in the equations)
            for requirement in self.REQUIREMENTS:
                # Create the equation key
                equation_key = cost_prefix + requirement + 'Equation'
                req = requirement.lower() + 'Requirement'

                if equation_key in cost_properties and req not in requirements:
                    equation = cost_properties[equation_key]

                    # Set the possible parameters in the equation:
                    variables = {
                        'itemLevel': dbr['itemLevel'],
                        'totalAttCount': len(result['properties']),
                    }

                    # Eval the equation:
                    requirements[req] = math.ceil(
                        # XXX - Find safe eval solution.
                        eval(equation, {}, variables))

        # Now merge the finalized requirements:
        result.update(requirements)


class ShieldParser(TQDBParser):
    """
    Parser for `weaponarmor_shield.tpl`.

    """
    # The tag of the resource text that will show block chance & values:
    TEXT = 'tagShieldBlockInfo'
    BLOCK = 'defensiveBlock'

    def __init__(self):
        super().__init__()

    @staticmethod
    def get_template_path():
        return f'{TQDBParser.base}\\weaponarmor_shield.tpl'

    def parse(self, dbr, result):
        # Set the block chance and value:
        result['properties'][self.BLOCK] = texts.get(self.TEXT).format(
            # Block chance
            dbr[f'{self.BLOCK}Chance'],
            # Blocked damage
            dbr[self.BLOCK])


class WeaponParser(TQDBParser):
    """
    Parser for `templatebase/weapon.tpl`.

    """
    def __init__(self):
        super().__init__()

    @staticmethod
    def get_template_path():
        return f'{TQDBParser.base}\\templatebase\\weapon.tpl'

    def parse(self, dbr, result):
        dbr_class = dbr['Class']

        # Skip shields:
        if (dbr_class.startswith('Weapon') and 'Shield' in dbr_class):
            return None

        # Set the attack speed
        result['characterAttackSpeed'] = texts.get(
            dbr['characterBaseAttackSpeedTag'])


class ArmorWeaponParser():
    """
    Parser for Weapon files.

    """
    def __init__(self, dbr, props, strings):
        self.dbr = dbr
        self.strings = strings
        # Jewelry is never tiered, grab first item from list:
        self.props = props[0]

    @classmethod
    def keys(cls):
        return [
            'ArmorJewelry_Ring',
            'ArmorJewelry_Amulet',
            'ArmorProtective_Head',
            'ArmorProtective_Forearm',
            'ArmorProtective_UpperBody',
            'ArmorProtective_LowerBody',
            'WeaponMelee_Axe',
            'WeaponMelee_Mace',
            'WeaponMelee_Sword',
            'WeaponHunting_Bow',
            'WeaponHunting_RangedOneHand',
            'WeaponHunting_Spear',
            'WeaponMagical_Staff',
            'WeaponArmor_Shield',
        ]

    def parse(self):
        from tqdb.constants.parsing import DIFFICULTIES

        result = {}

        # Only parse special/unique equipment:
        classification = self.props.get('itemClassification', None)
        if classification not in ['Rare', 'Epic', 'Legendary', 'Magical']:
            return {}

        result['classification'] = classification

        # For Monster Infrequents, make sure a drop difficulty exists:
        if classification == 'Rare':
            file_name = os.path.basename(self.dbr).split('_')
            if len(file_name) < 2 or file_name[1] not in DIFFICULTIES:
                return {}

            result['dropsIn'] = DIFFICULTIES[file_name[1]]

        # Set item level, tag & name
        result['itemLevel'] = int(self.props.get('itemLevel', 0))
        result['tag'] = self.props.get('itemNameTag', None)
        if not result['tag']:
            return {}

        result['name'] = self.strings.get(result['tag'], '')
        if result['name']:
            # Fix for {} appearing in MI names:
            result['name'] = re.sub(r'\{[^)]*\}', '', result['name'])

        # Set the bitmap if it exists
        if 'bitmap' in self.props:
            result['bitmap'] = self.props['bitmap']

        # Let the UtilityParser parse all the common properties:
        util = UtilityParser(self.dbr, self.props, self.strings)
        util.parse_character()
        util.parse_damage()
        util.parse_defense()
        util.parse_item_skill_augment()
        util.parse_pet_bonus()
        util.parse_racial()
        util.parse_skill_properties()

        result['properties'] = util.result

        # Now parse the requirements:
        result.update(util.parse_requirements())

        return result


class JewelryParser():
    """
    Parser for Weapon files.

    """
    def __init__(self, dbr, props, strings):
        self.dbr = dbr
        self.strings = strings
        # Jewelry is never tiered, grab first item from list:
        self.props = props[0]

    @classmethod
    def keys(cls):
        return [
            'ArmorJewelry_Ring',
            'ArmorJewelry_Amulet',
        ]

    def parse(self):
        result = {}

        # Only parse special/unique equipment:
        classification = self.props.get('itemClassification', None)
        if classification not in ['Rare', 'Epic', 'Legendary', 'Magical']:
            return {}
        result['classification'] = classification

        # Set item level, tag & name
        result['itemLevel'] = int(self.props.get('itemLevel', 0))
        result['tag'] = self.props.get('itemNameTag', None)
        if not result['tag']:
            return {}
        result['name'] = self.strings.get(result['tag'], '')

        # Set the bitmap if it exists
        if 'bitmap' in self.props:
            result['bitmap'] = self.props['bitmap']

        # Let the UtilityParser parse all the common properties:
        util = UtilityParser(self.dbr, self.props, self.strings)
        util.parse_character()
        util.parse_damage()
        util.parse_defense()
        util.parse_item_skill_augment()
        util.parse_pet_bonus()
        util.parse_racial()
        util.parse_skill_properties()

        result['properties'] = util.result

        # Now parse the requirements:
        result.update(util.parse_requirements())

        return result


class SetParser():
    """
    Parser for set bonuses.

    """
    def __init__(self, dbr):
        self.dbr = dbr

    def parse(self):
        from tqdb.parsers.main import parser

        reader = parser.reader
        strings = parser.strings

        # Read the properties:
        props = reader.read(self.dbr)

        # Set some of the shared properties:
        set_props = props[0]
        set_result = {
            'tag': set_props.get('setName', None),
            'set': None,
        }

        # Skip all sets that have no corresponding tag:
        if not set_result['tag'] or set_result['tag'] not in strings:
            logging.warning(f'No tag or name for set in {self.dbr}')
            return set_result

        result = {
            'name': strings[set_result['tag']],
            'properties': [],
            'items': [],
        }
        for prop in props:
            util = UtilityParser(self.dbr, prop, strings)
            util.parse_character()
            util.parse_damage()
            util.parse_defense()
            util.parse_skill_properties()

            result['properties'].append(util.result)

            # Add the set member:
            set_member = format_path(prop['setMembers'])

            # If the equipment is available; load the item tag
            if set_member not in equipment:
                logging.warning(f'Missing {set_member} in {result["name"]}')
                continue

            set_item = equipment[set_member]
            result['items'].append(set_item['tag'])

        # Pop off the first element of the properties (1 set item)
        if len(result['properties']) > 1:
            if not result['properties'][0]:
                result['properties'].pop(0)

        # Store the full set result & return it
        set_result['set'] = result

        return set_result
