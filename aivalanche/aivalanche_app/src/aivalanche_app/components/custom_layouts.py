from PySide6.QtWidgets import QVBoxLayout, QHBoxLayout, QGridLayout
from PySide6.QtCore import Qt

class v_layout(QVBoxLayout):
    def __init__(self, parent = None, padding = (0, 0, 0, 0), spacing = 0, alignment = Qt.AlignmentFlag.AlignCenter):
        super().__init__(parent)
        self.setSpacing(spacing)
        self.setContentsMargins(*padding)
        self.setAlignment(alignment)

class h_layout(QHBoxLayout):
    def __init__(self, parent = None, padding = (0, 0, 0, 0), spacing = 0, alignment = Qt.AlignmentFlag.AlignCenter):
        super().__init__(parent)
        self.setSpacing(spacing)
        self.setContentsMargins(*padding)
        self.setAlignment(alignment)

class g_layout(QGridLayout):
    def __init__(self, parent = None, padding = (0, 0, 0, 0), horizontal_spacing = 0, vertical_spacing = 0, alignment = Qt.AlignmentFlag.AlignCenter):
        super().__init__(parent)
        self.setHorizontalSpacing(horizontal_spacing)
        self.setVerticalSpacing(vertical_spacing)
        self.setContentsMargins(*padding)
        self.setAlignment(alignment)
        
def clear_layout(layout):
    while layout.count():
        item = layout.takeAt(0)
        widget = item.widget()
        if widget:
            widget.deleteLater()    
