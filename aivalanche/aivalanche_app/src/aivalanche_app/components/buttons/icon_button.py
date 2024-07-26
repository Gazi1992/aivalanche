from PySide6.QtWidgets import QPushButton
from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap

class icon_button(QPushButton):
    def __init__(self, parent = None, icon_path: str = None, icon_hover_path: str = None, icon_press_path: str = None,
                 on_click: callable = None, object_name: str = None, enabled: bool = True):
        super().__init__(parent)

        self.icon = QPixmap(icon_path)        
        self.icon_hover = QPixmap(icon_hover_path) if icon_hover_path else QPixmap(icon_path)
        self.icon_press = QPixmap(icon_press_path) if icon_press_path else QPixmap(icon_path)        
        
        if object_name is not None:
            self.setObjectName(object_name)

        if on_click is not None:
            self.clicked.connect(on_click)
        
        self.setMouseTracking(True)

        self.set_icon(self.icon)     
        self.set_enabled(enabled)
        
    def enterEvent(self, event):
        if self.isEnabled():
            self.set_icon(self.icon_hover)
        super().enterEvent(event)


    def leaveEvent(self, event):
        if self.isEnabled():
            self.set_icon(self.icon)
        super().leaveEvent(event)


    def mousePressEvent(self, event):
        if self.isEnabled():
            if event.button() == Qt.LeftButton:
                self.set_icon(self.icon_press)
        super().mousePressEvent(event)


    def mouseReleaseEvent(self, event):
        if self.isEnabled():
            if event.button() == Qt.LeftButton:
                self.set_icon(self.icon)
        super().mouseReleaseEvent(event)


    def set_icon(self, pixmap = None):
        self.setIcon(pixmap)
        
    def set_enabled(self, state = True):
        self.setEnabled(state)