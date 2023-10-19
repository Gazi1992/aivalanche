'''
Modal that has the following layout:
    Message
    Line edit
    Explanation
    Buttons (Cancel, Confirm)
'''

from PySide6.QtWidgets import QPushButton, QLabel, QLineEdit, QDialog, QStyle
from PySide6.QtCore import Qt
from PySide6.QtGui import QKeySequence, QAction
from aivalanche_app.components.custom_layouts import v_layout, h_layout
from aivalanche_app.resources.themes.style import style

class modal_1(QDialog):
    def __init__(self, parent = None, title = 'Title', message = 'Message', explanation = 'Explanation',
                 placeholder = 'Placeholder', on_cancel = None, on_confirm = None, style: style = None):
        super().__init__(parent = parent)
        
        self.on_confirm = on_confirm
        self.on_cancel = on_cancel
        
        self.setContentsMargins(20, 20, 20, 20)
        self.setWindowTitle(title)
        self.setStyleSheet(style.modal_1)
        
        # Create layout for the dialog
        layout = v_layout(spacing = 10)

        # Add label
        label = QLabel(message, parent = self)
        label.setObjectName('message')
        layout.addWidget(label)
        
        # Add line edit
        self.line_edit = QLineEdit(self)
        self.line_edit.setPlaceholderText(placeholder)
        layout.addWidget(self.line_edit)
        
        # Add label
        label = QLabel(explanation, parent = self)
        label.setObjectName('explanation')
        layout.addWidget(label)
        
        # Add space to buttons
        layout.addSpacing(20)
        
        # Create layout for buttons
        button_layout = h_layout(spacing = 10, alignment = Qt.AlignmentFlag.AlignRight)
        layout.addLayout(button_layout)
        
        # Add cancel button
        cancel_button = QPushButton(self.style().standardIcon(QStyle.StandardPixmap.SP_DialogCancelButton), "Cancel", self)
        cancel_button.clicked.connect(self.on_cancel_press)
        button_layout.addWidget(cancel_button)
        
        # Add confirm button
        confirm_button = QPushButton(self.style().standardIcon(QStyle.StandardPixmap.SP_DialogApplyButton), "Confirm", self)
        confirm_button.clicked.connect(self.on_confirm_press)
        button_layout.addWidget(confirm_button)
        
        # Create an action for the Return key to cancel
        return_action = QAction(self)
        return_action.setShortcut(QKeySequence(Qt.Key_Return))
        return_action.triggered.connect(confirm_button.click)
        self.addAction(return_action)
        
        # Create an action for the Enter key to cancel
        enter_action = QAction(self)
        enter_action.setShortcut(QKeySequence(Qt.Key_Enter))
        enter_action.triggered.connect(confirm_button.click)
        self.addAction(enter_action)
        
        # Create an action for the Escape key to cancel
        escape_action = QAction(self)
        escape_action.setShortcut(QKeySequence(Qt.Key_Escape))
        escape_action.triggered.connect(cancel_button.click)
        self.addAction(escape_action)

        # Set the layout for the dialog
        self.setLayout(layout)
        
        # Set fixed size and non-resizable
        self.setFixedSize(self.sizeHint())
        
        
    def on_confirm_press(self):
        if self.on_confirm is not None:
            self.on_confirm(self.line_edit.text())
        self.accept()
            
    
    def on_cancel_press(self):
        if self.on_cancel is not None:
            self.on_cancel(self.line_edit.text())
        self.reject()
        