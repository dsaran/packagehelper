import logging
import os
from path import path as Path
from package.config import Config
from package.commandrunner import CommandRunner, Command
from package.util.format import urljoin

log = logging.getLogger('[SCM]')

class ScmError(Exception):
    message = None

    def __init__(self, msg, cause=None, stdout=None):
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
            raise ScmError(error, stdout=output)

        return output

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

        command = Command(self.get_config().cvs)
        command.args = ["-d", self.root, "login"]
        output = self.run_command(command)

        if output:
            log.info(output)
        self.logged = True


    def export(self, dest, tag):
        """ Export files from cvs using the given tags and repositories.
            Corresponding CVS command would be:
                cvs export -r tag -d dest
            @param dest destination path where the files should be exported into.
            @param tag the TAG of files to be exported. Should be a Tag object.
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
        cvs_path = self.get_config().cvs

        log.debug("cvs path: " + cvs_path)

        command = Command(cvs_path)
        command.args = ["-q", "-z", "9", "-d", self.root, "export", "-d", tag.name, "-r", tag.name, self.module]

        output = self.run_command(command)

        os.chdir(original_cwd)

        if output:
            log.info(output)

        log.info("done.")


    def tag(self, tag, base_tag="HEAD"):
        """ Tag files on the repository (corresponds to rtag cvs command).
            Corresponding CVS command would be:
                cvs -d :pserver:user:pass@cvs.host.org:/path/to/cvs \
                    rtag [-r base_tag] tag
            @param tag the tag to put on files. Tag should be a str.
            @param base_tag if given, use base_tag as base instead of Head."""
        self.login()

        cvs_path = self.get_config().cvs
        command = Command(cvs_path)
        command.args = ['-q', '-z', '9', 'rtag', '-F', '-r', base_tag, tag, self.module]

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
message = '"Packaged by PackageHelper"'

class SubversionProcessor(BaseProcessor):
    username = "NGINPackageManager"
    password = "NGINPackageManager"

    def __init__(self, root, module=None):
        """ Initialize subversion processor.
            If the URL of trunk of a module is svn://svn.host.org/repos/MyModule/trunk
            then root should be "svn://svn.host.org/repos/" and module "MyModule".
            @param root Repository root
            @param module Module name
        """
        self.root = root
        self.module = module

        BaseProcessor.__init__(self)

    def export(self, dest, tag, tag_type='tag', username=None, password=None, create_tag_dir=True):
        """ Export tag content of the given module to destination.
            @param dest path where the files should be exported to.
            @param tag tag to export. Should be a Tag object.
            @param tag_type if tag is a tag or branch, valid values are 'tag' and 'branch' (default is 'tag')
            @param username username to use on export
            @param password password to use on export
            @create_tag_dir if it should files should be exported to dest/tag/ (default is True)
            For example, to export a tag new_tag of module MyModule
            whose root repository is svn://svn.host.org/repos/
            to destination '/my/destination/path' the corresponding subversion
            command would be:
                svn export --force svn://svn.host.org/repos/MyModule/tags/the_tag \
                    /my/destination/path
        """
        log.info("Checking out data...")

        svn_bin = self.get_config().svn

        destination = dest/tag.name if create_tag_dir else dest

        if not username or not password:
            username, password = self.username, self.password

        repo_path = urljoin(self.root, self.module, 'tags', tag.name)

        command = Command(svn_bin)
        command.args = ["export", "--force", "--no-auth-cache", "--username", username, "--password", password, repo_path, destination]

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

        svn_bin = self.get_config().svn

        repo_path = urljoin(self.root, self.module)

        if not base_tag:
            base_tag_path = 'trunk'
        else:
            base_tag_path = 'tags/%s/' % base_tag

        from_path = '%s/%s' % (repo_path, base_tag_path)
        to_path = '%s/tags/%s/' % (repo_path, tag)
        command = Command(svn_bin)
        command.args = ['copy', "--no-auth-cache", "--username", self.username, "--password", self.password, "-m", message,  from_path, to_path]

        self.run_command(command)

    def list(self, path='trunk'):
        """ List content of path at repository. If no path is given the content of trunk will be listed.
            @param path the path inside the module repository to list
            @return a xml with content of repository path
            Corresponds to SVN command:
                svn list --xml svn://svn.host.org/repos/path/
        """
        log.info("Listing repository content for path '%s'" % path)

        svn_bin = self.get_config().svn

        repo_path = urljoin(self.root, self.module, path)

        command = Command(svn_bin)
        command.args = ["list", "--no-auth-cache", "--username", self.username, "--password", self.password, "--xml", repo_path]

        result = self.run_command(command)

        return result
 
