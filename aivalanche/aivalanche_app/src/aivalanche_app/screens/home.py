from PySide6.QtWidgets import QSplitter
from PySide6.QtCore import Signal
from aivalanche_app.components.main_tabs import main_tabs
from aivalanche_app.components.drawer import drawer
from aivalanche_app.data_store.store import store


class home(QSplitter):   
    
    go_to_log_in = Signal()
    
    def __init__(self, parent = None, store: store = None, object_name: str = None):
        super().__init__(parent = parent)
        self.store = store
        if object_name is not None:
            self.setObjectName(object_name)
        self.init_ui()


    def init_ui(self):

        # Create the drawer on the left
        drawer_widget = drawer(parent = self, user = self.store.user, object_name = 'drawer')
        
        # Create a main tabs on the right
        self.tab_widget = main_tabs(parent = self, store = self.store, object_name = 'main_tabs')
        
        # Set stretch factors to ensure the drawer widget takes minimum space
        self.setStretchFactor(0, 0)
        self.setStretchFactor(1, 1)
        
        # Connect the drawer buttons to their respoctive actions
        drawer_widget.projects_active.connect(lambda: self.set_active_tab('projects'))
        drawer_widget.running_active.connect(lambda: self.set_active_tab('running'))
        drawer_widget.logout_active.connect(self.on_log_out_press)
        
        # Set projects as active tab
        drawer_widget.set_projects_active()        

        
    def set_active_tab(self, tab: str = None):
        self.tab_widget.set_active_tab(tab)
        
    def on_log_out_press(self):
        self.go_to_log_in.emit()
        
    def fetch_projects(self):
        self.tab_widget.fetch_projects()