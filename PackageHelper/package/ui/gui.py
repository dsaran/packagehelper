#!/usr/bin/python2.5
# encoding: utf-8
# Version: $Id: gui.py,v 1.1.1.1 2009-01-07 22:58:30 daniel Exp $

import logging
from gtk import main, main_quit

from pickle import dump, loads

from kiwi.ui.delegates import Delegate
from kiwi.ui.objectlist import Column

from package.domain.tag import Tag
from package.domain.repository import Repository
from package.domain.package import Package
from package.domain.defect import Defect
from package.ui.editor import Editor
from package.ui.filechooser import FileChooser
from package.ui.config import ConfigEditor
from package.config import REPOSITORY_FILE
from package.releasenotes import RNGenerator
from package.sqlrunner import run_scripts
from package.processor import PackageProcessor
from package.util.format import list2str

from path import path as Path

_log = logging.getLogger('PackageProcessorGUI')

class Logger(logging.Logger):
    logger = _log
    callback = None

    def info(self, msg, *args, **kwargs):
        self.notify(msg)
        self.logger.info(msg)

    def warn(self, msg, *args, **kwargs):
        self.notify(msg)
        self.logger.warn(msg)

    def error(self, msg, *args, **kwargs):
        self.notify(msg)
        self.logger.error(msg, exc_info=1)

    def set_callback(self, callback):
        self.callback = callback

    def notify(self, msg):
        if self.callback:
            self.callback(msg)

log = Logger("PackageProcessorGUI")
log.addHandler(_log)

class PackageProcessorGUI(Delegate):

    widgets = [# General widgets
               "add_tag_button",
               "del_tag_button",
               "quit_button",
               "confirm_button",
               "add_repository_button",
               "del_repository_button",
               "package_entry",
               "path_entry",
               "logger_view",
               "open_folder_button",
               "cancel_folder_button",
               "select_path_button",
               "filelist",
               "scriptlist",
               # Java build widgets
               "buildfile_entry",
               "buildtarget_entry",
               "distfolder_entry",
               # RN widgets
               "defect_ptin_entry",
               "defect_vivo_entry",
               "defect_desc_entry",
               # Actions
               "quit_action",
               "save_action",
               "open_action",
               "process_action"]

    gladefile = "app"

    processor = None

    def __init__(self):
        log.info("Starting application")
        log.set_callback(self._write_logger)

        self.package = Package()
        self.processor = PackageProcessor(self.package)

        Delegate.__init__(self, delete_handler=self.quit)
        self.add_proxy(self.package, ["path_entry", "package_entry"])

        # Creates a list for the tags
        self.tags.set_columns([Column('name', data_type=str,\
                                      title="Tag", width=400,\
                                      editable=True)])

        # Creates a list of repositories
        self.repositories.set_columns(
                [Column('root', data_type=str, title="Repositório", editable=True, width=400),
                 Column('module', data_type=str, title="Módulo", width=140, editable=True),
                 Column('active', data_type=bool, title="Ativo", editable=True)])

        for repo in self._load_repos():
            self.package.add_repository(repo)
        self.repositories.add_list(self.package.get_repositories())

        # Creates a list of checked out files
        filecolumns = [Column('path', data_type=str, title="Arquivo")]
        self.filelist.set_columns(filecolumns)

        # Creates a list of created scripts
        scriptcolumns = [Column('path', data_type=str, title="Script gerado"),\
                         Column("type", data_type=str, title="Tipo")]
        self.scriptlist.set_columns(scriptcolumns)

        # Creates a list of defects
        defectcolumns = [Column('id_ptin', data_type=str, title= "ID PTIn", editable=True),
                         Column('id_vivo', data_type=str, title= "ID Vivo", editable=True),
                         Column('description', data_type=unicode, title= "Descrição", editable=True)]
        self.defectlist.set_columns(defectcolumns)

        self.register_validate_function(self.validity)

        self.force_validation()
        self.show_all()
        main()

    def get_processor(self):
        if not self.processor:
            if self.get_package() and self.get_path():
                return None                

    def get_package(self):
        return self.package_entry.get_text()

    def set_package(self, package):
        return self.package_entry.set_text(package)

    def get_path(self):
        return self.path_entry.get_text()

    def get_tags(self):
        return self.tags[:]

    #
    # Hooks
    #

    def validity(self, valid):
            self.confirm_button.set_sensitive(valid)
            self.process_action.set_sensitive(valid)
            self.checkout_action.set_sensitive(valid)
            self.generate_rn_button.set_sensitive(valid)

    def on_select_path_button__clicked(self, *args):
        FileChooser(self.path_entry, folder_mode=True)

    def on_quit_button__clicked(self, *args):
        self.quit()
    
    def on_confirm_button__clicked(self, *args):
        checkout = True
        repos = [r for r in self.repositories[:] if r.active]
        if not repos:
            log.warn("Nenhum repositório selecionado.")
            checkout = False

        if checkout and not self.tags[:]:
            log.warn("Nenhuma tag selecionada.")
            checkout = False

        if checkout:
            self._run_checkout()

        log.info("\nGerando scripts...")

        self._run_process()

        log.info("Fim da geração dos scripts.")

    def on_add_tag_button__clicked(self, *args):
        newTag = Tag("TAG_NAME")
        self.package.add_tag(newTag)
        self.tags.append(newTag)
        self.tags._select_and_focus_row(len(self.tags)-1)

    def on_del_tag_button__clicked(self, *args):
        selected = self.tags.get_selected()
        if selected:
            self.package.remove_tag(selected)
            self.tags.remove(selected)

    def on_add_repository_button__clicked(self, *args):
        repository = Repository(":pserver:<user>:<password>@host:path", "Module")
        self.package.add_repository(repository)
        self.repositories.append(repository)
        self.repositories._select_and_focus_row(len(self.repositories)-1)
         
    def on_del_repository_button__clicked(self, *args):
        selected = self.repositories.get_selected()
        if selected:
            self.package.remove_repository(selected)
            self.repositories.remove(selected)

    def on_preferences_action__activate(self, *args):
        ConfigEditor()

    def on_process_action__activate(self, *args):
        self._run_process()

    def on_checkout_action__activate(self, *args):
        self._run_checkout()

    def on_scriptlist__row_activated(self, treeview, path):
        Editor(path)

    def on_filelist__row_activated(self, treeview, path):
        Editor(path)

    def on_buildfile_button__clicked(self, *args):
        FileChooser(self.buildfile_entry)

    def on_distfolder_button__clicked(self, *args):
        FileChooser(self.distfolder_entry, folder_mode=True)

    def on_execute_button__clicked(self, *args):
        if len(self.scriptlist) == 0:
            log.info("Não há scripts para executar.")
            return
        try:
            self._set_running(True)
            run_scripts(self.scriptlist[:])
            self._write_logger("Scripts executados. Para mais informações veja os logs gerados.")
        except Exception, msg:
            log.error("\nErro executando scripts:\n>>" + str(msg), exc_info=1)
            raise
        finally:
            self._set_running(False)


    def on_generate_rn_button__clicked(self, *args):
        try:
            log.info("\nGerando RN...")
            rngen = RNGenerator(self.package)
            rngen.writeRN()
            log.info("RN gerada com sucesso.")
        except:
            log.error("Erro gerando RN.", exc_info=1)
            raise

    def on_add_defect_button__clicked(self, *args):
        id_ptin = self.defect_ptin_entry.get_text()
        id_vivo = self.defect_vivo_entry.get_text()
        description = self.defect_desc_entry.read()

        if not id_ptin and not id_vivo:
            return

        defect = Defect()
        defect.id_ptin = id_ptin 
        defect.id_vivo = id_vivo
        defect.description = description
        self.defect_ptin_entry.set_text('')
        self.defect_vivo_entry.set_text('')
        self.defect_desc_entry.update('')
        self.package.add_defect(defect)
        self.defectlist.append(defect)

    def on_del_defect_button__clicked(self, *args):
        selected = self.defectlist.get_selected()
        if selected:
            self.package.remove_defect(selected)
            self.defectlist.remove(selected)

    def quit(self, *args):
        log.info("\nSaindo...")
        self._save_repos(self.repositories[:])
        main_quit()

    #
    # Helpers
    #

    def _run_checkout(self):
        try:
            log.info("Iniciando Checkout...")

            self._set_running(True)
            status = self.processor.checkout_files()
        except:
            log.error("Erro realizando checkout dos repositorios!", exc_info=1)
            raise
        finally:
            self._set_running(False)
        log.info("Checkout finalizado.")

        result = self._show_status(status)
        log.info(result)

        return status

    def _run_process(self):
        try:
            log.info("Iniciando processamento dos arquivos...")

            self._set_running(True)
            scripts = self.processor.process_files()
        except Exception:
            log.error("Erro gerando scripts!", exc_info=1)
            raise
        finally:
            self._set_running(False)

        self.filelist.add_list(self.package.get_files())
        self.scriptlist.add_list(scripts)

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

    def _write_logger(self, value):
        try:
            textbuf = self.logger_view.props.buffer
            end_mark = textbuf.get_mark('insert')
            begin = textbuf.get_iter_at_offset(0)
            end = textbuf.get_iter_at_mark(end_mark)
            old_data = textbuf.get_text(begin, end)
            textbuf.set_text(old_data + value + '\n')
            self.logger_view.scroll_to_mark(end_mark, 0, True, 0, 1)
        except:
            log.error("Error writing log to logger_view", exc_info=1)

    def _load_repos(self):
        repos = []
        file = Path(REPOSITORY_FILE)

        if file.exists():
            try:
                data = file.text()
                if len(data) > 0:
                    from xml.marshal import generic
                    repos = generic.loads(data)
            except Exception:
                log.error("Error loading saved repository data.")

        return repos

    def _save_repos(self, repos):
        try:
            log.info("Saving repository information")
            file = open(REPOSITORY_FILE, "w")
            from xml.marshal import generic
            generic.dump(repos, file)
        finally:
            file.close()

    def _set_running(self, running):
        self.app.set_sensitive(not running)


