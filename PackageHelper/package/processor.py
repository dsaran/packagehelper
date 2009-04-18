#! /usr/bin/env python2.5
# Version: $Id$

import logging
import os
from path import path as Path
from typecheck import takes
from package.domain.pack import Package
from package.domain.file import File, InstallScript
from package.util.format import ENCODING
from package.scm import ScmError, CvsProcessor

log = logging.getLogger('PackageProcessor')

class PackageProcessor:
    """ This class provides methods for package generation,
        including cvs checkout and SQL scripts creation. """

    package = None
    logger = None

    @takes("PackageProcessor", Package)
    def __init__(self, package):
        self.package = package
        self.files_loaded = False

    def _get_files(self, filter):
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
                    file = File(item, path, parse=True)
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

    def _write_scripts(self, scripts):
        scriptName = str(id).zfill(3) + '_' + db.getUser() + '_' + db.getName()
        script_data.append('SPOOL ' + scriptName + '.log')
        script_data += list[0].getInitScript()
        script_data = []
        path = self.package.get_full_path()

        for file in list:
            value = file.getScript()
            script_data += value

        script_data += list[0].getFinalScript()

        script_data.append('SPOOL OFF')
        script_file = path.joinpath(path, scriptName + '.sql')
        try:
            script_file.touch()
            script_file.write_lines(script_data, encoding=ENCODING)
        except Exception:
            log.error("Error writing script ("+ scriptName +" )", exc_info=1)
            raise
        pass

    def _generateScript(self, id, db, cat, list):
        """ Create the SQL script for a list of files.
            @param id the sequencial number of the file to be created.
            @param db Database for which the script will be created.
            @param list a list of File object to be added to the SQL script."""
        log.debug("Generating script %d_%s_%s..." % (id, db.getUser(), db.getName())) 
        list.sort()
        scriptName = "%s_%s_%s.sql" % (str(id).zfill(3), db.getUser(), db.getName())
        type = list[0].type

        script = InstallScript(scriptName, content=list, desc=cat)

        log.debug("done.")

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

    def prepare_package(self):
        """ Prepare environment for package.
            Creates directory for files if it does not exist
            or clean processed files if it exists."""
        pkg_path = self.package.full_path
        if not pkg_path.exists():
            os.mkdir(pkg_path)
        else:
            self.clean()

    def process_files(self):
        """ Process previous checked out files generating the SQL scripts.
            @return a list with the generated SQL scripts."""
        log.info("Processing files...")

        if not self.files_loaded:
            self._load_files()

        scriptId = 0
        groupedList = self.package.getGroupedFiles()
        dbKeys = groupedList.keys()
        dbKeys.sort()
        scripts = []
        for db in dbKeys:
            for cat in groupedList[db]:
                scriptId += 1
                files = groupedList[db][cat]
                script = self._generateScript(scriptId, db, cat, files)
                scripts.append(script)
        log.info("Processing files done.")

        otherfiles = self._process_other()
        return scripts

    def checkout_files(self):
        """ Check out files from cvs using the given tags and repositories.
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
        for repo in repositories:
            if repo.is_active():

                processor = repo.processor
                if self.logger:
                    processor.logger = self.logger

                for tag in tags:
                    log.debug("Checking out tag %s" %tag)
                    try:
                        processor.export(dest, tag) 
                    except ScmError, e:
                        status.append(e.message)

                    try:
                        processor.tag(self.package.get_name(), tag.name)
                    except ScmError, e:
                        status.append(e.message)

        log.info("done.")

        if not self.files_loaded:
            self._load_files()

        return status

    def clean(self, full=False):
        log.info("Cleaning package data...")
        for script in self.package.scripts:
            log.debug("Removing file %s" % script)
            script.remove()
            self.package.scripts.remove(script)
        if full:
            raise NotImplementedError("Clean has no full behavior implemented")
        log.info("done.")
 
    def _load_files(self):
        self.package.set_files([])
        files = self._get_files("*.sql")
        for file in files:
            self.package.add_file(file)

    def _process_other(self):
        xmls = self._get_files("*.xml")
        shellscripts = self._get_files("*.sh")
        basedir = self.package.get_full_path()
        os.chdir(basedir)
        otherfiles = []

        if len(xmls) > 0:
            xmlpath = basedir.joinpath("XML")
            if not xmlpath.exists():
                xmlpath.mkdir()

            for xml in xmls:
                file = Path(xml.path)

                if not file.dirname() == xmlpath:
                    file.move(xmlpath)
                otherfiles.append(xml)
        
        if len(shellscripts) > 0:
            shpath = basedir.joinpath("SH")
            if not shpath.exists():
                shpath.mkdir()

            for sh in shellscripts:
                file = Path(sh.path)
 
                if not file.dirname() == shpath:
                    file.move(shpath)
                otherfiles.append(sh)

        log.info("Cleaning up empty directories...")
        self._clean_directory(basedir)

        return otherfiles


    def _clean_directory(self, dir):
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
                self._clean_directory(d)

