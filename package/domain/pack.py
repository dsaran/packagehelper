#!/usr/bin/python2.5
# encoding: utf-8
# Version: $Id$

from os import sep
from typecheck import *
from package.domain.tag import Tag
from package.domain.file import File
from package.domain.repository import Repository
from package.domain.defect import Defect
from path import path as Path

class Package(object):
    files = None
    scripts = None
    name = None 
    tags = None
    repositories = None
    _path = None
    defects = None
    requirements = None
    checkout = None
    process = None
    has_sql = False
    has_xml = False
    has_shellscript = False

    def __init__(self, name=""):
        """ Initializes the package object.
            @param name if given, sets initializes the package name."""
        self.name = name
        self.files = []
        self.scripts = []
        self.tags = []
        self.repositories = []
        self.defects = []
        self.requirements = []
        self._path = None

    def setpath(self, path):
        if type(path) == str:
            self._path = Path(path.strip())
        elif type(path) == Path:
            self._path = path
        else:
            raise ValueError('Type %s not accepted for path property.' % str(type(path)))

    def getpath(self):
        """ Returns the package's base path excluding the package path. """
        if self._path:
            if self._path._get_namebase() == self.name:
                return self._path.dirname()
        return self._path

    def get_full_path(self):
        """ Returns the packages's path, including itself """
        if not self._path or self._path._get_namebase() == self.name:
            return self._path
        return self._path.joinpath(self.name)

    @takes("Package", File)
    def add_file(self, file):
        self.files.append(file)

    @takes("Package", Tag)    
    def add_tag(self, tag):
        self.tags.append(tag)

    def remove_tag(self, tag):
        self.tags.remove(tag)

    @takes("Package", Repository)
    def add_repository(self, repository):
        self.repositories.append(repository)

    @takes("Package", Repository)
    def remove_repository(self, repository):
        self.repositories.remove(repository)

    @takes("Package", Defect)
    def add_defect(self, defect):
        self.defects.append(defect)

    @takes ("Package", Defect)
    def remove_defect(self, defect):
        self.defects.remove(defect)

    path = property(getpath, setpath, doc="Package parent path")
    full_path = property(get_full_path, doc="Package path")

    def getFilesByAttribute(self, attribute, value):
        list = []
        for file in self.files:
            if file.__getattribute__(attribute) == value:
                list.append(file)
        return list

    def getGroupedFiles(self):
        databases = {}
        for file in self.files:
            cat = file.get_category()
            db = file.database
            if not databases.has_key(db):
                databases[db] = {}

            if not databases[db].has_key(cat):
                databases[db][cat] = []

            databases[db][cat].append(file)
        return databases

    def getFilesByDbAndCategory(self, database, category):
        list = []
        for file in self.files:
            if file.database == database and file.get_category() == category:
                list.append(file)
        return list

