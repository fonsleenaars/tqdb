# TQDB
TQDB is a parser for the game data of Titan Quest Anniversary Edition. It turns the game's ARZ database, ARC archives, and TEX textures into one JSON file per locale plus a sprite sheet, which power the equipment database at [tq-db.net][tqdb].

## Titan Quest
Although the base game Titan Quest was released in 2006 and the expansion Immortal Throne in 2007, I, as many others kept playing it throughout the years. With the pick up by THQ Nordic there are changes being made to the database that are no longer reflected in the other databases that are still around (most notably [GameBanshee][gb]).

That, and a desire to create a smoother equipment database running on some more modern technologies, prompted me to start breaking down the ARZ and ARC files that make up the in-game content for Titan Quest.

The result is two files containing all in-game information:
  - A single JSON file (per locale) containing the data (equipment, sets, skills, boss loot, etc.)
  - A single sprite image along with a CSS sprite sheet containing all the graphics for the equipment available in the JSON file.

## Documentation

- [`docs/setup.md`](docs/setup.md) — host setup, game data, input layout
- [`docs/build-pipeline.md`](docs/build-pipeline.md) — the container image, version pins, update policy
- [`docs/architecture.md`](docs/architecture.md) — how the parser works
- [`docs/game-formats.md`](docs/game-formats.md) — DBR, TPL, ARZ, ARC, and TEX formats
- [`docs/data-contract.md`](docs/data-contract.md) — the JSON and sprite output the website depends on

## Setup

Everything runs in a container; the host needs Docker (Colima on macOS) and [`just`](https://github.com/casey/just). No Rust or Python is installed on the host.

1. Copy your Titan Quest Anniversary Edition install, or just its `Database`, `Toolset`, `Text`, and `Resources` folders, to `game/` in this repository. It is gitignored.
2. Build the image and run the tests:

   ```sh
   just build
   just test
   ```

3. Extract the game data. This reads `game/` and writes about 3.6 GB into a Docker volume:

   ```sh
   just extract
   ```

`just` on its own lists every command.

## Running the parser

```sh
just parse          # english
just parse fr       # any locale: br cs de en es fr it ja ko pl ru uk zh
just parse-all      # all locales, then the sprite sheet
```

Output lands in `output/`: `tqdb.<locale>.<version>.json`, `sprite.png`, and `sprite.css`.

## The extractor

`tqextract` (Rust, in `extract/`) replaces the Windows-only tools this project used to bundle. Besides `prepare`, which does the whole extraction, it can inspect and extract each format on its own:

```sh
docker compose run --rm dev tqextract arz info /game/Database/database.arz
docker compose run --rm dev tqextract arc info /game/Toolset/Templates.arc
docker compose run --rm dev tqextract tex survey /data/textures/items
```

## DBR records
Titan Quest works with so called DBR files (Database Records). These files are basically dictionaries of all properties of whatever the file is referencing. The file is comma separated, with the following formats:

```
key,value1;value2;value3,
key,value1,
key,value1
```

These values can thus easily be parsed into a usable dictionary or collection. The keys for these files are checked based on the Template used for the DBR file, which is defined in the `templateName` key, and indirectly in its `Class` key as well.

## Website
The React site at [tq-db.net][tqdb] wraps the parsed JSON with navigation, filtering, and search. Report issues you find on the website on this repository's issue tracker.

[gb]: <https://www.gamebanshee.com/titanquest/>
[tqdb]: <https://www.tq-db.net>
