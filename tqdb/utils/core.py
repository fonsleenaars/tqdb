"""
Utility functions.

"""
import argparse
import os
import sys

from tqdb.constants.resources import DB, TEX
from tqdb.parsers.util import format_path
from tqdb.utils.images import save_bitmap


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
def index_equipment(files, parser, label):
    equipment = {}
    items = {}

    for index, dbr in enumerate(files):
        print_progress(f'Parsing {label}', index, len(files))
        parsed, category = pluck(parser.parse(dbr, include_type=True),
                                 'parsed',
                                 'class')

        # The equipment files have some unwanted files, check classification:
        if not parsed or 'classification' not in parsed or not parsed['name']:
            continue

        # Save the bitmap and remove the bitmap key
        save_bitmap(parsed, category, 'output/graphics/', TEX)

        # Add to the global equipment list:
        equipment[format_path(dbr.replace(DB, ''))] = parsed

        # Organize the equipment based on the category
        if category and category in items:
            items[category].append(parsed)
        elif category:
            items[category] = [parsed]

    return items, equipment


def pluck(d, *k):
    return [d[i] for i in k]
