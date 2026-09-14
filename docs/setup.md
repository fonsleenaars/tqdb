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

The raw game install is copied to `game/` (gitignored) and mounted read-only into the container. It stays there permanently as the source for extraction. It, `data/`, and `output/` are never committed.

**Today** extraction still requires the Windows tools described below; `tqextract` is a stub. Once it works, the whole step is:

```sh
just extract          # game/ → /data volume, several minutes
just parse en         # /data → output/tqdb.en.<version>.json
```

### Extraction with the original tools (Windows only)

1. `python prepare.py` on a Windows machine with the Steam install: reads the install path from the registry, creates the `data/` tree, runs the game's `ArchiveTool.exe <archive> -extract <dir>` for templates, the 13 text archives, quests, and item textures. Return codes are not checked.
2. Run `utils/arzextractor/ARZExtractor.exe` by hand (GUI only): source `Database/database.arz`, destination `data/database`.
3. Copy the resulting `data/` tree to this box and into the `tqdb_data` volume.

## Input layout the parser expects

```
data/
  database/
    records/**/*.dbr          from database.arz (~2 GB extracted)
    templates/**/*.tpl        from Toolset/Templates.arc
  resources/<locale>/*.txt    from Text/Text_XX.arc; Text_CH.arc lands in zh/
  quests/*.qst                Resources/Quests.arc and XPack{,2,3,4}/Quests.arc, flattened together
  textures/
    Items/                    Resources/Items.arc
    XPack/Items/              Resources/XPack/Items.arc
    XPack2/Items/             Resources/XPack2/Items.arc
    XPack3/Items/             Resources/XPack3/Items.arc
    XPack4/Item/              Resources/XPack4/Item.arc (singular, in the game files)
```

Notes:

- Base-game creatures live under `records/creature/`, expansions under `records/xpack*/creatures/` (plural).
- Set folders differ per expansion: `xpack/item/sets`, `xpack2/item/sets`, `xpack3/items/set`, `xpack4/item/sets`.
- `tqextract` writes every path lowercased, and the parser looks up lowercased paths, so filesystem case sensitivity never matters. The original tools preserved the game's mixed case.
- The game's own data has known defects the parser works around, listed in `architecture.md`.

## Regression baseline

The website's history holds the output of parser 1.4.5 against game v2.10.21415 (twelve data files and the sprite, committed May 2023). It is the only complete known-good output available, since this repo's last release commit is parser 1.4.3 and no `output/` is preserved anywhere else.
