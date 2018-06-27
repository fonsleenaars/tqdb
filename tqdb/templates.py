import glob
import re

from pathlib import Path

DATA_DIR = Path('data')
DATABASE_DIR = DATA_DIR / 'database'
TEMPLATE_DIR = DATABASE_DIR / 'templates/**/*.tpl'
TEMPLATE_PREFIX = '%TEMPLATE_DIR%'

# Regex to match all Group or Variable lines, with a bracket on the next line
BRACKET_REGEX = re.compile(r'(Group|Variable)\s+{')
# Regex to place the bracket on the same line as the Group or Variable
BRACKET_REPLACE = r'\1 {'
# Regex to find all tabs
TAB_REGEX = re.compile(r'\t')
# Regex to find empty lines
EMPTY_LINE_REGEX = re.compile(r'\n\n')
# Replace empty lines with a single linebreak
EMPTY_LINE_REPLACE = r'\n'

VARIABLE_REGEX = re.compile(r'Variable {\n(?P<properties>[^}]*)\n}')

templates_by_path = {}
templates = {}


class Variable:
    """
    Variable entity in a TPL file.

    Variables in TPL files always have the following structure:

    Variable
    {
        name = ""
        class = "static|variable|array"
        type = "include|file_dbr|file_tex|string|real|int|bool"
        description = ""
        value = ""
        defaultValue = ""
    }

    """
    def __init__(self, content, groups):
        # Create a dictionary with all properties from this variable
        self.properties = dict(
            # Remove all quotes, split the line from a key = value format
            [i.replace('"', '').strip() for i in line.split('=', 1)]
            # For all the lines (split them by newline character)
            for line in content)

        # Store the full ancestry of group names:
        self.groups = groups

    def __getitem__(self, key):
        """
        Access Variable properties like a dictionary.

        The reason this method is implemented is that some properties of
        Variables are reserved keywords (class, for example) so accessing
        them is easier as a dictionary.

        """
        return self.properties[key]

    def is_template_reference(self):
        """
        Checks whether or not this Variable is a reference to another template.

        """
        return self['class'] == 'static' and self['type'] == 'include'

    def parse_value(self, value):
        """
        Parse a given value for this Variable.

        """
        if self['class'] == 'array':
            # Return a list of parsed values
            values = value.split(';')

            if len(values) == 1:
                return [self._parse(v) for v in values if self._parse(v)]

            # If more than one value was present, keep all values:
            return [self._parse(v, always_return=True) for v in values]

        # Return the singular parsed value:
        return self._parse(value)

    def _parse(self, value, always_return=False):
        """
        Internal parse function used in list comprehension.

        """
        if self['type'] == 'real':
            if always_return:
                return float(value)
            return float(value) if float(value) > 0 else None
        elif self['type'] == 'int':
            if always_return:
                return int(value)
            return int(value) if int(value) > 0 else None
        elif self['type'] == 'bool':
            if always_return:
                return bool(int(value))
            return bool(int(value)) if bool(int(value)) else None
        elif self['type'] in ['file_dbr', 'file_tex']:
            return DATABASE_DIR / value.lower()
        return value


class Template:
    """
    Template class representing a TPL file.

    """
    def __init__(self, tpl_file):
        template_file = Path(tpl_file)

        try:
            # Make sure the path DATA_DIR is present
            template_file.relative_to(DATA_DIR)
        except ValueError:
            template_file = DATA_DIR / template_file

        # Prepare the path of this template as a key for the templates mapping
        self.file = template_file
        self.key = str(template_file.relative_to(DATA_DIR)).lower()

        # Open and read the file:
        content = open(self.file, 'r').read()

        # Variables will be the full map of variables (key = variable name)
        self.variables = {}
        # Templates is a set of all included template paths
        self.templates = list()

        # First move all the brackets '{' on the same line:
        content = BRACKET_REGEX.sub(BRACKET_REPLACE, content)

        # Remove all tab indentation:
        content = TAB_REGEX.sub('', content)

        # Remove all unnecessary newlines:
        content = EMPTY_LINE_REGEX.sub(EMPTY_LINE_REPLACE, content)

        # Split the content by line and recursively build the groups:
        self.parse_content(content.split('\n'), [])

        # Set the name of this template according to its Class:
        self.name = (self.variables['Class']['defaultValue'].lower()
                     if 'Class' in self.variables else None)

    def parse_content(self, content, ancestry):
        """
        Parse the content, which has been split by newline into a list.

        """
        bracket_count = 0

        # Iterate over the remaining content:
        index = 0
        while index < len(content):
            line = content[index]

            # Check if this a new group:
            if line == 'Group {':
                # Find the closing bracket for this group:
                bracket_count = 1
                closing_index = index
                while bracket_count > 0:
                    closing_index += 1

                    # Increment count for all new open brackets
                    if content[closing_index] in ['Variable {', 'Group {']:
                        bracket_count += 1
                    # Decrement for all we close
                    if content[closing_index] == '}':
                        bracket_count -= 1

                # Grab the group name, we don't care about type:
                name = (
                    # Grab the next line
                    content[index + 1]
                    # Remove the quotes
                    .replace('"', '')
                    # Split into key, value
                    .split('=', 1)
                    # Just grab the value
                    [1]
                    # Remove the whitespace
                    .strip())
                self.parse_content(
                    content[index + 1:closing_index],
                    # Add this groups name to the current ancestry
                    ancestry + [name])

                # Update the index to skip:
                index = closing_index
            elif line == 'Variable {':
                # Find the next closing bracket:
                closing_index = content.index('}', index + 1)

                self.parse_variable(
                    content[index + 1: closing_index],
                    ancestry)

                # Skip to the closing_index:
                index = closing_index

            index += 1

    def parse_variable(self, content, groups):
        variable = Variable(content, groups)

        if variable.is_template_reference():
            # Strip %TEMPLATE_DIR% from the file path if it's present:
            template_path = (variable['defaultValue']
                             .replace(TEMPLATE_PREFIX, '')
                             .lower())

            # Either parse or grab the previously parsed Template:
            template = (templates_by_path[template_path]
                        if template_path in templates_by_path
                        else Template(template_path))

            # Store this included template path and all of its templates
            self.templates.append(template_path)
            self.templates += template.templates

            # Parse any template references, and only add variables of type
            # 'variable' or 'array' to this Template.
            self.variables.update(dict(
                (k, v) for k, v in template.variables.items()
                if v['class'] == 'variable' or v['class'] == 'array'))
        else:
            # Add the variable to the list:
            self.variables[variable['name']] = variable


def load_templates():
    """
    Load all the .tpl templates in the TEMPLATE_DIR.

    """
    for template_file in glob.glob(str(TEMPLATE_DIR), recursive=True):
        # Parse the template and store it by its key
        template = Template(template_file)
        templates_by_path[template.key] = template

        if template.name:
            templates[template.name] = template


load_templates()
