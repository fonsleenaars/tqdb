# TQDB

Parser that turns Titan Quest Anniversary Edition game data (ARZ database, ARC archives, TEX textures) into one JSON file per locale plus a sprite sheet. The React site at [tq-db.net](https://tq-db.net) consumes that output verbatim.

This file holds only what is specific to this project and true right now.

## Documentation Map

- `docs/architecture.md` — how the Python pipeline works, end to end, and the game-data defects it works around
- `docs/game-formats.md` — DBR, TPL, ARZ, ARC, TEX formats and the localized text resources
- `docs/data-contract.md` — the JSON and sprite output the website depends on
- `docs/setup.md` — host setup, game data, input `data/` layout
- `docs/build-pipeline.md` — container image, version pins, update policy, verification ladder

Bugs and feature requests are tracked as GitHub issues on this repository.

Read `docs/architecture.md` and `docs/data-contract.md` before changing any parser. Read `docs/game-formats.md` before touching extraction.

## Layout

- `justfile`, `compose.yaml`, `Dockerfile` — the dev container; `just` lists the commands
- `rust-toolchain.toml`, `.python-version`, `Cargo.lock`, `uv.lock` — the version pins
- `extract/` — the `tqextract` Rust crate: `arz`, `arc`, `tex` readers and `prepare`, which builds the whole `data/` tree
- `run.py` — Python parser entry point
- `tqdb/main.py` — the six top-level collectors (affixes, creatures, equipment, quests, sets, skills)
- `tqdb/dbr.py`, `tqdb/templates.py`, `tqdb/storage.py` — record reader, template registry, global caches
- `tqdb/parsers/` — one `TQDBParser` subclass per game template; `base.py` holds the property formatters
- `tqdb/utils/text.py` — localized text loading and format-string conversion; `images.py` — TEX to PNG and sprite sheet
- `tqdb/constants/` — input globs and the hand-maintained boss-chest table
- `game/`, `data/`, `output/` — gitignored game content; `data/` is a Docker volume, not a host directory

## Hard Rules

- **Never commit game data.** Anything extracted from the game stays gitignored unless a decision in `docs/` says otherwise.
- **The website contract is frozen.** Property keys, the pre-formatted property strings, the six top-level JSON keys, the 19 equipment categories, the positional difficulty arrays, and the sprite CSS class names are all consumed by the site. Changing any of them is a website change too. `docs/data-contract.md` is the authority.
- **Game-data quirks are documented, not silently patched.** A workaround for a defect in the game files gets a comment naming the record and the symptom, and an entry in the game-data workarounds list in `docs/architecture.md`.
- **Localization goes through `texts.get`.** No English strings in parser output except where the game itself has none.
- **New code is path-portable.** Use `pathlib`, forward slashes, and lowercase game paths on both sides of every lookup.

## Working On This Project

- **Code executes in the container, never on the host.** `just test`, `just lint`, `just parse`, or `docker compose run --rm dev <cmd>`. The host has no Rust, Python, or uv. Edit on the host; run in the container.
- Always pass `--locked` to cargo and `--frozen` to uv, as the justfile does. Lockfiles change only via `just lock`, in their own commit.
- Run everything from the repo root. All input and output paths are relative to it.
- The full pipeline needs roughly 2 GB of extracted game data and several minutes per locale. Prefer targeted checks on single records over full runs while iterating.
- Parser version is `tqdb/__init__.py:__version__` and `pyproject.toml`, and appears in the output filename. Bump both in one commit.
