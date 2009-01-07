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

import gtk
from kiwi.ui.dialogs import BaseDialog

_ = lambda msg: gettext.dgettext('gazpacho', msg)

class CloseConfirmationDialog(BaseDialog):
    """A base class for the close confirmation dialogs. It lets the
    user choose to Save the projects, Close without saving them and to
    abort the close operation.
    """

    def __init__(self, projects, toplevel=None):
        BaseDialog.__init__(self, parent=toplevel)

        self.add_buttons(_("Close _without Saving"), gtk.RESPONSE_NO,
                         gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL,
                         gtk.STOCK_SAVE, gtk.RESPONSE_YES)

        save, cancel, close = self.action_area.get_children()
        if gtk.settings_get_default().get_property(
            "gtk-alternative-button-order"):
            save, close = close, save
        save.set_name("save")
        cancel.set_name("cancel")
        close.set_name("close")

        self.set_default_response(gtk.RESPONSE_YES)

        self.set_border_width(6)
        self.set_resizable(False)
        self.set_has_separator(False)
        self.vbox.set_spacing(12)

        # Add the warning image to the dialog
        warning_image = gtk.image_new_from_stock(gtk.STOCK_DIALOG_WARNING,
                                                 gtk.ICON_SIZE_DIALOG)
        warning_image.set_alignment(0.5, 0)

        self._hbox = gtk.HBox(False, 12)
        self._hbox.set_border_width(6)
        self._hbox.pack_start(warning_image, False, False, 0)

        self.vbox.pack_start(self._hbox)


class SingleCloseConfirmationDialog(CloseConfirmationDialog):
    """A close confirmation dialog for a single project."""

    def __init__(self, project, toplevel=None):
        CloseConfirmationDialog.__init__(self, toplevel)
        self._project = project

        submsg1 = _('Save changes to project "%s" before closing?') % \
                  project.name
        submsg2 = _("Your changes will be lost if you don't save them.")
        msg = '<span weight="bold" size="larger">%s</span>\n\n%s\n' % \
              (submsg1, submsg2)
        label = gtk.Label(msg)
        label.set_use_markup(True)
        label.set_line_wrap(True)
        label.set_alignment(0.0, 0.5)
        self._hbox.pack_start(label)

        self.vbox.show_all()

    def get_projects(self):
        """Get a list of the projects that should be saved."""
        return [self._project]

class MultipleCloseConfirmationDialog(CloseConfirmationDialog):
    """A close confirmation dialog for a multiple project. It presents
    a list of the projects and let the user choose which to save."""

    def __init__(self, projects, toplevel=None):
        CloseConfirmationDialog.__init__(self, toplevel)
        self._projects = projects
        self._projects.sort(lambda x, y: cmp(x.name, y.name))

        # ListStore (boolean, Project) storing information about which
        # projects should be saved.
        self._model = None

        submsg1 = ('There are %d projects with unsaved changes. '
                   'Do you want to save those changes before closing?') % \
                 len(projects)
        submsg2 = _("Your changes will be lost if you don't save them.")
        msg = '<span weight="bold" size="larger">%s</span>\n\n%s\n' % \
              (submsg1, submsg2)
        label = gtk.Label(msg)
        label.set_use_markup(True)
        label.set_line_wrap(True)
        label.set_alignment(0.0, 0.5)

        list_label = gtk.Label()
        list_label.set_markup_with_mnemonic(_("S_elect the projects you "
                                              "want to save:"))
        list_label.set_line_wrap(True)
        list_label.set_alignment(0.0, 0.5)
        list_label.set_padding(0, 6)

        view = self._create_project_list()
        list_label.set_mnemonic_widget(view)

        scrolled_window = gtk.ScrolledWindow()
        scrolled_window.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        scrolled_window.add_with_viewport(view)
        scrolled_window.set_size_request(200, 100)

        project_vbox = gtk.VBox(False)
        project_vbox.pack_start(label)
        project_vbox.pack_start(list_label)
        project_vbox.pack_start(scrolled_window)
        self._hbox.pack_start(project_vbox)

        self.vbox.show_all()

    def _create_project_list(self):
        """Create, populate and return a TreeView containing the
        unsaved projects."""
        # Create a ListStore model
        self._model = gtk.ListStore(bool, object)
        for project in self._projects:
            self._model.append([True, project])

        # Create the TreeView
        view = gtk.TreeView(self._model)
        view.set_headers_visible(False)

        # Create the check-box column
        toggle_renderer = gtk.CellRendererToggle()
        toggle_renderer.set_property('activatable', True)
        toggle_renderer.connect("toggled", self._toggled_cb, (self._model, 0))
        toggle_column = gtk.TreeViewColumn('Save', toggle_renderer)
        toggle_column.add_attribute(toggle_renderer, 'active', 0)
        view.append_column(toggle_column)

        # Create the project column
        def render_func(treeviewcolumn, renderer, model, iter):
            project = model[iter][1]
            renderer.set_property('text', project.name)
            return
        text_renderer = gtk.CellRendererText()
        text_column = gtk.TreeViewColumn('Project', text_renderer)
        text_column.set_cell_data_func(text_renderer, render_func)
        view.append_column(text_column)

        return view

    def _toggled_cb(self, renderer, path, user_data):
        """Callback to change the state of the check-box."""
        model, column = user_data
        model[path][column] = not model[path][column]

    def get_projects(self):
        """Get a list of the projects that should be saved."""
        return [project for saved, project in self._model if saved]
