# Version: $id$

from test  import mock
from test.framework import TestCase
from sys import path as pythonpath
from os import path, rmdir
from package.cvs import CVS

class CvsTest(TestCase):

    def setUp(self):
        self.cvsroot = ":pserver:user:pass@localhost:/var/local/cvs"
        self.module = "TestData/TestData"
        self.tag = "TEST_TAG"
        self.test_data_dir = path.join(path.dirname(__file__), "test_data")

        self.runner = mock.Mock() 
        self.runner.run.return_value = None

        self.cvs = CVS(self.cvsroot, self.module)
        self.cvs.runner = self.runner

        self.config_mock = mock.Mock()
        self.config_mock.get_cvs.return_value = "cvsmock"
        self.cvs.get_config = lambda: self.config_mock 


    def tearDown(self):
        if path.exists(self.test_data_dir):
            rmdir(self.test_data_dir)

    def testLogin(self):
        """ Login should call cvs with the correct command line."""
        self.cvs.login()

        self.assertEquals(self.runner.run.call_count, 1)
        self.runner.run.assert_called_with("cvsmock -d%s login" % self.cvsroot)


    def testExport(self):
        """ Export should call login and then call export with the correct command line."""
        self.cvs.export(self.test_data_dir, self.tag)

        self.assertEquals(len(self.runner.method_calls), 2) 
 
        expected = "cvsmock -q -z 9 export -d %s -r %s %s" % (self.tag, self.tag, self.module)
        self.runner.run.assert_called_with(expected)

        self.assertTrue(path.exists(self.test_data_dir), "Destination path should have been created.")

