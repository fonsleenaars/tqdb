"""
Main parser file.

"""
import re

from tqdb.constants import parsing as pc
from tqdb.constants import resources
from tqdb.parsers.util import format_path
from tqdb.parsers.generic import GenericParser
from tqdb.storage import records


class DBRReader:
    """
    Reader class to prepare a DBR file for parsing.

    """
    def read(self, dbr):
        try:
            dbr_file = open(dbr)
        except FileNotFoundError:
            return [{}]

        # Split DBR file into a list of lines, delimited by a comma + newline:
        lines = [line.rstrip(',\n') for line in dbr_file]

        # All lines are key-value pairs, delimited by a comma:
        props = dict([(k, v) for k, v in (dict(properties.split(',')
                     for properties in lines)).items()
                     if self.property_isset(v)])

        # The values can be tiered, delimited by a semi-colon:
        props_tiered = (dict([(key, value.split(';'))
                        for key, value in props.items()
                        if ';' in value]))

        # If there are no tiered properties, return here
        if not props_tiered:
            return [props]

        # Check occurences where value is set, but first iteration is 0% chance
        chance_zeroes = {}
        for key, value in props_tiered.items():
            if('Chance' in key and float(value[0]) == 0):
                # Store the prefix to check on another iteration
                chance_zeroes[key[0:key.index('Chance')]] = len(value)

        # Find longest list of split fields:
        tiers = len(props_tiered[max(props_tiered,
                                     key=lambda
                                     x:len(props_tiered[x]))])

        # Now add all non-tiered properties:
        props_tiered.update(dict([(key, value)
                            for key, value
                            in props.items()
                            if ';' not in value]))

        # Check the edge case mentioned above
        for prefix, total in chance_zeroes.items():
            for key, value in props_tiered.items():
                if ('Chance' not in key and prefix in key and not
                   isinstance(value, list)):
                    # Fix the first occurance by seting it to zero
                    # and repeating the normal value for the others
                    props_tiered[key] = ['0.000000'] + ([value] * (total - 1))

        tiered = []
        for i in range(0, tiers):
            tier = {}

            # Setup the tier
            for key, value in props_tiered.items():
                if key == 'racialBonusRace':
                    tier[key] = (';'.join(value)
                                 if isinstance(value, list)
                                 else value)
                elif not isinstance(value, list):
                    tier[key] = value
                elif i < len(value) and self.property_isset(value[i]):
                    tier[key] = value[i]
                elif i >= len(value):
                    tier[key] = value[len(value) - 1]

            # Append this tier
            tiered.append(tier)

        return tiered

    def property_isset(self, property):
        try:
            float(property)
            return float(property) != 0
        except ValueError:
            return True


class DBRParser:
    """
    Main TQDB parser for the dbr files.

    This is the main parser that can take a DBR file and return the defined
    and relevant information for that file. When initialized the class will
    make sure all its available parsers are registered.

    Upon receiving a file to parse it will attempt to grab the correct parser
    for the DBR file and pass it along to that parser, and return the value
    from it.

    """
    def __init__(self, parsers, strings):
        self.parsers = parsers
        self.strings = strings
        self.reader = DBRReader()

    def parse(self, dbr, include_type=False, allow_generic=False):
        """
        Parse a list of properties.

        Args:
            dbr - path to the DBR file to parse

        Return:
            dict - Dictionary with all defined and parsed properties.

        """
        # See if this DBR has been parsed before:
        dbr_key = format_path(dbr)
        if dbr_key in records:
            return records[dbr_key]

        # Grab the type from this file:
        props = self.reader.read(dbr)
        parsed = {}

        # If a parser exists for this type, parse the file:
        dbr_class = props[0].get('Class', None)
        if dbr_class in self.parsers:
            parsed = self.parsers[dbr_class](dbr, props, self.strings).parse()
        elif allow_generic:
            parsed = GenericParser(dbr, props, self.strings).parse()

        # Determine whether or not to return the type as well:
        if include_type:
            return {
                'parsed': parsed,
                'class': dbr_class,
            }

        # Store this DBR entry to prevent double parsing:
        records[dbr_key] = parsed
        return parsed


def parse_text_resource(text_file):
    """
    Parse a text resource, extracted from the Text_**.arc files.

    """
    try:
        # Most files have UTF-16 or RAW encoding
        lines = [l.rstrip('\n') for l in open(text_file, encoding='utf16')]
    except UnicodeError:
        # Some files have ??? encoding (literally)
        lines = [l.rstrip('\n') for l in open(text_file)]

    # Parse line into a dictionary of key, value properties:
    return dict(
        properties.split('=', 1)
        for properties in lines
        if '=' in properties and not properties.startswith('//'))


class PropertyTable:
    """
    Table of DBR property keys mapping to string values.

    """

    def __init__(self, props):
        """
        Initialize the table.

        """
        self.table = {}

        # Remove all the (x)tag prefixes:
        tags = dict((k[3:], v) for (k, v) in props.items()
                    if k.startswith('tag'))
        tags.update(dict((k[4:], v) for (k, v) in props.items()
                    if k.startswith('xtag')))
        props.update(tags)

        for key, val in props.items():
            for repl in pc.PT_REPLACEMENTS:
                if repl['type'] == 'regex':
                    # Replace all regex matches:
                    pattern = re.compile(repl['find'])
                    if re.match(pattern, key):
                        self.table[re.sub(pattern, repl['replace'], key)] = val
                        break
                else:
                    # Simply replace (if it's a prefix)
                    prefix = repl['find']
                    if key.startswith(prefix):
                        self.table[
                            key.replace(prefix, repl['replace'], 1)
                        ] = val
                        break

        # Manually add a few keys that are needed:
        for field in pc.PT_ADD_CUSTOM:
            self.table[field[0]] = field[1]
        for field in pc.PT_ADD_CUSTOM_FROM_PROPS:
            self.table[field[0]] = props[field[1]]
        for field in pc.PT_ADD_CUSTOM_FROM_TABLE:
            self.table[field[0]] = self.table[field[1]]

        # Optional ranged keys:
        ranged = dict()

        # Now format all regex values
        for key, val in self.table.items():
            if re.search(pc.PT_VALUE_OLD, val):
                # Replace the TQ regex with a Python regex:
                for m in re.finditer(pc.PT_VALUE_OLD, val):
                    val = val.replace(
                        m.group(),
                        pc.PT_VALUE_NEW.format(**m.groupdict()))
            elif 'second' in val:
                # Also add a ranged formatter:
                ranged[key + 'Ranged'] = '{0:.1f} ~ {1:.1f}' + val
                val = '{0:.1f}' + val
            elif 'characterAttackSpeed' not in key:
                # Also add a ranged formatter:
                ranged[key + 'Ranged'] = '{0:.0f} ~ {1:.0f}' + val
                val = '{0:.0f}' + val

            self.table[key] = val

        # Merge all the ranged keys into the table
        self.table.update(ranged)


def create_parser():
    # Load the mapping for keys to parsers:
    parsers = {}
    for parser, keys in pc.PARSERS.items():
        parsers.update(dict((key, parser) for key in keys))

    # Prepare the formatted strings
    strings_tags = {}
    for tags in resources.STRINGS_TAGS:
        strings_tags.update(parse_text_resource(resources.RES + tags))

    strings_ui = {}
    for tags in resources.STRINGS_UI:
        strings_ui.update(parse_text_resource(resources.RES + tags))

    # Merge all formatted strings together
    strings = {**PropertyTable(strings_ui).table, **strings_tags}

    # Create a DBRParser for other modules to import
    return DBRParser(parsers, strings)


parser = create_parser()
