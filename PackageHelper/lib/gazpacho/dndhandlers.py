# Copyright (C) 2005 Red Hat, Inc.
# Copyright (C) 2006 Async Open Source
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

from gazpacho import util
from gazpacho.commandmanager import command_manager
from gazpacho.widget import Gadget

(DND_POS_TOP,
 DND_POS_BOTTOM,
 DND_POS_LEFT,
 DND_POS_RIGHT,
 DND_POS_BEFORE,
 DND_POS_AFTER) = range(6)

(INFO_TYPE_XML,
 INFO_TYPE_WIDGET,
 INFO_TYPE_PALETTE) = range(3)

MIME_TYPE_OBJECT_XML = 'application/x-gazpacho-object-xml'
MIME_TYPE_OBJECT     = 'application/x-gazpacho-object'
MIME_TYPE_OBJECT_PALETTE = 'application/x-gazpacho-palette'

# This is the value returned by Widget.drag_dest_find_target when no
# targets have been found. The API reference says it should return
# None (and NONE) but it seems to return the string "NONE".
DND_NO_TARGET = "NONE"

DND_WIDGET_TARGET  = (MIME_TYPE_OBJECT, gtk.TARGET_SAME_APP, INFO_TYPE_WIDGET)
DND_XML_TARGET     = (MIME_TYPE_OBJECT_XML, 0, INFO_TYPE_XML)
DND_PALETTE_TARGET = (MIME_TYPE_OBJECT_PALETTE, gtk.TARGET_SAME_APP,
                      INFO_TYPE_PALETTE)

class DnDHandler(object):

    #
    # Public methods
    #

    def connect_drag_handlers(self, widget):
        """
        Connect all handlers necessary for the widget to serve as a
        drag source.

        @param widget: widget to which the handlers should be connected
        @type widget: gtk.Widget
        """
        widget.drag_source_set(gtk.gdk.BUTTON1_MASK,
                               [DND_WIDGET_TARGET, DND_XML_TARGET],
                               gtk.gdk.ACTION_COPY | gtk.gdk.ACTION_MOVE)
        widget.connect('drag_begin', self._on_drag_begin)
        widget.connect('drag_data_get', self._on_drag_data_get)


    def connect_drop_handlers(self, widget):
        """
        Connect all handlers necessary for the widget to serve as a
        drag destination.

        @param widget: widget to which the handlers should be connected
        @type widget: gtk.Widget
        """
        widget.drag_dest_set(0,
                             [DND_WIDGET_TARGET,
                              DND_XML_TARGET,
                              DND_PALETTE_TARGET],
                             gtk.gdk.ACTION_MOVE | gtk.gdk.ACTION_COPY)
        widget.connect('drag_motion', self._on_drag_motion)
        widget.connect('drag_leave', self._on_drag_leave)
        widget.connect('drag_drop', self._on_drag_drop)
        widget.connect('drag_data_received', self._on_drag_data_received)



    #
    # Methods that can be used and overridden by subclasses
    #

    def _get_target_project(self, target_widget):
        """
        Get the project to which the target belongs.

        @param target_widget: the target widget
        @type target_widget: gtk.Widget
        """
        raise NotImplementedError

    def _set_drag_highlight(self, target_widget, x, y):
        """Highlight the widget in an appropriate way to indicate
        that this is a valid drop zone.

        @param target_widget: the gtk target widget
        @type target_widget: gtk.Widget
        @param x: the mouse x position
        @type x: int
        @param y: the mouse y position
        @type y: int
        """
        raise NotImplementedError

    def _clear_drag_highlight(self, target_widget):
        """Clear the drag highligt.

        @param target_widget: the gtk target widget
        @type target_widget: gtk.Widget
        """
        raise NotImplementedError

    def _is_valid_drop_zone(self, drag_context, target_widget):
        """Check whether the drop zone is valid or not.

        @param drag_context: the drag context
        @type drag_context: gtk.gdk.DragContext
        @param target_widget: the target gtk widget
        @type target_widget: gtk.Widget
        """
        # Check if it is a valid target type
        targets = target_widget.drag_dest_get_target_list()
        target = target_widget.drag_dest_find_target(drag_context, targets)
        if target == DND_NO_TARGET:
            return False

        # We can always drag widgets from the palette and widgets that
        # are in XML form
        if target in (MIME_TYPE_OBJECT_PALETTE, MIME_TYPE_OBJECT_XML):
            return True

        # Get the widget that is being dragged. Note that the source
        # widget in the drag event isn't always the widget that is
        # being dragged (for example labels)
        source_widget = drag_context.get_source_widget()
        source_gadget = Gadget.from_widget(source_widget)
        dragged_widget = source_gadget.dnd_widget.widget

        # Not a valid drop zone if target == source.
        if dragged_widget == target_widget:
            return False

        # Make sure we don't try to drop a widget onto one of its
        # children
        if dragged_widget.is_ancestor(target_widget):
            return False

        return True

    def _get_drag_action(self, drag_context, target_widget):
        """Get the drag action. If the target is in the same project
        as the source we move the widget, otherwise we copy it.

        @param drag_context:
        @type drag_context:
        @param target_widget: the target widget
        @type target_widget: gtk.Widget
        """
        target_project = self._get_target_project(target_widget)
        source_widget = drag_context.get_source_widget()
        source_gadget = source_widget and Gadget.from_widget(source_widget)
        if not source_gadget or source_gadget.project != target_project:
            return gtk.gdk.ACTION_COPY

        return gtk.gdk.ACTION_MOVE

    def _get_dnd_gadget(self, data, info, drag_context, project):
        """Get the actual gazpacho Gadget that is dragged. This is not
        necessarily the same widget as the one that recieved the drag
        event.
        """
        dnd_widget = None
        if info == INFO_TYPE_WIDGET:
            source_widget = drag_context.get_source_widget()
            source_gadget = Gadget.from_widget(source_widget)
            dnd_widget = source_gadget.dnd_widget

        elif info == INFO_TYPE_XML:
            dnd_widget = Gadget.from_xml(project, data.data)

        return dnd_widget


    #
    # Signal handlers for the drag source
    #

    def _on_drag_begin(self, source_widget, drag_context):
        """Callback for the 'drag-begin' event."""
        raise NotImplementedError

    def _on_drag_data_get(self, source_widget, drag_context, selection_data,
                          info, time):
        """Callback for the 'drag-data-get' event."""
        raise NotImplementedError


    #
    # Signal handlers for the drag target
    #

    def _on_drag_leave(self, target_widget, drag_context, time):
        """Callback for the 'drag-leave' event. We clear the drag
        highlight."""
        self._clear_drag_highlight(target_widget)

    def _on_drag_motion(self, target_widget, drag_context, x, y, time):
        """Callback for the 'drag-motion' event. If the drop zone is
        valid we set the drag highlight and the drag action."""
        if not self._is_valid_drop_zone(drag_context, target_widget):
            return False

        # XXX: Do not draw highlight if there is a children visible at
        #      position x, y.
        #      Test case is HBox->Notebook, drag notebook into itself, notice
        #      border which is not correct
        self._set_drag_highlight(target_widget, x, y)

        drag_action = self._get_drag_action(drag_context, target_widget)
        drag_context.drag_status(drag_action, time)
        return True

    def _on_drag_drop(self, target_widget, drag_context, x, y, time):
        """Callback for handling the 'drag_drop' event."""
        if not drag_context.targets:
            return False

        if drag_context.get_source_widget():
            # For DnD within the application we request to use the
            # widget or adaptor directly
            if MIME_TYPE_OBJECT_PALETTE in drag_context.targets:
                mime_type = MIME_TYPE_OBJECT_PALETTE
            else:
                mime_type = MIME_TYPE_OBJECT
        else:
            # otherwise we'll have request the data to be passed as XML
            mime_type = MIME_TYPE_OBJECT_XML

        target_widget.drag_get_data(drag_context, mime_type, time)

        return True

    def _on_drag_data_received(self, target_widget, drag_context,
                                  x, y, data, info, time):
        """Callback for the 'drag-data-recieved' event."""
        raise NotImplementedError


class WidgetDnDHandler(DnDHandler):


    def _get_target_project(self, target_widget):
        """
        Get the project to which the target belongs.

        @param target_widget: the target widget
        @type target_widget: gtk.Widget
        """
        target_gadget = Gadget.from_widget(target_widget)
        return target_gadget.project

    def _set_drag_highlight(self, target_widget, x, y):
        """
        Highlight the widget in an appropriate way to indicate
        that this is a valid drop zone.

        @param target_widget: the gtk target widget
        @type target_widget: gtk.Widget
        @param x: the mouse x position
        @type x: int
        @param y: the mouse y position
        @type y: int
        """
        gadget = Gadget.from_widget(target_widget)
        gadget.set_drop_region(self._get_drop_location(target_widget, x, y)[1])

    def _clear_drag_highlight(self, target_widget):
        """
        Clear the drag highligt.

        @param target_widget: the gtk target widget
        @type target_widget: gtk.Widget
        """
        gadget = Gadget.from_widget(target_widget)
        gadget.clear_drop_region()

    def _get_drop_location(self, target_widget, x, y):
        """Calculate the drop region and also the drop location
        relative to the widget.

        The location can be one of the following constants
          - DND_POS_TOP
          - DND_POS_BOTTOM
          - DND_POS_LEFT
          - DND_POS_RIGHT
          - DND_POS_BEFORE
          - DND_POS_AFTER

        The drop region is a tuple of x,y,width and height.

        @param target_widget: the widget where the drop occurred
        @type target_widget: gtk.Widget
        @param x: the x position of the drop
        @type x: int
        @param y: the y position of the drop
        @type y: int

        @return: (location, region)
        @rtype: tuple
        """
        parent = util.get_parent(target_widget)
        h_appendable = parent and isinstance(parent.widget, gtk.HBox)
        v_appendable = parent and isinstance(parent.widget, gtk.VBox)

        x_off, y_off, width, height = target_widget.allocation

        x_third = width / 3
        y_third = height / 3

        if x > x_third * 2:
            if h_appendable:
                location = DND_POS_AFTER
            else:
                location = DND_POS_RIGHT
            region = (x_third * 2 + x_off, 2 + y_off,
                      x_third, height - 4)
        elif x < x_third:
            if h_appendable:
                location = DND_POS_BEFORE
            else:
                location = DND_POS_LEFT
            region = (2 + x_off, 2 + y_off, x_third - 2, height - 4)
        elif y > y_third * 2:
            if v_appendable:
                location = DND_POS_AFTER
            else:
                location = DND_POS_BOTTOM
            region = (2 + x_off, y_third * 2 + y_off, width - 4, y_third - 2)
        elif y < y_third:
            if v_appendable:
                location = DND_POS_BEFORE
            else:
                location = DND_POS_TOP
            region = (2 + x_off, 2 + y_off, width - 4, y_third)
        else:
            location = None
            region = (0, 0, 0, 0)

        return location, region

    def _is_extend_action(self, location):
        """
        Check if we should perform an extend action.

        @param location: the drop location
        @type location: dnd constant
        @return: True if we should extend
        @rtype: bool
        """
        return location in (DND_POS_TOP, DND_POS_BOTTOM, DND_POS_LEFT,
                            DND_POS_RIGHT)

    def _is_append_action(self, location):
        """
        Check if we should perform an append action.

        @param location: the drop location
        @type location: dnd constant
        @return: True if we should append
        @rtype: bool
        """
        return location in (DND_POS_AFTER, DND_POS_BEFORE)

    def _get_append_position(self, target_widget, location):
        """
        Get the position where we should add the widget.

        @param target_widget: the widget where the drop occurred
        @type target_widget: gtk.Widget
        @param location: the drop location
        @type location: dnd constant
        """
        box = target_widget.get_parent()
        pos = box.get_children().index(target_widget)
        if location == DND_POS_AFTER:
            pos = pos + 1
        return pos

    def _execute_drag(self, location, dnd_widget, target_gadget, keep_source):
        """
        Execute the drag-append or drag-extend command.

        @param location: the drop location
        @type location: dnd constant
        @param dnd_widget: the widget that is being dragged
        @type dnd_widget: L{gazpacho.widget.Widget}
        @param target_gadget: the widget where the drop occurred
        @type target_gadget: L{gazpacho.widget.Widget}
        @param keep_source: True if the source widget should not be removed
        @type keep_source: bool

        @return: True if the drop was successful
        @rtype: bool
        """
        if not dnd_widget:
            return False

        if self._is_extend_action(location):
            command_manager.execute_drag_extend(dnd_widget, target_gadget,
                                                location, keep_source)
            return True

        elif self._is_append_action(location):
            pos = self._get_append_position(target_gadget.widget, location)
            parent = target_gadget.get_parent()
            command_manager.execute_drag_append(dnd_widget, parent, pos,
                                                keep_source)
            return True

        return False

    def _execute_create(self, location, adaptor, target_gadget):
        """
        Execute the create-append or create-extend command.

        @param location: the drop location
        @type location: dnd constant
        @param adaptor: adaptor for creating the class
        @type adaptor: L{gazpacho.widgetadaptor.WidgetAdaptor}
        @param target_gadget: the widget where the drop occurred
        @type target_gadget: L{gazpacho.widget.Widget}

        @return: True if the drop was successful
        @rtype: bool
        """
        if self._is_extend_action(location):
            command_manager.execute_create_extend(adaptor, target_gadget,
                                                  location)
            return True

        elif self._is_append_action(location):
            pos = self._get_append_position(target_gadget.widget, location)
            parent = target_gadget.get_parent()
            command_manager.execute_create_append(adaptor, parent, pos)
            return True

        return False


    #
    # Signal handlers for the drag source
    #

    def _on_drag_begin(self, source_widget, drag_context):
        """
        Set a drag icon that matches the drag source widget.
        """
        source_gadget = Gadget.from_widget(source_widget)
        if source_gadget.dnd_widget:
            pixbuf = source_gadget.dnd_widget.adaptor.icon.get_pixbuf()
            source_widget.drag_source_set_icon_pixbuf(pixbuf)

    def _on_drag_data_get(self, source_widget, drag_context, selection_data,
                          info, time):
        """
        Make the widget data available in the format that was
        requested. If the drag and drop occurs within the application
        the widget can be accessed directly otherwise it has to be
        passed as an XML string.
        """
        source_gadget = Gadget.from_widget(source_widget)
        dnd_widget = source_gadget.dnd_widget

        # If we can't get the widget we indicate this failure by
        # passing an empty string. Not sure if it's correct but it
        # works for us.
        if not dnd_widget:
            selection_data.set(selection_data.target, 8, "")
            return

        # The widget should be passed as XML
        if info == INFO_TYPE_XML:
            selection_data.set(selection_data.target, 8, dnd_widget.to_xml())

        # The widget can be retrieved directly and we only pass the name
        elif info == INFO_TYPE_WIDGET:
            selection_data.set(selection_data.target, 8, dnd_widget.name)
        # We don't understand the request and pass nothing
        else:
            selection_data.set(selection_data.target, 8, "")


    #
    # Signal handlers for the drag target
    #

    def _on_drag_data_received(self, target_widget, drag_context, x, y, data,
                               info, time):
        """
        The data has been received and the appropriate command can now
        be executed.

        If the drag/drop is in the same project the target handles
        everything. If it's between different projects the target only
        handles the drop (paste) and the source takes care of the drag
        (cut).
        """
        # If there is no data we indicate that the drop was not
        # successful
        if not data.data:
            drag_context.finish(False, False, time)
            return

        project = self._get_target_project(target_widget)
        location = self._get_drop_location(target_widget, x, y)[0]
        target_gadget = Gadget.from_widget(target_widget)

        success = False
        if info in (INFO_TYPE_WIDGET, INFO_TYPE_XML):
            dnd_gadget = self._get_dnd_gadget(data, info, drag_context, project)
            keep_source = (drag_context.action != gtk.gdk.ACTION_MOVE)
            success = self._execute_drag(location, dnd_gadget, target_gadget,
                                         keep_source)

        elif info == INFO_TYPE_PALETTE:
            adaptor = project.get_app().add_class
            success = self._execute_create(location, adaptor, target_gadget)

        drag_context.finish(success, False, time)


class PlaceholderDnDHandler(DnDHandler):

    def _get_target_project(self, target_widget):
        """
        Get the project to which the target belongs.

        @param target_widget: the target placeholder
        @type target_widget: L{gazpacho.placeholder.Placeholder}
        """
        return target_widget.get_project()

    def _set_drag_highlight(self, target_widget, x, y):
        """
        Highlight the widget in an appropriate way to indicate
        that this is a valid drop zone.

        @param target_widget: the gtk target widget
        @type target_widget: gtk.Widget
        @param x: the mouse x position
        @type x: int
        @param y: the mouse y position
        @type y: int
        """
        target_widget.drag_highlight()

    def _clear_drag_highlight(self, target_widget):
        """
        Clear the drag highligt.

        @param target_widget: the gtk target widget
        @type target_widget: gtk.Widget
        """
        target_widget.drag_unhighlight()

    def _execute_drag(self, dnd_gadget, placeholder, keep_source, project):
        """
        Execute the drag and drop command.

        @param dnd_gadget: the gadget that is being dragged
        @type dnd_gadget: L{gazpacho.widget.Gadget}
        @param placeholder: the widget where the drop occurred
        @type placeholder: L{gazpacho.placeholder.Placeholder}
        @param keep_source: True if the source widget should not be removed
        @type keep_source: bool
        @param project: the target project
        @type project: L{gazpacho.project.Project}

        @return: True if the drop was successful
        @rtype: bool
        """
        if not dnd_gadget:
            return False

        if keep_source:
            command_manager.execute_drop(dnd_gadget.copy(project),
                                         placeholder)
        else:
            command_manager.execute_drag_drop(dnd_gadget, placeholder)

        return True

    #
    # Signal handlers for the drag target
    #

    def _on_drag_data_received(self, target_widget, drag_context, x, y, data,
                               info, time):
        """
        The data has been received and the appropriate command can now
        be executed.

        If the drag/drop is in the same project the target handles
        everything. If it's between different projects the target only
        handles the drop (paste) and the source takes care of the drag
        (cut)."""
        # If there is no data we indicate that the drop was not
        # successful
        if not data.data:
            drag_context.finish(False, False, time)
            return

        project = self._get_target_project(target_widget)

        success = False
        if info in (INFO_TYPE_WIDGET, INFO_TYPE_XML):
            # note that the dragged widget isn't always the same as
            # the source widget in the event
            dragged_gadget = self._get_dnd_gadget(data, info, drag_context,
                                                  project)
            keep_source = drag_context.action != gtk.gdk.ACTION_MOVE

            success = self._execute_drag(dragged_gadget, target_widget,
                                         keep_source, project)
        elif info == INFO_TYPE_PALETTE:
            command_manager.create(project.get_app().add_class, target_widget,
                                   None)
            success = True

        drag_context.finish(success, False, time)
