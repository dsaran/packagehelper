#!/usr/bin/python2.5
# encoding: utf-8
# Version: $Id: database.py,v 1.2 2009-01-22 04:10:42 daniel Exp $

import logging

log = logging.getLogger('Database')

class Database(object):
    USER_ORDER = {'CLI':2, 'ADM':1}
    DB_ORDER = {'BD1':1, 'BD2':2, 'SMP':3}

    _name = None
    _user = None
    def __init__(self, name, user):
        self._name = name
        self._user = user

    def getName(self):
        return self._name

    def getUser(self):
        return self._user

    def setName(self, name):
        self._name = name

    def setUser(self, user):
        self._user = user

    def getKey(self):
        return str(self._user) + '_' + str(self._name)

    def __eq__(self, obj):
        if (type(obj) != Database):
            log.warn("Comparing object from different types. Other is %s" % str(obj.__class__))
            return False
        return self.getKey() == obj.getKey()

    def getOrder(self):
        prefix = self.getUser()[:3]

        if (self.USER_ORDER.has_key(prefix)):
            return self.USER_ORDER[prefix]

        return max(self.USER_ORDER.values()) + 1

    def __hash__(self):
        return hash(self.getKey())

    def __cmp__(self, other):
        if (self.__class__ != other.__class__):
            raise TypeError

        if (self.getKey() == other.getKey()):
            return 0

        maxOrder = max(self.USER_ORDER.values()) + 1

        selfOrder = self.getOrder()
        otherOrder = other.getOrder()

        return selfOrder.__cmp__(otherOrder)

    def __str__(self):
        return "<" + self._user + "@" + self._name + ">"

