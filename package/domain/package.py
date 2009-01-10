#!/usr/bin/python2.5
# encoding: utf-8
# Version: $Id: package.py,v 1.2 2009-01-10 04:04:14 daniel Exp $

from os import sep
from typecheck import *
from tag import Tag
from file import File
from repository import Repository
from defect import Defect
from path import path as Path

class Package:
    _files = None
    _name = None 
    _tags = None
    _repositories = None
    _path = None
    _defects = None

    def __init__(self, name=""):
        """ Initializes the package object.
            @param name if given, sets initializes the package name."""
        self._name = name
        self._files = []
        self._tags = []
        self._repositories = []
        self._defects = []

    def set_path(self, path):
        if type(path) == str:
            self._path = Path(path.strip())
        else:
            self._path = path

    def get_path(self):
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

    def set_name(self, name):
        self._name = name.strip()

    def get_name(self):
        return self._name

    @takes("Package", list)
    def set_tags(self, tags):
        for tag in tags:
            self.addTag(tag)

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
            db = file.get_database()
            if not databases.has_key(db):
                databases[db] = {}

            if not databases[db].has_key(cat):
                databases[db][cat] = []

            databases[db][cat].append(file)
        return databases

    def getFilesByDbAndCategory(self, database, category):
        list = []
        for file in self._files:
            if file.get_database() == database and file.get_category() == category:
                list.append(file)
        return list



