import logging
import os
from path import path as Path
from package.config import Config
from package.commandrunner import CommandRunner

log = logging.getLogger('CVS')

class ScmError(Exception):
    message = None

    def __init__(self, msg, cause=None):
        self.cause = cause
        self.message = msg

class InvalidDataError(ScmError):
    pass

class BaseProcessor:
    runner = None
    def __init__(self):
        self.runner = CommandRunner()

    def run_command(self, command):
        output, error = self.runner.run(command)

        if output:
            log.info(output)
        if error:
            log.error(error)
            raise ScmError(error)

    def get_config(self):
        return Config(load=True)


class CvsProcessor(BaseProcessor):
    root = None
    module = None
    tag = None
    logged = False

    def __init__(self, root, module):
        """ Initialize the CVS data. 
            @param root the CVSROOT to use. 
            @param module the module to be used."""
        os.environ["CVSROOT"] = root
        self.root = root
        self.module = module
        BaseProcessor.__init__(self)


    def login(self):
        if self.logged:
            return
        output, errorfile = self.runner.run(self.get_config().get_cvs() + " -d%s login" % self.root)
        if output:
            log.info(output)
        if errorfile:
            log.error(errorfile)
            raise ScmError(errorfile)
        self.logged = True


    def export(self, dest, tag):
        """ Export files from cvs using the given tags and repositories.
            Corresponding CVS command would be:
                cvs export -r tag -d dest
            @param dest destination path where the files should be exported into.
            @param tag the TAG of files to be exported.
        """
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
                raise ScmError(error_msg, e)

        # This is necessary because cvs does not accept absolute directories
        # with -d option.
        # Need to backup original location to avoid breaking other components
        # who might need to get program location.
        original_cwd = os.getcwd()
        os.chdir(dest.abspath())
        cvs_path = self.get_config().get_cvs()

        log.debug("cvs path: " + cvs_path)

        command = cvs_path + " -q -z 9 -d%s export -d %s -r %s %s" %\
                (self.root,\
                tag,\
                tag,\
                self.module)

        output, error = self.runner.run(command)

        os.chdir(original_cwd)

        if output:
            log.info(output)
        if error:
            log.error(error)
            raise ScmError(error)

        log.info("done.")


    def tag(self, tag, base_tag="HEAD"):
        """ Tag files on the repository (corresponds to rtag cvs command).
            Corresponding CVS command would be:
                cvs -d :pserver:user:pass@cvs.host.org:/path/to/cvs \
                    rtag [-r base_tag] tag
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
        output, error = self.runner.run(command)

        if output:
            log.info(output)
        if error:
            log.error(error)
            raise ScmError(error)
 

    def get_config(self):
        config = Config(load=True)
        return config

login = "--username NGINPackageManager --password NGINPackageManager"
message = '-m "Packaged by PackageHelper"'

class SubversionProcessor(BaseProcessor):
    def __init__(self, root, module=None):
        """ Initialize subversion processor.
            If the URL of trunk of a module is svn://svn.host.org/repos/MyModule/trunk
            then root should be "svn://svn.host.org/repos/" and module "MyModule".
            @param root Repository root
            @param module Module name
        """
        self.root = Path(root)
        self.module = module

        BaseProcessor.__init__(self)

    def export(self, dest, tag):
        """ Export tag content of the given module to destination.
            For example, to export a tag new_tag of module MyModule
            whose root repository is svn://svn.host.org/repos/
            to destination '/my/destination/path' the corresponding subversion
            command would be:
                svn export svn://svn.host.org/repos/MyModule/tags/the_tag \
                    /my/destination/path
            @param dest Destination path
            @param tag Tag to export
        """
        log.info("Checking out data...")

        from string import Template
        svn_bin = self.get_config().svn

        destination = dest/tag.name

        repo_path = self.root/self.module/'tags'/tag.name
        cmd_template = Template("$svn_bin export $login $repo_path $dest")
        command = cmd_template.substitute(svn_bin=svn_bin, repo_path=repo_path, login=login, dest=destination)

        self.run_command(command)

        log.info("done.")

    def tag(self, tag, base_tag=None):
        """ Tag a file or base_tag files with 'tag', if no base_tag is given it will
            tag the trunk content.
            It will assume that the url is like Root/Module/ and then will copy
            base_tag content to Root/Module/tags/tag.
            For example, if base tag name is 'basetag' with root like svn://svn.host.org/repos
            corresponding SVN command would be:
                svn copy svn://svn.host.org/repos/Module/tags/base_tag \
                        svn://svn.host.org/repos/Module/tags/tag/
            or if no base_tag is given:
                svn copy svn://svn.host.org/repos/Module/trunk \
                        svn://svn.host.org/repos/Module/tags/tag/
        """
        log.info("Tagging repository...")

        from string import Template
        svn_bin = self.get_config().svn

        cmd_template = Template("$svn_bin copy $login $msg $repo_path/$base_tag_path $repo_path/tags/$tag/")

        repo_path = self.root/self.module

        if not base_tag:
            base_tag_path = 'trunk/'
        else:
            base_tag_path = 'tags/%s/' % base_tag

        command = cmd_template.substitute(svn_bin=svn_bin, login=login, msg=message, repo_path=repo_path, \
                                            base_tag_path=base_tag_path, tag=tag)

        self.run_command(command)

