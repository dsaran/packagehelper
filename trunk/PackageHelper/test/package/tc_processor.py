# Version: $id$

from test import mock
from test.framework import TestCase
from package.processor import PackageProcessor
from package.domain.database import Database
from package.domain.tag import Tag
from package.domain.file import File, InstallScript
from package.domain.pack import Package
from package.domain.repository import Repository
from package.scm import CvsProcessor
from path import path as Path

class PackageProcessorTests(TestCase):
    def setUp(self):
        self.package = Package("TestPackage")
        self.current_dir = Path(__file__).dirname()
        self.package.path = self.current_dir
        self.processor = PackageProcessor(self.package)

        for i in (1, 2, 3):
            tag = Tag("Tag" + str(i))
            self.package.add_tag(tag)
        for i in (1, 2, 3):
            repository = Repository("root" + str(i), "module" + str(i), active=(i != 3))
            self.package.add_repository(repository)

    def testCheckout(self):
        """ Checkout should call export and tag cvs commands for each tag and each module."""
        cvsExportMock = mock.Mock()
        cvsTagMock = mock.Mock()
        self.processor._load_files = mock.Mock()


        # Workaround to use mock with objects created inside the method execution.
        CvsProcessor.export = cvsExportMock.export
        CvsProcessor.tag = cvsTagMock.tag

        self.processor.checkout_files()

        self.assertEquals(6, cvsExportMock.export.call_count, "Wrong number of export calls.")
        self.assertEquals(6, cvsTagMock.tag.call_count, "Wrong number of tag calls.")

    def testCheckoutDestination(self):
        """ Checkout should call export command with the correct destination path."""
        cvsExportMock = mock.Mock()
        cvsTagMock = mock.Mock()

        # Workaround to use mock with objects created inside the method execution.
        CvsProcessor.export = cvsExportMock.export
        CvsProcessor.tag = cvsTagMock.tag
        package_name = "Test Package"

        package = Package(package_name)
        package.path = self.current_dir

        package.add_tag(self.package.get_tags()[0])
        package.add_repository(self.package.get_repositories()[0])

        processor = PackageProcessor(package)
        processor._load_files = mock.Mock()
        processor.checkout_files() 

        self.assertEquals(1, len(cvsExportMock.method_calls), "Wrong number of export calls.")
        self.assertEquals(1, len(cvsTagMock.method_calls), "Wrong number of tag calls.")

        expected_path = self.current_dir / package_name
        call_args = cvsExportMock.method_calls[0][1]
        self.assertEquals(expected_path, call_args[0])

    def testProcessFiles(self):
        """ Given I checked out files when i process files scripts should be grouped correctly"""

        self.givenICheckedOutFiles()

        self.whenIProcessFiles()

        self.shouldBeGroupedCorrectly()


    def givenICheckedOutFiles(self):
        database = Database(name='BD', user='USER')
        f1 = File('/some/path/to/package/TAG/BD/USER/PKB/pkb_file.sql')
        f1.type = 'PKB'
        f1.database = database
        m = mock.Mock()
        m.return_value = 'CAT1'
        f1.get_category = m

        f2 = File('/some/path/to/package/TAG/BD/USER/GRANT/grant_script.sql')
        f2.type = 'GRANT'
        f2.database = database
        m = mock.Mock()
        m.return_value = 'CAT2'
        f2.get_category = m
        f3 = File('/some/path/to/package/TAG/BD/USER/IDX/index_script.sql')
        f3.type = 'IDX'
        f3.database = database
        m = mock.Mock()
        m.return_value = 'CAT3'
        f3.get_category = m

        self.processor._process_other = mock.Mock()
        self.processor._get_files = mock.Mock()
        self.processor._get_files.return_value = [f1, f2, f3]

        s1 = InstallScript('001_USER_BD.sql', content=[f1])
        s2 = InstallScript('002_USER_BD.sql', content=[f2])
        s3 = InstallScript('003_USER_BD.sql', content=[f3])

        self.expected_scripts = [s1, s2, s3] 


    def whenIProcessFiles(self):
        self.groupedFiles = self.processor.process_files()
 

    def shouldBeGroupedCorrectly(self):
        self.assertEquals(self.expected_scripts, self.groupedFiles)

