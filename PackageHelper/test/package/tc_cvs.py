# Version: $id$

import os
from test  import mock
from test.framework import TestCase
from path import path as Path
from package.cvs import CVS

class CvsTest(TestCase):

    def setUp(self):
        self.cvsroot = ":pserver:user:pass@localhost:/var/local/cvs"
        self.module = "TestData/TestData"
        self.tag = "TEST_TAG"
        current_dir = Path(__file__).dirname()
        self.test_data_dir = current_dir / "test_data"

        self.runner = mock.Mock() 
        self.runner.run.return_value = None, None

        self.cvs = CVS(self.cvsroot, self.module)
        self.cvs.runner = self.runner

        self.config_mock = mock.Mock()
        self.config_mock.get_cvs.return_value = "cvsmock"
        self.cvs.get_config = lambda: self.config_mock 


    def tearDown(self):
        if self.test_data_dir.exists():
            self.test_data_dir.rmdir()

    def testLogin(self):
        """ Login should call cvs with the correct command line."""
        self.cvs.login()

        self.assertEquals(self.runner.run.call_count, 1)
        self.runner.run.assert_called_with("cvsmock -d%s login" % self.cvsroot)

    def testExport(self):
        """ Export should call login and then call export with the correct command line."""
        self.cvs.export(self.test_data_dir, self.tag)

        self.assertEquals(len(self.runner.method_calls), 2) 
 
        expected = "cvsmock -q -z 9 -d%s export -d %s -r %s %s" % (self.cvsroot, self.tag, self.tag, self.module)
        self.runner.run.assert_called_with(expected)

        self.assertTrue(self.test_data_dir.exists(), "Destination path should have been created.")

    def testExportDirectory(self):
        """ Export should create a directory when it does not exist."""
        package_dir = mock.Mock() 
        package_dir.abspath.return_value = '.'
        package_dir.exists.return_value = False
        self.cvs.export(package_dir, self.tag)

        self.assertEquals(3, len(package_dir.method_calls))
        self.assertEquals('exists', package_dir.method_calls[0][0])
        self.assertEquals('mkdir', package_dir.method_calls[1][0])
 
    def testExportCurrentDirectory(self):
        """ Export should not change current directory."""
        current_dir_before = self.given_i_am_on_an_existing_directory()

        self.when_i_checkout_files(self.test_data_dir, self.tag)

        self.should_be_on_directory(current_dir_before)


    #
    # Behaviors
    #

    def given_i_am_on_an_existing_directory(self):
        try:
            current_dir = os.getcwd()
        except OSError, e:
            self.fail("Impossible to get current directory (%s)" % e.strerror)
        self.assertTrue(os.path.exists(current_dir), 'Current directory does not exists')
        return current_dir

    def when_i_checkout_files(self, destination, tag):
        return self.cvs.export(destination, tag)
 
    def should_be_on_directory(self, directory):
        try:
            current_dir = os.getcwd()
        except OSError, e:
            self.fail("Impossible to get current directory (%s)" % e.strerror)
        self.assertEquals(directory, current_dir, "I am on a different directory")

