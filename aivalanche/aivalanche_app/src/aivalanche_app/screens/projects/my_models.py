from functools import partial
from PySide6.QtWidgets import QWidget, QScrollArea
from PySide6.QtCore import Signal, Qt
from aivalanche_app.components.custom_layouts import v_layout, g_layout, clear_layout
from aivalanche_app.components.model_card import model_card
from aivalanche_app.paths import model_card_background_path, plus_icon_path
from aivalanche_app.components.buttons.icon_text_button import icon_text_button
from aivalanche_app.constants.dimensions import MODEL_CARD_WIDTH, MODEL_CARD_HEIGHT, MODEL_CARD_MARGIN, MODELS_NR_COLUMNS, MODEL_PLUS_ICON_HEIGHT
from aivalanche_app.components.navigation_header import navigation_header
from aivalanche_app.data_store.store import store
from aivalanche_app.components.modals.modal_1 import modal_1
from aivalanche_app.components.modals.loading_modal import loading_modal

class my_models(QWidget):
    go_to_calibration = Signal()
    go_to_projects = Signal()
    
    def __init__(self, parent = None, store: store = None, object_name: str = None):
        super().__init__(parent)
                
        if object_name is not None:
            self.setObjectName(object_name)

        self.store = store
        self.store.fetch_models_start.connect(self.on_fetch_models_start)
        self.store.fetch_models_end.connect(self.on_fetch_models_end)
        self.store.create_model_start.connect(self.on_create_model_start)
        self.store.create_model_end.connect(self.on_create_model_end)
        
        self.init_ui()
        
        self._loading = False
        self._error = None
        
        
    @property
    def loading(self):
        return self._loading

    @loading.setter
    def loading(self, value):
        if self._loading != value:
            self._loading = value
            self.loading_changed()
    
    def loading_changed(self):
        if self.loading:
            self.loading_modal.start()
            self.loading_modal.exec()
        else:
            self.loading_modal.stop()
            self.loading_modal.accept()
    
    @property
    def error(self):
        return self._error

    @error.setter
    def error(self, value):
        if self._error != value:
            self._error = value
            self.error_changed()
            
    def error_changed(self):
        self.new_model_dialog.error = self.error
        
    def init_ui(self):
        layout = v_layout(parent = self)
        
        # Header Section
        self.header_navigation = [{'text': 'Projects', 'on_click': self.on_projects_press},
                                  {'text': self.store.active_project.title if self.store.active_project is not None else 'Models', 'on_click': None}]
        self.header_widget = navigation_header(navigation_path = self.header_navigation, on_search_text_changed = self.on_search, object_name = 'header')
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
                
        self.setLayout(layout)
        
        # Create an instance of the custom dialog
        self.new_model_dialog = modal_1(parent = self, title = 'New model', placeholder = 'Model title',
                                        message = 'Give a title to your model', explanation = 'You can edit the title later.',
                                        on_confirm = self.on_new_model_confirm, on_cancel = self.on_new_model_cancel, object_name = 'modal')

        # Loading modal        
        self.loading_modal = loading_modal(parent = self)

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
        
        for i, m in self.store.models.iterrows():
            button = model_card(self, image_path = model_card_background_path, image_height = MODEL_CARD_HEIGHT, image_width = MODEL_CARD_WIDTH,
                                front_hover_color = (0, 0, 0, 50), front_click_color = (0, 0, 0, 100), on_click = partial(self.on_model_press, m),
                                title = m.title, created_at = m.created_at, last_modified_at = m.last_modified_at)
            row = (i + 1) // MODELS_NR_COLUMNS
            col = (i + 1) % MODELS_NR_COLUMNS
            self.grid.addWidget(button, row, col, Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
    
    def on_fetch_models_start(self):
        self.loading_modal.update_text('Fetching your models...')
        self.loading = True     
    
    def on_fetch_models_end(self, res: dict = {}):
        if res['success']:
            self.loading = False
            self.update_models()
        else:
            self.error = res['error']
            self.loading = False
            
    def on_create_model_start(self):
        self.loading_modal.update_text('Creating your new model...')
        self.loading = True
            
    def on_create_model_end(self, res: dict = {}):
        if res['success']:
            self.loading = False
            self.error = None
            self.store.fetch_models()
        else:
            self.error = res['error']
            self.loading = False
            self.on_new_model_press()
    
    def on_model_press(self, m):
        self.store.set_active_model(m)
        self.go_to_calibration.emit()

    def on_projects_press(self):
        self.go_to_projects.emit()
        
    def on_new_model_press(self):
        self.new_model_dialog.exec()
    
    def on_new_model_confirm(self, title):
        self.store.create_model(title)
        
    def on_new_model_cancel(self, project_name):
        print("User clicked Cancel")
        
    def on_search(self, text):
        print(text)