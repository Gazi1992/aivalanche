from PySide6.QtWidgets import QWidget, QCheckBox, QGraphicsOpacityEffect
from aivalanche_app.components.custom_layouts import h_layout

class custom_checkbox_with_text(QWidget):
    def __init__(self, parent = None, text = '', state = False, on_click = None, is_enabled = True, object_name = None):
        super().__init__(parent)
        
        self.text = text
        self.on_click = on_click
        
        layout = h_layout()
        self.setLayout(layout)

        self.checkbox = QCheckBox(text = text)
        self.checkbox.setChecked(state)
        if object_name is not None:
            self.checkbox.setObjectName(object_name)
        
        layout.addWidget(self.checkbox)
        layout.addStretch()
        
        if self.on_click is not None:
            self.checkbox.stateChanged.connect(lambda state: self.on_click(state == 2, self.text))
            
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
    
    def set_state(self, state, emit_on_click: bool = True):
        if not emit_on_click:
            self.checkbox.blockSignals(True)
        self.checkbox.setChecked(state)
        if not emit_on_click:
            self.checkbox.blockSignals(False)
        
        
    
        