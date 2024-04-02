from PySide6.QtWidgets import QWidget, QLineEdit, QLabel
from PySide6.QtCore import Signal, Qt, QPoint
from PySide6.QtGui import QPainter, QColor
from aivalanche_app.data_store.store import store
from aivalanche_app.components.custom_layouts import v_layout
from aivalanche_app.components.custom_image import custom_image
from aivalanche_app.paths import logo_path
from aivalanche_app.components.buttons.icon_text_button import icon_text_button
from aivalanche_app.components.custom_label import custom_label
from aivalanche_app.components.password_text_input import password_text_input
from aivalanche_app.data_store.db import db
from aivalanche_app.components.loading_spinner import loading_spinner
from aivalanche_app.components.modals.loading_modal import loading_modal

class log_in(QWidget):   
    
    go_to_home = Signal()
    
    def __init__(self, parent = None, store: store = None, object_name: str = None):
        super().__init__(parent = parent)
        self.store = store
        if object_name is not None:
            self.setObjectName(object_name)
        self._loading = False
        self.init_ui()
        
        self.db = db(on_query_success = self.on_query_success, on_query_error = self.on_query_error)
        self.db.connect_to_db()

    @property
    def loading(self):
        return self._loading

    @loading.setter
    def loading(self, value):
        if self._loading != value:
            self._loading = value
            self.loading_changed()

    def init_ui(self):

        layout = v_layout(spacing = 10, padding = (0, 100, 0, 100), alignment = Qt.AlignmentFlag.AlignTop)
        self.setLayout(layout)
        
        # Logo
        logo = custom_image(image_path = logo_path, image_height = 200, resize = 'fit')
        layout.addWidget(logo)

        # Welcome message
        label = custom_label(parent = self, text = 'Welcome to aivalanche!', font_size = 'huge')
        layout.addWidget(label, alignment = Qt.AlignmentFlag.AlignCenter)
        
        layout.addSpacing(100)
        
        # Username
        self.username = QLineEdit(parent = self)
        self.username.setPlaceholderText('Username')
        self.username.setFixedWidth(500)
        layout.addWidget(self.username, alignment = Qt.AlignmentFlag.AlignCenter)
        
        # Password
        self.password = password_text_input(parent = self)
        self.password.setFixedWidth(500)
        layout.addWidget(self.password, alignment = Qt.AlignmentFlag.AlignCenter)
        
        # Add space to buttons
        layout.addSpacing(10)
                
        # Log in button
        button = icon_text_button(parent = self, text = 'Log in', padding = (10, 5, 10, 5), button_width = 150,
                                  on_click = self.on_log_in_press, object_name = 'log_in_button')
        layout.addWidget(button, alignment = Qt.AlignmentFlag.AlignCenter)
        
        # Spinner
        self.spinner_layout = v_layout()
        self.loading_spinner = loading_spinner()
        self.spinner_layout.addWidget(self.loading_spinner)
        self.loading_spinner.start()
        
        self.loading_modal = loading_modal(parent = self)
        
        
    def loading_changed(self):
        if self.loading:
            self.loading_modal.start()
            self.loading_modal.exec()
        else:
            self.loading_modal.stop()
            self.loading_modal.accept()
        
    
    def on_log_in_press(self):
        # self.go_to_home.emit()
        self.db.retrieve_data('users')
        self.loading = True

    
    def on_query_success(self, res: list = []):
        print(res)
        self.loading = False
        
    def on_query_error(self, error):
        print(error)
        self.loading = False
        
        
    def paintEvent(self, event):
        painter = QPainter(self)
        
        painter.save()
        
        painter.setRenderHint(QPainter.Antialiasing)
        center = QPoint(self.rect().x(), self.rect().y())
        painter.setBrush(QColor(self.store.style.colors['background_2']))
        painter.setPen(Qt.NoPen)
        radius = min(self.width(), self.height()) * 0.35
        painter.drawEllipse(center, radius, radius)        
        
        painter.restore()

        super().paintEvent(event)