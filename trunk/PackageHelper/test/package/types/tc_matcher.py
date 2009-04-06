# Version: $id$

from test.framework import TestCase
from test.mock import Mock
from package.types.matchers import ParentDirectoryMatcher
from package.domain.file import File

class MatcherTests(TestCase):
    def setUp(self):
        filename = "/path/to/module/base/trash/Database/Username/Type/001_prefix_filename.sql"
        self.file = Mock()
        self.file.get_path.return_value = filename

    def testParentDirectoryMatcher_equals(self):
        """ParentDirectoryMatcher should match exactly the same name."""
        expected = "Type"
        matcher = ParentDirectoryMatcher(expected)
        result = matcher.match(self.file)

        self.assertTrue(result)

    def testParentDirectoryMatcher_case_insensitive(self):
        """ParentDirectoryMatcher should match paths in different cases."""
        expected = "TYPE"
        matcher = ParentDirectoryMatcher(expected)
        result = matcher.match(self.file)

        self.assertTrue(result)

    def testParentDirectoryMatcher_contains(self):
        """ParentDirectoryMatcher should not match partly to a parent directory."""
        expected="Types"
        matcher = ParentDirectoryMatcher(expected)
        result = matcher.match(self.file)

        self.assertFalse(result)

