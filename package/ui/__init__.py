from kiwi.environ import Library
lib = Library('package')
if lib.uninstalled:
    lib.add_global_resource('glade', 'glade')

