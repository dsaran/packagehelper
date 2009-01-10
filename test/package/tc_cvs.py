from sys import path as pythonpath
from os import path, rmdir
from test.framework import TestCase
from package.cvs import CVS


OK = " => OK"
ERROR = " => Error (found: %s)"
# Create mock for command runner
class CommandRunnerMock:
    commands = None
    def __init__(self):
        self.commands = []

    def run(self, command):
        self.commands.append(command)

class ConfigMock:
    def get_cvs(self):
        return "cvsmock"

class CvsTest(TestCase):

    def __run__(self):
        self.setUp()
        self.testExport()
        self.tearDown()

    def setUp(self):
        self.cvsroot = ":pserver:user:pass@localhost:/var/local/cvs"
        self.module = "TestData/TestData"
        self.tag = "TEST_TAG"
        self.test_data_dir = path.join(path.dirname(__file__), "test_data")
        self.runner = CommandRunnerMock()
        self.cvs = CVS(self.cvsroot, self.module)
        self.cvs.runner = self.runner
        self.cvs.get_config = lambda: ConfigMock()


    def tearDown(self):
        if path.exists(self.test_data_dir):
            rmdir(self.test_data_dir)


    def testLogin(self):
        self.cvs.login()

        self.assertEquals(len(self.runner.commands), 1)
        self.assertEquals(self.runner.commands[0], "cvsmock -d%s login" % self.cvsroot, "Invalid cvs login command: %s" % self.runner.commands[0])


    def testExport(self):
        self.cvs.export(self.test_data_dir, self.tag)

        # Two command should run when exporting from cvs: login and export
        self.assertEquals(len(self.runner.commands), 2) 
 
        expected = "cvsmock -q -z 9 export -d %s -r %s %s" % (self.tag, self.tag, self.module)
        actual = self.runner.commands[1]
        self.assertEquals(expected, actual)

        self.assertTrue(path.exists(self.test_data_dir), "Destination path should have been created.")


if __name__ == "__main__":
    # Initializing PythonPath
    localdir = path.dirname(path.abspath(__file__))
    ph_home = path.join(localdir, "../../")
    pythonpath.insert(0, ph_home) 
    ph_lib = path.join(ph_home, "lib")
    pythonpath.insert(1, ph_lib) 
    ph_test = path.join(ph_home, "test")
    pythonpath.insert(2, ph_test) 

    from framework import TestCase
    # Setting up Logger
    from kiwi.log import set_log_file
    set_log_file("Tests.log")


    #unittest.main()
    suite = unittest.TestLoader().loadTestsFromTestCase(CvsTest)
    unittest.TextTestRunner(verbosity=2).run(suite)

