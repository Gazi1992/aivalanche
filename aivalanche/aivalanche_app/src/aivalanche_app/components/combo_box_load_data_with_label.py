from PySide6.QtWidgets import QWidget, QLabel
from aivalanche_app.components.custom_layouts import v_layout, h_layout
from aivalanche_app.components.combo_box_load_data import combo_box_load_data


class combo_box_load_data_with_label(QWidget):
    def __init__(self, parent = None, label: str = 'label', placeholder: str = 'placeholder',
                 caption = 'Select file', filter = 'Json file (*.json)',
                 label_position: str = 'top', spacing: int = 5, on_change: callable = None, tooltip: str = None):
        super().__init__(parent = parent)
        
        self.label = label
        self.placeholder = str(placeholder)
        self.label_position = label_position
        self.spacing = spacing
        self.caption = caption
        self.filter = filter
        self.on_change = on_change
        self.tooltip = tooltip        
        self.init_ui()
        
    def init_ui(self):
        if self.label_position not in ['top', 'bottom', 'left', 'right']:
            print('Warning: text_input_with_label requires label_position to be "top", "bottom", "right" or "left". Setting it to "top".')
            self.label_position = 'top'
        
        if self.label_position in ['top', 'bottom']:
           layout = v_layout(spacing = self.spacing)
        else:
            layout = h_layout(spacing = self.spacing)
        self.setLayout(layout)
        
        label_widget = QLabel(parent = self, text = self.label)
        combo_box = combo_box_load_data(parent = self,
                                        placeholder = self.placeholder,
                                        items = [],
                                        is_editable = True,
                                        caption = self.caption,
                                        filter = self.filter,
                                        on_combo_box_changed = self.on_change)
        
        if self.label_position in ['top', 'left']:
            layout.addWidget(label_widget, 0)
            
        layout.addWidget(combo_box)
        
        if self.label_position in ['bottom', 'right']:
            layout.addWidget(label_widget, 0)
            
        if self.tooltip is not None:
            self.setToolTip(self.tooltip)
            
           