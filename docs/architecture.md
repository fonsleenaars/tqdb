# Architecture (current Python parser)

Describes the pipeline as it exists at parser version 1.5.1. Source references are `file:line`.

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
- **Falsy values are dropped** (`dbr.py:88`): `0`, `False`, `""`, `[]` never reach a parser. Parsers cannot distinguish "absent" from "zero".
- Arrays with exactly one element are filtered for falsy values; arrays with more than one keep everything (`templates.py:79`). The two cases behave differently.

`parse(dbr_file, references=None)` is the dispatcher every parser recurses through:

1. Memoized in `storage.db` keyed by the record identity together with the references. `dbr.record` produces the identity: the path under `database/records`, lowercase, forward slashes, one trailing `.dbr` removed. Every spelling of a path (`Path` from a game reference, `str` from glob, mixed case) is one entry. The same string is the `record` field in the output and the sort key of every "by record" ordering.
2. Seeds `result = {"properties": {}, "references": references}`. `references` is a side channel (currently only `{"level": n}`) that loot parsers read. Because it is part of the cache key, a loot table is evaluated once per level it is reached at.
3. Collects the parser registered for the record's template plus one for every template it includes, sorts by priority (3 highest, 1 lowest), runs each `parse(dbr, dbr_file, result)` in turn.
4. Any `InvalidItemError` aborts the record and is re-raised with cause chain.

## Templates: `tqdb/templates.py`

`.tpl` files from `database/templates/**` under the data root are loaded by an explicit `load_templates()` call, which `run.py` makes once before parsing. Importing the parser modules needs no game data; reading a record before the call raises. Reloading replaces both registries: by path (`templates_by_path`) and by `Class` name (`templates`).

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
  - Tier count per field: `max(len(Min), len(Modifier))`. For damage- and effect-over-time fields the flat version also reads `{field}DurationMin`, and `{field}DurationMax` where `DurationMin` is set (named exactly, not by prefix), past the last `Min` index for as long as their values keep changing: with `n = len(Min)`, a duration array `D` counts to `1 +` the last `i` in `n <= i < len(D)` where `D[i] != D[i-1]`. The game pads each array to the skill's or item's own count, while the parser counts tiers from the longest property list, so a constant tail (the act 1 batfang relics' `3;3;3;3;3;3` against five `Min` values) adds no tier. The modifier version keeps the plain count.
- **Skill** (3 fields): cooldown, mana cost, projectile speed.
- **Racial bonus** (4 fields): English-only pluralization hard-coded (`base.py:934`); emits a 2-D list that the relic parser special-cases.

Also here: `ItemSkillAugmentParser` (granted and augmented skills; decides skill vs mastery by substring-matching `"Mastery"` in the **localized** name, `base.py:349`) and `PetBonusParser`.

## Domain parsers

- **`equipment.py`**: artifacts, formulae, items, relics/charms, sets, scrolls, shields, weapons. Drops common items via a rarity whitelist. Derives drop difficulty from filename prefixes. Computes requirements with `numexpr` over the game's own cost equations, reading `itemLevel` and `totalAttCount` from the local frame (`equipment.py:286`); a nonzero requirement on the record itself wins per field, and the equations, from the record's `itemCostName` or else the engine's default `records/game/itemcost.dbr`, fill the rest. Relics spread properties over piece count, sets over bonus tiers.
- **`creatures.py`**: monsters as 3-element difficulty arrays (Normal, Epic, Legendary) for level, properties, abilities, equipped loot, and boss chest. Boss chests come from a 260-line hand-maintained table in `constants/resources.py`. Invokes the defensive parser manually, bypassing dispatch (`creatures.py:187`). Per record, `normalize_level` pads a short `charLevel` by repeating its last value, turns `0` into `null`, and then applies the repeated-level heuristic (a repeated Normal level means the record spawns only from the last repeat onwards) to arrays the game shipped with more than one value; a single value (the summoned pets) means that level in every difficulty, and reading its padding as a repetition would blank the properties the summon parser takes from index 0. A difficulty without a level gets `{}` for properties and abilities, and all three arrays always have three entries. Loot and chests are evaluated at the padded levels regardless, as they always were. The heuristic is part of what "spawns in this difficulty" means in the output.
- **`loot.py`**: affix randomizer tables (weights to percentages), master tables (recursive, chances summed), fixed item loot (6 slots by 6 entries, scaled by mean spawn count), dynamic-weight tables (bell curve around a target level evaluated with `numexpr`; an item whose offset from the target falls outside `bellSlope` takes the slope's last entry, and a negative offset within it indexes from the end). A dynamic-weight table has three evaluation contexts, told apart by the memo key: a numeric `level` in the references applies the bell slope; a `level` of `None` is level-neutral, which evaluates the item level bounds without a level and, when they are constants, gives every item within them `defaultWeight` and marks the result `levelNeutral` (a master table inherits the mark from any sub-table); no `level` at all yields nothing and logs, which is what the equipment and skill collectors get when they reach a dynamic table. No cycle detection; termination relies on memoization and acyclic data. Chances across branches are summed, not combined probabilistically.
- **`skills.py`**: `SkillBaseParser` re-indexes properties by skill level (capped at `skillUltimateLevel`, `skillMaxLevel`, or 99). Buff and pet-modifier parsers replace the result wholesale with the referenced skill's, then restore their own `path`: the wrapper is what a monster or item references, so its `record` is its own, and two wrappers of one buff are two skills with the same name and properties. `SkillSpawnPetParser` emits `summons`, one per spawn object. The game lists one spawn object per skill level with the lifetime array alongside, so the spawn index picks the lifetime; the spawn record's life and mana arrays are per difficulty, like any monster's, and every summon shows its Normal values.
- **`main.py` collectors**: `parse_quests` does not use the DBR machinery. It byte-scrapes `.qst` binaries with regexes (`main.py:283`). Only quests whose first `titleTag` is non-empty survive, which excludes every main quest. Rewards are parsed level-neutral (`{"level": None}`): a quest reward is rolled at the player's level when the quest is turned in and the output has one chance per difficulty, so a dynamic-weight table weighs its whole pool uniformly and the quest carries `levelNeutral[d]` to say so. `parse_skills` turns the registry in `storage.skills` into the output: each skill's `path`, kept for tag de-duplication, becomes its `record`.

## Global state

Everything shares module-level mutable state. Nothing is injectable, and this is what blocks parallelism (the `TODO: add multithreading!` at `main.py:163`) and re-entrant multi-locale parsing.

| State | Where | Reset by `storage.reset()`? |
|---|---|---|
| `storage.db` (record memo cache) | `storage.py:5` | yes |
| `storage.skills`, `storage.skill_tags` (skill registry with tag de-duplication, and the tag each stored record got) | `storage.py:6` | yes |
| `templates`, `templates_by_path` | `templates.py:11` | no, filled by `load_templates()` |
| `dbr.parsers` (parser singletons) | `dbr.py:18` | no |
| `texts` (one locale at a time) | `utils/text.py:411` | no, mutated in place per locale |
| per-parse fields on `ParametersOffensiveParser` | `base.py:552` | no |

Cached result dicts are handed out by reference and then mutated by callers (`category` and `bitmap` are popped, `store_skill` rewrites `tag`), so the cache contents drift during a run. Now that every spelling of a path shares one cache entry, a parser that rewrites what it gets back must copy first: the affix collector builds its output from new objects, and the summon-skill parser copies the spawn before replacing its `properties`, since the same record can be a creature in its own right and the summon of several skills (before the copy, each skill's summon showed the lifetime and health of whichever skill parsed the record last).

Parse order is observable wherever several records share a tag: skills take their scalar fields from the first or last record parsed, and a monster skill whose tag is already taken gets a numbered suffix in parse order (every skill also carries its `record`, which does not depend on it). The output was produced on NTFS, which enumerates directories in case-insensitive name order, so the collectors sort their file lists that way (`main.py:ordered`) instead of trusting the host filesystem's order. Affixes and creatures no longer depend on it for their content: `parse_affixes` emits one variant per record, ordered by `levelRequirement` and then by `record`, and derives the legacy `properties`, `levelRequirement` and `equipment` fields from that list; `parse_creatures` groups every kept record by tag into `variants`, ordered by Normal, Epic, Legendary level (`null` after any number) and then by `record`, takes the scalar fields, level, properties and abilities from the first, and builds `loot` and `chest` as unions over all of them (see `docs/data-contract.md`). Records under an `old`, `zz_dev` or `zzdev` directory, or named `*_old`, `credits_*`, `*test*` or `*stuntdouble*`, are skipped before parsing (`main.py:creature_exclusion`), as are the three records that carry another monster's tag.

## Text resources: `tqdb/utils/text.py`

`Texts.load_locale` reads 34 tag files and 5 UI-string files from `data/resources/<locale>/`, as UTF-16 when the file starts with a byte order mark and as UTF-8 otherwise. It then:

- strips `tag`/`xtag`/`x2tag` prefixes and adds aliases,
- renames game text keys into DBR variable names (`damageFire` to `offensiveFire`, `defense*` to `defensive*`, and so on),
- converts the game's `{%.0f0}` placeholders into Python `{0:.0f}`,
- hand-builds several composite strings (mana cost, active duration, radius) from locale-dependent pieces,
- repairs two known-broken game strings (`retaliationstun`, `damagetaunt`).

`texts.get(key)` falls back to the key itself when unknown, so unresolved tags leak into the JSON verbatim. Declension variants are de-duplicated in the order the game lists them and joined with commas.

## Images: `tqdb/utils/images.py`

Per item, `save_bitmap` copies the `.png` that `tqextract prepare` wrote beside the item's `.tex` into `output/graphics/<tag>.png`. `SpriteCreator` packs the PNGs into a 768 px wide sheet with Pillow, writes `sprite.png` and `sprite.css`, then deletes `output/graphics`. CSS class names are the raw item tag, or the localized classification for formulae with spaces written as `.`, a compound selector (`.lesser.artifact`) matching the one-class-per-word attribute the site sets. The sheet holds every locale's formula classifications.

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

Functional tests live under `tests/` and parse synthetic records from `tests/fixtures/data/`, a miniature of the extracted tree; `docs/build-pipeline.md` describes the layout. `tqdb/parsers/base_test.py` checks that every variable in the game's own templates is covered by the corresponding parser's field list, and skips when the data root has no templates. Parsers are registered by the template path they declare, so a fixture only needs the templates its records use.

## Game-data workarounds

Defects in the game's own files that the parser compensates for. They are facts about the data, not parser bugs; keep them when rewriting.

- `bosschest13_chimera_epic.dbr.dbr` has a double extension (`constants/resources.py:24`).
- A few records carry trailing whitespace in their values: the dev-test monsters in `xpack4/creatures/monster/zz_dev/` and the `FileDescription` of the cave-in skills. `dbr.read` strips every value (`dbr.py:60`), as the Windows extractor this project used to rely on did.
- `charcteritemglobalreduction` is misspelled in the game's text files (`utils/text.py:38`).
- Four Ragnarok text files in the English locale (`x2mainquest`, `x2sidequest`, `x2skills`, `x2tutorial`) are plain ASCII without the UTF-16 byte order mark every other text file has; the loader decides the encoding by the mark (`utils/text.py`).
- `retaliationstun` lacks "second(s) of"; `damagetaunt` lacks its whole prefix (`utils/text.py:272`, `:287`).
- The Chinese locale lacks the `refreshtime` tag (`utils/text.py:55`).
- Greater Scroll of Svefnthorn references its Divine variant (`parsers/equipment.py:530`).
- The Tinkerer suffix `x3tagSuffix01` has no properties (`main.py:88`).
- Some set records are templates with no members (`parsers/equipment.py:436`). The Atlantis placeholder `xpack3/items/set/x3set(00).dbr` goes further: its only `setMembers` entry is the directory `records/xpack3/items/equipmentarmor/`, which `dbr.read` treats as a missing file (`dbr.py:64`).
- The Eternal Embers dungeon consumables in `records/item/hcdungeon/x4pot_*.dbr` use the `OneShot_Scroll` template but carry no difficulty in their file name; the scroll parser skips them like XP potions (`parsers/equipment.py:514`).
- The doppelganger summon template does not extend the monster template (`parsers/creatures.py:82`).
- Breaking Wheel lists its skill three times (`parsers/creatures.py:293`).
- The monster folders ship development leftovers that share tags with real monsters: superseded records under `old/` (nine for Hades), QA monsters under `xpack4/creatures/monster/zz_dev/` (a Pirate Captain test monster with a 51-item loot table, `ancient_forest_48.dbr` with "always drop" chances of 1000), `*_old` records, the credits-scene actors (`credits_hades.dbr`, `credits_ringlesstree.dbr`), test monsters (`hades_test.dbr`) and `qs_sandwraith_stuntdouble.dbr`. Immortal Throne keeps its developer testers under `xpack/creatures/monster/zzdev/` (`xtagDevName01` to `18`), Ragnarok its under `xpack2/creatures/monster/zzz/`: developers named by their own tags (all Quest or Boss) and joke monsters (the Hero "Inhuman Centipede", Laser Raptor, Druoid), which would otherwise appear as monsters of their own. `parse_creatures` skips records under an `old`, `zz_dev`, `zzdev` or `zzz` directory or named `*_old`, `credits_*`, `*test*` or `*stuntdouble*` before parsing them, logging each at debug level (`main.py:creature_exclusion`). The tags that only such records carry disappear from the output with them.
- Scylla's three Atlantis records (`xpack3/creatures/monster/bosses/xboss_scylla_49/52/55.dbr`) carry the Lernean Hydra's tag `tagMonsterName126`. Scylla spawns in all three difficulties and the Hydra only in Legendary, so by level Scylla would become the Hydra's canonical record. The bones and chains in Typhon's arena (`creature/monster/questbosses/typhon_bones.dbr`, `typhon_chains.dbr`) are destructible props carrying his tag `tagMonsterName382` at a single level of 1 and 42, so by level the bone pile would become Typhon. These records are excluded by name (`main.py:SHARED_TAG_RECORDS`) until a variant can carry a display name of its own.
- The Eternal Embers bosses ship `charLevel,0;0;N`; `normalize_level` reads `0` as no spawn (`parsers/creatures.py`).
- Atlantis records point at `skilltree` paths that must be rewritten to `mastery` (`parsers/base.py:335`).
- Reagent DBR references are arrays of one (`parsers/equipment.py:105`).
- A `Placeholder` item exists in Atlantis data (filtered on the website).
- Spear of Nemetona has a nested `petBonus` (`parsers/base.py:876`).
- Skill tags are not unique across monster and player skills (`storage.py:34`).
- Expansions spell the `creatures` and `sets` folders differently (`constants/resources.py:282`, `:303`).
