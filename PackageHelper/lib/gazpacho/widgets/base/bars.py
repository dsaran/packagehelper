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

import gettext

from gazpacho.editor import PropertyCustomEditorWithDialog
from gazpacho.properties import prop_registry, TransparentProperty, StringType
from gazpacho.uieditor import UIEditor
from gazpacho.widget import Gadget
from gazpacho.widgets.base.base import ContainerAdaptor

_ = lambda msg: gettext.dgettext('gazpacho', msg)

class UIPropEditor(PropertyCustomEditorWithDialog):
    dialog_class = UIEditor
    button_text = _('Edit UI Definition...')

class UIAdaptor(TransparentProperty, StringType):
    """This represents a fake property to edit the ui definitions of
    menubars and toolbars.

    It does not store anything because this information is stored in
    the uimanager itself. It's just a way to put a button in the Gazpacho
    interface to call the UIEditor.
    """
    editor = UIPropEditor

class MenuBarUIAdapter(UIAdaptor):
    pass

prop_registry.override_property('GtkMenuBar::ui', MenuBarUIAdapter)

class ToolbarUIAdapter(UIAdaptor):
    pass

prop_registry.override_property('GtkToolbar::ui', ToolbarUIAdapter)

class CommonBarsAdaptor(ContainerAdaptor):

    def post_create(self, context, widget, ui_string):
        # create some default actions
        gadget = Gadget.from_widget(widget)
        project = gadget.project
        project.uim.create_default_actions()

        project.uim.add_ui(gadget, ui_string)
        new_widget = project.uim.get_widget(gadget)

        # we need to replace widget with new_widget
        gadget.setup_widget(new_widget)
        #gadget.apply_properties()

    def save(self, context, widget):
        """This saver is needed to avoid saving the children of toolbars
        and menubars
        """
        widget.constructor = 'initial-state'

    def load(self, context, widget):
        """This loader is special because of these features:
        - It does not load the children of the menubar/toolbar
        - Load the uimanager and put its content (action groups) into the
        project
        """

#         # we need to save the properties of this widget because otherwise
#         # when we got it from the uimanager it's gonna be another widget with
#         # different properties
#         props = {}
#         for prop in gobject.list_properties(widget):
#             if 1 or prop.flags != gobject.PARAM_READWRITE:
#                 continue
#             if propertyclass.get_type_from_spec(prop) is gobject.TYPE_OBJECT:
#                 continue
#             # FIXME: This need to use the values from the catalog.
#             # But it doesn't work right now, the property in
#             # klass.properties is always set to False.
#             if prop.name == 'parent' or prop.name == 'child':
#                 continue
#             props[prop.name] = widget.get_property(prop.name)

        project = context.get_project()

        old_name = widget.name
        gadget = Gadget.load(widget, project)
        gadget._name = gadget.widget.name

        # change the widget for the one we get from the uimanager
        project.uim.load_widget(gadget, old_name)

        return gadget

    def fill_empty(self, context, widget):
        pass

class MenuBarAdaptor(CommonBarsAdaptor):

    def post_create(self, context, menubar, interactive=True):
        gadget = Gadget.from_widget(menubar)
        # A None in this list means a separator
        names = [gadget.name, 'FileMenu', 'New', 'Open', 'Save',
                 'SaveAs', 'Quit', 'EditMenu', 'Copy', 'Cut',
                 'Paste']
        tmp = []
        for name in names:
            tmp.extend([name, name])

        ui_string = """<menubar action="%s" name="%s">
  <menu action="%s" name="%s">
    <menuitem action="%s" name="%s"/>
    <menuitem action="%s" name="%s"/>
    <menuitem action="%s" name="%s"/>
    <menuitem action="%s" name="%s"/>
    <separator/>
    <menuitem action="%s" name="%s"/>
  </menu>
  <menu action="%s" name="%s">
    <menuitem action="%s" name="%s"/>
    <menuitem action="%s" name="%s"/>
    <menuitem action="%s" name="%s"/>
  </menu>
</menubar>""" % tuple(tmp)

        super(MenuBarAdaptor, self).post_create(context, menubar, ui_string)

class ToolbarAdaptor(CommonBarsAdaptor):
    def post_create(self, context, toolbar, interactive=True):
        gadget = Gadget.from_widget(toolbar)

        names = [gadget.name, 'New', 'Open', 'Save',
                 'Copy', 'Cut', 'Paste']
        tmp = []
        for name in names:
            tmp.extend([name, name])

        ui_string = """<toolbar action="%s" name="%s">
  <toolitem action="%s" name="%s"/>
  <toolitem action="%s" name="%s"/>
  <toolitem action="%s" name="%s"/>
  <separator/>
  <toolitem action="%s" name="%s"/>
  <toolitem action="%s" name="%s"/>
  <toolitem action="%s" name="%s"/>
</toolbar>""" % tuple(tmp)

        super(ToolbarAdaptor, self).post_create(context, toolbar, ui_string)

