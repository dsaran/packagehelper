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
        #print 'self.__dict__', self.__dict__
        #print 'obj.__dict__', obj.__dict__
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
%%
parser plsql:

    token END: "[$;]"
    token NUM: "[0-9]+"
    token ID: r'[a-zA-Z_][a-zA-Z0-9_-]*'
    token SP: r'\\s'
    token SINGLE_QUOTED_STRING: "[^']*"

    # Block comments
    ignore: "/\\*(.|\r?\n)+\\*/"
    # Single-line comment
    ignore: "--.*?\r?\n"
    ignore: "\\s+"
    ignore: "[ \t\r\n]+"
    
    rule goal: 
        expr END

    rule expr: (
         insert_statement (";" | "/")  {{ return insert_statement }}
        )

    rule identifier: (
            ID      {{ result = Identifier(id=ID) }}
        )           {{ return result }}

    rule QUOTED_STRING:
         "'" SINGLE_QUOTED_STRING "'" {{ return "'%s'" % SINGLE_QUOTED_STRING }}

    rule LITERAL:
        QUOTED_STRING    {{ return QUOTED_STRING }}
        | NUM            {{ return int(NUM) }}

    rule list_value:
        LITERAL         {{ return LITERAL }}
        | function_call {{ return function_call }}

    rule list:                           {{ result = [] }}
               '\\(' 
                       ( list_value      {{ result.append(list_value) }}
                         |',' list_value {{ result.append(list_value) }}
                       )+ 
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

    rule function_call: (
        identifier              {{ result = identifier }}
        #('.' identifier {{ result = )?       {{ 
        (list           {{ result = CallStatement(id=identifier, arguments=list) }} )?
            )           {{ return result }}

    #rule list:                      {{ result = [] }}
    #           '\\(' (
    #                   ( identifier         {{ result.append(identifier) }}
    #                     |',' identifier     {{ result.append(identifier) }}
    #                   )+ 
    #                  | ( LITERAL    {{ result.append(LITERAL) }}
    #                     |',' LITERAL {{ result.append(LITERAL) }}
    #                    )+
    #                 )
    #           '\\)'                {{ return result }}


    #rule list_item:
    #                 identifier         {{ return identifier }}
    #                 | ',' identifier   {{ return identifier }}

    #rule literal_list:                     {{ result = [] }}
    #                   ( literal_list_item {{ result.append(literal_list_item)}}
    #                   )+                  {{ return result }}

    #rule literal_list_item:
    #                (
    #                 LITERAL        {{ return LITERAL}}
    #                 | ',' LITERAL  {{ return LITERAL }}
    #                 )

%%
