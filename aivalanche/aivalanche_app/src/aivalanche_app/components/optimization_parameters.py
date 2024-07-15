from PySide6.QtWidgets import QWidget, QLabel
from aivalanche_app.components.custom_layouts import g_layout, clear_layout
from aivalanche_app.components.text_input_with_label import text_input_with_label
from aivalanche_app.components.combo_box_load_data_with_label import combo_box_load_data_with_label
import pandas as pd
from functools import partial

class optimization_parameters(QWidget):
    def __init__(self, parent = None, parameters: pd.DataFrame = pd.DataFrame(), on_change: callable = None):
        super().__init__(parent = parent)

        self.parameters = parameters
        self.on_change = on_change if on_change is not None else lambda x, y: print(f'{x}: {y}')
        self.init_ui()

    def init_ui(self):        
        self.layout = g_layout(parent = self, horizontal_spacing = 10, vertical_spacing = 10)
        self.setLayout(self.layout)
        self.update_parameters(self.parameters)
    
    def update_parameters(self, parameters: pd.DataFrame = pd.DataFrame()):
        clear_layout(self.layout)
        self.parameters = parameters.copy()        
        if self.parameters is not None and len(self.parameters.index > 0):
            if 'value' not in self.parameters.columns:
                self.parameters['value'] = self.parameters['default']
            for index, item in self.parameters.iterrows():
                row = index // 2
                column = index % 2
                
                if item['type'] in ['int', 'float', 'str']:
                    parameter_widget = text_input_with_label(parent = self,
                                                             label = item['name'].replace('_', ' '),
                                                             initial_value = item['value'],
                                                             label_position = 'top',
                                                             placeholder = item['default'],
                                                             on_change = partial(self.on_change, item['name']),
                                                             tooltip = item['explanation'] if not pd.isnull(item['explanation'] ) else None)
                elif item['type'] == 'file':
                    filter = f"({','.join([f'*{format}' for format in item['file_type']])})"
                    parameter_widget = combo_box_load_data_with_label(parent = self,
                                                                      label = item['name'].replace('_', ' '),
                                                                      # initial_value = item['value'],
                                                                      label_position = 'top',
                                                                      placeholder = item['default'],
                                                                      caption = item['default'],
                                                                      filter = filter,
                                                                      on_change = lambda x: self.on_change(item['name'], x),
                                                                      tooltip = item['explanation'] if not pd.isnull(item['explanation'] ) else None)               
                else:
                    parameter_widget = QLabel(parent = self, text = item['name'])
                    
                self.layout.addWidget(parameter_widget, row, column)
        
        
        