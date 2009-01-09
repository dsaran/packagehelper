import unittest
from os import path
from sys import path as pythonpath

# Initializing PythonPath
ph_home = path.dirname(path.abspath(__file__))
pythonpath.insert(0, ph_home) 
ph_lib = path.join(ph_home, "lib")
pythonpath.insert(1, ph_lib) 
ph_test = path.join(ph_home, "test")
pythonpath.insert(2, ph_test) 

# Setting up Logger
from kiwi.log import set_log_file
set_log_file("Tests.log")

import unit.package.cvs
suite = unittest.TestLoader().loadTestsFromTestCase(unit.package.cvs.CvsTest)
unittest.TextTestRunner(verbosity=2).run(suite)

