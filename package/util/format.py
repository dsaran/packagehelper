# Version: $Id: format.py,v 1.1.1.1 2009-01-07 22:58:30 daniel Exp $

from sys import platform

ENCODING='iso-8859-1'

def list2str(list, sep='\n'):
    if not list:
        return ''
    str_list = [str(item) for item in list]
    return sep.join(str_list)

def uri2path(uri):
    path = uri
    if platform == 'win32':
        path = path.replace('file:///', '')
        path = path.replace('/', '\\')
    else:
        path = path.replace('file://', '')

    path.replace('%20', ' ')
    return path
