from PySide6.QtWidgets import QMainWindow, QSplitter, QMessageBox
from aivalanche_app.components.main_tabs import main_tabs
from aivalanche_app.components.drawer import drawer
from aivalanche_app.data_store.store import store
from aivalanche_app.resources.themes.style import style


class home(QMainWindow):
    def __init__(self):
        super().__init__()
        
        self.initialize_store()
        
        self.style = style()
        
        self.setWindowTitle("aivalanche")
        
        # # Remove top bar        
        # self.setWindowFlags(self.windowFlags() | Qt.FramelessWindowHint)

        # Open the window in full-screen mode
        self.showMaximized()
        self.setStyleSheet(self.style.home)
        self.init_ui()
        

    def init_ui(self):        
        splitter = QSplitter()
        splitter.setHandleWidth(0)
        self.setCentralWidget(splitter)

        # Create the drawer on the left
        drawer_widget = drawer(parent = splitter, user = self.store.user, style = self.style)
        
        # Create a main tabs on the right
        self.tab_widget = main_tabs(parent = splitter, store = self.store, style = self.style)
        
        # Set stretch factors to ensure the drawer widget takes minimum space
        splitter.setStretchFactor(0, 0)
        splitter.setStretchFactor(1, 1)
        
        # Connect the drawer buttons to their respoctive actions
        drawer_widget.projects_active.connect(lambda: self.set_active_tab('projects'))
        drawer_widget.running_active.connect(lambda: self.set_active_tab('running'))
        drawer_widget.logout_active.connect(self.on_logout_press)
        
        # Set projects as active tab
        drawer_widget.set_projects_active()

        
    def set_active_tab(self, tab: str = None):
        self.tab_widget.set_active_tab(tab)
        
    
    def on_logout_press(self):
        self.close()
    
    
    def closeEvent(self, event):
        quit_msg = "Are you sure you want to exit the program?"
        reply = QMessageBox.question(self, 'Message', quit_msg, QMessageBox.Yes, QMessageBox.No)
    
        if reply == QMessageBox.Yes:
            event.accept()
        else:
            event.ignore()
            
    def initialize_store(self):
        self.store = store(user_id = 'asdsd-asdfr-123asd-asdas4-asdsda')