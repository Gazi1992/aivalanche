from PySide6.QtWidgets import QHBoxLayout, QWidget, QLabel
from PySide6.QtCore import QPropertyAnimation, QRect, QTimer, Qt

class snackbar(QWidget):
    def __init__(self, parent = None, message = 'Snackbar message', object_name: str = None):
        super().__init__(parent)
        
        if object_name is not None:
            self.setObjectName(object_name)
        else:
            self.setStyleSheet("background-color: red; color: white; padding: 10px; border-radius: 5px;")
        
        layout = QHBoxLayout()
        label = QLabel(message)
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(label)
        self.setLayout(layout)
        
        self.parent_rect = self.parent().rect()
        # self.setMaximumWidth(self.parent_rect .width() * 0.4)
        self.setMinimumHeight(60)
        self.setMinimumWidth(200)
        
    def show_snackbar(self):        
        start_y = -self.height()
        end_y = 0
        
        self.setGeometry((self.parent_rect.width() - self.width()) // 2, start_y, self.width(), self.height())
        self.show()
        
        self.animation = QPropertyAnimation(self, b"geometry")
        self.animation.setDuration(500)
        self.animation.setStartValue(QRect((self.parent_rect.width() - self.width()) // 2, start_y, self.width(), self.height()))
        self.animation.setEndValue(QRect((self.parent_rect.width() - self.width()) // 2, end_y, self.width(), self.height()))
        self.animation.start()
        
        QTimer.singleShot(3000, self.hide_snackbar)
        
    def hide_snackbar(self):        
        start_y = 0
        end_y = -self.height()
        
        self.animation = QPropertyAnimation(self, b"geometry")
        self.animation.setDuration(500)
        self.animation.setStartValue(QRect((self.parent_rect .width() - self.width()) // 2, start_y, self.width(), self.height()))
        self.animation.setEndValue(QRect((self.parent_rect .width() - self.width()) // 2, end_y, self.width(), self.height()))
        self.animation.start()
        self.animation.finished.connect(self.close)