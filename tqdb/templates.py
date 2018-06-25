import glob
import re

from pathlib import Path

DATA_DIR = Path('data')
DATABASE_DIR = DATA_DIR / 'database'
TEMPLATE_DIR = DATABASE_DIR / 'templates/**/*.tpl'
TEMPLATE_PREFIX = '%TEMPLATE_DIR%'
VARIABLE_REGEX = re.compile(r'Variable\n\s+{\n(?P<properties>[^}]*)\n\s+}')

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
    def __init__(self, content):
        # Create a dictionary with all properties from this variable
        self.properties = dict(
            # Remove all quotes, split the line from a key = value format
            [i.replace('"', '').strip() for i in line.split('=', 1)]
            # For all the lines (split them by newline character)
            for line in content.split('\n'))

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
            return [self._parse(v) for v in value.split(';')
                    if self._parse(v)]

        # Return the singular parsed value:
        return self._parse(value)

    def _parse(self, value):
        """
        Internal parse function used in list comprehension.

        """
        if self['type'] == 'real':
            return float(value) if float(value) > 0 else None
        elif self['type'] == 'int':
            return int(value) if int(value) > 0 else None
        elif self['type'] == 'bool':
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

        # Find all the Variables
        matches = VARIABLE_REGEX.findall(content)
        for match in matches:
            variable = Variable(match)

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

        # Set the name of this template according to its Class:
        self.name = (self.variables['Class']['defaultValue'].lower()
                     if 'Class' in self.variables else None)


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
