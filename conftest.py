"""
Shared pytest fixtures.

Two data sources exist for tests:

- `fixture_data` points the parser at the synthetic tree under
  tests/fixtures/data. It mirrors the layout of the extracted game data
  (database/templates, database/records, resources/<locale>), but its
  templates, records and texts are written for the tests and hold no game
  content; it needs no game data at all.
- `game_templates` loads the real templates from the data root and skips
  the test when they are absent. Only the template coverage tests use it.

Both load into the module-level registries the parser keeps, so a test
declares exactly one of them.

"""

from pathlib import Path

import pytest

from tqdb import storage
from tqdb.constants import paths
from tqdb.templates import load_templates
from tqdb.utils.text import texts

FIXTURE_DATA = Path(__file__).parent / "tests" / "fixtures" / "data"


@pytest.fixture
def fixture_data(monkeypatch, tmp_path):
    """
    Point the parser at the synthetic data tree and load its templates and
    English texts. Returns the tree's root.

    """
    monkeypatch.setattr(paths, "DATA", FIXTURE_DATA)
    monkeypatch.setattr(paths, "DB", FIXTURE_DATA / "database")
    monkeypatch.setattr(paths, "RES", FIXTURE_DATA / "resources")
    # The text loader dumps its merged table next to the parser output:
    monkeypatch.setattr(paths, "OUTPUT", tmp_path)

    load_templates()
    texts.load_locale("en")
    storage.reset()

    return FIXTURE_DATA


@pytest.fixture
def game_templates():
    """
    Load the game's own templates from the data root, or skip.

    """
    if not (paths.DB / "templates").is_dir():
        pytest.skip("needs the extracted game templates under the data root")

    load_templates()
