"""
All resource constants.

"""

# Input files and directories
DB = 'data\\database-beta\\'
RES = 'data\\resources-beta\\'

EQUIPMENT = [
    'records\\item\\equipment*\\**\\*.dbr',
    'records\\xpack\\item\\equipment*\\**\\*.dbr',
    'records\\item\\relics\\*.dbr',
    'records\\item\\animalrelics\\*.dbr',
    'records\\xpack\\item\\relics\\*.dbr',
    'records\\xpack\\item\\le_new\\*.dbr',
    'records\\xpack\\item\\charms\\*.dbr',
    'records\\xpack\\item\\scrolls\\*.dbr',
    'records\\xpack\\item\\artifacts\\*.dbr',
    'records\\xpack\\item\\artifacts\\arcaneformulae\\*.dbr']

SKILLS = [
    # 'records\\skills\\defensive\\defensiveskilltree.dbr',
    # 'records\\skills\\earth\\earthskilltree.dbr',
    # 'records\\skills\\hunting\\huntingskilltree.dbr',
    # 'records\\skills\\nature\\natureskilltree.dbr',
    # 'records\\skills\\spirit\\spiritskilltree.dbr',
    # 'records\\skills\\stealth\\stealthskilltree.dbr',
    # 'records\\skills\\storm\\stormskilltree.dbr',
    # 'records\\skills\\warfare\\warfareskilltree.dbr',
    # 'records\\xpack\\skills\\dream\\dreamskilltree.dbr']
    'records\\skills\\**\\*.dbr',
    'records\\xpack\\skills\\**\\*.dbr']

STRINGS_TAGS = [
    'commonequipment.txt',
    'xcommonequipment.txt',
    'monsters.txt',
    'xmonsters.txt',
    'skills.txt',
    'xskills.txt',
    'uniqueequipment.txt',
    'xuniqueequipment.txt',
]

STRINGS_UI = [
    'ui.txt',
    'xui.txt'
]
