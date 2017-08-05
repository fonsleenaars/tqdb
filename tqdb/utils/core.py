"""
Utility functions.

"""
import argparse
import glob
import os
import subprocess
import sys

from tqdb.constants.resources import DB
from tqdb.parsers.util import format_path


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
#                             BITMAP UTILITY                              #
###########################################################################
def save_bitmap(item):
    bitmap = ''
    tag = item[TAG]

    # Check what kind of bitmap exists:
    if BITMAP_ARTIFACT in item:
        bitmap = item[BITMAP_ARTIFACT]

        # Now remove the bitmap from the item:
        del(item[BITMAP_ARTIFACT])

    elif BITMAP_FORMULA in item:
        # Formula's all share 3 possible icons (lesser, greater, artifact):
        bitmap = item[BITMAP_FORMULA]
        tag = item[CLASSIFICATION].lower()

        del(item[BITMAP_FORMULA])
    elif BITMAP_ITEM in item:
        # If the file already exists, append a counter:
        if (item.get(CLASSIFICATION, None) != ITEM_RARE and
           os.path.isfile(graphics_dir + tag + '.png')):
            # Append the type:
            counter = 1
            images = glob.glob(graphics_dir)
            for image in enumerate(images):
                if tag in images:
                    counter += 1

            tag += '-' + str(counter)

        bitmap = item[BITMAP_ITEM]

        # Now remove the bitmap from the item:
        del(item[BITMAP_ITEM])
    elif BITMAP_RELIC in item:
        bitmap = item[BITMAP_RELIC]

        # Now remove the bitmap from the item:
        del(item[BITMAP_RELIC])

    # Run the texture viewer if a bitmap and tag are set:
    if bitmap and tag and os.path.isfile(tex_dir + bitmap):
        command = ['utils/textureviewer/TextureViewer.exe',
                   tex_dir + bitmap,
                   graphics_dir + tag + '.png']
        subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)


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
        if not parsed or 'classification' not in parsed:
            continue

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
