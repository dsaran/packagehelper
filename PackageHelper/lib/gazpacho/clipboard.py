# Copyright (C) 2004,2005 by SICEm S.L.
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA 02111-1307, USA.

"""This module implements a Clipboard object to add support for
cut/copy/paste operations in Gazpacho.
It also defines a ClipboardWindow widget to graphically display and
select Clipboard data.

The Clipboard holds instances of ClipboardItems which contains information
of the widgets and a XML representation of them.
"""

import gettext

import gobject
import gtk
from kiwi.utils import gsignal, type_register

_ = lambda msg: gettext.dgettext('gazpacho', msg)

class ClipboardItem(object):
    """The ClipboardItem is the data that is stored in the
    clipboard. It contains an XML representation of the widget and
    some additional information that can be useful to know about
    without having to recreate the widget.."""

    def __init__(self, widget):
        self.name = widget.name
        self.icon = widget.adaptor.icon.get_pixbuf()
        self.is_toplevel = widget.is_toplevel()

        self._xml = widget.to_xml()

    def to_xml(self):
        return self._xml

class Clipboard(gobject.GObject):
    """The Clipboard is an abstraction Gazpacho uses to support
    cut/copy/paste operations. It's basically a container which
    holds XML representation of copied/cut widgets.

    So far it doesn't use X selection mechanism but it should
    not be dificult to add it in the future.
    """

    gsignal('widget-added', object)
    gsignal('widget-removed', object)
    gsignal('selection-changed', object)

    def __init__(self):
        gobject.GObject.__init__(self)

        # A list with the clipboard content. New items are added to
        # the end of the list.
        self.content = []

        # The currently selected item. If None we use the last item in
        # the content list instead.
        self._selected = None

        # We limit the maximum number of items in the clipboard
        # otherwise it would grow indefinitely. If to many items are
        # added the oldest will be removed.
        self._max_clipboard_items = 15

    def get_selected(self):
        return self._selected

    def set_selected(self, item):
        self._selected = item
        if not item and self.content:
            item = self.content[-1]
        self.emit('selection_changed', item)

    selected = property(get_selected, set_selected)

    def add_widget(self, src_widget):
        """Add a ClipboardItem wrapping the the source widget to the clipboard.
        A 'widget-added' signal is then emitted to indicate that there
        are new data on the clipboard. If the clipboard contains too
        many items the oldest item will be removed and a
        'widget-removed' signal emitted."""

        item = ClipboardItem(src_widget)

        self.content.append(item)
        self.emit('widget-added', item)
        self.selected = item

        # Remove the oldest item if the clipboard contains too many
        # items
        if len(self.content) > self._max_clipboard_items:
            self._remove_oldest_item()

    def _remove_oldest_item(self):
        """Remove the oldest item from the clipboard."""
        if not self.content:
            return

        item_removed = self.content.pop(0)
        self.emit('widget-removed', item_removed)

    def get_selected_item(self):
        """Get the selected clipboard item."""
        if self.selected:
            return self._selected
        elif self.content:
            return self.content[-1]
        return None

    def get_selected_widget(self, project):
        """Get a widget instance from the selected item.

        This build a widget instance from the XML of the selected item.
        Before adding this to a project you should check that its name
        is unique
        """


        item = self.get_selected_item()
        if item is None:
            return

        from gazpacho.widget import Gadget
        return Gadget.from_xml(project, item.to_xml(), item.name)

type_register(Clipboard)

clipboard = Clipboard()

class ClipboardWindow(gtk.Window):
    """ClipboardWindow is a Widget to represent and manage a Clipboard.

    It displays the current Clipboard contents through a TreeView.
    """

    ICON_COLUMN = 0
    NAME_COLUMN = 1
    WIDGET_COLUMN = 2

    def __init__(self, parent, clipboard):
        gtk.Window.__init__(self)
        self.set_title(_('Clipboard Contents'))
        self.set_transient_for(parent)

        self._clipboard = clipboard
        clipboard.connect('widget-added', self._widget_added_cb)
        clipboard.connect('widget-removed', self._widget_removed_cb)

        self._store = self._create_store(clipboard)
        self._store.connect('row-changed', self._row_changed_cb)

        self._view = self._create_view()
        self._view.get_selection().connect('changed',
                                           self._selection_changed_cb)
        self._view.connect('row-activated', self._row_activated_cb)
        self._set_default_selection()

        scroll = gtk.ScrolledWindow()
        scroll.set_size_request(300, 200)
        scroll.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        scroll.set_shadow_type(gtk.SHADOW_IN)
        scroll.add(self._view)
        self.add(scroll)

        self._view.show_all()

    def _create_store(self, clipboard):
        """Create a ListStore and fill it will items from the clipboard."""
        store = gtk.ListStore(gtk.gdk.Pixbuf, str, object)
        for clip_item in clipboard.content:
            store.append((clip_item.icon, clip_item.name, clip_item))
        return store

    def _create_view(self):
        """Create the tree view that will display the clipboard data."""
        view = gtk.TreeView(self._store)
        view.set_headers_visible(False)

        column = gtk.TreeViewColumn()
        renderer1 = gtk.CellRendererPixbuf()
        column.pack_start(renderer1, False)
        column.add_attribute(renderer1, 'pixbuf', ClipboardWindow.ICON_COLUMN)
        renderer2 = gtk.CellRendererText()
        column.pack_start(renderer2)
        column.add_attribute(renderer2, 'text', ClipboardWindow.NAME_COLUMN)

        view.append_column(column)
        return view

    def _set_clipboard_selection(self):
        """Notify the Clipboard about which item is currently selected."""
        (model, it) = self._view.get_selection().get_selected()
        if it:
            clip_item = model[it][ClipboardWindow.WIDGET_COLUMN]
            self._clipboard.selected = clip_item

    def _selection_changed_cb(self, selection, data=None):
        """Callback for selection changes in the tree view."""
        self._set_clipboard_selection()

    def _widget_added_cb(self, clipboard, new_item):
        """Callback that is triggered when an item is added to the
        clipboard."""
        self._store.append((new_item.icon, new_item.name, new_item))

    def _widget_removed_cb(self, clipboard, old_item):
        """Callback that is triggered when an item is removed from the
        clipboard."""
        # It's always the oldes item that is removed so we can just
        # remove the first item from the store.
        first_iter = self._store.get_iter_first()
        if first_iter:
            self._store.remove(first_iter)

    def _row_changed_cb(self, model, path, new_iter, data=None):
        """Callback that is called when rows are added or removed."""
        self._set_default_selection()

    def _set_default_selection(self):
        """Set the default selection, i.e. the latest additiion."""
        last_iter = get_last_iter(self._store)
        if last_iter:
            self._view.get_selection().select_iter(last_iter)

    def _row_activated_cb(self, treeview, path, column):
        item = self._store[path][2]
        print 'The current item is represented by:'
        print item.to_xml()

    def hide_window(self):
        """Hide the clipboard window."""
        self.hide()
        self._clipboard.selected = None

    def show_window(self):
        """Show the clipboard window."""
        self.show_all()
        self._set_default_selection()

def get_last_iter(model):
    """Convenient function to get the last iterator from a tree model."""
    items = len(model)
    if items > 0:
        return model.iter_nth_child(None, items - 1)
    return None

