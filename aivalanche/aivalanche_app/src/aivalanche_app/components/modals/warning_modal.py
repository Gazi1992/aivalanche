'''
Modal that has the following layout:
    Title
    Message
    Explanation
    OK Button
'''

from PySide6.QtWidgets import QPushButton, QDialog, QStyle, QSizePolicy
from PySide6.QtCore import Qt
from PySide6.QtGui import QKeySequence, QAction
from aivalanche_app.components.custom_layouts import v_layout, h_layout
from aivalanche_app.components.custom_label import custom_label
from aivalanche_app.paths import warning_icon_path
from aivalanche_app.components.custom_image import custom_image

class warning_modal(QDialog):
    def __init__(self, parent = None, title = 'Title', message = 'Message', explanation = 'Explanation',
                 icon_path: str = warning_icon_path, on_confirm = None, object_name: str = None):
        super().__init__(parent = parent)
        
        if object_name is not None:
            self.setObjectName(object_name)
        self.title = title
        self.message = message
        self.explanation = explanation
        self.icon_path = icon_path
        self.on_confirm = on_confirm
        
        self.init_ui()
    
    def init_ui(self):
        self.setContentsMargins(20, 20, 20, 20)
        self.setWindowTitle(self.title)
                
        main_layout = v_layout(spacing = 20)
        self.setLayout(main_layout)
        
        top_layout = h_layout(spacing = 20)
        main_layout.addLayout(top_layout)
        
        # Add the icon
        self.icon = custom_image(image_path = self.icon_path, image_height = 50, resize = 'fit')
        top_layout.addWidget(self.icon)
        
        # Create layout for the dialog
        right_layout = v_layout(spacing = 10)
        top_layout.addLayout(right_layout)

        # Add message
        self.message_label = custom_label(text = self.message, parent = self, font_size = 'normal')
        right_layout.addWidget(self.message_label)
        
        # Explanation
        self.explanation_label = custom_label(text = self.explanation, parent = self, font_size = 'small')
        right_layout.addWidget(self.explanation_label)
        
        # Create layout for buttons
        button_layout = h_layout(alignment = Qt.AlignmentFlag.AlignRight)
        main_layout.addLayout(button_layout)
        
        # Add confirm button
        self.ok_button = QPushButton(self.style().standardIcon(QStyle.StandardPixmap.SP_DialogApplyButton), "Ok", self)
        self.ok_button.clicked.connect(self.on_ok_press)
        button_layout.addWidget(self.ok_button)
        
        # Create an action for the Enter key to cancel
        enter_action = QAction(self)
        enter_action.setShortcut(QKeySequence(Qt.Key_Enter))
        enter_action.triggered.connect(self.ok_button.click)
        self.addAction(enter_action)

    def on_ok_press(self):
        if self.on_confirm is not None:
            self.on_confirm()
        self.accept()
        
    def update_icon(self, icon_path: str = warning_icon_path):
        if self.icon_path != icon_path:
            self.icon_path = icon_path
            self.icon.update_image(self.icon_path)
        
    def update_title(self, title: str = 'Title'):
        if self.title != title:
            self.title = title
            self.setWindowTitle(self.title)
    
    def update_message(self, message: str = 'Message'):
        if self.message != message:
            self.message = message
            self.message_label.setText(self.message)
    
    def update_explanation(self, explanation: str = 'Explanation'):
        if self.explanation != explanation:
            self.explanation = explanation
            self.explanation_label.setText(self.explanation)

        