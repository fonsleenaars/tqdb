import logging
import os
import re
from tqdb.constants.field import EQUIPABLE_LOOT
from tqdb.constants.resources import CHESTS
from tqdb.parsers.util import UtilityParser


class BossLootParser():
    """
    Parser for boss loot and its respective containers.

    """
    def __init__(self, dbr, props, strings):
        self.dbr = dbr
        self.strings = strings
        # Jewelry is never tiered, grab first item from list:
        self.props = props[0]

    @classmethod
    def keys(cls):
        return [
            'Cerberus',
            'Hades',
            'Megalesios',
            'Monster',
            'Ormenos',
            'Typhon2',
        ]

    def parse(self):
        from tqdb.constants.parsing import DIFF_LIST
        from tqdb.parsers.main import parser

        reader = parser.reader
        util = UtilityParser(self.dbr, None, None)
        strings = parser.strings

        # Read the properties:
        props = reader.read(self.dbr)

        # Grab the first set of properties:
        boss_props = props[0]
        bossClass = boss_props.get('monsterClassification', None)
        bossTag = boss_props.get('description', None)

        boss = {
            'tag': None,
            'result': None,
        }

        # Skip tagless, existing, classless or Common bosses:
        if (not bossTag or (
                bossClass != 'Boss' and
                bossClass != 'Quest')):
            return boss

        # Keep track of all of the result data:
        result = {
            'name': strings.get(bossTag, None)
        }

        # Iterate over normal, epic & legendary version of the boss:
        difficulties = {}
        for index, difficulty in enumerate(DIFF_LIST):
            loot = props[index]

            # Store all items for this difficulty in an array:
            difficulty = difficulty.lower()
            difficulties[difficulty] = {}

            # Parse all equipable loot:
            for equipment in EQUIPABLE_LOOT:
                equip_key = f'chanceToEquip{equipment}'
                equip_chance = float(loot.get(equip_key, '0'))

                # Skip equipment that has 0 chance to be equiped
                if not equip_chance:
                    continue

                equip_key = f'{equip_key}Item'

                # Iterate over all the possibilities and sum up the weights:
                summed = sum(int(v) for k, v in loot.items()
                             if k.startswith(equip_key))
                for i in range(1, 7):
                    weight = float(loot.get(f'{equip_key}{i}', '0'))

                    # Skip slots that have 0 chance
                    if not weight:
                        continue

                    chance = float('{0:.5f}'.format(weight / summed))

                    # Parse the table and multiply the values by the chance:
                    loot_ref = loot.get(f'loot{equipment}Item{i}')
                    if not loot_ref:
                        logging.warning(
                            f'Empty loot{equipment}Item{i} in {self.dbr}')
                        continue
                    table = parser.parse(util.get_reference_dbr(loot_ref))

                    if 'tag' in table:
                        # Individual item:
                        items = {table['tag']: chance * equip_chance}
                    else:
                        # Dictionary of items:
                        items = dict((k, v * chance * equip_chance)
                                     for k, v in table.items())

                    for k, v in items.items():
                        if k in difficulties[difficulty]:
                            difficulties[difficulty][k] += v
                        else:
                            difficulties[difficulty][k] = v

            # Convert all item chances to 4 point precision max:
            difficulties[difficulty] = dict(
                (k, float('{0:.4f}'.format(v))) for k, v
                in difficulties[difficulty].items())

        # Remove all empty difficulties:
        difficulties = {k: v for k, v in difficulties.items() if v}

        if difficulties:
            result['loot'] = difficulties

        # Now find the chest for this boss:
        m = re.match(r'boss_(.*)_([0-9]{2})\.dbr', os.path.basename(self.dbr))
        if m:
            boss_name = m.group(1)
            chests = {}

            # Find the chest for each difficulty:
            for index, difficulty in enumerate(DIFF_LIST):
                difficulty = difficulty.lower()

                # Grab the chest to parse:
                if boss_name in CHESTS and CHESTS[boss_name][index]:
                    chests[difficulty] = parser.parse(
                        util.get_reference_dbr(CHESTS[boss_name][index]))

                    # Convert all item chances to 4 point precision max:
                    chests[difficulty] = dict(
                        (k, float('{0:.4f}'.format(v))) for k, v
                        in chests[difficulty].items())

            result['chest'] = chests

        return {
            'tag': bossTag,
            'result': result
        }
