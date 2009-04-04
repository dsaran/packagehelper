import os
from path import path as Path

if (os.environ.has_key('PKG_BASEDIR')):
    WORKING_DIR = Path(os.environ['PKG_BASEDIR'])
else:
    WORKING_DIR = Path('.')

