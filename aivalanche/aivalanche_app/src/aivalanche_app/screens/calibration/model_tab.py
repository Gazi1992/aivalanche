from PySide6.QtWidgets import QWidget, QScrollArea, QButtonGroup
from PySide6.QtCore import Qt
from aivalanche_app.components.custom_layouts import v_layout, h_layout, g_layout
from aivalanche_app.data_store.store import store
from aivalanche_app.components.combo_box_load_data import combo_box_load_data
from aivalanche_app.components.custom_label import custom_label
from aivalanche_app.components.custom_radio_button import custom_radio_button

MODEL_TEMPLATES = {'Transistors': ['BSIM4', 'BSIM3', 'BSIMBULK', 'BSIM CMG', 'Level 1', 'Level 3'],
                   'Pasive elements': ['Resistor', 'Capacitor', 'Inductor', 'Diode']}

TESTBENCH_TEMPLATES = ['id_vd_vg', 'id_vb_vd', 'cgd_vg_vd', 'cgs_vg_vd', 'ciss_vd_vg']


class model_tab(QWidget):
    
    def __init__(self, parent = None, store: store = None, object_name: str = None):
        super().__init__(parent)
        
        if object_name is not None:
            self.setObjectName(object_name)
        
        self.store = store

        self.init_ui()


    def init_ui(self):
        
        self.model_buttons_group = QButtonGroup(self)
        self.model_buttons_group.buttonClicked.connect(self.on_model_template_clicked)
        
        self.testbench_buttons_group = QButtonGroup(self)
        self.testbench_buttons_group.buttonClicked.connect(self.on_testbench_template_clicked)

        layout = h_layout(spacing = 40)
        self.setLayout(layout)

        # Create left scroll area
        left_scroll_area = QScrollArea()
        left_scroll_area.setContentsMargins(0, 0, 0, 0)
        left_scroll_area.setWidgetResizable(True)
        layout.addWidget(left_scroll_area)
        
        # Create left widget
        left_widget = QWidget(self)
        left_layout = v_layout(spacing = 20, alignment = Qt.AlignmentFlag.AlignTop)
        left_widget.setLayout(left_layout)
        left_scroll_area.setWidget(left_widget)
        
        # Model label
        model_label = custom_label(parent = self, text = 'Model', font_size = 'huge', opacity = 0.5)
        left_layout.addWidget(model_label)

        # Custom model button
        custom_model_button = custom_radio_button(parent = self, text = 'Custom model', group = self.model_buttons_group)
        left_layout.addWidget(custom_model_button)
        
        # Create load model combo box
        self.load_model_widget = combo_box_load_data(parent = self, caption = 'Select model file', filter = 'cir file (*.cir)', is_enabled = False)
        left_layout.addWidget(self.load_model_widget)
        
        # Add the model templates
        for item in MODEL_TEMPLATES.keys():
            layout_temp = v_layout(spacing = 15) 
            label = custom_label(parent = self, text = item, font_size = 'normal')
            layout_temp.addWidget(label)

            grid_layout_temp = g_layout( vertical_spacing = 10)
            for index, val in enumerate(MODEL_TEMPLATES[item]):
                button_temp = custom_radio_button(parent = self, text = val, group = self.model_buttons_group)
                row = index // 3
                col = index % 3
                grid_layout_temp.addWidget(button_temp, row, col)
            
            layout_temp.addLayout(grid_layout_temp)
            
            left_layout.addLayout(layout_temp)
        
        # Create right scroll area
        right_scroll_area = QScrollArea()
        right_scroll_area.setContentsMargins(0, 0, 0, 0)
        right_scroll_area.setWidgetResizable(True)
        layout.addWidget(right_scroll_area)
        
        # Create right widget
        right_widget = QWidget(self)
        right_layout = v_layout(spacing = 20, alignment = Qt.AlignmentFlag.AlignTop)
        right_widget.setLayout(right_layout)
        right_scroll_area.setWidget(right_widget)
        
        # Testbench label
        testbench_label = custom_label(parent = self, text = 'Testbench', font_size = 'huge', opacity = 0.5)
        right_layout.addWidget(testbench_label)
        
        # Custom testbenches button
        custom_testbenches_button = custom_radio_button(parent = self, text = 'Custom testbenches', group = self.testbench_buttons_group)
        right_layout.addWidget(custom_testbenches_button)
        
        # Create load testbench combo box
        self.load_testbenches_widget = combo_box_load_data(parent = self, caption = 'Select testbenches file', filter = 'json file (*.json)', is_enabled = False)
        right_layout.addWidget(self.load_testbenches_widget)
        
        # Add the testbench templates
        grid_layout_temp = g_layout( vertical_spacing = 10)
        for index, val in enumerate(TESTBENCH_TEMPLATES):
            button_temp = custom_radio_button(parent = self, text = val, group = self.testbench_buttons_group)
            row = index // 3
            col = index % 3
            grid_layout_temp.addWidget(button_temp, row, col)
            
        right_layout.addLayout(grid_layout_temp)
        
    
    def on_model_template_clicked(self, button):
        if button.text() == 'Custom model':
            self.load_model_widget.set_state(True)
        else:
            self.load_model_widget.set_state(False)


    def on_testbench_template_clicked(self, button):
        if button.text() == 'Custom testbenches':
            self.load_testbenches_widget.set_state(True)
        else:
            self.load_testbenches_widget.set_state(False)
