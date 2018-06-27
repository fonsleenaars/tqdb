# import os
# from tqdb.parsers.util import UtilityParser

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
