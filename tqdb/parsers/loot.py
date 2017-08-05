import os
import re
from tqdb.parsers.util import format_path
from tqdb.parsers.util import UtilityParser
from tqdb.storage import equipment


class LootRandomizerParser:
    """
    Parser for affixes.

    """
    def __init__(self, dbr, props, strings):
        self.dbr = dbr
        self.props = props[0]
        self.strings = strings

    @classmethod
    def keys(cls):
        return ['LootRandomizer']

    def parse(self):
        result = {}
        if 'lootRandomizerName' in self.props:
            result['tag'] = self.props['lootRandomizerName']
            result['name'] = self.strings[result['tag']]

        util = UtilityParser(self.dbr, self.props, self.strings)
        util.parse_character()
        util.parse_damage()
        util.parse_defense()
        util.parse_item_skill_augment()
        util.parse_pet_bonus()
        util.parse_racial()
        util.parse_skill_properties()

        result['options'] = util.result

        # Now parse the requirements:
        result.update(util.parse_requirements())
        # After parsing the requirements, turn options into a list.
        result['options'] = [result['options']]

        # Find the LootRandomizerTables it's in:

        return result


class LootRandomizerTableParser:
    """
    Parser for affix/bonus tables.

    """
    def __init__(self, dbr, props, strings):
        self.dbr = dbr
        self.props = props[0]
        self.strings = strings

    @classmethod
    def keys(cls):
        return ['LootRandomizerTable']

    def parse(self):
        from tqdb.parsers.main import parser

        options = []
        option_files = {}
        weights = {}

        # Parse the possible completion bonuses:
        for field, value in self.props.items():
            if 'randomizerName' in field:
                number = re.search(r'\d+', field).group()
                option_files[number] = value
            if 'randomizerWeight' in field:
                number = re.search(r'\d+', field).group()
                weights[number] = int(value)

        util = UtilityParser(self.dbr, self.props, self.strings)

        if 'prefix' not in self.dbr and 'suffix' not in self.dbr:
            # Add all the weights together to determined % later
            total_weight = sum(weights.values())
            for field, value in option_files.items():
                if field in weights:
                    # There are some old pointers files that no longer exist:
                    option_file = util.get_reference_dbr(value)
                    if not os.path.exists(option_file):
                        continue

                    # Append the parsed bonus with its chance:
                    options.append({
                        'chance': float('{0:.2f}'.format(
                            (weights[field] / total_weight) * 100)),
                        'option': parser.parse(option_file)['options'][0]
                    })

            # Set all parsed bonuses
            return {
                'options': options
            }


class LootMasterParser:
    """
    Parser for a master table of loot.

    """
    def __init__(self, dbr, props, strings):
        self.dbr = dbr
        self.props = props[0]
        self.strings = strings

    @classmethod
    def keys(cls):
        return ['LootMasterTable']

    def parse(self):
        from tqdb.parsers.main import parser

        util = UtilityParser(self.dbr, self.props, self.strings)
        items = {}

        # Add up all the loot weights:
        summed = sum(int(v) for k, v in self.props.items()
                     if k.startswith('lootWeight'))

        # Run through all the loot chances and parse them:
        for i in range(1, 31):
            weight = int(self.props.get(f'lootWeight{i}', '0'))

            # Skip items with no chance:
            if not weight:
                continue

            chance = float('{0:.5f}'.format(weight / summed))

            # Parse the table and multiply the values by the chance:
            table = parser.parse(util.get_reference_dbr(
                self.props.get(f'lootName{i}'))).items()
            new_items = dict((k, v * chance) for k, v in table)

            for k, v in new_items.items():
                if k in items:
                    items[k] += v
                else:
                    items[k] = v

        return items


class LootFixedContainerParser:
    """
    Parser for chests and fixed item loot.

    """
    def __init__(self, dbr, props, strings):
        self.dbr = dbr
        self.props = props[0]
        self.strings = strings

    @classmethod
    def keys(cls):
        return ['FixedItemContainer']

    def parse(self):
        from tqdb.parsers.main import parser

        util = UtilityParser(self.dbr, self.props, self.strings)
        loot_dbr = util.get_reference_dbr(self.props['tables'])
        loot_props = parser.reader.read(loot_dbr)

        return LootFixedItemParser(loot_dbr, loot_props, self.strings).parse()


class LootFixedItemParser:
    """
    Parser for a fixed list of loot.

    """
    def __init__(self, dbr, props, strings):
        self.dbr = dbr
        self.props = props[0]
        self.strings = strings

    @classmethod
    def keys(cls):
        return ['FixedItemLoot']

    def parse(self):
        from tqdb.parsers.main import parser

        util = UtilityParser(self.dbr, self.props, self.strings)
        items = {}

        # There are 6 loot slots:
        for slot in range(1, 7):
            slot_key = f'loot{slot}'
            slot_chance = float(self.props.get(slot_key + 'Chance', '0'))

            # Skip slots that have 0 chance to drop
            if not slot_chance:
                continue

            # Add up all the loot weights:
            summed = sum(int(v) for k, v in self.props.items()
                         if k.startswith(slot_key + 'Weight'))

            # Run through all the loot chances and parse them:
            for i in range(1, 7):
                weight = int(self.props.get(f'{slot_key}Weight{i}', '0'))

                # Skip items with no chance:
                if not weight:
                    continue

                loot_dbr = util.get_reference_dbr(
                    self.props.get(f'{slot_key}Name{i}'))

                if not os.path.exists(loot_dbr):
                    continue

                # Parse the table and multiply the values by the chance:
                loot_chance = float('{0:.5f}'.format(weight / summed))
                new_items = dict(
                    (k, v * loot_chance * slot_chance) for k, v in
                    parser.parse(loot_dbr).items()
                )

                for k, v in new_items.items():
                    if k in items:
                        items[k] += v
                    else:
                        items[k] = v

        return items


class LootTableDWParser:
    """
    Parser for Dynamic Weight loot tables.

    """
    def __init__(self, dbr, props, strings):
        self.dbr = dbr
        self.props = props
        self.strings = strings

    @classmethod
    def keys(cls):
        return ['LootItemTable_DynWeight']

    def parse(self):
        items = {}

        # Add up all the loot weights:
        summed = sum(float(prop['bellSlope']) for prop in self.props)

        for prop in self.props:
            # Skip tables without items:
            if not prop.get('itemNames') or not prop.get('bellSlope'):
                continue

            # Check that this item is in the equipment list:
            item_path = format_path(prop['itemNames'])
            if item_path not in equipment:
                continue

            weight = float(prop['bellSlope'])
            items[equipment[item_path]['tag']] = float(
                '{0:.5f}'.format(weight / summed))

        return items


class LootTableFWParser:
    """
    Parser for Fixed Weight loot tables.

    """
    def __init__(self, dbr, props, strings):
        self.dbr = dbr
        self.props = props[0]
        self.strings = strings

    @classmethod
    def keys(cls):
        return ['LootItemTable_FixedWeight']

    def parse(self):
        items = {}

        # Add up all the loot weights:
        summed = sum(int(v) for k, v in self.props.items()
                     if k.startswith('lootWeight'))

        # Run through all the loot chances and parse them:
        for i in range(1, 31):
            weight = int(self.props.get('lootWeight' + str(i), '0'))

            # Skip items with no chance:
            if not weight:
                continue

            # Check that this item is in the equipment list:
            item_path = format_path(self.props.get('lootName' + str(i)))
            if item_path not in equipment:
                continue

            # Parse the table and multiply the values by the chance:
            items[equipment[item_path]['tag']] = float(
                '{0:.5f}'.format(weight / summed))

        return items
