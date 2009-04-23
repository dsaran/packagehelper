from test.framework import TestCase
from package.util.format import urljoin, url_split

class UrlTests(TestCase):

    def testValidUrlJoin(self):
        """ UrlJoin should works with arguments with no '/' at start or end"""
        url = 'http://hostname.org/test'
        joined = urljoin(url, 'suffix')
        self.assertEquals('http://hostname.org/test/suffix', joined)


    def testValidUrlJoinSlashesBefore(self):
        """ UrlJoin should works with arguments starting with '/'"""
        url = 'http://hostname.org/test'
        joined = urljoin(url, '/suffix')
        self.assertEquals('http://hostname.org/test/suffix', joined)

    def testValidUrlJoinSlashesAfter(self):
        """ UrlJoin should works with arguments starting with '/'"""
        url = 'http://hostname.org/test/'
        joined = urljoin(url, 'suffix')
        self.assertEquals('http://hostname.org/test/suffix', joined)

    def testValidUrlJoinSlashesBeforeAndAfter(self):
        """ UrlJoin should works with arguments starting and ending with '/'"""
        url = 'http://hostname.org/test/'
        joined = urljoin(url, '/suffix/')
        self.assertEquals('http://hostname.org/test/suffix', joined)

    def testValidUrlJoinMultipleArgs(self):
        """ UrlJoin should works with multiple arguments"""
        url = 'http://hostname.org/test/'
        joined = urljoin(url, '/suffix1/', 'suffix2/', '/suffix3')
        self.assertEquals('http://hostname.org/test/suffix1/suffix2/suffix3', joined)

    def testValidUrlJoinSlashArg(self):
        """ UrlJoin should works with a '/' argument"""
        url = 'http://hostname.org/test/'
        joined = urljoin(url, '/suffix1/', '/', '/suffix2')
        self.assertEquals('http://hostname.org/test/suffix1/suffix2', joined)

    def testValidUrlAllSplittedInput(self):
        """ UrlJoin should works with all args splitted"""
        url = 'http://hostname.org/test/'
        joined = urljoin('http://', 'hostname.org', 'test', '/suffix1/', 'suffix2')
        self.assertEquals('http://hostname.org/test/suffix1/suffix2', joined)

    def testUrlSplitTrailingSlash(self):
        """ UrlSplit should correctly split a url with trailing slash"""
        url = 'http://hostname.org/test/path/'
        base, path = url_split(url)

        self.assertEquals('http://hostname.org/test', base)
        self.assertEquals('path', path)

    def testUrlSplitNoTrailingSlash(self):
        """ UrlSplit should correctly split a url with no trailing slash"""
        url = 'http://hostname.org/test/path'
        base, path = url_split(url)

        self.assertEquals('http://hostname.org/test', base)
        self.assertEquals('path', path)

    def testUrlRoot(self):
        """ UrlSplit should split correctly a root URL"""
        url = 'http://hostname.org/'

        base, path = url_split(url)

        self.assertEquals('http://hostname.org', base)
        self.assertEquals('/', path)

    def testUrlRootNoSlash(self):
        """ UrlSplit should split correctly a root URL with no trailing slash"""
        url = 'http://hostname.org'

        base, path = url_split(url)

        self.assertEquals('http://hostname.org', base)
        self.assertEquals('/', path)

