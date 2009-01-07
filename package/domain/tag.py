#!/usr/bin/python2.5
# encoding: utf-8
# Version: $Id: tag.py,v 1.1.1.1 2009-01-07 22:58:30 daniel Exp $

class Tag(object):
    name = None

    def __init__(self, name=None):
        self.name = name

    def setname(self, name):
        self.name = name

    def setName(self, name):
        self._name = name

    def set_name(self, name):
        self.name = name

    def get_name(self):
        return self.name
    
    def __eq__(self, other):
        if type(other) == str:
            return self.name == other
        return self.__class__ == other.__class__\
               and self.name == other.name

    def __str__(self):
        return self.name

    def __repr__(self):
        return self.name

