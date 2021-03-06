import gtk
import pickle
import logging

from kiwi.ui.delegates import GladeSlaveDelegate
from kiwi.ui.objectlist import Column
from kiwi.ui.widgets.contextmenu import ContextMenu, ContextMenuItem

from package.domain.file import File, InstallScript


log = logging.getLogger('FileTree')

class FileTree(GladeSlaveDelegate):
    gladefile = "filetree"
    widgets = ["fileTree",
               "ok_button",
               "cancel_button",
               "editbox"]

    _changed = None
    _file = None

    TARGETS = [('FILE_TREE_ROW', gtk.TARGET_SAME_WIDGET, 1)]

    def __init__(self, model=None, scripts=None, statusbar=None):
        GladeSlaveDelegate.__init__(self, gladefile=self.gladefile)

        assert model, "Model should not be None"
        self.model = model

        self.statusbar = statusbar

        self.fileTree.set_columns([Column('name', data_type=str, searchable=True, 
                                   expand=True)])

        #XXX: This argument is not necessary anymore since we should use model data to fill list
        if scripts:
            self._set_message("")
            self._fill(scripts)

        self._enable_drag_and_drop()
        self._setup_context_menu()

    def _show(self):
        self.show_all()
        gtk.main()

    #
    # Setup Drag N Drop and menus
    #

    def _enable_drag_and_drop(self):
        log.debug("enabling dnd...")
        self.fileTree._treeview.connect('drag_data_get',
                               self._on_fileTree__drag_data_get)
        self.fileTree._treeview.connect("drag_data_received",
                              self._on_fileTree__drag_data_received)
        self.fileTree._treeview.enable_model_drag_dest(self.TARGETS,
            gtk.gdk.ACTION_MOVE)

        self.fileTree._treeview.enable_model_drag_source(
            gtk.gdk.BUTTON1_MASK, self.TARGETS,
            gtk.gdk.ACTION_DEFAULT| gtk.gdk.ACTION_MOVE)

    def _on_fileTree__drag_data_get(self, treeview, context, selection, target_id,
                                    etime):
        log.debug('Drag data get event ' + str([treeview, context, selection, target_id, etime]))

        self._clean()
        data_object = self.fileTree.get_selected()
        #model, iter = treeview.get_selection().get_selected()
        #data_object = model.get_value(iter, 0)

        # Root objects cannot be dragged.
        is_root = self._is_script(data_object)
        if is_root:
            self._set_message("Somente o conteudo dos scripts pode ser movido")
            context.drag_abort(etime)
            return False

        data = pickle.dumps(data_object)
        selection.set(selection.target, 8, data)
        log.debug('Drag data get event done.')

    def _on_fileTree__drag_data_received(self, treeview, context, x, y, selection,
                                              info, etime):
        log.debug('Drag data received event ' + str([treeview, context, x, y, selection, info, etime]))
        model = treeview.get_model()
        if not selection.data:
            context.finish(False, False, etime)
            return False

        data = pickle.loads(selection.data)

        drop_info = treeview.get_dest_row_at_pos(x, y)
        if drop_info:
            path, position = drop_info
            iter = model.get_iter(path)
            parent = model.get_value(iter, 0)

            data_object = model.get_value(iter, 0)
            can_be_root = self._is_script(data_object)

            if (position == gtk.TREE_VIEW_DROP_BEFORE):

                depth = self.fileTree.get_model().iter_depth(iter)
                if depth == 0:
                    self._set_message("O arquivo deve ser movido para um script de instalacao")
                    return False
                model.insert_before(None, iter, [data])

            elif (position == gtk.TREE_VIEW_DROP_INTO_OR_BEFORE
                 or position == gtk.TREE_VIEW_DROP_INTO_OR_AFTER) \
                 and can_be_root:
                self.fileTree.append(parent, data)
            else:

                depth = self.fileTree.get_model().iter_depth(iter)
                if depth == 0:
                    self._set_message("O arquivo deve ser movido para um script de instalacao")
                    return False

                model.insert_after(None, iter, [data])
        else:
            self._set_message("O arquivo deve ser movido para um script de instalacao")
            return False
        if context.action == gtk.gdk.ACTION_MOVE:
            context.finish(True, True, etime)
        log.debug('Drag data received event finished')        
        self._update_model()
        return True

    def _setup_context_menu(self):
        menu = ContextMenu()        
 
        item = ContextMenuItem('Editar', stock=gtk.STOCK_EDIT)
        item.connect('activate', self._on_context_edit__activate)
        item.connect('can-disable', self._on_context_edit__can_disable)
        menu.append(item)

        self.fileTree.set_context_menu(menu)
        menu.show_all()

    #
    # Data processing
    #

    def _fill(self, scripts):
        for script in scripts:
            self.append(script)
        self._update_model()

    def append(self, data, parent=None):
        if self._is_script(data):
            self.fileTree.append(None, data)
            for c in data.content:
                self.append(c, data)
            # Don't know if it is necessary yet
            # Maybe if we need to reconstruct the files after moving
        else:
            self.fileTree.append(parent, data)

    def _is_script(self, data):
        return hasattr(data, 'content')


    def _clean(self):
        self._set_message("")

    def _set_message(self, message):
        if self.statusbar:
            self.statusbar.push(0, message)

    def get_data(self):
        """ Returns tree data into a list of L{InstallScript}.
            @return list of L{InstallScript}
        """
        # Cannot use kiwi get_descendants because it does not respect
        # the order of tree elements.
        root_nodes = [m.iter for m in self.fileTree.get_model()]
        model = self.fileTree.get_model()
        scripts = []
        for root in root_nodes:
            script = model.get_value(root, 0)
            assert self._is_script(script), "Only InstallScript instances should be root nodes"
            script.content = [model.get_value(model.iter_nth_child(root, i), 0) for i in range(model.iter_n_children(root))]

            scripts.append(script)

        return scripts

    def _update_model(self):
        # This is not optimized but since the list is often small
        # it is ok for now
        for item in self.model.scripts[:]:
            self.model.scripts.remove(item)
        self.model.scripts = self.get_data()

    #
    # Callbacks
    #

    def on_ok_button__clicked(self, *args):
        new_name = self.new_name.get_text()
        self.new_name.set_text('')
        self.editbox.hide()
        selected_item = self.fileTree.get_selected()
        selected_item.name = new_name

    def on_cancel_button__clicked(self, *args):
        self.editbox.hide()

    def _on_context_edit__activate(self, *args):
        selected = self.fileTree.get_selected()
        self.editbox.show()

    def _on_context_edit__can_disable(self, *args):
        selected = self.fileTree.get_selected()
        disable = True
        if selected and self._is_script(selected):
            disable = False

        return disable


