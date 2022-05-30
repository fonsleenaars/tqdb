"""
All loot table parsers.

"""
import logging
import numexpr
import os
import re

from tqdb import dbr as DBRParser
from tqdb.parsers.main import TQDBParser, InvalidItemError
from tqdb.utils.text import texts


class LootRandomizerParser(TQDBParser):
    """
    Parser for `lootrandomizer.tpl`.

    """

    def __init__(self):
        super().__init__()

    @staticmethod
    def get_template_path():
        return f"{TQDBParser.base}\\lootrandomizer.tpl"

    def parse(self, dbr, dbr_file, result):
        if "lootRandomizerName" in dbr:
            result["tag"] = dbr["lootRandomizerName"]
            # Some names had inline comments, so strip the spaces:
            result["name"] = texts.get(result["tag"]).strip()
            # Add the level requirement:
            result["levelRequirement"] = dbr["levelRequirement"]


class LootRandomizerTableParser(TQDBParser):
    """
    Parser for `lootrandomizertable.tpl`.

    """

    def __init__(self):
        super().__init__()

    @staticmethod
    def get_template_path():
        return f"{TQDBParser.base}\\lootrandomizertable.tpl"

    def parse(self, dbr, dbr_file, result):
        tables = {}
        weights = {}

        # Initialize the results table:
        result["table"] = []

        # Parse all available entries
        for field, value in dbr.items():
            if field.startswith("randomizerName"):
                # Grab the number suffix (1-70)
                number = re.search(r"\d+", field).group()
                # Store the DBR reference in the table
                tables[number] = value
            if field.startswith("randomizerWeight"):
                # Grab the number suffix (1-70)
                number = re.search(r"\d+", field).group()
                # Store the weight reference in the table
                weights[number] = value

        # Add all the weights together to determined % later
        total_weight = sum(weights.values())
        for key, randomizer_file in tables.items():
            # Skip entries without chance or without a file
            if key not in weights or not os.path.exists(randomizer_file):
                continue

            # Parse the table entry
            randomizer = DBRParser.parse(randomizer_file)

            # Append the parsed bonus with its chance:
            result["table"].append(
                {
                    "chance": float("{0:.2f}".format((weights[key] / total_weight) * 100)),
                    "option": randomizer["properties"],
                }
            )


class LootMasterTableParser(TQDBParser):
    """
    Parser for `lootmastertable.tpl`.

    """

    def __init__(self):
        super().__init__()

    @staticmethod
    def get_template_path():
        return f"{TQDBParser.base}\\lootmastertable.tpl"

    def parse(self, dbr, dbr_file, result):
        items = {}

        # Add up all the loot weights:
        summed = sum(v for k, v in dbr.items() if k.startswith("lootWeight"))

        # Run through all the loot entries and parse them:
        for i in range(1, 31):
            weight = dbr.get(f"lootWeight{i}", 0)

            # Skip items with no chance:
            if not weight:
                continue

            chance = float("{0:.5f}".format(weight / summed))

            try:
                # Try to parse the referenced loot file
                loot_file = dbr[f"lootName{i}"]
            except KeyError:
                logging.debug(f"No lootName{i} not found in {dbr_file}.")
                continue

            # Parse the loot file
            try:
                loot = DBRParser.parse(
                    loot_file,
                    # Always pass along any references that were set:
                    result["references"],
                )
            except InvalidItemError as e:
                logging.debug(f"Invalid lootName{i} in {loot_file} referenced by {dbr_file}.")
                continue

            # e.g. xpack2\quests\rewards\loottables\generic_rareweapon_n.dbr
            # The entry lootName15 has two entries separated by ';'
            if "loot_table" not in loot:
                logging.debug(f"Invalid lootName{i} in {dbr_file}.")
                continue

            # Loot entries will be in 'table', add those:
            for k, v in loot["loot_table"].items():
                if k in items:
                    items[k] += v * chance
                else:
                    items[k] = v * chance

        # Add the parsed loot table
        result["loot_table"] = items


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
        return f"{TQDBParser.base}\\fixeditemcontainer.tpl"

    def parse(self, dbr, dbr_file, result):
        if "tables" not in dbr:
            logging.debug(f"No table found in {dbr_file}")
            raise InvalidItemError(f"No table found in {dbr_file}")

        # Parse the references 'tables' file and set the result:
        loot = DBRParser.parse(
            dbr["tables"][0],
            # Always pass along any references that were set:
            result["references"],
        )
        result["loot_table"] = loot["loot_table"]


class FixedItemLootParser(TQDBParser):
    """
    Parser for `fixeditemloot.tpl`.

    """

    def __init__(self):
        super().__init__()

    @staticmethod
    def get_template_path():
        return f"{TQDBParser.base}\\fixeditemloot.tpl"

    def parse(self, dbr, dbr_file, result):
        # Initialize a dictionary of item chances to add to:
        self.items = {}

        # This camelCased variable is required for the spawn equations:
        numberOfPlayers = 1  # noqa

        # Grab min/max equation for items that will spawn:
        max_spawn = numexpr.evaluate(dbr["numSpawnMaxEquation"]).item()
        min_spawn = numexpr.evaluate(dbr["numSpawnMinEquation"]).item()
        spawn_number = (min_spawn + max_spawn) / 2

        # There are 6 loot slots:
        for slot in range(1, 7):
            self.parse_loot(f"loot{slot}", spawn_number, dbr, result)

        result["loot_table"] = self.items

    def parse_loot(self, loot_key, spawn_number, dbr, result):
        chance = dbr.get(f"{loot_key}Chance", 0)

        # Skip slots that have 0 chance to drop
        if not chance:
            return

        # Add up all the loot weights:
        summed = sum(v for k, v in dbr.items() if k.startswith(f"{loot_key}Weight"))

        # Run through all the loot possibilities and parse them:
        for i in range(1, 7):
            weight = dbr.get(f"{loot_key}Weight{i}", 0)

            # Skip items with no chance:
            if not weight:
                continue

            try:
                loot = DBRParser.parse(
                    dbr[f"{loot_key}Name{i}"][0],
                    # Always pass along any references that were set:
                    result["references"],
                )

                # Parse the table and multiply the values by the chance:
                loot_chance = float("{0:.5f}".format(weight / summed))
                new_items = dict((k, v * loot_chance * chance * spawn_number) for k, v in loot["loot_table"].items())
            except (KeyError, InvalidItemError):
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
        return f"{TQDBParser.base}\\lootitemtable_dynweight.tpl"

    def parse(self, dbr, dbr_file, result):
        if "level" in result["references"]:
            # This camelCased variable is required for the level equations.
            # Grab the level from the references which has been passed:
            averagePlayerLevel = result["references"]["level"]  # noqa
            parentLevel = result["references"]["level"]  # noqa

        # Calculate the minimum and maximum levels:
        try:
            min_level = numexpr.evaluate(dbr["minItemLevelEquation"]).item()
            max_level = numexpr.evaluate(dbr["maxItemLevelEquation"]).item()
            target_level = numexpr.evaluate(dbr["targetLevelEquation"]).item()
        except KeyError:
            # Log the missing variable:
            logging.info(f"Missing parentLevel in {dbr_file}")
            return

        # Grab the slope and defaultWeight, to use for adjusting values later:
        slope = dbr["bellSlope"]
        weight = dbr["defaultWeight"]

        # Store the drop and their adjusted weights in this dictionary:
        drops = {}

        for index, loot_file in enumerate(dbr.get("itemNames", [])):
            # Grab the item and its chance
            try:
                item = DBRParser.parse(loot_file)
            except InvalidItemError as e:
                logging.debug(f"Invalid loot file {loot_file} in {dbr_file}. {e}")
                continue

            if "tag" not in item:
                logging.debug(f"No tag for {loot_file} in {dbr_file}")
                continue

            level = item["itemLevel"]

            # Skip all items outside the range
            if level is None or level < min_level or level > max_level:
                continue

            # Next compare the item's level to the target level
            target = int(level - target_level)

            # Grab the adjustment from the slope (or the last one)
            adjustment = slope[target] if len(slope) > target else slope[-1]

            # The adjusted weight is the default multiplied by the adjustment:
            drops[item["tag"]] = weight * adjustment

        # The sum of all weights can now be calculated
        summed = sum(v for v in drops.values())

        # Store the chance of this item by its tag:
        result["loot_table"] = {
            tag: float("{0:.5f}".format(item_weight / summed)) for tag, item_weight in drops.items()
        }


class LootItemTable_FixedWeightParser(TQDBParser):
    """
    Parser for `lootitemtable_fixedweight.tpl`.

    """

    def __init__(self):
        super().__init__()

    @staticmethod
    def get_template_path():
        return f"{TQDBParser.base}\\lootitemtable_fixedweight.tpl"

    def parse(self, dbr, dbr_file, result):
        items = {}

        # Add up all the loot weights:
        summed = sum(v for k, v in dbr.items() if k.startswith("lootWeight"))

        # Run through all the loot chances and parse them:
        for i in range(1, 31):
            weight = dbr.get(f"lootWeight{i}", 0)

            # Skip items with no chance:
            if not weight:
                continue

            try:
                # Grab the item and its chance
                item = DBRParser.parse(dbr[f"lootName{i}"])
                # Store the chance of this item by its tag:
                items[item["tag"]] = float("{0:.5f}".format(weight / summed))
            except (KeyError, InvalidItemError):
                # Skip items that have no tag:
                continue

        result["loot_table"] = items
