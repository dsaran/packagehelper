import gtk
import time
from kiwi.python import enum

#
# Helper classes and methods
#


DELAY = 0.00
DISPLAY=False

class Position(enum):
    BEFORE = gtk.TREE_VIEW_DROP_BEFORE
    INTO = gtk.TREE_VIEW_DROP_INTO_OR_BEFORE
    AFTER = gtk.TREE_VIEW_DROP_AFTER


def display(widget, delay=DELAY):
    if DISPLAY:
        widget.show_all()
        refresh_gui(delay)
        widget.hide()
        refresh_gui(0)

def refresh_gui(delay=DELAY):
    while gtk.events_pending():
        gtk.main_iteration_do(block=False)
    time.sleep(delay)


