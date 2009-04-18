#! /usr/bin/env python2.5
# Version $Id$

import logging
from sys import exit
from package.domain.repository import Repository
from package.domain.tag import Tag
from package.domain.pack import Package
from package.processor import PackageProcessor
from package.util.format import list2str
from package.util.commandline import clearscreen, read, read_int, pause

log = logging.getLogger('PackageProcessorUI')

class PackageProcessorUI:
    tags = []
    repositories = []
    package = None
    directory = None

    def __init__(self):
        self.OPTIONS = """Checkout options
                            1 - Add repositories
                            2 - Remove Repository
                            3 - Add Tag
                            4 - Remove Tag
                            5 - Checkout files
                            6 - Process checked out files
                            7 - Checkout and process
                            8 - Quit"""

        self.ACTIONS = {'1': self.add_repository,\
                                 '2': self.remove_repository,\
                                 '3': self.add_tag,\
                                 '4': self.remove_tag,\
                                 '5': self.checkout,\
                                 '6': self.process,\
                                 '7': self.run_all,\
                                 '8': self.quit}

        # Start UI
        self.start()

    def start(self):
        clearscreen()
        print "Welcome to the package processor command line UI"
        self.package = read("Package name")
        self.directory = read("Base directory to create the package")
        while True:
            try:
                self.main_menu()
            except Exception, e:
                clearscreen()
                print "Error: ", e
                read("Press Enter to return.")

    def top(self):
        top = "Package: " + self.package
        top += "\nDirectory: " + self.directory
        top += "\nRepositories: " + str(self.repositories)
        top += "\nTags: " + str(self.tags)
        top += "\n========================================================="
        return top

    def main_menu(self):
        option = None
        while option not in self.ACTIONS.keys():
            clearscreen()
            print self.top()
            print self.OPTIONS
            option = read("Option")

        return self.ACTIONS[option]()

    def add_repository(self):
        clearscreen()
        print "Adding repository"
        repo = read("CVSROOT")
        module = read("Module")
        self.repositories.append(Repository(repo, module))

    def remove_repository(self):
        self.remove(self.repositories)

    def add_tag(self):
        clearscreen()
        print "Adding tag"
        tag = read("TAG")
        self.tags.append(Tag(tag))

    def remove_tag(self):
        self.remove(self.tags)

    def remove(self, list):
        option = -1 
        indexes = range(len(list))
        # Add the 'back' option
        back_option = len(indexes)

        while option not in indexes + [back_option]:
            clearscreen()
            print "Which one do you want to remove?"
            for i in indexes:
                print i, ' - ', list[i]
            print back_option, ' - Back to previous menu'
            option = read_int("option")

        if option == back_option:
            return
        list.pop(option)

    def _get_processor(self):
        package = Package(self.package)
        package.set_tags(self.tags)
        package.set_repositories(self.repositories)
        package.path = self.directory
        processor = PackageProcessor(package)

        return processor 

    def checkout(self):
        processor = self._get_processor()
        try:
            errors = processor.checkout_files()
        except:
            print "Error checking out files."
        self._show_errors(errors)

    def process(self):
        processor = self._get_processor()
        scripts = processor.process_files()
        self._show_scripts(scripts)

    def run_all(self):
        processor = self._get_processor()
        scripts, errors = processor.run()
        self._show_errors(errors)
        self._show_scripts(scripts)

    def _show_errors(self, errors):
        clearscreen()
        if errors:
            print "Errors found:"
            print list2str(errors)
        else:
            print "No errors found!"
        pause()

    def _show_scripts(self, results):
        if len(results):
            print "Generated scripts:"
            print list2str(results)
        else:
            print "No scripts were generated"
        pause()

    def quit(self):
        confirm = None
        yes_values = ['y', 'Y']
        no_values = ['n', 'N']
        while confirm not in no_values: 
            clearscreen()      
            confirm = read("Do you really want to leave? (Y/N)")
            if confirm in yes_values: 
                print "Good bye!"
                exit(0)
        return

