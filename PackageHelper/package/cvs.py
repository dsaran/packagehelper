class CVS

    root = None
    module = None
    tag = None

    def __init__(self, root, module):
        """ Initialize the CVS data. 
            @param root the CVSROOT to use. 
            @param module the module to be used."""
       self.root = root
       self.module = module
       self.tag = tag

    def export(self, tags=[]):
        """ Export files from cvs using the given tags and repositories.
            @param tags is a list of Tag objects
            @return a list with errors occurred, if any."""
        log.info("Checking out files...")
        status = []
        tags = self.package.get_tags()
        repositories = self.package.get_repositories()
        if not tags or not repositories:
            status.append("No repository/tag to checkout.")
            log.info(status)
            return status

        p = self.package.get_full_path()
        if not p.exists():
            try:
                log.info("Creating directory: " + str(p))
                p.mkdir()
            except OSError:
                log.error("Error creating directory.", exc_info=1)
                raise 
        # This is necessary because cvs does not accept absolute directories
        # with -d option.
        chdir(p)
        config = Config(load=True)
        cvs = config.get_cvs()
        log.debug("cvs path: " + cvs)
        for repo in repositories:
            if repo.is_active():
                environ["CVSROOT"] = repo.root
                errorfile = popen(cvs + " login")
                error = errorfile.read()
                errorfile.close()
                if error:
                    log.info(error)
                    status.append(error)

                for tag in tags:
                    command = cvs + " -q -z 9  export -d %s -r %s %s" %\
                            (tag.name,\
                            tag.name,\
                            repo.module)
                    log.debug("Executing command: " + command)
                    errorfile = popen(command)
                    error = errorfile.read()
                    errorfile.close()

                    command = cvs + " -q -z 9 rtag -F -r %s %s %s" %\
                            (tag.name,\
                            self.package.get_name(),\
                            repo.module)
                    log.debug("Executing command: " + command)
                    errorfile = popen(command)
                    error = errorfile.read()
                    errorfile.close()
 
                    if error:
                        log.info(error)
                        status.append(error)
        log.info("done.")
        return status


