# Version: $Id: editor.py,v 1.1.1.1 2009-01-07 22:58:30 daniel Exp $

import logging
from kiwi.ui.delegates import Delegate
from path import path
from typecheck import takes

from package.util.format import ENCODING

log = logging.getLogger("Editor")

class Editor(Delegate):
    gladefile = "editor"
    widgets = ["fileview", "save", "confirm_button"]

    _changed = None
    _file = None

    @takes("Editor", "File")
    def __init__(self, file):
        Delegate.__init__(self, delete_handler=self.quit_if_last)

        self._file = path(file.get_path())
        if not self._file.exists():
            log.error("File not found: %s" % self._file)
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
