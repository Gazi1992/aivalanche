from PySide6.QtWidgets import QWidget, QFrame
from PySide6.QtCore import Signal
from aivalanche_app.components.custom_layouts import v_layout, h_layout
from aivalanche_app.components.buttons.icon_text_button import icon_text_button
from aivalanche_app.components.navigation_header import navigation_header
from aivalanche_app.data_store.store import store
from aivalanche_app.components.calibration_tabs import calibration_tabs
from aivalanche_app.constants.dimensions import CALIBRATION_TAB_BUTTON_WIDTH, CALIBRATION_TAB_BUTTON_HEIGHT

class my_calibration(QWidget):
    go_to_projects = Signal()
    go_to_models = Signal()
    
    def __init__(self, parent = None, store: store = None, object_name: str = None):
        super().__init__(parent)
        
        self.store = store
        
        if object_name is not None:
            self.setObjectName(object_name)
        
        self.init_ui()
        
        
    def init_ui(self):
        layout = v_layout(self)
        self.setLayout(layout)

        # Header Section
        self.header_navigation = [{'text': 'Projects', 'on_click': self.on_projects_press},
                                  {'text': self.store.active_project.title if self.store.active_project is not None else 'Models', 'on_click': self.on_models_press},
                                  {'text': self.store.active_model.title if self.store.active_model is not None else 'My model', 'on_click': None}]
        self.header_widget = navigation_header(navigation_path = self.header_navigation, object_name = 'header', show_calibration_buttons = True)
        layout.addWidget(self.header_widget)
        self.update_header()
        
        # Calibration buttons bar
        buttons_frame = QFrame(self)
        buttons_frame.setObjectName('calibration_header_frame')
        buttons_layout = h_layout()
        buttons_frame.setLayout(buttons_layout)
        layout.addWidget(buttons_frame)
                    
        # Reference data button    
        self.reference_data_button = icon_text_button(parent = self, text = 'Reference data', checkable = True, on_click = self.on_reference_data_click, button_height = CALIBRATION_TAB_BUTTON_HEIGHT, button_width = CALIBRATION_TAB_BUTTON_WIDTH, object_name = 'calibration_header_button')
        buttons_layout.addWidget(self.reference_data_button)
        buttons_layout.addStretch()
        
        # Model button    
        self.model_button = icon_text_button(parent = self, text = 'Model', checkable = True, on_click = self.on_model_click, button_height = CALIBRATION_TAB_BUTTON_HEIGHT, button_width = CALIBRATION_TAB_BUTTON_WIDTH, object_name = 'calibration_header_button')
        buttons_layout.addWidget(self.model_button)
        buttons_layout.addStretch()

        # Parameters button    
        self.parameters_button = icon_text_button(parent = self, text = 'Parameters', checkable = True, on_click = self.on_parameters_click, button_height = CALIBRATION_TAB_BUTTON_HEIGHT, button_width = CALIBRATION_TAB_BUTTON_WIDTH, object_name = 'calibration_header_button')
        buttons_layout.addWidget(self.parameters_button)
        buttons_layout.addStretch()

        # Optimizer button    
        self.optimization_button = icon_text_button(parent = self, text = 'Optimization settings', checkable = True, on_click = self.on_optimizer_click, button_height = CALIBRATION_TAB_BUTTON_HEIGHT, button_width = CALIBRATION_TAB_BUTTON_WIDTH, object_name = 'calibration_header_button')
        buttons_layout.addWidget(self.optimization_button)
        buttons_layout.addStretch()

        # Results button    
        self.results_button = icon_text_button(parent = self, text = 'Results', checkable = True, on_click = self.on_results_click, button_height = CALIBRATION_TAB_BUTTON_HEIGHT, button_width = CALIBRATION_TAB_BUTTON_WIDTH, object_name = 'calibration_header_button')
        buttons_layout.addWidget(self.results_button)
        
        # Calibration tabs
        layout.addSpacing(20)
        self.calibration_tabs = calibration_tabs(parent = self, store = self.store, object_name = 'calibration_tabs')
        layout.addWidget(self.calibration_tabs)
        
        self.reference_data_button.click()
    
    
    # Update header
    def update_header(self):
        self.header_navigation = [{'text': 'Projects', 'on_click': self.on_projects_press},
                                  {'text': self.store.active_project.title if self.store.active_project is not None else 'Models', 'on_click': self.on_models_press},
                                  {'text': self.store.active_model.title if self.store.active_model is not None else 'My model', 'on_click': None}]
        self.header_widget.update_navigation_path(self.header_navigation)
        
    def on_models_press(self, m):
        self.go_to_models.emit()
        
    def on_projects_press(self, m):
        self.go_to_projects.emit()
        
    def on_reference_data_click(self, checked):
        if checked:
            self.model_button.setChecked(False)
            self.parameters_button.setChecked(False)
            self.optimization_button.setChecked(False)
            self.results_button.setChecked(False)
            self.calibration_tabs.set_active_tab('reference_data')
        else:
            self.reference_data_button.setChecked(True)
        
    def on_model_click(self, checked):
        if checked:
            self.reference_data_button.setChecked(False)
            self.parameters_button.setChecked(False)
            self.optimization_button.setChecked(False)
            self.results_button.setChecked(False)
            self.calibration_tabs.set_active_tab('model')
        else:
            self.model_button.setChecked(True)
        
    def on_parameters_click(self, checked):
        if checked:
            self.reference_data_button.setChecked(False)
            self.model_button.setChecked(False)
            self.optimization_button.setChecked(False)
            self.results_button.setChecked(False)
            self.calibration_tabs.set_active_tab('parameters')
        else:
            self.parameters_button.setChecked(True)
    
    def on_optimizer_click(self, checked):
        if checked:
            self.reference_data_button.setChecked(False)
            self.model_button.setChecked(False)
            self.parameters_button.setChecked(False)
            self.results_button.setChecked(False)
            self.calibration_tabs.set_active_tab('optimizer')
        else:
            self.optimization_button.setChecked(True)
        
    def on_results_click(self, checked):
        if checked:
            self.reference_data_button.setChecked(False)
            self.model_button.setChecked(False)
            self.parameters_button.setChecked(False)
            self.optimization_button.setChecked(False)
            self.calibration_tabs.set_active_tab('results')
        else:
            self.results_button.setChecked(True)
        
        
        
        
        
        
        
        
        
        