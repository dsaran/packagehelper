# Version: $id$

import re
from package.domain.file import File
from package.domain.database import Database

SEP = "[/\\\\]"
ANYTHING = ".*"
EOL = "$"
DATABASE="(?P<database>\\w+)"
USER="(?P<user>\\w+)"
TYPE="(?P<type>\\w+)"
FILENAME="(?P<filename>.*)"
class Parser:
    def parser(self, path):
        return None

class RegexParser(Parser):
    def __init__(self, regex):
        self.regex = regex

    def parse(self, path):
        pattern = re.compile(self.regex)
        match = pattern.match(path)
        map = match.groupdict()

        file = File()
        database = Database(map['database'].upper(), map['user'].upper())
        file.set_type(map['type'].upper())
        file.set_database(database)
        file.set_name(map['filename'])
        return file


class DefaultParser(Parser):
    """Parses the file path using the following rule:
    ANYTHING/<database>/<user>/<type>/<filename>
    and
    ANYTHING\<database>\<user>\<type>\<filename>"""

    def parse(self, path):
        regex = ANYTHING + SEP + "(?P<database>\\w+)" + SEP + "(?P<user>\\w+)" + SEP + "(?P<type>\\w+)" + SEP + "(?P<filename>.*)" + EOL
        pattern = re.compile(regex)
        match = pattern.match(path)
        map = match.groupdict()

        file = File()
        database = Database(map['database'].upper(), map['user'].upper())
        file.set_type(map['type'].upper())
        file.set_database(database)
        file.set_name(map['filename'])
        return file

class CustomParser(Parser):
    """CustomParser to be used to parse paths matching to a
    custom user defined expression. It offers some language sugars
    to help the user to write regular expressions more easily.
    Defined variables:
        #SEP: path separator ('/' or '\')
        #ANYTHING: match to anything
        #EOL: represents the end of path.
        #DATABASE: will be used to get the database from path.
        #USER: will be used to extract the database username from path.
        #TYPE: will be used to extract the type from path.
        #FILENAME: will be used to extract the filename."""

    def __init__(self, userRegex):
        self.userRegex = userRegex
        regex = userRegex.replace("#SEP", SEP)
        regex = regex.replace("#ANYTHING", ANYTHING)
        regex = regex.replace("#EOL", EOL)
        regex = regex.replace("#DATABASE", DATABASE)
        regex = regex.replace("#USER", USER)
        regex = regex.replace("#TYPE", TYPE)
        regex = regex.replace("#FILENAME", FILENAME)
        self.regex = regex

    def parse(self, path):
        pattern = re.compile(self.regex)
        match = pattern.match(path)
        map = match.groupdict()

        file = File()
        database = Database(map['database'], map['user'])
        file.set_type(map['type'])
        file.set_database(database)
        file.set_name(map['filename'])
        return file

