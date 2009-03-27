#!/usr/bin/python2.5
# encoding: utf-8
# Version: $Id: gui.py,v 1.5 2009-03-27 02:31:33 daniel Exp $

import logging
import gtk

from pickle import dump, loads

from kiwi.ui.delegates import Delegate
from kiwi.ui.objectlist import Column
#from kiwi.ui.wizard import PluggableWizard
from package.ui.wizard import Wizard

from package.domain.tag import Tag
from package.domain.repository import Repository
from package.domain.pack import Package
from package.domain.defect import Defect
from package.ui.editor import Editor
from package.ui.filechooser import FileChooser
from package.ui.config import ConfigEditor
from package.ui.listslave import FileListSlave, MainDataStep, ManageFilesStep, ReleaseNotesStep, ShowPackageStep
from package.config import Config 
from package.releasenotes import RNGenerator
from package.sqlrunner import run_scripts
from package.processor import PackageProcessor

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
               "logger_view",
               # Actions
               "quit_action",
               "save_action",
               "open_action",
               "process_action"
               ]

    gladefile = "app2"

    processor = None

    def __init__(self):
        log.info("Starting application")
        log.set_callback(self._write_logger)

        self.package = Package()
        self.model = self.package
        self.processor = PackageProcessor(self.package)

        Delegate.__init__(self, delete_handler=self.quit)

        # Wizard definition
        self.first_step = MainDataStep(model=self.model, header="Dados do pacote", logger=log,
                                       statusbar=self.main_statusbar)
        self.manage_files_step = ManageFilesStep(model=self.model, previous=self.first_step,
                                                 header="Gerenciamento de arquivos",
                                                 statusbar=self.main_statusbar)
        self.displayscripts_step = ShowPackageStep(model=self.model, header="Pacote gerado",
                                                   previous=self.manage_files_step,
                                                   statusbar=self.main_statusbar)
        self.releasenotes_step = ReleaseNotesStep(model=self.model, previous=self.displayscripts_step,
                                                  header="Release Notes",
                                                  statusbar=self.main_statusbar)
        self.first_step.next = self.manage_files_step
        self.manage_files_step.next = self.displayscripts_step
        self.displayscripts_step.next = self.releasenotes_step

        self.steps = []
        self.steps.append(self.first_step)
        self.steps.append(self.manage_files_step)
        self.steps.append(self.displayscripts_step)
        self.steps.append(self.releasenotes_step)

        self.wizard = Wizard("Package Generation Wizard", steps=self.steps, progressbar=self.progressbar)
        self.wizard.finish = self.finish
        self.wizard.cancel = self.quit

        self.attach_slave('wizard_holder', self.wizard)

    def main(self):
        self.show_all()
        gtk.main()

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


    def _on_quit_button__clicked(self, *args):
        self.quit()
    
    def finish(self):
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

    def on_preferences_action__activate(self, *args):
        ConfigEditor()

    def _on_process_action__activate(self, *args):
        self._run_process()

    def _on_checkout_action__activate(self, *args):
        self._run_checkout()

    def _on_buildfile_button__clicked(self, *args):
        FileChooser(self.buildfile_entry)

    def _on_distfolder_button__clicked(self, *args):
        FileChooser(self.distfolder_entry, folder_mode=True)

    def _on_execute_button__clicked(self, *args):
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


    def _on_generate_rn_button__clicked(self, *args):
        try:
            log.info("\nGerando RN...")
            rngen = RNGenerator(self.package)
            rngen.writeRN()
            log.info("RN gerada com sucesso.")
        except:
            log.error("Erro gerando RN.", exc_info=1)
            raise

    

    def quit(self, *args):
        log.info("\nSaindo...")
        self.first_step._save_repos()
        gtk.main_quit()

    #
    # Helpers
    #

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


    def _set_running(self, running):
        self.app.set_sensitive(not running)


