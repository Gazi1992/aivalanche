import sys
from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QLabel, QFrame, QDialog
from PySide6.QtCore import Qt, QThread, Signal, QTimer
from PySide6.QtGui import QMovie, QColor
from aivalanche_app.components.loading_spinner import loading_spinner

class DataFetcher(QThread):
    data_ready = Signal(str)

    def run(self):
        # Simulate fetching data from API (replace with actual API call)
        import time
        time.sleep(3)
        fetched_data = "Fetched data from API"
        self.data_ready.emit(fetched_data)

        
class LoadingDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Loading")
        # self.setWindowFlags(Qt.Dialog | Qt.WindowTitleHint)
        self.setModal(True)
        self.setLayout(QVBoxLayout())
        self.loading_label = QLabel("Loading...", self)
        self.loading_label.setAlignment(Qt.AlignCenter)
        self.layout().addWidget(self.loading_label)
        self.movie = QMovie(str(loading_spinner))  # Replace "spinner.gif" with your GIF file
        self.loading_label.setMovie(self.movie)
        self.movie.start()

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Loading Indicator Example")
        self.setGeometry(100, 100, 300, 200)

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.fetch_button = QPushButton("Fetch Data", self)
        self.fetch_button.clicked.connect(self.fetch_data)
        self.layout.addWidget(self.fetch_button)

        self.result_label = QLabel("", self)
        self.result_label.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.result_label)

    def fetch_data(self):
        # Show loading dialog
        loading_dialog = LoadingDialog(self)
        loading_dialog.exec_()  # Block until dialog is closed

        # Start data fetching in a separate thread
        data_fetcher = DataFetcher()
        data_fetcher.data_ready.connect(self.handle_data_ready)
        data_fetcher.start()

    def handle_data_ready(self, data):
        # Update UI with fetched data
        self.result_label.setText(data)


if __name__ == "__main__":
    if not QApplication.instance():
        app = QApplication(sys.argv)
    else:
        app = QApplication.instance()
    mainWindow = MainWindow()
    mainWindow.show()
    sys.exit(app.exec())
