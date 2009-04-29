# encoding: utf-8
# Version: $Id$

import logging
import subprocess
import time

from package.log import GlobalLogger

log = logging.getLogger("CommandRunner")

class Command:
    args = None
    command = None

    def __init__(self, command=None, args=None):
        self.command = command
        self.args  = args or []

    def __str__(self):
        return "<COMMAND " + self.command + " " + " ".join(self.args) + "/>"
    __repr__ = __str__

    def __eq__(self, other):
        return hasattr(other, "full_command") and self.full_command == other.full_command

    def getcommand(self):
        return [self.command] + self.args

    full_command = property(getcommand)

class CommandRunner:

    def run(self, command):
        """ Runs the command and returns the stderr.
            @return strout, stderr from command execution."""
        log.debug("Executing command: " + str(command))

        output, error = "", ""
        p = subprocess.Popen(command.full_command, stdout=subprocess.PIPE)

        for line in p.stdout:
            output += line
            log.debug(line)
        stdout, error = p.communicate()

        return output, error

