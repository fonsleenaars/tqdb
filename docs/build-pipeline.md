# Build pipeline

How code is built, tested, and run, and how the pinned versions are kept current.

## Shape

Everything that executes code runs in one container image, `tqdb-dev`, under Colima. The host needs Colima, the docker CLI, and `just`. No Rust, Python, or uv on the host.

```
 host                                   container (Ubuntu, ext4)
 repo root         ── bind, rw ──▶   /work          source; output/ written here
 repo root/game    ── bind, ro ──▶   /game          raw game install, read once
 volume tqdb_data                     /data          extracted game data
 volume tqdb_target                   /work/target   cargo cache
```

`compose.yaml` declares the single `dev` service and both volumes. `justfile` wraps the invocations; `just` lists them.

Why each placement: source is small and edited on the host, so a bind mount is fine. The extracted tree is around 100k files read on every parse, so it lives on ext4 inside the VM, away from virtiofs and its case-insensitivity and stale-read issues. `target/` is a volume because Rust artifacts on virtiofs have known linker failures. Raw game files are a few dozen large files read sequentially once, fine over virtiofs. Output is a dozen files, written back through the source mount so the website's import script finds them unchanged.

Data flow: `game/` → `tqextract` → `/data` volume (persists across `colima stop`) → parser → `output/` → website import.

## Pins and where they live

| What | Pinned in | Consumed by |
|---|---|---|
| Rust toolchain | `rust-toolchain.toml` (channel) and the `rust:` base image tag in `Dockerfile` | both must agree; rustup adds components without downloading a second toolchain |
| Python interpreter | `.python-version` | `uv python install` in the image |
| uv | `Dockerfile` (`ghcr.io/astral-sh/uv` tag and digest) | copied into the image |
| Base image | `Dockerfile` (`rust:<ver>-slim-bookworm@sha256:…`) | digest-pinned; a mismatch fails the build loudly |
| Rust crates | `Cargo.lock` | `cargo fetch --locked` at build; `--locked` on every cargo invocation |
| Python packages | `uv.lock` | `uv sync --frozen` at build; `--frozen` on every uv invocation |
| `just` | Homebrew formula, unpinned | host only; a thin wrapper, any 1.x works |

Dependencies are baked into the image at build time. Changing a lockfile means `just build`.

## Regenerating lockfiles

`just lock` builds the toolchain-only `base` stage, runs `uv lock` and `cargo generate-lockfile` inside it against the bind-mounted manifests, then rebuilds `dev`. Never edit a lockfile by hand.

## Update policy

- **Rust**: track stable. Bump `rust-toolchain.toml` and the base image tag and digest together, in one commit, roughly every second stable release (12 weeks). Verification: `just build && just lint && just test`.
- **Python**: track the latest patch of the current minor. Move to a new minor within a month of the first patch release of it, when the three runtime dependencies publish wheels for it. Bump `.python-version`, run `just lock`. Verification: `just test` and a full `just parse` diffed against the previous output.
- **uv**: bump the tag and digest in `Dockerfile` with the Rust bump. Verification: `just build && just test-python`.
- **Base image digest**: refresh with the Rust bump. Verification: build succeeds.
- **Crates and Python packages**: `just lock` with the Rust bump; review the diff of both lockfiles before committing. Verification: `just lint && just test`, and for parser dependencies (Pillow, numpy, numexpr) a full `just parse` diffed against the previous output.
- **Bumps are their own commits.** Version change plus verification, no feature work.

There are no platform deadlines: the output is static JSON consumed by a website with its own pipeline.

## Verification ladder

1. `just lint` — clippy with warnings as errors, rustfmt.
2. `just test` — `cargo test` and `pytest` on synthetic fixtures. No game data needed. The Python tests come in two kinds:
   - **Fixture tests** under `tests/` parse hand-written records from `tests/fixtures/data/`, a miniature of the extracted tree: `database/templates/` (only the templates the records use, with only the variables the parsers read), `database/records/` (the records, at paths shaped like the game's so file-name rules apply), and `resources/en/` (the tags and format strings the records need, plus the composite strings the text loader requires in every locale). The `fixture_data` fixture in `conftest.py` points the parser at it, loads the templates and English texts, and clears the record cache. Nothing in it is copied from the game.
   - **Template coverage tests** in `tqdb/parsers/base_test.py` read the game's own templates through the `game_templates` fixture and skip when the data root has none.
3. `just extract` after any change to `extract/`: every step must report zero failures. `tqextract arc info` and `tex survey` verify checksums and decoding on a single archive or directory.
4. `just parse en` diffed against the previous output with the scripts in `tqdb/tools/`: `diffjson.py` writes a structural summary of two output files, `triage.py` classifies every leaf change, and `identical.py` parses a locale twice in separate processes and fails unless the files match byte for byte (set iteration order differs per process, so a single run cannot show it). Usage is in each docstring. Keep the last known-good output in `output/baseline/` (gitignored) as the reference. Needs the extracted data volume.
5. `just parse-all` before a release, triaged per locale against the baseline.

## Known gaps

- The Python parser keeps all state in module globals (`docs/architecture.md`, global state section). The template coverage tests in `tqdb/parsers/base_test.py` need the extracted data volume and skip without it.
- No CI. When added, it builds the same `Dockerfile` on `ubuntu-latest` and runs steps 1 and 2.
