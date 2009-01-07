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

import cStringIO
import xml.dom
from xml.sax.saxutils import escape

import gobject
import gtk

from gazpacho.choice import enum_to_string, flags_to_string
from gazpacho.loader import tags
from gazpacho.placeholder import Placeholder
from gazpacho.properties import prop_registry
from gazpacho.widget import Gadget

def write_xml(file, xml_node, indent=0, indent_increase=4):
    if xml_node.nodeType == xml_node.TEXT_NODE:
        file.write(xml_node.data)
        return
    elif xml_node.nodeType == xml_node.CDATA_SECTION_NODE:
        file.write('<![CDATA[%s]]>' % xml_node.data)
        return

    file.write(' '*indent)

    file.write('<%s' % xml_node.tagName)
    if len(xml_node.attributes) > 0:
        attr_string = ' '.join(['%s="%s"' % (n, v)
                                    for n, v in xml_node.attributes.items()])
        file.write(' ' + attr_string)

    children = [a for a in xml_node.childNodes
                    if a.nodeType != a.ATTRIBUTE_NODE]
    if children:
        has_text_child = False
        for child in children:
            if child.nodeType in (child.TEXT_NODE,
                                  child.CDATA_SECTION_NODE):
                has_text_child = True
                break

        if has_text_child:
            file.write('>')
        else:
            file.write('>\n')
        for child in children:
            write_xml(file, child, indent+indent_increase, indent_increase)

        if not has_text_child:
            file.write(' '*indent)
        file.write('</%s>\n' % xml_node.tagName)
    else:
        file.write('/>\n')

class XMLWriter:
    def __init__(self, document=None, project=None):
        if not document:
            dom = xml.dom.getDOMImplementation()
            document = dom.createDocument(None, None, None)
        self._doc = document
        self._project = project

    def write(self, path, widgets, sizegroups, uim, domain):
        root = self._write_root(widgets, domain)
        self._write_sizegroups(root, sizegroups)
        self._write_widgets(root, widgets, uim)
        self._write_gazpacho_document(path, root)

    def _write_header(self, f, dtd_url):
        f.write("""<?xml version="1.0" standalone="no"?> <!--*- mode: xml -*-->
<!DOCTYPE glade-interface SYSTEM "%s">
""" % dtd_url)

    def _write_gazpacho_document(self, path, root):
        f = file(path, 'w')
        self._write_header(f, "http://gazpacho.sicem.biz/gazpacho-0.1.dtd")
        write_xml(f, root)
        f.close()

    # FIXME: Should this really be exported
    write_node = _write_gazpacho_document

    def _write_libglade_document(self, path, root):
        f = file(path, 'w')
        self._write_header(f, "http://glade.gnome.org/glade-2.0.dtd")

        f.write('\n<glade-interface>\n\n')
        for node in root.childNodes:
            write_xml(f, node, indent_increase=2)
        f.write('\n</glade-interface>\n')

        f.close()

    def serialize_node(self, gadget):
        element = self._doc.createElement(tags.XML_TAG_PROJECT)
        root = self._doc.appendChild(element)

        # FIXME: Requirements? see _write_root

        # save the UI Manager if needed
        gadget.project.uim.save_gadget(gadget, root, self._doc)
        root.appendChild(self._write_widget(gadget))

        return self._doc.documentElement

    def serialize(self, gadget):
        fp = cStringIO.StringIO()
        node = self.serialize_node(gadget)
        write_xml(fp, node)

        fp.seek(0)

        return fp.read()

    def serialize_widgets(self, widgets, sizegroups, uim):
        fp = cStringIO.StringIO()
        root = self._write_root(widgets)
        self._write_sizegroups(root, sizegroups)
        self._write_widgets(root, widgets, uim)
        write_xml(fp, root)
        fp.seek(0)

        return fp.read()

    def _get_requirements(self, gadgets):
        # check what modules are the gadgets using
        # Not implemented
        return []

    def _write_root(self, gadgets, domain=None):
        project_node = self._doc.createElement(tags.XML_TAG_PROJECT)
        node = self._doc.appendChild(project_node)

        if domain:
            node.setAttribute(tags.XML_TAG_DOMAIN, domain)

        for module in self._get_requirements(gadgets):
            n = self._doc.createElement(tags.XML_TAG_REQUIRES)
            n.setAttribute(tags.XML_TAG_LIB, module)
            node.appendChild(n)

        return node

    def _write_sizegroups(self, root, sizegroups):
        for sizegroup in sizegroups:
            node = self._doc.createElement(tags.XML_TAG_WIDGET)
            root.appendChild(node)
            node.setAttribute(tags.XML_TAG_CLASS, 'GtkSizeGroup')
            node.setAttribute(tags.XML_TAG_ID, sizegroup.name)

            prop_node = self._doc.createElement(tags.XML_TAG_PROPERTY)
            node.appendChild(prop_node)
            prop_node.setAttribute(tags.XML_TAG_NAME, 'mode')
            text = self._doc.createTextNode(enum_to_string(
                sizegroup.mode, enum=gtk.SizeGroupMode))
            prop_node.appendChild(text)

    def _write_widgets(self, node, widgets, uim):
        # Append uimanager
        ui_widgets = [Gadget.from_widget(w)
                          for w in widgets
                               if isinstance(w, (gtk.Toolbar,
                                                 gtk.MenuBar))]
        ui_node = uim.save(self._doc, ui_widgets)
        if ui_node:
            node.appendChild(ui_node)

        # Append toplevel widgets. Each widget then takes care of
        # appending its children
        for widget in widgets:
            gadget = Gadget.from_widget(widget)
            if (gadget is None or
                not gadget.is_toplevel()):
                continue

            wnode = self._write_widget(gadget)
            node.appendChild(wnode)

        return node

    def _write_widget(self, gadget):
        """Serializes this gadget into a XML node and returns this node"""

        gadget.maintain_gtk_properties = True

        gadget.adaptor.save(gadget.project.context, gadget)

        # otherwise use the default saver
        node = self._write_basic_information(gadget)

        self._write_properties(node, gadget, child=False)
        self._write_signals(node, gadget.get_all_signal_handlers())

        # Children
        widget = gadget.widget
        if not isinstance(widget, gtk.Container):
            return node

        # We're not writing children when we have a constructor set
        if gadget.constructor:
            return node

        children = gadget.get_children()
        if isinstance(widget, gtk.Table):
            table = widget
            def table_sort(a, b):
                res =  cmp(table.child_get_property(a, 'left-attach'),
                           table.child_get_property(b, 'left-attach'))
                if res == 0:
                    res = cmp(table.child_get_property(a, 'top-attach'),
                              table.child_get_property(b, 'top-attach'))
                return res
            children.sort(table_sort)

        # Boxes doesn't need to be sorted, they're already in the right order
        for child_widget in children:
            if isinstance(child_widget, Placeholder):
                child_node = self._write_placeholder(child_widget)
            else:
                # if there is no gadget for this child
                # we don't save it. If your children are not being
                # saved you should create a gadget for them
                # in your Adaptor
                child_gadget = Gadget.from_widget(child_widget)
                if child_gadget is None:
                    continue
                child_node = self._write_child(child_gadget)

            node.appendChild(child_node)

        gadget.maintain_gtk_properties = False

        return node

    def _write_properties(self, widget_node, gadget, child):
        properties = prop_registry.get_writable_properties(gadget.widget,
                                                           child)
        properties.sort(lambda a, b: cmp(a.name, b.name))

        for prop_type in properties:
            if prop_type.child:
                prop = gadget.get_child_prop(prop_type.name)
            else:
                prop = gadget.get_prop(prop_type.name)
            value = prop.save()
            if value == None:
                continue
            property_node = self._write_property(prop, value)
            widget_node.appendChild(property_node)

    def _write_signals(self, widget_node, signals):
        # <signal name="..." handler="..." after="..." object="..."/>
        for signals in signals:
            for signal in signals:
                signal_node = self._doc.createElement(tags.XML_TAG_SIGNAL)
                signal_node.setAttribute(tags.XML_TAG_NAME, signal.name)
                signal_node.setAttribute(tags.XML_TAG_HANDLER, signal.handler)
                if signal.after:
                    signal_node.setAttribute(tags.XML_TAG_AFTER, tags.TRUE)
                if signal.object:
                    signal_node.setAttribute(tags.XML_TAG_OBJECT, signal.object)
                widget_node.appendChild(signal_node)

    def _write_basic_information(self, gadget):
        # <widget class="..." id=" constructor="">
        assert gadget.adaptor.type_name
        assert gadget.name, 'gadget %r is nameless' % gadget.widget
        node = self._doc.createElement(tags.XML_TAG_WIDGET)

        # If name is set write it to the file
        if gadget.adaptor.name:
            type_name = gadget.adaptor.name
        else:
            type_name = gadget.adaptor.type_name

        node.setAttribute(tags.XML_TAG_CLASS, type_name)
        node.setAttribute(tags.XML_TAG_ID, gadget.name)
        if gadget.constructor:
            node.setAttribute('constructor', gadget.constructor)
        return node

    def _write_child(self, child_gadget):
        # <child>
        #   <child internal-name="foo">
        # </child>

        child_node = self._doc.createElement(tags.XML_TAG_CHILD)

        if child_gadget.internal_name is not None:
            child_node.setAttribute(tags.XML_TAG_INTERNAL_CHILD,
                                    child_gadget.internal_name)

        child = self._write_widget(child_gadget)
        child_node.appendChild(child)

        # Append the packing properties
        packing_node = self._doc.createElement(tags.XML_TAG_PACKING)
        self._write_properties(packing_node, child_gadget, child=True)

        if packing_node.childNodes:
            child_node.appendChild(packing_node)

        return child_node

    def _write_placeholder(self, widget):
        # <child>
        #   <placeholder>
        # </child>

        child_node = self._doc.createElement(tags.XML_TAG_CHILD)
        placeholder_node = self._doc.createElement(tags.XML_TAG_PLACEHOLDER)
        child_node.appendChild(placeholder_node)

        # we need to write the packing properties of the placeholder.
        # otherwise the container gets confused when loading its
        # children
        self._write_placeholder_properties(child_node, widget)

        return child_node

    def _write_placeholder_properties(self, child_node, placeholder):
        # <packing>
        #    <property>...</property>
        #    ....
        # </packing>

        # XXX: use prop_registry for this.

        parent = placeholder.get_parent()
        # get the non default packing properties
        packing_list = []
        props = gtk.container_class_list_child_properties(parent)
        for prop in props:
            v = parent.child_get_property(placeholder, prop.name)
            if v != prop.default_value:
                packing_list.append((prop, v))

        if not packing_list:
            return

        packing_node = self._doc.createElement(tags.XML_TAG_PACKING)

        for prop, value in packing_list:
            prop_node = self._doc.createElement(tags.XML_TAG_PROPERTY)
            prop_name = prop.name.replace('-', '_')
            prop_node.setAttribute(tags.XML_TAG_NAME, prop_name)

            if prop.value_type == gobject.TYPE_ENUM:
                v = enum_to_string(value, prop)
            elif prop.value_type == gobject.TYPE_FLAGS:
                v = flags_to_string(value, prop)
            else:
                v = escape(str(value))

            text = self._doc.createTextNode(v)
            prop_node.appendChild(text)
            packing_node.appendChild(prop_node)

        child_node.appendChild(packing_node)

    def _write_property(self, prop, value):
        # <property name="..."
        #           context="yes|no"
        #           translatable="yes|no">...</property>

        node = self._doc.createElement(tags.XML_TAG_PROPERTY)

        # We should change each '-' by '_' on the name of the property
        # put the name="..." part on the <property ...> tag
        node.setAttribute(tags.XML_TAG_NAME, prop.name.replace('-', '_'))

        # Only write context and comment if translatable is
        # enabled, to mimic glade-2
        if prop.is_translatable():
            node.setAttribute(tags.XML_TAG_TRANSLATABLE, tags.YES)
            if prop.has_i18n_context:
                node.setAttribute(tags.XML_TAG_CONTEXT, tags.YES)
            if prop.i18n_comment:
                node.setAttribute(tags.XML_TAG_COMMENT, prop.i18n_comment)

        text = self._doc.createTextNode(escape(value))
        node.appendChild(text)
        return node

