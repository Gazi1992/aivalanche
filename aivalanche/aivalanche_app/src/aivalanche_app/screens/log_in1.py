from PySide6.QtWidgets import QWidget, QLineEdit
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
from aivalanche_app.components.modals.loading_modal import loading_modal

class log_in(QWidget):   
    
    go_to_home = Signal()
    update_store = Signal(dict)
    
    def __init__(self, parent = None, store: store = None, object_name: str = None):
        super().__init__(parent = parent)
        self.store = store
        if object_name is not None:
            self.setObjectName(object_name)
        self.init_ui()
        
        self._loading = False
        self._error = None
        self.username = None
        self.password = None
        
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

    @property
    def error(self):
        return self._error

    @error.setter
    def error(self, value):
        if self._error != value:
            self._error = value
            self.error_changed()

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
        self.username_widget = QLineEdit(parent = self)
        self.username_widget.setPlaceholderText('Username')
        self.username_widget.setFixedWidth(500)
        layout.addWidget(self.username_widget, alignment = Qt.AlignmentFlag.AlignCenter)
        
        # Password
        self.password_widget = password_text_input(parent = self)
        self.password_widget.setFixedWidth(500)
        layout.addWidget(self.password_widget, alignment = Qt.AlignmentFlag.AlignCenter)
        
        # Add space to buttons
        layout.addSpacing(10)
                
        # Log in button
        button = icon_text_button(parent = self, text = 'Log in', padding = (10, 5, 10, 5), button_width = 150,
                                  on_click = self.on_log_in_press, object_name = 'log_in_button')
        layout.addWidget(button, alignment = Qt.AlignmentFlag.AlignCenter)
        
        # Error message
        self.error_widget = custom_label(parent = self, object_name = 'error', font_size = 'small')
        layout.addWidget(self.error_widget, alignment = Qt.AlignmentFlag.AlignCenter)
        
        # Loading modal        
        self.loading_modal = loading_modal(parent = self, text = 'Confirming user credentials...')
        
    
    def error_changed(self):
        if self.error is None:
            self.error_widget.hide()
        else:
            self.error_widget.setText(self.error)
            self.error_widget.show()
        
        
    def loading_changed(self):
        if self.loading:
            self.loading_modal.start()
            self.loading_modal.exec()
        else:
            self.loading_modal.stop()
            self.loading_modal.accept()
    
    def on_log_in_press(self):
        self.validate_log_in()

    def on_query_success(self, res: dict = {}):
        if res['description'] == 'get_users':
            result = res['result']
            user = result[(result['username'] == self.username) & (result['password'] == self.password)]
            if user.empty:
                self.error = 'No user matches the username and password given! Please contact aivalanche support for further information!'
                self.loading = False
            elif len(user.index) > 1:
                self.error = 'More than 1 user matches the username and password given! Please contact aivalanche support for further information!'
                self.loading = False
            else:
                user = user.squeeze()
                user_id = user['id']
                self.update_store.emit({'user': {'id': user_id}})
                self.loading = False
                self.go_to_home.emit()
        
    def on_query_error(self, error):
        self.error = 'Error communicating to the database! Try again!'
        self.loading = False
        
    def validate_log_in(self):
        self.username = self.username_widget.text()
        if len(self.username) == 0:
            self.error = 'Username cannot be empty!'
            return
        
        self.password = self.password_widget.text()
        if len(self.password) == 0:
            self.error = 'Password cannot be empty!'
            return
        
        self.error = None       
        self.db.get_users()
        self.loading = True
        
        
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