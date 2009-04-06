import logging
import os

log = logging.getLogger("CommandRunner")

class CommandRunner:

    def run(self, command):
        """ Runs the command and returns the stderr.
            @return stderr from command execution."""
        log.debug("Executing command: " + command)

        inputfile, outputfile, errorfile = os.popen3(command)
        try:
            output = outputfile.read()
            error = errorfile.read()
        finally:
            inputfile.close()
            outputfile.close()
            errorfile.close()
        return output, error

