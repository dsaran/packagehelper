from test.framework import TestCase
from parser.yappsrt import SyntaxError
from parser.plsql import InsertStatement, CallStatement 
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
        expected = ['a', 'b', 'c', 'd', 'e', 'f']
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
        result = plsql.parse("list", mixed_list)
        self.assertTrue(result)
        self.assertEquals([1, "'a'", 'b'], result)

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
        expected = InsertStatement(table='table', columns=['a', 'b'], values=[1, "'b'"])

        result = plsql.parse("expr", insert)
        self.assertTrue(result, "Insert statement not parsed")

        self.assertEquals(expected, result)

    def testInsertStatementWithoutColumns(self):
        """ PlSqlParser should parse a simple pl/sql insert statement without columns""" 
        insert = "INSERT INTO table VALUES (1, 'b');"
        expected = InsertStatement(table='table', values=[1, "'b'"])

        result = plsql.parse("expr", insert)
        self.assertTrue(result, "Insert statement not parsed")

        self.assertEquals(expected, result)

    def testInsertStatementWithFunctions(self):
        """ PlSqlParser should parse an insert with functions on values"""
        insert = "INSERT INTO table VALUES (variable1, UPPER(variable2), 'value');"
        expected = InsertStatement(table='table', values=["variable1", CallStatement(id="UPPER", arguments=["variable2"]), "'value'"])

        result = plsql.parse("expr", insert)
        self.assertTrue(result, "Insert statement not parsed")

        self.assertEquals(expected, result)

    def testFunctionCall(self):
        """ PlSqlParser should parse a function/procedure call"""
        call = "myFunction('var1', 2)"
        expected = CallStatement(id="myFunction", arguments=["'var1'", 2])

        result = plsql.parse("function_call", call)
        self.assertTrue(result, "Insert statement not parsed")
        self.assertEquals(expected, result)

    def testFunctionCallOnObject(self):
        """ PlSqlParser should parse a function/procedure call with object"""
        call = "object.myFunction('var1', 2)"
        expected = CallStatement(object='object', id="myFunction", arguments=["'var1'", 2])

        result = plsql.parse("function_call", call)
        self.assertTrue(result, "Insert statement not parsed")
        self.assertEquals(expected, result)

