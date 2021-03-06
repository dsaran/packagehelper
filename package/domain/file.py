#!/usr/bin/python2.5
# encoding: utf-8
# Version: $Id$

from os import sep
from path import path as Path
from package.util.format import ENCODING
from package.domain.database import Database
import logging

log = logging.getLogger('File')

class File(object):
    TYPE_ORDER = {'TAB':1, 'VIEW':5, 'DDL':10, 'TRG':15, 'IDX':20, 'DML':25, 'ACT_BD':30, 'PKH':35, 'PKB':40, 'GRANT':45}
    CATEGORIES = {'COMPILABLE':['PKH', 'PKB', 'FNC', 'PRC', 'GRANT', 'TRG', 'IDX', 'DDL', 'VIEW', 'TAB'], 'COMMITABLE':['DML', 'ACT_BD']}

    _database = None
    _type = None
    _name = None
    _basepath = None
    _path = None

    def __init__(self, path=None, basepath=None, parse=False):
        """ Constructor.
        @param path 'path' instance or a string representing the file"
        @param basepath 'path' instance or a string representing package path.
        @param parse (optional) if the filename must be parsed."""
        self._database = None
        self._type = None
        self._name = None
        self._basepath = None
        self._path = None

        if basepath:
            self._basepath = basepath
            if not self._basepath.endswith(sep):
                self._basepath += sep

        if path:
            self._path = path
            if not hasattr(self._path, 'splitall'):
                self._path = Path(self._path)

            fileDetails = self._path.splitall()
            self._name = fileDetails[-1]

        if parse:
            try:
                db = fileDetails[-4].upper()
                dbUser = fileDetails[-3].upper()
                self._database = Database(db, dbUser)
                self._type = fileDetails[-2].upper()
                log.debug("File Created [db: %s, dbUser: %s, type: %s, name: %s]"%\
                            (db, dbUser, self._type, self._name))
            except IndexError:
                log.warn("Unknown file path: " + path)
                raise ValueError

    def getname(self):
        return self._name

    def getdatabase(self):
        return self._database

    def gettype(self):
        return self._type

    def getpath(self):
        return self._path #self._basepath + self._path

    def getbasepath(self):
        return self._basepath

    def setname(self, name):
        self._name = name

    def setdatabase(self, database):
        self._database = database

    def settype(self, type):
        self._type = type

    def setpath(self, path):
        self._path = path

    name = property(getname, setname, doc="File name (ex: /path/to/filename.ext -> filename.ext)")
    database = property(getdatabase, setdatabase, doc="Database extracted from path")
    type = property(gettype, settype, doc="Type extracted from path")
    path = property(getpath, setpath, doc="Full path of file")

    def __repr__(self):
        return str(self._path)

    def __str__(self):
        return "<File name: %s, database: %s, type: %s>" \
                % (self.name, self.database, self.type)

    def get_order(self):
        if (not self.TYPE_ORDER.has_key(self._type)):
            return max(self.TYPE_ORDER.values())
        return self.TYPE_ORDER[self._type]

    def get_category(self):
        for cat in self.CATEGORIES.keys():
            if self._type in self.CATEGORIES[cat]:
                return cat
        return 'OTHER'

    def __cmp__(self, other):
        """Compare a file instance. The criterias are:
        1 - Database
        2 - type """
        if (self.__class__ != other.__class__):
            raise TypeError

        if (self.database == other.database):
            return self.get_order().__cmp__(other.get_order())
        else:
            return self.database.__cmp__(other.database)

    def __eq__(self, other):
        if other == None or other.__class__ != File:
            return False

        equals = self.name == other.name \
                 and self.database == other.database \
                 and self.type == other.type
        return equals

    def getInitScript(self):
        value = ''
        return value

    def getScript(self):
        path = self._path.replace(self._basepath, '', 1)
        value = []
        value.append('PROMPT Executando script ' + self.name)
        value.append('@' + path)
        if (self._type in self.CATEGORIES['COMPILABLE']):
            value.append('SHOW ERRORS')
        return value

    def getFinalScript(self):
        value = []
        if (self._type in self.CATEGORIES['COMMITABLE']):
            value.append('PROMPT *************************************')
            value.append('PROMPT ** Fazer commit se tudo correr bem **')
            value.append('PROMPT *************************************')
        return value

    def remove(self):
        if self.path and self.path.exists():
            self.path.remove()

class InstallScript(object):
    """ Represents a install script used to invoke package's sql files."""

    """Script name"""
    name = None
    """Short description of the script"""
    description = None
    """Content of script ([File, ..])"""
    content = None
    """Full path of script"""
    path = None

    def __init__(self, name=None, content=None, desc=None):
        """ Initialize the install script
            @param name name of file to be created in the filesystem
            @param content list of files (File objects) to be invoked
            @param desc description of install script.
        """
        self.name = name
        self.content = content or []
        self.description = desc
        self.path = None

    def add_file(self, file):
        self._content.append(file)

    def __eq__(self, other):
        if not hasattr(other, 'name'):
            return False

        return self.name == other.name

    def __str__(self):
        return "<InstallScript name='%s' content=%s/>" % (self.name, str(self.content))

    __repr__ = __str__

    def remove(self):
        """ Remove script from filesystem if it was already written.
        """
        if self.path:
            self.path.remove()
 
    def create(self, base_path):
        """ Generate script data and write Install Script to filesystem.
            @param base_path Directory where the file will be created.
        """
        assert self.name, "InstallScript must have a name"

        init_script_data = []
        script_data = []
        script_content = []
        final_script_data = []

        logfile_name = self.name.replace('.sql', '')
        logfile_name += '.log'

        for file in self.content:
            init_script_data += file.getInitScript()
            script_data += file.getScript()
            final_script_data += file.getFinalScript()

        script_content.append('SPOOL %s' % logfile_name)
        script_content += init_script_data
        script_content += script_data
        script_content += final_script_data
        script_content.append('SPOOL OFF')

        self._write_script(base_path, script_content)

    def _write_script(self, base_path, data):
        """ Writes script data to filesystem.
        """
        log.debug("Writing file '%s'" % self.name)
        self.base_path = base_path.abspath()
        script_file = self.base_path/self.name

        try:
            if script_file.exists():
                log.debug("File with same name exists, moving it")
                script_file.move(script_file + '.bak')

            script_file.touch()
            self.path = script_file
            self.path.write_lines(data, encoding=ENCODING)
        except Exception:
            log.error("Error writing script (%s)" % script_file, exc_info=1)
            raise

