# Developer commands. Everything that executes code runs inside the dev
# container; see docs/build-pipeline.md. Run `just` to list recipes.

set shell := ["bash", "-euo", "pipefail", "-c"]

compose := "docker compose"
run := compose + " run --rm dev"

# List recipes
default:
    @just --list

# Build the dev image (rerun after a Dockerfile or lockfile change)
build:
    {{compose}} build

# Rust and Python test suites
test: test-rust test-python

# Rust tests only
test-rust:
    {{run}} cargo test --locked

# Python tests only
test-python:
    {{run}} uv run --frozen pytest

# Clippy with warnings as errors, rustfmt check, then black check
lint:
    {{run}} cargo clippy --locked --all-targets -- -D warnings
    {{run}} cargo fmt --check
    {{run}} uv run --frozen black --check .

# Build tqextract in release mode
extractor:
    {{run}} cargo build --release --locked

# Extract the game install at game/ into the data volume
extract: extractor
    {{run}} ./target/release/tqextract prepare /game /data

# Parse one locale into output/ (default: en)
parse locale="en":
    {{run}} uv run --frozen python run.py --locale {{locale}}

# Parse all twelve locales into output/
parse-all:
    {{run}} uv run --frozen python run.py --all-languages

# Interactive shell in the dev container
shell:
    {{compose}} run --rm dev bash

# Regenerate Cargo.lock and uv.lock from the manifests, then rebuild the image
lock:
    docker build --target base -t tqdb-base .
    docker run --rm -v "{{justfile_directory()}}:/work" -w /work tqdb-base \
        sh -c "uv lock && cargo generate-lockfile"
    {{compose}} build

# Remove containers and the cargo cache volume; keeps the extracted game data
clean:
    {{compose}} down
    docker volume rm -f tqdb_target

# Remove the extracted game data volume; run `just extract` again afterwards
clean-data:
    docker volume rm -f tqdb_data
