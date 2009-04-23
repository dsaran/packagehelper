from test.framework import TestCase
from test.mock import Mock
from package.util.svnutil import ReleaseXmlParser, Release
import time

class SvnUtilTests(TestCase):
    def setUp(self):
        r1 = Release()
        r1.name = 'BETA1.1.0'
        r1.type = 'BETA'
        r1.version = '1.1.0'
        r1.date = time.strptime('2009-04-21 23:22:03', '%Y-%m-%d %H:%M:%S')

        r2 = Release()
        r2.name = 'STABLE0.4.9'
        r2.type = 'STABLE'
        r2.version = '0.4.9'
        r2.date = time.strptime('2009-01-07 22:58:31', '%Y-%m-%d %H:%M:%S')

        self.expected = [r1, r2]

    def testXmlLoad(self):
        """ XML from svn list should be parsed correctly into releases"""
        loader = ReleaseXmlParser(text=xml)
        releases = loader.get_releases()

        self.assertTrue(releases, 'No release loaded')
        self.assertEquals(self.expected, releases, "Releases not loaded correctly")


xml = """<?xml version="1.0"?>
<lists>
<list
   path="svn://localhost/tools/packagehelper/tags">
<entry
   kind="dir">
<name>1.0.1b</name>
<commit
   revision="39">
<author>daniel</author>
<date>2009-04-07T05:59:19.743486Z</date>
</commit>
</entry>
<entry
   kind="dir">
<name>BETA1.1.0</name>
<commit
   revision="43">
<author>dsaran</author>
<date>2009-04-21T23:22:03.748373Z</date>
</commit>
</entry>
<entry
   kind="dir">
<name>RELEASE_1_0_0b</name>
<commit
   revision="37">
<author>daniel</author>
<date>2009-04-06T17:49:17.446056Z</date>
</commit>
</entry>
<entry
   kind="dir">
<name>STABLE0.4.9</name>
<commit
   revision="3">
<date>2009-01-07T22:58:31.000000Z</date>
</commit>
</entry>
</list>
</lists>"""
