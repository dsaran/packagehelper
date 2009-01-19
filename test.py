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

cvs_suite = unittest.TestLoader().loadTestsFromTestCase(test.package.tc_cvs.CvsTest)
processor_suite = unittest.TestLoader().loadTestsFromTestCase(test.package.tc_processor.PackageProcessorTests)
types_suite = unittest.TestLoader().loadTestsFromTestCase(test.package.types.tc_matcher.MatcherTests)
suite = unittest.TestSuite([cvs_suite, processor_suite, types_suite])
unittest.TextTestRunner(verbosity=2).run(suite)

