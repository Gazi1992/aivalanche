from PySide6.QtWidgets import QWidget, QLabel
from aivalanche_app.components.custom_layouts import v_layout
from aivalanche_app.data_store.store import store


class parameters_tab(QWidget):
    
    def __init__(self, parent = None, store: store = None, object_name: str = None):
        super().__init__(parent)

        if object_name is not None:
            self.setObjectName(object_name)
        
        self.store = store
        
        layout = v_layout()
        layout.addWidget(QLabel('Parameters', self))
        
        self.setLayout(layout)

        