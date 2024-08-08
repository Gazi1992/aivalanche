import pyqtgraph as pg
from PySide6.QtCore import Qt

class custom_graphics_layout_widget(pg.GraphicsLayoutWidget):
    def wheelEvent(self, ev):
        if ev.modifiers() == Qt.ControlModifier:
            super().wheelEvent(ev)
        else:
            ev.ignore()
