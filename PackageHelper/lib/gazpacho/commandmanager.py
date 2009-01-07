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
from kiwi.ui.dialogs import warning

from gazpacho.clipboard import clipboard
from gazpacho.gaction import GAction, GActionGroup
from gazpacho.sizegroup import safe_to_add_gadgets
from gazpacho.util import get_parent

_ = lambda msg: gettext.dgettext('gazpacho', msg)

(COMMAND_CUT,
 COMMAND_PASTE) = range(2)

def create_gadget(adaptor, project, interactive):
    from gazpacho.widget import Gadget
    gadget = Gadget(adaptor, project)
    gadget.create_widget(interactive)
    return gadget

class CommandManager(object):
    """This class is the entry point accesing the commands.
    Every undoable action in Gazpacho is wrapped into a command.
    The stack of un/redoable actions is stored in the Project class
    so each project is independent on terms of undo/redo.

    The CommandManager knows how to perform the undo and redo actions.
    There is also a method for every type of command supported so
    you don't have to worry about creating the low level command
    objects.
    """
    def __init__(self):
        self._commands = {}

    def _get_command(self, command_name, *args, **kwargs):
        cmd_class = self._commands[command_name]
        return cmd_class(*args, **kwargs)

    def register(self, command_class, command):
        self._commands[command_class] = command

    def undo(self, project):
        """Undo the last command if there is such a command"""
        if project.undo_stack.has_undo():
            cmd = project.undo_stack.pop_undo()
            cmd.undo()

    def redo(self, project):
        """Redo the last undo command if there is such a command"""
        if project.undo_stack.has_redo():
            cmd = project.undo_stack.pop_redo()
            cmd.redo()

    #
    # for every possible command we have a method here
    #

    def delete(self, gadget):
        # internal children cannot be deleted. Should we notify the user?
        if gadget.internal_name is not None:
            return
        description = _("Delete %s") % gadget.name
        cmd = self._get_command('delete', gadget, None,
                                gadget.get_parent(), False,
                                description)
        cmd.execute()
        gadget.project.undo_stack.push_undo(cmd)

    def delete_selection(self, project):
        """
        Delete the widget in the selection.
        """
        # XXX I'm not sure if this should really be in the command
        # manager
        from gazpacho.placeholder import Placeholder
        from gazpacho.widget import Gadget
        assert len(project.selection) == 1

        widget = project.selection[0]
        gadget = Gadget.from_widget(widget)
        if gadget:
            command_manager.delete(gadget)

        elif (isinstance(widget, Placeholder) and widget.is_deletable()):
            command_manager.delete_placeholder(widget)


    def create(self, adaptor, placeholder, project, parent=None,
               interactive=True):
        """
        @return: the gadget that was created
        @rtype: gazpatcho.widget.Gadget
        """
        if placeholder:
            parent = get_parent(placeholder)
            if parent is None:
                return

        if project is None:
            project = parent.project

        gadget = create_gadget(adaptor, project, interactive)

        description = _("Create %s") % gadget.name
        cmd = self._get_command('create', gadget, placeholder,
                                parent, True, description)
        cmd.execute()
        gadget.project.undo_stack.push_undo(cmd)

        from gazpacho.palette import palette
        if not palette.persistent_mode:
            palette.unselect_widget()

        return gadget

    def delete_placeholder(self, placeholder):
        parent = get_parent(placeholder)
        if len(parent.widget.get_children()) == 1:
            return

        description = _("Delete placeholder")
        cmd = self._get_command('delete-placeholder', placeholder,
                                parent, description)
        cmd.execute()
        parent.project.undo_stack.push_undo(cmd)

    def box_insert_placeholder(self, box, pos, after):
        """
        Insert a placeholder before or after the specified position
        in the box.

        @param box: the box to insert the placeholder into
        @type box. gtk.Box
        @param pos: the possition we should insert into
        @type pos: int
        @param after: if we should insert the placeholder after the
                      specified position
        @type after: bool
        """
        if after:
            description = _("Insert after")
            pos += 1
        else:
            description = _("Insert before")

        cmd = self._get_command('insert-placeholder', box, pos, description)
        cmd.execute()
        box.project.undo_stack.push_undo(cmd)

    def set_property(self, prop, value):
        dsc = _('Setting %s of %s') % (prop.name, prop.get_object_name())
        cmd = self._get_command('set-property', prop, value, dsc)
        cmd.execute()
        project = prop.get_project()
        project.undo_stack.push_undo(cmd)

    def set_translatable_property(self, prop, value, comment,
                                  translatable, has_context):
        gadget = prop.gadget
        dsc = _('Setting %s of %s') % (prop.name, gadget.name)
        cmd = self._get_command('set-translatable',
                                prop, value, comment, translatable,
                                has_context, dsc)
        cmd.execute()
        project = prop.get_project()
        project.changed = True
        project.undo_stack.push_undo(cmd)

    def add_signal(self, gadget, signal):
        dsc = _('Add signal handler %s') % signal.handler
        cmd = self._get_command('add-signal',
                                True, signal, gadget, dsc)
        cmd.execute()
        gadget.project.undo_stack.push_undo(cmd)

    def remove_signal(self, gadget, signal):
        dsc = _('Remove signal handler %s') % signal.handler
        cmd = self._get_command('add-signal',
                                False, signal, gadget, dsc)
        cmd.execute()
        gadget.project.undo_stack.push_undo(cmd)

    def change_signal(self, gadget, old_signal, new_signal):
        dsc = _('Change signal handler for signal "%s"') % old_signal.name
        cmd = self._get_command('change-signal',
                                gadget, old_signal, new_signal,
                                dsc)
        cmd.execute()
        gadget.project.undo_stack.push_undo(cmd)

    def copy(self, gadget):
        """Add a copy of the widget to the clipboard.

        Note that it does not make sense to undo this operation
        """
        clipboard.add_widget(gadget)

    def cut(self, gadget):
        dsc = _('Cut widget %s into the clipboard') % gadget.name
        clipboard.add_widget(gadget)
        cmd = self._get_command('cut-paste', gadget,
                                gadget.project, None,
                                COMMAND_CUT, dsc)
        cmd.execute()
        gadget.project.undo_stack.push_undo(cmd)

    def paste(self, placeholder, project):
        if project is None:
            raise ValueError("No project has been specified. Cannot paste "
                             "the widget")

        gadget = clipboard.get_selected_widget(project)

        dsc = _('Paste widget %s from the clipboard') % gadget.name
        cmd = self._get_command('cut-paste', gadget, project, placeholder,
                                COMMAND_PASTE, dsc)
        gadget = cmd.execute()
        project.undo_stack.push_undo(cmd)

        return gadget

    def add_action(self, values, parent, project):
        gact = GAction(parent, values['name'], values['label'],
                       values['short_label'], values['is_important'],
                       values['tooltip'], values['stock_id'],
                       values['callback'], values['accelerator'])
        dsc = _('Add action %s') % gact.name
        cmd = self._get_command('add-action', parent, gact, True, dsc)
        cmd.execute()
        project.undo_stack.push_undo(cmd)

    def remove_action(self, gact, project):
        dsc = _('Remove action %s') % gact.name
        cmd = self._get_command('add-action',
                                gact.parent, gact, False, dsc)
        cmd.execute()
        project.undo_stack.push_undo(cmd)

    def edit_action(self, gact, new_values, project):
        dsc = _('Edit action %s') % gact.name
        cmd = self._get_command('edit-action', gact, new_values,
                                project, dsc)
        cmd.execute()
        project.undo_stack.push_undo(cmd)

    def add_action_group(self, name, project):
        gaction_group = GActionGroup(name)
        dsc = _('Add action group %s') % gaction_group.name
        cmd = self._get_command('add-action-group',
                                gaction_group, project, True, dsc)
        cmd.execute()
        project.undo_stack.push_undo(cmd)
        return gaction_group

    def remove_action_group(self, gaction_group, project):
        dsc = _('Remove action group %s') % gaction_group.name
        cmd = self._get_command('remove-action-group',
                                gaction_group, project, False, dsc)
        cmd.execute()
        project.undo_stack.push_undo(cmd)

    def edit_action_group(self, gaction_group, new_name, project):
        dsc = _('Edit action group %s') % gaction_group.name
        cmd = self._get_command('edit-action-group',
                                gaction_group, new_name, project, dsc)
        cmd.execute()
        project.undo_stack.push_undo(cmd)

    def set_button_contents(self, gadget, stock_id=None, notext=False,
                            label=None, image_path=None, position=-1,
                            icon_size=gtk.ICON_SIZE_BUTTON, child_name=None):
        dsc = _("Setting button %s contents") % gadget.name
        cmd = self._get_command('button', gadget, stock_id, notext,
                                label, image_path, position,
                                icon_size, child_name, dsc)
        cmd.execute()
        gadget.project.undo_stack.push_undo(cmd)

    def execute_drag_drop(self, source_gadget, target_placeholder):
        """Execute a drag and drop action, i.e. move a widget from one
        place to another. This method cannot be used to drag widgets
        between programs.

        @param source_gadget: the widget that is dragged
        @type source_gadget: gazpacho.widget.Gadget
        @param target_placeholder: the placeholder onto which the
        widget is droped
        @type target_placeholder: gazpacho.placeholder.Placeholder
        """
        cmd = self._get_command(
            'drag-drop', source_gadget, target_placeholder,
            _("Drag and Drop widget %s") % source_gadget.name)
        cmd.execute()
        source_gadget.project.undo_stack.push_undo(cmd)

    def execute_drop(self, gadget, target_placeholder):
        """Execute a drop action, i.e. add a widget.

        @param gadget: the widget that is droped
        @type gadget: gazpacho.widget.Gadget
        @param target_placeholder: the placeholder onto which the
        widget is droped
        @type target_placeholder: gazpacho.placeholder.Placeholder
        """
        project = gadget.project
        cmd = self._get_command('cut-paste', gadget, project,
                                target_placeholder, COMMAND_PASTE,
                                _('Drop widget %s') % gadget.name)
        cmd.execute()
        project.undo_stack.push_undo(cmd)

    def execute_drag_extend(self, source_gadget, target_gadget,
                            location, keep_source):
        cmd = self._get_command('drag-extend', source_gadget,
                                target_gadget, location,
                                keep_source, _("Drag - extend"))
        cmd.execute()
        target_gadget.project.undo_stack.push_undo(cmd)

    def execute_create_extend(self, adaptor, target_gadget, location,
                              interactive=True):

        gadget = create_gadget(adaptor, target_gadget.project, interactive)
        cmd = self._get_command('create-extend', gadget, target_gadget,
                                location, _("Create - extend"))
        cmd.execute()
        target_gadget.project.undo_stack.push_undo(cmd)

        from gazpacho.palette import palette
        if not palette.persistent_mode:
            palette.unselect_widget()

    def execute_drag_append(self, source_gadget, target_box, pos, keep_source):
        cmd = self._get_command('drag-append', source_gadget, target_box, pos,
                                keep_source, _("Drag - append"))
        cmd.execute()
        target_box.project.undo_stack.push_undo(cmd)


    def execute_create_append(self, adaptor, target_box, pos, interactive=True):
        gadget = create_gadget(adaptor, target_box.project, interactive)
        cmd = self._get_command('create-append', gadget, target_box,
                                pos, _("Create - extend"))

        cmd.execute()
        target_box.project.undo_stack.push_undo(cmd)

        from gazpacho.palette import palette
        if not palette.persistent_mode:
            palette.unselect_widget()


    def add_sizegroup_gadgets(self, sizegroup, gadgets, project):
        """
        Add a gadget to a size group. If a gadget is already in the
        size group it will be ignored.

        It is not possible to add gadgets that already exist in the
        sizegroup. If that should happend those gadgets will be
        ignored. It is thus possible to end up with a command that
        doesn't do anything at all.

        @param sizegroup: the sizegroup that the gadgets belong to
        @type sizegroup: gazpacho.sizegroup.GSizeGroup
        @param gadget: the gadget that should be added
        @type gadget: gazpacho.widget.Gadget
        @param project: the project that the sizegroup belongs to
        @type project: gazpacho.project.Project
        """
        add_gadgets = []

        # We don't add a gadget that's already in the sizegroup
        for gadget in gadgets:
            if not sizegroup.has_gadget(gadget):
                add_gadgets.append(gadget)

        if gadgets and not safe_to_add_gadgets(sizegroup, add_gadgets):
            warning(_("Cannot add the widget"),
                    _("It's not possible to add a gadget who has an ancestor"
                      " or child in the sizegroup."))
            return

        dsc = _("Add widgets to size group '%s'") % sizegroup.name
        cmd = self._get_command('sizegroup', sizegroup, add_gadgets,
                                project, True, dsc)
        cmd.execute()
        project.undo_stack.push_undo(cmd)

    def remove_sizegroup_gadgets(self, sizegroup, gadgets, project):
        """
        Remove gadgets from a size group.

        @param sizegroup: the sizegroup that the gadgets belong to
        @type sizegroup: gazpacho.sizegroup.GSizeGroup
        @param gadgets: the gadgets that should be removed
        @type gadgets: list (of gazpacho.widget.Gadget)
        @param project: the project that the sizegroup belongs to
        @type project: gazpacho.project.Project
        """
        dsc = _("Remove widgets from size group '%s'") % sizegroup.name
        cmd = self._get_command('sizegroup', sizegroup, gadgets,
                                project, False, dsc)
        cmd.execute()
        project.undo_stack.push_undo(cmd)

    def remove_sizegroup(self, sizegroup, project):
        """
        Remove a size group.

        @param sizegroup: the sizegroup that should be removed
        @type sizegroup: gazpacho.sizegroup.GSizeGroup
        @param project: the project that the sizegroup belongs to
        @type project: gazpacho.project.Project
        """
        gadgets = sizegroup.get_gadgets()
        dsc = _("Remove size group '%s'") % sizegroup.name
        cmd = self._get_command('sizegroup', sizegroup, gadgets,
                                project, False, dsc)
        cmd.execute()
        project.undo_stack.push_undo(cmd)

command_manager = CommandManager()
