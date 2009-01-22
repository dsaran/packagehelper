import logging
import os
from package.config import Config
from package.commandrunner import CommandRunner

log = logging.getLogger('CVS')

class CvsError(Exception):
    message = None

    def __init__(self, msg):
        self.message = msg
    
    def __init__(self, msg, cause):
        self.cause = cause
        self.message = msg

class InvalidDataError(CvsError):
    pass

class CVS:
    root = None
    module = None
    tag = None
    logged = False
    runner = None

    def __init__(self, root, module):
        """ Initialize the CVS data. 
            @param root the CVSROOT to use. 
            @param module the module to be used."""
        self.root = root
        self.module = module
        self.runner = CommandRunner()


    def login(self):
        if self.logged:
            return
        #environ["CVSROOT"] = self.root
        errorfile = self.runner.run(self.get_config().get_cvs() + " -d%s login" % self.root)
        if errorfile:
            log.error(error)
            raise CvsError(error)
        self.logged = True


    def export(self, dest, tag):
        """ Export files from cvs using the given tags and repositories.
            @param dest destination path where the files should be exported to.
            @param tag the TAG of files to be exported.
            @return a list with errors occurred, if any."""
        log.info("Exporting files...")
        if not tag:
            error_msg = "No tag to checkout."
            log.error(error_msg)
            raise InvalidDataError("No tag to checkout.")

        self.login()

        if not os.path.exists(dest):
            try:
                log.info("Creating directory: " + str(dest))
                os.mkdir(dest)
            except OSError, e:
                error_msg = "Error creating directory (%s)." % e.message
                log.error(error_msg, exc_info=1)
                raise CvsError(error_msg, e)

        # This is necessary because cvs does not accept absolute directories
        # with -d option.
        os.chdir(dest)
        cvs_path = self.get_config().get_cvs()

        log.debug("cvs path: " + cvs_path)

        command = cvs_path + " -q -z 9 export -d %s -r %s %s" %\
                (tag,\
                tag,\
                self.module)

        error = self.runner.run(command)

        if error:
            log.error(error)
            raise CvsError(error)

        log.info("done.")


    def tag(self, tag, base_tag="HEAD"):
        """ Tag files on the repository (corresponds to rtag cvs command).
            @param tag the tag to put on files.
            @param base_tag if given, use base_tag as base instead of Head."""
        self.login()

        cvs_path = self.get_config().get_cvs()
        #TODO: Validate arguments.
        command = cvs_path + " -q -z 9 rtag -F -r %s %s %s" %\
                (base_tag,\
                tag,\
                self.module)
        #log.debug("Executing command: " + command)
        #errorfile = popen(command)
        #error = errorfile.read()
        #errorfile.close()
        error = self.runner.run(command)

        if error:
            log.error(error)
            raise CvsError(error)
 

    def get_config(self):
        config = Config(load=True)
        return config
