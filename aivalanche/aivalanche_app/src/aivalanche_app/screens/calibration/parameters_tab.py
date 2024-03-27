from PySide6.QtWidgets import QWidget
from aivalanche_app.components.custom_layouts import v_layout, h_layout
from aivalanche_app.data_store.store import store
from aivalanche_app.components.combo_box_load_data import combo_box_load_data
from aivalanche_app.components.custom_table import custom_table
from aivalanche_app.components.buttons.icon_text_button import icon_text_button
from parameters import Parameters
import os


class parameters_tab(QWidget):
    
    def __init__(self, parent = None, store: store = None, object_name: str = None):
        super().__init__(parent)

        if object_name is not None:
            self.setObjectName(object_name)
        
        self.store = store
        
        self.init_ui()
        
    def init_ui(self):
        
        # main layout
        layout = v_layout(spacing = 30)
        self.setLayout(layout)

        # top layout
        top_layout = h_layout(spacing = 20)
        layout.addLayout(top_layout)
        
        # Create load data combo box
        self.load_data_widget = combo_box_load_data(parent = self,
                                                    caption = 'Select parameters file',
                                                    filter = 'CSV and Json files (*.csv *.json)',
                                                    placeholder = 'Select parameters file',
                                                    on_combo_box_changed = self.load_parameters,
                                                    object_name = 'round_combo_box')       
        top_layout.addWidget(self.load_data_widget, 0)
        top_layout.addSpacing(20)
        
        # Save parameter to file button
        save_button = icon_text_button(parent = self, text = 'Save parameters to file', padding = (10, 5, 10, 5),
                                       on_click = self.save_parameters_to_file, object_name = 'parameters_tab')
        top_layout.addWidget(save_button)
        
        # Save parameter to file button
        import_default_button = icon_text_button(parent = self, text = 'Import default values', padding = (10, 5, 10, 5),
                                                 on_click = self.import_default_values, object_name = 'parameters_tab')
        top_layout.addWidget(import_default_button)
        
        # Create table
        self.table = custom_table(store = self.store, column_width_mode = 'Stretch')
        layout.addWidget(self.table, 1)
        

    def load_parameters(self, file):
        if os.path.exists(file):
            self.parameters = Parameters(file)
            self.parameters.all_parameters.insert(0, 'include', True)
            self.table.update_data(self.parameters.all_parameters)


    def save_parameters_to_file(self):
        print('save parameters to file')
        
    def import_default_values(self):
        print('import default values')