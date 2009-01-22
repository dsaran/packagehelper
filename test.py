import unittest
from os import path
from sys import path as pythonpath

# Initializing PythonPath
ph_home = path.dirname(path.abspath(__file__))
pythonpath.insert(0, ph_home) 
ph_lib = path.join(ph_home, "lib")
pythonpath.insert(1, ph_lib) 
#ph_test = path.join(ph_home, "test")
#pythonpath.insert(2, ph_test) 

# Setting up Logger
from kiwi.log import set_log_file
set_log_file("Tests.log")

import test.package.tc_cvs
import test.package.tc_processor
import test.package.types.tc_matcher
import test.package.types.tc_parser

cvs_suite = unittest.TestLoader().loadTestsFromTestCase(test.package.tc_cvs.CvsTest)
processor_suite = unittest.TestLoader().loadTestsFromTestCase(test.package.tc_processor.PackageProcessorTests)
matcher_suite = unittest.TestLoader().loadTestsFromTestCase(test.package.types.tc_matcher.MatcherTests)
parser_suite = unittest.TestLoader().loadTestsFromTestCase(test.package.types.tc_parser.ParserTests)

suite = unittest.TestSuite([cvs_suite, processor_suite, matcher_suite, parser_suite])
unittest.TextTestRunner(verbosity=2).run(suite)

