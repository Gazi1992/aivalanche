from PySide6.QtWidgets import QWidget, QLabel
from aivalanche_app.components.custom_layouts import v_layout
from aivalanche_app.data_store.store import store


class running_tab(QWidget):
    def __init__(self, parent = None, store: store = None, object_name: str = None):
        super().__init__(parent)
        
        self.store = store
        if object_name is not None:
            self.setObjectName(object_name)
        
        layout = v_layout()
        self.setLayout(layout)

        text = QLabel("This is running tab.")
        layout.addWidget(text)
        


