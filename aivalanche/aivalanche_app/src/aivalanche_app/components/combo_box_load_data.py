from PySide6.QtWidgets import QWidget, QComboBox, QFileDialog, QGraphicsOpacityEffect
from aivalanche_app.components.custom_layouts import h_layout
from aivalanche_app.paths import upload_icon_path
from aivalanche_app.components.buttons.icon_text_button import icon_text_button

class combo_box_load_data(QWidget):
    def __init__(self, parent = None, items: list = [], acitve_item: str = None,
                 caption = 'Select file', filter = 'Json file (*.json)',
                 on_combo_box_changed: callable = None, on_load_button_press: callable = None,
                 is_enabled: bool = True):
                
        super().__init__(parent)
        
        self.caption = caption
        self.filter = filter
        self.on_combo_box_changed = on_combo_box_changed
        self.on_load_button_press = on_load_button_press
        
        self.items = items
        self.active_item = acitve_item
        self.is_enabled = None
        
        self.init_ui()
        self.set_state(is_enabled)
        
        
    def init_ui(self):
        
        # Create load data layout
        layout = h_layout(spacing = 10)
        self.setLayout(layout)
        
        # Create drop-down widget
        self.drop_down_widget = QComboBox(parent = self)
        self.drop_down_widget.setFixedHeight(30)
        self.drop_down_widget.currentTextChanged.connect(lambda text: self.on_drop_down_text_changed(text))
        if len(self.items) > 0:
            self.drop_down_widget.addItems(self.items)
            if self.active_item is not None:
                self.drop_down_widget.setCurrentText(self.active_item)
        layout.addWidget(self.drop_down_widget, 1)
        
        # Create load data button
        load_data_button = icon_text_button(parent = self, icon_path = upload_icon_path, icon_height = 25, on_click = self.on_load_data_button_click)
        layout.addWidget(load_data_button, 0)
    
        


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
        opacity_effect = QGraphicsOpacityEffect(self)
        if self.is_enabled:
            opacity_effect.setOpacity(1)
        else:
            opacity_effect.setOpacity(0.3)
        self.setGraphicsEffect(opacity_effect)

    
    def on_drop_down_text_changed(self, text):
        if self.on_combo_box_changed is not None:
            self.on_combo_box_changed(text)
        else:
            print(text)
    
    
    def on_load_data_button_click(self):
        response = QFileDialog.getOpenFileName(parent = self, caption = self.caption, filter = self.filter)
        if len(response[0]) > 0:
            ref_data_file = response[0]
            if ref_data_file not in self.items:                
                self.items.append(ref_data_file)
                self.drop_down_widget.addItem(ref_data_file)
                
            self.drop_down_widget.setCurrentText(ref_data_file)
            self.active_item = ref_data_file
            
            if self.on_load_button_press is not None:
                self.on_load_button_press(ref_data_file)