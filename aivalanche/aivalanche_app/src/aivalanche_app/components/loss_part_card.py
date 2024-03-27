from PySide6.QtWidgets import QWidget, QScrollArea, QFrame, QSizePolicy
from PySide6.QtCore import Qt, QRect
from PySide6.QtGui import QPainter, QPixmap
from aivalanche_app.components.custom_layouts import h_layout, v_layout
from aivalanche_app.components.custom_combo_box_with_label import custom_combo_box_with_label
from aivalanche_app.components.text_input_with_label import text_input_with_label
from aivalanche_app.components.custom_label import custom_label
from aivalanche_app.components.custom_combo_box import custom_combo_box
from aivalanche_app.components.buttons.custom_icon_button import custom_icon_button
from aivalanche_app.paths import plus_icon_path, plus_hover_icon_path, plus_press_icon_path, delete_1_icon_path, delete_1_hover_icon_path, delete_1_press_icon_path
import uuid, functools

class loss_part_card(QFrame):
    def __init__(self, parent = None, id: str = None, weight: float = 1, norm: bool = True, transforms_available: list[str] = [], groups: list[str] = [], object_name: str = None, on_delete_button_clicked: callable = None):
        super().__init__(parent = parent)
        
        if len(transforms_available) == 0:
            transforms_available = ['none', 'log']
        
        self.id = id
        self.weight = weight
        self.norm = norm
        self.transforms_available = transforms_available
        self.groups = groups
        self.object_name = object_name
        self.on_delete_button_clicked = on_delete_button_clicked
        self.group_types = {}
        
        if self.object_name is not None:
            self.setObjectName(self.object_name)
        
        self.delete_button_width = 20
        self.delete_button_height = 20
        self.delete_button_margin = 3
        self.delete_button_icon_path = delete_1_icon_path
        self.delete_button_rect = QRect(0, 0, 0, 0)
        self.hovered = False
        self.mouse_pressed = False
        
        self.setMouseTracking(True)
        
        self.init_ui()
        
    
    def init_ui(self):
        layout = v_layout(spacing = 5)
        self.setLayout(layout)
        
        top_layout = h_layout(spacing = 10)
        layout.addLayout(top_layout)
        
        # id
        id_widget = text_input_with_label(parent = self, label = 'id', label_position = 'top', placeholder = 'enter an id')
        top_layout.addWidget(id_widget, 1)
        
        # weight
        weight_widget = text_input_with_label(parent = self, label = 'weight', label_position = 'top', placeholder = '1')
        top_layout.addWidget(weight_widget, 1)
        
        # norm
        norm_widget = custom_combo_box_with_label(parent = self, label = 'norm', label_position = 'top', items = ['True', 'False'])
        top_layout.addWidget(norm_widget, 1)
        
        # transform
        transform_widget = custom_combo_box_with_label(parent = self, label = 'transform', label_position = 'top', items = self.transforms_available)
        top_layout.addWidget(transform_widget, 1)
        
        # group types
        group_types_label = custom_label(text = 'Group types')
        layout.addWidget(group_types_label)
        
        # scroll area for group types
        self.scroll_area = QScrollArea(parent = self)
        self.scroll_area.setContentsMargins(0, 0, 0, 0)
        self.scroll_area.setWidgetResizable(True)
        layout.addWidget(self.scroll_area)
        
        # Create right widget
        self.scroll_widget = QWidget(self)
        self.scroll_area.resizeEvent = self.on_scroll_widget_resize
        self.scroll_layout = h_layout(spacing = 5, alignment = Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
        self.scroll_widget.setLayout(self.scroll_layout)
        self.scroll_area.setWidget(self.scroll_widget)
        
        # add button
        add_group_button = custom_icon_button(parent = self,
                                              icon_path = plus_icon_path,
                                              icon_hover_path = plus_hover_icon_path,
                                              icon_press_path = plus_press_icon_path,
                                              object_name = 'add_group_type',
                                              on_click = self.add_group_type_button_click)       
        self.scroll_layout.addWidget(add_group_button)
        
        # Add the first group type combo box
        self.add_group_type_button_click()
        self.scroll_area.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Minimum)
        

    def add_group_type_button_click(self):
        id = uuid.uuid4()
        group_type_widget = custom_combo_box(parent = self,
                                             placeholder = 'Select group type',
                                             items = self.groups,
                                             has_delete_button = True,
                                             on_delete_button_clicked = functools.partial(self.on_delete_group_type, id),
                                             horizontal_size_policy = QSizePolicy.Policy.Fixed)
        self.group_types[id] = group_type_widget
        self.scroll_layout.insertWidget(self.scroll_layout.count() - 1, group_type_widget)
        
    def on_delete_group_type(self, id):
        self.scroll_layout.removeWidget(self.group_types[id])
        self.group_types[id].deleteLater()
        del self.group_types[id]
        
        
    def on_scroll_widget_resize(self, event):
        self.on_scroll_bar_visibility_changed()
        super().resizeEvent(event)
        
        
    def on_scroll_bar_visibility_changed(self):
        required_height = self.scroll_area.sizeHint().height()
        if self.scroll_area.horizontalScrollBar().isVisible():
            required_height += self.scroll_area.horizontalScrollBar().height()
        if self.scroll_area.height() != required_height:
            self.scroll_area.setFixedHeight(required_height)
            
    def paintEvent(self, event):
        super().paintEvent(event)
        if self.hovered:
            painter = QPainter(self)            
            painter.save()
            painter.drawPixmap(self.delete_button_rect, QPixmap(self.delete_button_icon_path))
            painter.restore()
    
    def resizeEvent(self, event):
        # Calculate the button rect position
        rect = self.rect()
        x = rect.x() + rect.width() - self.delete_button_margin - self.delete_button_width
        y = rect.y() + self.delete_button_margin
        self.delete_button_rect = QRect(x, y, self.delete_button_width, self.delete_button_height)
        super().resizeEvent(event)

    
    def mouseMoveEvent(self, event):
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
        self.mouse_pressed = True
        if self.delete_button_rect.contains(event.pos()):
            if self.delete_button_icon_path != delete_1_press_icon_path:
                self.delete_button_icon_path = delete_1_press_icon_path
        else:
            if self.delete_button_icon_path != delete_1_icon_path:
                self.delete_button_icon_path = delete_1_icon_path
            super().mousePressEvent(event)
        self.update()


    def mouseReleaseEvent(self, event):
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

            
    def leaveEvent(self, event):
        if not self.mouse_pressed:
            if self.hovered:
                self.hovered = False
            if self.delete_button_icon_path != delete_1_icon_path:
                self.delete_button_icon_path = delete_1_icon_path
        super().leaveEvent(event)
        self.update()