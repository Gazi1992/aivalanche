from PySide6.QtWidgets import QWidget, QFrame
from PySide6.QtCore import Qt
from aivalanche_app.components.custom_layouts import v_layout, h_layout
from aivalanche_app.data_store.store import store
from aivalanche_app.components.results_tabs import results_tabs
from aivalanche_app.constants.dimensions import CALIBRATION_TAB_BUTTON_WIDTH, CALIBRATION_TAB_BUTTON_HEIGHT
from aivalanche_app.components.buttons.icon_text_button import icon_text_button


class results_tab(QWidget):
    
    def __init__(self, parent = None, store: store = None, object_name: str = None):
        super().__init__(parent = parent)
        
        if object_name is not None:
            self.setObjectName(object_name)
        
        self.store = store
        self.style = self.store.style
        
        self.init_ui()
        
    
    def init_ui(self):
        layout = v_layout()
        self.setLayout(layout)
        
        header_layout = h_layout(alignment = Qt.AlignmentFlag.AlignRight)
        header_layout.addStretch()
        layout.addLayout(header_layout)
        
        # buttons bar
        buttons_frame = QFrame(self)
        buttons_frame.setObjectName('calibration_header_frame')
                
        # buttons layout
        buttons_layout = h_layout()
        buttons_frame.setLayout(buttons_layout)
        header_layout.addWidget(buttons_frame)
        
        # results progress button    
        self.results_progress_button = icon_text_button(parent = self, text = 'Progress', checkable = True, on_click = self.on_results_progress_click, button_height = CALIBRATION_TAB_BUTTON_HEIGHT, button_width = CALIBRATION_TAB_BUTTON_WIDTH / 2, object_name = 'calibration_header_button')
        buttons_layout.addWidget(self.results_progress_button)
        
        # results data button    
        self.results_data_button = icon_text_button(parent = self, text = 'Data', checkable = True, on_click = self.on_results_data_click, button_height = CALIBRATION_TAB_BUTTON_HEIGHT, button_width = CALIBRATION_TAB_BUTTON_WIDTH / 2, object_name = 'calibration_header_button')
        buttons_layout.addWidget(self.results_data_button)
        
        # data and progress tabs
        layout.addSpacing(10)
        self.tabs = results_tabs(parent = self, store = self.store)
        layout.addWidget(self.tabs)
        
        self.results_progress_button.click()
        
    def on_results_data_click(self, checked):
        if checked:
            self.results_progress_button.setChecked(False)
            self.tabs.set_active_tab('results_data_tab')
        else:
            self.reference_data_button.setChecked(True)
        
    def on_results_progress_click(self, checked):
        if checked:
            self.results_data_button.setChecked(False)
            self.tabs.set_active_tab('results_progress_tab')
        else:
            self.results_progress_button.setChecked(True)