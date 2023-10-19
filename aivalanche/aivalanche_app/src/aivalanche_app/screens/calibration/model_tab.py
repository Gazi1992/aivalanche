from PySide6.QtWidgets import QWidget, QLabel
from aivalanche_app.components.custom_layouts import v_layout
from aivalanche_app.data_store.store import store


class model_tab(QWidget):
    
    def __init__(self, parent = None, store: store = None):
        super().__init__(parent)
        
        self.store = store
        
        layout = v_layout()
        layout.addWidget(QLabel('Model', self))
        
        self.setLayout(layout)

        