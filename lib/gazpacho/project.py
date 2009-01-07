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

import gettext
import os.path

import gtk
import gobject
from kiwi.utils import gsignal, type_register

from gazpacho import util
from gazpacho.context import Context
from gazpacho.loader.loader import ObjectBuilder
from gazpacho.loader.custom import ButtonAdapter, DialogAdapter, \
     WindowAdapter, str2bool, adapter_registry
from gazpacho.placeholder import Placeholder
from gazpacho.signaleditor import SignalInfo
from gazpacho.sizegroup import GSizeGroup
from gazpacho.uim import GazpachoUIM
from gazpacho.widget import Gadget, load_gadget_from_widget
from gazpacho.widgetregistry import widget_registry
from gazpacho.widgets.base.custom import Custom
from gazpacho.filewriter import XMLWriter

_ = lambda msg: gettext.dgettext('gazpacho', msg)

class GazpachoObjectBuilder(ObjectBuilder):
    def __init__(self, **kwargs):
        self._app = kwargs.pop('app', None)
        kwargs['placeholder'] = self.create_placeholder
        kwargs['custom'] = Custom
        ObjectBuilder.__init__(self, **kwargs)

    def create_placeholder(self, name):
        return Placeholder()

    def show_windows(self):
        pass

class GazpachoButtonAdapter(ButtonAdapter):
    def add(self, parent, child, properties):
        # This is a hack, remove when the button saving/loading code
        # is improved
        for cur_child in parent.get_children():
            parent.remove(cur_child)
        ButtonAdapter.add(self, parent, child, properties)


class GazpachoWindowAdapter(WindowAdapter):
    object_type = gtk.Window
    def prop_set_visible(self, window, value):
        window.set_data('gazpacho::visible', str2bool(value))

    def prop_set_modal(self, window, value):
        window.set_data('gazpacho::modal', str2bool(value))

adapter_registry.register_adapter(GazpachoWindowAdapter)

# FIXME: This is quite strange, but apparently we need this too.
class GazpachoDialogAdapter(DialogAdapter):
    object_type = gtk.Dialog
    def prop_set_modal(self, window, value):
        window.set_data('gazpacho::modal', str2bool(value))

adapter_registry.register_adapter(GazpachoDialogAdapter)

class Project(gobject.GObject):
    gsignal('add-widget', object),
    gsignal('remove-widget', object),
    gsignal('project-changed'),
    gsignal('add-action', object),
    gsignal('remove-action', object),
    gsignal('add-sizegroup', object),
    gsignal('remove-sizegroup', object),

    # XXX: notify::name
    gsignal('widget-name-changed', object),
    gsignal('action_name_changed', object),

    project_counter = 1

    def __init__(self, untitled, app, loader=None):
        gobject.GObject.__init__(self)

        self._app = app

        self.name = None

        if untitled:
            # The name of the project like network-conf
            self.name = _('Untitled %d') % Project.project_counter
            Project.project_counter += 1

        # The full path of the xml file for this project
        self.path = None

        # The menu entry in the /Project menu
        self.entry = None

        self._domain = ''

        self._widgets = {}

        self._unsupported_widgets = {}

        # A list of GSizeGroups that are part of this project
        self.sizegroups = []

        # We need to keep the selection in the project because we have multiple
        # projects and when the user switchs between them, he will probably
        # not want to loose the selection. This is a list of widget items.
        self.selection = WidgetSelection()

        # widget -> old name of the widget (it's a bit of a hack)
        self._widget_old_names = {}

        self.tooltips = gtk.Tooltips()

        # A flag that is set when a project has changes if this flag is not set
        # we don't have to query for confirmation after a close or exit is
        # requested
        self._changed = False

        # There is a UIManager in each project which holds the information
        # about menus and toolbars
        self.uim = GazpachoUIM(self)

        # This is the id for the menuitem entry on Gazpacho main menu for this
        # project
        self.uim_id = -1

        # Contains the undo (and redo) commands
        self.undo_stack = UndoRedoStack()
        self.undo_stack.connect('changed', self._undo_stack_changed_cb)

        # create our context
        self.context = Context(self)

        if loader:
            self._read_from_loader(loader)

    # Private

    def _read_from_loader(self, loader):
        """
        Reads all data from the loader, such as widgets, ui manager
        definitions, signals.

        @param loader: the loader
        @type loader: L{gazpacho.loader.loader.ObjectBuilder} instance
        """
        self._domain = loader.get_domain() or ''

        # Load UIM manager
        # Do this first since the custom menubar and toolbars adapters
        # depends on all ui definitions being loaded
        self.uim.load(loader)

        # Load the widgets
        for widget in loader.toplevels:
            if isinstance(widget, gtk.Widget):
                self._load_widget(widget)

        # Load sizegroups, must be done after loading all the widgets,
        # since the sizegroups has references to the widgets
        for sizegroup in loader.sizegroups:
            name = sizegroup.get_data('gazpacho::object-id')
            widgets =  sizegroup.get_data('gazpacho::sizegroup-widgets')
            gadgets = [Gadget.from_widget(widget)
                       for widget in widgets]
            self.add_sizegroup(GSizeGroup(name, sizegroup, gadgets))

        # Signals
        for signal in loader.get_signals():
            gobj, signal_name, signal_handler, signal_after = signal[:4]
            gadget = Gadget.from_widget(gobj)
            if gadget is None:
                continue
            gadget.add_signal_handler(SignalInfo(name=signal_name,
                                                 handler=signal_handler,
                                                 after=signal_after))

        self.changed = False

    def _load_widget(self, widget):
        gadget = load_gadget_from_widget(widget, self)
        self.add_widget(widget)
        return gadget

    def _undo_stack_changed_cb(self, stack):
        """Callback for the undo stack's 'changed' signal."""
        self.changed = not self.undo_stack.on_saved()

    def _add_action_cb(self, action_group, action):
        self.emit('add-action', action)

    def _remove_action_cb(self, action_group, action):
        self.emit('remove-action', action)

    def _on_widget_notify_name(self, widget, pspec):
        
        old_name = self._widget_old_names[widget]
        new_name = widget.get_name()
        if old_name == new_name:
            # This happens but I'm not sure why, it would be nice if
            # it could be avoided
            return

        del self._widget_old_names[widget]
        del self._widgets[old_name]
        
        gadget = Gadget.from_widget(widget)
        if isinstance(widget, (gtk.MenuBar, gtk.Toolbar)):
            self.uim.update_widget_name(gadget)
            # gadget.widget might have been replaced with a new widget
            # after calling this method
            widget = gadget.widget
            widget.connect('notify::name', self._on_widget_notify_name)

        self._widget_old_names[widget] = new_name
        self._widgets[widget.get_name()] = widget

        self.emit('widget-name-changed', gadget)


    # Class methods

    def open(cls, path, app, buffer=None):
        loader = GazpachoObjectBuilder(filename=path, buffer=buffer, app=app)

        project = cls(False, app, loader)
        project.path = path
        project.name = os.path.basename(path)
        project._unsupported_widgets = loader.get_unsupported_widgets()

        return project
    open = classmethod(open)

    # Properties

    def _get_changed(self):
        return self._changed

    def _set_changed(self, value):
        if self._changed != value:
            self._changed = value
            self.emit('project-changed')
    changed = property(_get_changed, _set_changed)

    # Public API

    def get_domain(self):
        """
        Retrieves the translatable domain

        @returns: the domain
        """
        return self._domain

    def set_domain(self, domain):
        """
        Set the translatable domain for this glade file

        @param domain: domain to set
        @type domain: string
        """

        # Avoid changing the project if the domain doesn't change
        if domain == self._domain:
            return
        self._domain = domain

        # FIXME: Undo/Redo
        self.changed = True

    def get_unsupported_widgets(self):
        """
        Get a dict of the widgets that could not be loaded because
        they're not supported. The dict maps the class of the widget
        to a list of widget ids.

        @return: the unsupported widgets
        @rtype: dict
        """
        return self._unsupported_widgets

    def get_app(self):
        return self._app

    def get_id(self):
        return "project%d" % id(self)

    def get_widgets(self):
        return self._widgets.values()

    def get_gadget_by_name(self, name):
        if not name in self._widgets:
            return

        return Gadget.from_widget(self._widgets[name])

    def get_windows(self):
        return [widget for widget in self._widgets.values()
                           if widget.flags() & gtk.TOPLEVEL]

    def add_widget(self, widget, new_name=False):
        """
        Adds a widget to the project and optionally sets a new name
        if it already exists. Will emit add-widget signal when done.

        @param widget:
        @param new_name: If True assign a new name if it already
          exists
        """

        # we don't list placeholders
        if isinstance(widget, Placeholder):
            return

        if isinstance(widget, gtk.Container):
            children = widget.get_children()
        else:
            children = []

        # The internal widgets (e.g. the label of a GtkButton) are handled
        # by gtk and don't have an associated gadget: we don't want to
        # add these to our list. It would be nicer to have a flag to check
        # (as we do for placeholders) instead of checking for the associated
        # gadget, so that we can assert that if a widget is _not_
        # internal, it _must_ have a corresponding gadget...
        # Anyway this suffice for now.
        gadget = Gadget.from_widget(widget)
        if not gadget:
            return

        gadget.project = self
        self._widget_old_names[widget] = widget.get_name()

        widget_name = widget.name
        if new_name and gadget.name in self._widgets:
            widget_name = self.set_new_widget_name(gadget.widget)

        widget.connect('notify::name', self._on_widget_notify_name)
        self._widgets[widget_name] = widget

        for child in children:
            self.add_widget(child, new_name=new_name)

        self.emit('add-widget', gadget)

    def add_hidden_widget(self, widget):
        """
        Adds a hidden widget, eg one which is not displayed to a project.
        It also updates the name of the widget
        @param widget: the widget
        """

        if not isinstance(widget, gtk.Widget):
            raise TypeError("widget %r is not gtk.Widget instance" % widget)

        self._widgets[widget.get_name()] = widget

    def remove_widget(self, widget):
        if isinstance(widget, Placeholder):
            return

        if isinstance(widget, gtk.Container):
            for child in widget.get_children():
                self.remove_widget(child)

        gadget = Gadget.from_widget(widget)
        if not gadget:
            return

        if widget in self.selection:
            self.selection.remove(widget, False)
            self.selection.selection_changed()

        del self._widgets[widget.get_name()]

        self.emit('remove-widget', gadget)

    # XXX: replace_widget
    def replace(self, widget_name, new_widget):
        """
        Replace an existing widget with a new one
        @param widget_name: name of widget to replace
        @param new_widget: new widget
        """

        widgets = self._widgets
        if not widget_name in widgets:
            raise KeyError("No widget called: %s" % widget_name)

        if not isinstance(new_widget, gtk.Widget):
            raise TypeError("new_widget must be a gtk.Widget")

        del widgets[widget_name]
        widgets[widget_name] = new_widget
        self.changed = True

    def add_sizegroup(self, sizegroup):
        """
        Add a SizeGroup to the project.

        @param sizegroup: the sizegroup to add
        @type sizegroup: gazpacho.sizegroup.GSizeGroup
        """
        if sizegroup in self.sizegroups:
            return

        self.sizegroups.append(sizegroup)
        self.emit('add-sizegroup', sizegroup)

    def remove_sizegroup(self, sizegroup):
        """
        Remove a SizeGroup from the project. Note that this doesn't
        remove the widgets from the sizegroup.

        @param sizegroup: the sizegroup to remove
        @type sizegroup: gazpacho.sizegroup.GSizeGroup
        """
        self.sizegroups.remove(sizegroup)
        self.emit('remove-sizegroup', sizegroup)

    def add_action_group(self, action_group):
        self.uim.add_action_group(action_group)

        self.emit('add-action', action_group)

    def remove_action_group(self, action_group):
        self.uim.remove_action_group(action_group)
        self.emit('remove-action', action_group)

    def change_action_name(self, action):
        self.emit('action-name-changed', action)

    def set_new_widget_name(self, widget):
        """Create a new name based on type."""
        if not isinstance(widget, gtk.Widget):
            raise TypeError("widget must be a gtk.Widget, not %r" % widget)

        adapter = widget_registry.get_by_type(widget)
        base_name = adapter.generic_name
        i = 0
        while True:
            i += 1
            name = '%s%d' % (base_name, i)
            if not name in self._widgets:
                break

        widget.set_name(name)
        return name

    def save(self, path):
        self.path = path
        self.name = os.path.basename(path)

        xw = XMLWriter(project=self)
        widgets = self._widgets.values()
        widgets.sort(lambda x, y: cmp(x.name, y.name))
        retval = xw.write(path, widgets, self.sizegroups, self.uim,
                          self._domain)

        self.changed = False
        self.undo_stack.mark_saved()
        return retval

    def serialize(self):
        xw = XMLWriter()
        widgets = self._widgets.values()
        widgets.sort(lambda x, y: cmp(x.name, y.name))
        return xw.serialize_widgets(widgets, self.sizegroups, self.uim)

type_register(Project)


class UndoRedoStack(gobject.GObject):
    """Class representing an undo/redo stack."""

    gsignal('changed')

    def __init__(self):
        gobject.GObject.__init__(self)

        #  A stack with the last executed commands
        self._commands = []

        #  Points to current undo command
        self._current_undo_command = -1

        # The possition marked when the project was last saved
        self._saved_position = -1

    def mark_saved(self):
        """Mark that the project has been saved at the current
        possition.
        """
        self._saved_position = self._current_undo_command

    def on_saved(self):
        """Check whether we are on the possition that has been marked
        as changed or not.

        @return: True if we're on the saved possition otherwise False
        @rtype: bool
        """
        return self._saved_position == self._current_undo_command

    def has_undo(self):
        """Check if there are any commands in the undo stack."""
        return self._current_undo_command != -1

    def has_redo(self):
        """Check if there are any commands in the redo stack."""
        return self._current_undo_command + 1 != len(self._commands)

    def get_undo_info(self):
        """Get the current undo command description."""
        if self.has_undo():
            return self._commands[self._current_undo_command].description
        return None

    def get_redo_info(self):
        """Get the current redo command description."""
        if self.has_redo():
            return self._commands[self._current_undo_command + 1].description
        return None

    def pop_undo(self):
        """Return the current undo command and move it to the redo stack."""
        if self.has_undo():
            cmd = self._commands[self._current_undo_command]
            self._current_undo_command -= 1
            self.emit('changed')
            return cmd
        return None

    def pop_redo(self):
        """Return the current redo command and move it to the undo stack."""
        if self.has_redo():
            cmd =  self._commands[self._current_undo_command + 1]
            self._current_undo_command += 1
            self.emit('changed')
            return cmd
        return None

    def push_undo(self, command):
        """Put the command in the project command stack
        It tries to collapse the command with the previous command
        """
        # If there are no "redo" items, and the last "undo" item unifies with
        # us, then we collapse the two items in one and we're done
        if self.has_undo() and not self.has_redo():
            cmd = self._commands[self._current_undo_command]
            if not self.on_saved() and cmd.unifies(command):
                cmd.collapse(command)
                self.emit('changed')
                return

        # We should now free all the 'redo' items
        self._commands = self._commands[:self._current_undo_command + 1]

        # and then push the new undo item
        self._commands.append(command)
        self._current_undo_command += 1

        self.emit('changed')

    def get_undo_commands(self):
        """Get a list of all undo commands."""
        return self._commands[:self._current_undo_command + 1]

    def get_redo_commands(self):
        """Get a list of all redo commands."""
        return self._commands[self._current_undo_command + 1:]

type_register(UndoRedoStack)

def refresh_selected_nodes(widget):
    """ Invalidates the portion of the window covered by the selection
    nodes for the given widget """

    if not widget.window:
        return

    if widget.get_parent():
        window = widget.get_parent_window()
    else:
        window = widget.window
    window.invalidate_rect(widget.allocation, True)

class WidgetSelection(gobject.GObject):
    """
    The widget selection keeps track of which widgets are currently
    selected and provide means to manipulate the selection.

    When the selection is modified a 'selection-changed' signal will
    be emitted.
    """

    gsignal('selection_changed')

    def __init__(self):
        gobject.GObject.__init__(self)
        self._selection = []

    def selection_changed(self):
        """
        Emit a selection-changed signal.
        """
        self.emit('selection_changed')

    def clear(self, emit_signal=True):
        """
        Clear the selection. This might emit a selection-changed
        signal.

        @param emit_signal: if the signal should be emitted
        @type emit_signal: bool
        """
        if not self._selection:
            return

        for widget in self._selection:
            refresh_selected_nodes(widget)

        self._selection = []

        if emit_signal:
            self.selection_changed()

    def remove(self, widget, emit_signal=True):
        """
        Remove the widget from the current selection. This might emit
        a selection-changed signal.

        @param widget: the widget to remove
        @type widget: gtk.Widget
        @param emit_signal: if the signal should be emitted
        @type emit_signal: bool
        """
        if widget not in self._selection:
            return

        refresh_selected_nodes(widget)

        self._selection.remove(widget)
        if emit_signal:
            self.selection_changed()

    def add(self, widget, emit_signal=True):
        """
        Add the widget to the selection. This might emit a
        selection-changed signal.

        @param widget: the widget to add
        @type widget: gtk.Widget
        @param emit_signal: if the signal should be emitted
        @type emit_signal: bool
        """
        if widget in self._selection:
            return

        self._selection.insert(0, widget)
        if emit_signal:
            self.selection_changed()

        refresh_selected_nodes(widget)

    def set(self, widget, emit_signal=True):
        """
        Clear the selection and add the specified widget. This might
        emit a selection-changed signal.

        @param widget: the widget to add
        @type widget: gtk.Widget
        @param emit_signal: if the signal should be emitted
        @type emit_signal: bool
        """
        self.clear(False)
        self.add(widget, emit_signal)

    def toggle(self, widget, emit_signal=True):
        """
        The the widget is in the selection it will be removed
        otherwise it will be added.

        @param widget: the widget to add or remove
        @type widget: gtk.Widget
        @param emit_signal: if the signal should be emitted
        @type emit_signal: bool
        """
        if widget in self._selection:
            self.remove(widget, emit_signal)
        else:
            self.add(widget, emit_signal)

    def circle(self, leaf_widget):
        """
        Select the parent of the selected widget. If the selected
        widget is a toplevel widget or there isn't a selected widget
        in the current branch of the tree, select the leaf widget.

        @param leaf_widget: the leaf widget
        @type leaf_widget: gtk.Widget
        """
        parent_gadget = util.get_parent(leaf_widget)

        # If the leaf widget doesn't have a parent select it.
        if not parent_gadget:
            self.set(leaf_widget)
            return

        # If there is no or multiple selections, select the leaf
        # widget. Note that it's not sure that the leaf widget has a
        # gadget (if it' a placeholder).
        if len(self._selection) != 1:
            self.set(leaf_widget)
            return

        selected = self._selection[0]

        # If the leaf widget is selected, select its parent
        if leaf_widget is selected:
            self.set(parent_gadget.widget)
            return

        # Circle through the tree
        new_selection = leaf_widget
        while parent_gadget:
            if parent_gadget.widget is selected:
                # Choose the leaf if selected is toplevel
                if parent_gadget.is_toplevel():
                    new_selection = leaf_widget
                # otherwise choose the parent
                else:
                    new_selection = parent_gadget.get_parent().widget
                break
            parent_gadget = parent_gadget.get_parent()
        self.set(new_selection)


    def __iter__(self):
        return iter(self._selection)

    def __len__(self):
        return len(self._selection)

    def __contains__(self, item):
        return item in self._selection

    def __getitem__(self, key):
        return self._selection[key]

type_register(WidgetSelection)
