from PySide6.QtWidgets import QPushButton, QGraphicsOpacityEffect

class text_button(QPushButton):
    def __init__(self, parent = None, label: str = '', switch_label: str = None, on_click: callable = None,
                 object_name: str = None, is_visible: bool = True, is_enabled: bool = True):
        super().__init__(parent)
        
        self.label = label
        self.switch_label = switch_label
        self.on_click = on_click
        self.is_enabled = None
        self.is_visible = None
        
        self.setText(label)
        
        if object_name is not None:
            self.setObjectName(object_name)

        self.clicked.connect(self.on_button_click)
        
        self.opacity_effect = QGraphicsOpacityEffect()
        
        self.set_visible(is_visible)
        self.set_enabled(is_enabled)

    def on_button_click(self):
        if self.on_click is not None:
            self.on_click(self.text())
        if self.switch_label is not None:
            self.switch_text()    
            
    def switch_text(self):
        if self.text() == self.label:
            self.setText(self.switch_label)
        else:
            self.setText(self.label)   
            
    def set_visible(self, visible: bool = True):
        if self.is_visible is None or visible != self.is_visible:
            self.is_visible = visible
            self.setVisible(self.is_visible)
        
    def set_enabled(self, is_enabled: bool = True):
        if self.is_enabled is None or self.is_enabled != is_enabled:
            self.is_enabled = is_enabled
            self.setEnabled(self.is_enabled)
            self.adjust_opacity()
    
    def adjust_opacity(self):
        if self.is_enabled:
            self.opacity_effect.setOpacity(1)
        else:
            self.opacity_effect.setOpacity(0.3)
        self.setGraphicsEffect(self.opacity_effect)
        
                        
        
   