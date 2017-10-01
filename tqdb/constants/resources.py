"""
All resource constants.

"""

# Input files and directories
DB = 'data\\database\\'
RES = 'data\\resources\\'
TEX = 'data\\textures\\'

AFFIXES = [
    'records\\item\\\lootmagicalaffixes\\*ix\\default\\*.dbr',
    'records\\xpack\\item\\\lootmagicalaffixes\\*ix\\default\\*.dbr',
    'records\\xpack\\item\\\lootmagicalaffixes\\*ix\\*.dbr']

AFFIX_TABLES = [
    'records\\item\\\lootmagicalaffixes\\*ix\\**\\*.dbr',
    'records\\xpack\\item\\\lootmagicalaffixes\\*ix\\**\\*.dbr']

CHESTS = {
    'chimaera': [
        'records\\item\\containers\\boss\\bosschest13_chimera_normal.dbr',
        # Chimera Epic has a double .dbr extension:
        'records\\item\\containers\\boss\\bosschest13_chimera_epic.dbr.dbr',
        'records\\item\\containers\\boss\\bosschest13_chimera_legendary.dbr'],
    'chinatelkine_ormenos': [
        'records\\item\\containers\\boss\\bosschest20_ormenos_normal.dbr',
        'records\\item\\containers\\boss\\bosschest20_ormenos_epic.dbr',
        'records\\item\\containers\\boss\\bosschest20_ormenos_legendary.dbr'],
    'cyclops_polyphemus': [
        'records\\item\\containers\\boss\\bosschest03_cyclops_normal.dbr',
        'records\\item\\containers\\boss\\bosschest03_cyclops_epic.dbr',
        'records\\item\\containers\\boss\\bosschest03_cyclops_legendary.dbr'],
    'daemonbull_yaoguai': [
        'records\\item\\containers\\boss\\bosschest19_yaoguai_normal.dbr',
        'records\\item\\containers\\boss\\bosschest19_yaoguai_epic.dbr',
        'records\\item\\containers\\boss\\bosschest19_yaoguai_legendary.dbr'],
    'dragonliche': [
        '',
        'records\\item\\containers\\boss\\bosschest24_dragonliche_epic.dbr',
        'records\\item\\containers\\boss\\'
        'bosschest24_dragonliche_legendary.dbr'],
    'egypttelkine_aktaios': [
        'records\\item\\containers\\boss\\bosschest11_aktaios_normal.dbr',
        'records\\item\\containers\\boss\\bosschest11_aktaios_epic.dbr',
        'records\\item\\containers\\boss\\bosschest11_aktaios_legendary.dbr'],
    'gargantuanyeti': [
        'records\\item\\containers\\boss\\'
        'bosschest15_gargantuanyeti_normal.dbr',
        'records\\item\\containers\\boss\\'
        'bosschest15_gargantuanyeti_epic.dbr',
        'records\\item\\containers\\boss\\'
        'bosschest15_gargantuanyeti_legendary.dbr'],
    'gorgon_euryale': [
        'records\\item\\containers\\boss\\bosschest05_gorgons_normal.dbr',
        'records\\item\\containers\\boss\\bosschest05_gorgons_epic.dbr',
        'records\\item\\containers\\boss\\bosschest05_gorgons_legendary.dbr'],
    'gorgon_medusa': [
        'records\\item\\containers\\boss\\bosschest05_gorgons_normal.dbr',
        'records\\item\\containers\\boss\\bosschest05_gorgons_epic.dbr',
        'records\\item\\containers\\boss\\bosschest05_gorgons_legendary.dbr'],
    'gorgon_sstheno': [
        'records\\item\\containers\\boss\\bosschest05_gorgons_normal.dbr',
        'records\\item\\containers\\boss\\bosschest05_gorgons_epic.dbr',
        'records\\item\\containers\\boss\\bosschest05_gorgons_legendary.dbr'],
    'greektelkine_megalesios': [
        'records\\item\\containers\\boss\\bosschest07_megalesios_normal.dbr',
        'records\\item\\containers\\boss\\bosschest07_megalesios_epic.dbr',
        'records\\item\\containers\\boss\\'
        'bosschest07_megalesios_legendary.dbr'],
    'hydra': [
        '',
        '',
        'records\\item\\containers\\boss\\bosschest25_hydra_legendary.dbr'],
    'manticore': [
        '',
        'records\\item\\containers\\boss\\bosschest23_manticore_epic.dbr',
        'records\\item\\containers\\boss\\'
        'bosschest23_manticore_legendary.dbr'],
    'minotaurlord': [
        'records\\item\\containers\\boss\\'
        'bosschest07a_minotaurlord_normal.dbr',
        'records\\item\\containers\\boss\\'
        'bosschest07a_minotaurlord_epic.dbr',
        'records\\item\\containers\\boss\\'
        'bosschest07a_minotaurlord_legendary.dbr'],
    'neanderthalchief_barmanu': [
        'records\\item\\containers\\boss\\bosschest14_barmanu_normal.dbr',
        'records\\item\\containers\\boss\\bosschest14_barmanu_epic.dbr',
        'records\\item\\containers\\boss\\bosschest14_barmanu_legendary.dbr'],
    'necromancer_alastor': [
        'records\\item\\containers\\boss\\bosschest06_alastor_normal.dbr',
        'records\\item\\containers\\boss\\bosschest06_alastor_epic.dbr',
        'records\\item\\containers\\boss\\bosschest06_alastor_legendary.dbr'],
    'pharaohshonorguard1': [
        'records\\item\\containers\\boss\\'
        'bosschest09_pharaohshonorguard_normal.dbr',
        'records\\item\\containers\\boss\\'
        'bosschest09_pharaohshonorguard_epic.dbr',
        'records\\item\\containers\\boss\\'
        'bosschest09_pharaohshonorguard_legendary.dbr'],
    'sandwraithlord': [
        'records\\item\\containers\\boss\\'
        'bosschest12_sandwraithlord_normal.dbr',
        'records\\item\\containers\\boss\\'
        'bosschest12_sandwraithlord_epic.dbr',
        'records\\item\\containers\\boss\\'
        'bosschest12_sandwraithlord_legendary.dbr'],
    'satyrshaman': [
        'records\\item\\containers\\boss\\bosschest01_satyrshaman_normal.dbr',
        'records\\item\\containers\\boss\\bosschest01_satyrshaman_epic.dbr',
        'records\\item\\containers\\boss\\'
        'bosschest01_satyrshaman_legendary.dbr'],
    'scarabaeus': [
        'records\\item\\containers\\boss\\bosschest08_scarabaeus_normal.dbr',
        'records\\item\\containers\\boss\\bosschest08_scarabaeus_epic.dbr',
        'records\\item\\containers\\boss\\'
        'bosschest08_scarabaeus_legendary.dbr'],
    'scorposking': [
        'records\\item\\containers\\boss\\bosschest10_scorposking_normal.dbr',
        'records\\item\\containers\\boss\\bosschest10_scorposking_epic.dbr',
        'records\\item\\containers\\boss\\'
        'bosschest10_scorposking_legendary.dbr'],
    'spartacentaur': [
        'records\\item\\containers\\boss\\bosschest02_nessus_normal.dbr',
        'records\\item\\containers\\boss\\bosschest02_nessus_epic.dbr',
        'records\\item\\containers\\boss\\bosschest02_nessus_legendary.dbr'],
    'spiderqueen_arachne': [
        'records\\item\\containers\\boss\\bosschest04_arachne_normal.dbr',
        'records\\item\\containers\\boss\\bosschest04_arachne_epic.dbr',
        'records\\item\\containers\\boss\\bosschest04_arachne_legendary.dbr'],
    'talos': [
        '',
        'records\\item\\containers\\boss\\bosschest22_talos_epic.dbr',
        'records\\item\\containers\\boss\\bosschest22_talos_legendary.dbr'],
    'terracottamage_bandari': [
        'records\\item\\containers\\boss\\bosschest18_bandari_normal.dbr',
        'records\\item\\containers\\boss\\bosschest18_bandari_epic.dbr',
        'records\\item\\containers\\boss\\bosschest18_bandari_legendary.dbr'],
    'titan_typhon': [
        'records\\item\\containers\\boss\\bosschest21_typhon_normal.dbr',
        'records\\item\\containers\\boss\\bosschest21_typhon_epic.dbr',
        'records\\item\\containers\\boss\\bosschest21_typhon_legendary.dbr'],
    'xiao': [
        'records\\item\\containers\\boss\\bosschest17_xiao_normal.dbr',
        'records\\item\\containers\\boss\\bosschest17_xiao_epic.dbr',
        'records\\item\\containers\\boss\\bosschest17_xiao_legendary.dbr'],
    'deino': [
        'records\\xpack\\item\\containers\\bosschest01_graeae_01.dbr',
        'records\\xpack\\item\\containers\\bosschest01_graeae_02.dbr',
        'records\\xpack\\item\\containers\\bosschest01_graeae_03.dbr'],
    'enyo': [
        'records\\xpack\\item\\containers\\bosschest01_graeae_01.dbr',
        'records\\xpack\\item\\containers\\bosschest01_graeae_02.dbr',
        'records\\xpack\\item\\containers\\bosschest01_graeae_03.dbr'],
    'pemphredo': [
        'records\\xpack\\item\\containers\\bosschest01_graeae_01.dbr',
        'records\\xpack\\item\\containers\\bosschest01_graeae_02.dbr',
        'records\\xpack\\item\\containers\\bosschest01_graeae_03.dbr'],
    'charon': [
        'records\\xpack\\item\\containers\\bosschest02_charon_01.dbr',
        'records\\xpack\\item\\containers\\bosschest02_charon_02.dbr',
        'records\\xpack\\item\\containers\\bosschest02_charon_03.dbr'],
    'cerberus': [
        'records\\xpack\\item\\containers\\bosschest03_cerberus_01.dbr',
        'records\\xpack\\item\\containers\\bosschest03_cerberus_02.dbr',
        'records\\xpack\\item\\containers\\bosschest03_cerberus_03.dbr'],
    'skeletaltyphon': [
        'records\\xpack\\item\\containers\\bosschest04_skeletaltyphon_01.dbr',
        'records\\xpack\\item\\containers\\bosschest04_skeletaltyphon_02.dbr',
        'records\\xpack\\item\\containers\\bosschest04_skeletaltyphon_03.dbr'],
    'hades': [
        'records\\xpack\\item\\containers\\bosschest05_hades_01.dbr',
        'records\\xpack\\item\\containers\\bosschest05_hades_02.dbr',
        'records\\xpack\\item\\containers\\bosschest05_hades_03.dbr'],
    }

CREATURES = [
    'records\\creature\\monster\\questbosses\\*.dbr',
    'records\\xpack\\creatures\\monster\\bosses\\**\\*.dbr']

EQUIPMENT_BASE = [
    'records\\item\\equipment*\\**\\*.dbr',
    'records\\xpack\\item\\equipment*\\**\\*.dbr',
    'records\\xpack\\item\\le_new\\*.dbr',
]

EQUIPMENT_EXT = [
    'records\\item\\relics\\*.dbr',
    'records\\item\\animalrelics\\*.dbr',
    'records\\xpack\\item\\relics\\*.dbr',
    'records\\xpack\\item\\charms\\*.dbr',
    'records\\xpack\\item\\scrolls\\*.dbr',
    'records\\xpack\\item\\artifacts\\*.dbr',
    'records\\xpack\\item\\artifacts\\arcaneformulae\\*.dbr']

SETS = [
    'records\\item\\sets\\*.dbr',
    'records\\xpack\\item\\sets\\*.dbr']

SKILLS = [
    'records\\skills\\defensive\\defensiveskilltree.dbr',
    'records\\skills\\earth\\earthskilltree.dbr',
    'records\\skills\\hunting\\huntingskilltree.dbr',
    'records\\skills\\nature\\natureskilltree.dbr',
    'records\\skills\\spirit\\spiritskilltree.dbr',
    'records\\skills\\stealth\\stealthskilltree.dbr',
    'records\\skills\\storm\\stormskilltree.dbr',
    'records\\skills\\warfare\\warfareskilltree.dbr',
    'records\\xpack\\skills\\dream\\dreamskilltree.dbr']

STRINGS_TAGS = [
    'commonequipment.txt',
    'xcommonequipment.txt',
    'monsters.txt',
    'xmonsters.txt',
    'quest.txt',
    'xquest.txt',
    'skills.txt',
    'xskills.txt',
    'uniqueequipment.txt',
    'xuniqueequipment.txt',
]

STRINGS_UI = [
    'ui.txt',
    'xui.txt'
]
