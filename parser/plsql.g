# PlSql Grammar for yapps3
# Version: $id$ 

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

    rule QUOTED_STRING:
         "'" SINGLE_QUOTED_STRING "'" {{ return "'%s'" % SINGLE_QUOTED_STRING }}

    rule LITERAL:
        QUOTED_STRING    {{ return QUOTED_STRING }}
        | NUM            {{ return int(NUM) }}

    rule list_value:
        LITERAL     {{ return LITERAL }}
        | ID        {{ return ID }}

    rule list:                      {{ result = [] }}
               '\\(' 
                       ( list_value      {{ result.append(list_value) }}
                         |',' list_value {{ result.append(list_value) }}
                       )+ 
               '\\)'                {{ return result }}

    #rule list:                      {{ result = [] }}
    #           '\\(' (
    #                   ( ID         {{ result.append(ID) }}
    #                     |',' ID     {{ result.append(ID) }}
    #                   )+ 
    #                  | ( LITERAL    {{ result.append(LITERAL) }}
    #                     |',' LITERAL {{ result.append(LITERAL) }}
    #                    )+
    #                 )
    #           '\\)'                {{ return result }}


    #rule list_item:
    #                 ID         {{ return ID }}
    #                 | ',' ID   {{ return ID }}

    #rule literal_list:                     {{ result = [] }}
    #                   ( literal_list_item {{ result.append(literal_list_item)}}
    #                   )+                  {{ return result }}

    #rule literal_list_item:
    #                (
    #                 LITERAL        {{ return LITERAL}}
    #                 | ',' LITERAL  {{ return LITERAL }}
    #                 )

    rule insert_base:
        'INSERT' 'INTO' ID  {{ return ID }}

    rule insert_statement:
        insert_base 
        ( {{ column_list = None }}
          |  list {{ column_list = list }}
        )
        'VALUES' list {{ return (insert_base, column_list, list) }}


