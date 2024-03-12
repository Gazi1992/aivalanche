from PySide6.QtWidgets import QWidget, QCheckBox, QGraphicsOpacityEffect
from aivalanche_app.components.custom_layouts import h_layout

class custom_checkbox_with_text(QWidget):
    def __init__(self, parent = None, text = '', state = False, on_click = None, is_enabled = True, object_name = None):
        super().__init__(parent)
        layout = h_layout()
        self.setLayout(layout)

        checkbox = QCheckBox(text = text)
        checkbox.setChecked(state)
        if object_name is not None:
            checkbox.setObjectName(object_name)
        
        layout.addWidget(checkbox)
        layout.addStretch()
        
        if on_click is not None:
            checkbox.stateChanged.connect(lambda state: on_click(state == 2, text))
            
        self.is_enabled = is_enabled
    
    
    def set_enabled(self, state: bool = True):
        if state != self.is_enabled:
            self.is_enabled = state
            self.setEnabled(self.is_enabled)
            self.adjust_opacity()
        
    
    def adjust_opacity(self):
        opacity_effect = QGraphicsOpacityEffect(self)
        if self.is_enabled:
            opacity_effect.setOpacity(1)
        else:
            opacity_effect.setOpacity(0.3)
        self.setGraphicsEffect(opacity_effect)

    
        