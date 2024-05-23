from PySide6.QtWidgets import QComboBox, QGraphicsOpacityEffect, QSizePolicy
from PySide6.QtGui import QPainter, QPixmap
from PySide6.QtCore import QRect
from aivalanche_app.paths import delete_1_icon_path, delete_1_hover_icon_path, delete_1_press_icon_path

class custom_combo_box(QComboBox):
    def __init__(self, parent = None, items: list = [], active_item: str = None, placeholder: str = 'Select',
                 on_change: callable = None, is_enabled: bool = True, is_editable: bool = True, object_name: str = None,
                 has_delete_button: bool = False, on_delete_button_clicked: callable = None,
                 horizontal_size_policy = QSizePolicy.Policy.Expanding, vertical_size_policy = QSizePolicy.Policy.Fixed):
                
        super().__init__(parent)
        
        self.setSizePolicy(horizontal_size_policy, vertical_size_policy)
        
        if object_name is not None:
            self.setObjectName(object_name)
                
        self.items = items
        self.active_item = active_item if active_item in items else items[0] if len(items) > 0 else None
        self.is_enabled = None
        self.on_change = on_change
        self.has_delete_button = has_delete_button
        self.opacity_effect = QGraphicsOpacityEffect(self)
        
        if is_editable:
            self.setEditable(True)
            self.lineEdit().setPlaceholderText(placeholder)
        else:
            self.setPlaceholderText(placeholder)
        
        self.connect_on_change_slot()
            
        if len(self.items) > 0:
            self.addItems(items)
            
        if self.active_item is not None:
            self.setCurrentText(self.active_item)

        self.set_state(is_enabled)
        
        if self.has_delete_button:
            self.delete_button_width = 15
            self.delete_button_height = 15
            self.delete_button_margin = 1
            self.delete_button_rect = QRect(0, 0, 0, 0)
            self.hovered = False
            self.mouse_pressed = False
            self.delete_button_icon_path = delete_1_icon_path
            self.on_delete_button_clicked = on_delete_button_clicked
            self.setMouseTracking(True)
            # self.setContentsMargins(0, 50, 0, 0)
    
    def update_items(self, items: list = [], active_item: str = None, trigger_on_change_slot: bool = False):
        self.clear()
        self.items = items
        current_index = self.currentIndex()
        if not trigger_on_change_slot:
            self.disconnect_on_change_slot()
            self.addItems(self.items)
            self.connect_on_change_slot()
        else:
            self.addItems(self.items)
                
        # Keep the current index in case it was -1
        if current_index == -1 and active_item is None:
            self.setCurrentIndex(-1)
        elif active_item is not None and active_item in items:
            self.active_item = active_item
            self.setCurrentText(self.active_item)
            
    def disconnect_on_change_slot(self):
        self.currentTextChanged.disconnect()
        
    def connect_on_change_slot(self):
        self.currentTextChanged.connect(lambda text: self.on_item_change(text))

    def toggle_state(self):
        self.is_enabled = not self.is_enabled
        self.setEnabled(self.is_enabled)
        self.adjust_opacity()
        
    def set_state(self, state: bool = True):
        if state != self.is_enabled:
            self.is_enabled = state
            self.setEnabled(self.is_enabled)
            self.adjust_opacity()
    
    def adjust_opacity(self):
        if self.is_enabled:
            self.opacity_effect.setOpacity(1)
        else:
            self.opacity_effect.setOpacity(0.3)
        self.setGraphicsEffect(self.opacity_effect)
        
    def on_item_change(self, text):
        self.active_item = text
        if self.on_change is not None:
            self.on_change(text)
            
    def paintEvent(self, event):
        super().paintEvent(event)
        if self.has_delete_button and self.hovered:
            painter = QPainter(self)            
            painter.save()
            painter.drawPixmap(self.delete_button_rect, QPixmap(self.delete_button_icon_path))
            painter.restore()
    
    def resizeEvent(self, event):
        if self.has_delete_button:
            # Calculate the button rect position
            rect = self.rect()
            x = rect.x() + rect.width() - self.delete_button_margin - self.delete_button_width
            y = rect.y() + self.delete_button_margin
            self.delete_button_rect = QRect(x, y, self.delete_button_width, self.delete_button_height)
        super().resizeEvent(event)
    
    def mouseMoveEvent(self, event):
        if self.has_delete_button:
            if self.rect().contains(event.pos()):
                if not self.hovered:
                    self.hovered = True
                if not self.mouse_pressed:
                    if self.delete_button_rect.contains(event.pos()):
                        if self.delete_button_icon_path != delete_1_hover_icon_path:
                            self.delete_button_icon_path = delete_1_hover_icon_path
                    else:
                        if self.delete_button_icon_path != delete_1_icon_path:
                            self.delete_button_icon_path = delete_1_icon_path
            else:
                if self.hovered:
                    self.hovered = False
            self.update()
        super().mouseMoveEvent(event)
     
    def mousePressEvent(self, event):
        if self.has_delete_button:
            self.mouse_pressed = True
            if self.delete_button_rect.contains(event.pos()):
                if self.delete_button_icon_path != delete_1_press_icon_path:
                    self.delete_button_icon_path = delete_1_press_icon_path
            else:
                if self.delete_button_icon_path != delete_1_icon_path:
                    self.delete_button_icon_path = delete_1_icon_path
                super().mousePressEvent(event)
            self.update()
        else:
            super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        if self.has_delete_button:
            self.mouse_pressed = False
            if self.delete_button_icon_path != delete_1_icon_path:
                self.delete_button_icon_path = delete_1_icon_path
            if self.delete_button_rect.contains(event.pos()):
                self.mouse_pressed = False
                self.hovered = self.rect().contains(event.pos())
                if self.on_delete_button_clicked is not None:
                    self.on_delete_button_clicked()
            else:
                super().mouseReleaseEvent(event)
            self.update()
        else:
            super().mouseReleaseEvent(event)

    def leaveEvent(self, event):
        if self.has_delete_button:
            if not self.mouse_pressed:
                if self.hovered:
                    self.hovered = False
                if self.delete_button_icon_path != delete_1_icon_path:
                    self.delete_button_icon_path = delete_1_icon_path
        super().leaveEvent(event)
        self.update()


