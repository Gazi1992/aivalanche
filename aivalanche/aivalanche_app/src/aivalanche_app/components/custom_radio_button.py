from PySide6.QtWidgets import QWidget, QRadioButton
from aivalanche_app.components.custom_layouts import h_layout

class custom_radio_button(QWidget):
    def __init__(self, parent = None, text = '', on_click = None, group = None):
        super().__init__(parent)
        layout = h_layout()
        self.setLayout(layout)

        button = QRadioButton(text = text)        
        
        layout.addWidget(button)
        layout.addStretch()
        
        if on_click is not None:
            button.clicked.connect(lambda state: on_click(state, text))
        
        if group is not None:
            group.addButton(button)
        
    
        