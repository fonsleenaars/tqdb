"""
Text utility functions

These text related functions are the strings that are displayed for attributes,
item names, and all other properties used in Titan Quest.abs

"""
import logging
import json
import re

from pathlib import Path


class Texts:
    """
    Class holding all TQ equipment, skill, and attribute texts.

    """
    # Directory holding all the resources:
    BASE_DIR = Path('data/resources')

    # Regex to match base fields (starts with these prefixes):
    BASE_FIELDS = re.compile(
        # Make sure we're matching prefixes
        r'^('
        # Don't match characterattackspeed or characterclass
        r'(character(?!attackspeed|class))|'
        # All defensive prefixes
        r'defensive|'
        # All offensive prefixes
        r'offensive|'
        # And lastly all retaliation prefixes
        r'retaliation'
        r')'
    )

    # Regex to remove the {} prefixes in texts:
    BRACKETS = re.compile(r'\{[^)]*\}')

    # Regex to remove inline comments in texts:
    INLINE = r'(.*)\/\/(.*)'
    INLINE_REPLACE = r'\1'

    # These resources are manually inserted:
    CUSTOM_RESOURCES = [
        ['damageabsorption', '{%.0f0} ({%s1}) Damage Absorption'],
        ['damageabsorptionpercent', '{%.0f0}% ({%s1}) Damage Absorption'],
        ['retaliationstun', ' second(s) of Stun retaliation'],
        ['projectileexplosionradius', '{%.0f0} Meter Radius'],
        ['skillactiveduration', '{%.0f0} Second Duration'],
        ['skillcooldowntime', '{%.1f0} Second(s) Recharge'],
        # Can't use 'manacost' entry because of incorrect spacing
        ['skillmanacost', '{%.0f0} Energy Cost'],
        ['skilltargetradius', '{%.0f0} Meter Radius'],
    ]

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
        ['projectilefragmentslaunchnumberranged',
         'projectilefragmentslaunchnumberminmax'],
        ['skillprojectilenumber', 'projectilelaunchnumber'],
        ['skilltargetangle', 'targetangle'],
        ['skilltargetnumber', 'targetnumber'],
        ['spawnobjectstimetolive', 'skillpettimetolive'],
    ]

    # These resources need a replace or regex replace to have the right names:
    REPLACEMENTS = [{
        'type': 'regex',
        'find': r'damagemodifier(.*)',
        'replace': r'offensive\1modifier',
    }, {
        'type': 'regex',
        'find': r'damagedurationmodifier(.*)',
        'replace': r'offensiveslow\1modifier',
    },  {
        # DamageDuration prefix
        'type': 'replace',
        'find': 'damageduration',
        'replace': 'offensiveslow',
    }, {
        # Damage prefix
        'type': 'replace',
        'find': 'damage',
        'replace': 'offensive',
    }, {
        # Defense prefix
        'type': 'replace',
        'find': 'defense',
        'replace': 'defensive',
    }, {
        'type': 'regex',
        'find': r'retaliationmodifier(.*)',
        'replace': r'retaliation\1modifier',
    }, {
        'type': 'regex',
        'find': r'retaliationdurationmodifier(.*)',
        'replace': r'retaliationslow\1modifier',
    },  {
        'type': 'replace',
        'find': 'retaliationduration',
        'replace': 'retaliationslow',
    }]

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

    def load_locale(self, locale):
        self.locale = locale.lower()

        for resource in self.TAG_RESOURCES:
            self.tags.update(
                # Remove brackets from tag texts:
                (k, self.BRACKETS.sub('', v))
                for k, v in self.parse_text_resource(resource).items())

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

        # Insert a few custom resources that are otherwise incorrect:
        self.strings.update(dict(
            (custom[0], custom[1]) for custom in self.CUSTOM_RESOURCES))

        # Now replace words that are different in DBR files such as
        # 'damage' becoming 'offensive':
        replacements = {}
        for key, value in self.strings.items():
            for repl in self.REPLACEMENTS:
                if repl['type'] == 'regex':
                    # Replace all regex matches:
                    pattern = re.compile(repl['find'])
                    if re.match(pattern, key):
                        new_key = re.sub(pattern, repl['replace'], key)
                        replacements[new_key] = value
                        break
                else:
                    # Simply replace (if it's a prefix)
                    prefix = repl['find']
                    if key.startswith(prefix):
                        new_key = key.replace(prefix, repl['replace'], 1)
                        replacements[new_key] = value
                        break

        # Now merge the replacement strings:
        self.strings.update(replacements)

        # Track ranged separately, we can't update a dict while iterating:
        ranged = dict()

        # Iterate over all known strings now
        for key, value in self.strings.items():
            # Update the regex structure for all strings that have regex:
            if re.search(self.REGEX_OLD, value):
                # Replace the TQ regex with a Python regex:
                for match in re.finditer(self.REGEX_OLD, value):
                    value = value.replace(
                        match.group(),
                        self.REGEX_NEW.format(**match.groupdict()))
            # All other base fields need a numeric prefix for values
            elif self.BASE_FIELDS.match(key):
                # Add a decimal ranged variant for values that have seconds:
                if 'second' in value:
                    # Also add a ranged formatter:
                    ranged[key + 'ranged'] = '{0:.1f} ~ {1:.1f}' + value
                    value = '{0:.1f}' + value
                else:
                    # Also add a ranged formatter:
                    ranged[key + 'ranged'] = '{0:.0f} ~ {1:.0f}' + value
                    value = '{0:.0f}' + value

            self.strings[key] = value

        # Now that iteration is done, merge the ranged formats:
        self.strings.update(ranged)

        # Last but not least, merge the entirety of text resources:
        self.texts = {**self.tags, **self.strings}

        # Output the dictionary so it can be reviewed during parsings:
        with open('output/texts.json', 'w', encoding='utf8') as texts_file:
            json.dump(
                self.texts,
                texts_file,
                ensure_ascii=False,
                sort_keys=True)

    def tag(self, tag):
        """
        Return the friendly name for a tag.

        If no friendly name was found, return the tag itself.

        """
        return self.texts.get(tag.lower(), tag)

    def has(self, string):
        """
        Returns a boolean indicating whether or not this string is known.

        """
        return string.lower() in self.strings

    def has_tag(self, tag):
        """
        Returns a boolean indicating whether or not this tag is known.

        """
        return tag.lower() in self.tags

    def get(self, string):
        """
        Return the friendly value, ready for formatting, for a string.

        """
        return self.texts[string.lower()]

    def parse_text_resource(self, text_file):
        """
        Parse a text resource file, for a certain locale.

        """
        f = self.BASE_DIR / self.locale / text_file

        try:
            # Most files have UTF-16 or RAW encoding
            lines = [l.rstrip('\n') for l in open(f, encoding='utf16')]
        except UnicodeError:
            # Some files have ??? encoding (literally)
            lines = [l.rstrip('\n') for l in open(f)]
        except FileNotFoundError:
            # Log error and move on:
            logging.warning(f'Text resource file missing: {text_file}')

            # Return an empty dict not to break the loop
            return {}

        # Parse line into a dictionary of key, value properties:
        return dict(
            # Keys are lowercased, inline comments are removed
            (k.lower(), re.sub(self.INLINE, self.INLINE_REPLACE, v))
            for k, v in (
                properties.split('=', 1) for properties in lines
                if '=' in properties and not properties.startswith('//')))


# Prepare an instance for usage:
texts = Texts()
