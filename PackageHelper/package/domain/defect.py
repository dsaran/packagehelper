#! /usr/bin/env python2.5
# Version: $Id: defect.py,v 1.1.1.1 2009-01-07 22:58:30 daniel Exp $

class Defect:

    id_ptin = None
    id_vivo = None
    description = None

    def __init__(self, id_ptin=None, id_vivo=None, description=None):
        self.id_ptin = id_ptin
        self.id_vivo = id_vivo
        self.description = description


    def set_id_ptin(self, value):
        self.id_ptin = value

    def set_id_vivo(self, value):
        self.id_vivo = value

    def set_description(self, value):
        self.description = value

    def get_id_ptin(self):
        return self.id_ptin

    def get_id_vivo(self):
        return self.id_vivo

    def get_description(self):
        return self.description


    def __repr__(self):
        return "<%s - %s - %s>" % (self.id_ptin, self.id_vivo, self.description)

    __str__ = __repr__
