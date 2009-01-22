# Version: $id$

from test import mock
from test.framework import TestCase
from package.processor import PackageProcessor
from package.domain.tag import Tag
from package.domain.package import Package
from package.domain.repository import Repository
from package.cvs import CVS
from os import path

class PackageProcessorTests(TestCase):
    def setUp(self):
        self.package = Package("TestPackage")
        self.package.set_path(path.dirname(__file__))
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

