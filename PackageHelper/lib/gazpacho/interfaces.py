# Copyright (C) 2005 by Async Open Source
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

from kiwi.component import Attribute, Interface

class BaseWidgetAdaptor:
    name = None
    type = None

class BaseLibrary:
    def __init__(self, name, library_name):
        pass

    def create_widget(self, gtype):
        pass

class IGazpachoApp(Interface):
    """Provides a gazpacho application"""

    add_class = Attribute('add_class')

    def get_current_project(self):
        pass

    def get_window(self):
        pass
