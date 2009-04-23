# Version: $Id$

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

class GlobalLogger:
    pass

def urljoin(*args):
    """ Join *args as a url using forward slashes.
        Usage:
        >>> urljoin('http://host/path', 'otherfolder', '/more/folders')
        'http://host/path/otherfolder/more/folders'
    """
    paths = []
    url = ''
    for arg in args:
        clean_arg = arg
        if arg.startswith('/'):
            clean_arg = clean_arg[1:]
        if arg.endswith('/'):
            clean_arg = clean_arg[:-1]
        if clean_arg:
            paths.append(clean_arg)

    url = '/'.join(paths)
    return url

def url_split(url):
    """ Splits a URL into two strings containing the base url and parent directory.
        Example:
        >>>url_split('http://host/path/otherfolder/some/folder')
        ('http://host/path/otherfolder/some', 'folder')"""
    url = url_normalize(url)
    if not url:
        raise ValueError("Invalid URL: %s" %url)

    protocol, rest = url.split('://')

    split = rest.split('/')

    host = split[0]
    if len(split) == 1:
        last = '/'
        base = url
    else:
        last = split[-1]
        base = url_normalize(url.rstrip(last))
    
    return base, last

def url_normalize(url):
    """ Removes trailing '/' from url"""
    if not url:
        return ""

    return url.rstrip('/')

