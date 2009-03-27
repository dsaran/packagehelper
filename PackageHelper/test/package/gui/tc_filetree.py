import unittest
from test import mock
from test.package.gui.util import refresh_gui, display, Position
from test.framework import TestCase
from package.ui.filetree import FileTree
from package.domain.file import File, InstallScript
from package.domain.pack import Package

class FileTreeTests(TestCase):
    def setUp(self):
        self.inst1 = InstallScript(name="InstallScript 1")
        self.inst2 = InstallScript(name="InstallScript 2")
        self.inst3 = InstallScript(name="InstallScript 3")
        self.f1 = File("/tmp/file1")
        self.f2 = File("/tmp/file2")
        self.f3 = File("/tmp/file3")

        self.inst1.content.append(self.f1)
        self.inst1.content.append(self.f2)
        self.inst1.content.append(self.f3)

        self.model = Package()

        self.data = [self.inst1, self.inst2, self.inst3]
        self.ft = FileTree(model=self.model, scripts=[self.inst1, self.inst2, self.inst3])
        display(self.ft)

    def tearDown(self):
        #FIXME: should have a toplevel to display and destroy
        pass

    def testRenameScript(self):
        pass

    def testGetData(self):
        """ When I get data from filetree result should match expected"""
        expected = [InstallScript(self.inst1.name, content=[self.f1, self.f2, self.f3]),
                    InstallScript(self.inst2.name),
                    InstallScript(self.inst3.name)]

        self.when_i_get_filetree_data()

        self.should_match_expected_data(expected)


    def testDragDataInto(self):
        """ Given I dragged a file into another script result should match expected"""
        expected = [InstallScript(self.inst1.name, content=[self.f2, self.f3]),
                    InstallScript(self.inst2.name, content=[self.f1]),
                    InstallScript(self.inst3.name)]

        self.given_i_dragged(item=self.f1, source=self.inst1, destination=self.inst2, position=Position.INTO)

        self.when_i_get_filetree_data()

        self.should_match_expected_data(expected)


    def testDragDataBefore(self):
        """ Given I dragged a file before another script it should not be moved"""
        expected = [InstallScript(self.inst1.name, content=[self.f1, self.f2, self.f3]),
                    InstallScript(self.inst2.name),
                    InstallScript(self.inst3.name)]

        self.given_i_dragged(item=self.f1, source=self.inst1, destination=self.inst2, position=Position.BEFORE)

        self.when_i_get_filetree_data()

        self.should_match_expected_data(expected)

    def _testDataModel(self):
        """ When I add data to filetree it should be added to model"""
        #XXX: This logic should be on filetree ?
        self.given_i_have_empty_filetree()

        self.when_i_add_a_script()

        self.then_it_should_add_script_to_model()
    #
    # Given clauses
    #

    def given_i_dragged(self, item, source, destination, position):
        tree = self.ft.fileTree
        treeview = tree.get_treeview()

        tree.expand(source)

        display(self.ft)

        tree.select(item)
        self.assertEquals(item, tree.get_selected())

        context = mock.Mock()
        selection = mock.Mock()

        self.ft._on_fileTree__drag_data_get(treeview, context, selection, None, 0L)
        self.assertTrue(selection.set.called, "selection.set not called")

        # Prepare GtkSelection mock with data set from drag_data_set to be used
        # with drag_data_received
        selection.data = selection.set.call_args[0][2]


        # Setup mock with the drop_info
        treeview.get_dest_row_at_pos = mock.Mock()
        treeview.get_dest_row_at_pos.return_value = ((1,), position)

        x, y = 0, 0
        moved = self.ft._on_fileTree__drag_data_received(treeview, context, x, y, selection, None, 0L)

        if moved:
            # Remove dragged row manually since drag handler will not call drag_data_delete
            tree.remove(item)

        tree.expand(destination)
        display(self.ft)

    #
    # When clauses
    #

    def when_i_get_filetree_data(self):
        self.loaded_data = self.ft.get_data()

    #
    # Should clauses
    #

    def should_match_expected_data(self, expected):
        self.assertEquals(expected, self.loaded_data)
        self.assertEquals(expected[0].content, self.loaded_data[0].content)
        self.assertEquals(expected[1].content, self.loaded_data[1].content)
        self.assertEquals(expected[2].content, self.loaded_data[2].content)

if __name__ == '__main__':
    from sys import path as pythonpath
    from os import path
    pythonpath.insert(0, 'lib')
    pythonpath.insert(0, 'test')

    ph_home = path.dirname(path.abspath(__file__))
    pythonpath.insert(0, ph_home) 

    from package.types.parsers import DefaultParser
    from package.rollback.parsers import *

    from package.gui.filetree import FileTree
    from package.domain.file import File, InstallScript
    import gtk
    import time


    unittest.main()
