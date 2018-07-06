# import numexpr
import os
import re

from tqdb import dbr as DBRParser
from tqdb.parsers.main import TQDBParser
from tqdb.utils.text import texts


class LootRandomizerParser(TQDBParser):
    """
    Parser for `lootrandomizer.tpl`.

    """
    def __init__(self):
        super().__init__()

    @staticmethod
    def get_template_path():
        return f'{TQDBParser.base}\\lootrandomizer.tpl'

    def parse(self, dbr, dbr_file, result):
        if 'lootRandomizerName' in dbr:
            result['tag'] = dbr['lootRandomizerName']
            # Some names had inline comments, so strip the spaces:
            result['name'] = texts.get(result['tag']).strip()


class LootRandomizerTableParser(TQDBParser):
    """
    Parser for `lootrandomizertable.tpl`.

    """
    def __init__(self):
        super().__init__()

    @staticmethod
    def get_template_path():
        return f'{TQDBParser.base}\\lootrandomizertable.tpl'

    def parse(self, dbr, dbr_file, result):
        tables = {}
        weights = {}

        # Initialize the results table:
        result['table'] = []

        # Parse all available entries
        for field, value in dbr.items():
            if field.startswith('randomizerName'):
                # Grab the number suffix (1-70)
                number = re.search(r'\d+', field).group()
                # Store the DBR reference in the table
                tables[number] = value
            if field.startswith('randomizerWeight'):
                # Grab the number suffix (1-70)
                number = re.search(r'\d+', field).group()
                # Store the weight reference in the table
                weights[number] = value

        # Add all the weights together to determined % later
        total_weight = sum(weights.values())
        for key, dbr_file in tables.items():
            # Skip entries without chance or without a file
            if key not in weights or not os.path.exists(dbr_file):
                continue

            # Parse the table entry
            randomizer = DBRParser.parse(dbr_file)

            # Append the parsed bonus with its chance:
            result['table'].append({
                'chance': float(
                    '{0:.2f}'.format((weights[key] / total_weight) * 100)),
                'option': randomizer['properties']
            })


# class LootMasterParser:
#     """
#     Parser for a master table of loot.

#     """
#     def __init__(self, dbr, props, strings):
#         self.dbr = dbr
#         self.props = props[0]
#         self.strings = strings

#     @classmethod
#     def keys(cls):
#         return ['LootMasterTable']

#     def parse(self):
#         from tqdb.parsers.main import parser

#         util = UtilityParser(self.dbr, self.props, self.strings)
#         items = {}

#         # Add up all the loot weights:
#         summed = sum(int(v) for k, v in self.props.items()
#                      if k.startswith('lootWeight'))

#         # Run through all the loot chances and parse them:
#         for i in range(1, 31):
#             weight = int(self.props.get(f'lootWeight{i}', '0'))

#             # Skip items with no chance:
#             if not weight:
#                 continue

#             chance = float('{0:.5f}'.format(weight / summed))

#             # Parse the table and multiply the values by the chance:
#             loot_file = self.props.get(f'lootName{i}')
#             if not loot_file:
#                 logging.warning(f'lootName{i} not found in {self.dbr}')
#                 continue

#             table = parser.parse(util.get_reference_dbr(loot_file)).items()
#             new_items = dict((k, v * chance) for k, v in table)

#             for k, v in new_items.items():
#                 if k in items:
#                     items[k] += v
#                 else:
#                     items[k] = v

#         return items


# class LootFixedContainerParser:
#     """
#     Parser for chests and fixed item loot.

#     """
#     def __init__(self, dbr, props, strings):
#         self.dbr = dbr
#         self.props = props[0]
#         self.strings = strings

#     @classmethod
#     def keys(cls):
#         return ['FixedItemContainer']

#     def parse(self):
#         from tqdb.parsers.main import parser

#         util = UtilityParser(self.dbr, self.props, self.strings)

#         if 'tables' not in self.props:
#             logging.warning(f'No table found in {self.dbr}')
#             return {}
#         loot_dbr = util.get_reference_dbr(self.props['tables'])
#         loot_props = parser.reader.read(loot_dbr)

#         return LootFixedItemParser(loot_dbr, loot_props, self.strings).parse()


# class LootFixedItemParser:
#     """
#     Parser for a fixed list of loot.

#     """
#     def __init__(self, dbr, props, strings):
#         self.dbr = dbr
#         self.props = props[0]
#         self.strings = strings

#     @classmethod
#     def keys(cls):
#         return ['FixedItemLoot']

#     def parse(self):
#         from tqdb.parsers.main import parser

#         util = UtilityParser(self.dbr, self.props, self.strings)
#         items = {}

#         # This camelCased variable is required for the spawn equations:
#         numberOfPlayers = 1  # noqa

#         # Grab min/max equation for items that will spawn:
#         max_spawn = numexpr.evaluate(self.props['numSpawnMaxEquation']).item()
#         min_spawn = numexpr.evaluate(self.props['numSpawnMinEquation']).item()
#         spawn_number = (min_spawn + max_spawn) / 2

#         # There are 6 loot slots:
#         for slot in range(1, 7):
#             slot_key = f'loot{slot}'
#             slot_chance = float(self.props.get(slot_key + 'Chance', '0'))

#             # Skip slots that have 0 chance to drop
#             if not slot_chance:
#                 continue

#             # Add up all the loot weights:
#             summed = sum(int(v) for k, v in self.props.items()
#                          if k.startswith(slot_key + 'Weight'))

#             # Run through all the loot chances and parse them:
#             for i in range(1, 7):
#                 weight = int(self.props.get(f'{slot_key}Weight{i}', '0'))

#                 # Skip items with no chance:
#                 if not weight:
#                     continue

#                 loot_dbr = util.get_reference_dbr(
#                     self.props.get(f'{slot_key}Name{i}'))

#                 if not os.path.exists(loot_dbr):
#                     continue

#                 # Parse the table and multiply the values by the chance:
#                 loot_chance = float('{0:.5f}'.format(weight / summed))
#                 new_items = dict(
#                     (k, v * loot_chance * slot_chance * spawn_number)
#                     for k, v in parser.parse(loot_dbr).items()
#                 )

#                 for k, v in new_items.items():
#                     if k in items:
#                         items[k] += v
#                     else:
#                         items[k] = v

#         return items


# class LootTableDWParser:
#     """
#     Parser for Dynamic Weight loot tables.

#     """
#     def __init__(self, dbr, props, strings):
#         self.dbr = dbr
#         self.props = props
#         self.strings = strings

#     @classmethod
#     def keys(cls):
#         return ['LootItemTable_DynWeight']

#     def parse(self):
#         items = {}

#         # Add up all the loot weights:
#         summed = sum(float(prop['bellSlope']) for prop in self.props)

#         for prop in self.props:
#             # Skip tables without items:
#             if not prop.get('itemNames') or not prop.get('bellSlope'):
#                 continue

#             # Check that this item is in the equipment list:
#             item_path = format_path(prop['itemNames'])
#             if not item_path or item_path not in equipment:
#                 logging.warning(f'Could not find {item_path} in equipment')
#                 continue

#             weight = float(prop['bellSlope'])
#             items[equipment[item_path]['tag']] = float(
#                 '{0:.5f}'.format(weight / summed))

#         return items


# class LootTableFWParser:
#     """
#     Parser for Fixed Weight loot tables.

#     """
#     def __init__(self, dbr, props, strings):
#         self.dbr = dbr
#         self.props = props[0]
#         self.strings = strings

#     @classmethod
#     def keys(cls):
#         return ['LootItemTable_FixedWeight']

#     def parse(self):
#         items = {}

#         # Add up all the loot weights:
#         summed = sum(int(v) for k, v in self.props.items()
#                      if k.startswith('lootWeight'))

#         # Run through all the loot chances and parse them:
#         for i in range(1, 31):
#             weight = int(self.props.get('lootWeight' + str(i), '0'))

#             # Skip items with no chance:
#             if not weight:
#                 continue

#             # Check that this item is in the equipment list:
#             item_path = format_path(self.props.get('lootName' + str(i)))
#             if item_path not in equipment:
#                 continue

#             # Parse the table and multiply the values by the chance:
#             items[equipment[item_path]['tag']] = float(
#                 '{0:.5f}'.format(weight / summed))

#         return items
