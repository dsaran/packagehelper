# Version: $id$

from test.framework import TestCase
from package.types.parsers import DefaultParser
from package.domain.file import File
from package.domain.database import Database

class ParserTests(TestCase):

    def setUp(self):
        self.filename = "filename.sql"
        self.database = "database_name"
        self.user = "user_name"
        self.type = "type_definition"

        self.expectedFile = File()
        self.expectedFile.set_name(self.filename)
        self.expectedFile.set_type(self.type.upper())
        expectedDatabase = Database(self.database.upper(), self.user.upper())
        self.expectedFile.set_database(expectedDatabase)
        

    def testDefaultParser_DOS(self):
        """DefaultParser should correctly parse dos-like paths.""" 
        path = "C:\\DOCUMENTS AND SETTINGS\\PROJECT\\%s\\%s\\%s\\%s" % \
                (self.database.upper(), self.user.upper(), \
                 self.type.upper(), self.filename)

        parser = DefaultParser()
        file = parser.parse(path)

        self.assertEquals(self.expectedFile, file, "File are not equal.")

    def testDefaultParser_DOS_caseinsensitive(self):
        """DefaultParser should correctly parse dos-like paths ignoring case."""
        path = "C:\\DOCUMENTS AND SETTINGS\\PROJECT\\%s\\%s\\%s\\%s" % \
                (self.database, self.user, self.type, self.filename)

        parser = DefaultParser()
        file = parser.parse(path)

        self.assertEquals(self.expectedFile, file, "File are not equal.")


    def testDefaultParser_UNIX(self):
        """DefaultParser should parse correctly unix-like paths"""
        path = "/HOME/USER/PROJECT/%s/%s/%s/%s" % \
                (self.database.upper(), self.user.upper(), \
                 self.type.upper(), self.filename)

        parser = DefaultParser()
        file = parser.parse(path)

        self.assertEquals(self.expectedFile, file, "File are not equal.")

