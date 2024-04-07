from PySide6.QtWidgets import QDialog, QLabel
from PySide6.QtCore import Qt
from aivalanche_app.components.custom_layouts import v_layout
from aivalanche_app.components.loading_spinner import loading_spinner

class loading_modal(QDialog):
    def __init__(self, parent = None, text = ''):
        super().__init__(parent = parent)
        
        self.setWindowFlags(Qt.Dialog | Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setModal(True)
        self.text = text
        # self.setStyleSheet("background-color: rgba(0, 0, 0, 128);") 
                
        # Create layout for the dialog
        layout = v_layout(spacing = 10)
        self.setLayout(layout)
        
        self.spinner = loading_spinner()
        layout.addWidget(self.spinner)
        
        self.text_widget = QLabel(self.text, parent = self)
        layout.addWidget(self.text_widget)
        
        self.enable_text_widget()

    def start(self):
        self.spinner.start()
        

    def stop(self):
        self.spinner.stop()
        
    def update_text(self, text):
        self.text = text
        self.text_widget.setText(self.text)
        self.enable_text_widget()
        
    def enable_text_widget(self):
        if len(self.text) > 0:
            self.text_widget.show()
        else:
            self.text_widget.hide()

