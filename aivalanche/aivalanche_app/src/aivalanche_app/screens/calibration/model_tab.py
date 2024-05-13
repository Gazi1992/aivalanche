from PySide6.QtWidgets import QWidget, QScrollArea, QButtonGroup
from PySide6.QtCore import Qt
from aivalanche_app.components.custom_layouts import v_layout, h_layout, g_layout, clear_layout
from aivalanche_app.data_store.store import store
from aivalanche_app.components.combo_box_load_data import combo_box_load_data
from aivalanche_app.components.custom_label import custom_label
from aivalanche_app.components.custom_radio_button import custom_radio_button
from aivalanche_app.components.custom_checkbox_with_text import custom_checkbox_with_text


class model_tab(QWidget):
    
    def __init__(self, parent = None, store: store = None, object_name: str = None):
        super().__init__(parent)
        
        if object_name is not None:
            self.setObjectName(object_name)
        
        self.store = store
        self.store.fetch_model_templates_end.connect(self.update_model_templates)
        
        self.model = None
        self.testbenches = []

        self.init_ui()


    def init_ui(self):
        
        self.testbench_checkboxes = []
        self.model_radiobuttons = []
        
        self.model_buttons_group = QButtonGroup(self)
        self.model_buttons_group.buttonClicked.connect(self.on_model_template_clicked)
        
        layout = h_layout(spacing = 40)
        self.setLayout(layout)

        # Create left scroll area
        scroll_area = QScrollArea()
        scroll_area.setContentsMargins(0, 0, 0, 0)
        scroll_area.setWidgetResizable(True)
        layout.addWidget(scroll_area)
        
        # Create left widget
        scroll_widget = QWidget(self)
        scroll_layout = v_layout(spacing = 20, alignment = Qt.AlignmentFlag.AlignTop)
        scroll_widget.setLayout(scroll_layout)
        scroll_area.setWidget(scroll_widget)
        
        # Custom model button
        custom_model_button = custom_radio_button(parent = self, text = 'Custom model', group = self.model_buttons_group)
        scroll_layout.addWidget(custom_model_button)
        
        # Create load model combo box
        self.load_model_widget = combo_box_load_data(parent = self,
                                                     caption = 'Select model file',
                                                     filter = 'cir file (*.cir)',
                                                     placeholder = 'Select model file',
                                                     is_enabled = False,
                                                     object_name = 'round_combo_box')
        scroll_layout.addWidget(self.load_model_widget)
        
        # Create load testbench combo box
        self.load_testbenches_widget = combo_box_load_data(parent = self,
                                                           caption = 'Select testbenches file',
                                                           filter = 'json file (*.json)',
                                                           placeholder = 'Select testbenches file',
                                                           is_enabled = False,
                                                           object_name = 'round_combo_box')
        scroll_layout.addWidget(self.load_testbenches_widget)
        
        # Templates label
        templates_label = custom_label(parent = self, text = 'Templates', font_size = 'huge', opacity = 0.5)
        scroll_layout.addWidget(templates_label)
        
        self.model_templates_layout = v_layout(spacing = 20, alignment = Qt.AlignmentFlag.AlignTop)
        scroll_layout.addLayout(self.model_templates_layout)

    
    def update_model_templates(self, data):
        clear_layout(self.model_templates_layout)
        if not self.store.model_templates.empty:
            groups = self.store.model_templates.groupby('category')
            for (category), group  in groups:
                layout_temp = v_layout(spacing = 15) 
                label = custom_label(parent = self, text = category, font_size = 'normal')
                layout_temp.addWidget(label)
    
                grid_layout_temp = g_layout( vertical_spacing = 10)
                for index, row in group.iterrows():
                    button_temp = custom_radio_button(parent = self, text = row['name'], group = self.model_buttons_group)
                    row = index // 3
                    col = index % 3
                    grid_layout_temp.addWidget(button_temp, row, col)
                
                layout_temp.addLayout(grid_layout_temp)
                
                self.model_templates_layout.addLayout(layout_temp)
    
    
    def on_model_template_clicked(self, button):
        if button.text() == 'Custom model':
            self.load_model_widget.set_state(True)
            self.load_testbenches_widget.set_state(True)
        else:
            self.load_model_widget.set_state(False)
            self.load_testbenches_widget.set_state(False)