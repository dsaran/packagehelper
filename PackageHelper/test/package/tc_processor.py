from test.framework import TestCase
from package.processor import PackageProcessor
from package.domain.tag import Tag
from package.domain.package import Package
from package.domain.repository import Repository
from package.commandrunner import CommandRunner
from package.cvs import CVS
from os import path

def run(self, command):
    if not self.commands.has_key(command):
        self.commands[command] = 0
    self.commands[command] += 1

def run_export(self, *args):
    run(self, 'export')

def run_tag(self, *args):
    run(self, 'tag')

class ConfigMock:
    def get_cvs(self):
        return "cvsmock"


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

        CVS.get_config = lambda(self): ConfigMock()
        CVS.commands = {}
        CVS.export = run_export
        CVS.tag = run_tag

    def testCheckout(self):
        processor = PackageProcessor(self.package)
        processor.checkout_files()

        commands = CVS.commands
        self.assertEquals(6, commands['export'], "Wrong number of export commands called.")
        self.assertEquals(6, commands['tag'], "Wrong number of tag commands called.")



