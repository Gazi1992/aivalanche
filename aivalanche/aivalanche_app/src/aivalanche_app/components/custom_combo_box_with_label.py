from PySide6.QtWidgets import QWidget, QLabel
from aivalanche_app.components.custom_layouts import v_layout, h_layout
from aivalanche_app.components.custom_combo_box import custom_combo_box


class custom_combo_box_with_label(QWidget):
    def __init__(self, parent = None, label: str = 'label', placeholder: str = 'placeholder', is_editable: bool = False,
                 items: list[str] = [], label_position: str = 'top', spacing: int = 5, on_change: callable = None, object_name: str = None):
        super().__init__(parent = parent)
        
        self.label = label
        self.placeholder = str(placeholder)
        self.is_editable = is_editable
        self.items = items
        self.label_position = label_position
        self.spacing = spacing
        self.on_change = on_change
        self.object_name = object_name
        
        self.init_ui()
        
    
    def init_ui(self):
        
        if self.label_position not in ['top', 'bottom', 'left', 'right']:
            print('Warning: custom_combo_box_with_label requires label_position to be "top", "bottom", "right" or "left". Setting it to "top".')
            self.label_position = 'top'
        
        if self.label_position in ['top', 'bottom']:
           layout = v_layout(spacing = self.spacing)
        else:
            layout = h_layout(spacing = self.spacing)
        self.setLayout(layout)
        
        
        label_widget = QLabel(parent = self, text = self.label)
        combo_box = custom_combo_box(parent = self,
                                     placeholder = self.placeholder,
                                     items = self.items,
                                     is_editable = self.is_editable,
                                     on_change = self.on_change)
        
        if self.label_position in ['top', 'left']:
            layout.addWidget(label_widget, 0)
        
        layout.addWidget(combo_box)

        if self.label_position in ['bottom', 'right']:
            layout.addWidget(label_widget, 0)
        
        if self.object_name is not None:
            self.setObjectName(self.object_name)
            label_widget.setObjectName(self.object_name)
            combo_box.setObjectName(self.object_name)
        
        