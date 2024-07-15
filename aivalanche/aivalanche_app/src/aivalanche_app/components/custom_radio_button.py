from PySide6.QtWidgets import QWidget, QRadioButton
from aivalanche_app.components.custom_layouts import h_layout

class custom_radio_button(QWidget):
    def __init__(self, parent = None, text = '', on_click = None, group = None, object_name = None):
        super().__init__(parent)
        layout = h_layout()
        self.setLayout(layout)

        self.button = QRadioButton(text = text)
        if object_name is not None:
            self.button.setObjectName(object_name)
        
        layout.addWidget(self.button)
        layout.addStretch()
        
        if on_click is not None:
            self.button.clicked.connect(lambda state: on_click(state, text))
        
        if group is not None:
            group.addButton(self.button)
            
    def click(self):
        self.button.click()
        
    def set_state(self, state):
        self.button.setChecked(state)

    
        