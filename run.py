import argparse
import json
import logging

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
    # Parse command line parameters
    argparser = argparse.ArgumentParser(description='TQ Database parser')
    argparser.add_argument(
        '-l',
        '--locale',
        action='store',
        default='en',
        type=lambda s: s.lower(),
        choices=['ch', 'cz', 'de', 'en', 'es', 'fr', 'it', 'ja', 'ko', 'pl',
                 'ru', 'uk'],
        help=('Specify the two letter locale you want to parse (default: '
              '%(default))'))

    # Grab the arguments:
    args = argparser.parse_args()

    # Prepare the texts based on the locale:
    texts.load_locale(args.locale)

    data = {
        'affixes': main.parse_affixes(),
        'creatures': main.parse_creatures(),
        'equipment': main.parse_equipment(),
        'sets': main.parse_sets(),
        'skills': main.parse_skills(),
    }

    logging.info('Writing output to files...')

    if data.get('equipment', None):
        # Only create a sprite if equipment was parsed:
        images.SpriteCreator('output/graphics/', 'output')

    output_name = f'output/tqdb.{args.locale.lower()}.{tqdb_version}.json'
    with open(output_name, 'w', encoding='utf8') as data_file:
        json.dump(data, data_file, ensure_ascii=False, sort_keys=True)


if __name__ == '__main__':
    tqdb()
