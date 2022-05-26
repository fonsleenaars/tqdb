"""
Text utility functions

These text related functions are the strings that are displayed for attributes,
item names, and all other properties used in Titan Quest.abs

"""
import json
import logging
import os
import re

from tqdb.constants import paths


class Texts:
    """
    Class holding all TQ equipment, skill, and attribute texts.

    """

    # Regex to remove the {} prefixes in texts:
    BRACKETS = re.compile(r"\{[^)]*\}")

    # Regex to remove an infrequent ^letter in a property:
    FORMATTER = re.compile(r"\^[a-z]")

    # Regex to remove inline comments in texts:
    INLINE = r"(.*)\/\/(.*)"
    INLINE_REPLACE = r"\1"

    # Regex to find declensions:
    DECLENSIONS = r"\[[a-z]*\]"

    # These resources need to be copied from existing ones, under a new name:
    COPY_RESOURCES = [
        # The misspelling of charcteritemglobalreduction is "correct", that's
        # how the files list it.
        ["characterglobalreqreduction", "charcteritemglobalreduction"],
        ["characterdeflectprojectile", "characterdeflectprojectiles"],
        ["defensiveabsorption", "defenseabsorptionmodifier"],
        ["defensiveprotection", "defenseabsorptionprotection"],
        ["defensiveslowlifeleach", "defenselifeleach"],
        ["defensiveslowlifeleachduration", "defenselifeleachduration"],
        ["defensiveslowmanaleach", "defensemanaleach"],
        ["defensiveslowmanaleachduration", "defensemanaleachduration"],
        ["defensivetotalspeed", "totalspeedresistance"],
        ["offensivebaselife", "tagdamagebasevitality"],
        ["offensivefumble", "damagedurationfumble"],
        ["offensiveprojectilefumble", "damagedurationprojectilefumble"],
        ["offensivepierceratio", "damagebasepierceratio"],
        ["offensiveslowdefensivereductionmodifier", "damagedurationdefensivereduction"],
        ["projectilefragmentslaunchnumberranged", "projectilefragmentslaunchnumberminmax"],
        ["projectilepiercing", "projectilepiercingchance"],
        # Some locales simply don't have a refresh time tag (Chinese)
        ["refreshtime", "skillrefreshtime"],
        ["skillcooldowntime", "cooldowntime"],
        ["skillprojectilenumber", "projectilelaunchnumber"],
        ["skilltargetangle", "targetangle"],
        ["skilltargetnumber", "targetnumber"],
        ["spawnobjectstimetolive", "skillpettimetolive"],
    ]

    # These resources need a replace or regex replace to have the right names:
    REPLACEMENTS = [
        {
            "type": "regex",
            # Example: damageModifierLigthning
            "find": r"damagemodifier(.*)",
            # => offensiveLightningModifier
            "replace": r"offensive\1modifier",
        },
        {
            "type": "regex",
            # Example: damageDurationModifierLightning
            "find": r"damagedurationmodifier(.*)",
            # => offensiveSlowLightningModifier
            "replace": r"offensiveslow\1modifier",
        },
        {
            "type": "replace",
            # Example: damageDurationLightning
            "find": "damageduration",
            # => offensiveSlowLightning
            "replace": "offensiveslow",
        },
        {
            "type": "replace",
            # Example: damageFire
            "find": "damage",
            # => offensiveFire
            "replace": "offensive",
        },
        {
            "type": "replace",
            # Example: defenseLightning
            "find": "defense",
            # => defensiveLightning
            "replace": "defensive",
        },
        {
            "type": "regex",
            # Example: retaliationModifierFire
            "find": r"retaliationmodifier(.*)",
            # => retaliationFireModifier
            "replace": r"retaliation\1modifier",
        },
        {
            "type": "regex",
            # Example: retalationDurationModifierFire
            "find": r"retaliationdurationmodifier(.*)",
            # => retaliationSlowFireModifier
            "replace": r"retaliationslow\1modifier",
        },
        {
            "type": "replace",
            # Example: retaliationDurationFire
            "find": "retaliationduration",
            # => retaliationSlowFire
            "replace": "retaliationslow",
        },
    ]

    # These resource files hold strings that map a tag to a name.
    TAG_RESOURCES = [
        "commonequipment.txt",
        "xcommonequipment.txt",
        "x2commonequipment.txt",
        "x3items_nonvoiced.txt",
        "x4items_nonvoiced.txt",
        "menu.txt",
        "monsters.txt",
        "xmonsters.txt",
        "x2monsters.txt",
        "x3mainquest.txt",
        "x4mainquest.txt",
        "x3mainquest_nonvoiced.txt",
        "x4mainquest_nonvoiced.txt",
        "x3misctags_nonvoiced.txt",
        "x4misctags_nonvoiced.txt",
        "x3nametags_nonvoiced.txt",
        "x4nametags_nonvoiced.txt",
        "npc.txt",
        "xnpc.txt",
        "x2npc.txt",
        "quest.txt",
        "xquest.txt",
        "x2quest.txt",
        "x3servicenpcs.txt",
        "x3sidequests.txt",
        "x3sidequests_nonvoiced.txt",
        "x4sidequests_nonvoiced.txt",
        "skills.txt",
        "xskills.txt",
        "x2skills.txt",
        "tutorial.txt",
        "uniqueequipment.txt",
        "xuniqueequipment.txt",
        "x2uniqueequipment.txt",
    ]

    # These resource files hold strings that require some formatting
    STRING_RESOURCES = [
        "ui.txt",
        "xui.txt",
        "x2ui.txt",
        "x3basegame_nonvoiced.txt",
        "x4basegame_nonvoiced.txt",
    ]

    # Old regex structure used in Titan Quest's resource text files
    REGEX_OLD = (
        r"{(?P<pre_signed>\-?\+?)%" r"(?P<post_signed>\+?)" r"(?P<decimals>\.?[0-9]?)" r"(?P<type>[a-z])(?P<arg>[0-9])}"
    )

    # New python friendly regex structure
    REGEX_NEW = "{{{arg}:{pre_signed}{post_signed}{decimals}{type}}}"

    def __init__(self):
        """
        Prepare directory for parsing output.

        """
        if not os.path.exists(paths.PARSING):
            os.makedirs(paths.PARSING)

    def load_locale(self, locale):
        self.locale = locale.lower()
        self.strings = {}
        self.tags = {}

        for resource in self.TAG_RESOURCES:
            self.tags.update(
                # Remove brackets from tag texts:
                (k, self.BRACKETS.sub("", v))
                for k, v in self.parse_text_resource(resource).items()
            )

        for resource in self.STRING_RESOURCES:
            self.strings.update((k, self.FORMATTER.sub("", v)) for k, v in self.parse_text_resource(resource).items())

        # Some strings require formatting to replace their TQ regex structure
        # with a python friendly one, others need some replacements in their
        # property names, and some fields are missing from the text database.

        # Begin by removing all tag, xtag and x2tag prefixes:
        self.strings.update(dict((k[3:], v) for (k, v) in self.strings.items() if k.startswith("tag")))
        self.strings.update(dict((k[4:], v) for (k, v) in self.strings.items() if k.startswith("xtag")))
        self.strings.update(dict((k[5:], v) for (k, v) in self.strings.items() if k.startswith("x2tag")))

        # Energy cost for a skill is formatted using a locale dependent format
        # such as '{%.0f0 %s1}' for the english locale.
        self.strings["skillmanacost"] = (
            self.strings["skillcostformat"]
            # Replace the { and }
            .replace("{", "").replace("}", "")
            # The string component becomes 'Duration'
            .replace("%s1", self.strings["manacost"])
            # The regex component becomes the regular {0:.1f} format
            .replace("%.0f0", "{0:.0f}")
        )

        # Active health or energy cost is formatted using a locale dependent
        # format such as '{%.1f0 %s1}'
        self.strings["skillactivelifecost"] = (
            self.strings["skillfloat1format"]
            # Replace the { and }
            .replace("{", "").replace("}", "")
            # The string component becomes 'Active Health Per Second'
            # Make sure to incorporate the extraneous space in the search
            .replace(" %s1", self.strings["activelifecost"])
            # The regex component becomes the regular {0:.1f} format
            .replace("%.1f0", "{0:.0f}")
        )
        self.strings["skillactivemanacost"] = (
            self.strings["skillfloat1format"]
            # Replace the { and }
            .replace("{", "").replace("}", "")
            # The string component becomes 'Active Health Per Second'
            # Make sure to incorporate the extraneous space in the search
            .replace(" %s1", self.strings["activemanacost"])
            # The regex component becomes the regular {0:.1f} format
            .replace("%.1f0", "{0:.0f}")
        )

        # "X Second Duration" is only available as: '{%.1f0 Second %s1}'
        # which is formatted depending on the locale.
        self.strings["skillactiveduration"] = (
            self.strings["skillsecondformat"]
            # Replace the { and }
            .replace("{", "").replace("}", "")
            # The string component becomes 'Duration'
            .replace("%s1", self.strings["activeduration"])
            # The regex component becomes the regular {0:.1f} format
            .replace("%.1f0", "{0:.1f}")
        )

        # "X Meter Radius" is only available as '{%.1f0 Meter %s1}'
        # which is formatted depending on the locale.
        distance = (
            self.strings["skilldistanceformat"]
            # Replace the { and }
            .replace("{", "").replace("}", "")
            # The string component becomes 'Radius'
            .replace("%s1", self.strings["targetradius"])
            # The regex component becomes the regular {0:.1f} format
            .replace("%.1f0", "{0:.1f}")
        )
        self.strings["projectileexplosionradius"] = distance
        self.strings["skilltargetradius"] = distance

        # Stun retaliation incorrectly is missing "second(s) of"
        stun_retaliation = self.strings["retaliationstun"].split(" ")
        stun_damage = self.strings["damagestun"]
        for word in stun_retaliation:
            if not word or word not in stun_damage:
                continue

            # "Stun" found, replace with full "stun damage" string.
            # This means that:
            # Stun Retaliation => second(s) of Stun Retaliation
            self.strings["retaliationstun"] = stun_damage.replace(word, self.strings["retaliationstun"].strip())

            # Stun retaliation has been fixed, we're done
            break

        # Taunt is missing the whole prefix of 'Second(s) of' so copy it from:
        # stun retaliation, which we know has been fixed:
        borrowed = " ".join(stun_retaliation)
        self.strings["damagetaunt"] = (
            # This is the full 'Second(s) of Stun Retaliation' text.
            self.strings["retaliationstun"].replace(
                # This is the verified 'Stun retaliation' text
                borrowed,
                # This is the incorrect but verified 'Taunt' text
                self.strings["damagetaunt"],
            )
        )

        # Copy over a few strings under a new property name, to match the
        # property that's set in the DBR files.
        for new_key, old_key in self.COPY_RESOURCES:
            try:
                self.strings[new_key] = self.strings[old_key]
            except KeyError:
                logging.warning(f"This locale is missing {old_key}")
                continue

        # Track dictionary for replacements
        replacements = {}

        for key, value in self.strings.items():
            # Update the regex structure for all strings that have regex:
            if re.search(self.REGEX_OLD, value):
                # Replace the TQ regex with a Python regex:
                for match in re.finditer(self.REGEX_OLD, value):
                    value = value.replace(match.group(), self.REGEX_NEW.format(**match.groupdict()))

                # After all the regex updating is completed, store the string:
                self.strings[key] = value

            # Now replace words that are different in DBR files such as
            # 'damage' becoming 'offensive':
            for repl in self.REPLACEMENTS:
                if repl["type"] == "regex":
                    # Replace all regex matches:
                    pattern = re.compile(repl["find"])
                    if re.match(pattern, key):
                        new_key = re.sub(pattern, repl["replace"], key)
                        replacements[new_key] = value
                        break
                else:
                    # Simply replace (if it's a prefix)
                    prefix = repl["find"]
                    if key.startswith(prefix):
                        new_key = key.replace(prefix, repl["replace"], 1)
                        replacements[new_key] = value
                        break

        # Now merge the replacement strings:
        self.strings.update(replacements)

        # Last but not least, merge the entirety of text resources:
        self.texts = {**self.tags, **self.strings}

        # Output the dictionary so it can be reviewed during parsings:
        output_name = paths.OUTPUT / f"texts.{self.locale}.json"
        with open(output_name, "w", encoding="utf8") as texts_file:
            json.dump(self.texts, texts_file, ensure_ascii=False, sort_keys=True)

    def has(self, string):
        """
        Returns a boolean indicating whether or not this string is known.

        """
        return string.lower() in self.texts

    def get(self, string):
        """
        Return the friendly value, ready for formatting, for a string.

        If no friendly name was found, return the string itself.

        """
        # Grab the text value, falling back on the key string:
        text_value = self.texts.get(string.lower(), string)

        # Split any declensions (remove empty start):
        declensions = filter(None, re.split(self.DECLENSIONS, text_value))

        # Remove duplicates
        declensions = list(set(declensions))

        # Return comma joined string:
        # Replace any declension occurences ([fs], [ms], [mp], ...):
        return ", ".join(declensions)

    def parse_text_resource(self, text_file):
        """
        Parse a text resource file, for a certain locale.

        """
        f = paths.RES / self.locale / text_file

        try:
            # Most files have UTF-16 or RAW encoding
            lines = [l.rstrip("\n") for l in open(f, encoding="utf16")]
        except UnicodeError:
            # Some files have ??? encoding (literally)
            lines = [l.rstrip("\n") for l in open(f)]
        except FileNotFoundError:
            # Log error and move on:
            logging.warning(f"Text resource file missing: {text_file}")

            # Return an empty dict not to break the loop
            return {}

        # Parse line into a dictionary of key, value properties:
        return dict(
            # Keys are lowercased, inline comments are removed
            (k.lower(), re.sub(self.INLINE, self.INLINE_REPLACE, v))
            for k, v in (
                properties.split("=", 1)
                for properties in lines
                if "=" in properties and not properties.startswith("//")
            )
        )


# Prepare an instance for usage:
texts = Texts()
