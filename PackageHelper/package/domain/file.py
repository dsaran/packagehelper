#!/usr/bin/python2.5
# encoding: utf-8
# Version: $Id: file.py,v 1.1.1.1 2009-01-07 22:58:30 daniel Exp $

from os import sep
from path import path as Path
from database import Database
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

    def __init__(self, path, basepath, parse=True):
        """ Constructor.
        @param path 'path' instance or a string representing the file"
        @param basepath 'path' instance or a string representing the base path of file"
        @param parse (optional) if the filename must be parsed."""

        self._basepath = basepath
        if not self._basepath.endswith(sep):
            self._basepath += sep

        self._path = path

        fileDetails = path.splitall()
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

    def get_name(self):
        return self._name

    def get_database(self):
        return self._database

    def get_type(self):
        return self._type

    def get_path(self):
        return self._path #self._basepath + self._path

    def get_basepath(self):
        return self._basepath

    def set_name(self, name):
        self._name = name

    def set_database(self, database):
        self._database = database

    def set_type(self, type):
        self._type = type

    def set_path(self, path):
        self._path = path

    def __repr__(self):
        return str(self._path)

    __str__ = __repr__

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

        if (self.get_database() == other.get_database()):
            return self.get_order().__cmp__(other.get_order())
        else:
            return self.get_database().__cmp__(other.get_database())

    def getInitScript(self):
        value = ''
        return value

    def getScript(self):
        path = self._path.replace(self._basepath, '', 1)
        value = []
        value.append('PROMPT Executando script ' + self.get_name())
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

