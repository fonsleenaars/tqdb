import glob

from pprint import pprint

from tqdb.dbr import parse

files = glob.glob(
    'data\\database\\records\\item\\equipmentarmband\\u*.dbr',
    recursive=True)
for dbr in files:
    print(dbr)
    props = parse(dbr)
    pprint(props)
