from PySide6.QtWidgets import QWidget, QScrollArea, QFrame, QSizePolicy
from PySide6.QtCore import Qt, QRect
from PySide6.QtGui import QPainter, QPixmap
from aivalanche_app.components.custom_layouts import h_layout, v_layout, g_layout, clear_layout
from aivalanche_app.components.custom_combo_box_with_label import custom_combo_box_with_label
from aivalanche_app.components.text_input_with_label import text_input_with_label
from aivalanche_app.components.custom_label import custom_label
from aivalanche_app.components.custom_checkbox_with_text import custom_checkbox_with_text
from aivalanche_app.components.buttons.text_button import text_button
from aivalanche_app.paths import delete_1_icon_path, delete_1_hover_icon_path, delete_1_press_icon_path
from aivalanche_app.helper_functions import positive_number_validator
import shortuuid

class loss_part_card(QFrame):
    def __init__(self, parent = None, id: str = None, weight: float = 1, norm: bool = True, transform: str = None, transforms_available: list[str] = [],
                 groups: list[str] = [], active_groups: list[str] = [], object_name: str = None, on_delete_button_clicked: callable = None, on_change: callable = None):
        super().__init__(parent = parent)
        
        if len(transforms_available) == 0:
            transforms_available = ['None', 'Log', 'Abs', '1st derivative', '2nd derivative']
        
        if id is None:
            id = shortuuid.uuid()
        
        self.id = id
        self.weight = weight
        self.norm = norm
        self.transform = transform
        self.transforms_available = transforms_available
        self.active_groups = active_groups
        self.groups = sorted(list(set(groups).union(set(active_groups))))
        self.groups_checkboxes = {}
        self.groups_checkboxes_widgets = {}
        self.object_name = object_name
        self.on_delete_button_clicked = on_delete_button_clicked
        self.on_change = on_change
        
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
        
    @property
    def loss_part_info(self):        
        return {'id': self.id,
                'group_types': self.active_groups,
                'metric_type': 'rmse',
                'weight': float(self.weight),
                'norm': self.norm,
                'transform': self.transform,
                'extra_args': {}}        
        
    def init_ui(self):
        self.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Minimum)
        
        layout = h_layout(spacing = 10)
        self.setLayout(layout)
        self.setFixedHeight(130)

        left_layout = v_layout(spacing = 0, alignment = Qt.AlignmentFlag.AlignTop)
        layout.addLayout(left_layout, 0)
        
        property_width = 150
        
        # # id
        # id_widget = text_input_with_label(parent = self, label = 'id', label_position = 'left', spacing = 10, placeholder = 'enter an id', text_edit_width = property_width)
        # left_layout.addWidget(id_widget, 1)
        
        # weight
        weight_widget = text_input_with_label(parent = self, label = 'weight', label_position = 'left', spacing = 10, placeholder = '1',
                                              initial_value = self.weight, text_edit_width = property_width, on_change = self.on_weight_change,
                                              validator = positive_number_validator(self))
        left_layout.addWidget(weight_widget, 1)
        
        # norm
        norm_widget = custom_combo_box_with_label(parent = self, label = 'norm', label_position = 'left', spacing = 10,
                                                  items = ['True', 'False'], active_item = self.norm,
                                                  combo_box_width = property_width, on_change = self.on_norm_change)
        left_layout.addWidget(norm_widget, 1)
        
        # transform
        transform_widget = custom_combo_box_with_label(parent = self, label = 'transform', label_position = 'left',spacing = 10,
                                                       items = self.transforms_available, active_item = self.transform, 
                                                       combo_box_width = property_width, on_change = self.on_transform_change)
        left_layout.addWidget(transform_widget, 1)
        
        # Separation line
        line = QFrame(self)
        line.setFixedWidth(1)
        line.setStyleSheet("background-color: rgba(6, 34, 121, 128); border: none; margin:")
        layout.addWidget(line)
        
        # right layout
        right_layout = v_layout(spacing = 10, alignment = Qt.AlignmentFlag.AlignTop)
        layout.addLayout(right_layout, 1)
        
        # right header layout
        right_header_layout = h_layout()
        right_layout.addLayout(right_header_layout)
        
        # group types
        group_types_label = custom_label(text = 'Group types')
        right_header_layout.addWidget(group_types_label, alignment = Qt.AlignmentFlag.AlignVCenter)
        
        # select/unselect all button
        self.select_all_button = text_button(parent = self, label = 'Select all', switch_label = 'Unselect all', object_name = 'loss_function_select_all', on_click = self.on_select_all)
        right_header_layout.addWidget(self.select_all_button, alignment = Qt.AlignmentFlag.AlignVCenter)
        
        right_header_layout.addSpacing(30)
        
        # scroll area for group types
        self.scroll_area = QScrollArea(parent = self)
        self.scroll_area.setContentsMargins(0, 0, 0, 0)
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Minimum)
        right_layout.addWidget(self.scroll_area)
        
        # Create scroll widget
        self.scroll_widget = QWidget(self)
        self.scroll_layout = g_layout(vertical_spacing = 5, alignment = Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
        self.scroll_widget.setLayout(self.scroll_layout)
        self.scroll_area.setWidget(self.scroll_widget)
        
        self.update_groups(self.groups)
    
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
        
    def update_groups(self, groups: list[str] = []):        
        self.groups_checkboxes = {}
        self.groups_checkboxes_widgets = {}
        self.groups = groups
        clear_layout(self.scroll_layout)
        for index, group in enumerate(self.groups):
            state = group in self.active_groups
            self.groups_checkboxes_widgets[group] = custom_checkbox_with_text(parent = self, text = group, on_click = self.on_group_selected, state = state)
            row = index // 3
            col = index % 3
            self.scroll_layout.addWidget(self.groups_checkboxes_widgets[group], row, col)  
            self.groups_checkboxes[group] = state
        self.update_select_button()
    
    def on_group_selected(self, state, text):
        self.groups_checkboxes[text] = state
        if state and not text in self.active_groups:
            self.active_groups.append(text)
        elif not state and text in self.active_groups:
            self.active_groups.remove(text)
            
        if self.on_change is not None:
            self.on_change(self.loss_part_info)
        
        self.update_select_button()
        
    # Check if the select_all button needs to be updated
    def update_select_button(self):
        values = self.groups_checkboxes.values()
        label = self.select_all_button.text()
        if (all(values) and label == 'Select all') or (not any(values) and label == 'Unselect all'):
            self.select_all_button.switch_text()
        
    def on_select_all(self, text):
        state = text == 'Select all'
        for key in self.groups_checkboxes_widgets.keys():
            self.groups_checkboxes_widgets[key].set_state(state, emit_on_click = False)
            self.groups_checkboxes[key] = state
            if state:
                self.active_groups = list(self.groups_checkboxes.keys())
            else:
                self.active_groups = []
        if self.on_change is not None:
            self.on_change(self.loss_part_info)
            
    def on_weight_change(self, val):
        self.weight = float(val)
        if self.on_change is not None:
            self.on_change(self.loss_part_info)
    
    def on_norm_change(self, val):
        self.norm = val
        if self.on_change is not None:
            self.on_change(self.loss_part_info)
            
    def on_transform_change(self, val):
        self.transform = val
        if self.on_change is not None:
            self.on_change(self.loss_part_info)