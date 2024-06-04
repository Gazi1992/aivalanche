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
        
        self.testbench_buttons_group = QButtonGroup(self)
        self.testbench_buttons_group.setExclusive(False)
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
        self.left_layout = v_layout(spacing = 20, alignment = Qt.AlignmentFlag.AlignTop)
        left_widget.setLayout(self.left_layout)
        left_scroll_area.setWidget(left_widget)
        
        # Model label
        model_label = custom_label(parent = self, text = 'Model', font_size = 'huge', opacity = 0.5)
        self.left_layout.addWidget(model_label)

        # Custom model button
        custom_model_button = custom_radio_button(parent = self, text = 'Custom model', group = self.model_buttons_group)
        self.left_layout.addWidget(custom_model_button)
        
        # Create load model combo box
        self.load_model_widget = combo_box_load_data(parent = self,
                                                     caption = 'Select model file',
                                                     filter = 'cir file (*.cir)',
                                                     placeholder = 'Select model file',
                                                     is_enabled = False,
                                                     object_name = 'round_combo_box')
        self.left_layout.addWidget(self.load_model_widget)
        
        self.model_templates_layout = v_layout(spacing = 20, alignment = Qt.AlignmentFlag.AlignTop)
        self.left_layout.addLayout(self.model_templates_layout)
        
        # # Add the model templates
        # for item in self.store.model_templates.keys():
        #     layout_temp = v_layout(spacing = 15) 
        #     label = custom_label(parent = self, text = item, font_size = 'normal')
        #     layout_temp.addWidget(label)

        #     grid_layout_temp = g_layout( vertical_spacing = 10)
        #     for index, val in enumerate(self.store.model_templates[item]):
        #         button_temp = custom_radio_button(parent = self, text = val, group = self.model_buttons_group)
        #         row = index // 3
        #         col = index % 3
        #         grid_layout_temp.addWidget(button_temp, row, col)
            
        #     layout_temp.addLayout(grid_layout_temp)
            
        #     self.left_layout.addLayout(layout_temp)
        
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
        self.load_testbenches_widget = combo_box_load_data(parent = self,
                                                           caption = 'Select testbenches file',
                                                           filter = 'json file (*.json)',
                                                           placeholder = 'Select testbenches file',
                                                           is_enabled = False,
                                                           object_name = 'round_combo_box')
        right_layout.addWidget(self.load_testbenches_widget)
        
        # Add the testbench templates
        grid_layout_temp = g_layout( vertical_spacing = 10)
        for index, val in enumerate(self.store.testbench_templates):
            button_temp = custom_checkbox_with_text(parent = self, text = val, on_click = self.on_testbench_checkbox_clicked)
            row = index // 5
            col = index % 5
            grid_layout_temp.addWidget(button_temp, row, col)
            self.testbench_checkboxes.append(button_temp)
            
        right_layout.addLayout(grid_layout_temp)
    
    
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
        else:
            self.load_model_widget.set_state(False)


    def on_testbench_template_clicked(self, button):
        if button.text() == 'Custom testbenches':
            self.load_testbenches_widget.set_state(button.isChecked())
        else:
            self.load_testbenches_widget.set_state(False)
            
    def on_testbench_checkbox_clicked(self, state, text):
        print(text, ': ', state)