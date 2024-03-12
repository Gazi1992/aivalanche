from functools import partial
from PySide6.QtWidgets import QWidget, QScrollArea
from PySide6.QtCore import Signal, Qt
from aivalanche_app.components.custom_layouts import v_layout, g_layout, clear_layout
from aivalanche_app.components.project_card import project_card
from aivalanche_app.paths import project_card_background_path, plus_icon_path
from aivalanche_app.constants.dimensions import PROJECT_CARD_WIDTH, PROJECT_CARD_HEIGHT, PROJECT_CARD_MARGIN, PROJECTS_NR_COLUMNS, PROJECT_PLUS_ICON_HEIGHT
from aivalanche_app.components.buttons.icon_text_button import icon_text_button
from aivalanche_app.components.navigation_header import navigation_header
from aivalanche_app.data_store.store import store
from aivalanche_app.components.modals.modal_1 import modal_1

class my_projects(QWidget):
    go_to_models = Signal()
    
    def __init__(self, parent = None, store: store = None, object_name: str = None):
        super().__init__(parent)
        
        self.store = store
        
        if object_name is not None:
            self.setObjectName(object_name)

        self.init_ui()
        
        
    def init_ui(self):
        layout = v_layout(parent = self)
        self.setLayout(layout)

        # Header Section
        header_navigation = [{'text': 'Projects', 'on_click': None}]
        header_widget = navigation_header(navigation_path = header_navigation, on_search_text_changed = self.on_search, object_name = 'header')
        layout.addWidget(header_widget)
        
        # Scrollable buttons Section
        scroll_area = QScrollArea()
        scroll_area.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(scroll_area)
        
        scroll_widget = QWidget(self)
        scroll_widget.setObjectName('my_projects')
        scroll_area.setWidget(scroll_widget)
        scroll_area.setWidgetResizable(True)
        
        self.grid = g_layout(horizontal_spacing = PROJECT_CARD_MARGIN, vertical_spacing = PROJECT_CARD_MARGIN)
        self.grid.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        scroll_widget.setLayout(self.grid)

        self.update_projects()
        
        # Create an instance of the custom dialog
        self.new_project_dialog = modal_1(parent = self, title = 'New project', placeholder = 'Project name',
                                          message = 'Give a name to your project', explanation = 'You can edit the name later.',
                                          on_confirm = self.on_new_project_confirm, on_cancel = self.on_new_project_cancel, object_name = 'modal')
        
        
    # Add buttons to the grid layout
    def update_projects(self):
        clear_layout(self.grid)
        
        # New project button
        new_project_button = icon_text_button(parent = self, icon_path = plus_icon_path, button_height = PROJECT_CARD_HEIGHT, button_width = PROJECT_CARD_WIDTH,
                                              icon_height = PROJECT_PLUS_ICON_HEIGHT, icon_position = 'top', direction = 'vertical', checkable = False,
                                              padding = (0, PROJECT_CARD_HEIGHT * 0.35, 0, PROJECT_CARD_HEIGHT * 0.2),
                                              text = "New project", text_alignment = Qt.AlignmentFlag.AlignCenter,
                                              on_click = self.on_new_project_press, object_name = 'new_project')
        
        self.grid.addWidget(new_project_button, 0, 0, Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
        for i, p in enumerate(self.store.projects):
            button = project_card(self, image_path = project_card_background_path, image_height = PROJECT_CARD_HEIGHT, image_width = PROJECT_CARD_WIDTH,
                                front_hover_color = (0, 0, 0, 50), front_click_color = (0, 0, 0, 100), on_click = partial(self.on_project_press, p),
                                title = p.title, created = p.created, last_modified = p.last_modified)
            row = (i + 1) // PROJECTS_NR_COLUMNS
            col = (i + 1) % PROJECTS_NR_COLUMNS
            self.grid.addWidget(button, row, col, Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)


    def on_project_press(self, p):
        self.store.set_active_project(id = p.id)
        self.go_to_models.emit()


    def on_search(self, text):
        print(text)


    def on_new_project_press(self, text):
        # Show the dialog and get the result
        self.new_project_dialog.exec()

            
    def on_new_project_confirm(self, project_name):
        print(f"User clicked Confirm. Project name: {project_name}")
        
        
    def on_new_project_cancel(self, project_name):
        print("User clicked Cancel")
