# PlSql Grammar for yapps3
# Version: $id$ 

class SqlStatement(object):
    def __init__(self, id=None, type=None):
        self.type = type
        self.id = id

    def __setattr__(self, name, val):
        self.__dict__[name] = val

    def __getattr__(self, name):
        return self.__dict__[name]

    def __repr__(self):
        return str(self.__dict__)

    def __eq__(self, obj):
        return self.__dict__ == obj.__dict__

class CallStatement(SqlStatement):
    def __init__(self, object=None, id=None, arguments=None):
        SqlStatement.__init__(self, type="CALL", id=id)
        self.object = object
        self.arguments = arguments

class InsertStatement(SqlStatement):
    def __init__(self, table=None, columns=[], values=[]):
        SqlStatement.__init__(self, type="INSERT", id=table)
        self.columns = columns
        self.values = values

    def __setattr__(self, name, val):
        if name == 'table':
            self.id = val
        else:
            SqlStatement.__setattr__(self, name, val)

    def __getattr__(self, name):
        if name == 'table':
            return self.id
        else:
            return SqlStatement.__getattr__(self, name)

class Identifier(SqlStatement):
    def __init__(self, id=None, object=None):
        SqlStatement.__init__(self, id=id, type="IDENTIFIER")
        self.object = object

# Begin -- grammar generated by Yapps
import sys, re
import yappsrt

class plsqlScanner(yappsrt.Scanner):
    patterns = [
        ("'VALUES'", re.compile('VALUES')),
        ("'INTO'", re.compile('INTO')),
        ("'INSERT'", re.compile('INSERT')),
        ("'\\\\)'", re.compile('\\)')),
        ("','", re.compile(',')),
        ("'\\\\('", re.compile('\\(')),
        ('"\'"', re.compile("'")),
        ('"/"', re.compile('/')),
        ('";"', re.compile(';')),
        ('END', re.compile('[$;]')),
        ('NUM', re.compile('[0-9]+')),
        ('ID', re.compile('[a-zA-Z_][a-zA-Z0-9_-]*')),
        ('SP', re.compile('\\\\s')),
        ('SINGLE_QUOTED_STRING', re.compile("[^']*")),
        ('/\\*(.|\r?\n)+\\*/', re.compile('/\\*(.|\r?\n)+\\*/')),
        ('--.*?\r?\n', re.compile('--.*?\r?\n')),
        ('\\s+', re.compile('\\s+')),
        ('[ \t\r\n]+', re.compile('[ \t\r\n]+')),
    ]
    def __init__(self, str):
        yappsrt.Scanner.__init__(self,None,['/\\*(.|\r?\n)+\\*/', '--.*?\r?\n', '\\s+', '[ \t\r\n]+'],str)

class plsql(yappsrt.Parser):
    Context = yappsrt.Context
    def goal(self, _parent=None):
        _context = self.Context(_parent, self._scanner, self._pos, 'goal', [])
        expr = self.expr(_context)
        END = self._scan('END')

    def expr(self, _parent=None):
        _context = self.Context(_parent, self._scanner, self._pos, 'expr', [])
        insert_statement = self.insert_statement(_context)
        _token = self._peek('";"', '"/"')
        if _token == '";"':
            self._scan('";"')
        else: # == '"/"'
            self._scan('"/"')
        return insert_statement

    def identifier(self, _parent=None):
        _context = self.Context(_parent, self._scanner, self._pos, 'identifier', [])
        ID = self._scan('ID')
        return ID

    def QUOTED_STRING(self, _parent=None):
        _context = self.Context(_parent, self._scanner, self._pos, 'QUOTED_STRING', [])
        self._scan('"\'"')
        SINGLE_QUOTED_STRING = self._scan('SINGLE_QUOTED_STRING')
        self._scan('"\'"')
        return "'%s'" % SINGLE_QUOTED_STRING

    def LITERAL(self, _parent=None):
        _context = self.Context(_parent, self._scanner, self._pos, 'LITERAL', [])
        _token = self._peek('"\'"', 'NUM')
        if _token == '"\'"':
            QUOTED_STRING = self.QUOTED_STRING(_context)
            return QUOTED_STRING
        else: # == 'NUM'
            NUM = self._scan('NUM')
            return int(NUM)

    def list_value(self, _parent=None):
        _context = self.Context(_parent, self._scanner, self._pos, 'list_value', [])
        _token = self._peek('"\'"', 'NUM', 'ID')
        if _token != 'ID':
            LITERAL = self.LITERAL(_context)
            return LITERAL
        else: # == 'ID'
            function_call = self.function_call(_context)
            return function_call

    def list(self, _parent=None):
        _context = self.Context(_parent, self._scanner, self._pos, 'list', [])
        result = []
        self._scan("'\\\\('")
        while 1:
            _token = self._peek('"\'"', 'NUM', "','", 'ID')
            if _token != "','":
                list_value = self.list_value(_context)
                result.append(list_value)
            else: # == "','"
                self._scan("','")
                list_value = self.list_value(_context)
                result.append(list_value)
            if self._peek('"\'"', 'NUM', "','", 'ID', "'\\\\)'") not in ['"\'"', 'NUM', "','", 'ID']: break
        self._scan("'\\\\)'")
        return result

    def insert_base(self, _parent=None):
        _context = self.Context(_parent, self._scanner, self._pos, 'insert_base', [])
        self._scan("'INSERT'")
        self._scan("'INTO'")
        identifier = self.identifier(_context)
        return identifier

    def insert_statement(self, _parent=None):
        _context = self.Context(_parent, self._scanner, self._pos, 'insert_statement', [])
        sqlobject = InsertStatement()
        insert_base = self.insert_base(_context)
        sqlobject.table = insert_base
        _token = self._peek("'\\\\('", "'VALUES'")
        if _token == "'VALUES'":
            columns = []
        else: # == "'\\\\('"
            list = self.list(_context)
            columns = list
        sqlobject.columns = columns
        self._scan("'VALUES'")
        list = self.list(_context)
        sqlobject.values = list
        return sqlobject

    def function_call(self, _parent=None):
        _context = self.Context(_parent, self._scanner, self._pos, 'function_call', [])
        identifier = self.identifier(_context)
        result = identifier
        if self._peek("'\\\\('", '"\'"', 'NUM', "','", "'\\\\)'", 'ID') == "'\\\\('":
            list = self.list(_context)
            result = CallStatement(id=identifier, arguments=list)
        return result


def parse(rule, text):
    P = plsql(plsqlScanner(text))
    return yappsrt.wrap_error_reporter(P, rule)

# End -- grammar generated by Yapps


