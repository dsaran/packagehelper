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

import sys

import gtk

# External API, used by extensions. Do not remove.
def get_bool_from_string_with_default(value, default):
    if value in ['True', 'TRUE', 'true', 'yes', '1']:
        return True
    elif value in ['False', 'FALSE', 'false', 'no', '0']:
        return False
    else:
        return default

def get_parent(widget):
    from gazpacho.widget import Gadget
    parent_widget = widget
    gadget = None
    while True:
        parent_widget = parent_widget.get_parent()
        if parent_widget is None:
            return None
        gadget = Gadget.from_widget(parent_widget)
        if gadget is not None:
            return gadget

    return None

def select_iter(treeview, item_iter):
    """
    @param treeview:
    @param item_iter:
    """
    model = treeview.get_model()
    path = model[item_iter].path
    if treeview.flags() & gtk.REALIZED:
        treeview.expand_to_path(path)
        treeview.scroll_to_cell(path)
    treeview.get_selection().select_path(path)

def get_button_state(button):
    """Get the state of the button in the form of a tuple with the following
    fields:
      - stock_id: string with the stock_id or None if the button is not
        using a stock_id
      - notext: boolean that says if the button has only a stock icon or
        if it also has the stock label
      - label: string with the contents of the button text or None
      - image_path: string with the path of a custom file for the
        image or None
      - position: one of gtk.POS_* that specifies the position of the
        image with respect to the label
    """
    stock_id = label = image_path = position = None
    notext = False
    icon_size = gtk.ICON_SIZE_BUTTON

    use_stock = button.get_use_stock()
    child_name = None
    child = button.get_child()
    image_file_name = None
    if child:
        image_file_name = child.get_data('image-file-name')
        child_name = child.get_name()

    # it is a stock button
    if use_stock and not image_file_name:
        stock_id = button.get_label()

    # it only has a text label
    elif isinstance(child, gtk.Label):
        label = child.get_text()

    # it has an image without text. it can be stock icon or custom image
    elif isinstance(child, gtk.Image):
        if image_file_name:

            image_path = image_file_name
        else:
            stock_id = child.get_property('stock')
            if not stock_id:
                print 'Unknown button image state, no stock, no filename'
        notext = True
        icon_size = child.get_property('icon-size')
    # it has custom image and text
    elif isinstance(child, gtk.Alignment):
        box = child.get_child()

        children = box.get_children()
        image_child = None
        text_child = None
        text_last = True
        for c in children:
            if isinstance(c, gtk.Image):
                image_child = c
                text_last = False
            elif isinstance(c, gtk.Label):
                text_child = c
                text_last = True

        if isinstance(box, gtk.HBox):
            if text_last:
                position = gtk.POS_LEFT
            else:
                position = gtk.POS_RIGHT
        else:
            if text_last:
                position = gtk.POS_TOP
            else:
                position = gtk.POS_BOTTOM

        if image_child:
            image_path = image_child.get_data('image-file-name')

        if text_child:
            label = text_child.get_text()
        else:
            notext = True

    return (stock_id, notext, label, image_path, position, icon_size,
            child_name)

def rebuild():
    try:
        from twisted.python.rebuild import rebuild
    except ImportError:
        print 'You need twisted installed to be able to reload'
        return

    sys.stdout.write('** reloading... ')
    # See #328669
    try:
        sys.stdout.flush()
    except IOError:
        pass

    _ignore = ()
    modules = sys.modules.keys()
    modules.sort()
    for name in modules:
        if name in _ignore:
            continue

        if not name.startswith('gazpacho'):
            continue

        if not sys.modules.has_key(name):
            continue

        module = sys.modules[name]
        if not module:
            continue

        rebuild(module, doLog=0)
    sys.stdout.write('done\n')

