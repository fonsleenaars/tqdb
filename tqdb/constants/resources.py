"""
All resource constants.

"""
from pathlib import Path

# This is being replaced by only parsing loot affixes that appear in
# the `randomizerName` properties of the AFFIX_TABLES.
# This way we know for sure those affixes can occur
# AFFIXES = [
#     "records/item*/lootmagicalaffixes/*ix/default/*.dbr",
#     "records/xpack*/item*/lootmagicalaffixes/*ix/default/*.dbr",
#     "records/xpack*/item*/lootmagicalaffixes/*ix/*.dbr",
# ]

AFFIX_TABLES = [
    "records/item*/lootmagicalaffixes/*ix/tables*/*.dbr",
    "records/xpack*/item*/lootmagicalaffixes/*ix/tables*/*.dbr",
]

CHESTS = {
    "tagMonsterName004": [
        "records/item/containers/boss/bosschest13_chimera_normal.dbr",
        # Chimera Epic has a double .dbr extension:
        "records/item/containers/boss/bosschest13_chimera_epic.dbr.dbr",
        "records/item/containers/boss/bosschest13_chimera_legendary.dbr",
    ],
    "tagMonsterName122": [
        "records/item/containers/boss/bosschest20_ormenos_normal.dbr",
        "records/item/containers/boss/bosschest20_ormenos_epic.dbr",
        "records/item/containers/boss/bosschest20_ormenos_legendary.dbr",
    ],
    "tagMonsterName155": [
        "records/item/containers/boss/bosschest03_cyclops_normal.dbr",
        "records/item/containers/boss/bosschest03_cyclops_epic.dbr",
        "records/item/containers/boss/bosschest03_cyclops_legendary.dbr",
    ],
    "tagMonsterName1184": [
        "records/item/containers/boss/bosschest19_yaoguai_normal.dbr",
        "records/item/containers/boss/bosschest19_yaoguai_epic.dbr",
        "records/item/containers/boss/bosschest19_yaoguai_legendary.dbr",
    ],
    "tagMonsterName1186": [
        "",
        "records/item/containers/boss/bosschest24_dragonliche_epic.dbr",
        "records/item/containers/boss/" "bosschest24_dragonliche_legendary.dbr",
    ],
    "tagMonsterName121": [
        "records/item/containers/boss/bosschest11_aktaios_normal.dbr",
        "records/item/containers/boss/bosschest11_aktaios_epic.dbr",
        "records/item/containers/boss/bosschest11_aktaios_legendary.dbr",
    ],
    "tagMonsterName1182": [
        "records/item/containers/boss/" "bosschest15_gargantuanyeti_normal.dbr",
        "records/item/containers/boss/" "bosschest15_gargantuanyeti_epic.dbr",
        "records/item/containers/boss/" "bosschest15_gargantuanyeti_legendary.dbr",
    ],
    "tagMonsterName143": [
        "records/item/containers/boss/bosschest05_gorgons_normal.dbr",
        "records/item/containers/boss/bosschest05_gorgons_epic.dbr",
        "records/item/containers/boss/bosschest05_gorgons_legendary.dbr",
    ],
    "tagMonsterName145": [
        "records/item/containers/boss/bosschest05_gorgons_normal.dbr",
        "records/item/containers/boss/bosschest05_gorgons_epic.dbr",
        "records/item/containers/boss/bosschest05_gorgons_legendary.dbr",
    ],
    "tagMonsterName144": [
        "records/item/containers/boss/bosschest05_gorgons_normal.dbr",
        "records/item/containers/boss/bosschest05_gorgons_epic.dbr",
        "records/item/containers/boss/bosschest05_gorgons_legendary.dbr",
    ],
    "tagMonsterName120": [
        "records/item/containers/boss/bosschest07_megalesios_normal.dbr",
        "records/item/containers/boss/bosschest07_megalesios_epic.dbr",
        "records/item/containers/boss/" "bosschest07_megalesios_legendary.dbr",
    ],
    "tagMonsterName126": ["", "", "records/item/containers/boss/bosschest25_hydra_legendary.dbr"],
    "tagMonsterName1185": [
        "",
        "records/item/containers/boss/bosschest23_manticore_epic.dbr",
        "records/item/containers/boss/" "bosschest23_manticore_legendary.dbr",
    ],
    "tagMonsterName286": [
        "records/item/containers/boss/" "bosschest07a_minotaurlord_normal.dbr",
        "records/item/containers/boss/" "bosschest07a_minotaurlord_epic.dbr",
        "records/item/containers/boss/" "bosschest07a_minotaurlord_legendary.dbr",
    ],
    "tagMonsterName1183": [
        "records/item/containers/boss/bosschest14_barmanu_normal.dbr",
        "records/item/containers/boss/bosschest14_barmanu_epic.dbr",
        "records/item/containers/boss/bosschest14_barmanu_legendary.dbr",
    ],
    "tagMonsterName110": [
        "records/item/containers/boss/bosschest06_alastor_normal.dbr",
        "records/item/containers/boss/bosschest06_alastor_epic.dbr",
        "records/item/containers/boss/bosschest06_alastor_legendary.dbr",
    ],
    "tagMonsterName1180": [
        "records/item/containers/boss/" "bosschest09_pharaohshonorguard_normal.dbr",
        "records/item/containers/boss/" "bosschest09_pharaohshonorguard_epic.dbr",
        "records/item/containers/boss/" "bosschest09_pharaohshonorguard_legendary.dbr",
    ],
    "tagMonsterName1129": [
        "records/item/containers/boss/bosschest08x_masika_normal.dbr",
        "records/item/containers/boss/bosschest08x_masika_epic.dbr",
        "records/item/containers/boss/bosschest08x_masika_legendary.dbr",
    ],
    "tagMonsterName060": [
        "records/item/containers/boss/" "bosschest12_sandwraithlord_normal.dbr",
        "records/item/containers/boss/" "bosschest12_sandwraithlord_epic.dbr",
        "records/item/containers/boss/" "bosschest12_sandwraithlord_legendary.dbr",
    ],
    "tagMonsterName293": [
        "records/item/containers/boss/bosschest01_satyrshaman_normal.dbr",
        "records/item/containers/boss/bosschest01_satyrshaman_epic.dbr",
        "records/item/containers/boss/" "bosschest01_satyrshaman_legendary.dbr",
    ],
    "tagMonsterName043": [
        "records/item/containers/boss/bosschest08_scarabaeus_normal.dbr",
        "records/item/containers/boss/bosschest08_scarabaeus_epic.dbr",
        "records/item/containers/boss/" "bosschest08_scarabaeus_legendary.dbr",
    ],
    "tagMonsterName115": [
        "records/item/containers/boss/bosschest10_scorposking_normal.dbr",
        "records/item/containers/boss/bosschest10_scorposking_epic.dbr",
        "records/item/containers/boss/" "bosschest10_scorposking_legendary.dbr",
    ],
    "tagMonsterName097": [
        "records/item/containers/boss/bosschest02_nessus_normal.dbr",
        "records/item/containers/boss/bosschest02_nessus_epic.dbr",
        "records/item/containers/boss/bosschest02_nessus_legendary.dbr",
    ],
    "tagMonsterName114": [
        "records/item/containers/boss/bosschest04_arachne_normal.dbr",
        "records/item/containers/boss/bosschest04_arachne_epic.dbr",
        "records/item/containers/boss/bosschest04_arachne_legendary.dbr",
    ],
    "tagMonsterName066": [
        "",
        "records/item/containers/boss/bosschest22_talos_epic.dbr",
        "records/item/containers/boss/bosschest22_talos_legendary.dbr",
    ],
    "tagMonsterName123": [
        "records/item/containers/boss/bosschest18_bandari_normal.dbr",
        "records/item/containers/boss/bosschest18_bandari_epic.dbr",
        "records/item/containers/boss/bosschest18_bandari_legendary.dbr",
    ],
    "tagMonsterName382": [
        "records/item/containers/boss/bosschest21_typhon_normal.dbr",
        "records/item/containers/boss/bosschest21_typhon_epic.dbr",
        "records/item/containers/boss/bosschest21_typhon_legendary.dbr",
    ],
    "tagMonsterName361": [
        "records/item/containers/boss/bosschest17_xiao_normal.dbr",
        "records/item/containers/boss/bosschest17_xiao_epic.dbr",
        "records/item/containers/boss/bosschest17_xiao_legendary.dbr",
    ],
    "xtagMonsterGraeae1": [
        "records/xpack/item/containers/bosschest01_graeae_01.dbr",
        "records/xpack/item/containers/bosschest01_graeae_02.dbr",
        "records/xpack/item/containers/bosschest01_graeae_03.dbr",
    ],
    "xtagMonsterGraeae2": [
        "records/xpack/item/containers/bosschest01_graeae_01.dbr",
        "records/xpack/item/containers/bosschest01_graeae_02.dbr",
        "records/xpack/item/containers/bosschest01_graeae_03.dbr",
    ],
    "xtagMonsterGraeae3": [
        "records/xpack/item/containers/bosschest01_graeae_01.dbr",
        "records/xpack/item/containers/bosschest01_graeae_02.dbr",
        "records/xpack/item/containers/bosschest01_graeae_03.dbr",
    ],
    "xtagMonsterCharon": [
        "records/xpack/item/containers/bosschest02_charon_01.dbr",
        "records/xpack/item/containers/bosschest02_charon_02.dbr",
        "records/xpack/item/containers/bosschest02_charon_03.dbr",
    ],
    "xtagMonsterCerberus": [
        "records/xpack/item/containers/bosschest03_cerberus_01.dbr",
        "records/xpack/item/containers/bosschest03_cerberus_02.dbr",
        "records/xpack/item/containers/bosschest03_cerberus_03.dbr",
    ],
    "xtagMonsterSkeletalTyphon": [
        "records/xpack/item/containers/bosschest04_skeletaltyphon_01.dbr",
        "records/xpack/item/containers/bosschest04_skeletaltyphon_02.dbr",
        "records/xpack/item/containers/bosschest04_skeletaltyphon_03.dbr",
    ],
    "xtagMonsterHades": [
        "records/xpack/item/containers/bosschest05_hades_01.dbr",
        "records/xpack/item/containers/bosschest05_hades_02.dbr",
        "records/xpack/item/containers/bosschest05_hades_03.dbr",
    ],
    "x2tagMonsterName096": [
        "records/xpack2/item/containers/boss containers/bosschest01_porcus_01.dbr",
        "records/xpack2/item/containers/boss containers/bosschest01_porcus_02.dbr",
        "records/xpack2/item/containers/boss containers/bosschest01_porcus_03.dbr",
    ],
    "x2tagMonsterName184": [
        "records/xpack2/item/containers/boss containers/bosschest03_mineghost_01.dbr",
        "records/xpack2/item/containers/boss containers/bosschest03_mineghost_02.dbr",
        "records/xpack2/item/containers/boss containers/bosschest03_mineghost_03.dbr",
    ],
    "x2tagMonsterName147": [
        "records/xpack2/item/containers/boss containers/bosschest05_ancients_01.dbr",
        "records/xpack2/item/containers/boss containers/bosschest05_ancients_02.dbr",
        "records/xpack2/item/containers/boss containers/bosschest05_ancients_03.dbr",
    ],
    "x2tagMonsterName148": [
        "records/xpack2/item/containers/boss containers/bosschest05_ancients_01.dbr",
        "records/xpack2/item/containers/boss containers/bosschest05_ancients_02.dbr",
        "records/xpack2/item/containers/boss containers/bosschest05_ancients_03.dbr",
    ],
    "x2tagMonsterName149": [
        "records/xpack2/item/containers/boss containers/bosschest05_ancients_01.dbr",
        "records/xpack2/item/containers/boss containers/bosschest05_ancients_02.dbr",
        "records/xpack2/item/containers/boss containers/bosschest05_ancients_03.dbr",
    ],
    "x2tagMonsterName150": [
        "records/xpack2/item/containers/boss containers/bosschest05_ancients_01.dbr",
        "records/xpack2/item/containers/boss containers/bosschest05_ancients_02.dbr",
        "records/xpack2/item/containers/boss containers/bosschest05_ancients_03.dbr",
    ],
    "x2tagMonsterName011": [
        "records/xpack2/item/containers/boss containers/bosschest07_hildisvini_01.dbr",
        "records/xpack2/item/containers/boss containers/bosschest07_hildisvini_02.dbr",
        "records/xpack2/item/containers/boss containers/bosschest07_hildisvini_03.dbr",
    ],
    "x2tagMonsterName121": [
        "records/xpack2/item/containers/boss containers/bosschest09_shroomking_01.dbr",
        "records/xpack2/item/containers/boss containers/bosschest09_shroomking_02.dbr",
        "records/xpack2/item/containers/boss containers/bosschest09_shroomking_03.dbr",
    ],
    "x2tagasgard_odin": [
        "records/xpack2/item/containers/boss containers/bosschest10_aesir_01.dbr",
        "records/xpack2/item/containers/boss containers/bosschest10_aesir_02.dbr",
        "records/xpack2/item/containers/boss containers/bosschest10_aesir_03.dbr",
    ],
    "x2tagasgard_freyja": [
        "records/xpack2/item/containers/boss containers/bosschest10_aesir_01.dbr",
        "records/xpack2/item/containers/boss containers/bosschest10_aesir_02.dbr",
        "records/xpack2/item/containers/boss containers/bosschest10_aesir_03.dbr",
    ],
    "x2tagasgard_baldr": [
        "records/xpack2/item/containers/boss containers/bosschest10_aesir_01.dbr",
        "records/xpack2/item/containers/boss containers/bosschest10_aesir_02.dbr",
        "records/xpack2/item/containers/boss containers/bosschest10_aesir_03.dbr",
    ],
    "x2tagasgard_tyr": [
        "records/xpack2/item/containers/boss containers/bosschest10_aesir_01.dbr",
        "records/xpack2/item/containers/boss containers/bosschest10_aesir_02.dbr",
        "records/xpack2/item/containers/boss containers/bosschest10_aesir_03.dbr",
    ],
    "x2tagutgard_mimer": [
        "records/xpack2/item/containers/boss containers/bosschest12_mimir_01.dbr",
        "records/xpack2/item/containers/boss containers/bosschest12_mimir_02.dbr",
        "records/xpack2/item/containers/boss containers/bosschest12_mimir_03.dbr",
    ],
    "x2tagMonsterName093": [
        "records/xpack2/item/containers/boss containers/bosschest14_loki_01.dbr",
        "records/xpack2/item/containers/boss containers/bosschest14_loki_02.dbr",
        "records/xpack2/item/containers/boss containers/bosschest14_loki_03.dbr",
    ],
    "x2tagmuspelheim_loki": [
        "records/xpack2/item/containers/boss containers/bosschest14_loki_01.dbr",
        "records/xpack2/item/containers/boss containers/bosschest14_loki_02.dbr",
        "records/xpack2/item/containers/boss containers/bosschest14_loki_03.dbr",
    ],
    "x2tagMonsterName058": [
        "records/xpack2/item/containers/boss containers/bosschest15_surtr_01.dbr",
        "records/xpack2/item/containers/boss containers/bosschest15_surtr_02.dbr",
        "records/xpack2/item/containers/boss containers/bosschest15_surtr_03.dbr",
    ],
    "x2tagMonsterName059": [
        "records/xpack2/item/containers/boss containers/bosschest15_surtr_01.dbr",
        "records/xpack2/item/containers/boss containers/bosschest15_surtr_02.dbr",
        "records/xpack2/item/containers/boss containers/bosschest15_surtr_03.dbr",
    ],
    "x2tagMonsterName094": ["", "", "records/xpack2/item/containers/boss containers/bosschest17_fafnir_03.dbr"],
}

CREATURES = [
    "records/creature/monster/**/*.dbr",
    # Note that the expansions folder is called 'creatures', not 'creature'
    "records/xpack*/creatures/monster/**/*.dbr",
]

EQUIPMENT = [
    "records/item*/animalrelics/*.dbr",
    "records/item*/equipment*/**/*.dbr",
    "records/item*/relics/*.dbr",
    "records/xpack*/item*/artifacts/*.dbr",
    "records/xpack*/item*/artifacts/arcaneformulae/*.dbr",
    "records/xpack*/item*/charms/*.dbr",
    "records/xpack*/item*/equipment*/**/*.dbr",
    "records/xpack*/item*/relics/*.dbr",
    "records/xpack*/item*/scrolls/*.dbr",
    "records/xpack/item*/le_new/*.dbr",
]

QUESTS = "data\\quests\\*.qst"

SETS = [
    "records/item/sets/*.dbr",
    # Note:
    # Immortal Throne:  xpack/item/sets
    # Ragnarok:         xpack2/item/sets
    # Atlantis:         xpack3/items/set
    # Eternal Embers:   xpack4/item/sets
    "records/xpack*/item*/set*/*.dbr",
]
