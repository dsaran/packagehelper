#!/usr/bin/python2.5
# encoding: utf-8
# Version: $Id$

class Tag(object):
    name = None

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

