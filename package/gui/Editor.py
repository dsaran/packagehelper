from kiwi.ui.delegates import Delegate
from gtk import main, main_quit
from path import path

from package.util.format import ENCODING

class Editor(Delegate):
    gladefile = "editor"
    widgets = ["fileview", "save", "confirm_button"]

    _changed = None
    _file = None

    def __init__(self, filename):
        Delegate.__init__(self, delete_handler=self.quit_if_last)

        self._file = path(filename)
        if not self._file.exists():
            print "File not found: " + filename
            return

        self.text = self._file.text(encoding=ENCODING)
        self.set_changed(False)

        self.add_proxy(self, ["fileview"])
        self.show_all()

    def on_fileview__content_changed(self, *args):
        self.set_changed(True)

    def on_save__activate(self, *args):
        self._file.write_text(self.text, encoding=ENCODING)
        self.set_changed(False)

    def on_confirm_button__clicked(self, *args):
        self.hide()

    def set_changed(self, changed):
        self.save.set_sensitive(changed)
        self._changed = changed
