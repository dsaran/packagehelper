# Version: $id$
from package.types.parsers import DefaultParser
from package.types.matchers import ParentDirectoryMatcher 

class SqlType:
    _types = [
        #SqlType("DML", 3500, DataManipulation),
        #SqlType("ACT_BD DML", 3500, DataManipulation, RegexMatcher, "ACT_BD.*DML"),
        #SqlType("PRC", 4200, Source),
        #SqlType("FNC", 4200, Source),
        #SqlType("PKB", 4500, Source),
        #SqlType("PKH", 4000, Source),
        #SqlType("TRG", 1500, Source),
        #SqlType("IDX", 2500, Source),
        #SqlType("DDL", 1000, DataDefinition),
        #SqlType("ACT_BD DDL", 1000, DataDefinition, RegexMatcher, "ACT_BD.*DDL"),
        #SqlType("SEQ", 2000, DataDefinition),
        #SqlType("TAB", 250, DataDefinition),
        #SqlType("VIEW", 500, DataDefinition),
        #SqlType("GRANTS", 5000, DataDefinitionSystem),
        #SqlType("SYN", 5500, DataDefinitionSystem),
        ]
    def __init__(self):
        self._name = None
        self._order = None
        self._category = None
        self._parser = None
        self._matcher = None

    def set_name(self, name):
        self._name = name

    def set_order(self, order):
        self._order = order

    def set_category(self, category):
        self._category = category

    def set_parser(self, parser):
        self._parser = parser

    def set_matcher(self, matcher):
        self._matcher = matcher


class SqlCategory:
    pass

class DataManipulation(SqlCategory):
    pass

class DataDefinition(SqlCategory):
    pass

class DataDefinitionSystem(SqlCategory):
    pass

class Source(SqlCategory):
    pass

