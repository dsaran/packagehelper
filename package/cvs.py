import logging
from commandrunner import CommandRunner

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

    def __init__(self, root, module):
        """ Initialize the CVS data. 
            @param root the CVSROOT to use. 
            @param module the module to be used."""
        self.root = root
        self.module = module
        self.tag = tag


    def export(self, dest, tag):
        """ Export files from cvs using the given tags and repositories.
            @param dest destination path where the files should be exported to.
            @param tags is a list of Tag objects
            @return a list with errors occurred, if any."""
        log.info("Exporting files...")
        if not tag:
            error_msg = "No tag to checkout."
            log.error(error_msg)
            raise InvalidDataError("No tag to checkout.")

        self.login()

        if not dest.exists():
            try:
                log.info("Creating directory: " + str(dest))
                dest.mkdir()
            except OSError, e:
                error_msg = "Error creating directory (%s)." % e.message
                log.error(error_msg, exc_info=1)
                raise CvsError(e)

        # This is necessary because cvs does not accept absolute directories
        # with -d option.
        chdir(dest)
        cvs_path = self.get_config().get_cvs()

        log.debug("cvs path: " + cvs_path)

        command = cvs_path + " -q -z 9  export -d %s -r %s %s" %\
                (tag.name,\
                tag.name,\
                self.module)

        runner = Commandrunner(command)
        error = runner.run()

        if error:
            log.error(error)
            raise CvsError(error)

        log.info("done.")


    def login(self):
        if self.logged:
            return
        environ["CVSROOT"] = self.root
        errorfile = popen(cvs + " login")
        error = errorfile.read()
        errorfile.close()
        if error:
            log.error(error)
            raise CvsError(error)
        self.logged = True


    def tag(self):
        self.login()
        command = cvs_path + " -q -z 9 rtag -F -r %s %s %s" %\
                (tag.name,\
                self.package.get_name(),\
                self.module)
        log.debug("Executing command: " + command)
        errorfile = popen(command)
        error = errorfile.read()
        errorfile.close()

        if error:
            log.error(error)
            raise CvsError(error)
 

    def get_config(self):
        config = Config(load=True)
        return config

