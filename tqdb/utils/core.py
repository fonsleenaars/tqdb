"""
Utility functions.

"""
import argparse
import os
import sys


###########################################################################
#                           ARGPARSE UTILITY                              #
###########################################################################
class FullPaths(argparse.Action):
    """
    Expand user- and relative-paths.

    """

    def __call__(self, parser, namespace, values, option_string=None):
        setattr(namespace, self.dest, os.path.abspath(os.path.expanduser(values)))


def is_dir(dirname):
    """
    Checks if a path is an actual directory.

    """
    if not os.path.isdir(dirname) and not os.path.isfile(dirname):
        msg = "{0} is not a directory or file".format(dirname)
        raise argparse.ArgumentTypeError(msg)
    else:
        return dirname


###########################################################################
#                                CLI UTILITY                              #
#               Credit: http://stackoverflow.com/a/13685020               #
###########################################################################
def print_progress(label, i, end_val, bar_length=20):
    percent = float(i + 1) / end_val
    hashes = "#" * int(round(percent * bar_length))
    spaces = " " * (bar_length - len(hashes))

    if i == end_val - 1:
        print("\r{0:45} [{1}] DONE".format(label, hashes + spaces))
    else:
        # Write out the progress
        progress = int(round(percent * 100))
        sys.stdout.write("\r{0:45} [{1}] {2}%".format(label, hashes + spaces, progress))
        sys.stdout.flush()


###########################################################################
#                              PARSE UTILITY                              #
###########################################################################
def get_affix_table_type(file_prefix):
    """
    Retrieve the minimal prefix for an affix file name.

    The result of these is used to i18n the equipment types an affix can
    occur on in the frontend.

    """
    for prefix in [
        # Both arm and arms are used:
        "armmage",
        "armsmage",
        "armmelee",
        "armsmelee",
        "headmage",
        "headmelee",
        # Both leg and legs are used:
        "legmage",
        "legsmage",
        "legmelee",
        "legsmelee",
        "torsomage",
        "torsomelee",
        "amulet",
        "ring",
        "shield",
        "axe",
        "bow",
        "club",
        "spear",
        "staff",
        "sword",
        # Ranged one-hand; throwing weapons
        "roh"
    ]:
        if file_prefix.startswith(prefix):
            return prefix

    # Fallback to just the file prefix:
    return file_prefix


def is_duplicate_affix(affixes, affix):
    """
    Check if the properties for an affix are already known.

    """
    for properties in affixes["properties"]:
        if properties == affix["properties"]:
            return True

    return False


def pluck(d, *k):
    return [d[i] for i in k]
