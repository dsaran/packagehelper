#!/usr/bin/python
import unittest
from os import path
from sys import argv, path as pythonpath

# Initializing PythonPath
basedir = path.abspath(path.dirname(path.abspath(argv[0])))
libdir = path.abspath(path.join(basedir, 'lib'))
guidir = path.abspath(path.join(basedir, 'package'))
pythonpath.insert(0, libdir)
pythonpath.insert(1, guidir)

# Setting up Logger
from package.log import set_log_file
set_log_file("Tests.log")

import test.package.tc_scm
import test.package.tc_processor
import test.package.types.tc_matcher
import test.package.types.tc_parser
import test.package.types.tc_loader
import test.package.rollback.tc_parser
import test.parser.tc_plsql
import test.package.gui.tc_filetree
import test.package.gui.tc_app
import test.package.tc_domain
import test.package.tc_config


tests = []
tests.append(unittest.TestLoader().loadTestsFromTestCase(test.package.tc_scm.CvsTest))
tests.append(unittest.TestLoader().loadTestsFromTestCase(test.package.tc_scm.SubversionTests))
tests.append(unittest.TestLoader().loadTestsFromTestCase(test.package.tc_processor.PackageProcessorTests))
tests.append(unittest.TestLoader().loadTestsFromTestCase(test.package.types.tc_matcher.MatcherTests))
tests.append(unittest.TestLoader().loadTestsFromTestCase(test.package.types.tc_parser.ParserTests))
tests.append(unittest.TestLoader().loadTestsFromTestCase(test.package.types.tc_loader.LoaderTests))
tests.append(unittest.TestLoader().loadTestsFromTestCase(test.parser.tc_plsql.PlSqlParserTests))
tests.append(unittest.TestLoader().loadTestsFromTestCase(test.package.gui.tc_filetree.FileTreeTests))
tests.append(unittest.TestLoader().loadTestsFromTestCase(test.package.gui.tc_app.AppGuiTests))
tests.append(unittest.TestLoader().loadTestsFromTestCase(test.package.gui.tc_app.MainDataStepTests))
tests.append(unittest.TestLoader().loadTestsFromTestCase(test.package.gui.tc_app.ReleaseNotesStepTests))
tests.append(unittest.TestLoader().loadTestsFromTestCase(test.package.gui.tc_app.ManageFilesStepTests))
tests.append(unittest.TestLoader().loadTestsFromTestCase(test.package.tc_domain.PackageTests))
tests.append(unittest.TestLoader().loadTestsFromTestCase(test.package.tc_domain.InstallScriptTests))
tests.append(unittest.TestLoader().loadTestsFromTestCase(test.package.tc_domain.RepositoryTests))
tests.append(unittest.TestLoader().loadTestsFromTestCase(test.package.tc_config.RepositoryConfigTests))

# Broken until plsql parser (yapps) is finished.
#tests.append(unittest.TestLoader().loadTestsFromTestCase(test.package.rollback.tc_parser.SqlParserTests))

suite = unittest.TestSuite(tests)
unittest.TextTestRunner(verbosity=2).run(suite)

