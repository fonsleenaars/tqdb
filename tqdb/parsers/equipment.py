import os
import re
from tqdb.parsers.util import format_path
from tqdb.parsers.util import UtilityParser
from tqdb.storage import equipment


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
            'tag': set_props['setName'],
            'set': None,
        }

        # Skip all sets that have no corresponding tag:
        if set_result['tag'] not in strings:
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
            set_item = equipment[set_member]
            result['items'].append(set_item['tag'])

        # Pop off the first element of the properties (1 set item)
        if len(result['properties']) > 1:
            if not result['properties'][0]:
                result['properties'].pop(0)

        # Store the full set result & return it
        set_result['set'] = result

        return set_result
