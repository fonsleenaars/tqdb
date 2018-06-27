# class BossLootParser():
#     """
#     Parser for boss loot and its respective containers.

#     """
#     def __init__(self, dbr, props, strings):
#         self.dbr = dbr
#         self.strings = strings
#         # Jewelry is never tiered, grab first item from list:
#         self.props = props[0]

#     @classmethod
#     def keys(cls):
#         return [
#             'Cerberus',
#             'Hades',
#             'Megalesios',
#             'Monster',
#             'Ormenos',
#             'Typhon2',
#         ]

#     def parse(self):
#         from tqdb.constants.parsing import DIFF_LIST
#         from tqdb.parsers.main import parser

#         reader = parser.reader
#         util = UtilityParser(self.dbr, None, None)
#         strings = parser.strings

#         # Read the properties:
#         props = reader.read(self.dbr)

#         # Grab the first set of properties:
#         boss_props = props[0]
#         boss_class = boss_props.get('monsterClassification', None)
#         boss_tag = boss_props.get('description', None)

#         boss = {
#             'tag': None,
#             'result': None,
#         }

#         # Skip tagless, existing, classless or Common bosses:
#         if (not boss_tag or (
#                 boss_class != 'Hero' and
#                 boss_class != 'Boss' and
#                 boss_class != 'Quest')):
#             return boss

#         # Keep track of all of the result data:
#         result = {
#             'name': strings.get(boss_tag, None)
#         }

#         # The Ragnarok DLC bosses don't all have names yet in the txt resources
#         if not result['name'] and boss_tag.startswith('x2tag'):
#             result['name'] = boss_tag.split('_')[-1].title()
#             logging.warning(
#                 f'Found a nameless boss with {boss_tag}, '
#                 f'using {result["name"]}')

#         # Iterate over normal, epic & legendary version of the boss:
#         difficulties = {}
#         for index, difficulty in enumerate(DIFF_LIST):
#             loot = props[index]

#             # Store all items for this difficulty in an array:
#             difficulty = difficulty.lower()
#             difficulties[difficulty] = {}

#             # Parse all equipable loot:
#             for equipment in EQUIPABLE_LOOT:
#                 equip_key = f'chanceToEquip{equipment}'
#                 equip_chance = float(loot.get(equip_key, '0'))

#                 # Skip equipment that has 0 chance to be equiped
#                 if not equip_chance:
#                     continue

#                 equip_key = f'{equip_key}Item'

#                 # Iterate over all the possibilities and sum up the weights:
#                 summed = sum(int(v) for k, v in loot.items()
#                              if k.startswith(equip_key))
#                 for i in range(1, 7):
#                     weight = float(loot.get(f'{equip_key}{i}', '0'))

#                     # Skip slots that have 0 chance
#                     if not weight:
#                         continue

#                     chance = float('{0:.5f}'.format(weight / summed))

#                     # Parse the table and multiply the values by the chance:
#                     loot_ref = loot.get(f'loot{equipment}Item{i}')

#                     # There are some hero/boss files that have an invalid
#                     # path as the property for the loot reference:
#                     if not loot_ref or not util.get_reference_dbr(loot_ref):
#                         logging.warning(
#                             f'Empty loot{equipment}Item{i} in {self.dbr}')
#                         continue
#                     table = parser.parse(util.get_reference_dbr(loot_ref))

#                     if 'tag' in table:
#                         # Individual item:
#                         items = {table['tag']: chance * equip_chance}
#                     else:
#                         # Dictionary of items:
#                         items = dict((k, v * chance * equip_chance)
#                                      for k, v in table.items())

#                     for k, v in items.items():
#                         if k in difficulties[difficulty]:
#                             difficulties[difficulty][k] += v
#                         else:
#                             difficulties[difficulty][k] = v

#             # Convert all item chances to 4 point precision max:
#             difficulties[difficulty] = dict(
#                 (k, float('{0:.4f}'.format(v))) for k, v
#                 in difficulties[difficulty].items())

#         # Remove all empty difficulties:
#         difficulties = {k: v for k, v in difficulties.items() if v}

#         if difficulties:
#             result['loot'] = difficulties

#         chests = {}

#         # Find the chest for each difficulty:
#         for index, difficulty in enumerate(DIFF_LIST):
#             difficulty = difficulty.lower()

#             # Grab the chest to parse:
#             if boss_tag in CHESTS and CHESTS[boss_tag][index]:
#                 chests[difficulty] = parser.parse(
#                     util.get_reference_dbr(CHESTS[boss_tag][index]))

#                 # Convert all item chances to 4 point precision max:
#                 chests[difficulty] = dict(
#                     (k, float('{0:.4f}'.format(v))) for k, v
#                     in chests[difficulty].items())

#         result['chest'] = chests

#         return {
#             'tag': boss_tag,
#             'result': result
#         }
