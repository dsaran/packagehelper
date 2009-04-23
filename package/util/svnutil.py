import xml.dom.minidom
import logging
import re
import time

log = logging.getLogger('svnutil')

class Release:
    name = None
    version = None
    type = None
    date = None

    def __eq__(self, other):
        return self.name == other.name \
            and self.version == other.version \
            and self.type == other.type \
            and self.date == other.date

    def gettime(self):
        return time.strftime('%Y-%m-%d %H:%M:%S', self.date)

    time = property(gettime)

    def __str__(self):
        d = time.strftime('%Y-%m-%d %H:%M:%S', self.date)
        return "<Release name:%s, type:%s, version:%s, date:%s/>" % \
            (self.name, self.type, self.version, d)

    __repr__ = __str__

class ReleaseXmlParser:
    def __init__(self, file=None, text=None):
        self.date_pattern = re.compile('\\d\\d\\d\\d-\\d\\d-\\d\\dT\\d\\d:\\d\\d:\\d\\d')
        self.release_pattern = re.compile('(?P<type>BETA|STABLE)(?P<version>\\d+.\\d+.\\d+)')
        if file:
            self._doc = xml.dom.minidom.parse(file)
        elif text:
            self._doc = xml.dom.minidom.parseString(text)
        else:
            raise Exception("Missing file/text argument - text:'%s' file:'%s'" % (text, file))

    def get_releases(self):
        entries = self._doc.getElementsByTagName('entry')
        releases = []
        for entry in entries:
            if not entry.getAttribute('kind') == 'dir':
                continue
            name_el = entry.getElementsByTagName("name")[0]
            name = name_el.childNodes[0].data

            matcher = self.release_pattern.match(name)
            if not matcher:
                log.debug('Tag discarded: %s' % name)
                continue
            groups = matcher.groupdict()

            release = Release()
            release.name = name
            release.version = groups['version']
            release.type = groups['type']

            commit_el = entry.getElementsByTagName("commit")[0]
            commit_date_el = commit_el.getElementsByTagName("date")[0]
            commit_date_data = commit_date_el.childNodes[0].data
            date = self.date_pattern.findall(commit_date_data)[0]
            release.date = time.strptime(date, '%Y-%m-%dT%H:%M:%S')

            releases.append(release)

        return releases


