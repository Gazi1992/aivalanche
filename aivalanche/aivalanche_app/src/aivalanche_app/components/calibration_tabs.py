from PySide6.QtWidgets import QTabWidget
from aivalanche_app.resources.themes.style import style
from aivalanche_app.data_store.store import store
from aivalanche_app.screens.calibration.reference_data_tab import reference_data_tab
from aivalanche_app.screens.calibration.model_tab import model_tab
from aivalanche_app.screens.calibration.parameters_tab import parameters_tab
from aivalanche_app.screens.calibration.optimizer_tab import optimizer_tab
from aivalanche_app.screens.calibration.results_tab import results_tab

class calibration_tabs(QTabWidget):
    
    def __init__(self, parent = None, store: store = None, style : style = None):
        super().__init__(parent)
        
        self.store = store
        self.style = style
        
        self.setContentsMargins(0, 0, 0, 0)

        # Create tabs for the QTabWidget
        self.reference_data_tab = reference_data_tab(parent = self, store = self.store, style = self.style)
        self.model_tab = model_tab(parent = self, store = self.store)
        self.parameters_tab = parameters_tab(parent = self, store = self.store)
        self.optimizer_tab = optimizer_tab(parent = self, store = self.store)
        self.results_tab = results_tab(parent = self, store = self.store)

        self.addTab(self.reference_data_tab, "Reference data")
        self.addTab(self.model_tab, "Model")
        self.addTab(self.parameters_tab, "Parameters")
        self.addTab(self.optimizer_tab, "Optimizer")
        self.addTab(self.results_tab, "Results")
        
        # Hide the tab bar
        for i in range(5):
            self.setTabVisible(i, False)

    
    def set_active_tab(self, tab: str = None):
        if tab == 'reference_data':
            self.setCurrentWidget(self.reference_data_tab)
        elif tab == 'model':
            self.setCurrentWidget(self.model_tab)
        elif tab == 'parameters':
            self.setCurrentWidget(self.parameters_tab)
        elif tab == 'optimizer':
            self.setCurrentWidget(self.optimizer_tab)
        elif tab == 'results':
            self.setCurrentWidget(self.results_tab)
            
            
            
            
            