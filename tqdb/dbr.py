"""
Main TQDB parser for the dbr files.

This is the main parser that can take a DBR file and return the defined
and relevant information for that file.

Upon receiving a file to parse it will grab the template associated with
the DBR and then parse it according to all properties in that template.

"""
import logging

from tqdb.parsers.main import parsers
from tqdb.templates import templates, templates_by_path


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
        return [{}]

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
    dbr = read(dbr_file)

    # If a template exists for this type, parse it accordingly:
    template = get_template(dbr, dbr_file)

    # Initialize an empty result, this variable will be updated by the parsers.
    result = {
        # Properties will be filled by all core attribute parsers, like
        # character, offensive, defensive, etc.
        'properties': {}
    }

    # Begin updating the result by the first template parser, if available:
    if template.key in parsers:
        parsers[template.key].parse(dbr, result)

    # Now update the result by parsing all the included templates:
    for t in template.templates:
        if t not in parsers:
            logging.warning(f'Skipping {t}, no parser found.')
            continue

        parsers[t].parse(dbr, result)

    return result
