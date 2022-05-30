"""
Main functions to parse the full Titan Quest Database.

"""
import glob
import logging
import os
import re
import string
import time
from collections import defaultdict

from pathlib import Path

from tqdb import storage
from tqdb.constants import resources, paths
from tqdb.dbr import parse, read
from tqdb.parsers.main import InvalidItemError
from tqdb.utils import images
from tqdb.utils.text import texts
from tqdb.utils.core import get_affix_table_type, is_duplicate_affix


def parse_affixes():
    """
    Parse all the Titan Quest affixes.

    Affixes are the pre- and suffixes that are applied to weapons.
    These affixes add properties to the equipment, these properties,
    the affix names and the equipment they can be applied to is
    indexed and parsed in this function.

    """
    start_time = time.time()

    files = []
    for resource in resources.AFFIX_TABLES:
        table_files = paths.DB / resource
        files.extend(glob.glob(str(table_files), recursive=True))

    logging.info(f"Found {len(files)} affix table files.")

    # The affix tables will determine what gear an affix can be applied to.
    affix_tables: dict[str, set] = {}
    affix_files: set[Path] = set()
    for dbr in files:
        table = read(dbr)

        # Use the filename to determine what equipment this table is for:
        file_name = os.path.basename(dbr).split("_")
        table_type = get_affix_table_type(file_name[0])

        # For each affix in this table, create an entry:
        for field, affix_dbr in table.items():
            if not field.startswith("randomizerName") or not affix_dbr.exists():
                continue

            # Add this file as discovered, this will determine what affixes are actually parsed
            affix_files.add(affix_dbr)

            if affix_dbr not in affix_tables:
                affix_tables[affix_dbr] = {table_type}
            elif table_type not in affix_tables[affix_dbr]:
                affix_tables[affix_dbr].add(table_type)

    logging.info(f"Found {len(affix_files)} affix files.")

    affixes = {"prefixes": {}, "suffixes": {}}
    for dbr in affix_files:
        affix = parse(dbr)

        # Tinkerer needs a little custom love because it has no properties, but a special text:
        if affix["tag"] == "x3tagSuffix01":
            affix["properties"] = {"description": texts.get("x3tagextrarelic")}

        # Assign the table types to this affix:
        if dbr not in affix_tables:
            # Affix can occur on all equipment:
            affix["equipment"] = {"none"}
        else:
            affix["equipment"] = affix_tables[dbr]

        # Add affixes to their respective pre- or suffix list.
        if "Prefix" in affix["tag"] and "suffix" not in dbr.parts:
            affixType = "prefixes"
        else:
            affixType = "suffixes"

        affixTag = affix.pop("tag")

        # Either add the affix or add its properties as an alternative
        if affixTag in affixes[affixType]:
            affix_result = affixes[affixType][affixTag]
            # Skip duplicate affix properties:
            if is_duplicate_affix(affix_result, affix):
                continue

            # Create a list if it wasn't already one
            if not isinstance(affix_result["properties"], list):
                affix_result["properties"] = [affix_result["properties"], affix["properties"]]
            else:
                affix_result["properties"].append(affix["properties"])
            affix_result["equipment"].update(affix["equipment"])
        else:
            # Make sure to copy here since we alter some properties after looping
            affixes[affixType][affixTag] = affix.copy()

    # Parse the equipment & properties one last time to standardize the formats
    for _, v in affixes.items():
        for _, affix in v.items():
            affix["equipment"] = ",".join(list(affix["equipment"]))
            affix["properties"] = (
                affix["properties"] if isinstance(affix["properties"], list) else [affix["properties"]]
            )

    # Log and reset the timer:
    logging.info(f"Parsed affixes in {time.time() - start_time:.2f} seconds.")

    return affixes


def parse_equipment():
    """
    Parse all wearable Titan Quest equipment.

    The wearable equipment is indexed and sorted by equipment type. These
    categories are defined by the Class property of each piece of equipment
    which is mapped to the 'category' key in the parsed result.

    :return: dictionary keyed by equipment category string, value is a list of
        dicts, one for each item in that category. Common items are omitted.

    """
    start_time = time.time()

    files = []
    for resource in resources.EQUIPMENT:
        for equipment_filename in paths.DB.glob(resource):
            if not (
                # Exclude all files in 'old' and 'default'
                "old" in equipment_filename.parts
                or "default" in equipment_filename.parts
            ):
                files.append(equipment_filename)

    logging.info(f"Found {len(files)} equipment files to process.")

    # TODO: add multithreading!

    items = defaultdict(list)
    for dbr in files:
        try:
            parsed = parse(dbr)
        except InvalidItemError as e:
            exception_messages = exception_messages_with_causes(e)

            logging.debug(f"Ignoring item in {dbr}. {exception_messages}")
            continue
        except Exception as e:
            logging.info(f"Error in {dbr}")
            logging.exception(e)
            continue

        try:
            # Skip items without a category
            if "category" not in parsed:
                continue

            # Organize the equipment based on its category
            category = parsed.pop("category")

            # Skip items without rarities
            if "classification" not in parsed:
                continue

            # Save the bitmap and remove the bitmap key
            images.save_bitmap(parsed, category, paths.GRAPHICS)
        except KeyError as e:
            # Skip equipment that couldn't be parsed:
            logging.warning(f"DBR {dbr} parse result unacceptable. Parse result: {parsed}. Error: {e}")
            # raise e
            continue

        # Pop off the properties key off any item without properties:
        if "properties" in parsed and not parsed["properties"]:
            parsed.pop("properties")

        # Now save the parsed item in the category:
        if category:
            items[category].append(parsed)

    # Log the timer:
    logging.info(f"Parsed equipment in {time.time() - start_time:.2f} seconds.")

    return items


def exception_messages_with_causes(e):
    exception_messages = [str(e)]
    while e.__cause__:
        e = e.__cause__
        exception_messages.append(str(e))
    return exception_messages


def parse_creatures():
    """
    Parse all creatures (bosses and heroes) in Titan Quest.

    Parsing the bosses and heroes is mostly about parsing their loot tables
    to create an index of what they can drop. This index will work two ways,
    the first being a complete list of items that the monster can drop and the
    reverse being added to each individual item's loot table so it can be
    sorted.

    """
    start_time = time.time()

    files = []
    for resource in resources.CREATURES:
        boss_files = paths.DB / resource
        files.extend(glob.glob(str(boss_files), recursive=True))

    logging.info(f"Found {len(files)} creature files.")

    creatures = {}
    for dbr in files:
        try:
            logging.debug(f"Attempting to parse creature in {dbr}.")
            parsed = parse(dbr)
        except InvalidItemError as e:
            logging.debug(f"Ignoring creature in {dbr}. {e}")
            continue

        try:
            # Don't include common monsters
            # XXX - Should 'Champion' be added?
            # Should this be moved to MonsterParser to save work? The equipment
            # parser does that.
            if parsed["classification"] not in ["Quest", "Hero", "Boss"]:
                continue

            # Store the monster by its tag:
            creatures[parsed["tag"]] = parsed
        except KeyError:
            # Skip creatures without tags
            logging.debug(f"Ignoring creature in {dbr}. No classification " "present.")
            continue

    # Log the timer:
    logging.info(f"Parsed creatures in {time.time() - start_time:.2f} seconds.")

    return creatures


def parse_quests():
    """
    Parse the Titan Quest quest rewards.

    The quest rewards are indexed by creating a text readable version of the
    QST files located in the Resources/Quests.arc file. The rewards are
    extracted by only retrieving rewards prefixed with item[] tags.

    """
    start_time = time.time()

    # Regex to find item rewards
    REWARD = re.compile(
        r"item\[(?P<index>[0-9])\](.{0,1})"
        r"(?P<file>"
        "records"
        r"[\\|/]"
        r"(xpack[2|3]?[\\|/])?"
        "quests"
        r"[\\|/]"
        "rewards"
        r"[\\|/]"
        r"([^.]+)\.dbr"
        r")"
    )

    # Regex to find the title tag
    TITLE = re.compile(r"titletag(?P<tag>[^\s]*)")

    files = glob.glob(resources.QUESTS)

    logging.info(f"Found {len(files)} quest files.")

    quests = {}
    for qst in files:
        with open(qst, "rb") as quest:
            # Read the content as printable characters only:
            content = "".join(
                c
                for c in
                # Lower case and convert to utf-8
                quest.read().decode("utf-8", errors="ignore").lower()
                if c in string.printable
            )

        # Find the title and skip this file if none is found:
        title_tag = TITLE.search(content)
        if not title_tag or not title_tag.group("tag"):
            continue

        # Grab the quest title tag
        tag = title_tag.group("tag")
        if tag not in quests:
            # Initialize three difficulties:
            quests[tag] = {
                "name": texts.get(tag),
                "rewards": [{}, {}, {}],
            }

        # Parsed reward files (so we don't duplicate):
        parsed = []

        # Add all the rewards to the quest:
        for match in REWARD.finditer(content):
            # The index in the item[index] tag determines the difficulty:
            difficulty = int(match.group("index"))
            reward_file = match.group("file")

            # Store the file or move on if we've already parsed it
            if reward_file not in parsed:
                parsed.append(reward_file)
            else:
                continue

            # Prepend the path with the database path:
            try:
                rewards = parse(paths.DB / reward_file)
            except InvalidItemError as e:
                messages = exception_messages_with_causes(e)
                logging.debug(f"Skipping quest reward {reward_file} of {qst}. {messages}")
                continue

            # Skip quests where the rewards aren't items:
            if "loot_table" not in rewards:
                continue

            # Either set the chance or add it to a previous chance:
            for item, chance in rewards["loot_table"].items():
                if item in quests[tag]["rewards"][difficulty]:
                    quests[tag]["rewards"][difficulty][item] += chance
                else:
                    quests[tag]["rewards"][difficulty][item] = chance

        # Don't save quests without item rewards:
        if not any(reward for reward in quests[tag]["rewards"]):
            quests.pop(tag)

    # Turn all chances into percentages:
    for tag, quest in quests.items():
        for index, difficulty in enumerate(quest["rewards"]):
            for item, chance in difficulty.items():
                # Format into 4 point precision percentages:
                quests[tag]["rewards"][index][item] = float("{0:.4f}".format(chance * 100))

    # Log the timer:
    logging.info(f"Parsed quest rewards in {time.time() - start_time:.2f} seconds.")

    return quests


def parse_sets():
    """
    Parse the Titan Quest equipment sets.

    The equipment sets are indexed and their properties are the set
    bonuses you receive for wearing multiple set pieces at once.

    """
    start_time = time.time()

    files = []
    for resource in resources.SETS:
        set_files = paths.DB / resource
        files.extend(glob.glob(str(set_files), recursive=True))

    sets = {}
    for dbr in files:
        try:
            parsed = parse(dbr)
        except InvalidItemError as e:
            exception_messages = exception_messages_with_causes(e)
            logging.debug(f"Ignoring item in {dbr}. {exception_messages}")
            continue

        try:
            # Add the set by its tag to the dictionary of sets:
            sets[parsed["tag"]] = parsed
        except KeyError:
            # Skip sets with no tag:
            continue

    # Log the timer:
    logging.info(f"Parsed sets in {time.time() - start_time:.2f} seconds.")

    return sets


def parse_skills():
    """
    Clean up the indexed skills during parsing.

    While parsing, all other functions will add to the skills variable in the
    storage module. This dictionary just needs to be cleaned up a little by
    removing the 'path' property of each skill, which was used during parsing
    but is no longer required for output.

    """
    skills = storage.skills.copy()
    for skill in skills.values():
        # Pop the 'path' property, it was used during parsing to ensure correct
        # skill tag references for requipment.
        skill.pop("path")

    return skills
