# Version: $Id: config.py,v 1.1.1.1 2009-01-07 22:58:30 daniel Exp $
# encoding: utf-8


import logging
from kiwi.ui.delegates import Delegate
from kiwi.ui.objectlist import Column
from package.domain.environment import Environment
from package.ui.filechooser import FileChooser
from package.config import Config

log = logging.getLogger('ConfigEditor')

class ConfigEditor(Delegate):
    gladefile = "configuration"
    proxy_widgets = ["cvs_entry", "sqlplus_entry", "ant_entry", "svn_entry"] 
    widgets = proxy_widgets + ["environment_list"]
    _changed = None
    _file = None
    _config = None 

    def __init__(self):
        Delegate.__init__(self, delete_handler=self.quit_if_last)
        self._config = Config()
        self._load_config()

        self.environment_list.set_columns(
                        [Column('bd_alias', data_type=str, title="Id BD", editable=True),
                         Column('user_alias', data_type=str, title="Id Usuário", editable=True),
                         Column('conn_string', data_type=str, title="String conexão", editable=True, width=400),
                         Column('active', data_type=bool, title="Ativo", editable=True)])

        self.add_proxy(self._config, self.proxy_widgets)
        self.show_all()

    def on_apply_button__clicked(self, *args):
        self._save_config()
        self.hide_and_quit()

    def on_select_cvs_button__clicked(self, *args):
        FileChooser(self.cvs_entry)

    def on_select_svn_button__clicked(self, *args):
        FileChooser(self.svn_entry)

    def on_select_sql_button__clicked(self, *args):
        FileChooser(self.sqlplus_entry)

    def on_select_ant_button__clicked(self, *args):
        FileChooser(self.ant_entry)

    def on_cancel_button__clicked(self, *args):
        self.hide_and_quit()

    def on_add_env_button__clicked(self, *args):
        env = Environment("bd_alias", "user_alias", "user/pass@host/sid")
        self._config.add_environment(env)
        self.environment_list.append(env)
        self.environment_list._select_and_focus_row(len(self.environment_list)-1)

    def on_del_env_button__clicked(self, *args):
        selected = self.environment_list.get_selected()
        if selected:
            self._config.remove_environment(selected)
            self.environment_list.remove(selected)

    def _load_config(self):
        log.info("Loading configuration...")
        self._config.load()
        for i in self._config.get_environments():
            self.environment_list.append(i)

    def _save_config(self):
        log.info("Saving configuration...")
        self._config.save()



