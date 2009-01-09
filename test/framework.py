import unittest

class TestCase(unittest.TestCase):

    def assertEquals(self, expected, actual, msg=""):
        if not expected == actual:
            raise self.failureException,\
                (msg + "Expected %s but found %s." % (expected, actual)) 

