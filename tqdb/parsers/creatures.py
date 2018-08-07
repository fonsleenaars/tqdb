"""
Creature and monster template parsers.

"""
import logging

from tqdb import dbr as DBRParser
from tqdb.constants.resources import DB, CHESTS
from tqdb.parsers.base import ParametersDefensiveParser
from tqdb.parsers.main import TQDBParser
from tqdb.storage import db
from tqdb.utils.text import texts


class MonsterParser(TQDBParser):
    """
    Parser for `monster.tpl`.

    """
    DIFFICULTIES = [
        'normal',
        'epic',
        'legendary',
    ]

    # Equipable slots for monsters to have items in:
    EQUIPMENT_SLOTS = [
        'Head',
        'Torso',
        'LowerBody',
        'Forearm',
        'Finger1',
        'Finger2',
        'RightHand',
        'LeftHand',
        'Misc1',
        'Misc2',
        'Misc3',
    ]

    HP = 'characterLife'
    MP = 'characterMana'

    def __init__(self):
        super().__init__()

    @staticmethod
    def get_template_path():
        return f'{TQDBParser.base}\\monster.tpl'

    def get_priority(self):
        """
        Override this parsers priority to set as lowest.

        """
        return TQDBParser.LOWEST_PRIORITY

    def parse(self, dbr, dbr_file, result):
        """
        Parse the monster.

        """
        self.parse_creature(dbr, dbr_file, result)

        # Don't parse any further for tagless creatures:
        if 'tag' not in result:
            return

        # Iterate over normal, epic & legendary version of the boss:
        difficulties = {}
        for index, difficulty in enumerate(self.DIFFICULTIES):
            # Create a DBR that only has the equipment for this difficulty:
            equipment = TQDBParser.extract_values(dbr, '', index)

            # Parse all the equipment in this difficulty
            difficulty_equipment = self.parse_difficulty(equipment, dbr_file)

            # Only store the equipment if there was any:
            if difficulty_equipment:
                difficulties[difficulty] = difficulty_equipment

        # We're done parsing equipable loot, store it!
        if difficulties:
            result['loot'] = difficulties

        chests = {}
        tag = result['tag']

        # Find the chest for each difficulty:
        for index, difficulty in enumerate(self.DIFFICULTIES):
            # Grab the chest to parse:
            if tag in CHESTS and CHESTS[tag][index]:
                loot = DBRParser.parse(DB / CHESTS[tag][index])

                # Convert all item chances to 4 point precision max:
                chests[difficulty] = dict(
                    (k, float('{0:.4f}'.format(v))) for k, v
                    in loot['loot_table'].items())

        # We're done parsing chest loot, store it!
        if chests:
            result['chest'] = chests

    def parse_creature(self, dbr, dbr_file, result):
        """
        Parse the creature and its properties and skills.

        """
        # Grab the first set of properties:
        classification = dbr.get('monsterClassification', 'Common')
        tag = dbr.get('description', None)

        # Set the known properties for this creature
        if tag:
            result.update({
                'classification': classification,
                'name': texts.get(tag),
                'tag': tag,
            })

        # Manually parse the defensive properties, since there's no template
        # tied for it for monsters:
        ParametersDefensiveParser().parse(dbr, dbr_file, result)

        # Iterate over the properties for each difficulty:
        properties = []
        for i in range(0, 3):
            properties.append({})
            itr = TQDBParser.extract_values(dbr, '', i)

            # Set this creature's HP and MP as stats, not as bonuses:
            if self.HP in itr:
                hp = itr[self.HP]
                properties[i][self.HP] = texts.get('LifeText').format(hp)
            if self.MP in itr:
                mp = itr[self.MP]
                properties[i][self.MP] = texts.get('ManaText').format(mp)

            # Add defensive properties:
            for k, v in result['properties'].items():
                if not k.startswith('defensive'):
                    continue

                # Add the defensive property to the correct difficulty index:
                if isinstance(v, list):
                    # The defensive property changes per difficulty:
                    properties[i][k] = v[i] if i < len(v) else v[-1]
                else:
                    # The defensive property is constant:
                    properties[i][k] = v

        # Add the base damage, stats, regens, and resistances:
        result['properties'] = properties

    def parse_difficulty(self, dbr, dbr_file):
        """
        Parse a difficulty of equipable loot.

        """
        result = {}

        # Parse all equipable loot:
        for equipment in self.EQUIPMENT_SLOTS:
            equip_key = f'chanceToEquip{equipment}'
            equip_chance = dbr.get(equip_key, 0)

            # Skip equipment that has 0 chance to be equiped
            if not equip_chance:
                continue

            equip_key = f'{equip_key}Item'

            # Iterate over all the possibilities and sum up the weights:
            summed = sum(v for k, v in dbr.items()
                         if k.startswith(equip_key))

            for i in range(1, 7):
                weight = dbr.get(f'{equip_key}{i}', 0)

                # Skip slots that have 0 chance
                if not weight:
                    continue

                chance = float('{0:.5f}'.format(weight / summed))

                # Grab the loot table holding the equipment list:
                loot_key = f'loot{equipment}Item{i}'
                loot_file = dbr.get(loot_key)
                if not loot_file or not loot_file.is_file():
                    logging.debug(f'No {loot_key} in {dbr_file}')
                    continue

                loot = DBRParser.parse(loot_file)
                if 'tag' in loot:
                    # ADd a single item that was found:
                    self.add_items(
                        result,
                        {loot['tag']: chance * equip_chance})
                elif 'loot_table' in loot:
                    # Add all the items (and multiply their chances)
                    items = dict(
                        (k, v * chance * equip_chance)
                        for k, v in loot['loot_table'].items())
                    self.add_items(result, items)

        # Convert all item chances to 4 point precision max:
        result = dict(
            (k, float('{0:.4f}'.format(v))) for k, v
            in result.items())

        return result

    def add_items(self, result, items):
        # Either set the chance or add it to a previous chance:
        for item, chance in items.items():
            if item in result:
                result[item] += chance
            else:
                result[item] = chance

        return result
