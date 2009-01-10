#!/usr/bin/python2.5
# encoding: utf-8
# Version: $Id: repository.py,v 1.2 2009-01-10 04:04:14 daniel Exp $


class Repository:
    root = None
    module = None
    active = None

    def __init__(self, root, module, active=True):
        """ Initializes the Repository instance.
            @param root the CVSROOT.
            @param module repository's module.
            @param active if the repository is active (default True)"""
        self.root = root
        self.module = module
        self.active = active

    def set_root(self, root):
        self.root = root

    def get_root(self):
        return self.root

    def set_module(self, module):
        self.module = module

    def get_module(self):
        return self.module

    def is_active(self):
        return self.active    

    def set_active(self, active):
        self.active = active

    def get_active(self):
        return self.active

    def __eq__(self, other):
        if type(other) == str:
            return self.root == other
        return self.__class__ == other.__class__ and self.root == other.root

    def __str__(self):
        if self.root and self.module:
            return "<" + self.module + ' at ' + self.root + ">"
        return ""

    def __repr__(self):
        if self.root and self.module:
            return "<" + self.module + ' at ' + self.root + ">"
        return ""


