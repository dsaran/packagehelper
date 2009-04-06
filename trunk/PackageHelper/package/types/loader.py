import xml.dom.minidom
import logging
from xml.dom.minidom import Node
from package.types.sqltypes import SqlType

log = logging.getLogger('Loader')

class Loader:
    def __init__(self, file=None, text=None):
        if file:
            self._doc = xml.dom.minidom.parse(file)
        elif text:
            self._doc = xml.dom.minidom.parseString(text)
        else:
            raise Exception("Missing invalid argument")

    def loadTypes(self):
        typeElements = self._get_type_elements()
        types = []
        for t in typeElements:
            sqltype = SqlType()
            sqltype.set_name(t.getAttribute("name"))
            sqltype.set_order(t.getAttribute("order"))

            c = t.getElementsByTagName('category')[0]
            sqltype.set_category(c.getAttribute("name"))

            matcher = self._get_matcher(t)
            if matcher:
                sqltype.set_matcher(matcher)

            parser = self._get_parser(t)
            if parser:
                sqltype.set_parser(parser)

            types.append(sqltype)
        return types

    def _get_type_elements(self):
        return self._doc.getElementsByTagName('type')

    def _get_matcher(self, type):
        m = type.getElementsByTagName('matcher')
        if m and len(m) == 1:
            m = m[0]
            matcherClass = m.getAttribute("class")
            args = {}
            for arg in m.getElementsByTagName('constructor-arg'):
                argName = str(arg.getAttribute("name"))
                argValue = str(arg.childNodes[0].data)
                args[argName] = argValue
            matcher = _get_class_instance(matcherClass, args)
            return matcher
 
    def _get_parser(self, type):
        p = type.getElementsByTagName('parser')
        if p and len(p) == 1:
            p = p[0]
            parserClass = m.getAttribute("class")
            args = {}
            for arg in m.getElementsByTagName('constructor-arg'):
                argName = str(arg.getAttribute("name"))
                argValue = str(arg.childNodes[0].data)
                args[argName] = argValue
            parser = _get_class_instance(parserClass, args)
            return matcher


def _get_class_instance(klassName, kwargs):
    log.debug("Getting instance of class %s with arguments: " % klassName + str(kwargs))

    packageSeparator = '.'
    modules = klassName.split(packageSeparator)
    klass = modules[-1] 
    module = packageSeparator.join(modules[:-1]) 
    mod = __import__(module, fromlist=[klass])
    cls = mod.__getattribute__(klass)

    return cls(**kwargs)

