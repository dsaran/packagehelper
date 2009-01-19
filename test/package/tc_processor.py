#from test import pmock
from test import mock
from test.framework import TestCase
from package.processor import PackageProcessor
from package.domain.tag import Tag
from package.domain.package import Package
from package.domain.repository import Repository
from package.commandrunner import CommandRunner
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

        # Preparing mocks
        #self.configMock = pmock.Mock()
        #self.configMock.expects(pmock.once()).method("get_cvs").will(pmock.return_value("cvsmock"))

    def testCheckout(self):
        #cvsMock = pmock.Mock()
        cvsExportMock = mock.Mock()
        cvsTagMock = mock.Mock()
        #cvsMock.expects(pmock.exactly(6)).method("export")
        #cvsMock.expects(pmock.exactly(6)).method("tag")

        # Workaround to use mock with objects created inside the method execution.
        CVS.export = cvsExportMock.export
        CVS.tag = cvsTagMock.tag

        processor = PackageProcessor(self.package)
        processor.checkout_files()

        self.assertEquals(6, len(cvsExportMock.method_calls), "Wrong number of export calls.")
        self.assertEquals(6, len(cvsTagMock.method_calls), "Wrong number of tag calls.")

        #cvsMock.verify()

