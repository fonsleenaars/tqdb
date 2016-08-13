class TXTReader:
    '''Class that parses RAW txt files'''

    def __init__(self, txt):
        try:
            # Open the file with UTF16 encoding
            self.file = open(txt, encoding='utf16', errors='ignore')

            # DBR file into a list of lines
            lines = [str(line.rstrip('\n')) for line in self.file]

            # Parse line into a dictionary of key, value properties:
            self.properties = dict(properties.split('=')
                                   for properties in lines
                                   if(properties != '' and
                                      properties[0] != '/'))
        except OSError:
            self.file = None
