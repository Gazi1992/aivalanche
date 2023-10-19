import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QPushButton, QFrame

# Sample stylesheet
stylesheet = """
    QFrame#Drawer {
        background-color: red;  /* Red background for the drawer */
    }

"""

class Drawer(QFrame):
    def __init__(self):
        super().__init__()
        self.setObjectName('Drawer')  # Set the object name for the drawer
        
        # Create a vertical layout for the drawer
        layout = QVBoxLayout(self)

        # Add a button to the drawer
        button1 = QPushButton("Drawer Button 1")
        button2 = QPushButton("Drawer Button 2")
        
        layout.addWidget(button1)
        layout.addStretch()
        layout.addWidget(button2)
        

class MyWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Minimal PySide6 Drawer Example")

        # Create a central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Create a vertical layout for the central widget
        layout = QVBoxLayout(central_widget)

        # Create the drawer widget and add it to the layout
        drawer_widget = Drawer()
        layout.addWidget(drawer_widget)

def main():
    if not QApplication.instance():
        app = QApplication(sys.argv)
    else:
        app = QApplication.instance()    
        
    # Apply the stylesheet
    app.setStyleSheet(stylesheet)
    
    window = MyWindow()
    window.show()
    sys.exit(app.exec())

main()
