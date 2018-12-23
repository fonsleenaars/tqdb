import argparse
import json
import logging

from tqdb import __version__ as tqdb_version
from tqdb import main
from tqdb import storage
from tqdb.utils import images
from tqdb.utils.text import texts

# Disable any DEBUG logging from PIL:
logging.getLogger('PIL').setLevel(logging.WARNING)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(message)s',
    datefmt='%H:%M')

# Supported languages
LANGUAGES = [
    'ch', 'cz', 'de', 'en', 'es', 'fr',
    'it', 'ja', 'ko', 'pl', 'ru', 'uk',
]


def tqdb_language(language):
    """
    Run the parser for a specific language.

    """
    # Prepare the texts based on the language:
    logging.info(f'Parsing locale: {language}')
    texts.load_locale(language)

    data = {
        'affixes': main.parse_affixes(),
        'creatures': main.parse_creatures(),
        'equipment': main.parse_equipment(),
        'quests': main.parse_quests(),
        'sets': main.parse_sets(),
        'skills': main.parse_skills(),
    }

    logging.info('Writing output to files...')

    output_name = f'output/tqdb.{language.lower()}.{tqdb_version}.json'
    with open(output_name, 'w', encoding='utf8') as data_file:
        json.dump(data, data_file, ensure_ascii=False, sort_keys=True)


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
    argparser.add_argument(
        '-a',
        '--all-languages',
        action='store_true',
        default=False,
        dest='all_languages')

    # Grab the arguments:
    args = argparser.parse_args()

    if not args.all_languages:
        # Parse the specified language:
        tqdb_language(args.locale)

        # Create the sprite for a single language
        images.SpriteCreator('output/graphics/', 'output')

        # Stop here
        return

    # Parse all languages:
    for language in LANGUAGES:
        tqdb_language(language)
        storage.reset()

    # Create the sprite after all languages have been parsed:
    images.SpriteCreator('output/graphics/', 'output')

if __name__ == '__main__':
    tqdb()
