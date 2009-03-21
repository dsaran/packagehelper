#!/usr/bin/python2.5
# Version: $Id: run.py,v 1.3 2009-03-21 20:57:45 daniel Exp $

from os import path
from sys import argv, path as pythonpath

__version__ = '0.1.2'

# Initializing PYTHONPATH
basedir = path.abspath(path.dirname(path.abspath(argv[0])))
libdir = path.abspath(path.join(basedir, 'lib'))
guidir = path.abspath(path.join(basedir, 'package'))
resdir = path.abspath(path.join(basedir, 'resources'))

pythonpath.insert(0, libdir)
pythonpath.insert(1, guidir)
pythonpath.insert(2, resdir)

# Initializing logger
import logging
from path import path as Path
from package.log import set_log_file
from os import environ
log = logging.getLogger('Runner')
homedir = Path(__file__).dirname()
LOG_FILE = Path.joinpath(homedir, 'packagehelper.log')
if not LOG_FILE.exists():
    print "Creating log file"
    LOG_FILE.touch()
environ['PKG_LOGFILE'] = str(LOG_FILE)
environ['PKG_HELPER_PATH'] = homedir
environ['PKG_BASEDIR'] = basedir
set_log_file(LOG_FILE, '*')
log.info("Logger started")

def run_no_gui():
    from package.ui.text import PackageProcessorUI
    PackageProcessorUI()

def run_gui():
    from package.ui.gui import PackageProcessorGUI
    app = PackageProcessorGUI()
    app.main()


if __name__ == "__main__":
    # Checking parameters
    if "--help" in argv[:]:
        print "Usage: " + __file__ + " [OPTION]"
        print """\nCheckout files from CVS using the given tags and create
    the execution scripts for *.sql files.
    The files are expected to have a directory tree like './<BD>/<USERNAME>/<TYPE>/script.sql'
    OPTIONS:
         --no-gui  Do not use graphical user interface."""

    elif "--no-gui" in argv[:]:
        log.info("Running with no GUI")
        try:
            run_no_gui()
        except Exception:
            log.error("Error loading processorUI!", exc_info=1)
            raise
    else:
        try:
            run_gui()
        except ImportError:
            log.error("Error loading GUI, trying to load command line interface", exc_info=1)
            run_no_gui()
        except Exception:
            log.error("Error loading GUI!", exc_info=1)
            raise

