from tqdb.parsers.util import UtilityParser


class GenericParser():
    """
    Parser for generic files that don't have a Class.

    """
    def __init__(self, dbr, props, strings):
        self.dbr = dbr
        self.strings = strings
        self.props = props

    def parse(self):
        result = {}

        if len(self.props) > 1:
            result['properties'] = []
            for props in self.props:
                util = UtilityParser(self.dbr, props, self.strings)
                util.parse_character()
                util.parse_damage()
                util.parse_defense()
                util.parse_item_skill_augment()
                util.parse_pet_bonus()
                util.parse_racial()
                util.parse_skill_properties()

                result['properties'].append(util.result)
        else:
            util = UtilityParser(self.dbr, self.props[0], self.strings)
            util.parse_character()
            util.parse_damage()
            util.parse_defense()
            util.parse_item_skill_augment()
            util.parse_pet_bonus()
            util.parse_racial()
            util.parse_skill_properties()

            result['properties'] = util.result

        return result
