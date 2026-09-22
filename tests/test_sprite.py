"""
Sprite CSS selectors. A formula's icon is named by its localized
classification, which can contain a space ("lesser artifact"). The site puts
that string in the class attribute, so the element carries one class per
word, and the selector has to require all of them.

"""

from PIL import Image

from tqdb.constants import paths
from tqdb.utils.images import SpriteCreator


def test_formula_selector_matches_each_word(monkeypatch, tmp_path):
    monkeypatch.setattr(paths, "OUTPUT", tmp_path)
    monkeypatch.setattr(paths, "GRAPHICS", tmp_path / "graphics")
    paths.GRAPHICS.mkdir()
    for name in ["lesser artifact", "tagring"]:
        Image.new("RGBA", (32, 32)).save(paths.GRAPHICS / f"{name}.png")

    SpriteCreator()

    selectors = [line for line in (tmp_path / "sprite.css").read_text().splitlines() if line.endswith("{")]
    assert selectors == [".lesser.artifact {", ".tagring {"]
