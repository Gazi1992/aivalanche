from PySide6.QtWidgets import QWidget, QStackedWidget
from aivalanche_app.components.custom_layouts import v_layout
from aivalanche_app.screens.projects.my_projects import my_projects
from aivalanche_app.screens.projects.my_models import my_models
from aivalanche_app.screens.projects.my_calibration import my_calibration
from aivalanche_app.data_store.store import store
from aivalanche_app.constants.dimensions import PROJECTS_TAB_PADDING_BOTTOM, PROJECTS_TAB_PADDING_LEFT, PROJECTS_TAB_PADDING_RIGHT, PROJECTS_TAB_PADDING_TOP
from aivalanche_app.resources.themes.style import style


class projects_tab(QWidget):
    def __init__(self, parent = None, store: store = None, style: style = None):
        super().__init__(parent)
        
        self.store = store
        self.style = style
        
        layout = v_layout(parent = self, padding = (PROJECTS_TAB_PADDING_LEFT, PROJECTS_TAB_PADDING_TOP, PROJECTS_TAB_PADDING_RIGHT, PROJECTS_TAB_PADDING_BOTTOM))
        
        # Create the stacked widget
        self.stacked_widget = QStackedWidget(self)
        # stacked_widget.setStyleSheet('background-color: red')
        
        # Create my_projects screens
        self.my_projects = my_projects(parent = self.stacked_widget, store = self.store, style = self.style)
        self.my_projects.go_to_models.connect(self.go_to_my_models)
        
        # Create my_models screens
        self.my_models = my_models(parent = self.stacked_widget, store = self.store, style = self.style)
        self.my_models.go_to_calibration.connect(self.go_to_my_calibration)
        self.my_models.go_to_projects.connect(self.go_to_my_projects)
        
        # Create my_calibration screens
        self.my_calibration = my_calibration(parent = self.stacked_widget, store = self.store, style = self.style)
        self.my_calibration.go_to_models.connect(self.go_to_my_models)
        self.my_calibration.go_to_projects.connect(self.go_to_my_projects)
        
        # Add screens
        self.stacked_widget.addWidget(self.my_projects)
        self.stacked_widget.addWidget(self.my_models)
        self.stacked_widget.addWidget(self.my_calibration)
        
        # Add the stacked widget to layout
        layout.addWidget(self.stacked_widget)
        
        # Set layout
        self.setLayout(layout)
        
    def go_to_my_projects(self):
        self.my_projects.update_projects()
        self.stacked_widget.setCurrentWidget(self.my_projects)
        
    def go_to_my_models(self):
        self.my_models.update_models()
        self.my_models.update_header()
        self.stacked_widget.setCurrentWidget(self.my_models)
        
    def go_to_my_calibration(self):
        self.my_calibration.update_header()
        self.stacked_widget.setCurrentWidget(self.my_calibration)