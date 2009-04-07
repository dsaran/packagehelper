# encoding: utf-8
# Version: $Id: repository.py,v 1.2 2009-01-10 04:04:14 daniel Exp $

from package.scm import ScmError, CvsProcessor, SubversionProcessor
from kiwi.python import enum

class ScmType(enum):
    CVS = 1
    SVN = 2 #(CvsProcessor, SubversionProcessor)

ScmProcessor = {
    ScmType.CVS: CvsProcessor,
    ScmType.SVN: SubversionProcessor
}

class Repository:
    root = None
    module = None
    active = None
    _type = None

    def __init__(self, root, module, type=ScmType.CVS, active=True):
        """ Initializes the Repository instance.
            @param root the CVSROOT.
            @param module repository's module.
            @param type The SCM Type of repository.
            @param active if the repository is active (default True)"""
        self.root = root
        self.module = module
        self.active = active
        self._type = type
        self.scm_processor = None

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

    def getprocessor(self):
        if self.scm_processor:
            return self.scm_processor

        processor = ScmProcessor.get(self.type, None)

        if not processor:
            raise Exception("Unknown SCM type.")

        self.scm_processor = processor(root=self.root, module=self.module)
        return self.scm_processor
 
    def gettype(self):
        return self._type

    def settype(self, type):
        self._type = type
        if self.scm_processor:
            self.scm_processor = None

    processor = property(getprocessor, doc="SCM Processor")
    type = property(gettype, settype, doc="SCM Type")

    def __eq__(self, other):
        if type(other) == str:
            return self.root == other
        return self.__class__ == other.__class__ and self.root == other.root

    def __str__(self):
        if self.root and self.module:
            active = 'active' if self.active else 'inactive'
            return "<%s at %s (%s)/>" % (self.module, self.root, active)
        return ""

    __repr__ = __str__


