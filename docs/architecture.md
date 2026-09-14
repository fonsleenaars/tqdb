# Architecture (current Python parser)

Describes the pipeline as it exists at parser version 1.4.3 (last code commit June 2022). Source references are `file:line`.

## Pipeline

```
game install ──ArchiveTool.exe / ARZExtractor.exe──▶ data/            (manual, Windows)
data/ ──run.py──▶ output/tqdb.<locale>.<version>.json + sprite.png + sprite.css
output/ ──the website's import──▶ tq-db.net
```

`run.py` is the entry point. Flags: `--locale` (default `en`), `--all-languages`, `--debug`. The `--force` flag is dead code (its consumer is commented out, `run.py:132`).

Per locale, `tqdb_language()` (`run.py:20`) does:

1. `texts.load_locale(locale)` — loads and normalizes every text resource for that locale into a module-level singleton.
2. Calls the six collectors in `tqdb/main.py` in this order: `parse_affixes`, `parse_creatures`, `parse_equipment`, `parse_quests`, `parse_sets`, `parse_skills`. Order matters: skills are never enumerated from disk, they are discovered transitively while parsing items and monsters, so `parse_skills` must run last.
3. Writes `output/tqdb.<locale>.<version>.json` with `sort_keys=True`.

With `--all-languages` the whole database is parsed once per locale (12 times) because formatting is fused into parsing. `storage.reset()` runs between locales; the sprite sheet is built once at the end.

## Record reading: `tqdb/dbr.py`

`read(dbr_file)` parses a DBR text file (`key,value,` lines, arrays `;`-separated) into a dict, typed and filtered by the record's template. Rules:

- Template resolution: `templateName` (path) first, else `Class` name, else error (`dbr.py:21`).
- Only keys declared in the template survive. Values are coerced by `Variable.parse_value`.
- **Falsy values are dropped** (`dbr.py:84`): `0`, `False`, `""`, `[]` never reach a parser. Parsers cannot distinguish "absent" from "zero".
- Arrays with exactly one element are filtered for falsy values; arrays with more than one keep everything (`templates.py:79`). The two cases behave differently.

`parse(dbr_file, references=None)` is the dispatcher every parser recurses through:

1. Memoized in `storage.db` keyed by the path as passed (`Path` or `str`; the same file can be parsed twice under two spellings).
2. Seeds `result = {"properties": {}, "references": references}`. `references` is a side channel (currently only `{"level": n}`) that loot parsers read. It is **not** part of the cache key, so a loot table parsed at one level is reused for every later caller.
3. Collects the parser registered for the record's template plus one for every template it includes, sorts by priority (3 highest, 1 lowest), runs each `parse(dbr, dbr_file, result)` in turn.
4. Any `InvalidItemError` aborts the record and is re-raised with cause chain.

## Templates: `tqdb/templates.py`

`.tpl` files from `data/database/templates/**` are loaded **at import time** (`templates.py:276`). Importing any parser module therefore requires the extracted game data on disk. Two registries: by path (`templates_by_path`) and by `Class` name (`templates`).

Parsing is line-oriented with regex preprocessing and manual brace counting, not a grammar. A template's `include` variables define inheritance: the included template's non-static variables are merged in and its path is appended to `template.templates`, which drives parser dispatch.

Keys are the template path relative to the data root, lowercase with forward slashes (`templates.py:152`), and every parser declares its template the same way (`parsers/main.py:36`). Every path read from the game files (`templateName`, `include` values, `file_dbr` and `file_tex` variables) is Windows-style with mixed case; `templates.game_path` normalizes it to the extracted tree, which `tqextract prepare` writes entirely in lowercase. The data root itself comes from the `TQDB_DATA` environment variable (`constants/paths.py`), `/data` in the container.

## Parser dispatch: `tqdb/parsers/main.py`

`TQDBParser` is the single abstract base. Each subclass declares `get_template_path()` (one path or a list) and `parse(dbr, dbr_file, result)`. `load_parsers()` discovers subclasses by importing every module in the package and reflecting on it, instantiating one singleton per class. Registration is a flat dict keyed by template path.

There are no lifecycle hooks. Ordering is expressed only through three priority constants:

| Priority | Who | Why |
|---|---|---|
| 3 (highest) | property-group parsers in `base.py`, `ItemSkillAugmentParser` | must fill `result["properties"]` before anything reads it |
| 2 (default) | most concrete parsers | |
| 1 (lowest) | `ItemEquipmentParser`, `ItemRelicParser`, `ItemSetParser`, `SkillBaseParser`, `MonsterParser` | need the finished property dict to re-tier it or count it |

Ties resolve by template include order, which is data, not code.

Shared helpers: `extract_values` (slice every array field at a tier index, repeating the last element), `highest_tier`, `insert_value` (the only mutation point for `result["properties"]`, auto-promotes scalar to list on a second write).

## Property formatting: `tqdb/parsers/base.py`

The heart of the project. Five parsers, one per `templatebase/parameters_*.tpl` group, each following the same shape:

```
for field in FIELDS present in dbr:
    for tier in extract_values(...):
        text = texts.get(field).format(value)      # localized template string
        text = chance_prefix + text + duration_suffix
        insert_value(field, text, result)
```

Output is a **localized display string keyed by the DBR variable name**, e.g. `"characterStrength": "+12 Strength"`. Multi-tier fields become lists of strings, which the relic, set, and skill parsers later re-interpret as piece counts, bonus tiers, or skill levels.

Groups:

- **Character** (45 fields): stats, speeds, requirement reductions. Also tries `{field}Modifier`.
- **Defensive** (37 fields): resistances and protections, with `{field}Chance` prefixes. Mutates the input dbr for `defensiveTotalSpeed` (`base.py:221`).
- **Offensive** (~80 fields, four kinds: flat, damage-over-time, effect-over-time, mana burn): the intricate one. Also silently handles `parameters_retaliation.tpl` and `parameters_weaponsbonusoffensive.tpl` because their variables land in the same dbr. Global chance groups (`offensiveGlobalChance`, `retaliationGlobalChance`) are the one structured output: `{"chance": "<formatted>", "properties": {...}}`. Keeps per-parse state on the singleton instance.
- **Skill** (3 fields): cooldown, mana cost, projectile speed.
- **Racial bonus** (4 fields): English-only pluralization hard-coded (`base.py:934`); emits a 2-D list that the relic parser special-cases.

Also here: `ItemSkillAugmentParser` (granted and augmented skills; decides skill vs mastery by substring-matching `"Mastery"` in the **localized** name, `base.py:349`) and `PetBonusParser`.

## Domain parsers

- **`equipment.py`**: artifacts, formulae, items, relics/charms, sets, scrolls, shields, weapons. Drops common items via a rarity whitelist. Derives drop difficulty from filename prefixes. Computes requirements with `numexpr` over the game's own cost equations, reading `itemLevel` and `totalAttCount` from the local frame (`equipment.py:286`). Relics spread properties over piece count, sets over bonus tiers.
- **`creatures.py`**: monsters as 3-element difficulty arrays (Normal, Epic, Legendary) for level, properties, abilities, equipped loot, and boss chest. Boss chests come from a 260-line hand-maintained table in `constants/resources.py`. Invokes the defensive parser manually, bypassing dispatch (`creatures.py:187`). A heuristic blanks earlier difficulties when `charLevel` repeats.
- **`loot.py`**: affix randomizer tables (weights to percentages), master tables (recursive, chances summed), fixed item loot (6 slots by 6 entries, scaled by mean spawn count), dynamic-weight tables (bell curve around a target level evaluated with `numexpr`). No cycle detection; termination relies on memoization and acyclic data. Chances across branches are summed, not combined probabilistically.
- **`skills.py`**: `SkillBaseParser` re-indexes properties by skill level (capped at `skillUltimateLevel`, `skillMaxLevel`, or 99). Buff and pet-modifier parsers replace the result wholesale with the referenced skill's. `SkillSpawnPetParser` emits `summons`.
- **`main.py` collectors**: `parse_quests` does not use the DBR machinery. It byte-scrapes `.qst` binaries with regexes (`main.py:283`); the reward regex covers `xpack`, `xpack2`, `xpack3` only, so Eternal Embers (`xpack4`) quest rewards are never found.

## Global state

Everything shares module-level mutable state. Nothing is injectable, and this is what blocks parallelism (the `TODO: add multithreading!` at `main.py:163`) and re-entrant multi-locale parsing.

| State | Where | Reset by `storage.reset()`? |
|---|---|---|
| `storage.db` (record memo cache) | `storage.py:5` | yes |
| `storage.skills` (skill registry with tag de-duplication) | `storage.py:6` | yes |
| `templates`, `templates_by_path` | `templates.py:11` | no, loaded at import |
| `dbr.parsers` (parser singletons) | `dbr.py:18` | no |
| `texts` (one locale at a time) | `utils/text.py:411` | no, mutated in place per locale |
| per-parse fields on `ParametersOffensiveParser` and `FixedItemLootParser` | `base.py:552`, `loot.py:198` | no |

Cached result dicts are handed out by reference and then mutated by callers (`category`, `bitmap`, `path`, `tag` are popped), so the cache contents drift during a run.

Because `references` is not part of the cache key, parse order is observable: a dynamic-weight loot table is cached at the level of the first creature that reaches it, and some tables raise on a level they were never meant for (`loot.py:312` indexes `bellSlope` with a negative offset). The output was produced on NTFS, which enumerates directories in case-insensitive name order, so every collector sorts its file list that way (`main.py:ordered`) instead of trusting the host filesystem's order.

## Text resources: `tqdb/utils/text.py`

`Texts.load_locale` reads 34 tag files and 5 UI-string files from `data/resources/<locale>/`, UTF-16 first then platform default. It then:

- strips `tag`/`xtag`/`x2tag` prefixes and adds aliases,
- renames game text keys into DBR variable names (`damageFire` to `offensiveFire`, `defense*` to `defensive*`, and so on),
- converts the game's `{%.0f0}` placeholders into Python `{0:.0f}`,
- hand-builds several composite strings (mana cost, active duration, radius) from locale-dependent pieces,
- repairs two known-broken game strings (`retaliationstun`, `damagetaunt`).

`texts.get(key)` falls back to the key itself when unknown, so unresolved tags leak into the JSON verbatim. Declension variants are de-duplicated through a `set`, so the joined order is non-deterministic across runs.

## Images: `tqdb/utils/images.py`

Per item, `save_bitmap` copies the `.png` that `tqextract prepare` wrote beside the item's `.tex` into `output/graphics/<tag>.png`. `SpriteCreator` packs the PNGs into a 768 px wide sheet with Pillow, writes `sprite.png` and `sprite.css`, then deletes `output/graphics`. CSS class names are the raw item tag, or the raw localized classification for formulae, which yields invalid selectors like `.lesser artifact`.

## Output layout

```
output/
  tqdb.<locale>.<version>.json   one per locale
  texts.<locale>.json            debug dump of the merged text table
  sprite.png, sprite.css         locale-independent
  graphics/                      transient, deleted after the sheet is built
```

The JSON shape is specified in `data-contract.md`.

## Tests

`tqdb/parsers/base_test.py` is the only test file. Its five tests check that every variable in a template is covered by the corresponding parser's field list. There are no functional tests, and the tests skip without the game data on disk because templates load at import.

## Game-data workarounds

Defects in the game's own files that the parser compensates for. They are facts about the data, not parser bugs; keep them when rewriting.

- `bosschest13_chimera_epic.dbr.dbr` has a double extension (`constants/resources.py:24`).
- `charcteritemglobalreduction` is misspelled in the game's text files (`utils/text.py:38`).
- `retaliationstun` lacks "second(s) of"; `damagetaunt` lacks its whole prefix (`utils/text.py:272`, `:287`).
- The Chinese locale lacks the `refreshtime` tag (`utils/text.py:55`).
- Greater Scroll of Svefnthorn references its Divine variant (`parsers/equipment.py:530`).
- The Tinkerer suffix `x3tagSuffix01` has no properties (`main.py:88`).
- Some set records are templates with no members (`parsers/equipment.py:436`). The Atlantis placeholder `xpack3/items/set/x3set(00).dbr` goes further: its only `setMembers` entry is the directory `records/xpack3/items/equipmentarmor/`, which `dbr.read` treats as a missing file (`dbr.py:60`).
- The Eternal Embers dungeon consumables in `records/item/hcdungeon/x4pot_*.dbr` use the `OneShot_Scroll` template but carry no difficulty in their file name; the scroll parser skips them like XP potions (`parsers/equipment.py:514`).
- The doppelganger summon template does not extend the monster template (`parsers/creatures.py:82`).
- Breaking Wheel lists its skill three times (`parsers/creatures.py:293`).
- Atlantis records point at `skilltree` paths that must be rewritten to `mastery` (`parsers/base.py:335`).
- Reagent DBR references are arrays of one (`parsers/equipment.py:105`).
- A `Placeholder` item exists in Atlantis data (filtered on the website).
- Spear of Nemetona has a nested `petBonus` (`parsers/base.py:876`).
- Skill tags are not unique across monster and player skills (`storage.py:34`).
- Expansions spell the `creatures` and `sets` folders differently (`constants/resources.py:282`, `:303`).
