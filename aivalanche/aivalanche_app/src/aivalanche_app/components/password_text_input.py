from PySide6.QtWidgets import QLineEdit
from PySide6.QtCore import QRect, Qt
from PySide6.QtGui import QPainter, QPixmap, QCursor
from aivalanche_app.paths import eye_show_icon_path, eye_hide_icon_path

class password_text_input(QLineEdit):
    def __init__(self, parent = None, object_name: str = None):
        super().__init__(parent = parent)
        if object_name is not None:
            self.setObjectName(object_name)
            
        self.setPlaceholderText('Password')
        
        self.show_hide_button_width = 30.965
        self.show_hide_button_height = 20
        self.show_hide_button_margin = 5
        self.show_hide_button_icon_path = eye_hide_icon_path
        self.show_hide_button_rect = QRect(0, 0, 0, 0)
        
        self.mouse_pressed = False
        self.setMouseTracking(True)
        
        self.password_visible = True
        self.toggle_password_visibility()

        
    def toggle_password_visibility(self):
        self.password_visible = not self.password_visible
        if self.password_visible:
            self.show_hide_button_icon_path = eye_show_icon_path
            self.setEchoMode(QLineEdit.EchoMode.Normal)
        else:
            self.show_hide_button_icon_path = eye_hide_icon_path
            self.setEchoMode(QLineEdit.EchoMode.Password)
        self.update()
        
    
    def resizeEvent(self, event):
        # Calculate the button rect position
        rect = self.rect()
        x = rect.x() + rect.width() - self.show_hide_button_width - self.show_hide_button_margin
        y = rect.y() + (rect.height() - self.show_hide_button_height) / 2
        self.show_hide_button_rect = QRect(x, y, self.show_hide_button_width, self.show_hide_button_height)
        super().resizeEvent(event)
        
    
    def paintEvent(self, event):
        super().paintEvent(event)
        painter = QPainter(self)            
        painter.save()
        painter.drawPixmap(self.show_hide_button_rect, QPixmap(self.show_hide_button_icon_path))
        painter.restore()
            
    
    def mousePressEvent(self, event):
        if self.show_hide_button_rect.contains(event.pos()):
            self.toggle_password_visibility()
        super().mousePressEvent(event)
        self.update()
        
    def mouseMoveEvent(self, event):
        if self.show_hide_button_rect.contains(event.pos()):
            self.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        else:
            self.setCursor(QCursor(Qt.CursorShape.IBeamCursor))
        super().mouseMoveEvent(event)
        self.update()

