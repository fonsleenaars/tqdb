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
        setattr(
            namespace,
            self.dest,
            os.path.abspath(os.path.expanduser(values)))


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
def print_progress(label,  i, end_val, bar_length=20):
    percent = float(i + 1) / end_val
    hashes = '#' * int(round(percent * bar_length))
    spaces = ' ' * (bar_length - len(hashes))

    if i == end_val - 1:
        print("\r{0:45} [{1}] DONE".format(label, hashes + spaces))
    else:
        # Write out the progress
        progress = int(round(percent * 100))
        sys.stdout.write("\r{0:45} [{1}] {2}%".format(label,
                                                      hashes + spaces,
                                                      progress))
        sys.stdout.flush()


###########################################################################
#                              PARSE UTILITY                              #
###########################################################################
def get_affix_table_type(file_prefix):
    """
    Retrieve a friendly name for an affix table.

    This transforms something like 'headmage' into 'Head (Mage)'

    """
    if file_prefix.startswith('armsmage'):
        return 'Arms (Mage)'
    elif file_prefix.startswith('armsmelee'):
        return 'Arms (Melee)'
    elif file_prefix.startswith('headmage'):
        return 'Head (Mage)'
    elif file_prefix.startswith('headmelee'):
        return 'Head (Melee)'
    elif file_prefix.startswith('legmage'):
        return 'Legs (Mage)'
    elif file_prefix.startswith('legmelee'):
        return 'Legs (Melee)'
    elif file_prefix.startswith('torsomage'):
        return 'Chest (Mage)'
    elif file_prefix.startswith('torsomelee'):
        return 'Chest (Melee)'
    elif file_prefix.startswith('amulet'):
        return 'Amulet'
    elif file_prefix.startswith('ring'):
        return 'Ring'
    elif file_prefix.startswith('shield'):
        return 'Shield'
    elif file_prefix.startswith('axe'):
        return 'Axe'
    elif file_prefix.startswith('bow'):
        return 'Bow'
    elif file_prefix.startswith('club'):
        return 'Club'
    elif file_prefix.startswith('spear'):
        return 'Spear'
    elif file_prefix.startswith('staff'):
        return 'Staff'
    elif file_prefix.startswith('sword'):
        return 'Sword'


def pluck(d, *k):
    return [d[i] for i in k]
