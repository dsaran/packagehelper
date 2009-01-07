# Copyright (C) 2005 by SICEm S.L. and Async Open Source
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

import gtk

from gazpacho.properties import prop_registry
from gazpacho.widgets.base.base import ContainerAdaptor

class TreeViewAdaptor(ContainerAdaptor):
    def create(self, context, interactive=True):
        tree_view = super(TreeViewAdaptor, self).create(context, interactive)
        model = gtk.ListStore(str) # dummy model
        tree_view.set_model(model)
        return tree_view

    # While we don't support column editing on the treeview
    # this does not make sense
##     renderer = gtk.CellRendererText()
##     column = gtk.TreeViewColumn('Column 1', renderer, text=0)
##     tree_view.append_column(column)

##     column = gtk.TreeViewColumn('Column 2', renderer, text=0)
##     tree_view.append_column(column)

    def fill_empty(self, context, widget):
        pass

# Disable headers-clickable, see bug #163851
prop_registry.override_simple('GtkTreeView::headers-clickable', disabled=True)

