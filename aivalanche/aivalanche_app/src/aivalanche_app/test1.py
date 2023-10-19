import sys
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QPushButton, QDialog, QLabel, QHBoxLayout

class MyWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        layout = QVBoxLayout()

        button = QPushButton("Click Me")
        button.clicked.connect(self.show_confirmation_message)

        layout.addWidget(button)
        central_widget.setLayout(layout)

    def show_confirmation_message(self):
        
        dialog = QDialog()
        dialog.exec() 
        # quit_msg = "Are you sure you want to exit the program?"

        # dialog = QDialog(self)
        # dialog.setWindowModality(Qt.WindowModal)
        # dialog.setWindowTitle("Message")
        # dialog_layout = QVBoxLayout()

        # label = QLabel(quit_msg)
        # dialog_layout.addWidget(label)

        # button_box = QHBoxLayout()
        # yes_button = QPushButton("Yes")
        # yes_button.clicked.connect(self.close)
        # no_button = QPushButton("No")
        # no_button.clicked.connect(dialog.reject)

        # button_box.addWidget(yes_button)
        # button_box.addWidget(no_button)
        # dialog_layout.addLayout(button_box)

        # dialog.setLayout(dialog_layout)

        # dialog.exec_()

if not QApplication.instance():
    app = QApplication(sys.argv)
else:
    app = QApplication.instance()

window = MyWindow()
window.show()
sys.exit(app.exec())
