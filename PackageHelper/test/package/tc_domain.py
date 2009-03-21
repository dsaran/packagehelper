from test.framework import TestCase

from package.domain.pack import Package
from path import path as Path

class PackageTests(TestCase):
    def setUp(self):
        self.package = Package()

    def testPathShouldAcceptString(self):
        """Package path property should accept strings"""
        self.package.path = '/tmp/'
        self.assertEquals(Path, type(self.package.path))
        self.assertEquals(Path('/tmp'), self.package.path)

    def testPathShouldAcceptPath(self):
        """Package path property should accept Path"""
        self.package.path = Path('/tmp/')
        self.assertEquals(Path, type(self.package.path))
        self.assertEquals(Path('/tmp'), self.package.path)

    def testPathShouldNotAcceptOtherTypes(self):
        """Package path property should not accept other types"""
        ok = False
        try:
            self.package.path = 1234
        except ValueError:
            ok = True
        self.assertTrue(ok)
        self.assertEquals(None, self.package.path)

        ok = False
        try:
            self.package.path = Package()
        except ValueError:
            ok = True
        self.assertTrue(ok)
        self.assertEquals(None, self.package.path)

