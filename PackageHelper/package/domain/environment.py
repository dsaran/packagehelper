# $Id: environment.py,v 1.1.1.1 2009-01-07 22:58:30 daniel Exp $
# encoding: utf-8

from database import Database

class Environment:

    bd_alias = None
    user_alias = None
    conn_string = None
    active = None

    def __init__(self, bd_alias, user_alias, conn_string, active=True):
        self.bd_alias = bd_alias
        self.user_alias = user_alias
        self.conn_string = conn_string
        self.active = active

    def __eq__(self, other):
        if isinstance(other, Database):
            return self.get_database() == other

        if self.__class__ != other.__class__:
            return False;

        return self.get_database() == other.get_database()

    def __hash__(self):
        return hash(self.get_database())

    def get_database(self):
        return Database(self.bd_alias, self.user_alias)

    def get_conn_string(self):
        return self.conn_string

    def is_active(self):
        return self.active

    def __str__(self):
        return "<%s@%s-%s>" % (self.user_alias, self.bd_alias, self.active)

    __repr__ = __str__
