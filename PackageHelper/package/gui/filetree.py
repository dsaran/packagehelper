import gtk
import pickle

from kiwi.ui.delegates import Delegate
from kiwi.ui.objectlist import Column

from package.domain.file import File


class FileTree(Delegate):
    gladefile = "filetree"
    widgets = ["fileTree"]

    _changed = None
    _file = None

    TARGETS = [('FILE_TREE_ROW', gtk.TARGET_SAME_WIDGET, 1)]

    def __init__(self, root=None):
        Delegate.__init__(self, delete_handler=self.quit_if_last)

        self.fileTree.set_columns([Column('name', data_type=str, searchable=True, editable=True)])
        print "filetree: ", self.fileTree
        if root:
            self.base_path.set_text(root)
            self._fill(root)

        self._enable_drag_and_drop()
        self.show_all()
        gtk.main()

    def _enable_drag_and_drop(self):
        print "enabling dnd..."
        self.fileTree._treeview.connect('drag-begin',
                               self._on_fileTree__drag_begin)

        self.fileTree._treeview.connect('drag_data_get',
                               self._on_fileTree__drag_data_get)
        self.fileTree._treeview.connect("drag_data_received",
                              self._on_fileTree__drag_data_received)
        self.fileTree._treeview.enable_model_drag_dest(self.TARGETS,
            gtk.gdk.ACTION_MOVE)
        #self.fileTree._treeview.connect("drag_drop",
        #                      self._on_fileTree__drag_drop)

        #self.fileTree._treeview.connect('drag_motion', self.motion_cb)


        self.fileTree._treeview.enable_model_drag_source(
            gtk.gdk.BUTTON1_MASK, self.TARGETS,
            gtk.gdk.ACTION_DEFAULT| gtk.gdk.ACTION_MOVE)
        #self.fileTree._treeview.drag_source_set(
        #    gtk.gdk.BUTTON1_MASK, self.TARGETS,
        #    gtk.gdk.ACTION_DEFAULT| gtk.gdk.ACTION_MOVE)

        #self.fileTree._treeview.drag_dest_set(gtk.DEST_DEFAULT_ALL,
        #    self.TARGETS,
        #    gtk.gdk.ACTION_MOVE)
    def _on_fileTree__drag_begin(self, treeview, context):
        print "---------------------------------------- drag begin"
        #context.drag_abort(0)
        #context.finish(False, False, 0)

        return False
        #from time import time
        #treeselection = treeview.get_selection()
        #model, iter = treeselection.get_selected()
        #children_iter = model.iter_children(iter)
        #print "iter: ", model[iter]
        #print "children_iter: ", children_iter
        #print "bool(children_iter): ", bool(children_iter)
        #if children_iter:
        #    context.drag_abort(1)
        #    return False



    def _on_fileTree__drag_data_get(self, treeview, context, selection, target_id,
                                    etime):
        print "drag get start"
        print "target_id: ", target_id
        treeselection = treeview.get_selection()
        model, iter = treeselection.get_selected()
        data = pickle.dumps(model.get_value(iter, 0))
        children_iter = model.iter_children(iter)
        print "iter: ", model[iter]
        print "children_iter: ", children_iter
        print "bool(children_iter): ", bool(children_iter)
        context.drag_abort(etime)
        if children_iter:
            return False
            #selection.set(self.TARGETS[1], 8, "")
        #file = model.get_value(iter, 0)
        #data = file.get_name()
        print "treeselection ", treeselection, " ", type(treeselection)
        print "selection.target ", selection.target
        selection.set(selection.target, 8, data)


    def _on_fileTree__drag_data_received(self, treeview, context, x, y, selection,
                                              info, etime):
        print "drag receive start"
        #for i in [self, treeview, context, x, y, selection, info, etime]:
        #    print type(i)

        model = treeview.get_model()
        print "model: ", model
        print "target: ", selection.target
        if not selection.data:
            context.finish(False, False, etime)
            return False

        data = pickle.loads(selection.data)
        #name = selection.data
        #file = File()
        #file.set_name(name)
        #data = file
        drop_info = treeview.get_dest_row_at_pos(x, y)
        if drop_info:
            print "drop_info: ", drop_info
            print "selection.selection: ", selection.selection
            print "selection.target: ", selection.target
            print "selection.type: ", selection.type
            path, position = drop_info
            iter = model.get_iter(path)
            print "iter: ", iter
            if (position == gtk.TREE_VIEW_DROP_BEFORE
                or position == gtk.TREE_VIEW_DROP_INTO_OR_BEFORE):
                model.insert_before(None, iter, [data])
                #model.move_before(iter, [data])
            else:
                model.insert_after(None, iter, [data])
                #model.move_after(iter, [data])
        else:
            model.append([data])
        print "action: ", context.action
        if context.action == gtk.gdk.ACTION_MOVE:
            print "Finishing..."
            context.finish(True, True, etime)
        return True

    #
    # Temporary methods
    #
    def _on_fileTree__drag_drop(self, treeview, context, x, y, etime):
        for i in [self, treeview, context, x, y, etime]:
            print type(i)
        print "targets: ", context.targets
        print "data: ", context.get_data(context.targets[0])
        context.finish(True, True, etime)
        return True

    def motion_cb(wid, context, x, y, time):
        context.drag_status(gtk.gdk.ACTION_move, time)
        return True

    #def drag_data_delete_cb(widget, drag_context, data):
        
        

    def _fill(self, root, load=False):
        _root = File(path=root)
        self.fileTree.append(None, _root)
        self._load_files(_root)

    def _load_files(self, path):
        generator = path.get_path().listdir()
        for item in generator:
            file = File(item)
            self.fileTree.append(path, file)
            if item.isdir():
                self._load_files(file)

    def on_fileTree__cell_edited(self, *args):
        print "cell edited: ", args

    def on_fileTree__row_expanded(self, *args):
        print "row expanded: ", args

    def on_fileTree__drag_begin(self, *args):
        print "drag begin: ", args


if __name__ == "__main__":
    t = Tree()

