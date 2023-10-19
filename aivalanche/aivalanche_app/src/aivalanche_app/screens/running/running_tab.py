from PySide6.QtWidgets import QWidget, QLabel
from aivalanche_app.components.custom_layouts import v_layout
from aivalanche_app.data_store.store import store
from aivalanche_app.resources.themes.style import style

class running_tab(QWidget):
    def __init__(self, parent = None, store: store = None, style: style = None):
        super().__init__(parent)
        
        self.store = store
        self.style = style
        
        layout = v_layout()
        text = QLabel("This is running tab.")
        layout.addWidget(text)
        
        self.setLayout(layout)

