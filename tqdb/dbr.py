"""
Main TQDB parser for the dbr files.

This is the main parser that can take a DBR file and return the defined
and relevant information for that file.

Upon receiving a file to parse it will grab the template associated with
the DBR and then parse it according to all properties in that template.

"""
import logging

from tqdb import storage
from tqdb.parsers.main import load_parsers, InvalidItemError
from tqdb.templates import templates, templates_by_path


parsers = {}


def get_template(dbr, dbr_file):
    """
    Attempts to retrieve a template for a DBR.

    :param dbr: a dict with key 'templateName' referring to a template file,
        or with key 'Class' referring to a template with a "Class" variable with
        that "defaultValue"
    :param dbr_file: the file the dbr came from, for logging purposes
    """
    if "templateName" in dbr:
        # The template path is set, retrieve it from the collection:
        return templates_by_path[dbr["templateName"].lower()]
    elif "Class" in dbr and dbr["Class"].lower() in templates:
        # The name of the template is set:
        return templates[dbr["Class"].lower()]

    # Unknown template, or template is not in our collection:
    raise Exception(f"Template could not be found for {dbr_file}")


def read(dbr):
    """
    Read a DBR file and split its contents into key, value properties.
    May return an empty dict if certain errors occur.

    """
    try:
        with open(dbr) as dbr_file:
            result = {}

            # DBR lines always end with ',\n' which we remove
            lines = (line.rstrip(",\n") for line in dbr_file)

            # Only add properties that have the correct format per line
            # of: key,value
            properties = dict(tuple(line.split(",", 1)) for line in lines if "," in line)
    except FileNotFoundError:
        logging.debug(f"No file found for {dbr}. ")
        return {}
    except PermissionError as e:
        logging.exception(f"Could not open {dbr}")
        return {}

    # The 'templateName' property isn't in any Template, so add
    # manually:
    if "templateName" in properties:
        result["templateName"] = properties["templateName"]

    # Get the template for this DBR
    template = get_template(properties, dbr)

    def parse_vars_to_tuples(variables_dict):
        for name, variable in variables_dict.items():
            if name in properties:
                parsed_value = variable.parse_value(properties[name])
                # Omit None, False, zero, and empty collections
                if parsed_value:
                    yield name, parsed_value

    # Now parse all properties using the Template:
    result.update(dict(parse_vars_to_tuples(template.variables)))

    return result


def parse(dbr_file, references=None):
    """
    Parse a DBR file according to its template.

    """
    if references is None:
        references = {}
    # Initialize the parsers map if necessary:
    global parsers
    if not parsers:
        parsers = load_parsers()

    # First check if the file has been parsed before:
    if dbr_file in storage.db:
        return storage.db[dbr_file]

    logging.debug(f"Parsing {dbr_file}")
    dbr = read(dbr_file)

    # Initialize an empty result, this variable will be updated by the parsers.
    result = {
        # Properties will be filled by all core attribute parsers, like
        # character, offensive, defensive, etc.
        "properties": {},
        # Any parser can pass references that another parser can then use:
        "references": references,
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
        try:
            prioritized_parser.parse(dbr, dbr_file, result)
        except InvalidItemError as e:
            # One of the parsers has determined this file shouldn't be parsed:
            raise InvalidItemError(
                f"Parser {prioritized_parser} for template key {prioritized_parser.template.key} "
                "tells us this item is invalid and should be ignored."
            ) from e

    # Pop the helper data references again:
    result.pop("references")

    # Retain the parsed result in memory, for reuse:
    storage.db[dbr_file] = result

    return result
