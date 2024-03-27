from PySide6.QtWidgets import QWidget, QLabel
from aivalanche_app.components.custom_layouts import g_layout
from aivalanche_app.components.text_input_with_label import text_input_with_label
from aivalanche_app.components.combo_box_load_data_with_label import combo_box_load_data_with_label

class optimization_parameters(QWidget):
    def __init__(self, parent = None, parameters: list[dict] = []):
        super().__init__(parent = parent)

        self.parameters = parameters
        self.init_ui()

    def init_ui(self):        
        layout = g_layout(parent = self, horizontal_spacing = 10, vertical_spacing = 10)
        self.setLayout(layout)
        
        if self.parameters is not None:
            for index, item in enumerate(self.parameters):
                row = index // 2
                column = index % 2
                
                if item['type'] in ['int', 'float', 'str']:
                    parameter_widget = text_input_with_label(parent = self,
                                                             label = item['name'],
                                                             label_position = 'top',
                                                             placeholder = item['default'],
                                                             on_change = lambda x: print(x))
                elif item['type'] == 'file':
                    parameter_widget = combo_box_load_data_with_label(parent = self,
                                                                      label = item['name'],
                                                                      label_position = 'top',
                                                                      placeholder = item['default'],
                                                                      caption = 'Select initial population file',
                                                                      filter = 'csv file (*.csv)',
                                                                      on_change = lambda x: print(x))                
                else:
                    parameter_widget = QLabel(parent = self, text = item['name'])
                    
                layout.addWidget(parameter_widget, row, column)
