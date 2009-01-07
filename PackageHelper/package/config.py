# Version: $Id: config.py,v 1.1.1.1 2009-01-07 22:58:30 daniel Exp $

import logging
from path import path as Path

log = logging.getLogger('Config')

class Config:
    _cvs_path = 'cvs' 
    _sqlplus_path = 'sqlplus'
    _ant_path = 'ant'

    _environments = []

    def __init__(self, load=False):
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
        save_config(self)

    def load(self):
        self.set_config(load_config())

    def __str__(self):
        value = "(cvs: " + self._cvs_path
        value += ", sqlplus: " + self._sqlplus_path
        value += ", ant: " + self._ant_path
        value += ")"
        return value

    __repr__ = __str__


def load_config():
    config_data = None
    if Path(CONFIG_FILE).exists():
        try:
            log.info("Loading file " + CONFIG_FILE)
            file = open(CONFIG_FILE, 'r')
            from xml.marshal import generic
            config_data = generic.load(file)
        except Exception:
            log.error("Error loading configuration.", exc_info=1)
        finally:
            file.close()
    else:
        config_data = Config()
    return config_data

def save_config(config):
    log.info("Saving configuration...")
    from xml.marshal import generic
    file = open(CONFIG_FILE, "w")
    generic.dump(config, file)
    file.close()


from sys import argv
import os
log.debug("Initializing config...")
WORKING_DIR     = Path(os.environ['PKG_BASEDIR'])
DATA_DIR        = WORKING_DIR.joinpath("data").abspath()
if not DATA_DIR.exists():
    DATA_DIR.mkdir()
CONFIG_FILE = DATA_DIR.joinpath("config.xml").abspath()
REPOSITORY_FILE = DATA_DIR.joinpath("repositories.xml").abspath()

