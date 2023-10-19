from PySide6.QtWidgets import QTabWidget
from aivalanche_app.screens.projects.projects_tab import projects_tab
from aivalanche_app.screens.running.running_tab import running_tab
from aivalanche_app.resources.themes.style import style
from aivalanche_app.data_store.store import store

class main_tabs(QTabWidget):
    
    def __init__(self, parent = None, store: store = None, style: style = None):
        super().__init__(parent)
        
        self.store = store
        self.style = style
        
        self.setContentsMargins(0, 0, 0, 0)

        # Create tabs for the QTabWidget
        self.projects_tab = projects_tab(parent = self, store = self.store, style = self.style)
        self.running_tab = running_tab(parent = self, store = self.store, style = self.style)

        self.addTab(self.projects_tab, "Projects")
        self.addTab(self.running_tab, "Running")

        # Hide the tab bar
        for i in range(2):
            self.setTabVisible(i, False)
            
        self.setStyleSheet(self.style.main_tabs)
    
    def set_active_tab(self, tab: str = None):
        if tab == 'projects':
            self.setCurrentWidget(self.projects_tab)
        elif tab == 'running':
            self.setCurrentWidget(self.running_tab)