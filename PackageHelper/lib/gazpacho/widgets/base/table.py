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

from gazpacho.placeholder import Placeholder
from gazpacho.properties import prop_registry, \
     TransparentProperty, CustomChildProperty, UIntType
from gazpacho.widget import Gadget
from gazpacho.widgets.base.base import ContainerAdaptor

_ = lambda msg: gettext.dgettext('gazpacho', msg)

class TableAdaptor(ContainerAdaptor):

    def create(self, context, interactive=True):
        """ a GtkTable starts with a default size of 1x1, and setter/getter of
        rows/columns expect the GtkTable to hold this number of placeholders,
        so we should add it. """
        table = super(TableAdaptor, self).create(context, interactive)
        table.attach(Placeholder(), 0, 1, 0, 1)
        return table

    def post_create(self, context, table, interactive=True):
        if not interactive:
            return
        gadget = Gadget.from_widget(table)
        property_rows = gadget.get_prop('n-rows')
        property_cols = gadget.get_prop('n-columns')
        dialog = gtk.Dialog(_('Create a table'), None,
                            gtk.DIALOG_NO_SEPARATOR,
                            (gtk.STOCK_OK, gtk.RESPONSE_ACCEPT))
        dialog.set_position(gtk.WIN_POS_MOUSE)
        dialog.set_default_response(gtk.RESPONSE_ACCEPT)

        label_rows = gtk.Label(_('Number of rows')+':')
        label_rows.set_alignment(0.0, 0.5)
        label_cols = gtk.Label(_('Number of columns')+':')
        label_cols.set_alignment(0.0, 0.5)

        spin_button_rows = gtk.SpinButton()
        spin_button_rows.set_increments(1, 5)
        spin_button_rows.set_range(1.0, 10000.0)
        spin_button_rows.set_numeric(False)
        spin_button_rows.set_value(3)
        spin_button_rows.set_property('activates-default', True)

        spin_button_cols = gtk.SpinButton()
        spin_button_cols.set_increments(1, 5)
        spin_button_cols.set_range(1.0, 10000.0)
        spin_button_cols.set_numeric(False)
        spin_button_cols.set_value(3)
        spin_button_cols.set_property('activates-default', True)

        table = gtk.Table(2, 2, True)
        table.set_col_spacings(4)
        table.set_border_width(12)

        table.attach(label_rows, 0, 1, 0, 1)
        table.attach(spin_button_rows, 1, 2, 0, 1)

        table.attach(label_cols, 0, 1, 1, 2)
        table.attach(spin_button_cols, 1, 2, 1, 2)

        dialog.vbox.pack_start(table)
        table.show_all()

        # even if the user destroys the dialog box, we retrieve the number and
        # we accept it.  I.e., this function never fails
        dialog.run()

        property_rows.set(spin_button_rows.get_value_as_int())
        property_cols.set(spin_button_cols.get_value_as_int())

        dialog.destroy()

    def fill_empty(self, context, widget):
        pass

class TableSize(TransparentProperty, UIntType):
    def _add_placeholders(self, table, value, old_size):
        n_columns = table.get_property('n-columns')
        n_rows = table.get_property('n-rows')

        if self.name == 'n-rows':
            table.resize(value, n_columns)
            for col in range(n_columns):
                for row in range(old_size, value):
                    table.attach(Placeholder(), col, col+1, row, row+1)
        else:
            table.resize(n_rows, value)
            for row in range(n_rows):
                for col in range(old_size, value):
                    table.attach(Placeholder(), col, col+1, row, row+1)

    def _remove_children(self, table, value):
        # Remove from the bottom up

        if self.name == 'n-rows':
            start_prop = 'top-attach'
            end_prop = 'bottom-attach'
        else:
            start_prop = 'left-attach'
            end_prop = 'right-attach'

        for child in table.get_children()[::-1]:
            # We need to completely remove it
            start = table.child_get_property(child, start_prop)
            if start >= value:
                table.remove(child)
                continue

            # If the widget spans beyond the new border, we should resize it to
            # fit on the new table
            end = table.child_get_property(child, end_prop)
            if end > value:
                table.child_set_property(child, end_prop, value)

        if self.name == 'n-rows':
            table.resize(value, self.get())
        else:
            table.resize(self.get(), value)

    def set(self, value):
        self._value = value
        if value >= 1:
            table = self.object
            old_size = table.get_property(self.name)
            if value > old_size:
                self._add_placeholders(table, value, old_size)
            elif value < old_size:
                self._remove_children(table, value)

    def load(self):
        self._initial = self.object.get_property(self.name)

    def get(self):
        return self._value

    def save(self):
        return str(self.get())

prop_registry.override_simple('GtkTable::n-rows', TableSize)
prop_registry.override_simple('GtkTable::n-columns', TableSize)

prop_registry.override_simple('GtkTable::row-spacing',
                              minimum=0, maximum=10000)
prop_registry.override_simple('GtkTable::column-spacing',
                              minimum=0, maximum=10000)

class BaseAttach(CustomChildProperty):
    """Base class for LeftAttach, RightAttach, TopAttach and BottomAttach
    adaptors"""
    def _get_attach(self, child):
        """Returns the four attach packing properties in a tuple"""
        right = self.table.child_get_property(child, 'right-attach')
        left = self.table.child_get_property(child, 'left-attach')
        top = self.table.child_get_property(child, 'top-attach')
        bottom = self.table.child_get_property(child, 'bottom-attach')
        return (left, right, top, bottom)

    def _cell_empty(self, x, y):
        """Returns true if the cell at x, y is empty. Exclude child from the
        list of widgets to check"""
        empty = True
        for w in self.table.get_children():
            left, right, top, bottom = self._get_attach(w)
            if (left <= x and (x + 1) <= right
                and top <= y and (y + 1) <= bottom):
                empty = False
                break

        return empty

    def _create_placeholder(self, x, y):
        """Puts a placeholder at cell (x, y)"""
        self.table.attach(Placeholder(), x, x+1, y, y+1)

    def _fill_with_placeholders(self, y_range, x_range):
        """Walk through the table creating placeholders in empty cells.
        Only iterate between x_range and y_range.
        Child is excluded in the computation to see if a cell is empty
        """
        for y in range(self.n_rows):
            for x in range(self.n_columns):
                if self._cell_empty(x, y):
                    self._create_placeholder(x, y)

    def _initialize(self, child, prop_name):
        """Common things all these adaptors need to do at the beginning"""
        self.table = child.get_parent()
        (self.left_attach,
         self.right_attach,
         self.top_attach,
         self.bottom_attach) = self._get_attach(child)

        self.n_columns = self.table.get_property('n-columns')
        self.n_rows = self.table.get_property('n-rows')

        self.prop_name = prop_name
        self.child = child
        self.gchild = Gadget.from_widget(self.child)
        self.gprop = self.gchild.get_child_prop(self.prop_name)

    def _value_is_between(self, value, minimum, maximum):
        if value < minimum:
            self.gprop._value = minimum
            return False

        if value > maximum:
            self.gprop._value = maximum
            return False

        return True

    def _internal_set(self, value, minimum, maximum,
                      y_range, x_range):
        """Check if value is between minium and maximum and then remove or
        add placeholders depending if we are growing or shrinking.
        If we are shrinking check the cells in y_range, x_range to add
        placeholders
        """
        if not self._value_is_between(value, minimum, maximum):
            return

        placeholder = Placeholder()

        # are we growing?
        if self._is_growing(value):
            # check if we need to remove some placeholder
            for ph in filter(lambda w: isinstance(w, type(placeholder)),
                             self.table.get_children()):
                lph, rph, tph, bph = self._get_attach(ph)
                if self._cover_placeholder(value, lph, rph, tph, bph):
                    self.table.remove(ph)

            self.table.child_set_property(self.child, self.prop_name, value)

        # are we shrinking? maybe we need to create placeholders
        elif self._is_shrinking(value):
            self.table.child_set_property(self.child, self.prop_name, value)
            self._fill_with_placeholders(y_range, x_range)


    # virtual methods that should be implemented by subclasses:
    def _is_growing(self, value):
        """Returns true if the child widget is growing"""

    def _is_shrinking(self, value):
        """Returns true if the child widget is shrinking"""

    def _cover_placeholder(self, value, left, right, top, bottom):
        """Return True if there is a placeholder in these coordinates"""

class LeftAttach(BaseAttach, UIntType):
    label = 'Left attachment'

    def _is_growing(self, value):
        return value < self.left_attach

    def _is_shrinking(self, value):
        return value > self.left_attach

    def _cover_placeholder(self, value, left, right, top, bottom):
        if value < right and self.left_attach > left:
            if top >= self.top_attach and bottom <= self.bottom_attach:
                return True
        return False

    def set(self, value):
        child = self.object
        self._initialize(child, 'left-attach')
        self._internal_set(value, 0, self.right_attach - 1,
                           range(self.n_rows),
                           range(self.left_attach, value))
        super(LeftAttach, self).set(value)

prop_registry.override_simple_child('GtkTable::left-attach', LeftAttach)

class RightAttach(BaseAttach, UIntType):
    label = 'Right attachment'

    def _is_growing(self, value):
        return value > self.right_attach

    def _is_shrinking(self, value):
        return value < self.right_attach

    def _cover_placeholder(self, value, left, right, top, bottom):
        if value > left and self.right_attach < right:
            if top >= self.top_attach and bottom <= self.bottom_attach:
                return True
        return False

    def set(self, value):
        child = self.object
        self._initialize(child, 'right-attach')
        self._internal_set(value, self.left_attach + 1, self.n_columns,
                           range(self.n_rows),
                           range(self.left_attach, value))
        super(RightAttach, self).set(value)

prop_registry.override_simple_child('GtkTable::right-attach', RightAttach)

class BottomAttach(BaseAttach, UIntType):
    label = 'Bottom attachment'

    def _is_growing(self, value):
        return value > self.bottom_attach

    def _is_shrinking(self, value):
        return value < self.bottom_attach

    def _cover_placeholder(self, value, left, right, top, bottom):
        if value > top and self.bottom_attach < bottom:
            if left >= self.left_attach and right <= self.right_attach:
                return True
        return False

    def set(self, value):
        child = self.object
        self._initialize(child, 'bottom-attach')
        self._internal_set(value, self.top_attach + 1, self.n_rows,
                           range(value, self.bottom_attach),
                           range(self.n_columns))
        super(BottomAttach, self).set(value)

prop_registry.override_simple_child('GtkTable::bottom-attach', BottomAttach)

class TopAttach(BaseAttach, UIntType):
    label = 'Top attachment'

    def _is_growing(self, value):
        return value < self.top_attach

    def _is_shrinking(self, value):
        return value > self.top_attach

    def _cover_placeholder(self, value, left, right, top, bottom):
        if value < bottom and self.top_attach > top:
            if left >= self.left_attach and right <= self.right_attach:
                return True
        return False

    def set(self, value):
        child = self.object
        self._initialize(child, 'top-attach')
        self._internal_set(value, 0, self.bottom_attach - 1,
                           range(self.n_columns),
                           range(self.top_attach, value))
        super(TopAttach, self).set(value)

prop_registry.override_simple_child('GtkTable::top-attach', TopAttach)
