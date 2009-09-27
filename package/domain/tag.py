#!/usr/bin/python2.5
# encoding: utf-8
# Version: $Id$

class Tag(object):
    _name = None

    def __init__(self, name=None):
        """ Initializes the Tag instance.
            @param name if given, initializes the name attribute."""
        self.name = name

    def __eq__(self, other):
        if type(other) == str:
            return self.name == other
        return self.__class__ == other.__class__\
               and self.name == other.name

    def __str__(self):
        return self.name

    __repr__ = __str__

    def get_name(self):
        return self._name

    def set_name(self, name):
        if (name):
            self._name = name.strip()

    name = property(get_name, set_name, doc="Tag name")

