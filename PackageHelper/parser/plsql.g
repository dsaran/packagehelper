# PlSql Grammar for yapps3
# Version: $Id: plsql.g,v 1.8 2009-03-09 01:12:59 daniel Exp $ 

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
        if obj != None and hasattr(obj, '__dict__'):
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
    def __init__(self, id=None, type=None, members=[]):
        SqlStatement.__init__(self, id=id, stmt_type="SOURCE")
        self.type = type
        self.members = members


class RelationalOperation(SqlStatement):
    def __init__(self, op1=None, operator=None, op2=None):
        SqlStatement.__init__(self, id=operator, stmt_type="RELATIONAL")
        self.op1 = op1
        self.op2 = op2

    def __setattr__(self, name, val):
        if name == 'operator':
            self.id = val
        else:
            SqlStatement.__setattr__(self, name, val)

    def __getattr__(self, name):
        if name == 'operator':
            return self.id
        else:
            return SqlStatement.__getattr__(self, name)

class SelectStatement(SqlStatement):
    def __init__(self, columns=None, tables=None, where_clause=None):
        SqlStatement.__init__(self, stmt_type="INSERT")
        self.columns = columns
        self.tables = tables
        self.where_clause = where_clause

%%



parser plsql:

    token END: "[$;]"
    token NUM: "[0-9]+"
    token ID: r'[a-zA-Z_][a-zA-Z0-9_-]*'
    token SP: r'\\s'
    token SINGLE_QUOTED_STRING: "[^']*"
    token DOT: '\\.'
    token STAR: '\\*'

    # White spaces
    ignore: "\\s+"
    # Empty lines
    ignore: "^(\\s+)*$"
    # Set environment variables
    ignore: "^(\\s+)*SET.*?\r?\n"
    # Block comments
    ignore: "/\\*(.|\r?\n)+?\\*/"
    # Single-line comment
    ignore: "--.*?\r?\n"
    ignore: "[ \t\r\n]+"
    
    rule goal: 
        expr END

    rule expr: (
         insert_statement (";" | "/")    {{ return insert_statement }}
         | select_statement (";" | "/")  {{ return select_statement }}
         | source_declaration            {{ return source_declaration }} 
        )

    ########################
    # Identifiers & Values #
    ########################

    rule QUOTED_STRING:
         "'" SINGLE_QUOTED_STRING "'" {{ return "'%s'" % SINGLE_QUOTED_STRING }}

    rule LITERAL:
        QUOTED_STRING    {{ return QUOTED_STRING }}
        | NUM            {{ return int(NUM) }}

    rule identifier: (
            ID       {{ result = Identifier(id=ID) }}
            (  # if identifier matches an argument declaration
                ( ( 'IN' ('OUT')?
                   | 'OUT' )
                  ID     {{ result.type = ID }} 
                )?
             |  (  ID     {{ result.alias = ID }} 
                )?
            )
            (  # if identifier matches id.id or id.*
             | DOT
               ( ID {{ result = Identifier(id=ID, parent=result) }}
                 | STAR {{ result = Identifier(id='*', parent=result) }}
               )
            )
        )           {{ return result }}

    rule callable: (
            identifier   {{ result = identifier }}
            ( list       {{ result = CallableStatement(object=identifier.parent, name=identifier.id, arguments=list) }} )?
        )                {{ return result }}

    #########
    # Lists #
    #########

    rule list_value:
        LITERAL         {{ return LITERAL }}
        | callable {{ return callable }}

    # List between parenthesis
    rule list:                           {{ result = [] }}
               '\\(' 
                       ( list_value      {{ result.append(list_value) }}
                         |',' list_value {{ result.append(list_value) }}
                       )* 
               '\\)'                     {{ return result }}

    # Simple comma separated list outside parenthesis
    rule simplified_list: (      {{ result = [] }}
               ( list_value      {{ result.append(list_value) }}
                 |',' list_value {{ result.append(list_value) }}
               )* 
           )                     {{ return result }}
 
    #####################
    # PL/SQL Operators #
    #####################

    rule comparison: (
                list_value relational_op {{ result = RelationalOperation(op1=list_value, operator=relational_op) }}
                list_value               {{ result.op2 = list_value }}
            )                            {{ return result }}
 
    rule relational_op: (
            ('\\^' | '!') '=' {{ result = 'NOT_EQ' }}
            | '='             {{ result = 'EQ' }}
            | '<'             {{ result = 'LT' }}
                  (
                    | '='     {{ result = 'LE' }}
                    | '>'     {{ result = 'NOT_EQ' }}
                   )?
            | '>' (           {{ result = 'GT' }}
                    | '='     {{ result = 'GE' }}
                   )
        )                     {{ return result }}

    #####################
    # PL/SQL Statements #
    #####################

    rule insert_base:
        'INSERT' 'INTO' identifier  {{ return identifier }}

    rule insert_statement: ( {{ sqlobject = InsertStatement() }}
        insert_base          {{ sqlobject.table = insert_base }} 
        ( {{ columns = [] }}
         | list {{ columns = list }}
         ) {{ sqlobject.columns = columns }}
        'VALUES' list        {{ sqlobject.values = list }}
        )                    {{ return sqlobject }} 

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
            callable    {{ result.id = callable }} 
            ( END
              | "IS"
              | "AS"
            )           {{ result.members = [] }}
            'BEGIN'?
            (
                object_type {{ member= Source(type=object_type) }}
                callable    {{ member.id = callable }} 
                (END
                 | ( 
                     "IS" block {{ result.members.append(member) }}
                   )
                )
            )*
            'END' ID END? '/'  {{ return result }}
        )#      {{ return result }}

    rule block: (
        'BEGIN' block 'END' ID? ';'?
        | ('IF' comparison 'THEN' executable_code
          ('ELSE' executable_code)?
            'END' 'IF')
        | exception_handling
        | (identifier ':=')? callable ';'
    )

    rule executable_code: (
        callable ';'
        | identifier 
            (':=' 
             ( callable
             | LITERAL)
            )? ';'
    )

    rule exception_handling: (
        'EXCEPTION' ID 'THEN'
        | ('WHEN' ID block)+
    )

    rule select_statement: (
            'SELECT'            {{ select = SelectStatement() }}
                ( 'DISTINCT'
                  | 'UNIQUE'
                  | 'ALL'
                )?
                query_columns   {{ select.columns = query_columns }}
                'FROM'
                simplified_list {{ select.tables = simplified_list }}
                where_clause    {{ select.where_clause = where_clause }}
            )                   {{ return select }}

    rule query_columns:
        ( STAR              {{ result = STAR }} 
         | simplified_list  {{ result = simplified_list }}
        )                   {{ return result }}

    rule where_clause: (
            'WHERE'                      {{ conditions = [] }}
            (
                comparison                   {{ conditions.append(comparison) }}
                | (('AND' | 'OR') comparison  {{ conditions.append(comparison) }})
            )+
        )                                {{ return conditions }}

    
%%

