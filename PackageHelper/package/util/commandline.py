# Version: $Id: commandline.py,v 1.1.1.1 2009-01-07 22:58:30 daniel Exp $

def clearscreen():
    from sys import platform
    from os import system
    if platform == 'win32':
        cmd = 'cls'
    else:
        cmd = 'clear'
    system(cmd)

def read(label):
    print label + ": ",
    return raw_input().strip()

def read_int(label):
    value = read(label)
    try:
        return int(value)
    except ValueError:
        return -99

def pause():
    read("Press enter to continue...")
