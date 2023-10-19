from PySide6.QtWidgets import QFrame
from PySide6.QtCore import Signal
from aivalanche_app.resources.themes.style import style
from aivalanche_app.components.custom_image import custom_image
from aivalanche_app.components.custom_layouts import v_layout
from aivalanche_app.components.buttons.icon_text_button import icon_text_button
from aivalanche_app.paths import logo_path, projects_icon_path, running_icon_path, logout_icon_path
from aivalanche_app.constants.dimensions import DRAWER_LOGO_HEIGHT, DRAWER_WIDTH, DRAWER_BUTTON_ICON_WIDTH, DRAWER_BUTTON_ICON_HEIGHT, DRAWER_BUTTON_HEIGHT

class drawer(QFrame):
    
    projects_active = Signal(bool)
    running_active = Signal(bool)
    logout_active = Signal()
    
    def __init__(self, parent = None, user = None, style: style = None):
        super().__init__(parent)
        
        self.user = user
        self.style = style
                        
        # Create the layout
        layout = v_layout(parent = self, padding = (0, 0, 0, 10))
        
        # Add logo
        image_widget = custom_image(image_path = logo_path, image_height = DRAWER_LOGO_HEIGHT, resize = 'fit',
                                    padding_left = 10, padding_right = 10, padding_top = 10, padding_bottom = 10)
        layout.addWidget(image_widget)

        # Create the buttons
        self.projects_button = icon_text_button(parent = self, icon_path = projects_icon_path, button_height = DRAWER_BUTTON_HEIGHT,
                                                icon_width = DRAWER_BUTTON_ICON_WIDTH, icon_height = DRAWER_BUTTON_ICON_HEIGHT, padding = (10, 0, 0, 0),
                                                text = "Projects", checkable = True, on_click = self.on_projects_press)
        self.running_button = icon_text_button(parent = self, icon_path = running_icon_path, button_height = DRAWER_BUTTON_HEIGHT,
                                               icon_width = DRAWER_BUTTON_ICON_WIDTH, icon_height = DRAWER_BUTTON_ICON_HEIGHT, padding = (10, 0, 0, 0),
                                               text = "Running", checkable = True, on_click = self.on_running_press)
        self.logout_button = icon_text_button(parent = self, icon_path = logout_icon_path, button_height = DRAWER_BUTTON_HEIGHT,
                                              icon_width = DRAWER_BUTTON_ICON_WIDTH, icon_height = DRAWER_BUTTON_ICON_HEIGHT, padding = (10, 0, 0, 0),
                                              text = "Log out", on_click = self.on_logout_press)

        # Add the buttons to the drawer
        layout.addWidget(self.projects_button)
        layout.addWidget(self.running_button)
        layout.addStretch()
        layout.addWidget(self.logout_button)
        
        # Set the style
        self.setStyleSheet(self.style.drawer)
        
        # Set minimum width
        self.setFixedWidth(DRAWER_WIDTH)
        
        # Set layout
        self.setLayout(layout)

    def on_projects_press(self, checked):
        if checked:
            self.running_button.setChecked(False)
            self.logout_button.setChecked(False)
            self.projects_active.emit(True)
        else:
            self.projects_button.setChecked(True)


    def on_running_press(self, checked):
        if checked:
            self.projects_button.setChecked(False)
            self.logout_button.setChecked(False)
            self.running_active.emit(True)
        else:
            self.running_button.setChecked(True)
            
    
    def on_logout_press(self):
        self.logout_active.emit()


    def set_projects_active(self):
        self.projects_button.click()
        

    def set_running_active(self):
        self.running_button.click()
        
    