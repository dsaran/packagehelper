# Version: $Id: config.py,v 1.7 2009-04-04 00:16:18 daniel Exp $

import logging
from path import path as Path
from package.util.runtime import WORKING_DIR

log = logging.getLogger('Config')

class Config:
    _cvs_path = 'cvs' 
    _sqlplus_path = 'sqlplus'
    _ant_path = 'ant'

    _environments = []

    def __init__(self, load=False):
        log.debug("Initializing config...")
        self.DATA_DIR        = WORKING_DIR.joinpath("data").abspath()
        if not self.DATA_DIR.exists():
            log.debug("Creating data directory...")
            self.DATA_DIR.mkdir()
        self.CONFIG_FILE = self.DATA_DIR.joinpath("config.xml").abspath()

        if load:
            self.load()

    def set_config(self, config):
        if config:
            log.debug("Setting configuration: " + str(config))
            self._cvs_path = config.get_cvs() or self._cvs_path
            self._sqlplus_path = config.get_sqlplus() or self._sqlplus_path
            self._ant_path = config.get_ant() or self._ant_path
            self._environments = config.get_environments() or self._environments

    def get_cvs(self):
        return self._cvs_path

    def get_sqlplus(self):
        return self._sqlplus_path

    def get_ant(self):
        return self._ant_path

    def get_environments(self):
        return self._environments

    def get_environments(self, database=None):
        if not database:
            return self._environments

        env_list = []
        for env in self._environments:
            if env == database:
                env_list.append(env)
        return env_list

    def get_environment(self, database):
        env = None
        try:
            index = self._environments.index(database)
            env = self._environments[index]
        except ValueError:
            log.warn("Environment not configured [%s]" % str(database))
            raise
        return env

    def set_cvs(self, path):
        self._cvs_path = path

    def set_sqlplus(self, path):
        self._sqlplus_path = path

    def set_ant(self, path):
        self._ant_path = path

    def set_environments(self, environments):
        self._environments = environments

    def add_environment(self, env):
        self._environments.append(env)

    def remove_environment(self, env):
        self._environments.remove(env)

    def save(self):
        self._save_config(self)

    def load(self):
        self.set_config(self._load_config())

    def __str__(self):
        value = "(cvs: " + self._cvs_path
        value += ", sqlplus: " + self._sqlplus_path
        value += ", ant: " + self._ant_path
        value += ")"
        return value

    __repr__ = __str__


    def _load_config(self):
        config_data = None
        config_file = Path(self.CONFIG_FILE)
        if config_file.exists():
            try:
                log.info("Loading file " + config_file)
                config_content = config_file.text()
                import yaml
                config_data = yaml.load(config_content)
            except Exception:
                log.error("Error loading configuration.", exc_info=1)
        else:
            config_data = Config()
        return config_data
    
    def _save_config(self, config):
        log.info("Saving configuration...")
        import yaml
        config_file = Path(self.CONFIG_FILE)
        try:
            config_content = yaml.dump(config)
            config_file.write_text(config_content)
        except Exception:
            log.error("Error saving configuration.", exc_info=1)


class Repositories:
    def __init__(self):
        self.DATA_DIR        = WORKING_DIR.joinpath("data").abspath()
        if not self.DATA_DIR.exists():
            log.debug("Creating data directory...")
            self.DATA_DIR.mkdir()
        self.REPOSITORY_FILE = self.DATA_DIR.joinpath("repositories.xml").abspath()

    def load(self):
        repos = []
        config = Config()
        file = Path(self.REPOSITORY_FILE)

        if file.exists():
            try:
                data = file.text()
                if len(data) > 0:
                    import yaml
                    repos = yaml.load(data)
            except Exception:
                log.error("Error loading saved repository data.")
        else:
            log.warn("Repository file does not exist!")
        return repos

    def save(self, repos):
        file = None
        log.info("Saving repository information")
        config = Config()
        file = Path(self.REPOSITORY_FILE)
        import yaml
        dump = yaml.dump(repos)
        file.write_text(dump)

