from PySide6.QtWidgets import QTabWidget
from aivalanche_app.data_store.store import store
from aivalanche_app.screens.calibration.reference_data_tab import reference_data_tab
from aivalanche_app.screens.calibration.model_tab import model_tab
from aivalanche_app.screens.calibration.parameters_tab import parameters_tab
from aivalanche_app.screens.calibration.optimization_tab import optimization_tab
from aivalanche_app.screens.calibration.results_tab import results_tab

class calibration_tabs(QTabWidget):
    
    def __init__(self, parent = None, store: store = None, object_name: str = None, on_warning: callable = None):
        super().__init__(parent)
        
        if object_name is not None:
            self.setObjectName(object_name)
        
        self.store = store
        self.setContentsMargins(0, 0, 0, 0)
        self.setDocumentMode(True)

        # Create tabs for the QTabWidget
        self.reference_data_tab = reference_data_tab(parent = self, store = self.store, object_name = 'reference_data_tab')
        self.model_tab = model_tab(parent = self, store = self.store, object_name = 'model_tab')
        self.parameters_tab = parameters_tab(parent = self, store = self.store, object_name = 'parameters_tab')
        self.optimization_tab = optimization_tab(parent = self, store = self.store, object_name = 'optimization_tab')
        self.results_tab = results_tab(parent = self, store = self.store, object_name = 'results_tab')

        self.addTab(self.reference_data_tab, "Reference data")
        self.addTab(self.model_tab, "Model")
        self.addTab(self.parameters_tab, "Parameters")
        self.addTab(self.optimization_tab, "Optimizer")
        self.addTab(self.results_tab, "Results")
        
        # Connect warning signals
        if on_warning is not None:
            self.reference_data_tab.reference_data_warning.connect(on_warning)
        
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
            self.setCurrentWidget(self.optimization_tab)
        elif tab == 'results':
            self.setCurrentWidget(self.results_tab)
            
            
            
            
            