# import os
# from tqdb.parsers.util import UtilityParser


# class ArtifactParser():
#     """
#     Parser for Artifact files.

#     """
#     def __init__(self, dbr, props, strings):
#         self.dbr = dbr
#         self.strings = strings
#         # Artifacts are never tiered, grab first item from list:
#         self.props = props[0]

#     @classmethod
#     def keys(cls):
#         return ['ItemArtifact']

#     def parse(self):
#         from tqdb.constants.parsing import DIFFICULTIES

#         # Only parse artifacts that have a difficulty set:
#         file_name = os.path.basename(self.dbr).split('_')
#         if file_name[0] not in DIFFICULTIES:
#             return {}

#         result = {}
#         result['tag'] = self.props['description']
#         result['name'] = self.strings[result['tag']]
#         result['classification'] = self.props['artifactClassification']
#         result['dropsIn'] = DIFFICULTIES[file_name[0]]

#         # Set the bitmap if it exists
#         if 'artifactBitmap' in self.props:
#             result['bitmap'] = self.props['artifactBitmap']

#         # Let the UtilityParser parse all the common properties:
#         util = UtilityParser(self.dbr, self.props, self.strings)
#         util.parse_character()
#         util.parse_damage()
#         util.parse_defense()
#         util.parse_item_skill_augment()
#         util.parse_pet_bonus()
#         util.parse_racial()
#         util.parse_skill_properties()

#         result['properties'] = util.result

#         # Now parse the requirements:
#         result.update(util.parse_requirements())

#         return result


# class CharmRelicParser():
#     """
#     Parser for Charm and Relic files.

#     """
#     def __init__(self, dbr, props, strings):
#         self.dbr = dbr
#         self.strings = strings
#         self.props = props

#     @classmethod
#     def keys(cls):
#         return [
#             'ItemRelic',
#             'ItemCharm']

#     def parse(self):
#         from tqdb.constants.parsing import DIFF_LIST
#         from tqdb.parsers.main import parser

#         # Use the file name to determine the difficulty and act it drops in:
#         file_name = os.path.basename(self.dbr).split('_')

#         shared = self.props[0]

#         result = {}
#         result['tag'] = shared['description']
#         result['name'] = self.strings[result['tag']]
#         result['description'] = self.strings[shared['itemText']]
#         result['classification'] = DIFF_LIST[int(file_name[0][1:]) - 1]
#         result['act'] = file_name[1]

#         # Set the bitmap if it exists
#         if 'relicBitmap' in shared:
#             result['bitmap'] = shared['relicBitmap']

#         result['properties'] = []
#         for props in self.props:
#             # Let the UtilityParser parse all the common properties:
#             util = UtilityParser(self.dbr, props, self.strings)
#             util.parse_character()
#             util.parse_damage()
#             util.parse_defense()
#             util.parse_racial()
#             util.parse_skill_properties()

#             result['properties'].append(util.result)

#         # Now parse the requirements:
#         util = UtilityParser(self.dbr, shared, self.strings)
#         result.update(util.parse_requirements())

#         # Add the potential completion bonuses
#         bonus = parser.parse(util.get_reference_dbr(shared['bonusTableName']))
#         result['bonus'] = bonus.get('options', [])

#         return result


# class FormulaParser():
#     """
#     Parser for Formula files.

#     """
#     def __init__(self, dbr, props, strings):
#         self.dbr = dbr
#         self.strings = strings
#         # Formula is never tiered, grab first item from list:
#         self.props = props[0]

#     @classmethod
#     def keys(cls):
#         return ['ItemArtifactFormula']

#     def parse(self):
#         from tqdb.parsers.main import parser

#         # All formula's need an artifact to create:
#         if 'artifactName' not in self.props:
#             return

#         # Grab the artifact it will create:
#         util = UtilityParser(self.dbr, self.props, self.strings)
#         artifact = parser.parse(util.get_reference_dbr(
#             self.props['artifactName']))

#         # Set the artifact tag and name for this formula:
#         result = {}
#         result['tag'] = artifact['tag']
#         result['name'] = artifact['name']
#         result['classification'] = artifact['classification']

#         # Set the bitmap if it exists
#         if 'artifactFormulaBitmapName' in self.props:
#             result['bitmap'] = self.props['artifactFormulaBitmapName']

#         # Parse the requirements
#         result.update(util.parse_requirements())

#         # Grab the reagents (ingredients):
#         for reagent_number in ['reagent1', 'reagent2', 'reagent3']:
#             reagent = parser.parse(util.get_reference_dbr(
#                 self.props[reagent_number + 'BaseName']))

#             # Add the reagent (relic, scroll or artifact)
#             result[reagent_number] = reagent['tag']

#         # Add the potential completion bonuses
#         bonus = parser.parse(util.get_reference_dbr(
#             self.props['artifactBonusTableName']))
#         result['bonus'] = bonus.get('options', [])

#         return result


# class ScrollParser():
#     """
#     Parser for Scroll files.

#     """
#     def __init__(self, dbr, props, strings):
#         self.dbr = dbr
#         self.strings = strings
#         # Scrolls are never tiered, grab first item from list:
#         self.props = props[0]

#     @classmethod
#     def keys(cls):
#         return ['OneShot_Scroll']

#     def parse(self):
#         from tqdb.constants.parsing import DIFF_LIST
#         from tqdb.parsers.main import parser

#         # Use the file name to determine the difficulty and act it drops in:
#         file_name = os.path.basename(self.dbr).split('_')[0][1:]
#         # Strip all but digits from the string, then cast to int:
#         difficulty_index = ''.join(filter(lambda x: x.isdigit(), file_name))

#         result = {}
#         result['tag'] = self.props['description']
#         result['name'] = self.strings[result['tag']]
#         result['classification'] = DIFF_LIST[int(difficulty_index) - 1]
#         result['description'] = self.strings[self.props['itemText']]

#         # Set the bitmap if it exists
#         if 'bitmap' in self.props:
#             result['bitmap'] = self.props['bitmap']

#         util = UtilityParser(self.dbr, self.props, self.strings)

#         # Parse the requirements
#         result.update(util.parse_requirements())

#         # Grab the skill file:
#         skill = parser.parse(util.get_reference_dbr(self.props['skillName']))

#         # Add properties and summons from the scrolls, whichever is applicable:
#         if 'properties' in skill:
#             result['properties'] = skill['properties']

#         if 'summons' in skill:
#             result['summons'] = skill['summons']

#         return result
