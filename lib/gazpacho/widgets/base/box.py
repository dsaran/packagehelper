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

import gtk

from gazpacho.properties import prop_registry, CustomProperty, IntType
from gazpacho.placeholder import Placeholder
from gazpacho.widgets.base.base import ContainerAdaptor
from gazpacho.widget import Gadget

class BoxAdaptor(ContainerAdaptor):
    def fill_empty(self, context, widget):
        pass

# GtkBox
class BoxSizeProp(CustomProperty, IntType):
    minimum = 1
    default = 3
    label = 'Size'
    persistent = False
    def load(self):
        self._initial = self.default

        # Don't set default if object has childs already
        if not self.get():
            self.set(self.default)

    def get(self):
        return len(self.object.get_children())

    def set(self, new_size):
        old_size = len(self.object.get_children())
        if new_size == old_size:
            return
        elif new_size > old_size:
            # The box has grown. Add placeholders
            while new_size > old_size:
                self.object.add(Placeholder())
                old_size += 1
        elif new_size > 0:
            # The box has shrunk. Remove placeholders first, starting
            # with the last one
            for child in self.object.get_children()[::-1]:
                if isinstance(child, Placeholder):
                    gtk.Container.remove(self.object, child)
                    old_size -= 1

                if old_size == new_size:
                    return

            # and then remove widgets
            child = self.object.get_children()[-1]
            while old_size > new_size and child:
                gadget = Gadget.from_widget(child)
                if gadget: # It may be None, e.g a placeholder
                    gadget.project.remove_widget(child)

                gtk.Container.remove(self.object, child)
                child = self.object.get_children()[-1]
                old_size -= 1

prop_registry.override_property('GtkBox::size', BoxSizeProp)
prop_registry.override_simple('GtkBox::spacing', minimum=0)

