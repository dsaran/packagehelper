#!/usr/bin/python2.5

import logging
from os import path
from sys import argv, path as pythonpath

log = logging.getLogger('DomainTest')

currentdir = path.dirname(path.abspath(argv[0]))
basedir = path.abspath('../../../')
libdir = path.join(basedir, 'lib')
guidir = path.join(basedir, 'package')
resdir = path.join(basedir, 'resources')

pythonpath.insert(0, libdir)
pythonpath.insert(1, guidir)
pythonpath.insert(2, resdir)


# Checking parameters
print "Testing domain objects"
from domain.file import File
from path import path as Path

print "=========================== Testing File =============================="
filename = '/home/daniel/pacote/tag/bd4/admin/act_BD/runscript.sql'
filepath = '/home/daniel/pacote/'
f = File(Path(filename), filepath)

print "Testing get_name                => ",
assert f.get_name() == 'runscript.sql'
print "OK"

print "Testing getType                 => ",
assert f.get_type() == 'ACT_BD'
print "OK"

print "Testing getCategory             => ",
assert f.get_category() == 'COMMITABLE'
print 'OK'

print "Testing __str__                 => ",
print str(f)
#assert str(f) == 'runscript.sql'#filename
print 'OK'

filename2 = '/home/daniel/pacote/tag/bd4/admin/ddl/createTable.sql'
filepath2 = '/home/daniel/pacote/'
f2 = File(Path(filename2), filepath2)
print "Testing __cmp__                 => ",
assert f2 < f
print 'OK'

filename3 = '/home/daniel/pacote/tag/bd4/admin/blah/createTable.sql'
filepath3 = '/home/daniel/pacote/'
f3 = File(Path(filename3), filepath3)
print "Testing __cmp__ (unknown type)  => ",
assert f3 > f
print 'OK'

path = '/home/daniel/pacote'
filename1 = '/tag/bd4/admin/ACT_BD/script.sql'
filename2 = '/tag/bd4/admin/DML/del.sql'
f1 = File(Path(filename1), path)
f2 = File(Path(filename2), path)
print "Testing __cmp__ (DML vs ACT_BD) => ",
assert f2 < f1
print 'OK'


print "Testing file ordering           => ",
file1 = File(Path(path + '/tag/bd4/admin/TAB/script.sql'), path)
file2 = File(Path(path + '/tag/bd4/admin/DDL/script.sql'), path)
file3 = File(Path(path + '/tag/bd4/admin/TRG/script.sql'), path)
file4 = File(Path(path + '/tag/bd4/admin/IDX/script.sql'), path)
file5 = File(Path(path + '/tag/bd4/admin/DML/script.sql'), path)
file6 = File(Path(path + '/tag/bd4/admin/ACT_BD/script.sql'), path)
file7 = File(Path(path + '/tag/bd4/admin/PKH/script.sql'), path)
file8 = File(Path(path + '/tag/bd4/admin/PKB/script.sql'), path)

unorderedList = [file2, file3, file1, file8, file4, file6, file5, file7]
unorderedList.sort()
assert unorderedList == [file1, file2, file3, file4, file5, file6, file7, file8]
print "OK"

from domain.database import Database
print "=========================== Testing Database =============================="
db1 = Database('BD1', 'ADMINPROV2_10')
db2 = Database('BD1', 'CLIPROV2_10')

print "Testing __cmp__                 => ",
assert db1 < db2
print "OK"

db1 = Database('BD1', 'SUPPORT')
print "Testing __cmp__ (unknown user)  => ",
assert db1 > db2
print "OK"

db2 = Database('BD1', 'UNKNOWN')
print "Testing __cmp__ (2 unknown user)=> ",
assert not db1 < db2 and not db1 > db2
print "OK"

db1 = Database('BD1', 'ADMINPROV2_10')
db2 = Database('BD1', 'CLIPROV2_10')
print "Testing __eq__ ('!=')           => ",
assert db1 != db2
print "OK"

db1 = Database('BD1', 'CLIPROV2_10')
db2 = Database('BD1', 'CLIPROV2_10')
print "Testing __eq__ ('==')           => ",
assert db1 == db2
print "OK"

from domain.environment import Environment
print "=========================== Testing Database =============================="
db1 = Database('BD1', 'ADMINPROV2_10')
env = Environment('BD1', 'ADMINPROV2_10', '')
print "Testing __eq__ ('==')         => ",
assert env.__eq__(db1)
print "OK"

env_list = [env]
print "Testing list.index()          => ",
assert env_list.index(db1) == 0
print "OK"

