from test.framework import TestCase
from test.mock import Mock

from package.domain.pack import Package
from package.domain.file import InstallScript
from path import path as Path

class PackageTests(TestCase):
    def setUp(self):
        self.package = Package()

    def testPathShouldAcceptString(self):
        """Package path property should accept strings"""
        self.package.path = '/tmp/'
        self.assertEquals(Path, type(self.package.path))
        self.assertEquals(Path('/tmp'), self.package.path)

    def testPathShouldAcceptPath(self):
        """Package path property should accept Path"""
        self.package.path = Path('/tmp/')
        self.assertEquals(Path, type(self.package.path))
        self.assertEquals(Path('/tmp'), self.package.path)

    def testPathShouldNotAcceptOtherTypes(self):
        """Package path property should not accept other types"""
        ok = False
        try:
            self.package.path = 1234
        except ValueError:
            ok = True
        self.assertTrue(ok)
        self.assertEquals(None, self.package.path)

        ok = False
        try:
            self.package.path = Package()
        except ValueError:
            ok = True
        self.assertTrue(ok)
        self.assertEquals(None, self.package.path)


class InstallScriptTests(TestCase):

    def setUp(self):
        self.base_path = Mock()
        file1 = Mock()
        file2 = Mock()
        self.base_path.abspath.return_value = '/tmp/'
        file1.getInitScript.return_value = ['file 1 init']
        file2.getInitScript.return_value = ['file 2 init']
        file1.getScript.return_value = ['file 1 script']
        file2.getScript.return_value = ['file 2 script']
        file1.getFinalScript.return_value = ['file 1 end']
        file2.getFinalScript.return_value = ['file 2 end']
        self.install_script = InstallScript('filename.sql', content=[file1, file2])

        self.expected_data = ['SPOOL filename.log',
                         'file 1 init', 'file 2 init',
                         'file 1 script', 'file 2 script',
                         'file 1 end', 'file 2 end',
                         'SPOOL OFF']

        self.test_dir = Path('TEST_OUTPUT')
        self.test_dir.mkdir()

    def tearDown(self):
        self.test_dir.rmtree()
 
    def testScriptCreation(self):
        """ Given a Script with files data should be generated correctly"""

        self.install_script._write_script = Mock()
 
        self.install_script.create(self.base_path)

        write_script_method = self.install_script._write_script

        write_script_method.assert_called_with(self.base_path, self.expected_data)
 
    def testWriteScript(self):
        """ When a script is written it should be created on filesystem correctly"""
        self.install_script._write_script(self.test_dir, self.expected_data)

        expected_script = Path('TEST_OUTPUT')/Path(self.install_script.name)
        self.assertTrue(expected_script.exists(), "File not created")
        written_lines = expected_script.lines(retain=False)

        self.assertEquals(self.expected_data, written_lines, "Written data should match expected.")
        
    def testExistingScriptMovedBeforeCreation(self):
        """ Given a script with same name exists it should be moved to scriptname.bak"""
        self.fail('Test not implemented')

    def testIfScriptNameDoesNotEndWithSQL(self):
        """ Given script name doesn't end with SQL spool should be to scriptname.log"""
        self.fail('Test not implemented')

