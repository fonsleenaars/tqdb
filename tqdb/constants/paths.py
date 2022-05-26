"""
Path constants

"""
from pathlib import Path

# Input files and directories
DATA = Path('data')
DB = DATA / 'database'
RES = DATA / 'resources'

OUTPUT = Path('output')
GRAPHICS = OUTPUT / 'graphics'
CACHE = OUTPUT / 'cache'
PARSING = OUTPUT / 'parsing'