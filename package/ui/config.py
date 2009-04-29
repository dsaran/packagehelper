# Version: $Id$
# encoding: utf-8


import logging
import datetime
from kiwi.ui.delegates import Delegate
from kiwi.ui.objectlist import Column
from package.domain.environment import Environment
from package.domain.repository import Repository, ScmType
from package.domain.tag import Tag
from package.ui.filechooser import FileChooser
from package.config import Config
from package.util.svnutil import ReleaseXmlParser

log = logging.getLogger('ConfigEditor')

class ConfigEditor(Delegate):
    gladefile = "configuration"
    proxy_widgets = ["cvs_entry", "sqlplus_entry", "ant_entry", "svn_entry", "update_url_entry"]
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

        self.release_list.set_columns(
                        [Column('version', data_type=str, title="Versão"),
                         Column('type', data_type=str, title="Tipo"),
                         Column('time', data_type=str, title="Data")])

        self.add_proxy(self._config, self.proxy_widgets)
        self.show_all()

    #
    # Hooks
    #

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

    def on_refresh_releases_button__clicked(self, button):
        self.update_status_lbl.set_text("")
        repository_url = self._config.update_url
        log.info("Using repository %s" % repository_url)
        if not repository_url:
            self.update_status_lbl.set_text("Favor preencher a URL para update")
            return
        self.repository = Repository(root=repository_url, type=ScmType.SVN)
        xml = self.repository.processor.list('tags')
        if not xml:
            return
        parser = ReleaseXmlParser(text=xml)
        releases = parser.get_releases()
        for release in releases:
            self.release_list.append(release)

    def on_update_release_button__clicked(self, button):
        self.update_status_lbl.set_text("")
        selected = self.release_list.get_selected()
        if not selected:
            return

        from package.util.runtime import WORKING_DIR
        dest = WORKING_DIR

        tag = Tag(selected.name)
        try:
            self.repository.processor.export(dest, tag, create_tag_dir=False)
        except:
            self.update_status_lbl.set_text("Erro efetuando update, verifique o log para maiores informações.")
            raise

        self.update_status_lbl.set_text("Update realizado com sucesso, reinicie a aplicação.")
        

    #
    # Internal
    #

    def _load_config(self):
        log.info("Loading configuration...")
        self._config.load()
        for i in self._config.get_environments():
            self.environment_list.append(i)

    def _save_config(self):
        log.info("Saving configuration...")
        self._config.save()



