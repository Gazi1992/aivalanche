from PySide6.QtWidgets import QMainWindow, QMessageBox, QStackedWidget
from aivalanche_app.screens.home import home
from aivalanche_app.screens.log_in import log_in
from aivalanche_app.data_store.store import store


class main_window(QMainWindow):
    def __init__(self, store: store = None):
        super().__init__()
        self.store = store
        self.setWindowTitle("aivalanche")
        # self.setWindowFlags(self.windowFlags() | Qt.FramelessWindowHint)
        self.showMaximized()
        self.init_ui()
        self.setObjectName('main_window')
        

    def init_ui(self):        
        # Create the stacked widget
        self.stacked_widget = QStackedWidget(parent = self)
        self.setCentralWidget(self.stacked_widget)
        
        # Create log_in screen
        self.log_in_screen = log_in(parent = self.stacked_widget, store = self.store, object_name = 'log_in')
        self.log_in_screen.go_to_home.connect(self.go_to_home)
        self.log_in_screen.update_store.connect(self.update_store)
        self.stacked_widget.addWidget(self.log_in_screen)
        
        # Create home screen
        self.home_screen = home(parent = self.stacked_widget, store = self.store, object_name = 'home')
        self.home_screen.go_to_log_in.connect(self.go_to_log_in)
        self.stacked_widget.addWidget(self.home_screen)
        
        self.stacked_widget.setCurrentWidget(self.log_in_screen)


    def closeEvent(self, event):
        quit_msg = "Are you sure you want to exit the program?"
        reply = QMessageBox.question(self, 'Message', quit_msg, QMessageBox.Yes, QMessageBox.No)
    
        if reply == QMessageBox.Yes:
            event.accept()
        else:
            event.ignore()
            
    def go_to_home(self):
        self.stacked_widget.setCurrentWidget(self.home_screen)
        self.home_screen.fetch_projects()

    def go_to_log_in(self):
        self.stacked_widget.setCurrentWidget(self.log_in_screen)
        
    def update_store(self, data = dict):
        self.store.update(data)
        self.home_screen.print_user()
