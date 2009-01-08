from os import popen

class CommandRunner:
    def __init__(self, command):
        self.command = command

    def run(self):
    """ Runs the command and returns the stderr.
        @return stderr from command execution."""
        log.debug("Executing command: " + command)

        errorfile = popen(command)
        error = errorfile.read()
        errorfile.close()
        return error

