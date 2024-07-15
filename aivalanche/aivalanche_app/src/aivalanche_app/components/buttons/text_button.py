from PySide6.QtWidgets import QPushButton

class text_button(QPushButton):
    def __init__(self, parent = None, label: str = '', switch_label: str = None, on_click: callable = None, object_name: str = None):
        super().__init__(parent)
        
        self.label = label
        self.switch_label = switch_label
        self.on_click = on_click
        
        self.setText(label)
        
        if object_name is not None:
            self.setObjectName(object_name)

        self.clicked.connect(self.on_button_click)

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
        
                        
        
   