'''
Modal that has the following layout:
    Message
    Line edit
    Explanation
    Buttons (Cancel, Confirm)
'''

from PySide6.QtWidgets import QPushButton, QLabel, QLineEdit, QDialog, QStyle, QGraphicsOpacityEffect
from PySide6.QtCore import Qt
from PySide6.QtGui import QKeySequence, QAction
from aivalanche_app.components.custom_layouts import v_layout, h_layout

class modal_1(QDialog):
    def __init__(self, parent = None, title = 'Title', message = 'Message', explanation = 'Explanation',
                 placeholder = 'Placeholder', on_cancel = None, on_confirm = None, object_name: str = None):
        super().__init__(parent = parent)
        
        if object_name is not None:
            self.setObjectName(object_name)
        self.title = title
        self.message = message
        self.explanation = explanation
        self.placeholder = placeholder
        self.on_confirm = on_confirm
        self.on_cancel = on_cancel
        self.opacity_effect = QGraphicsOpacityEffect(self)
        
        self.init_ui()
    
    def init_ui(self):
        self.setContentsMargins(20, 20, 20, 20)
        self.setWindowTitle(self.title)
        
        # Create layout for the dialog
        layout = v_layout(spacing = 10)
        self.setLayout(layout)

        # Add label
        label = QLabel(self.message, parent = self)
        label.setObjectName('modal_message')
        layout.addWidget(label)
        
        # Add line edit
        self.line_edit = QLineEdit(self)
        self.line_edit.setPlaceholderText(self.placeholder)
        self.line_edit.textChanged.connect(self.on_text_changed)
        layout.addWidget(self.line_edit)
        
        # Add label
        label = QLabel(self.explanation, parent = self)
        label.setObjectName('modal_explanation')
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
        self.confirm_button = QPushButton(self.style().standardIcon(QStyle.StandardPixmap.SP_DialogApplyButton), "Confirm", self)
        self.confirm_button.clicked.connect(self.on_confirm_press)
        button_layout.addWidget(self.confirm_button)
        
        # Create an action for the Return key to cancel
        return_action = QAction(self)
        return_action.setShortcut(QKeySequence(Qt.Key_Return))
        return_action.triggered.connect(self.confirm_button.click)
        self.addAction(return_action)
        
        # Create an action for the Enter key to cancel
        enter_action = QAction(self)
        enter_action.setShortcut(QKeySequence(Qt.Key_Enter))
        enter_action.triggered.connect(self.confirm_button.click)
        self.addAction(enter_action)
        
        # Create an action for the Escape key to cancel
        escape_action = QAction(self)
        escape_action.setShortcut(QKeySequence(Qt.Key_Escape))
        escape_action.triggered.connect(cancel_button.click)
        self.addAction(escape_action)
        
        # Set fixed size and non-resizable
        # self.setFixedSize(self.sizeHint())
        # self.setMinimumWidth(500)
        
        self.on_text_changed()

    def on_confirm_press(self):
        if self.on_confirm is not None:
            self.on_confirm(self.line_edit.text())
        self.accept()
            
    
    def on_cancel_press(self):
        if self.on_cancel is not None:
            self.on_cancel(self.line_edit.text())
        self.reject()
    
    def on_text_changed(self):
        state = len(self.line_edit.text()) > 0
        if self.confirm_button.isEnabled() != state:
            self.confirm_button.setEnabled(state)
            self.adjust_confirm_button_opacity(state)
            
    def adjust_confirm_button_opacity(self, state):
        if state:
            self.opacity_effect.setOpacity(1)
        else:
            self.opacity_effect.setOpacity(0.3)
        self.confirm_button.setGraphicsEffect(self.opacity_effect)