import glob
import os
import pprint
import re

DATA_DIR = 'data\\'
TEMPLATE_DIR = '%TEMPLATE_DIR%'
TEMPLATE_PREFIX = 'data\\database\\templates\\'
VARIABLE_REGEX = re.compile(r'Variable\n{\n(?P<variables>[^}]*)\n}')

variables = {}


def prepare_path(template):
    """
    Prepare a path for a linked template, as well as its key.

    The path to a template starts from within the `DATA_DIR`. The linked
    resource will take it from there, although on ocassion a %TEMPLATE_DIR%
    prefix is present, which needs to be removed.

    The key requires all backslashes are replaced by an underscore, and the
    template directory (`TEMPLATE_PREFIX`) prefix needs to be removed.

    Args:
        template (str): Path to turn into a key

    Returns:
        A string that's safe to use as a unique key for a dictionary.
    """
    if not template.startswith(DATA_DIR):
        template = os.path.join(DATA_DIR, template)
    template = template.replace(TEMPLATE_DIR, '')

    return (
        # The first tuple is the path to the new template
        template,
        # The second tuple is the key for the new template
        template
        .replace('\\', '_')
        .lower()
        [len(TEMPLATE_PREFIX):])


def read_variables(variable, template_key):
    # Create a dictionary with all properties from this variable
    properties = dict(
        # Remove all quotes, split the line from a key = value format
        [i.replace('"', '').strip() for i in line.split('=', 1)]
        # For all the lines (split them by newline character)
        for line in variable.split('\n'))

    if properties['class'] == 'variable':
        # Add this variable to the template
        variables[template_key].add(properties['name'])
    elif properties['type'] == 'include':
        # Parse the included file first:
        include_file, include_key = prepare_path(properties['defaultValue'])

        if include_key not in variables:
            read_template(include_file)

        # Add all variables from the included template
        variables[template_key] |= variables[include_key]


def read_template(template):
    # Open and read the file, remove all the tabs:
    content = open(template, 'r').read().replace('\t', '')

    template, template_key = prepare_path(template)

    # Initialize the variable set for this template
    variables[template_key] = set()

    matches = VARIABLE_REGEX.findall(content)
    for match in matches:
        read_variables(match, template_key)


templates = glob.glob('data\\database\\templates\\**\\*.tpl')
for template in templates:
    read_template(template)

pprint.PrettyPrinter().pprint(variables)
