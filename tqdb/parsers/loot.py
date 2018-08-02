"""
All loot table parsers.

"""
import logging
import numexpr
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


class LootMasterTableParser(TQDBParser):
    """
    Parser for `lootmastertable.tpl`.

    """
    def __init__(self):
        super().__init__()

    @staticmethod
    def get_template_path():
        return f'{TQDBParser.base}\\lootmastertable.tpl'

    def parse(self, dbr, dbr_file, result):
        items = {}

        # Add up all the loot weights:
        summed = sum(v for k, v in dbr.items() if k.startswith('lootWeight'))

        # Run through all the loot entries and parse them:
        for i in range(1, 31):
            weight = dbr.get(f'lootWeight{i}', 0)

            # Skip items with no chance:
            if not weight:
                continue

            chance = float('{0:.5f}'.format(weight / summed))

            try:
                # Try to parse the referenced loot file
                loot_file = dbr[f'lootName{i}']
            except KeyError:
                logging.warning(f'lootName{i} not found in {dbr_file}.')
                continue

            # Parse the loot file
            loot = DBRParser.parse(loot_file)

            # Loot entries will be in 'table', add those:
            for k, v in loot['loot_table'].items():
                if k in items:
                    items[k] += (v * chance)
                else:
                    items[k] = (v * chance)

        # Add the parsed loot table
        result['loot_table'] = items


class FixedItemContainerParser(TQDBParser):
    """
    Parser for `fixeditemcontainer.tpl`.

    This type of loot table simply references another in its 'tables' property.
    All that's required is parsing the reference, and setting the result.

    """
    def __init__(self):
        super().__init__()

    @staticmethod
    def get_template_path():
        return f'{TQDBParser.base}\\fixeditemcontainer.tpl'

    def parse(self, dbr, dbr_file, result):
        if 'tables' not in dbr:
            logging.warning(f'No table found in {dbr_file}')
            return

        # Parse the references 'tables' file and set the result:
        loot = DBRParser.parse(dbr['tables'][0])
        result['loot_table'] = loot['loot_table']


class FixedItemLootParser(TQDBParser):
    """
    Parser for `fixeditemloot.tpl`.

    """
    def __init__(self):
        super().__init__()

    @staticmethod
    def get_template_path():
        return f'{TQDBParser.base}\\fixeditemloot.tpl'

    def parse(self, dbr, dbr_file, result):
        # Initialize a dictionary of item chances to add to:
        self.items = {}

        # This camelCased variable is required for the spawn equations:
        numberOfPlayers = 1  # noqa

        # Grab min/max equation for items that will spawn:
        max_spawn = numexpr.evaluate(dbr['numSpawnMaxEquation']).item()
        min_spawn = numexpr.evaluate(dbr['numSpawnMinEquation']).item()
        spawn_number = (min_spawn + max_spawn) / 2

        # There are 6 loot slots:
        for slot in range(1, 7):
            self.parse_loot(f'loot{slot}', spawn_number, dbr)

        result['loot_table'] = self.items

    def parse_loot(self, loot_key, spawn_number, dbr):
        chance = dbr.get(f'{loot_key}Chance', 0)

        # Skip slots that have 0 chance to drop
        if not chance:
            return

        # Add up all the loot weights:
        summed = sum(v for k, v in dbr.items()
                     if k.startswith(f'{loot_key}Weight'))

        # Run through all the loot possibilities and parse them:
        for i in range(1, 7):
            weight = dbr.get(f'{loot_key}Weight{i}', 0)

            # Skip items with no chance:
            if not weight:
                continue

            try:
                loot = DBRParser.parse(dbr[f'{loot_key}Name{i}'][0])

                # Parse the table and multiply the values by the chance:
                loot_chance = float('{0:.5f}'.format(weight / summed))
                new_items = dict(
                    (k, v * loot_chance * chance * spawn_number)
                    for k, v in loot['loot_table'].items()
                )
            except KeyError:
                # Skip files that weren't found/parsed (no loot_table)
                continue

            for k, v in new_items.items():
                if k in self.items:
                    self.items[k] += v
                else:
                    self.items[k] = v


class LootItemTable_DynWeightParser(TQDBParser):
    """
    Parser for `lootitemtable_dynweight.tpl`.

    """
    def __init__(self):
        super().__init__()

    @staticmethod
    def get_template_path():
        return f'{TQDBParser.base}\\lootitemtable_dynweight.tpl'

    def parse(self, dbr, dbr_file, result):
        items = {}

        # Add up all the loot weights:
        summed = sum(weight for weight in dbr['bellSlope'])

        for index, loot_file in enumerate(dbr.get('itemNames', [])):
            # Grab the item and its chance
            item = DBRParser.parse(loot_file)

            if 'tag' not in item:
                logging.warning(f'No tag for {loot_file} in {dbr_file}')
                continue

            try:
                weight = dbr['bellSlope'][index]
            except IndexError:
                # Grab the last known entry
                weight = dbr['bellSlope'][-1]

            # Store the chance of this item by its tag:
            items[item['tag']] = float('{0:.5f}'.format(weight / summed))

        result['loot_table'] = items


class LootItemTable_FixedWeightParser(TQDBParser):
    """
    Parser for `lootitemtable_fixedweight.tpl`.

    """
    def __init__(self):
        super().__init__()

    @staticmethod
    def get_template_path():
        return f'{TQDBParser.base}\\lootitemtable_fixedweight.tpl'

    def parse(self, dbr, dbr_file, result):
        items = {}

        # Add up all the loot weights:
        summed = sum(v for k, v in dbr.items()
                     if k.startswith('lootWeight'))

        # Run through all the loot chances and parse them:
        for i in range(1, 31):
            weight = dbr.get(f'lootWeight{i}', 0)

            # Skip items with no chance:
            if not weight:
                continue

            # Grab the item and its chance
            item = DBRParser.parse(dbr[f'lootName{i}'])

            try:
                # Store the chance of this item by its tag:
                items[item['tag']] = float('{0:.5f}'.format(weight / summed))
            except KeyError:
                # Skip items that have no tag:
                continue

        result['loot_table'] = items
