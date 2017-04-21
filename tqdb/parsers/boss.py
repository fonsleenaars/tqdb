import os
import re
from tqdb.constants import field
from tqdb.constants.parsing import DIFF_LIST
from tqdb.constants.resources import CHESTS
from tqdb.parsers.util import UtilityParser


class BossLootParser():
    """
    Parser for boss loot and its respective containers.

    """
    def __init__(self, dbr):
        self.dbr = dbr

    def parse(self):
        from tqdb.parsers.main import parser

        reader = parser.reader
        util = UtilityParser(self.dbr, None, None)
        strings = parser.strings

        # Read the properties:
        props = reader.read(self.dbr)

        # Grab the first set of properties:
        boss = props[0]
        bossClass = boss.get('monsterClassification', None)
        bossTag = boss.get('description', None)

        # Skip tagless, existing, classless or Common bosses:
        if (not bossTag or (
                bossClass != 'Boss' and
                bossClass != 'Quest')):
            return None, None

        result = {
            'name': strings.get(bossTag, None),
        }

        difficulties = {}

        # Iterate over normal, epic & legendary version of the boss:
        for index, difficulty in enumerate(DIFF_LIST):
            loot = props[index]

            # Store all items for this difficulty in an array:
            difficulty = difficulty.lower()
            difficulties[difficulty] = {}

            # Parse all equipable loot:
            for equipment in field.EQUIPABLE_LOOT:
                chance_equip = float(loot.get(
                    'chanceToEquip' + equipment, '0'))

                # Skip equipment that has 0 chance to be equiped
                if not chance_equip:
                    continue

                item_key = equipment + 'Item'

                # Iterate over all the possibilities and sum up the weights:
                summed = sum(int(v) for k, v in loot.items()
                             if k.startswith('chanceToEquip' + item_key))
                for i in range(1, 6):
                    weight = float(loot.get(
                        'chanceToEquip' + item_key + str(i), '0'))

                    # Skip slots that have 0 chance
                    if not weight:
                        continue

                    chance = float('{0:.5f}'.format(weight / summed))

                    # Parse the table and multiply the values by the chance:
                    items = dict(
                        (k, v * chance * chance_equip) for k, v in
                        parser.parse(util.get_reference_dbr(
                            loot.get('loot' + item_key + str(i)))
                        ).items()
                    )

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

        return bossTag, result
