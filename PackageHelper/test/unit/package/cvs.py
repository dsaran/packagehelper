from sys import path as pythonpath
from os import path

OK = " => OK"
ERROR = " => Error (found: %s)"
# Create mock for command runner
class CommandRunnerMock:
    commands = []
    def run(self, command):
        self.commands.append(command)

class ConfigMock:
    def get_cvs(self):
        return "cvsmock"

class CvsTest:

    def __run__(self):
        self.setup()
        self.testExport()

    def setup(self):
        # Initializing PythonPath
        localdir = path.dirname(path.abspath(__file__))
        ph_home = path.join(localdir, "../../../")
        pythonpath.insert(0, ph_home) 
        ph_lib = path.join(ph_home, "lib")
        pythonpath.insert(1, ph_lib) 

        # Setting up Logger
        from kiwi.log import set_log_file
        set_log_file("Tests.log")


        self.cvsroot = ":pserver:user:pass@localhost:/var/local/cvs"
        self.module = "TestData/TestData"
        self.tag = "TEST_TAG"
        self.test_data_dir = path.join(localdir, "test_data")
        self.runner = CommandRunnerMock()

    def testExport(self):
        from package.cvs import CVS

        cvs = CVS(self.cvsroot, self.module)
        cvs.runner = self.runner
        cvs.get_config = lambda: ConfigMock()
        cvs.export(self.test_data_dir, self.tag)
    
        print "Checking login command line: ",
        if self.runner.commands[0] == ("cvsmock -d%s login" % self.cvsroot):
            print OK
        else:
            print ERROR % self.runner.commands[0]

if __name__ == "__main__":
    CvsTest().__run__()

