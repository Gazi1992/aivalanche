from PySide6.QtWidgets import QTabWidget
from aivalanche_app.screens.projects.projects_tab import projects_tab
from aivalanche_app.screens.running.running_tab import running_tab
from aivalanche_app.resources.themes.style import style
from aivalanche_app.data_store.store import store

class main_tabs(QTabWidget):
    
    def __init__(self, parent = None, store: store = None, object_name: str = None):
        super().__init__(parent)
        
        self.store = store
        self.setContentsMargins(0, 0, 0, 0)
        self.setDocumentMode(True)
        
        if object_name is not None:
            self.setObjectName(object_name)

        # Create tabs for the QTabWidget
        self.projects_tab = projects_tab(parent = self, store = self.store, object_name = 'projects_tab')
        self.running_tab = running_tab(parent = self, store = self.store, object_name = 'running_tab')

        self.addTab(self.projects_tab, "Projects")
        self.addTab(self.running_tab, "Running")

        # Hide the tab bar
        for i in range(2):
            self.setTabVisible(i, False)

    
    def set_active_tab(self, tab: str = None):
        if tab == 'projects':
            self.setCurrentWidget(self.projects_tab)
        elif tab == 'running':
            self.setCurrentWidget(self.running_tab)