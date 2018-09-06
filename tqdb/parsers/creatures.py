"""
Creature and monster template parsers.

"""
import logging

from tqdb import dbr as DBRParser
from tqdb import storage
from tqdb.constants.resources import DB, CHESTS
from tqdb.parsers import base as parsers
from tqdb.parsers.main import TQDBParser
from tqdb.utils.text import texts


class CharacterParser(TQDBParser):
    """
    Parser for `character.tpl`.

    """
    MAX = 'handHitDamageMax'
    MIN = 'handHitDamageMin'

    def __init__(self):
        super().__init__()

    @staticmethod
    def get_template_path():
        return f'{TQDBParser.base}\\character.tpl'

    def parse(self, dbr, dbr_file, result):
        """
        Parse a character's properties.

        """
        if self.MIN not in dbr:
            return

        dmg_min = dbr[self.MIN]
        dmg_max = dbr.get(self.MAX, dmg_min)

        # Set the damage this character does as a property:
        result['properties']['offensivePhysical'] = (
            parsers.ParametersOffensiveParser.format(
                parsers.ParametersOffensiveParser.ABSOLUTE,
                'offensivePhysical',
                dmg_min,
                dmg_max))


class MonsterParser(TQDBParser):
    """
    Parser for `monster.tpl`.

    """
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
        return [
            f'{TQDBParser.base}\\monster.tpl',
            # For some reason the doppel summon template does not extend the
            # regular monster template, but has its own:
            f'{TQDBParser.base}\\doppelganger.tpl',
        ]

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

        # Don't parse any further for tagless or level-less creatures:
        if 'tag' not in result or not result['level']:
            return

        # Iterate over normal, epic & legendary version of the boss:
        loot = []
        for index in range(3):
            # Initialize an empty result:
            loot.append({})

            # Create a DBR that only has the equipment for this difficulty:
            difficulty_dbr = TQDBParser.extract_values(dbr, '', index)

            # Parse all the equipment in this difficulty
            difficulty_dbr = self.parse_difficulty(difficulty_dbr, dbr_file)

            # Only store the equipment if there was any:
            if difficulty_dbr:
                loot[index] = difficulty_dbr

        # If there is any tiered data to store, store it:
        if any(tier for tier in loot if tier):
            result['loot'] = loot

        chests = []
        tag = result['tag']

        # Find the chest for each difficulty:
        for index in range(3):
            # Initialize an empty result:
            chests.append({})

            # Grab the chest to parse:
            if tag in CHESTS and CHESTS[tag][index]:
                loot = DBRParser.parse(DB / CHESTS[tag][index])

                # Convert all item chances to 4 point precision:
                chests[index] = dict(
                    (k, float('{0:.4f}'.format(v))) for k, v
                    in loot['loot_table'].items())

        # If there is any tiered data to store, store it:
        if any(tier for tier in chests if tier):
            result['chest'] = chests

        # Check if this monster is limited to a difficulty:
        if len(result['level']) != len(set(result['level'])):
            # If a level is repeated, it means a creature doesn't spawn in
            # some difficulties. The 'normal' difficulty level is either
            # repeated in Epic and Legendary, so find the index and subtract
            # 1 from that to get all difficulties that should be removed:
            for i in range(result['level'].count(result['level'][0]) - 1):
                result['properties'][i] = {}
                result['abilities'][i] = {}
                result['level'][i] = None

    def parse_creature(self, dbr, dbr_file, result):
        """
        Parse the creature and its properties and skills.

        """
        # Grab the first set of properties:
        classification = dbr.get('monsterClassification', 'Common')
        tag = dbr.get('description', None)

        # Set the known properties for this creature
        if tag:
            race = dbr.get('characterRacialProfile', None)
            result.update({
                'classification': classification,
                'name': texts.get(tag),
                'race': race[0] if race else None,
                'level': [level for level in dbr.get('charLevel', [])],
                'tag': tag,
            })

        # Manually parse the defensive properties, since there's no template
        # tied for it for monsters:
        parsers.ParametersDefensiveParser().parse(dbr, dbr_file, result)

        # Iterate over the properties for each difficulty:
        properties = []
        for i in range(3):
            properties.append({})
            itr = TQDBParser.extract_values(dbr, '', i)

            # Set this creature's HP and MP as stats, not as bonuses:
            if self.HP in itr:
                hp = itr[self.HP]
                properties[i][self.HP] = texts.get('LifeText').format(hp)
            if self.MP in itr:
                mp = itr[self.MP]
                properties[i][self.MP] = texts.get('ManaText').format(mp)

            # Add non-character properties:
            for k, v in result['properties'].items():
                if k.startswith('character'):
                    continue

                # Add the property to the correct difficulty index:
                if isinstance(v, list):
                    # The property changes per difficulty:
                    properties[i][k] = v[i] if i < len(v) else v[-1]
                else:
                    # The property is constant:
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

                loot = DBRParser.parse(loot_file, {'level': dbr['charLevel']})
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

        # Convert all item chances to 4 point precision:
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


class MonsterSkillManager(TQDBParser):
    """
    Parser for `templatebase\\monsterskillmanager.tpl`.

    """
    # Skills to ignore when parsing pet buffs/skills:
    IGNORE_SKILLS = list(
        f'data\\database\\records{skill}' for skill in [
            '\\skills\\monster skills\\passive_totaldamageabsorption01.dbr',
            '\\skills\\monster skills\\defense\\armor_passive.dbr',
            '\\skills\\monster skills\\defense\\banner_debuff.dbr',
            '\\skills\\monster skills\\defense\\trap_resists.dbr',
            '\\skills\\monster skills\\defense\\resist_undead.dbr',
            '\\skills\\monster skills\\defense\\resist_ghost.dbr',
            '\\skills\\monster skills\\defense_undeadresists.dbr',
            '\\skills\\boss skills\\boss_conversionimmunity.dbr',
            '\\skills\\boss skills\\hero_conversionimmunity.dbr',
        ]) + [
            # Breaking wheel has its skill three times for some reason:
            'data\\database\\records\\xpack\\skills\\scroll skills\\pets\\'
            'all_breakingwheel_bladeattack2.dbr',
            'data\\database\\records\\xpack\\skills\\scroll skills\\pets\\'
            'all_breakingwheel_bladeattack3.dbr',
        ]

    PROJECTILES = 'projectileLaunchNumber'

    def __init__(self):
        super().__init__()

    @staticmethod
    def get_template_path():
        return [
            f'{TQDBParser.base}\\templatebase\\monsterskillmanager.tpl',
            # For some reason the doppel summon template does not extend the
            # regular monsterskillmanager, but has its own:
            f'{TQDBParser.base}\\templatebase\\doppelskillmanager.tpl',
        ]

    def parse(self, dbr, dbr_file, result):
        """
        Parse all the abilities a monster has.

        """
        # Initialize the abilities (to be indexed per level)
        abilities = []

        # Parse all the normal skills (17 max):
        for i in range(1, 18):
            nameTag = f'skillName{i}'
            levelTag = f'skillLevel{i}'

            # Skip unset skills or skills that are to be ignored:
            if (nameTag not in dbr or levelTag not in dbr or
                    str(dbr[nameTag]).lower() in self.IGNORE_SKILLS):
                continue

            skill = DBRParser.parse(dbr[nameTag])
            if not skill['properties']:
                continue

            # Store the skill, which will ensure a unique tag:
            skill_tag = storage.store_skill(skill)

            # Iterate over the difficulties:
            for difficulty in range(3):
                itr = TQDBParser.extract_values(dbr, 'skill', difficulty)

                # If a level is set to 0 for a difficulty, it won't be in the
                # extracted result, so use the KeyError safe 'get' method:
                level = itr.get(levelTag, 0)

                if not level:
                    continue

                if len(abilities) - 1 < difficulty:
                    # Create missing tiers:
                    abilities += ([{}] * (difficulty - len(abilities) + 1))

                abilities[difficulty][skill_tag] = level

        result['abilities'] = abilities
