from PyQt4 import QtCore, QtGui
Qt = QtCore.Qt

from ..utils import debug
from .base import Node


class SGFSRoots(Node):
    
    def update(self, *args):
        super(SGFSRoots, self).update(*args)
        self.view_data.setdefault('header', 'SGFS Project')
        
    @staticmethod
    def is_next_node(state):
        return 'Project' not in state
    
    def child_matches_initial_state(self, child, init_state):
        return 'Project' in init_state and init_state['Project'] == child.state['Project']
    
    # We override the master here since we can return children very quickly.
    def fetch_children(self, init_state):
        for project, path in self.model.sgfs.project_roots.iteritems():
            yield (
                project.cache_key,
                {
                    Qt.DisplayRole: project['name'],
                    Qt.DecorationRole: '/home/mboers/Documents/icons/fatcow/16x16/newspaper.png',
                }, {
                    'Project': project,
                    'self': project,
                },
            )
