from test.framework import TestCase
from parser.yappsrt import SyntaxError
from parser.plsql import InsertStatement, CallableStatement, Identifier, Source, RelationalOperation, SelectStatement
from parser import plsql

quoted_string = "' a quoted string'"
insert_columns = "(a, b, c,d,e ,f)"
insert_values = "(1, 'b', 3,'d')"

class PlSqlParserTests(TestCase):

    def testQuotedString(self):
        """ PlSqlParser should parse correctly a single-quoted text"""
        result = plsql.parse("QUOTED_STRING", quoted_string)
        self.assertEquals('\' a quoted string\'', result)

    def testList(self):
        """ PlSqlParser should parse correctly a list between parenthesis"""
        result = plsql.parse("list", insert_columns)
        a = Identifier('a')
        b = Identifier('b')
        c = Identifier('c')
        d = Identifier('d')
        e = Identifier('e')
        f = Identifier('f')
        expected = [a, b, c, d, e, f]
        self.assertEquals(expected, result)

    def testLiteralMatch(self):
        """ PlSqlParser should parse a Literal (numbers and strings) correctly"""
        result = plsql.parse("LITERAL", "1")
        self.assertEquals(1, result)

        result = plsql.parse("LITERAL", "'a'")
        self.assertEquals("'a'", result)

    # Disabled because there is no literal_list rule anymore.
    def _testLiteralListItem(self):
        """ PlSqlParser should correctly parse a literal in a list """
        result = plsql.parse("literal_list_item", "1")
        self.assertEquals(1, result)

        result = plsql.parse("literal_list_item", "'a'")
        self.assertEquals("'a'", result)

        result = plsql.parse("literal_list_item", ", 1")
        self.assertEquals(1, result)

        result = plsql.parse("literal_list_item", ", 'a'")
        self.assertEquals("'a'", result)

    def testMixedList(self):
        """ PlSqlParser should accept lists with both literal and identifiers"""
        mixed_list = "(1, 'a', b)"
        b = Identifier(id='b')
        expected = [1, "'a'", b]

        result = plsql.parse("list", mixed_list)

        self.assertTrue(result)
        self.assertEquals(expected, result)

    def testLiteralList(self):
        """ PlSqlParser should parse a list of literals correctly"""
        literal_list = "(1, 2, 3, 'a')"
        result = plsql.parse("list", literal_list)
        expected = [1, 2, 3, "'a'"]
        self.assertEquals(expected, result)

    def testIgnoreBlockComments(self):
        """ PlSqlParser should ignore block comments"""
        comment = "(1, 2, 3/*Many comments*/, 'a')"
        result = plsql.parse("list", comment)
        expected = [1, 2, 3, "'a'"]
        self.assertEquals(expected, result)

    def testIgnoreSingleLineComment(self):
        """ PlSqlParser should ignore single line comments"""
        comment = "-- Many comments \n 'some literal'"
        result = plsql.parse("LITERAL", comment)
        self.assertEquals("'some literal'", result)

    def testSimpleInsertStatementWithColumns(self):
        """ PlSqlParser should parse a simple pl/sql insert statement with columns""" 
        insert = "INSERT INTO table(a, b) VALUES (1, 'b');"
        columns = [Identifier(id='a'), Identifier(id='b')]
        table = Identifier(id='table')
        expected = InsertStatement(table=table, columns=columns, values=[1, "'b'"])

        result = plsql.parse("expr", insert)
        self.assertTrue(result, "Insert statement not parsed")

        self.assertEquals(expected, result)

    def testInsertStatementWithoutColumns(self):
        """ PlSqlParser should parse a simple pl/sql insert statement without columns""" 
        insert = "INSERT INTO table VALUES (1, 'b');"
        table = Identifier(id='table')
        expected = InsertStatement(table=table, values=[1, "'b'"])

        result = plsql.parse("expr", insert)
        self.assertTrue(result, "Insert statement not parsed")

        self.assertEquals(expected, result)

    def testInsertStatementWithFunctions(self):
        """ PlSqlParser should parse an insert with functions on values"""
        insert = "INSERT INTO table VALUES (variable1, UPPER(variable2), 'value');"
        table = Identifier(id='table')
        variable1 = Identifier(id='variable1')
        variable2 = Identifier(id='variable2')
        upper = 'UPPER'
        expected = InsertStatement(table=table, values=[variable1, CallableStatement(name=upper, arguments=[variable2]), "'value'"])

        result = plsql.parse("expr", insert)
        self.assertTrue(result, "Insert statement not parsed")

        self.assertEquals(expected, result)

    def testFunctionCall(self):
        """ PlSqlParser should parse a function/procedure call"""
        call = "myFunction('var1', 2)"
        func_id = 'myFunction'
        expected = CallableStatement(name=func_id, arguments=["'var1'", 2])

        result = plsql.parse("callable", call)
        self.assertTrue(result, "Function call not parsed")
        self.assertEquals(expected, result)

    def testFunctionCallWithNoArgument(self):
        """ PlSqlParser should parse a function/procedure call with no arguments"""
        call = "myFunction()"
        func_id = 'myFunction'
        expected = CallableStatement(name=func_id)

        result = plsql.parse("callable", call)
        self.assertTrue(result, "Function call not parsed")
        self.assertEquals(expected, result)

    def testFunctionCallOnObject(self):
        """ PlSqlParser should parse a function/procedure call with object"""
        call = "object.myFunction('var1', 2)"
        object = Identifier(id='object')
        name = 'myFunction'
        expected = CallableStatement(object=object, name=name, arguments=["'var1'", 2])

        result = plsql.parse("callable", call)
        self.assertTrue(result, "Function call not parsed")
        self.assertEquals(expected, result)

    def testCreateOrReplaceProcedureDeclarationAs(self):
        """ PlSqlParser should parse a Create Or Replace Procedure declaration AS"""
        declaration = "CREATE OR REPLACE PROCEDURE my_procedure (arg1 IN NUMBER) AS "
        arguments = [Identifier(id="arg1", type="NUMBER")]
        name = CallableStatement(name="my_procedure", arguments=arguments)
        expected = Source(id=name, type="PROCEDURE")

        result = plsql.parse("expr", declaration)
        self.assertTrue(result, "Declaration not parsed")
        self.assertEquals(expected, result)

    def testCreateOrReplaceProcedureDeclarationIs(self):
        """ PlSqlParser should parse a Create Or Replace Procedure declaration AS"""
        declaration = "CREATE OR REPLACE PROCEDURE my_procedure (arg1 IN NUMBER) IS"
        arguments = [Identifier(id="arg1", type="NUMBER")]
        name = CallableStatement(name="my_procedure", arguments=arguments)
        expected = Source(id=name, type="PROCEDURE")

        result = plsql.parse("expr", declaration)
        self.assertTrue(result, "Declaration not parsed")
        self.assertEquals(expected, result)

    def testCreateProcedureDeclaration(self):
        """ PlSqlParser should parse a Create Procedure declaration"""
        declaration = "CREATE PROCEDURE my_procedure (arg1 IN NUMBER) IS"
        arguments = [Identifier(id="arg1", type="NUMBER")]
        name = CallableStatement(name="my_procedure", arguments=arguments)
        expected = Source(id=name, type="PROCEDURE")

        result = plsql.parse("expr", declaration)
        self.assertTrue(result, "Declaration not parsed")
        self.assertEquals(expected, result)

    def testPackageBodyDeclaration(self):
        """ PlSqlParser should parse a Create Or Replace Package Body declaration"""
        declaration = "CREATE OR REPLACE PACKAGE BODY my_package(arg1 IN NUMBER) IS"
        arguments = [Identifier(id="arg1", type="NUMBER")]
        name = CallableStatement(name="my_package", arguments=arguments)
        expected = Source(id=name, type="PACKAGE BODY")

        result = plsql.parse("expr", declaration)
        self.assertTrue(result, "Declaration not parsed")
        self.assertEquals(expected, result)

    def testPackageDeclaration(self):
        """ PlSqlParser should parse a Create Or Replace Package declaration"""
        declaration = """CREATE OR REPLACE PACKAGE /* some comments */    schema.package IS"""
        parent = Identifier(id="schema")
        name = Identifier(id="package", parent=parent)

        expected = Source(id=name, type="PACKAGE")

        result = plsql.parse("expr", declaration)
        self.assertTrue(result, "Declaration not parsed")
        self.assertEquals(expected, result)

    def testBlockCommentProblem(self):
        """ PlSqlParser comment parsing should not be greedy"""
        text = "an_identifier /* some comments */ other_identifier /* other comments */;"        
        expected = Identifier(id="an_identifier", alias="other_identifier")

        result = plsql.parse("identifier", text)
        self.assertTrue(result, "Identifier not parsed")
        self.assertEquals(expected, result)

    def testWhereClause(self):
        """ PlSqlParser should recognize a Where clause with one condition"""
        operators = {'!=': 'NOT_EQ', '^=': 'NOT_EQ', '<>': 'NOT_EQ', '=': 'EQ', '<': 'LT', '<=': 'LE', \
        '>': 'GT', '>=': 'GE'}
        for operator in operators:
            value1 = Identifier(id='value1')
            expected = RelationalOperation(op1=value1, operator=operators[operator], op2=10)
            where = "WHERE value1 %s 10;" % operator

            result = plsql.parse('where_clause', where)
            self.assertTrue(result, "Where clause not parsed")
            self.assertEquals(1, len(result))
            self.assertEquals(expected, result[0])

    def testCompositeWhereClause(self):
        """ PlSqlParser should parse a Where clause with more than one condition"""
        where = "WHERE value1 = 10 AND value2 < 20 OR 1 <> 2;"
        value1 = Identifier(id='value1')
        value2 = Identifier(id='value2')
        condition1 = RelationalOperation(op1=value1, operator='EQ', op2=10)
        condition2 = RelationalOperation(op1=value2, operator='LT', op2=20)
        condition3 = RelationalOperation(op1=1, operator='NOT_EQ', op2=2)
        expected = [condition1, condition2, condition3]

        result = plsql.parse('where_clause', where)
        self.assertTrue(result, "Where clause not parsed")
        self.assertEquals(3, len(result))
        self.assertEquals(expected, result)

    def testSelectStatement(self):
        """ PlSqlParser should parse a simple Select statement"""
        select = "SELECT * FROM table WHERE value1 = 2;"
        value1 = Identifier(id='value1')
        where = [ RelationalOperation(op1=value1, operator='EQ', op2=2) ]
        tables = [ Identifier(id="table") ]
        expected = SelectStatement(columns="*", tables=tables, where_clause=where)

        result = plsql.parse('select_statement', select)

        self.assertTrue(result, "Select statement not parsed")
        self.assertEquals(expected, result)

    def testSelectStatementMultipleTablesAndColumns(self):
        """ PlSqlParser should parse a Select statement with multiple tables"""
        select = "SELECT t1.column, t2.* FROM table1 t1, table2 t2 WHERE value1 = 2;"
        column1 = Identifier(id='column', parent=Identifier(id="t1"))
        column2 = Identifier(id='*', parent=Identifier(id="t2"))
        table1 = Identifier(id="table1", alias='t1')
        table2 = Identifier(id="table2", alias='t2')
        value1 = Identifier(id='value1')
        where = [ RelationalOperation(op1=value1, operator='EQ', op2=2) ]
        expected = SelectStatement(columns=[column1, column2], tables=[table1, table2], where_clause=where)

        result = plsql.parse('select_statement', select)

        self.assertTrue(result, "Select statement not parsed")
        self.assertEquals(expected, result)




