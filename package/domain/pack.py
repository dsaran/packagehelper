#!/usr/bin/python2.5
# encoding: utf-8
# Version: $Id: pack.py,v 1.2 2009-03-21 20:57:45 daniel Exp $

from os import sep
from typecheck import *
from package.domain.tag import Tag
from package.domain.file import File
from package.domain.repository import Repository
from package.domain.defect import Defect
from path import path as Path

class Package(object):
    _files = None
    _scripts = None
    _name = None 
    _tags = None
    _repositories = None
    _path = None
    _defects = None
    _requirements = None
    _checkout = None
    _process = None

    def __init__(self, name=""):
        """ Initializes the package object.
            @param name if given, sets initializes the package name."""
        self._name = name
        self._files = []
        self._scripts = []
        self._tags = []
        self._repositories = []
        self._defects = []
        self._requirements = []
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
            if self._path._get_namebase() == self._name:
                return self._path.dirname()
        return self._path

    def get_full_path(self):
        """ Returns the packages's path, including itself """
        if not self._path or self._path._get_namebase() == self._name:
            return self._path
        return self._path.joinpath(self._name)

    @takes("Package", list)
    def set_files(self, files):
        self._files = files

    def get_files(self):
        return self._files

    @takes("Package", File)
    def add_file(self, file):
        self._files.append(file)

    def setscripts(self, scripts):
        self._scripts = scripts

    def getscripts(self):
        return self._scripts

    def set_name(self, name):
        self._name = name.strip()

    def get_name(self):
        return self._name

    @takes("Package", list)
    def set_tags(self, tags):
        for tag in tags:
            self.add_tag(tag)

    def get_tags(self):
        return self._tags

    @takes("Package", Tag)    
    def add_tag(self, tag):
        self._tags.append(tag)

    def remove_tag(self, tag):
        self._tags.remove(tag)

    @takes("Package", list)
    def set_repositories(self, repositories):
        for repo in repositories:
            self.add_repository(repo)

    #@deprecated
    def get_repositories(self):
        return self._repositories

    @takes("Package", Repository)
    def add_repository(self, repository):
        self._repositories.append(repository)

    @takes("Package", Repository)
    def remove_repository(self, repository):
        self._repositories.remove(repository)

    @takes("Package", Defect)
    def add_defect(self, defect):
        self._defects.append(defect)

    @takes ("Package", Defect)
    def remove_defect(self, defect):
        self._defects.remove(defect)

    def get_defects(self):
        return self._defects

    def setdefects(self, defects):
        self._defects = defects

    def getrequirements(self):
        return self._requirements

    def setrequirements(self, requirements):
        self._requirements = requirements

    def getcheckout(self):
        return self._checkout

    def setcheckout(self, checkout):
        self._checkout = checkout

    def getprocess(self):
        return self._process

    def setprocess(self, process):
        self._process = process

    scripts = property(getscripts, setscripts, doc="Generated scripts")
    name = property(get_name, set_name, doc="Package name")
    path = property(getpath, setpath, doc="Package path")
    repositories = property(get_repositories, set_repositories, doc="Repository list")
    tags = property(get_tags, set_tags, doc="Tag list")
    defects = property(get_defects, setdefects, doc="Package Defects")
    requirements = property(getrequirements, setrequirements, doc="Package requirements")
    checkout = property(getcheckout, setcheckout, doc="Package files should checked out")
    process = property(getprocess, setprocess, doc="Package files should be processed")

    def getFilesByAttribute(self, attribute, value):
        list = []
        for file in self._files:
            if file.__getattribute__(attribute) == value:
                list.append(file)
        return list

    def getGroupedFiles(self):
        databases = {}
        for file in self._files:
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
        for file in self._files:
            if file.database == database and file.get_category() == category:
                list.append(file)
        return list



