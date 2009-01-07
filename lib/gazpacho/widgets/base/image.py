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

from gazpacho.properties import prop_registry, CustomProperty, StringType

class FileProp(CustomProperty, StringType):
    # we can remove this class when depending in gtk 2.8 since this property
    # is readable there
    editable = True
    translatable = False

    # We need to override get_default, since
    # the standard mechanism to get the initial value
    # is calling get_property, but ::file is not marked as readable
    def get_default(self, gobj):
        return ""

    def load(self):
        value = super(FileProp, self).load()
        self._initial = value
        self.set(value)

    def get(self):
        return self.object.get_data('image-file-name')

    def set(self, value):
        if value:
            self.object.set_data('image-file-name', value)
            self.object.set_property('file', value)

    def save(self):
        return self.get()

prop_registry.override_simple('GtkImage::file', FileProp)

class StockProp(CustomProperty, StringType):
    default = "gtk-missing-image"
    translatable = False
    def save(self):
        if self.object.get_data('image-file-name'):
            return
        return super(StockProp, self).save()

prop_registry.override_simple('GtkImage::stock', StockProp)

# <property id="icon" name="Icon">
#   <function name="get" type="ignore"/>
#   <function name="set" type="ignore"/>
#   <function name="create" type="legacy"
#             value="glade_gtk_image_icon_editor_create"/>
#   <function name="update" type="legacy"
#             value="glade_gtk_image_icon_editor_update"/>
# <property id="icon-size">
#   <function name="create" type="legacy"
#             value="glade_gtk_image_icon_size_editor_create"/>
#   <function name="update" type="legacy"
#             value="glade_gtk_image_icon_size_editor_update"/>

### Managing the custom editors for GtkImage
# TODO: this has to be redone since now editors need to be classes, not just
# functions
## def _image_icon_editor_add_widget(box, name, widget, expand):
##     box.pack_start(widget, expand=expand)
##     box.set_data(name, widget)

## def glade_gtk_image_icon_editor_create(context):

##     store = gtk.ListStore(str, str)
##     completion = gtk.EntryCompletion()
##     completion.set_model(store)

##     cell = gtk.CellRendererPixbuf()
##     completion.pack_start(cell, True)
##     completion.add_attribute(cell, 'stock-id', 0)

##     cell = gtk.CellRendererText()
##     completion.pack_start(cell, True)
##     completion.add_attribute(cell, 'text', 1)

##     completion.set_text_column(0)
##     completion.set_minimum_key_length(1)

##     _image_icon_create_stock_popup(completion)

##     entry = gtk.Entry()
##     entry.set_completion(completion)

##     fc_button = gtk.Button(_('...'))

##     hbox = gtk.HBox()
##     _image_icon_editor_add_widget(hbox, 'image-icon-entry', entry, True)
##     _image_icon_editor_add_widget(hbox, 'image-icon-file-chooser', fc_button,
##                                   False)

##     return hbox

## def _image_icon_create_stock_popup(completion):
##     model = completion.get_model()

##     for stock_id in gtk.stock_list_ids():
##         if stock_id == 'gtk-missing-image': continue
##         stock_item = gtk.stock_lookup(stock_id)
##         if not stock_item:
##             continue
##         model.append([stock_id, stock_item[1]])

## def _image_icon_entry_changed(entry, proxy):
##     if entry.get_text() in gtk.stock_list_ids():
##         proxy.set_property('stock', entry.get_text())

## def _image_icon_file_clicked(button, (proxy, image, entry)):
##     dialog = gtk.FileChooserDialog('Chooser', None,
##                                    gtk.FILE_CHOOSER_ACTION_OPEN,
##                                    buttons=(gtk.STOCK_CANCEL,
##                                             gtk.RESPONSE_CANCEL,
##                                             gtk.STOCK_OPEN,
##                                             gtk.RESPONSE_OK))

##     filter = gtk.FileFilter()
##     filter.set_name("Images")
##     filter.add_mime_type("image/png")
##     filter.add_mime_type("image/jpeg")
##     filter.add_mime_type("image/gif")
##     filter.add_mime_type("image/x-xpixmap")
##     filter.add_pattern("*.png")
##     filter.add_pattern("*.jpg")
##     filter.add_pattern("*.gif")
##     filter.add_pattern("*.xpm")

##     dialog.add_filter(filter)

##     response = dialog.run()
##     if response == gtk.RESPONSE_OK and dialog.get_filename():
##         entry.handler_block(entry.get_data('handler-id-changed'))
##         entry.set_text(os.path.basename(dialog.get_filename()))
##         entry.handler_unblock(entry.get_data('handler-id-changed'))
##         proxy.set_property('file', dialog.get_filename())
##         image.set_data('image-file-name', entry.get_text())

##     dialog.destroy()
##     return

## def _image_icon_reconnect(widget, signal, callback, userdata):
##     handler_id = widget.get_data('handler-id-' + signal)
##     if handler_id:
##         widget.disconnect(handler_id)

##     handler_id = widget.connect(signal, callback, userdata)
##     widget.set_data('handler-id-' + signal, handler_id)

## def glade_gtk_image_icon_editor_update(context, box, image, proxy):
##     entry = box.get_data('image-icon-entry')
##     toggle = box.get_data('image-icon-stock-chooser')
##     fc_button = box.get_data('image-icon-file-chooser')

##     stock_id = image.get_property('stock')
##     if stock_id and stock_id != 'gtk-missing-image':
##         text = stock_id
##     elif image.get_data('image-file-name'):
##         text = image.get_data('image-file-name')
##     else:
##         text = ''

##     entry.set_text(text)

##     _image_icon_reconnect(entry, 'changed', _image_icon_entry_changed, proxy)
##     _image_icon_reconnect(fc_button, 'clicked', _image_icon_file_clicked,
##                           (proxy, image, entry))

## def glade_gtk_image_icon_size_editor_create(context):
##     store = gtk.ListStore(str, int)

##     combo = gtk.ComboBox(store)

##     cell = gtk.CellRendererText()
##     combo.pack_start(cell, True)
##     combo.add_attribute(cell, 'text', 0)

##     return combo

## def _image_icon_size_setup_combo(editor, image):
##     model = editor.get_model()
##     model.clear()

##     stock_id = image.get_property('stock')
##     if not stock_id or stock_id == 'gtk-missing-image':
##         editor.set_sensitive(False)
##         return

##     icon_set = gtk.icon_factory_lookup_default(stock_id)
##     editor.set_sensitive(True)

##     icon_size = image.get_property('icon-size')
##     for size in icon_set.get_sizes():
##         iter = model.append([gtk.icon_size_get_name(size), size])

##         if size == icon_size:
##             editor.handler_block(editor.get_data('handler-id-changed'))
##             editor.set_active_iter(iter)
##             editor.handler_unblock(editor.get_data('handler-id-changed'))

## def _image_icon_size_notify(image, param_spec, (editor, proxy)):
##     _image_icon_size_setup_combo(editor, image)

## def _image_icon_size_changed(editor, proxy):
##     iter = editor.get_active_iter()
##     if iter:
##         model = editor.get_model()
##         proxy.set_value(model[iter][1])

## def glade_gtk_image_icon_size_editor_update(context, editor, image, proxy):
##     handler_id = image.get_data('image-notify-id')
##     if handler_id:
##         image.disconnect(handler_id)

##     _image_icon_reconnect(editor, 'changed', _image_icon_size_changed, proxy)

##     _image_icon_size_setup_combo(editor, image)

##     handler_id = image.connect('notify', _image_icon_size_notify,
##                                (editor, proxy))
##     image.set_data('image-notify-id', handler_id)
##     return



