from kiwi.ui.delegates import Delegate
from path import path as Path

class FileChooser(Delegate):
    gladefile = "filechooser"

    def __init__(self, target, folder_mode=False):
        Delegate.__init__(self, delete_handler=self.quit_if_last)
        self._target = target
        self._folder_mode = folder_mode
        if folder_mode:
            self.filechooser.set_action('select-folder')

        self.filechooser.show()
        self.filechooser.set_modal(True)

    def on_filechooser_cancel_button__clicked(self, *args):
        self.hide_and_quit()

    def on_filechooser_confirm_button__clicked(self, *args):
        path = self.filechooser.get_filename()
        if not self._folder_mode and Path(path).isdir():
            return
        self._target.set_text(path)
        self.hide_and_quit()
