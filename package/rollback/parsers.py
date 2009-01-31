import re

ANY = ".*"
COMMENT_PATTERN = "/\\*.*\\*/"
DECLARATION_PATTERN =  "CREATE\\s+(OR\\s+REPLACE)?"
TYPE_PATTERN = "(?P<type>" + "(FUNCTION|PACKAGE|PACKAGE\\s+.*BODY|PROCEDURE|TYPE)" + ")"
SCHEMA_PATTERN = "((?P<schema>\\w+)\\.)"
OBJECT_NAME_PATTERN = "(?P<name>" + "\\w+" + ")"

class FileTO:
    def __init__(self):
        self.version = None
        self.object_name = None
        self.object_type = None
        self.schema = None

class SqlParser:
    def __init__(self):
        complete = DECLARATION_PATTERN + "\\s+(" + COMMENT_PATTERN + "\\s*)?" + TYPE_PATTERN + "\\s+(" + COMMENT_PATTERN + "\\s*)?" + SCHEMA_PATTERN + "?" + OBJECT_NAME_PATTERN + "\\s*" + ANY
        self.pattern = re.compile(complete, re.DOTALL)

    def parse(self, source):
        match = self.pattern.search(source)
        to = None
        if (match):
            to = FileTO()
            data = match.groupdict()
            to.object_name = data["name"]
            to.object_type = data["type"]
            to.schema = data["schema"]

        return to


