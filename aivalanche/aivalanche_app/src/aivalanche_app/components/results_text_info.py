from PySide6.QtWidgets import QWidget, QLabel
from aivalanche_app.components.custom_layouts import h_layout

class results_text_info(QWidget):
    def __init__(self, parent = None, label = 'label', value = 'value'):
        super().__init__(parent = parent)
        
        layout = h_layout()
        self.setLayout(layout)
        
        label_widget = QLabel(text = label)
        layout.addWidget(label_widget)
        
        layout.addStretch()
        
        self.value_widget = QLabel()
        layout.addWidget(self.value_widget)

        self.update_value(value)
        
    def update_value(self, value):
        if value is None:
            value = ''
        if isinstance(value, int):
            value = f'{value}'
        if isinstance(value, float):
            value = f'{value:.4e}'
            
        if value == '':
            value = '----'
        
        self.value_widget.setText(str(value))

        
    
