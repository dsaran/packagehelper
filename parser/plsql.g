# PlSql Grammar for yapps3
# Version: $id$ 

class SqlStatement(object):
    def __init__(self, id=None, stmt_type=None):
        self.stmt_type = stmt_type
        self.id = id

    def __setattr__(self, name, val):
        self.__dict__[name] = val

    def __getattr__(self, name):
        return self.__dict__[name]

    def __repr__(self):
        return str(self.__dict__)

    def __eq__(self, obj):
        #print 'self.__dict__', self.__dict__
        if obj != None:
            #print 'obj.__dict__', obj.__dict__
            return self.__dict__ == obj.__dict__
        return False

class CallableStatement(SqlStatement):
    """ Represents the call or declaration of a function or procedure.
    A callable has three properties:
    - object: the object receiving the 'message', it is an Identifier
    - name: the name of the method called/declared on the object, it is a string
    - arguments: arguments sent to name, it is a list even if there is no argument
    ex: call the_object.method(arg1, arg2)
    In this example we have:
        object: the_object
        name: method
        arguments: [arg1, arg2]
    """
    def __init__(self, object=None, name=None, arguments=[]):
        """ Constructor
            @param object the object receiving the call.
            @param arguments arguments passed to function/procedure."""
        SqlStatement.__init__(self, stmt_type="CALL", id=name)
        self.object = object
        self.arguments = arguments

    def __getattr__(self, name):
        if name == 'name':
            return self.id
        return SqlStatement.__getattr__(self, name)

    def __setattr__(self, name, val):
        if name == 'name':
            self.id = val
        else:
            SqlStatement.__setattr__(self, name, val)


class InsertStatement(SqlStatement):
    def __init__(self, table=None, columns=[], values=[]):
        SqlStatement.__init__(self, stmt_type="INSERT", id=table)
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
    def __init__(self, id=None, alias=None, parent=None, type=None):
        SqlStatement.__init__(self, id=id, stmt_type="IDENTIFIER")
        self.parent = parent
        self.alias = alias
        self.type = type 

class Source(SqlStatement):
    def __init__(self, id=None, type=None):
        SqlStatement.__init__(self, id=id, stmt_type="SOURCE")
        self.type = type

%%
parser plsql:

    token END: "[$;]"
    token NUM: "[0-9]+"
    token ID: r'[a-zA-Z_][a-zA-Z0-9_-]*'
    token SP: r'\\s'
    token SINGLE_QUOTED_STRING: "[^']*"
    token DOT: '\\.'

    # White spaces
    ignore: "\\s+"
    # Empty lines
    ignore: "^(\\s+)*$"
    ignore: "[ \t\r\n]+"
    # Block comments
    ignore: "/\\*(.|\r?\n)+?\\*/"
    # Single-line comment
    ignore: "--.*?\r?\n"
    
    rule goal: 
        expr END

    rule expr: (
         insert_statement (";" | "/")  {{ return insert_statement }}
         | source_declaration {{ return source_declaration }} 
        )

    rule identifier: (
            ID       {{ result = Identifier(id=ID) }}
            (
                ( ( 'IN' ('OUT')?
                   | 'OUT' )
                  ID     {{ result.type = ID }} 
                )?
             |  (  ID     {{ result.alias = ID }} 
                )?
            )
            (
             | DOT ID {{ result = Identifier(id=ID, parent=result) }}
            )
        )           {{ return result }}

    rule QUOTED_STRING:
         "'" SINGLE_QUOTED_STRING "'" {{ return "'%s'" % SINGLE_QUOTED_STRING }}

    rule LITERAL:
        QUOTED_STRING    {{ return QUOTED_STRING }}
        | NUM            {{ return int(NUM) }}

    rule list_value:
        LITERAL         {{ return LITERAL }}
        | callable {{ return callable }}

    rule list:                           {{ result = [] }}
               '\\(' 
                       ( list_value      {{ result.append(list_value) }}
                         |',' list_value {{ result.append(list_value) }}
                       )* 
               '\\)'                     {{ return result }}


    rule insert_base:
        'INSERT' 'INTO' identifier  {{ return identifier }}

    rule insert_statement: ( {{ sqlobject = InsertStatement() }}
        insert_base          {{ sqlobject.table = insert_base }} 
        ( {{ columns = [] }}
         | list {{ columns = list }}
         ) {{ sqlobject.columns = columns }}
        'VALUES' list        {{ sqlobject.values = list }}
        )                    {{ return sqlobject }} 

    rule callable: (
            identifier   {{ result = identifier }}
            ( list       {{ result = CallableStatement(object=identifier.parent, name=identifier.id, arguments=list) }} )?
        )                {{ return result }}

    rule object_type: (
        'FUNCTION' {{ result = 'FUNCTION' }}
        | 'PROCEDURE' {{ result = 'PROCEDURE' }}
        | 'PACKAGE' {{ result = 'PACKAGE' }}
          ('BODY' {{ result = 'PACKAGE BODY' }} )?
        ) {{ return result }}

    rule source_declaration: (
            'CREATE'
            ('OR' 'REPLACE')?
            object_type {{ result = Source(type=object_type) }}
            callable {{ result.id = callable }} 
            ( END
            | "IS"
            | "AS"
            )
        )           {{ return result }}
%%
