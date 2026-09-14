"""
Path constants

"""
import os
from pathlib import Path

# Input files and directories. TQDB_DATA points at the extracted game data
# tree (the dev container mounts it at /data); it defaults to data/ in the
# working directory.
DATA = Path(os.environ.get("TQDB_DATA", "data"))
DB = DATA / "database"
RES = DATA / "resources"

OUTPUT = Path("output")
GRAPHICS = OUTPUT / "graphics"
CACHE = OUTPUT / "cache"
PARSING = OUTPUT / "parsing"
