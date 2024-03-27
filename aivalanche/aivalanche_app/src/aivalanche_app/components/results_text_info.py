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
        if isinstance(value, str):
            self.value_widget.setText(value)
        elif isinstance(value, (int, float)):
            self.value_widget.setText(f'{value:.4e}')
        else:
            self.value_widget.setText(str(value))

        
    
