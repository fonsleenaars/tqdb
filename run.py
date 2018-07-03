import argparse
import json
import logging
import os

from tqdb import __version__ as tqdb_version
from tqdb import main
from tqdb.utils import images
from tqdb.utils.text import texts

# Disable any DEBUG logging from PIL:
logging.getLogger('PIL').setLevel(logging.WARNING)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(message)s',
    datefmt='%H:%M')


def tqdb():
    """
    Run the Titan Quest Database parser.

    """
    # Directory preparations for bitmap
    if not os.path.exists('output/graphics'):
        os.makedirs('output/graphics')

    # Parse command line parameters
    argparser = argparse.ArgumentParser(description='TQ Database parser')
    argparser.add_argument(
        '-l',
        '--locale',
        action='store',
        default='EN',
        nargs=1,
        choices=['CH', 'CZ', 'DE', 'EN', 'ES', 'FR', 'IT', 'JA', 'KO', 'PL',
                 'RU', 'UK'],
        help=('Specify the two letter locale you want to parse (default: '
              '%(default))'))

    # Grab the arguments:
    args = argparser.parse_args()

    # Prepare the texts based on the locale:
    texts.load_locale(args.locale)

    data = {
        'affixes': main.parse_affixes(),
        'equipment': main.parse_equipment(),
        'sets': main.parse_sets(),
        'skills': main.parse_skills(),
    }

    logging.info('Writing output to files...')
    images.SpriteCreator('output/graphics/', 'output')

    output_name = f'output/tqdb.{args.locale.lower()}.{tqdb_version}.json'
    with open(output_name, 'w') as data_file:
        json.dump(data, data_file, sort_keys=True)


if __name__ == '__main__':
    tqdb()
