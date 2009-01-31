import unittest
from os import path
from sys import path as pythonpath

# Initializing PythonPath
ph_home = path.dirname(path.abspath(__file__))
pythonpath.insert(0, ph_home) 
ph_lib = path.join(ph_home, "lib")
pythonpath.insert(1, ph_lib) 

# Setting up Logger
from kiwi.log import set_log_file
set_log_file("Tests.log")

import test.package.tc_cvs
import test.package.tc_processor
import test.package.types.tc_matcher
import test.package.types.tc_parser
import test.package.types.tc_loader
import test.package.rollback.tc_parser

tests = []
tests.append(unittest.TestLoader().loadTestsFromTestCase(test.package.tc_cvs.CvsTest))
tests.append(unittest.TestLoader().loadTestsFromTestCase(test.package.tc_processor.PackageProcessorTests))
tests.append(unittest.TestLoader().loadTestsFromTestCase(test.package.types.tc_matcher.MatcherTests))
tests.append(unittest.TestLoader().loadTestsFromTestCase(test.package.types.tc_parser.ParserTests))
tests.append(unittest.TestLoader().loadTestsFromTestCase(test.package.types.tc_loader.LoaderTests))
tests.append(unittest.TestLoader().loadTestsFromTestCase(test.package.rollback.tc_parser.SqlParserTests))

suite = unittest.TestSuite(tests)
unittest.TextTestRunner(verbosity=2).run(suite)

