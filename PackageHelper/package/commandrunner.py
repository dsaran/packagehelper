import logging
import os
import subprocess
import time

from package.log import GlobalLogger

log = logging.getLogger("CommandRunner")

class CommandRunner:

    def run(self, command):
        """ Runs the command and returns the stderr.
            @return stderr from command execution."""
        log.debug("Executing command: " + command)
        p = subprocess.Popen(command.split(), stdout=subprocess.PIPE)
        #for line in p.stdout:
        #    GlobalLogger.instance.info(line)
        #    print '--> ', line

        #while True:
        #    line = p.stdout.readline()
        #    if not line:
        #        #time.sleep(1)
        #        if p.poll() != None:
        #            break
        #        continue
        p.communicate()

        return "", ""

