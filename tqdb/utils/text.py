"""
Text utility functions

These text related functions are the strings that are displayed for attributes,
item names, and all other properties used in Titan Quest.abs

"""
import re

from pathlib import Path


class Texts:
    """
    Class holding all TQ equipment, skill, and attribute texts.

    """
    # Directory holding all the resources:
    BASE_DIR = Path('data/resources')

    # These resources need to be copied from existing ones, under a new name:
    COPY_RESOURCES = [
        # The misspelling of charcteritemglobalreduction is "correct", that's
        # how the files list it.
        ['characterglobalreqreduction', 'charcteritemglobalreduction'],
        ['defensivetotalspeed', 'totalspeedresistance'],
        ['offensivebaselife', 'tagdamagebasevitality'],
        ['offensiveslowdefensivereductionmodifier',
         'damagedurationdefensivereduction'],
        ['projectilepiercing', 'projectilepiercingchance'],
        ['refreshtime', 'skillrefreshtime'],
        ['skillactivelifecost', 'activelifecost'],
        ['skillactivemanacost', 'activemanacost'],
        ['characterdeflectprojectile', 'characterdeflectprojectiles'],
        ['defensiveabsorption', 'defenseabsorptionmodifier'],
        ['defensiveprotection', 'defenseabsorptionprotection'],
        ['defensiveslowlifeleach', 'defenselifeleach'],
        ['defensiveslowlifeleachduration', 'defenselifeleachduration'],
        ['defensiveslowmanaleach', 'defensemanaleach'],
        ['defensiveslowmanaleachduration', 'defensemanaleachduration'],
        ['offensivefumble', 'damagedurationfumble'],
        ['offensiveprojectilefumble', 'damagedurationprojectilefumble'],
        ['offensivepierceratio', 'damagebasepierceratio'],
        ['spawnobjectstimetolive', 'skillpettimetolive'],
    ]

    # These resource files hold strings that map a tag to a name.
    TAG_RESOURCES = [
        'commonequipment.txt',
        'xcommonequipment.txt',
        'x2commonequipment.txt',
        'monsters.txt',
        'xmonsters.txt',
        'x2monsters.txt',
        'quest.txt',
        'xquest.txt',
        'x2quest.txt',
        'skills.txt',
        'xskills.txt',
        'x2skills.txt',
        'uniqueequipment.txt',
        'xuniqueequipment.txt',
        'x2uniqueequipment.txt',
    ]

    # These resource files hold strings that require some formatting
    STRING_RESOURCES = [
        'ui.txt',
        'xui.txt',
        'x2ui.txt',
    ]

    # Old regex structure used in Titan Quest's resource text files
    REGEX_OLD = (
        r'{(?P<pre_signed>\-?\+?)%'
        r'(?P<post_signed>\+?)'
        r'(?P<decimals>\.?[0-9]?)'
        r'(?P<type>[a-z])(?P<arg>[0-9])}'
    )

    # New python friendly regex structure
    REGEX_NEW = '{{{arg}:{pre_signed}{post_signed}{decimals}{type}}}'

    def __init__(self):
        self.tags = {}
        for resource in self.TAG_RESOURCES:
            self.tags.update(self.parse_text_resource(resource))

        self.strings = {}
        for resource in self.STRING_RESOURCES:
            self.strings.update(self.parse_text_resource(resource))

        # Some strings require formatting to replace their TQ regex structure
        # with a python friendly one, others need some replacements in their
        # property names, and some fields are missing from the text database.

        # Begin by removing all tag, xtag and x2tag prefixes:
        self.strings.update(dict(
            (k[3:], v) for (k, v) in self.strings.items()
            if k.startswith('tag')))
        self.strings.update(dict(
            (k[4:], v) for (k, v) in self.strings.items()
            if k.startswith('xtag')))
        self.strings.update(dict(
            (k[5:], v) for (k, v) in self.strings.items()
            if k.startswith('x2tag')))

        # Copy over a few strings under a new property name, to match the
        # property that's set in the DBR files.
        self.strings.update(dict(
            (new_key, self.strings[old_key])
            for new_key, old_key in self.COPY_RESOURCES))

        # Iterate over all known strings now
        for key, value in self.strings.items():
            # Update the regex structure for all strings that have regex:
            if re.search(self.REGEX_OLD, value):
                # Replace the TQ regex with a Python regex:
                for match in re.finditer(self.REGEX_OLD, value):
                    value = value.replace(
                        match.group(),
                        self.REGEX_NEW.format(**match.groupdict()))
            # Add a decimal ranged variant for values that have seconds:
            elif 'second' in value:
                # Also add a ranged formatter:
                self.strings[key + 'Ranged'] = '{0:.1f} ~ {1:.1f}' + value
                value = '{0:.1f}' + value
            # All other regular get a non-decimal ranged variant:
            elif 'characterAttackSpeed' not in key:
                # Also add a ranged formatter:
                self.strings[key + 'Ranged'] = '{0:.0f} ~ {1:.0f}' + value
                value = '{0:.0f}' + value

            self.strings[key] = value

    def tag(self, tag):
        """
        Return the friendly name for a tag.

        If no friendly name was found, return the tag itself.

        """
        return self.tags.get(tag.lower(), tag)

    def get(self, string):
        """
        Return the friendly value, ready for formatting, for a string.

        """
        return self.strings[string.lower()]

    def parse_text_resource(self, text_file):
        """
        Parse a text resource file, for a certain locale.

        """
        f = self.BASE_DIR / text_file

        try:
            # Most files have UTF-16 or RAW encoding
            lines = [l.rstrip('\n') for l in open(f, encoding='utf16')]
        except UnicodeError:
            # Some files have ??? encoding (literally)
            lines = [l.rstrip('\n') for l in open(f)]

        # Parse line into a dictionary of key, value properties:
        return dict(
            # To be consistent, make all keys lower cased
            (k.lower(), v) for k, v in (
                properties.split('=', 1)
                for properties in lines
                if '=' in properties and not properties.startswith('//')))


# Prepare an instance for usage:
texts = Texts()
