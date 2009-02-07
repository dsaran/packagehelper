# Version: $id$

from test import mock
from test.framework import TestCase
from package.processor import PackageProcessor
from package.domain.tag import Tag
from package.domain.pack import Package
from package.domain.repository import Repository
from package.cvs import CVS
from path import path as Path

class PackageProcessorTests(TestCase):
    def setUp(self):
        self.package = Package("TestPackage")
        self.current_dir = Path(__file__).dirname()
        self.package.set_path(self.current_dir)
        for i in (1, 2, 3):
            tag = Tag("Tag" + str(i))
            self.package.add_tag(tag)
        for i in (1, 2, 3):
            repository = Repository("root" + str(i), "module" + str(i), (i != 3))
            self.package.add_repository(repository)

    def testCheckout(self):
        """ Checkout should call export and tag cvs commands for each tag and each module."""
        cvsExportMock = mock.Mock()
        cvsTagMock = mock.Mock()

        # Workaround to use mock with objects created inside the method execution.
        CVS.export = cvsExportMock.export
        CVS.tag = cvsTagMock.tag

        processor = PackageProcessor(self.package)
        processor.checkout_files()

        self.assertEquals(6, len(cvsExportMock.method_calls), "Wrong number of export calls.")
        self.assertEquals(6, len(cvsTagMock.method_calls), "Wrong number of tag calls.")

    def testCheckoutDestination(self):
        """ Checkout should call export command with the correct destination path."""
        cvsExportMock = mock.Mock()
        cvsTagMock = mock.Mock()

        # Workaround to use mock with objects created inside the method execution.
        CVS.export = cvsExportMock.export
        CVS.tag = cvsTagMock.tag
        package_name = "Test Package"

        package = Package(package_name)
        package.set_path(self.current_dir)

        package.add_tag(self.package.get_tags()[0])
        package.add_repository(self.package.get_repositories()[0])

        processor = PackageProcessor(package)
        processor.checkout_files() 

        self.assertEquals(1, len(cvsExportMock.method_calls), "Wrong number of export calls.")
        self.assertEquals(1, len(cvsTagMock.method_calls), "Wrong number of tag calls.")

        expected_path = self.current_dir / package_name
        call_args = cvsExportMock.method_calls[0][1]
        self.assertEquals(expected_path, call_args[0])

