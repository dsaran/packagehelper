from os import popen

class CommandRunner:

    def run(self, command):
        """ Runs the command and returns the stderr.
            @return stderr from command execution."""
        log.debug("Executing command: " + command)

        errorfile = popen(command)
        error = errorfile.read()
        errorfile.close()
        return error

