# Development image for tqdb. Carries the pinned Rust and Python toolchains and
# every locked dependency, so the host needs nothing but Docker.
#
# Pins: Rust from rust-toolchain.toml (must match the base image tag),
#       Python from .python-version, uv below, base images by digest.
#
# Stages:
#   base   toolchains only; used to (re)generate lockfiles
#   dev    base + dependencies from Cargo.lock and uv.lock; the image compose uses

# --- base -------------------------------------------------------------------
FROM rust:1.98.1-slim-bookworm@sha256:ebd900bae66fd508b466cef82d64a83a5fb34682e4c8b2797a42908bddc95a57 AS base

COPY --from=ghcr.io/astral-sh/uv:0.12.13@sha256:b485bd65cc2cf1c9a93b3554012c9c3778cf7b1b5fd3d3096ce9e1226c97e1e6 \
     /uv /uvx /usr/local/bin/

ENV UV_PYTHON_INSTALL_DIR=/opt/uv/python \
    UV_PROJECT_ENVIRONMENT=/opt/venv \
    UV_LINK_MODE=copy \
    UV_COMPILE_BYTECODE=1 \
    PATH="/opt/venv/bin:${PATH}"

WORKDIR /work

# Interpreter version comes from .python-version, Rust components from
# rust-toolchain.toml (whose channel must equal the base image's version, so
# rustup adds components without downloading a second toolchain).
COPY .python-version rust-toolchain.toml ./
RUN uv python install \
 && rustup show active-toolchain \
 && rustup component add rustfmt clippy

# --- dev --------------------------------------------------------------------
FROM base AS dev

# Python dependencies, from the lockfile only. The project itself is not
# installed (package = false); it runs from the bind-mounted source.
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-install-project

# Rust dependencies, from the lockfile only. Manifests are enough for cargo
# fetch; sources arrive via the bind mount at run time.
COPY Cargo.toml Cargo.lock ./
COPY extract/Cargo.toml extract/Cargo.toml
RUN cargo fetch --locked

CMD ["bash"]
