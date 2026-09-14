# Setup and input data

## Toolchain

Host requirements: Colima with the docker CLI and `just` (`brew install just`). Nothing else. Rust, Python, and uv live in the container image; `docs/build-pipeline.md` explains the pins.

```sh
colima start          # once per session
just build            # builds the dev image; rerun after Dockerfile or lockfile changes
just                  # lists every recipe
just test             # cargo test + pytest, no game data needed
```

## Game data

The game install is copied to `game/` (gitignored) and mounted read-only into the container at `/game`. It stays there permanently as the source for extraction. It, `data/`, and `output/` are never committed.

Only four folders of the install are read: `Database`, `Toolset`, `Text`, and `Resources`. Copying just those (about 1 GB) is enough.

```sh
just extract          # game/ → the tqdb_data volume at /data; about two minutes, 3.6 GB
```

`just extract` runs `tqextract prepare /game /data`. Add `--dry-run` through compose to see the plan without writing:

```sh
docker compose run --rm dev tqextract prepare /game /data --dry-run
```

Lookups in `game/` are case-insensitive, so a copy that arrived with different casing still works. Every path written under `/data` is lowercase.

## Data layout

```
data/
  database/
    records/**/*.dbr          Database/database.arz, 74,013 records
    templates/**/*.tpl        Toolset/Templates.arc
  resources/<locale>/*.txt    Text/Text_XX.arc; 13 locales: br cs de en es fr it ja ko pl ru uk zh
  quests/*.qst                Resources/Quests.arc and XPack{,2,3,4}/Quests.arc, flattened together
  textures/
    items/                    Resources/Items.arc
    xpack/items/              Resources/XPack/Items.arc
    xpack2/items/             Resources/XPack2/Items.arc
    xpack3/items/             Resources/XPack3/Items.arc
    xpack4/item/              Resources/XPack4/Item.arc (singular, in the game files)
```

Every `.tex` has a `.png` beside it, converted during extraction.

Locale codes come from the archive suffix: `Text_CH.arc` is `zh`, `Text_CZ.arc` is `cs`, `Text_JA.arc` is `ja`, `Text_BR.arc` is `br`; the rest map to their lowercase suffix.

Notes:

- Base-game creatures live under `records/creature/`, expansions under `records/xpack*/creatures/` (plural).
- Set folders differ per expansion: `xpack/item/sets`, `xpack2/item/sets`, `xpack3/items/set`, `xpack4/item/sets`.
- The game's own data has known defects the parser works around, listed in `architecture.md`.

## Regression baseline

The website's history holds the output of parser 1.4.5 against game v2.10.21415 (twelve data files and the sprite, committed May 2023). It is the only complete known-good output available, since this repo's last release commit is parser 1.4.3 and no `output/` is preserved anywhere else.
