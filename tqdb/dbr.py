"""
Main TQDB parser for the dbr files.

This is the main parser that can take a DBR file and return the defined
and relevant information for that file.

Upon receiving a file to parse it will grab the template associated with
the DBR and then parse it according to all properties in that template.

"""
import logging

from tqdb import storage
from tqdb.parsers.main import load_parsers
from tqdb.templates import templates, templates_by_path


parsers = {}


def get_template(dbr, dbr_file):
    """
    Attempts to retrieve a template for a DBR.

    """
    if 'templateName' in dbr:
        # The template path is set, retrieve it from the collection:
        return templates_by_path[dbr['templateName'].lower()]
    elif 'Class' in dbr and dbr['Class'].lower() in templates:
        # The name of the template is set:
        return templates[dbr['Class'].lower()]

    # Unknown template, or template is not in our collection:
    raise Exception(f'Template could not be found for {dbr_file}')


def read(dbr):
    """
    Read a DBR file and split its contents into key, value properties.

    """
    try:
        dbr_file = open(dbr)
    except FileNotFoundError:
        logging.debug(f'No file found for {dbr}')
        return {}

    result = {}

    # All lines (delimited by ,\n) are (key, value) pairs:
    properties = dict(
        line.split(',') for line in
        [line.rstrip(',\n') for line in dbr_file])

    # The 'templateName' property isn't in any Template, so add manually:
    if 'templateName' in properties:
        result['templateName'] = properties['templateName']

    # Get the template for this DBR
    template = get_template(properties, dbr)

    # Now parse all properties using the Template:
    result.update(dict(
        (name, variable.parse_value(properties[name])) for
        name, variable in template.variables.items()
        if name in properties and
        variable.parse_value(properties[name])))

    return result


def parse(dbr_file):
    """
    Parse a DBR file according to its template.

    """
    logging.debug(f'Parsing {dbr_file}')

    # Initialize the parsers map if necessary:
    global parsers
    if not parsers:
        parsers = load_parsers()

    # First check if the file has been parsed before:
    if dbr_file in storage.db:
        return storage.db[dbr_file]

    dbr = read(dbr_file)

    # Initialize an empty result, this variable will be updated by the parsers.
    result = {
        # Properties will be filled by all core attribute parsers, like
        # character, offensive, defensive, etc.
        'properties': {}
    }

    # There are still non-existent references, make sure the DBR isn't empty:
    if not dbr:
        return result

    # If a template exists for this type, parse it accordingly:
    template = get_template(dbr, dbr_file)

    # Construct a list of parsers to organize by priority:
    prioritized = []

    # Begin updating the result by the first template parser, if available:
    if template.key in parsers:
        prioritized.append(parsers[template.key])

    # Add any inherited template parsers:
    for t in template.templates:
        if t not in parsers:
            continue
        prioritized.append(parsers[t])

    # Prioritize the list and then run through the parsers:
    prioritized.sort(key=lambda p: p.get_priority(), reverse=True)
    for prioritized_parser in prioritized:
        prioritized_parser.parse(dbr, dbr_file, result)

    # Set the parsed result in the storage db:
    storage.db[dbr_file] = result

    return result
