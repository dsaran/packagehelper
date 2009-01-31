from test.framework import TestCase
from package.rollback.parsers import SqlParser

class SqlParserTests(TestCase):

    def setUp(self):
        self.parser = SqlParser()

    def testPackageWithCommentInline(self):
        """SqlParser should parse correctly packages with declaration inline"""
        inline = 'CREATE OR REPLACE PACKAGE /* many comments */ nome_do_schema.nome_do_package'
        fileTO = self.parser.parse(inline)
        #self.assertEquals("many comments", fileTO.version.strip())
        self.assertEquals("nome_do_package", fileTO.object_name)
        self.assertEquals("PACKAGE", fileTO.object_type)
        self.assertEquals("nome_do_schema", fileTO.schema)

 
    def testPackageWithMultiLineDeclaration(self):
        """SqlParser should parse correctly packages with multiline declaration"""
        multiline = """CREATE OR REPLACE PACKAGE
                        /* many comments
                        including line breaks */ 
                        nome_do_schema.nome_do_package"""
        fileTO = self.parser.parse(multiline)
        self.assertNotEquals(None, fileTO, "Multiline Header not correctly parsed.")
        #self.assertTrue(len(fileTO.version.strip()) > 0, "Comments not parsed correctly.")
        self.assertEquals("nome_do_package", fileTO.object_name)
        self.assertEquals("PACKAGE", fileTO.object_type)
        self.assertEquals("nome_do_schema", fileTO.schema)


    def testPackageWithNoSchemaName(self):
        """SqlParser should parse correctly packages with no schema name"""
        noschema = 'CREATE OR REPLACE PACKAGE /* inline comment */ nome_do_package'
        fileTO = self.parser.parse(noschema)
        self.assertNotEquals(None, fileTO, "Package with no schema not correctly parsed.")
        #self.assertTrue(len(fileTO.version.strip()) > 0, "Comments not parsed correctly.")
        self.assertEquals("nome_do_package", fileTO.object_name)
        self.assertEquals("PACKAGE", fileTO.object_type)
        self.assertEquals(None, fileTO.schema, "Schema should be None.")


    def testPackageBodyWithMultiLineDeclaration(self):
        """SqlParser should parse correctly package body with multiline declaration"""
        multiline = """CREATE OR REPLACE PACKAGE
                        BODY
                        /* many comments
                        including line breaks */ 
                        nome_do_schema.nome_do_package"""
        fileTO = self.parser.parse(multiline)
        self.assertNotEquals(None, fileTO, "Multiline package body not correctly parsed.")
        #self.assertTrue(len(fileTO.version.strip()) > 0, "Comments not parsed correctly.")
        self.assertEquals("nome_do_package", fileTO.object_name)
        self.assertNotEquals(None, fileTO.object_type)
        self.assertEquals("nome_do_schema", fileTO.schema)


    def testPackageBodyWithMultiLineDeclarationAndCommentBeforeType(self):
        """SqlParser should parse correctly package body with multiline declaration and comment before object type"""
        multiline = """CREATE OR REPLACE
                        /* many comments
                        including line breaks */ 
                        PACKAGE BODY
                        nome_do_schema.nome_do_package"""
        fileTO = self.parser.parse(multiline)
        self.assertNotEquals(None, fileTO, "Comment before object type not correctly parsed.")
        #self.assertTrue(len(fileTO.version.strip()) > 0, "Comments not parsed correctly.")
        self.assertEquals("nome_do_package", fileTO.object_name)
        self.assertNotEquals(None, fileTO.object_type)
        self.assertEquals("nome_do_schema", fileTO.schema)


    def testPackageBodyWithMultiLineDeclarationAndNoComment(self):
        """SqlParser should parse correctly package body with no comment"""
        multiline = """CREATE OR REPLACE PACKAGE BODY
                        nome_do_schema.nome_do_package"""
        fileTO = self.parser.parse(multiline)
        self.assertNotEquals(None, fileTO, "Declaration with no comment not correctly parsed.")
        #self.assertTrue(len(fileTO.version.strip()) > 0, "Comments not parsed correctly.")
        self.assertEquals("nome_do_package", fileTO.object_name)
        self.assertEquals("PACKAGE BODY", fileTO.object_type)
        self.assertEquals("nome_do_schema", fileTO.schema)

