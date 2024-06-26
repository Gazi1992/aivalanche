from PySide6.QtWidgets import QCheckBox
from PySide6.QtGui import QPainter, QPixmap, QColor, QBrush, QMouseEvent
from PySide6.QtCore import Qt, QRect
from aivalanche_app.paths import checkbox_checked_path, checkbox_checked_hovered_path, checkbox_checked_pressed_path, checkbox_unchecked_path, checkbox_unchecked_hovered_path, checkbox_unchecked_pressed_path
from aivalanche_app.resources.themes.style import style

class custom_checkbox(QCheckBox):
    def __init__(self, parent = None,
                 checkbox_checked_path = checkbox_checked_path, checkbox_unchecked_path = checkbox_unchecked_path,
                 checkbox_width: int = 16, checkbox_height: int = 16, state: bool = False,
                 style: style = None, on_click: callable = None, object_name: str = None):
        
        super().__init__(parent)
        
        self.checkbox_checked_path = checkbox_checked_path
        self.checkbox_unchecked_path = checkbox_unchecked_path
        self.checkbox_width = checkbox_width
        self.checkbox_height = checkbox_height
        self.on_click = on_click

        self.setCheckable(True)
        
        self.checkbox_hovered = False
        self.checkbox_pressed = False
        self.checkbox_checked = state
        
        self.checkbox_rect = QRect(0, 0, 0, 0)
        
        if object_name is not None:
            self.setObjectName(object_name)
            

    def mouseMoveEvent(self, event: QMouseEvent):
        if not self.checkbox_pressed:
            if self.checkbox_rect.contains(event.pos()):
                if not self.checkbox_hovered:
                    self.checkbox_hovered = True
                    self.update()
            else:
                if self.checkbox_hovered:
                    self.checkbox_hovered = False
                    self.update()


    def leaveEvent(self, event):
        if not self.checkbox_pressed:
            if self.checkbox_hovered:
                self.checkbox_hovered = False
                self.update()


    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:            
            if self.checkbox_rect.contains(event.pos()):
               self.checkbox_pressed = True
               self.checkbox_hovered = False
               self.update()               


    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            if self.checkbox_rect.contains(event.pos()):
                self.checkbox_checked = not self.checkbox_checked
                self.checkbox_hovered = False
                self.checkbox_pressed = False
                self.update()
                if self.on_click is not None:
                    self.on_click(self.checkbox_checked)
                self.stateChanged.emit(self.checkbox_checked)
            elif self.checkbox_pressed:
                self.checkbox_hovered = False
                self.checkbox_pressed = False
                self.update()
                

    def paintEvent(self, event):
        rect = self.rect()
        painter = QPainter(self)
        self.paint(painter, rect)
        

    def paint(self, painter, rect):
        # Make the height of the rect a little larger, so that the image is not cut
        min_rect_height = self.checkbox_height + 2
        min_rect_width = self.checkbox_width + 2
        
        if rect.height() < min_rect_height:
            rect.setHeight(min_rect_width)
        if rect.width() < min_rect_width:
            rect.setWidth(min_rect_width)
            
        self.setMinimumWidth(min_rect_width)
        self.setMinimumHeight(min_rect_height)
        
        # Get rect position
        x = rect.x()
        y = rect.y()
        width = rect.width()
        height = rect.height()
                
        # Calculate checkbox position
        checkbox_x = x + (width - self.checkbox_height) / 2
        checkbox_y = y + (height - self.checkbox_height) / 2
        self.checkbox_rect = QRect(checkbox_x, checkbox_y, self.checkbox_width, self.checkbox_height)
        
        # Get painter
        painter.save()
        
        painter.fillRect(rect, QColor(Qt.transparent))
        
        # Draw the checkbox icon
        checkbox_icon = get_checkbox_icon(is_checked = self.checkbox_checked,
                                          is_hovered = self.checkbox_hovered,
                                          is_pressed = self.checkbox_pressed)
        painter.drawPixmap(self.checkbox_rect, checkbox_icon)

        painter.restore()
    
    
    def set_checked(self, state):       
        if isinstance(state, int):
            state = False if state == 0 else True
            
        if isinstance(state, bool):
            self.checkbox_checked = state
            self.update()

        
def get_checkbox_icon(is_checked = False, is_hovered = False, is_pressed = False):
    if is_pressed:
        if is_checked:
            checkbox_icon = QPixmap(checkbox_checked_pressed_path)
        else:
            checkbox_icon = QPixmap(checkbox_unchecked_pressed_path)
    elif is_hovered:
        if is_checked:
            checkbox_icon = QPixmap(checkbox_checked_hovered_path)
        else:
            checkbox_icon = QPixmap(checkbox_unchecked_hovered_path)        
    else:
        if is_checked:
            checkbox_icon = QPixmap(checkbox_checked_path)
        else:
            checkbox_icon = QPixmap(checkbox_unchecked_path)
            
    return checkbox_icon



