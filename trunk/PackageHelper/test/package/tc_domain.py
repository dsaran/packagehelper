from test.framework import TestCase
from test.mock import Mock

from package.domain.pack import Package
from package.domain.file import InstallScript
from package.domain.repository import Repository, ScmType
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

        self.expected_script = self.test_dir / Path(self.install_script.name)

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
        self.when_install_script_is_written()

        self.then_install_script_should_exists_on_filesystem()

        self.then_install_script_data_should_be_correct()
        
    def testExistingScriptMovedBeforeCreation(self):
        """ Given a script with same name exists it should be moved to scriptname.bak"""
        self.given_exists_file_with_same_name()

        self.when_install_script_is_written()

        self.then_existing_file_should_be_backed_up()

        self.then_install_script_data_should_be_correct()


    def testScriptNameDoesNotEndWithSQL(self):
        """ Given script name doesn't end with SQL spool should be to scriptname.log"""
        self.given_script_name_doesnt_end_with_sql()

        self.when_install_script_is_created()

        self.then_spool_should_be_to_scriptname_log()

    ############
    # Behavior #
    ############
    def given_script_name_doesnt_end_with_sql(self):
        self.install_script.name = 'filename'
        self.expected_script = self.test_dir / Path(self.install_script.name)

    def given_exists_file_with_same_name(self):
        self.existing_file = self.test_dir/self.install_script.name
        self.existing_file.touch()

        self.assertTrue(self.existing_file.exists())

    def when_install_script_is_written(self):
        self.install_script._write_script(self.test_dir, self.expected_data)

    def when_install_script_is_created(self):
        self.install_script._write_script = Mock()

        self.install_script.create(self.test_dir)

    def then_install_script_should_exists_on_filesystem(self):
        self.assertTrue(self.expected_script.exists(), "File not created")

    def then_install_script_data_should_be_correct(self):
        written_lines = self.expected_script.lines(retain=False)

        self.assertEquals(self.expected_data, written_lines, "Written data should match expected.")

    def then_existing_file_should_be_backed_up(self):
        moved_file = self.existing_file + '.bak' 
        self.assertTrue(moved_file.exists(), "Backup file not created")

    def then_spool_should_be_to_scriptname_log(self):
        self.install_script._write_script.assert_called_with(self.test_dir, self.expected_data)

class RepositoryTests(TestCase):
    def testGetCvsProcessor(self):
        """ Repository's processor property should return an instance of CvsProcessor if Scm type is CVS"""
        from package.scm import CvsProcessor
        repository = Repository('root', 'module', ScmType.CVS)

        processor = repository.processor

        self.assertTrue(processor, "Processor not set")
        self.assertTrue(isinstance(processor, CvsProcessor), "Processor should be CVS instance")

    def testGetSvnProcessor(self):
        """ Repository's processor property should return an instance of SubversionProcessor if Scm type is SVN"""
        from package.scm import SubversionProcessor
        repository = Repository('root', 'module', ScmType.SVN)

        processor = repository.processor

        self.assertTrue(processor, "Processor not set")
        self.assertTrue(isinstance(processor, SubversionProcessor), "Processor should be CVS instance")





