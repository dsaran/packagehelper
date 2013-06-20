#! /usr/bin/env python2.5
# Version: $Id$

class Defect:

    id_local = None
    id_client = None
    description = None

    def __init__(self, id_local=None, id_client=None, description=None):
        self.id_local = id_local
        self.id_client = id_client
        self.description = description


    def set_id_local(self, value):
        self.id_local = value

    def set_id_client(self, value):
        self.id_client = value

    def set_description(self, value):
        self.description = value

    def get_id_local(self):
        return self.id_local

    def get_id_client(self):
        return self.id_client

    def get_description(self):
        return self.description


    def __repr__(self):
        return "<%s - %s - %s>" % (self.id_local, self.id_client, self.description)

    __str__ = __repr__

class Requirement:

    """Requirement ID"""
    id = None
    """Requirement Description"""
    description = None

    def __init__(self, id=None, desc=None):
        self.id = id
        self.description = desc

    def __repr__(self):
        return "<Req %s - %s>" % (self.id, self.description)

    __str__ = __repr__


