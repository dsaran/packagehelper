# encoding: utf-8

import logging

from kiwi.ui.delegates import GladeSlaveDelegate
from kiwi.ui.objectlist import Column
from kiwi.ui.wizard import WizardStep

from package.processor import PackageProcessor
from package.domain.tag import Tag
from package.domain.repository import Repository
from package.domain.defect import Defect, Requirement
from package.util.format import list2str

from package.ui.filetree import FileTree
from package.ui.filechooser import FileChooser
from package.ui.editor import Editor

from package.config import Config, Repositories

log = logging.Logger("Application")

class BaseWizardStep(WizardStep, GladeSlaveDelegate):
    """A wizard step base class definition"""
    gladefile = None

    def __init__(self, previous=None, next=None, header=None):
        WizardStep.__init__(self, previous, header)
        GladeSlaveDelegate.__init__(self, gladefile=self.gladefile)
        self.next = next

    def next_step(self):
        return self.next

    def has_next_step(self):
        return self.next != None

class FileListSlave(GladeSlaveDelegate):

    widgets=["filelist"]

    gladefile="filelistslave"

    def __init__(self, model=None, statusbar=None):
        GladeSlaveDelegate.__init__(self, gladefile=self.gladefile)

        self.model = model or self
        #self.model.filelist = self.filelist

        filecolumns = [Column('path', data_type=str, title="Arquivo", expand=True, searchable=True)]
        self.filelist.set_columns(filecolumns)
 
        self.filelist.add_list(self.model.get_files())

    def on_filelist__row_activated(self, treeview, path):
        Editor(path)

    def add_list(self, list):
        self.filelist.add_list(list)
        #self.model.files = list

    def get_data(self):
        return self.filelist[:]

class ScriptListSlave(GladeSlaveDelegate):

    widgets=["filelist"]
    gladefile="filelistslave"

    def __init__(self, model=None):
        GladeSlaveDelegate.__init__(self, gladefile=self.gladefile)

        self.model = model or self
 
        # Creates a list of created scripts
        scriptcolumns = [Column('path', data_type=str, title="Script gerado"),\
                         Column("type", data_type=str, title="Tipo")]
        self.model.scriptlist.set_columns(scriptcolumns)

    def on_scriptlist__row_activated(self, treeview, path):
        Editor(path)


class MainDataStep(BaseWizardStep):

    widgets = [# General widgets
               "add_tag_button",
               "del_tag_button",
               "add_repository_button",
               "del_repository_button",
               "package_entry",
               "path_entry",
               "checkout_chk",
               "process_chk",
               "open_folder_button",
               "cancel_folder_button",
               "select_path_button"]

    gladefile = "maindataslave"

    def __init__(self, model=None, previous=None, header=None, logger=None,
                 statusbar=None):
        BaseWizardStep.__init__(self, previous=previous, header=header)

        if logger:
            global log
            log = logger

        self.model = model or self

        # Creates a list for the tags
        self.tag_list.set_columns([Column('name', data_type=str,\
                                      title="Tag", expand=True,\
                                      editable=True)])

        # Creates a list of repositories
        self.repository_list.set_columns(
                [Column('root', data_type=str, title="Repositório", editable=True, expand=True),
                 Column('module', data_type=str, title="Módulo", width=150, editable=True),
                 Column('active', data_type=bool, title="Ativo", editable=True)])

        self.add_proxy(self.model, ["path_entry", "package_entry", "checkout_chk", "process_chk"])

        self.checkout_chk.set_active(True)
        self.process_chk.set_active(True)

        self._load_repos()


    def validate_step(self):
        is_ok = self.model.path and self.model.path.strip()
        #XXX: Display feedback to user.
        return is_ok

    def on_add_tag_button__clicked(self, *args):
        newTag = Tag("TAG_NAME")
        self.model.add_tag(newTag)
        self.tag_list.append(newTag)
        self.tag_list._select_and_focus_row(len(self.tag_list)-1)

    def on_del_tag_button__clicked(self, *args):
        selected = self.tag_list.get_selected()
        if selected:
            self.model.remove_tag(selected)
            self.tag_list.remove(selected)

    def on_add_repository_button__clicked(self, *args):
        repository = Repository(":pserver:<user>:<password>@<host>:<path>", "<Module>")
        self.model.repositories.append(repository)
        self.repository_list.append(repository)
        self.repository_list._select_and_focus_row(len(self.repository_list)-1)
         
    def on_del_repository_button__clicked(self, *args):
        selected = self.repository_list.get_selected()
        if selected:
            self.model.remove_repository(selected)
            self.repository_list.remove(selected)

    def on_select_path_button__clicked(self, *args):
        FileChooser(self.path_entry, folder_mode=True)

    def _load_repos(self):
        log.info("Carregando repositorios salvos...")
        repositories = Repositories()
        repos = repositories.load()
        if repos:
            for repo in repos:
                self.model.repositories.append(repo)
                self.repository_list.append(repo)
        log.info("Dados carregados com sucesso.")

    def _save_repos(self):
        log.info("Salvando repositorios...")
        repositories = Repositories()
        repositories.save(self.model.repositories)

class ManageFilesStep(BaseWizardStep):

    gladefile = "managefilesslave"

    def __init__(self, model=None, previous=None, header=None,
                 statusbar=None, logger=None):
        BaseWizardStep.__init__(self, previous=previous, header=header)

        if logger:
            global log
            log = logger

        self.model = model or self

        self.filetree = FileTree(model=self, statusbar=statusbar)
        self.filelist = FileListSlave(model=self.model)
        self.attach_slave('filelist_holder', self.filelist)
        self.attach_slave('scriptlist_holder', self.filetree)
        ## Creates a list of checked out files
        #filecolumns = [Column('path', data_type=str, title="Arquivo", expand=True)]
        #self.filelist.set_columns(filecolumns)

        self.processor = PackageProcessor(self.model)

    def post_init(self):
        self.processor.clean()
        for item in self.filetree.fileTree[:]:
            self.filetree.fileTree.remove(item)

        if self.model.checkout:
            self._run_checkout()

        if self.model.process:
            self._run_process()

    def _run_checkout(self):
        #XXX: Make it asynchronous
        try:
            log.info("Iniciando Checkout...")

            #self._set_running(True)
            status = self.processor.checkout_files()
        except:
            log.error("Erro realizando checkout dos repositorios!", exc_info=1)
            raise
        #finally:
        #    self._set_running(False)
        log.info("Checkout finalizado.")

        result = self._show_status(status)
        log.info(result)

        self.filelist.add_list(self.model.get_files())
        return status

    def _run_process(self):
        try:
            log.info("Iniciando processamento dos arquivos...")

            #self._set_running(True)
            scripts = self.processor.process_files()
        except Exception:
            log.error("Erro gerando scripts!", exc_info=1)
            raise
        #finally:
        #    self._set_running(False)

        for script in scripts:
            self.filetree.append(script)

        result = self._show_scripts(scripts)
        log.info(result)

        return scripts

    def _show_scripts(self, scripts):
        buffer = ""
        if scripts:
            buffer += "\nScripts criados:\n"
            buffer += list2str(scripts)
            buffer += "\nScripts criados com sucesso!"
        else:
            buffer += "\nNenhum script criado!"
        return buffer

    def _show_status(self, status):
        buffer = "\nStatus da execução:\n"
        if status:
            buffer += list2str(status)
        return buffer


class ReleaseNotesStep(BaseWizardStep):

    gladefile = "releasenotesstep"

    widgets = ["add_defect_button",
               "del_defect_button",
               "add_req_button",
               "del_req_button"
               "defect_ptin_entry",
               "defect_vivo_entry",
               "defect_desc_entry",
               "req_id_entry",
               "req_desc_entry"]

    def __init__(self, model=None, previous=None, header=None, statusbar=None):
        self.model = model or self
        BaseWizardStep.__init__(self, previous=previous, header=header)

        # Creates a list of defects
        defectcolumns = [Column('id_ptin', data_type=str, title= "ID PTIn", editable=True),
                         Column('id_vivo', data_type=str, title= "ID Vivo", editable=True),
                         Column('description', data_type=unicode, title= "Descrição",
                                editable=True, expand=True)]
        self.defectlist.set_columns(defectcolumns)

        reqcolumns = [Column('id', data_type=str, title="ID", editable=True),
                      Column('description', data_type=str, title="Descrição",
                             editable=True, expand=True)]
        self.requirementlist.set_columns(reqcolumns)

        self.add_proxy(self, ["req_desc_entry"])

    def on_add_defect_button__clicked(self, *args):
        id_ptin = self.defect_ptin_entry.get_text()
        id_vivo = self.defect_vivo_entry.get_text()
        description = self.defect_desc_entry.read()

        if not id_ptin and not id_vivo:
            #XXX: Display message to user
            return

        defect = Defect()
        defect.id_ptin = id_ptin 
        defect.id_vivo = id_vivo
        defect.description = description
        self.defect_ptin_entry.set_text('')
        self.defect_vivo_entry.set_text('')
        self.defect_desc_entry.update('')
        self.model.add_defect(defect)
        self.defectlist.append(defect)

    def on_del_defect_button__clicked(self, *args):
        selected = self.defectlist.get_selected()
        if selected:
            self.model.remove_defect(selected)
            self.defectlist.remove(selected)
 
    def on_add_req_button__clicked(self, *args):
        req_id = self.req_id_entry.get_text()
        req_desc = self.req_desc_entry.read()
        if not req_id:
            #XXX: Display message to user
            return

        req = Requirement(req_id, req_desc)
        self.requirementlist.append(req)
        self.model.requirements.append(req)

        self.req_id_entry.set_text('')
        self.req_desc_entry.update('')

    def on_del_req_button__clicked(self, *args):
        selected = self.requirementlist.get_selected()
        if selected:
            self.model.requirements.remove(selected)
            self.requirementlist.remove(selected)


class ShowPackageStep(BaseWizardStep):

    def __init__(self, model=None, previous=None, header=None, statusbar=None):
        self.statusbar = statusbar
        self.model = model or self
        self.filelist = FileListSlave(model=model, statusbar=statusbar)
        self.gladefile = self.filelist.gladefile

        BaseWizardStep.__init__(self, previous=previous, header=header)
 
        self._initialized = False

    def post_init(self):
        print "Post init called"
        for script in self.model.scripts:
            script.created()
        self._initialized = True


