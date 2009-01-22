
class Matcher:
    def match(self, expected, file):
        return False


class PathRegexMatcher(Matcher):
    def __init__(self):
        """Uses the given regex to match against the full path (uppercase)."""

    def match(self, expected, file):
        import re
        pattern = re.compile(expected)
        match = pattern.search(file.get_path().upper())
        return bool(match)


class ParentDirectoryMatcher(Matcher):
    def __init__(self):
        """Uses the type (parent directory name) to match."""

    def match(self, expected, file):
        from os.path import sep
        filetype = file.get_path().split(sep)[-2].upper()
        return expected.upper() == filetype

