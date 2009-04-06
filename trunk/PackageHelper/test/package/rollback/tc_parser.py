from test.framework import TestCase
from package.rollback.parsers import SqlParser

class SqlParserTests(TestCase):

    def setUp(self):
        self.parser = SqlParser()

    def testGetLines(self):
        """_get_lines should remove multiple tabs and spaces"""
        text = """CREATE OR REPLACE PACKAGE BODY
                  \t /* many comments */ package_name"""
        lines = self.parser._get_lines(text)
        self.assertTrue(lines)
        self.assertEquals(2, len(lines), "_get_lines should have returned two lines")
        self.assertEquals("/* many comments */ package_name", lines[1])


    def testDiscardComments(self):
        """_discard_comments should remove block comments correctly."""
        text = """CREATE OR REPLACE PACKAGE BODY /* many comments */ package_name"""
        result = self.parser._discard_comments(text)
        self.assertTrue(result)
        self.assertEquals(6, len(result), "_discard_comments should return six tokens.")
        self.assertEquals("CREATE OR REPLACE PACKAGE BODY package_name", " ".join(result))

    def testDiscardCommentsMultiline(self):
        """_discard_comments should remove block comments in multiple lines correctly"""
        text = """CREATE OR REPLACE PACKAGE BODY 
        /* many
        comments 
        */
        package_name"""
        result = self.parser._discard_comments(text)
        self.assertTrue(result)
        self.assertEquals(6, len(result), "_discard_comments should return six tokens.")
        self.assertEquals("CREATE OR REPLACE PACKAGE BODY package_name", " ".join(result))

    def testDiscardSingleLineComments(self):
        """_discard_comments should remove single-line comments correctly"""
        text = """CREATE OR REPLACE PACKAGE BODY package_name -- comments after the statement"""
        result = self.parser._discard_comments(text)
        self.assertTrue(result)
        self.assertEquals(6, len(result), "_discard_comments should return six tokens.")
        self.assertEquals("CREATE OR REPLACE PACKAGE BODY package_name", " ".join(result))

    def testDiscardSingleLineCommentsMultiLine(self):
        """_discard_comments should remove single-line comments correctly on multi line declaration"""
        text = """CREATE OR REPLACE PACKAGE BODY package_name -- comments after the comment"""
        result = self.parser._discard_comments(text)
        self.assertTrue(result)
        self.assertEquals(6, len(result), "_discard_comments should return six tokens.")
        self.assertEquals("CREATE OR REPLACE PACKAGE BODY package_name", " ".join(result))

    def testParsePackageWithSchema(self):
        """Parse should parse correctly package with comments and schema"""
        inline = 'CREATE OR REPLACE PACKAGE schema_name.package_name'
        fileTO = self.parser._parse(inline)
        self.assertNotEquals(None, fileTO, "Package Header with comments and schema not correctly parsed.")
        self.assertEquals("PACKAGE_NAME", fileTO.object_name)
        self.assertEquals("PACKAGE", fileTO.object_type)
        self.assertEquals("SCHEMA_NAME", fileTO.schema)

 
    def testParsePackageWithNoSchema(self):
        """Parse should parse correctly package with no schema"""
        text = """CREATE OR REPLACE PACKAGE package_name"""
        fileTO = self.parser._parse(text)

        self.assertNotEquals(None, fileTO, "Package Header with comments and no schema not correctly parsed.")
        self.assertEquals("PACKAGE_NAME", fileTO.object_name)
        self.assertEquals("PACKAGE", fileTO.object_type)
        self.assertFalse(fileTO.schema)


    def testParsePackageBodyWithSchema(self):
        """Parse should parse correctly package body with schema"""
        inline = 'CREATE OR REPLACE PACKAGE BODY schema_name.package_name'
        fileTO = self.parser._parse(inline)
        self.assertNotEquals(None, fileTO, "Package Body with schema not correctly parsed.")
        self.assertEquals("PACKAGE_NAME", fileTO.object_name)
        self.assertEquals("PACKAGE BODY", fileTO.object_type)
        self.assertEquals("SCHEMA_NAME", fileTO.schema)

    def testParsePackageBodyNoSchema(self):
        """Parse should parse correctly package body with no schema"""
        inline = 'CREATE OR REPLACE PACKAGE BODY package_name'
        fileTO = self.parser._parse(inline)
        self.assertNotEquals(None, fileTO, "Package Body with no schema not correctly parsed.")
        self.assertEquals("PACKAGE_NAME", fileTO.object_name)
        self.assertEquals("PACKAGE BODY", fileTO.object_type)
        self.assertFalse(fileTO.schema)

    def testParseTypeWithSchema(self):
        """Parse should parse correctly type with comments and schema"""
        inline = 'CREATE OR REPLACE TYPE schema_name.type_name'
        fileTO = self.parser._parse(inline)
        self.assertNotEquals(None, fileTO, "Type Header with schema not correctly parsed.")
        self.assertEquals("TYPE_NAME", fileTO.object_name)
        self.assertEquals("TYPE", fileTO.object_type)
        self.assertEquals("SCHEMA_NAME", fileTO.schema)

 
    def testParseTypeWithNoSchema(self):
        """Parse should parse correctly type with no schema"""
        text = """CREATE OR REPLACE TYPE type_name"""
        fileTO = self.parser._parse(text)

        self.assertNotEquals(None, fileTO, "Type Header with no schema not correctly parsed.")
        self.assertEquals("TYPE_NAME", fileTO.object_name)
        self.assertEquals("TYPE", fileTO.object_type)
        self.assertFalse(fileTO.schema)


    def testParseTypeBodyWithSchema(self):
        """Parse should parse correctly type body with schema"""
        inline = 'CREATE OR REPLACE TYPE BODY schema_name.type_name'
        fileTO = self.parser._parse(inline)
        self.assertNotEquals(None, fileTO, "Type Body with schema not correctly parsed.")
        self.assertEquals("TYPE_NAME", fileTO.object_name)
        self.assertEquals("TYPE BODY", fileTO.object_type)
        self.assertEquals("SCHEMA_NAME", fileTO.schema)

    def testParsePackageBodyNoSchema(self):
        """Parse should parse correctly type body with no schema"""
        inline = 'CREATE OR REPLACE TYPE BODY package_name'
        fileTO = self.parser._parse(inline)
        self.assertNotEquals(None, fileTO, "Type Body with no schema not correctly parsed.")
        self.assertEquals("PACKAGE_NAME", fileTO.object_name)
        self.assertEquals("TYPE BODY", fileTO.object_type)
        self.assertFalse(fileTO.schema)

    def testParseParseCaseInsensitive(self):
        """Parse should parse ignoring case."""
        inline = 'create or replace type body schema_name.package_name'
        fileTO = self.parser._parse(inline)
        self.assertNotEquals(None, fileTO, "Type Body with no schema not correctly parsed.")
        self.assertEquals("PACKAGE_NAME", fileTO.object_name)
        self.assertEquals("TYPE BODY", fileTO.object_type)
        self.assertEquals("SCHEMA_NAME", fileTO.schema)

    def testParseInsertWithSpaces(self):
        """Parse should parse correctly an Insert statement with no spaces before parenthesis""" 
        insert_no_space = "INSERT INTO tabela(coluna1, coluna2, coluna3) VALUES('value1', 'value2', 'value3')"
        fileTO = self.parser._parse(insert_no_space)
        self.assertTrue(fileTO, "Insert with no spaces not parsed correctly")
        self.assertEquals("tabela", fileTO.object_name)
        expected_parameters = ['coluna1', 'coluna2', 'coluna3']
        expected_values = ["'value1'", "'value2'", "'value3'"]
        self.assertEquals(expected_parameters, fileTO.parameters, "Parameters did not match")
        self.assertEquals(expected_values, fileTO.values, "Parameters did not match")


    def testProcessInline(self):
        """Process should parse correctly declaration inline"""
        text = """CREATE OR REPLACE PACKAGE BODY /* many comments */ schema_name.package_name"""

        fileTO = self.parser.process(text)

        self.assertEquals("PACKAGE_NAME", fileTO.object_name)
        self.assertEquals("PACKAGE BODY", fileTO.object_type)
        self.assertEquals("SCHEMA_NAME", fileTO.schema)

    def testProcessInlineNoSchema(self):
        """Process should parse correctly declaration inline with no schema"""
        text = """CREATE OR REPLACE PACKAGE BODY /* many comments */ package_name"""

        fileTO = self.parser.process(text)

        self.assertEquals("PACKAGE_NAME", fileTO.object_name)
        self.assertEquals("PACKAGE BODY", fileTO.object_type)
        self.assertEquals(None, fileTO.schema)

    def testProcessPackageBodyMultiLine(self):
        """Process should parse correctly multiline package body declaration"""
        text = """CREATE OR 
        REPLACE PACKAGE 
        BODY
        /* many comments */ 
        schema_name.package_name"""

        fileTO = self.parser.process(text)

        self.assertEquals("PACKAGE_NAME", fileTO.object_name)
        self.assertEquals("PACKAGE BODY", fileTO.object_type)
        self.assertEquals("SCHEMA_NAME", fileTO.schema)

    def testProcessPackage(self):
        """Process should parse correctly multiline package declaration"""
        text = """CREATE OR 
        REPLACE PACKAGE 
        /* many comments */ 
        schema_name.package_name"""

        fileTO = self.parser.process(text)

        self.assertEquals("PACKAGE_NAME", fileTO.object_name)
        self.assertEquals("PACKAGE", fileTO.object_type)
        self.assertEquals("SCHEMA_NAME", fileTO.schema)

    def testProcessSingleLineComment(self):
        """Process should parse correctly multiline package declaration with single-line comment"""
        text = """CREATE OR 
        REPLACE PACKAGE -- many comments
        schema_name.package_name"""

        fileTO = self.parser.process(text)

        self.assertEquals("PACKAGE_NAME", fileTO.object_name)
        self.assertEquals("PACKAGE", fileTO.object_type)
        self.assertEquals("SCHEMA_NAME", fileTO.schema)

    def testDiscardComments(self):
        """Discard comments should remove comments with no separator between tokens"""
        text = """CREATE OR REPLACE test
                /****************************
                COMMENTS
                ****************************/"""



