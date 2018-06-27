import logging
import math
import os
import re

from tqdb import dbr as DBRParser
from tqdb.parsers.main import TQDBParser
from tqdb.utils.text import texts


class ItemBaseParser(TQDBParser):
    """
    Parser for `templatebase/itembase.tpl`.

    """
    # TQ difficulties, the keys are used in file names and values in texts.
    DIFFICULTIES = {
        'n': 'Normal',
        'e': 'Epic',
        'l': 'Legendary',
    }

    def __init__(self):
        super().__init__()

    @staticmethod
    def get_template_path():
        return f'{TQDBParser.base}\\templatebase\\itembase.tpl'

    def parse(self, dbr, result):
        # Only parse special/unique equipment:
        classification = dbr.get('itemClassification', None)
        if classification not in ['Rare', 'Epic', 'Legendary', 'Magical']:
            return

        result['classification'] = classification

        # For Monster Infrequents, make sure a drop difficulty exists:
        if classification == 'Rare':
            file_name = os.path.basename(self.dbr).split('_')
            if len(file_name) < 2 or file_name[1] not in self.DIFFICULTIES:
                return {}

            result['dropsIn'] = self.DIFFICULTIES[file_name[1]]


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
        tag = dbr.get('itemNameTag', None)
        if not tag:
            return

        # Set the known item properties:
        result.update({
            'bitmap': dbr.get('bitmap', None),
            'itemLevel': dbr.get('itemLevel', None),
            'name': self.MI_NAME_PREFIX.sub('', texts.tag(tag)),
            'tag': tag,
        })

        # Check if this item is part of a set:
        item_set_path = dbr.get('itemSetName', None)
        if item_set_path:
            # Read (don't parse to avoid recursion) the set to get the tag:
            item_set = DBRParser.read(item_set_path)
            result['set'] = item_set[ItemSetParser.NAME]

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


class ItemSetParser(TQDBParser):
    """
    Parser for `itemset.tpl`

    """
    NAME = 'setName'

    def __init__(self):
        super().__init__()

    def get_priority(self):
        """
        Override this parsers priority to set as lowest.

        """
        return TQDBParser.LOWEST_PRIORITY

    @staticmethod
    def get_template_path():
        return f'{TQDBParser.base}\\itemset.tpl'

    def parse(self, dbr, result):
        tag = dbr.get(self.NAME, None)

        if not tag or texts.tag(tag) == tag:
            logging.warning(f'No tag or name for set found.')
            return

        result.update({
            # Prepare the list of set items
            'items': [],
            'name': texts.tag(tag),
            'tag': tag,
        })

        # Add the set members:
        for set_member_path in dbr['setMembers']:
            # Parse the set member:
            set_member = DBRParser.parse(set_member_path)

            # Add the tag to the items list:
            result['items'].append(set_member['tag'])

        # Find the property that has the most tiers
        highest_tier = max([len(v) for v in result['properties'].values()])

        # Because this parser has the lowest priority, all properties will
        # already have been parsed, so they can now be reconstructed to match
        # the set bonuses. Begin by initializing the properties for each set
        # bonus tier to an empty dict:
        properties = [{} for i in range(highest_tier)]

        # Insert the existing properties by adding them to the correct tier:
        for field, values in result['properties'].items():
            # The starting tier is determined by the highest tier
            starting_index = highest_tier - len(values)

            # Now just iterate and add the properties to each tier:
            for index, value in enumerate(values):
                properties[starting_index + index][field] = value

        # Now set the tiered set bonuses:
        result['properties'] = properties

        # Pop off the first element of the properties, if it's empty:
        if len(result['properties']) > 1:
            if not result['properties'][0]:
                result['properties'].pop(0)


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
            dbr.get(f'{self.BLOCK}Chance', 0),
            # Blocked damage
            dbr.get(self.BLOCK, 0))


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
        result['properties']['characterAttackSpeed'] = texts.get(
            dbr['characterBaseAttackSpeedTag'])
