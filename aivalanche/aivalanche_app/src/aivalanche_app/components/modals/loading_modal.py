from PySide6.QtWidgets import QDialog
from PySide6.QtCore import Qt
from aivalanche_app.components.custom_layouts import v_layout
from aivalanche_app.components.loading_spinner import loading_spinner

class loading_modal(QDialog):
    def __init__(self, parent = None):
        super().__init__(parent = parent)
        
        self.setWindowFlags(Qt.Dialog | Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setModal(True)
        # self.setStyleSheet("background-color: rgba(0, 0, 0, 128);") 
        
        # Create layout for the dialog
        layout = v_layout(spacing = 10)
        self.setLayout(layout)
        
        self.spinner = loading_spinner()
        layout.addWidget(self.spinner)


    def start(self):
        self.spinner.start()
        

    def stop(self):
        self.spinner.stop()
        

