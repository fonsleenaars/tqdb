import logging
import math
import os

import numexpr

from tqdb import dbr as DBRParser
from tqdb.parsers.main import TQDBParser
from tqdb.utils.text import texts


class ItemArtifactParser(TQDBParser):
    """
    Parser for `itemartifact.tpl`.

    """
    DIFFICULTIES = {
        'n': 'Lesser',
        'e': 'Greater',
        'l': 'Divine',
    }

    def __init__(self):
        super().__init__()

    @staticmethod
    def get_template_path():
        return f'{TQDBParser.base}\\itemartifact.tpl'

    def parse(self, dbr, dbr_file, result):
        file_name = os.path.basename(dbr_file).split('_')

        # Skip artifacts with unknown difficulties in which they drop:
        if file_name[0] not in self.DIFFICULTIES:
            return

        result.update({
            # Bitmap has a different key name than items here.
            'bitmap': dbr.get('artifactBitmap', None),
            # Classification is either Lesser, Greater or Divine
            'classification': dbr.get('artifactClassification', None),
            # Act it starts dropping is based on the file name
            'dropsIn': self.DIFFICULTIES[file_name[0]],
            # For relics the tag is in the Actor.tpl variable 'description'
            'name': texts.get(dbr['description']),
            'tag': dbr['description'],
        })


class ItemArtifactFormulaParser(TQDBParser):
    """
    Parser for `itemartifactformula.tpl`.

    """
    ARTIFACT = 'artifactName'
    BITMAP = 'artifactFormulaBitmapName'

    def __init__(self):
        super().__init__()

    @staticmethod
    def get_template_path():
        return f'{TQDBParser.base}\\itemartifactformula.tpl'

    def parse(self, dbr, dbr_file, result):
        # Skip formula without artifacts
        if self.ARTIFACT not in dbr:
            return

        artifact = DBRParser.parse(dbr[self.ARTIFACT])

        # Update the result with the artifact:
        result['tag'] = artifact['tag']
        result['name'] = artifact['name']
        result['classification'] = artifact['classification']

        if self.BITMAP in dbr:
            result['bitmap'] = dbr[self.BITMAP]

        # Grab the reagents (ingredients):
        for reagent_key in ['reagent1', 'reagent2', 'reagent3']:
            # For some reason reagent DBRs are of type array, so grab [0]:
            reagent = DBRParser.parse(dbr[reagent_key + 'BaseName'][0])

            # Add the reagent (relic, scroll or artifact)
            result[reagent_key] = reagent['tag']

        # Add the potential completion bonuses
        bonuses = DBRParser.parse(dbr['artifactBonusTableName'])
        result['bonus'] = bonuses.get('table', [])

        # Last but not least, pop the 'properties' from this result, since
        # formula don't have the properties themselves, but their respective
        # artifacts do.
        result.pop('properties')


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

    REQUIREMENTS = [
        'dexterityRequirement',
        'intelligenceRequirement',
        'levelRequirement',
        'strengthRequirement',
    ]

    def __init__(self):
        super().__init__()

    @staticmethod
    def get_template_path():
        return f'{TQDBParser.base}\\templatebase\\itembase.tpl'

    def parse(self, dbr, dbr_file, result):
        # Always set the category:
        result['category'] = dbr.get('Class', None)

        # Flat requirements are a part of ItemBase, variable ones aren't:
        for requirement in self.REQUIREMENTS:
            if requirement in dbr:
                result[requirement] = dbr[requirement]

        # Only parse special/unique equipment:
        classification = dbr.get('itemClassification', None)
        if classification not in ['Rare', 'Epic', 'Legendary', 'Magical']:
            return
        result['classification'] = classification

        # For Monster Infrequents, make sure a drop difficulty exists:
        if classification == 'Rare':
            file_name = os.path.basename(dbr_file).split('_')
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

    def __init__(self):
        super().__init__()

    def get_priority(self):
        """
        Override this parsers priority to set as lowest.

        """
        return TQDBParser.LOWEST_PRIORITY

    @staticmethod
    def get_template_path():
        return f'{TQDBParser.base}\\templatebase\\itemequipment.tpl'

    def parse(self, dbr, dbr_file, result):
        # If no tag exists, skip parsing:
        tag = dbr.get('itemNameTag', None)
        if not tag:
            return

        # Set the known item properties:
        result.update({
            'bitmap': dbr.get('bitmap', None),
            'itemLevel': dbr.get('itemLevel', None),
            'name': texts.get(tag),
            'tag': tag,
        })

        # Check if this item is part of a set:
        item_set_path = dbr.get('itemSetName', None)
        if item_set_path:
            # Read (don't parse to avoid recursion) the set to get the tag:
            item_set = DBRParser.read(item_set_path)

            # Only add the set if it has a tag:
            result['set'] = item_set.get(ItemSetParser.NAME, None)

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

                # Existing requirements shouldn't be overriden:
                if equation_key in cost_properties and req not in result:
                    equation = cost_properties[equation_key]

                    # camelCased variables are required for the equations:
                    itemLevel = dbr['itemLevel']  # noqa
                    totalAttCount = len(result['properties'])  # noqa

                    # Eval the equation:
                    result[req] = math.ceil(numexpr.evaluate(equation).item())


class ItemRelicParser(TQDBParser):
    """
    Parser for `itemrelic.tpl`.

    """
    DIFFICULTIES = ['Normal', 'Epic', 'Legendary']

    def __init__(self):
        super().__init__()

    @staticmethod
    def get_template_path():
        return f'{TQDBParser.base}\\itemrelic.tpl'

    def parse(self, dbr, dbr_file, result):
        file_name = os.path.basename(dbr_file).split('_')
        difficulty_index = int(file_name[0][1:]) - 1

        result.update({
            # The act it starts dropping in is also listed in the file name
            'act': file_name[1],
            # Bitmap has a different key name than items here.
            'bitmap': dbr.get('relicBitmap', None),
            # Difficulty classification is based on the file name
            'classification': self.DIFFICULTIES[difficulty_index],
            # Ironically the itemText holds the actual description tag
            'description': texts.get(dbr['itemText']),
            # For relics the tag is in the Actor.tpl variable 'description'
            'name': texts.get(dbr['description']),
            'tag': dbr['description'],
        })

        # The possible completion bonuses are in bonusTableName:
        bonuses = DBRParser.parse(dbr['bonusTableName'])
        result['bonus'] = bonuses.get('table', [])


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

    def parse(self, dbr, dbr_file, result):
        tag = dbr.get(self.NAME, None)

        if not tag or texts.get(tag) == tag:
            logging.warning(f'No tag or name for set found in {dbr_file}.')
            return

        result.update({
            # Prepare the list of set items
            'items': [],
            'name': texts.get(tag),
            'tag': tag,
        })

        # Add the set members:
        for set_member_path in dbr['setMembers']:
            # Parse the set member:
            set_member = DBRParser.parse(set_member_path)

            # Add the tag to the items list:
            result['items'].append(set_member['tag'])

        # Find the property that has the most tiers
        highest_tier = max(
            # Property was parsed as list, grab length of the list
            len(v)
            if isinstance(v, list)
            # Property wasn't parsed as list, meaning there is 1 instance
            else 1
            for v in result['properties'].values())

        # Because this parser has the lowest priority, all properties will
        # already have been parsed, so they can now be reconstructed to match
        # the set bonuses. Begin by initializing the properties for each set
        # bonus tier to an empty dict:
        properties = [{} for i in range(highest_tier)]

        # Insert the existing properties by adding them to the correct tier:
        for field, values in result['properties'].items():
            if not isinstance(values, list):
                # Values that aren't repeated should be set for all tiers:
                for index, _ in enumerate(properties):
                    properties[index][field] = values

                # Don't parse any further
                continue

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


class OneShotScrollParser(TQDBParser):
    """
    Parser for `oneshot_scroll.tpl`.

    """
    DIFFICULTIES = ['Normal', 'Epic', 'Legendary']

    def __init__(self):
        super().__init__()

    @staticmethod
    def get_template_path():
        # Note: this technically handles parameters from oneshot.tpl too.
        return f'{TQDBParser.base}\\oneshot_scroll.tpl'

    def parse(self, dbr, dbr_file, result):
        """
        Parse the scroll.

        """
        # Use the file name to determine the difficulty:
        file_name = os.path.basename(dbr_file).split('_')[0][1:]
        # Strip all but digits from the string, then cast to int:
        difficulty_index = int(
            ''.join(filter(lambda x: x.isdigit(), file_name))) - 1

        result.update({
            'tag': dbr['description'],
            'name': texts.get(dbr['description']),
            'classification': self.DIFFICULTIES[difficulty_index],
            'description': texts.get(dbr['itemText']),
        })

        # Set the bitmap if it exists
        if 'bitmap' in dbr:
            result['bitmap'] = dbr['bitmap']

        # Grab the skill file:
        skill = DBRParser.parse(dbr['skillName'])

        # Add properties if there are any:
        if 'properties' in skill and skill['properties']:
            result['properties'] = skill['properties']

        # Add any summon (just the first one)
        if 'summons' in skill:
            result['summons'] = skill['summons'][0]


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

    def parse(self, dbr, dbr_file, result):
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

    def parse(self, dbr, dbr_file, result):
        dbr_class = dbr['Class']

        # Skip shields:
        if (dbr_class.startswith('Weapon') and 'Shield' in dbr_class):
            return None

        # Set the attack speed
        result['properties']['characterAttackSpeed'] = texts.get(
            dbr['characterBaseAttackSpeedTag'])
