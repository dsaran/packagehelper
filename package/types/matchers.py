# Version: $id$

class Matcher:
    def match(self, expected, file):
        return False


class PathRegexMatcher(Matcher):
    def __init__(self, regex=None):
        """Uses the given regex to match against the full path (uppercase)."""
        import re
        self.pattern = re.compile(regex)

    def match(self, file):
        match = self.pattern.search(file.get_path().upper())
        return bool(match)


class ParentDirectoryMatcher(Matcher):
    def __init__(self, expectedParent):
        """Uses the type (parent directory name) to match."""
        self._expectedParent = expectedParent

    def match(self, file):
        from os.path import sep
        filetype = file.get_path().split(sep)[-2].upper()
        return self._expectedParent.upper() == filetype

