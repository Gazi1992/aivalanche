from PySide6.QtWidgets import QWidget, QFileDialog
from aivalanche_app.components.custom_layouts import h_layout
from aivalanche_app.components.custom_combo_box import custom_combo_box
from aivalanche_app.paths import upload_icon_path
from aivalanche_app.components.buttons.icon_text_button import icon_text_button

class combo_box_load_data(QWidget):
    def __init__(self, parent = None, items: list = [], active_item: str = None,
                 caption = 'Select file', filter = 'Json file (*.json)', placeholder: str = 'Select',
                 on_combo_box_changed: callable = None, on_load_button_press: callable = None, on_import_new_file: callable = None,
                 object_name: str = None, is_enabled: bool = True, is_editable: bool = True):
                
        super().__init__(parent)
        
        self.caption = caption
        self.filter = filter
        self.placeholder = placeholder
        self.on_combo_box_changed = on_combo_box_changed
        self.on_load_button_press = on_load_button_press
        self.on_import_new_file = on_import_new_file
        
        self.items = items
        self.active_item = active_item
        self.is_enabled = None
        self.is_editable = is_editable
        self.object_name = object_name
        if object_name is not None:
            self.setObjectName(object_name)
                
        self.init_ui()
        self.set_state(is_enabled)
        
    def init_ui(self):
        # Create load data layout
        layout = h_layout(spacing = 10)
        self.setLayout(layout)
        
        # Create drop-down widget
        self.drop_down_widget = custom_combo_box(parent = self,
                                                 items = self.items,
                                                 active_item = self.active_item,
                                                 object_name = self.object_name,
                                                 placeholder = self.placeholder,
                                                 is_editable = self.is_editable,
                                                 on_change = self.on_drop_down_text_changed)
        layout.addWidget(self.drop_down_widget, 1)
        
        # Create load data button
        self.load_data_button = icon_text_button(parent = self,
                                                 icon_path = upload_icon_path,
                                                 icon_height = 25,
                                                 on_click = self.on_load_data_button_click,
                                                 object_name = self.object_name)
        layout.addWidget(self.load_data_button, 0)
    

    def toggle_state(self):
        self.set_state(not self.is_enabled)
        
    def update_items(self, items: list = [], trigger_on_change_slot: bool = False):
        self.items = items
        self.drop_down_widget.update_items(items, trigger_on_change_slot)
        
    def set_active_item(self, item, trigger_on_change_slot: bool = True):
        if item in self.items:
            self.active_item = item
            if not trigger_on_change_slot:
                self.drop_down_widget.disconnect_on_change_slot()
                self.drop_down_widget.setCurrentText(item)
                self.drop_down_widget.connect_on_change_slot()
            else:
                self.drop_down_widget.setCurrentText(item)
        else:
            self.drop_down_widget.setCurrentIndex(-1)
        
    def set_state(self, state: bool = True):
        if state != self.is_enabled:
            self.is_enabled = state
            self.setEnabled(self.is_enabled)
            self.drop_down_widget.set_state(self.is_enabled)
            self.load_data_button.set_state(self.is_enabled)
    
    def on_drop_down_text_changed(self, text):
        if self.on_combo_box_changed is not None:
            self.on_combo_box_changed(text)
        else:
            print(text)
    
    def on_load_data_button_click(self):
        response = QFileDialog.getOpenFileName(parent = self, caption = self.caption, filter = self.filter)
        if len(response[0]) > 0:
            ref_data_file = response[0]
            if self.on_import_new_file is not None:
                self.on_import_new_file(ref_data_file)
            else:
                if ref_data_file not in self.items:
                    self.items.append(ref_data_file)
                    self.drop_down_widget.addItem(ref_data_file)

                self.drop_down_widget.setCurrentText(ref_data_file)
                self.active_item = ref_data_file
            
            if self.on_load_button_press is not None:
                self.on_load_button_press(ref_data_file)