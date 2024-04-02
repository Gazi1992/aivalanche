from PySide6.QtWidgets import QWidget, QLabel
from PySide6.QtGui import QMovie
from aivalanche_app.components.custom_layouts import v_layout
from aivalanche_app.paths import loading_path


class loading_spinner(QWidget):
    def __init__(self, parent = None):
        super().__init__(parent = parent)
        
        layout = v_layout()
        self.setLayout(layout)
        
        spinner = QLabel(self)
        layout.addWidget(spinner)
        
        self.movie = QMovie(str(loading_path))
        spinner.setMovie(self.movie)

    
    def start(self):
        self.movie.start()
        
    
    def stop(self):
        self.movie.stop()

