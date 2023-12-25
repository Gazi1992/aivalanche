import sys
from PySide6.QtWidgets import QApplication
from aivalanche_app.screens.home import home

#TODO Make sure to close the app once the GUI closes.
# This problem appeared when migrated from PyQt6 to PySide6.
if not QApplication.instance():
    app = QApplication(sys.argv)
else:
    app = QApplication.instance()

window = home()    
window.show()
sys.exit(app.exec())
