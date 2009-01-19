from test.framework import TestCase
from test.mock import Mock
from package.types.matcher import ParentDirectoryMatcher
from package.domain.file import File

class MatcherTests(TestCase):
    def setUp(self):
        filename = "/path/to/module/base/trash/Database/Username/Type/001_prefix_filename.sql"
        self.file = Mock()
        self.file.get_path.return_value = filename
        self.matcher = ParentDirectoryMatcher()

    def testParentDirectoryMatcher_equals(self):
        expected = "Type"
        result = self.matcher.match(expected, self.file)

        self.assertTrue(result)

    def testParentDirectoryMatcher_case_insensitive(self):
        expected = "TYPE"
        result = self.matcher.match(expected, self.file)

        self.assertTrue(result)

