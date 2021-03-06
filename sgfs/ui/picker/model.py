import traceback

from PyQt4 import QtCore, QtGui
Qt = QtCore.Qt

from uitools.headeredlistview import HeaderDisplayRole

from sgfs import SGFS
from .nodes.base import Group, Leaf
from .utils import debug, icon
from ..threadpool import ThreadPool


class Model(QtCore.QAbstractItemModel):
    
    _pixmaps = {}
    
    def __init__(self, root_state=None, sgfs=None, shotgun=None, session=None):
        super(Model, self).__init__()
        
        self._root_state = root_state or {}
        self._root = None
        
        self.sgfs = sgfs or SGFS(shotgun=shotgun, session=session)
        
        # Force a more reasonable timeout. Note that this does change the
        # global parameters on the shotgun object.
        self.sgfs.session.shotgun.close()
        self.sgfs.session.shotgun.config.timeout_secs = 5
        self.sgfs.session.shotgun.config.max_rpc_attempts = 1
        
        self.threadpool = ThreadPool(8, lifo=True)
        
        self._node_types = []
    
    def _thread_target(self):
        while True:
            try:
                func, args, kwargs = self._thread_queue.get()
                func(*args, **kwargs)
            except Exception:
                traceback.print_exc()
        
    def register_node_type(self, node_type):
        self._node_types.append(node_type)
    
    def index_from_state(self, state):
        
        # debug('index_from_state %r', sorted(state))
        
        last_match = None
        nodes = [self.root()]
        while True:
            
            if not nodes:
                break
            
            node = nodes.pop(0)
            
            # Skip over groups. It would be nice if the group class would be
            # able to property handle this logic, but we don't want a "positive
            # match" (for the purposes of traversing the group) to result in
            # not selecting something real (because it is at a lower level than
            # the last group).
            if isinstance(node, Group):
                nodes.extend(node.children())
                continue
            
            # debug('match?: %r <- %r', node, sorted(node.state))

            if node.parent is None or node.parent.child_matches_initial_state(node, state):
                # debug('YES!!')
            
                # Trigger initial async.
                node.children()
                
                node.add_raw_children(node.get_temp_children_from_state(state))
                nodes.extend(node.children())
                
                last_match = node
        
        if last_match:
            return last_match.index
    
    def construct_node(self, key, view_data, state):
        for node_type in self._node_types:
            try:
                return node_type(self, key, view_data, state)
            except TypeError:
                pass
        return Leaf(self, key, view_data, state)
        
    def hasChildren(self, index):
        node = self.node_from_index(index)
        return not node.is_leaf()
    
    def root(self):
        if self._root is None:
            self._root = self.construct_node(None, {}, self._root_state)
            self._root.index = QtCore.QModelIndex()
            self._root.parent = None
        return self._root
    
    def node_from_index(self, index):
        return index.internalPointer() if index.isValid() else self.root()
    
    def rowCount(self, parent):
        node = self.node_from_index(parent)
        return len(node.children())
    
    def columnCount(self, parent):
        return 1
    
    def index(self, row, col, parent):
        
        if col > 0:
            return QtCore.QModelIndex()
        
        node = self.node_from_index(parent)
        try:
            child = node.children()[row]
        except IndexError:
            return QtCore.QModelIndex()
        
        if child.index is None:
            debug('child.index is None: %r -> %r', child, child.state)
            child.index = self.createIndex(row, col, child)
            if child.parent is None:
                debug('\tchild.parent is also None')
                child.parent = node
        
        return child.index
    
    def parent(self, child):
        node = self.node_from_index(child)
        if node.parent is not None:
            return node.parent.index
        else:
            return QtCore.QModelIndex()
    
    def flags(self, index):

        if not index.isValid():
            return QtCore.QVariant()
        node = self.node_from_index(index)

        if node.view_data.get('disabled'):
            return Qt.NoItemFlags
        else:
            return super(Model, self).flags(index)
        

    def data(self, index, role):
        
        if not index.isValid():
            return QtCore.QVariant()

        node = self.node_from_index(index)
        
        if role == Qt.DisplayRole:
            try:
                return node.view_data[Qt.DisplayRole]
            except KeyError:
                return QtCore.QVariant()
        
        if role == Qt.DecorationRole:
            
            if node.error_count:
                return icon('fatcow/cross')
            
            if node.is_loading:
                return icon('fatcow/arrow_refresh')
            
            node = self.node_from_index(index)
            data = node.view_data.get(Qt.DecorationRole)
            
            if data is None:
                return QtCore.QVariant()
            
            if isinstance(data, QtGui.QColor):
                key = (data.red(), data.green(), data.blue())
                if key not in self._pixmaps:
                    pixmap = QtGui.QPixmap(16, 16)
                    pixmap.fill(Qt.transparent)
                    painter = QtGui.QPainter(pixmap)
                    brush = QtGui.QBrush(data)
                    painter.setBrush(brush)
                    painter.setPen(data.darker())
                    painter.drawRect(2, 2, 12, 12)
                    painter.end()
                    self._pixmaps[key] = pixmap
                return self._pixmaps[key]
            
            if isinstance(data, basestring):
                try:
                    return self._pixmaps[data]
                except KeyError:
                    pass
                self._pixmaps[data] = pixmap = icon(data) or QtGui.QPixmap(data)
                return pixmap
            
            return data
        
        if role == Qt.FontRole:
            if node.view_data.get(Qt.FontRole) is not None:
                return node.view_data[Qt.FontRole]
            return QtCore.QVariant()
        
        if role == Qt.ForegroundRole:
            if node.error_count:
                return QtGui.QColor.fromRgb(128, 0, 0)
        
        if role == HeaderDisplayRole:
            try:
                return node.view_data['header']
            except KeyError:
                pass

        # Passthrough other roles.
        try:
            return node.view_data[role]
        except KeyError:
            return QtCore.QVariant()

