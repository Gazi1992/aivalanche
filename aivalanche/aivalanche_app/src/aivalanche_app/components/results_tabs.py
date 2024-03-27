from PySide6.QtWidgets import QTabWidget
from aivalanche_app.data_store.store import store
from aivalanche_app.screens.calibration.results_data_tab import results_data_tab
from aivalanche_app.screens.calibration.results_progress_tab import results_progress_tab

class results_tabs(QTabWidget):
    
    def __init__(self, parent = None, store: store = None, object_name: str = None):
        super().__init__(parent)
        
        if object_name is not None:
            self.setObjectName(object_name)
        
        self.store = store
        self.setContentsMargins(0, 0, 0, 0)
        self.setDocumentMode(True)

        # Create tabs for the QTabWidget
        self.results_progress_tab = results_progress_tab(parent = self, store = self.store, object_name = 'results_progress_tab')
        self.results_data_tab = results_data_tab(parent = self, store = self.store, object_name = 'results_data_tab')

        self.addTab(self.results_progress_tab, "Results progress")
        self.addTab(self.results_data_tab, "Results data")
        
        # Hide the tab bar
        for i in range(2):
            self.setTabVisible(i, False)

    
    def set_active_tab(self, tab: str = None):
        if tab == 'results_data_tab':
            self.setCurrentWidget(self.results_data_tab)
        elif tab == 'results_progress_tab':
            self.setCurrentWidget(self.results_progress_tab)
            
            
            
            
            