from functools import partial
from PySide6.QtWidgets import QWidget, QScrollArea
from PySide6.QtCore import Signal, Qt
from aivalanche_app.components.custom_layouts import v_layout, g_layout, clear_layout
from aivalanche_app.components.model_card import model_card
from aivalanche_app.paths import model_card_background_path, plus_icon_path
from aivalanche_app.components.buttons.icon_text_button import icon_text_button
from aivalanche_app.constants.dimensions import MODEL_CARD_WIDTH, MODEL_CARD_HEIGHT, MODEL_CARD_MARGIN, MODELS_NR_COLUMNS, MODEL_PLUS_ICON_HEIGHT
from aivalanche_app.components.header import header
from aivalanche_app.data_store.store import store
from aivalanche_app.components.modals.modal_1 import modal_1


class my_models(QWidget):
    go_to_calibration = Signal()
    go_to_projects = Signal()
    
    def __init__(self, parent = None, store: store = None, object_name: str = None):
        super().__init__(parent)
        
        self.store = store
        
        if object_name is not None:
            self.setObjectName(object_name)
            
        self.init_ui()
        
    
    def init_ui(self):
        layout = v_layout(parent = self)
        
        # Header Section
        self.header_navigation = [{'text': 'Projects', 'on_click': self.on_projects_press},
                                  {'text': self.store.active_project.title if self.store.active_project is not None else 'Models', 'on_click': None}]
        self.header_widget = header(navigation_path = self.header_navigation, on_search_text_changed = self.on_search, object_name = 'header')
        layout.addWidget(self.header_widget)
        self.update_header()
        
        # Scrollable Buttons Section
        scroll_area = QScrollArea()
        scroll_area.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(scroll_area)
        
        scroll_widget = QWidget(self)
        scroll_area.setWidget(scroll_widget)
        scroll_area.setWidgetResizable(True)
        
        self.grid = g_layout(horizontal_spacing = MODEL_CARD_MARGIN, vertical_spacing = MODEL_CARD_MARGIN)
        self.grid.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        scroll_widget.setLayout(self.grid)
        
        self.update_models()
        
        self.setLayout(layout)
        
        # Create an instance of the custom dialog
        self.new_model_dialog = modal_1(parent = self, title = 'New model', placeholder = 'Model name',
                                        message = 'Give a name to your model', explanation = 'You can edit the name later.',
                                        on_confirm = self.on_new_model_confirm, on_cancel = self.on_new_model_cancel, object_name = 'modal')


    # Update header
    def update_header(self):
        self.header_navigation = [{'text': 'Projects', 'on_click': self.on_projects_press},
                                  {'text': self.store.active_project.title if self.store.active_project is not None else 'Models', 'on_click': None}]
        self.header_widget.update_navigation_path(self.header_navigation)
    
    
    # Add buttons to the grid layout (example)
    def update_models(self):
        clear_layout(self.grid)
        
        # New model button
        new_model_button = icon_text_button(parent = self, icon_path = plus_icon_path, button_height = MODEL_CARD_HEIGHT, button_width = MODEL_CARD_WIDTH,
                                            icon_height = MODEL_PLUS_ICON_HEIGHT, icon_position = 'top', direction = 'vertical', checkable = False,
                                            padding = (0, MODEL_CARD_HEIGHT * 0.35, 0, MODEL_CARD_HEIGHT * 0.2),
                                            text = "New model", text_alignment = Qt.AlignmentFlag.AlignCenter,
                                            on_click = self.on_new_model_press, object_name = 'new_model')
        
        self.grid.addWidget(new_model_button, 0, 0, Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
        
        for i, m in enumerate(self.store.models):
            button = model_card(self, image_path = model_card_background_path, image_height = MODEL_CARD_HEIGHT, image_width = MODEL_CARD_WIDTH,
                                front_hover_color = (0, 0, 0, 50), front_click_color = (0, 0, 0, 100), on_click = partial(self.on_model_press, m),
                                title = m.title, created = m.created, last_modified = m.last_modified)
            row = (i + 1) // MODELS_NR_COLUMNS
            col = (i + 1) % MODELS_NR_COLUMNS
            self.grid.addWidget(button, row, col, Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
    

    def on_model_press(self, m):
        self.store.set_active_model(m.id)
        self.go_to_calibration.emit()


    def on_projects_press(self):
        self.go_to_projects.emit()
        
        
    def on_new_model_press(self):
        # Show the dialog and get the result
        self.new_model_dialog.exec()

    
    def on_new_model_confirm(self, model_name):
        print(f"User clicked Confirm. Project name: {model_name}")
        
        
    def on_new_model_cancel(self, project_name):
        print("User clicked Cancel")

        
    def on_search(self, text):
        print(text)