import re
import logging

ANY = ".*"
SEPARATOR = "([\\s\\n])+"
OPTIONAL_SEPARATOR = "([\\s\\n])*"
COMMENT_PATTERN = "(/\\*.*\\*/\\s*)?"
DECLARATION_PATTERN =  "CREATE\\s+(OR\\s+REPLACE)?"
TYPE_PATTERN = "(?P<type>" + "(FUNCTION|PACKAGE BODY|PACKAGE|PROCEDURE|TYPE BODY|TYPE)" + ")"
SCHEMA_PATTERN = "((?P<schema>\\w+)\\.)"
OBJECT_NAME_PATTERN = "(?P<name>" + "\\w+" + ")"
INSERT_STATEMENT = "INSERT INTO"
COLUMNS_PATTERN = "\\((?P<columns>.*)\\)"
VALUES_PATTERN = "VALUES" + OPTIONAL_SEPARATOR + "\\((?P<values>.*)\\)"

SOURCE_DECLARATION = DECLARATION_PATTERN + SEPARATOR + TYPE_PATTERN + SEPARATOR + SCHEMA_PATTERN + "?" + OBJECT_NAME_PATTERN + ANY
INSERT_COMMAND = INSERT_STATEMENT + SEPARATOR + OBJECT_NAME_PATTERN + OPTIONAL_SEPARATOR + COLUMNS_PATTERN + SEPARATOR + VALUES_PATTERN

class FileTO:
    def __init__(self):
        self.object_name = None
        self.object_type = None
        self.schema = None
        self.parameters = None
        self.values = None

log = logging.getLogger("SqlParser")

class SqlParser:
    def __init__(self):
        self.pattern = re.compile(SOURCE_DECLARATION, re.DOTALL)
        #parsers = {'TYPE': self._parse_declaration,
        #           'PKB': self._parse_declaration,
        #           'PKH':
        #            'ACT_BD'
        #            'ADM'
        #            'CMT'
        #            'CONSTR'
        #            'CVS'
        #            'DML'
        #            'FUNC'
        #            'GRANTS'
        #            'IDX'
        #            'JOB'
        #            'LIB'
        #            'MISC'
        #            'PKB'
        #            'PKH'
        #            'PRC'
        #            'QUE'
        #            'SEQ'
        #            'SYN'
        #            'TAB'
        #            'TRG'
        #            'TST'
        #            'TYPE'
        #            'VIEW'
        #}

    def process(self, text, type):
        """Process the given text and return the parsed file data
            @param text the source to process
            @param type the type of file being parsed
            @return FileTO with the file data"""
        lines = self._get_lines(text)
        converted_lines = []
        count = 0
        for line in lines:
            line = self._discard_comments(line)
            converted_lines += line
            count += len(line)
            if count > 6:
                break

        expression = " ".join(converted_lines)
        return self._parse(expression)

    def _parse(self, source):
        """Uses regular expression to parse the given source"""
        match = self.pattern.search(source.upper())
        to = None
        if (match):
            to = FileTO()
            data = match.groupdict()
            to.object_name = data.has_key("name") and data["name"]
            to.object_type = data.has_key("type") and data["type"]
            to.schema = data.has_key("schema") and data["schema"]
            to.parameters = data.has_key("columns") and data["columns"]
            to.values = data.has_key("values") and data["values"]

        return to

    def _parse_insert(self, source):
        pass
    def _parse_declaration(self, source):
        pass

    def _get_lines(self, text):
        """Split text lines discarding special characters
            @param text text data to convert
            @return text splitted into lines"""
        lines = [re.sub("[\\s\\t]+", " ", line).strip() for line in text.splitlines()]
        return lines

    def _discard_comments(self, line):
        """Parses a line to remove comments
           @param line the line process
           @return a list of tokens"""
        tokens = [token.strip() for token in re.split("[\\s]", line)]
        ignore = False
        valid_tokens = []
        for token in tokens:
            if token == "/*":
                ignore = True
            elif token == "*/" and ignore:
                ignore = False
                continue
            elif token == "--":
                break

            if not ignore and token:
                valid_tokens.append(token)
        return valid_tokens


        
#types = {
#    'CREATE': Next(),
#    'OR': Next(),
#    'REPLACE': Next(),
#    # Types
#    'PACKAGE': Next(PackageHeader()),
#    'BODY': PackageBody(),
#    'PROCEDURE': Procedure(),
#    'FUNCTION': Function(),
#    'TYPE': Type(),
#}
 
#class Next:
#    def __init__(self, default=None):
#        self._default = default
#
#    def get_default(self):
#        return self._default
#
#class Replace(Next):
#    pass
#
#class Final:
#    pass
#
#class Package(Next):
#    pass
#
#class PackageHeader(Final):
#    pass
#
#class PackageBody(Final):
#    pass
#
#class Function(Final):
#    pass
#
#class Procedure(Final):
#    pass
#
#class Type(Final):
#    pass

