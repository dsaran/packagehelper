#! /usr/bin/env python2.5
# Version: $Id: sqlrunner.py,v 1.1.1.1 2009-01-07 22:58:30 daniel Exp $

import logging
from os import popen3, chdir
from package.config import Config

log = logging.getLogger('SqlRunner')

config = None

def run_scripts(list):
    if list:
        global config
        config = Config(load=True)
        log.debug(config.get_environments())

    for file in list:
        log.info('Running script ' + str(file))
        run_script(file)

def run_script(file):
    try:
        database = file.get_database()

        log.debug("Database => " + str(database))

        sqlplus = config.sqlplus
        envs = config.get_environments(database)

        log.debug("Environments found => " + str(envs))

        chdir(file.get_basepath())

        for env in envs:
            if env.is_active():
                conn_string = env.get_conn_string()

                command = sqlplus + " -L %s" % conn_string
                log.debug("Running: " + command)

                inFile, outFile, errFile = popen3(command)

                error = errFile.read()
                errFile.close()

                if not error: 
                    inFile.write('@%s \n' % file.get_name())
                    inFile.write('exit \n')

                    inFile.close()
                else:
                    log.error(error)
                    raise Exception("Error running command '%s': %s" % (command, error))

                if not outFile.closed:
                    out = outFile.read()
                    outFile.close()
        
                log.debug("output: " + out)
                log.info("Done.")

    except Exception:
        log.error("Error running script %s" % str(file), exc_info=1)
        raise

