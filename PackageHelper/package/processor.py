#! /usr/bin/env python2.5
# Version: $Id: processor.py,v 1.2 2009-01-10 04:04:14 daniel Exp $

import logging
from os import environ, popen, chdir
from path import path as Path
from typecheck import takes
from package.domain.repository import Repository
from package.domain.tag import Tag
from package.domain.package import Package
from package.domain.database import Database
from package.domain.file import File
from package.util.format import ENCODING
#from package.config import Config 
from package.cvs import CvsError, CVS

log = logging.getLogger('PackageProcessor')

class PackageProcessor:
    """ This class provides methods for package generation,
        including cvs checkout and SQL scripts creation. """

    package = None

    def __init__(self):
        self.tags = []
        self.repositories = []

    @takes("PackageProcessor", Package)
    def __init__(self, package):
        self.package = package

    def getFiles(self, filter):
        """ Search for "*.sql" files below the directory tree.
        @param directory the base directory path to search for files.
        @return a list of File instances. """
        log.debug("Searching files in directory %s..."\
                  % str(self.package.get_full_path()))
        try:
            path = self.package.get_full_path()
            generator = path.walk(filter, case_sensitive=False)
            files = []
            for item in generator:
                try:
                    file = File(item, path)
                    files.append(file)
                except ValueError:
                    # Ignoring unknown file paths
                    log.warn("Ignoring file: ", item)
                    pass
        except Exception:
            log.error("Error searching files.", exc_info=1)
            raise

        log.debug("done.")
        return files

    def _generateScript(self, id, db, list):
        """ Create the SQL script for a list of files.
            @param id the sequencial number of the file to be created.
            @param db Database for which the script will be created.
            @param list a list of File object to be added to the SQL script."""
        log.debug("Generating script %d_%s_%s..." % (id, db.getUser(), db.getName())) 
        list.sort()
        scriptName = str(id).zfill(3) + '_' + db.getUser() + '_' + db.getName()
        script_data = []
        script_data.append('SPOOL ' + scriptName + '.log')
        script_data += list[0].getInitScript()
        type = list[0].get_type()


        for file in list:
            value = file.getScript()
            script_data += value

        script_data += list[0].getFinalScript()
        script_data.append('SPOOL OFF')
        path = self.package.get_full_path()
        script_file = path.joinpath(path, scriptName + '.sql')
        try:
            script_file.touch()
            script_file.write_lines(script_data, encoding=ENCODING)
        except Exception:
            log.error("Error writing script ("+ scriptName +" )", exc_info=1)
            raise
        log.debug("done.")

        script = File(script_file, path, False)
        script.set_database(db)
        script.set_type(type)
        return script

    def run(self):
        """ Start the process of package generation.
        Checkout files and create scripts.
            @return a list of scripts and a list of errors."""
        log.debug("Calling checkout process...")
        errors = self.checkout_files()
        
        if errors:
            log.error(errors)

        log.debug("Calling file process...")

        scripts = self.process_files()

        log.debug("done.")
        return scripts, errors

    def process_files(self):
        """ Process previous checked out files generating the SQL scripts.
            @return a list with the generated SQL scripts."""
        log.info("Processing files...")
        categories = {}
        self.package.set_files([])
        files = self.getFiles("*.sql")
        for file in files:
            categories[file.get_category()] = ''
            self.package.add_file(file)

        scriptId = 0
        groupedList = self.package.getGroupedFiles()
        dbKeys = groupedList.keys()
        dbKeys.sort()
        scripts = []
        for db in dbKeys:
            for cat in groupedList[db]:
                scriptId += 1
                files = groupedList[db][cat]
                script = self._generateScript(scriptId, db, files)
                scripts.append(script)
        log.info("Processing files done.")

        otherfiles = self.process_other()
        return scripts

    def checkout_files(self):
        """ Check out files from cvs using the given tags and repositories.
            @param tags is a list of Tag objects
            @param repositories is a list of Repository objects
            @return a list with errors occurred, if any."""
        log.info("Checking out files...")
        status = []
        tags = self.package.get_tags()
        repositories = self.package.get_repositories()
        if not tags or not repositories:
            status.append("No repository/tag to checkout.")
            log.info(status)
            return status

        dest = self.package.get_full_path()
        #if not p.exists():
        #    try:
        #        log.info("Creating directory: " + str(p))
        #        p.mkdir()
        #    except OSError:
        #        log.error("Error creating directory.", exc_info=1)
        #        raise 
        ## This is necessary because cvs does not accept absolute directories
        ## with -d option.
        #chdir(p)
        #config = Config(load=True)
        #cvs = config.get_cvs()
        #log.debug("cvs path: " + cvs)
        for repo in repositories:
            if repo.is_active():
                #environ["CVSROOT"] = repo.root
                #errorfile = popen(cvs + " login")
                #error = errorfile.read()
                #errorfile.close()
                #if error:
                #    log.info(error)
                #    status.append(error)

                cvs = CVS(repo.root, repo.module)

                for tag in tags:
                    #command = cvs + " -q -z 9  export -d %s -r %s %s" %\
                    #        (tag.name,\
                    #        tag.name,\
                    #        repo.module)
                    #log.debug("Executing command: " + command)
                    #errorfile = popen(command)
                    #error = errorfile.read()
                    #errorfile.close()

                    try:
                        cvs.export(dest, tag) 
                    except CvsError, e:
                        status.append(e.message)

                    #command = cvs + " -q -z 9 rtag -F -r %s %s %s" %\
                    #        (tag.name,\
                    #        self.package.get_name(),\
                    #        repo.module)
                    #log.debug("Executing command: " + command)
                    #errorfile = popen(command)
                    #error = errorfile.read()
                    #errorfile.close()
 
                    #if error:
                    #    log.info(error)
                    #    status.append(error)
                    try:
                        cvs.tag(self.package.get_name(), tag.name)
                    except CvsError, e:
                        status.append(e.message)


        log.info("done.")
        return status


    def process_other(self):
        xmls = self.getFiles("*.xml")
        shellscripts = self.getFiles("*.sh")
        basedir = self.package.get_full_path()
        chdir(basedir)
        otherfiles = []

        if len(xmls) > 0:
            xmlpath = basedir.joinpath("XML")
            if not xmlpath.exists():
                xmlpath.mkdir()

            for xml in xmls:
                file = Path(xml)

                if not file.dirname() == xmlpath:
                    file.move(xmlpath)
                otherfiles.append(xml)
        
        if len(shellscripts) > 0:
            shpath = basedir.joinpath("SH")
            if not shpath.exists():
                shpath.mkdir()

            for sh in shellscripts:
                file = Path(sh)
 
                if not file.dirname() == shpath:
                    file.move(shpath)
                otherfiles.append(sh)

        log.info("Cleaning up empty directories...")
        self.clean_directory(basedir)

        return otherfiles


    def clean_directory(self, dir):
        if not dir.isdir() or self.package.get_full_path() == dir:
            return
        gen = dir.walkfiles()
        try:
            gen.next()
        except:
            dir.rmtree()
            return
        for d in dir.listdir():
            if d.isdir():
                self.clean_directory(d)

