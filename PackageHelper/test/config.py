#!/usr/bin/python2.5
# Version: $Id$

from os import path
from sys import argv, path as pythonpath

__version__ = '0.1.2'

# Initializing PYTHONPATH
basedir = path.dirname(path.abspath(argv[0]))
libdir = path.join(basedir, 'lib')
guidir = path.join(basedir, 'package')
resdir = path.join(basedir, 'resources')

pythonpath.insert(0, libdir)
pythonpath.insert(1, guidir)
pythonpath.insert(2, resdir)

# Initializing logger
import logging
from lib.path import path as Path
from kiwi.log import set_log_file
from os import environ
log = logging.getLogger('Runner')
homedir = Path(__file__).getcwd()
LOG_FILE = Path.joinpath(homedir, 'packagehelper.log')
if not LOG_FILE.exists():
    print "Creating log file"
    LOG_FILE.touch()
environ['PKG_LOGFILE'] = str(LOG_FILE)
set_log_file(LOG_FILE, '*')
log.info("Logger started")

# Checking parameters
if "--help" in argv[:]:
    print "Usage: " + __file__ + " [OPTION]"
    print """\nCheckout files from CVS using the given tags and create
the execution scripts for *.sql files.
The files are expected to have a directory tree like './<BD>/<USERNAME>/<TYPE>/script.sql'
OPTIONS:
     --no-gui  Do not use graphical user interface."""

from package.gui.config import ConfigEditor
config = ConfigEditor()

#elif "--no-gui" in argv[:]:
#    log.info("Running with no GUI")
#    try:
#        from package.ProcessorUI import ProcessorUI
#        ProcessorUI()
#    except Exception:
#        log.error("Error loading processorUI!", exc_info=1)
#        raise
#else:
#    try:
#        from package.gui.PackageProcessorGUI import PackageProcessorGUI
#        PackageProcessorGUI()
#    except Exception:
#        log.error("Error loading GUI!", exc_info=1)
#        raise

