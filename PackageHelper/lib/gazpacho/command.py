# Copyright (C) 2004,2005 by SICEm S.L. and Imendio AB
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

import gtk
import gobject
from kiwi.component import get_utility

from gazpacho import util
from gazpacho.app.bars import bar_manager
from gazpacho.commandmanager import command_manager, COMMAND_CUT, COMMAND_PASTE
from gazpacho.dndhandlers import DND_POS_TOP, DND_POS_BOTTOM, DND_POS_LEFT
from gazpacho.interfaces import IGazpachoApp
from gazpacho.placeholder import Placeholder
from gazpacho.widget import Gadget, load_gadget_from_widget
from gazpacho.widgetregistry import widget_registry

_ = lambda msg: gettext.dgettext('gazpacho', msg)

class Command(object):
    """A command is the minimum unit of undo/redoable actions.

    It has a description so the user can see it on the Undo/Redo
    menu items.

    Every Command subclass should implement the 'execute' method in
    the following way:
        - After a command is executed, if the execute method is called
        again, their effects will be undone.
        - If we keep calling the execute method, the action will
        be undone, then redone, then undone, etc...
        - To acomplish this every command constructor will probably
        need to gather more data that it may seems necessary.

    After you execute a command in the usual way you should put that
    command in the command stack of that project and that's what
    the push_undo method does. Otherwise no undo will be available.

    Some commands unifies themselves. This means that if you execute
    several commands of the same type one after the other, they will be
    treated as only one big command in terms of undo/redo. In other words,
    they will collapse. For example, every time you change a letter on a
    widget's name it is a command but all these commands unifies to one
    command so if you undo that all the name will be restored to the old one.
    """
    def __init__(self, description=None, ):
        self.description = description

    def __repr__(self):
        return self.description

    def execute(self):
        """ This is the main method of the Command class.
        Note that it does not have any arguments so all the
        necessary data should be provided in the constructor.
        """
        pass

    def undo(self):
        """Convenience method that just call execute"""
        self.execute()

    def redo(self):
        """Convenience method that just call redo"""
        self.execute()

    def unifies(self, other):
        """True if self unifies with 'other'
        Unifying means that both commands can be treated as they
        would be only one command
        """
        return False

    def collapse(self, other):
        """Combine self and 'other' to form only one command.
        'other' should unifies with self but this method does not
        check that.
        """
        return False

class GadgetCommand(Command):
    """
    This should be the super class of all commands that adds or
    removes a widget.

    When a widget is added or removed everything that depends on the
    widget has to be updated as well. This is true both for the
    specified widget and all of it's children. This is done through
    the following methods:

      - remove_gadget_dependencies
      - add_gadget_dependencies
    """

    def __init__(self, description=None):
        """
        Initialize the command.
        """
        Command.__init__(self, description)

        # List of sizegroup commands
        self._sizegroup_cmds = []

        # Mapping of widgets to ui definitions
        self._ui_defs = {}

        # Mapping of container to placeholder that should be replaced
        # with a ui widget
        self._ui_placeholders = {}

    def remove_gadget_dependencies(self, gadget):
        """
        Remove everything that depends on this widget.

        @param gadget: the widget
        @type gadget: gazpacho.widget.Gadget
        """
        self._remove_gadget_dependencies(gadget, None)

    def _remove_gadget_dependencies(self, gadget, parent):
        """
        Remove everything that depends on this widget. This method
        will also recurse through all the children of the widget and
        remove their dependencies as well.

        @param gadget: the widget
        @type gadget: gazpacho.widget.Gadget
        @param parent: the parent of this widget or None if it's the start widget
        @type parent: gazpacho.widget.Gadget
        """
        widget = gadget.widget

        if isinstance(widget, gtk.Container):
            for gtk_child in widget.get_children():
                child = Gadget.from_widget(gtk_child)
                if child:
                    self._remove_gadget_dependencies(child, gadget)

        # Remove the dependencies
        self._remove_ui_defs(gadget, parent)
        self._remove_gadget_from_sizegroup(gadget)

    def _remove_ui_defs(self, gadget, parent):
        """
        Remove the widget's ui definitions from the ui manager.

        @param gadget: the widget
        @type gadget: gazpacho.widget.Gadget
        @param parent: the parent of this widget or None if it's
                       the start widget
        @type parent: gazpacho.widget.Gadget
        """
        if isinstance(gadget.widget, (gtk.Toolbar, gtk.MenuBar)):
            uim = gadget.project.uim
            ui_defs = uim.get_ui(gadget)
            if ui_defs:
                self._ui_defs[gadget] = dict(ui_defs)
                uim.remove_gadget(gadget)

            if parent:
                placeholder = Placeholder()
                Gadget.replace(gadget.widget, placeholder , parent)
                self._ui_placeholders[parent] = placeholder

    def _remove_gadget_from_sizegroup(self, gadget):
        project = gadget.project
        for sizegroup in project.sizegroups:
            if not sizegroup.has_gadget(gadget):
                continue

            cmd = CommandAddRemoveSizeGroupGadgets(sizegroup,
                                                   [gadget],
                                                   project, False)
            cmd.execute()
            self._sizegroup_cmds.append(cmd)

    def add_gadget_dependencies(self, gadget):
        """
        Add everything that depends on this widget or any of it's
        descendants. Note that this might replace the widget's
        gtk-widget so make sure you refer to the correct one
        afterward.

        @param gadget: the widget
        @type gadget: gazpacho.widget.Gadget
        """
        self._add_widgets_to_sizegroups()
        self._add_ui_defs(gadget)

    def _add_ui_defs(self, gadget):
        """
        Add the widget's ui definitions to the ui manager.

        @param gadget: the widget
        @type gadget: gazpacho.widget.Gadget
        """
        for gadget, ui_defs in self._ui_defs.iteritems():
            # Adding the widget to uim might replace the gtk-widget
            # connected to the widget instance, just a reminder
            gadget.project.uim.add_gadget(gadget, ui_defs)
        self._ui_defs = {}

        for parent, placeholder in self._ui_placeholders.iteritems():
            Gadget.replace(placeholder, gadget.widget, parent)

        self._ui_placeholders = {}

    def _add_widgets_to_sizegroups(self):
        """
        Add the widget to any sizegroups that it should be part of.
        """
        for cmd in self._sizegroup_cmds:
            cmd.execute()

        self._sizegroup_cmds = []

class CommandCreateDelete(GadgetCommand):
    def __init__(self, gadget, placeholder, parent, create,
                 description=None):
        GadgetCommand.__init__(self, description)

        self._gadget = gadget
        self._placeholder = placeholder
        self._parent = parent
        self._create = create
        self._initial_creation = create

    def _create_execute(self):
        gadget = self._gadget

        # Note that updating the dependencies might replace the
        # widget's gtk-widget so we need to make sure we refer to the
        # correct one afterward.
        self.add_gadget_dependencies(gadget)

        widget = gadget.widget

        if isinstance(widget, gtk.Window):

            # make window management easier by making created windows
            # transient for the editor window
            widget.set_transient_for(get_utility(IGazpachoApp).get_window())

            # Show windows earlier so we can restore the window-position
            # before the property editor is shown
            old_pos = widget.get_property('window-position')
            widget.set_position(gtk.WIN_POS_CENTER_ON_PARENT)
        else:
            if self._placeholder is None:
                for child in self._parent.widget.get_children():
                    if isinstance(child, Placeholder):
                        self._placeholder = child
                        break
            Gadget.replace(self._placeholder, widget, self._parent)

        self._gadget.project.add_widget(widget)
        self._gadget.select()

        widget.show_all()
        if isinstance(widget, gtk.Window):
            widget.set_position(old_pos)

            # we have to attach the accelerators groups so key shortcuts
            # keep working when this window has the focus. Only do
            # this the first time when creating a window, not when
            # redoing the creation since the accel group is already
            # set by then
            if self._initial_creation:
                widget.add_accel_group(bar_manager.get_accel_group())
                self._initial_creation = False

    def _delete_execute(self):
        gadget = self._gadget

        if self._parent:
            if self._placeholder is None:
                self._placeholder = Placeholder()

            Gadget.replace(gadget.widget,
                           self._placeholder, self._parent)

        gadget.widget.hide()
        gadget.project.remove_widget(gadget.widget)

        self.remove_gadget_dependencies(gadget)

    def execute(self):
        if self._create:
            self._create_execute()
        else:
            self._delete_execute()

        self._create = not self._create
command_manager.register('create', CommandCreateDelete)
command_manager.register('delete', CommandCreateDelete)

class CommandDeletePlaceholder(Command):
    def __init__(self, placeholder, parent, description=None):
        Command.__init__(self, description)

        self._project = parent.project
        self._placeholder = placeholder
        self._gtk_parent = parent.widget
        self._create = False

        children = self._gtk_parent.get_children()
        self._pos = children.index(placeholder)

    def _create_execute(self):
        """
        Insert the placeholder at self._pos.
        """
        self._gtk_parent.add(self._placeholder)
        self._gtk_parent.reorder_child(self._placeholder, self._pos)

    def _delete_execute(self):
        """
        Remove the placeholder.
        """
        self._gtk_parent.remove(self._placeholder)
        self._project.selection.clear()

    def execute(self):
        if self._create:
            self._create_execute()
        else:
            self._delete_execute()

        self._create = not self._create
command_manager.register('delete-placeholder', CommandDeletePlaceholder)

class CommandInsertPlaceholder(Command):
    def __init__(self, box, pos, description=None):
        Command.__init__(self, description)

        self._box = box
        self._pos = pos
        self._placeholder = None
        self._insert = True


    def _insert_execute(self):
        # create a placeholder and insert it at self._pos
        self._placeholder = Placeholder()
        self._box.widget.add(self._placeholder)
        self._box.widget.reorder_child(self._placeholder, self._pos)

    def _delete_execute(self):
        self._placeholder.destroy()
        self._placeholder = None

    def execute(self):
        if self._insert:
            self._insert_execute()
        else:
            self._delete_execute()

        self._insert = not self._insert
command_manager.register('insert-placeholder', CommandInsertPlaceholder)

class CommandSetProperty(Command):
    def __init__(self,  property, value, description=None):
        Command.__init__(self, description)
        self._property = property
        self._value = value

    def execute(self):
        new_value = self._value
        # store the current value for undo
        self._value = self._property.value
        self._property.set(new_value)

        # TODO: this should not be needed
        # if the property is the name, we explicitily set the name of the
        # gadget to trigger the notify signal so several parts of the
        # interface get updated
        if self._property.name == 'name':
            self._property.object.notify('name')

    def unifies(self, other):
        if isinstance(other, CommandSetProperty):
            return self._property == other._property
        return False

    def collapse(self, other):
        self.description = other.description
        other.description = None
command_manager.register('set-property', CommandSetProperty)

class CommandSetTranslatableProperty(Command):
    def __init__(self,  property, value, comment, translatable, has_context,
                 description=None):
        Command.__init__(self, description)

        self._property = property
        self._value = value
        self._comment = comment
        self._translatable = translatable
        self._has_context = has_context

    def execute(self):
        new_value = self._value
        new_comment = self._comment
        new_translatable = self._translatable
        new_has_context = self._has_context

        # store the current value for undo
        self._value = self._property.value
        self._comment = self._property.i18n_comment
        self._translatable = self._property.translatable
        self._has_context = self._property.has_i18n_context

        self._property.set(new_value)
        self._property.translatable = new_translatable
        self._property.i18n_comment = new_comment
        self._property.has_i18n_context = new_has_context

    def unifies(self, other):
        return False

    def collapse(self, other):
        return False
command_manager.register('set-translatable',
                         CommandSetTranslatableProperty)

class CommandAddRemoveSignal(Command):
    def __init__(self, add, signal, gadget, description=None):
        Command.__init__(self, description)
        self._add = add
        self._signal = signal
        self._gadget = gadget

    def execute(self):
        if self._add:
            self._gadget.add_signal_handler(self._signal)
        else:
            self._gadget.remove_signal_handler(self._signal)

        self._add = not self._add
command_manager.register('add-signal', CommandAddRemoveSignal)

class CommandChangeSignal(Command):
    def __init__(self, gadget, old_signal_handler, new_signal_handler,
                 description=None):
        Command.__init__(self, description)
        self._gadget = gadget
        self._old_handler = old_signal_handler
        self._new_handler = new_signal_handler

    def execute(self):
        self._gadget.change_signal_handler(self._old_handler,
                                                    self._new_handler)
        self._old_handler, self._new_handler = (self._new_handler,
                                                self._old_handler)

command_manager.register('change-signal', CommandChangeSignal)

class CommandCutPaste(GadgetCommand):

    def __init__(self, gadget, project, placeholder, operation,
                 description=None, ):
        GadgetCommand.__init__(self, description)

        self._project = project
        self._placeholder = placeholder
        self._operation = operation
        self._gadget = gadget

    def execute(self):
        if self._operation == COMMAND_CUT:
            self._execute_cut()
            self._operation = COMMAND_PASTE
        else:
            gadget = self._execute_paste()
            self._operation = COMMAND_CUT
            return gadget

    def _execute_cut(self):
        gadget = self._gadget

        if not gadget.is_toplevel():
            parent = gadget.get_parent()

            if not self._placeholder:
                self._placeholder = Placeholder()

            Gadget.replace(gadget.widget,
                           self._placeholder, parent)

        gadget.widget.hide()
        gadget.project.remove_widget(gadget.widget)

        self.remove_gadget_dependencies(gadget)

    def _execute_paste(self):
        # Note that updating the dependencies might replace the
        # widget's gtk-widget so we need to make sure we refer to the
        # correct one afterward.
        self.add_gadget_dependencies(self._gadget)

        if self._gadget.is_toplevel():
            project = self._project
        else:
            parent = util.get_parent(self._placeholder)
            project = parent.project
            Gadget.replace(self._placeholder,
                           self._gadget.widget,
                           parent)

        project.add_widget(self._gadget.widget, new_name=True)
        self._gadget.select()

        self._gadget.widget.show_all()

        # We need to store the project of a toplevel widget to use
        # when undoing the cut.
        self._project = project

        return self._gadget
command_manager.register('cut-paste', CommandCutPaste)

class CommandAddRemoveAction(Command):
    def __init__(self, parent, gact, add, description=None):
        Command.__init__(self, description)

        self.add = add
        self.gact = gact
        self.parent = parent

    def execute(self):
        if self.add:
            self._add_execute()
        else:
            self._remove_execute()

        self.add = not self.add

    def _add_execute(self):
        self.parent.add_action(self.gact)

    def _remove_execute(self):
        self.parent.remove_action(self.gact)
command_manager.register('add-action', CommandAddRemoveAction)

class CommandEditAction(Command):
    def __init__(self, gact, new_values, project, description=None):
        Command.__init__(self, description)

        self.new_values = new_values
        self.gact = gact
        self.project = project

    def execute(self):
        old_values = {
            'name' : self.gact.name,
            'label': self.gact.label,
            'short_label': self.gact.short_label,
            'is_important': self.gact.is_important,
            'stock_id': self.gact.stock_id,
            'tooltip': self.gact.tooltip,
            'accelerator': self.gact.accelerator,
            'callback': self.gact.callback,
            }
        self.gact.name = self.new_values['name']
        self.gact.label = self.new_values['label']
        self.gact.short_label = self.new_values['short_label']
        self.gact.is_important = self.new_values['is_important']
        self.gact.stock_id = self.new_values['stock_id']
        self.gact.tooltip = self.new_values['tooltip']
        self.gact.accelerator = self.new_values['accelerator']
        self.gact.callback = self.new_values['callback']
        self.gact.parent.update_action(self.gact, old_values['name'])
        self.new_values = old_values
        self.project.change_action_name(self.gact)
command_manager.register('edit-action', CommandEditAction)

class CommandAddRemoveActionGroup(Command):
    def __init__(self, gaction_group, project, add, description=None):
        Command.__init__(self, description)

        self.add = add
        self.project = project
        self.gaction_group = gaction_group
        self.gactions = self.gaction_group.get_actions()

    def execute(self):
        if self.add:
            self._add_execute()
        else:
            self._remove_execute()

        self.add = not self.add

    def _add_execute(self):
        self.project.add_action_group(self.gaction_group)
        for gaction in self.gactions:
            self.gaction_group.add_action(gaction)

    def _remove_execute(self):
        self.project.remove_action_group(self.gaction_group)
command_manager.register('add-action-group',
                         CommandAddRemoveActionGroup)
command_manager.register('remove-action-group',
                         CommandAddRemoveActionGroup)

class CommandEditActionGroup(Command):
    def __init__(self, gaction_group, new_name, project, description=None ):
        Command.__init__(self, description)

        self.new_name = new_name
        self.gaction_group = gaction_group
        self.project = project

    def execute(self):
        old_name = self.gaction_group.name
        self.gaction_group.name = self.new_name
        self.new_name = old_name
        self.project.change_action_name(self.gaction_group)
command_manager.register('edit-action-group', CommandEditActionGroup)

class CommandSetButtonContents(Command):
    def __init__(self, gadget, stock_id, notext, label, image_path, position,
                 icon_size, child_name, description=None):
        Command.__init__(self, description)

        self.gadget = gadget
        self.stock_id = stock_id
        self.notext = notext
        self.label = label
        self.image_path = image_path
        self.position = position
        self.icon_size = icon_size
        self.child_name = child_name

    def execute(self):
        widget = self.gadget
        button = self.gadget.widget
        state = util.get_button_state(button)
        use_stock = widget.get_prop('use-stock')
        label = widget.get_prop('label')
        self._clear_button(button)

        if self.stock_id:
            # stock button

            if self.notext:
                image = gtk.Image()
                image.set_from_stock(self.stock_id, self.icon_size)
                image.show()
                button.add(image)
            else:
                use_stock.set(True)
                label.set(self.stock_id)

        else:
            # custom button. 3 cases:
            # 1) only text, 2) only image or 3) image and text
            if self.label and not self.image_path:
                # only text
                label.set(self.label)
            elif not self.label and self.image_path:
                # only image
                image = gtk.Image()
                image.set_from_file(self.image_path)
                image.set_data('image-file-name', self.image_path)
                image.show()
                button.add(image)
            elif self.label and self.image_path:
                # image and text
                align = gtk.Alignment(0.5, 0.5, 1.0, 1.0)
                if self.position in (gtk.POS_LEFT, gtk.POS_RIGHT):
                    box = gtk.HBox()
                else:
                    box = gtk.VBox()
                align.add(box)
                image = gtk.Image()
                image.set_from_file(self.image_path)
                image.set_data('image-file-name', self.image_path)
                label = gtk.Label(self.label)
                if '_' in self.label:
                    label.set_use_underline(True)

                if self.position in (gtk.POS_LEFT, gtk.POS_TOP):
                    box.pack_start(image)
                    box.pack_start(label)
                else:
                    box.pack_start(label)
                    box.pack_start(image)

                align.show_all()
                button.add(align)

        if button.child:
            if not self.child_name:
                project = self.gadget.project
                button.child.set_name('')
                load_gadget_from_widget(button, project)
                if not button.child.get_name():
                    project.set_new_widget_name(button.child)
                project.add_hidden_widget(button.child)
            else:
                button.child.set_name(self.child_name)

        # save the state for undoing purposes
        (self.stock_id, self.notext, self.label,
         self.image_path, self.position, self.icon_size,
         self.child_name) = state

    def _clear_button(self, button):
        "Clear the button and set default values for its properties"
        button.set_use_stock(False)
        button.set_use_underline(False)
        button.set_label('')

        child = button.get_child()
        if child:
            button.remove(child)
command_manager.register('button', CommandSetButtonContents)

class CommandDragDrop(Command):
    """Command for executing a drag and drop action. This will move
    the widget and cannot be used to drag widgets between programs.
    """

    def __init__(self, source_gadget, target_placeholder, description=None):
        """
        Initialize the command.

        @param source_gadget: the source widget
        @type source_gadget: gazpacho.widget.Gadget
        @param target_placeholder: the target placeholder
        @type target_placeholder: gazpacho.placeholder.Placeholder
        """
        Command.__init__(self, description)

        self._undo = False
        self._source_placeholder = None
        self._target_placeholder = target_placeholder
        self._source = source_gadget

    def execute(self):
        if self._undo:
            self._remove_widget(self._source, self._target_placeholder)
            self._add_widget(self._source, self._source_placeholder)

        else:
            if not self._source_placeholder:
                self._source_placeholder = Placeholder()
            self._remove_widget(self._source, self._source_placeholder)
            self._add_widget(self._source, self._target_placeholder)

        self._undo = not self._undo

    def _remove_widget(self, gadget, placeholder):
        """
        Remove the widget.

        @param gadget: the widget that should be removed
        @type gadget: gazpacho.widget.Gadget
        @param placeholder: the new placeholder
        @type placeholder: gazpacho.placeholder.Placeholder
        """
        parent = gadget.get_parent()
        Gadget.replace(gadget.widget,
                       placeholder,
                       parent)

        gadget.widget.hide()
        gadget.project.remove_widget(gadget.widget)

    def _add_widget(self, gadget, placeholder):
        """
        Add the widget.

        @param gadget: the widget that should be added
        @type gadget: gazpacho.widget.Gadget
        @param placeholder: the old placeholder
        @type placeholder: gazpacho.placeholder.Placeholder
        """
        parent = util.get_parent(placeholder)
        project = parent.project
        Gadget.replace(placeholder,
                       gadget.widget,
                       parent)

        project.add_widget(gadget.widget)
        gadget.select()

        gadget.widget.show_all()
command_manager.register('drag-drop', CommandDragDrop)

class CommandAddRemoveSizeGroupGadgets(Command):
    """
    Command for adding and removing sizegroup gadgets. When adding
    gadgets to an empty sizegroup the sizegroup will be added to the
    project. When the last gadgets is removed from a sizegroup the
    sizegroup will be removed as well.
    """

    def __init__(self, sizegroup, gadgets, project, add, description=None):
        """
        Initialize the command.

        @param sizegroup: the sizegroup that the gadgets belong to
        @type sizegroup: gazpacho.sizegroup.GSizeGroup
        @param gadgets: the gadgets that should be added or removed
        @type gadgets: list (of gazpacho.widget.Gadget)
        @param project: the project that the sizegroup belongs to
        @type project: gazpacho.project.Project
        @param add: True if the gadgets should be added
        @type add: bool
        """
        Command.__init__(self, description)

        self._sizegroup = sizegroup
        self._gadgets = gadgets
        self._project = project
        self._add = add

    def execute(self):
        if self._add:
            self._execute_add()
        else:
            self._execute_remove()

        self._add = not self._add

    def _execute_add(self):
        """
        Add the gadgets to the sizegroup. This might mean that the
        sizegroup will be added as well.
        """
        if self._sizegroup.is_empty():
            self._project.add_sizegroup(self._sizegroup)

        self._sizegroup.add_gadgets(self._gadgets)

    def _execute_remove(self):
        """
        Remove the gadgets from the sizegroup. This might cause the
        sizegroup to be removed as well.
        """
        self._sizegroup.remove_gadgets(self._gadgets)

        if self._sizegroup.is_empty():
            self._project.remove_sizegroup(self._sizegroup)
command_manager.register('sizegroup', CommandAddRemoveSizeGroupGadgets)

class CommandStackView(gtk.ScrolledWindow):
    """This class is just a little TreeView that knows how
    to show the command stack of a project.
    It shows a plain list of all the commands performed by
    the user and also it mark the current command that
    would be redone if the user wanted so.
    Older commands are under newer commands on the list.
    """
    def __init__(self):
        gtk.ScrolledWindow.__init__(self)
        self._project = None

        self._model = gtk.ListStore(bool, str)
        self._treeview = gtk.TreeView(self._model)
        self._treeview.set_headers_visible(False)

        column = gtk.TreeViewColumn()
        renderer1 = gtk.CellRendererPixbuf()
        column.pack_start(renderer1, expand=False)
        column.set_cell_data_func(renderer1, self._draw_redo_position)

        renderer2 = gtk.CellRendererText()
        column.pack_start(renderer2, expand=True)
        column.add_attribute(renderer2, 'text', 1)

        self._treeview.append_column(column)

        self.add(self._treeview)

    def set_project(self, project):
        self._project = project
        self.update()

    def update(self):
        self._model.clear()
        if self._project is None:
            return

        undos = self._project.undo_stack.get_undo_commands()
        if undos:
            for cmd in undos[:-1]:
                self._model.insert(0, (False, cmd.description))
            self._model.insert(0, (True, undos[-1].description))

        for cmd in self._project.undo_stack.get_redo_commands():
            self._model.insert(0, (False, cmd.description))

    def _draw_redo_position(self, column, cell, model, iter):
        is_the_one = model[iter][0]

        if is_the_one:
            stock_id = gtk.STOCK_JUMP_TO
        else:
            stock_id = None

        cell.set_property('stock-id', stock_id)

gobject.type_register(CommandStackView)


class ExtendGadgetCommand(Command):
    """
    Command for replacing a target widget with a box containing a copy
    of both the target and the source.
    """

    def __init__(self, source_gadget, target_gadget, location,
                 description=None):
        """
        Initialize the command. Note that the source_gadget has to be
        a new widget that is not already in use in the project.

        @param source_gadget: the widget to add
        @type source_gadget: L{gazpacho.widget.Gadget}
        @param target_gadget: the widget to replace
        @type target_gadget: L{gazpacho.widget.Gadget}
        @param location: Where to put the source in relation to the target
        @type location: (constant value)
        """
        Command.__init__(self, description)

        self._project = target_gadget.project
        self._gtk_source = source_gadget.widget
        self._gtk_target = target_gadget.widget

        # Create the box with a copy of the target
        target_copy = target_gadget.copy(keep_name=True)

        self._gtk_box = self._create_box(source_gadget.widget,
                                         target_copy.widget, location)


    def _create_box(self, gtk_source, gtk_target, location):
        """
        Create a Box containing the widgets.

        @param gtk_source: the gtk  widget to add
        @type gtk_source: gtk.Gadget
        @param gtk_target: the gtk widget to replace
        @type gtk_target: gtk.Gadget
        @param location: Where to put the source in relation to the target
        @type location: (constant value)
        """
        # Create a Box with size 2
        if location in [DND_POS_TOP, DND_POS_BOTTOM]:
            box_type = 'GtkVBox'
        else:
            box_type = 'GtkHBox'
        adaptor = widget_registry.get_by_name(box_type)
        box_gadget = Gadget(adaptor, self._project)
        box_gadget.create_widget(interactive=False)
        box_gadget.get_prop('size').set(2)

        # Add the source and target widgets
        children = box_gadget.widget.get_children()
        if location in [DND_POS_TOP, DND_POS_LEFT]:
            source_placeholder, target_placeholder = children[0], children[1]
        else:
            source_placeholder, target_placeholder = children[1], children[0]

        Gadget.replace(source_placeholder, gtk_source, box_gadget)
        Gadget.replace(target_placeholder, gtk_target, box_gadget)

        return box_gadget.widget

    def _replace(self, target, source):
        """
        Replace the target widget with the source widget.

        @param target: the target gtk widget
        @type target: gtk.Gadget
        @param source: the source gtk widget
        @type source: gtk.Gadget
        """
        parent = util.get_parent(target)
        Gadget.replace(target, source, parent)

        # Remove old widget
        target.hide()
        self._project.remove_widget(target)

        # Add new widget
        self._project.add_widget(source)
        source.show_all()

    def add_box(self):
        """
        Replace the original target widget with the box.
        """
        self._replace(self._gtk_target, self._gtk_box)
        self._project.selection.set(self._gtk_source)

    def remove_box(self):
        """
        Replace the box with the original target widget.
        """
        self._replace(self._gtk_box, self._gtk_target)
        self._project.selection.set(self._gtk_target)

class DragExtendCommand(ExtendGadgetCommand):
    """
    Command for replacing a target widget with a box containing a copy
    of both the target and the source.
    """

    def __init__(self, source_gadget, target_gadget, location, keep_source,
                 description=None):
        """
        Initialize the command.

        @param source_gadget: the widget to add
        @type source_gadget: L{gazpacho.widget.Gadget}
        @param target_gadget: the widget to replace
        @type target_gadget: L{gazpacho.widget.Gadget}
        @param location: Where to put the source in relation to the target
        @type location: (constant value)
        @param keep_source: if true we should not remove the source
        widget, if false we should.
        @type keep_source: bool
        """
        source_copy = source_gadget.copy(target_gadget.project,
                                         not keep_source)
        ExtendGadgetCommand.__init__(self, source_copy, target_gadget, location,
                                     description)

        self._undo = False
        self._remove_cmd = None

        # Reuse the Cut command for removing the widget
        if not keep_source:
            self._remove_cmd = CommandCutPaste(source_gadget,
                                               source_gadget.project,
                                               None,
                                               COMMAND_CUT,
                                               None)

    def execute(self):
        """
        Execute the command.
        """
        if self._undo:
            self.remove_box()

        if self._remove_cmd:
            self._remove_cmd.execute()

        if not self._undo:
            self.add_box()

        self._undo = not self._undo

command_manager.register('drag-extend', DragExtendCommand)


class CreateExtendCommand(ExtendGadgetCommand):
    """
    Command for replacing a target widget with a box containing a copy
    of both the target and the source.
    """

    def __init__(self, source_gadget, target_gadget, location,
                 description=None):
        """
        Initialize the command.

        @param source_gadget: the widget to add
        @type source_gadget: L{gazpacho.widget.Gadget}
        @param target_gadget: the widget to replace
        @type target_gadget: L{gazpacho.widget.Gadget}
        @param location: Where to put the source in relation to the target
        @type location: (constant value)
        @param keep_source: if true we should not remove the source
        widget, if false we should.
        @type keep_source: bool
        """
        ExtendGadgetCommand.__init__(self, source_gadget, target_gadget,
                                     location, description)
        self._undo = False

    def execute(self):
        """
        Execute the command.
        """
        if self._undo:
            self.remove_box()

        if not self._undo:
            self.add_box()

        self._undo = not self._undo

command_manager.register('create-extend', CreateExtendCommand)


class AppendGadgetCommand(Command):
    """
    Command for adding a widget to a box. This command isn't inteded
    to be used directly but to be subclasses by other commands.
    """

    def __init__(self, source_gadget, box, pos, description=None):
        """
        Initialize the command. Note that the source_gadget has to be
        a new widget that is not already in use in the project.

        @param source_gadget: the widget that is to be inserted
        @type source_gadget: L{gazpacho.widget.Gadget}
        @param box: the box into which the widget should be inserted
        @type box: L{gazpacho.widget.Gadget}
        @param pos: the position where the widget will be inserted
        @type pos: int
        """
        Command.__init__(self, description)

        self._box = box.widget
        self._pos = pos
        self._source = source_gadget.widget
        self._project = box.project


    def insert_execute(self):
        """
        Insert the widget into the box.
        """
        self._box.add(self._source)
        self._box.reorder_child(self._source, self._pos)

        self._project.add_widget(self._source)
        self._project.selection.set(self._source)
        self._source.show_all()

    def remove_execute(self):
        """
        Remove the widget from the box.
        """
        self._box.remove(self._source)
        self._source.hide()
        self._project.remove_widget(self._source)

class DragAppendCommand(AppendGadgetCommand):
    """
    Append a copy of an existing widget to a box. It's optional to
    remove the source widget as well.
    """

    def __init__(self, source_gadget, box, pos, keep_source, description=None):
        """
        Initialize the command.

        @param source_gadget:
        @type source_gadget: L{gazpacho.widget.Gadget}
        @param box: the box into which the widget should be inserted
        @type box: L{gazpacho.widget.Gadget}
        @param pos: the position where the widget will be inserted
        @type pos: int
        """
        # We append a copy of the widget
        source_copy = source_gadget.copy(box.project, not keep_source)
        AppendGadgetCommand.__init__(self, source_copy, box, pos, description)

        self._undo = False

        # Reuse the Cut command for removing the widget
        self._remove_cmd = None
        if not keep_source:
            self._remove_cmd = CommandCutPaste(source_gadget,
                                               source_gadget.project,
                                               None,
                                               COMMAND_CUT,
                                               None)

    def execute(self):
        """
        Execute the command.
        """
        if self._undo:
            self.remove_execute()

        if self._remove_cmd:
            self._remove_cmd.execute()

        if not self._undo:
            self.insert_execute()

        self._undo = not self._undo

command_manager.register('drag-append', DragAppendCommand)


class CreateAppendCommand(AppendGadgetCommand):
    """
    Append a newly created widget to a box.
    """

    def __init__(self, source_gadget, box, pos, description=None):
        """
        Initialize the command.

        @param source_gadget:
        @type source_gadget: L{gazpacho.widget.Gadget}
        @param box: the box into which the widget should be inserted
        @type box: L{gazpacho.widget.Gadget}
        @param pos: the position where the widget will be inserted
        @type pos: int
        """
        AppendGadgetCommand.__init__(self, source_gadget, box, pos, description)
        self._undo = False

    def execute(self):
        """
        Execute the command.
        """
        if self._undo:
            self.remove_execute()
        else:
            self.insert_execute()

        self._undo = not self._undo

command_manager.register('create-append', CreateAppendCommand)
