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
from tqdb.dbr import parse, read, record
from tqdb.parsers.main import InvalidItemError
from tqdb.templates import game_path
from tqdb.utils import images
from tqdb.utils.text import texts
from tqdb.utils.core import get_affix_table_type


def ordered(files):
    """
    Sort a list of record paths case-insensitively.

    Parse order is observable: when several records share a tag (affix
    variants, multi-level bosses, skills) the first or last one parsed wins.
    The output was originally produced on NTFS, which enumerates directories
    in case-insensitive name order, so that order is reproduced here rather
    than whatever the host filesystem returns.

    """
    return sorted(files, key=lambda f: str(f).upper())


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

    # One variant per record, grouped by tag. Everything assembled here is a
    # new object: the cached parse result is read, never altered.
    variants = {"prefixes": defaultdict(list), "suffixes": defaultdict(list)}
    names = {}
    for dbr in affix_files:
        parsed = parse(dbr)
        tag = parsed["tag"]
        properties = parsed["properties"]

        # Tinkerer needs a little custom love because it has no properties, but a special text:
        if tag == "x3tagSuffix01":
            properties = {"description": texts.get("x3tagextrarelic")}

        # An affix that no table lists can occur on all equipment:
        equipment = affix_tables.get(dbr, {"none"})

        # Add affixes to their respective pre- or suffix list.
        if "Prefix" in tag and "suffix" not in dbr.parts:
            affix_type = "prefixes"
        else:
            affix_type = "suffixes"

        names[affix_type, tag] = parsed["name"]
        variants[affix_type][tag].append(
            {
                "record": record(dbr),
                "levelRequirement": parsed["levelRequirement"],
                "equipment": ",".join(sorted(equipment)),
                "properties": properties,
            }
        )

    affixes = {"prefixes": {}, "suffixes": {}}
    for affix_type, by_tag in variants.items():
        for tag, entries in by_tag.items():
            entries.sort(key=lambda variant: (variant["levelRequirement"], variant["record"]))
            equipment = set()
            for variant in entries:
                equipment.update(variant["equipment"].split(","))

            affixes[affix_type][tag] = {
                "name": names[affix_type, tag],
                "variants": entries,
                # The fields the site reads today are projections of the variants:
                "properties": [variant["properties"] for variant in entries],
                "levelRequirement": entries[0]["levelRequirement"],
                "equipment": ",".join(sorted(equipment)),
            }

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
    for dbr in ordered(files):
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


# The game ships its own development leftovers among the monsters, sharing
# tags with the real ones: superseded records under old/ (nine for Hades
# alone), QA monsters under zz_dev/ (a Pirate Captain with a 51-item test
# loot table, an Ancient of the Wild with "always drop" chances of 1000),
# records named *_old, the credits-scene actors (credits_hades.dbr, "Not in
# game - credits scene only"), test monsters and stunt doubles. Immortal
# Throne keeps its developer testers under zzdev/ (no underscore). Left in,
# they would be elected canonical or feed the loot union, so they are
# skipped before parsing. Each skipped record is logged at debug level.
DEVELOPMENT_DIRECTORIES = {"old", "zz_dev", "zzdev"}
DEVELOPMENT_NAMES = re.compile(r"_old$|^credits_|test|stuntdouble")

# Records whose tag names another monster. Scylla's three Atlantis records
# carry the Lernean Hydra's description tag, tagMonsterName126. Scylla spawns
# in all three difficulties and the Hydra only in Legendary, so by level
# Scylla would be the Hydra's canonical record, level, abilities and chest.
# The bones and chains in Typhon's arena are destructible props with his
# tag, tagMonsterName382, at a single level of 1 and 42; by level the bone
# pile would be Typhon. Excluded until a variant can carry a display name
# of its own.
SHARED_TAG_RECORDS = {
    "xpack3/creatures/monster/bosses/xboss_scylla_49",
    "xpack3/creatures/monster/bosses/xboss_scylla_52",
    "xpack3/creatures/monster/bosses/xboss_scylla_55",
    "creature/monster/questbosses/typhon_bones",
    "creature/monster/questbosses/typhon_chains",
}


def creature_exclusion(path):
    """
    Why a creature record stays out of the collection, or None to keep it.

    """
    identity = record(path)
    directories, _, name = identity.rpartition("/")

    if DEVELOPMENT_DIRECTORIES & set(directories.split("/")):
        return "development directory"
    if DEVELOPMENT_NAMES.search(name):
        return "development record name"
    if identity in SHARED_TAG_RECORDS:
        return "shares its tag with another monster"
    return None


def level_order(level):
    """
    Sort key for a creature record: Normal, Epic, Legendary level, with a
    difficulty the record does not spawn in (None) after any level.

    """
    return tuple((1, 0) if value is None else (0, value) for value in level)


def union_over_variants(variants, field):
    """
    The `loot` or `chest` difficulty arrays merged over a creature's
    variants: every item any variant lists in a difficulty, with the chance
    of the first variant, in variants order, that gives it a chance above
    zero. An item at zero in every variant keeps the first zero, which is
    the canonical's when the canonical lists it.

    The result is built from new dicts; the cached records are only read.

    """
    tiers = []
    for index in range(3):
        merged = {}
        for variant in variants:
            for item, chance in variant.get(field, [{}, {}, {}])[index].items():
                if item not in merged or (merged[item] == 0 and chance > 0):
                    merged[item] = chance
        tiers.append(merged)

    return tiers


def parse_creatures():
    """
    Parse all creatures (bosses and heroes) in Titan Quest.

    Parsing the bosses and heroes is mostly about parsing their loot tables
    to create an index of what they can drop. This index will work two ways,
    the first being a complete list of items that the monster can drop and the
    reverse being added to each individual item's loot table so it can be
    sorted.

    A monster is one entry per tag. Every record that carries the tag is a
    variant; the first by level, then by record, is canonical and supplies
    the scalar fields, level, properties and abilities, while loot and chest
    are the union over all variants (see docs/data-contract.md).

    """
    start_time = time.time()

    files = []
    for resource in resources.CREATURES:
        boss_files = paths.DB / resource
        files.extend(glob.glob(str(boss_files), recursive=True))

    logging.info(f"Found {len(files)} creature files.")

    # Every kept record by tag. Parse order still decides the suffix a
    # monster skill gets when its tag is already taken, so it stays sorted.
    by_tag = defaultdict(list)
    skipped = 0
    for dbr in ordered(files):
        reason = creature_exclusion(dbr)
        if reason:
            logging.debug(f"Skipping creature {record(dbr)}: {reason}.")
            skipped += 1
            continue

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

            by_tag[parsed["tag"]].append((record(dbr), parsed))
        except KeyError:
            # Skip creatures without tags
            logging.debug(f"Ignoring creature in {dbr}. No classification " "present.")
            continue

    logging.info(f"Skipped {skipped} development or shared-tag creature records.")

    creatures = {}
    for tag, entries in by_tag.items():
        entries.sort(key=lambda entry: (level_order(entry[1]["level"]), entry[0]))
        canonical = entries[0][1]

        creature = {
            field: canonical[field]
            for field in ("tag", "name", "race", "classification", "level", "properties", "abilities")
        }
        creature["variants"] = [{"record": identity, "level": parsed["level"]} for identity, parsed in entries]

        for field in ("loot", "chest"):
            union = union_over_variants([parsed for _, parsed in entries], field)
            if any(union):
                creature[field] = union

        creatures[tag] = creature

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
        r"(xpack[234]?[\\|/])?"
        "quests"
        r"[\\|/]"
        "rewards"
        r"[\\|/]"
        r"([^.]+)\.dbr"
        r")"
    )

    # Regex to find the title tag
    TITLE = re.compile(r"titletag(?P<tag>[^\s]*)")

    files = glob.glob(str(paths.DATA / resources.QUESTS))

    logging.info(f"Found {len(files)} quest files.")

    quests = {}
    for qst in ordered(files):
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

            # Prepend the path with the database path; the scraped path is
            # spelled Windows-style inside the quest file:
            try:
                rewards = parse(paths.DB / game_path(reward_file))
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
    for dbr in ordered(files):
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
