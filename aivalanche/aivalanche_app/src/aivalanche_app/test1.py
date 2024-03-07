import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QSplitter, QTabWidget, QPushButton, QWidget, QProxyStyle, QStyle
from PySide6.QtGui import QPainter, QColor, QPalette
from PySide6.QtCore import Qt

# Custom Style class
class CustomStyle(QProxyStyle):
    def drawControl(self, element, option, painter, widget=None):
        print(element)
        if element == QProxyStyle.CE_TabBarTabLabel:
            print(widget.parent().objectName())
            # Set the background of the QTabWidget to transparent
            painter.save()
            painter.setBrush(QColor(Qt.green))
            painter.drawRect(option.rect)
            painter.restore()  
            option.palette.setColor(QPalette.WindowText, QColor(0, 0, 255, 255))
            super().drawControl(element, option, painter, widget)
        elif element == QProxyStyle.CE_PushButtonLabel:
            # Customize the button appearance when pressed or hovered
            if option.state & QStyle.State_Sunken:
                painter.fillRect(option.rect, QColor(Qt.green))
            elif option.state & QStyle.State_MouseOver:
                painter.fillRect(option.rect, QColor(Qt.red))
            super().drawControl(element, option, painter, widget)
        elif element == QProxyStyle.CE_ShapedFrame:
            if widget.parent().objectName() == 'kot':
                painter.save()
                painter.setBrush(QColor(255, 0, 0, 0))
                painter.drawRect(option.rect)
                painter.restore()
            # option.palette.setColor(QPalette.Window, QColor(255, 0, 0, 255))
        else:
            super().drawControl(element, option, painter, widget)
        
    def drawPrimitive(self, element, option, painter, widget=None):
        print(element)
        if element == QProxyStyle.PE_FrameTabWidget:
            # Set the background of the QTabWidget to transparent
            # option.palette.setColor(QPalette.WindowText, QColor(255, 0, 0, 255))
            # option.palette.setColor(QPalette.Window, QColor(255, 255, 0, 255))
            # painter.save()
            # painter.setBrush(QColor(Qt.green))
            # painter.drawRect(option.rect)
            # painter.restore()
            return
        else:
            super().drawPrimitive(element, option, painter, widget)

# main_tabs widget
class main_tabs(QTabWidget):
    def __init__(self, parent = None):
        super().__init__(parent)
        self.setContentsMargins(0, 0, 0, 0)


# home widget
class home(QMainWindow):
    def __init__(self):
        super().__init__()
        self.showMaximized()
        self.init_ui()

        
    def init_ui(self):        
        splitter = QSplitter(parent = self)
        self.setCentralWidget(splitter)
        
        # Create a main tabs on the right
        self.tab_widget = main_tabs(parent = splitter)
        # self.tab_widget.setDocumentMode(True)
        self.tab_widget.setObjectName('kot')
        self.tab_widget.addTab(QWidget(), 'tab 1')
        self.tab_widget.addTab(QWidget(), 'tab 2')
        self.tab_widget.setMinimumHeight(500)
        self.button = QPushButton(text = 'press me', parent = splitter)
        
        # Set stretch factors to ensure the drawer widget takes minimum space
        splitter.setStretchFactor(0, 1)  
        splitter.setStretchFactor(1, 1)  
            

if not QApplication.instance():
    app = QApplication(sys.argv)
else:
    app = QApplication.instance()
    
# Example style sheet
style_sheet = """
    QMainWindow {
        background-color: rgba(255, 0, 0, 255); /* Set background color */
    }
    
    QTabWidget#kot {
        background-color: rgba(255, 255, 0, 100); /* Set background color */
    }
    
    QPushButton {
        background-color: rgba(255, 255, 0, 255); /* Green background color */
        color: white; /* White text color */
        border: none; /* No border */
        padding: 10px 20px; /* Padding */
        text-align: center; /* Center text */
        text-decoration: none;
        font-size: 16px; /* Font size */
    }
    
    QPushButton:hover {
        background-color: #45a049; /* Darker green on hover */
    }
"""

# Apply the style sheet to the application
# app.setStyleSheet(style_sheet)
app.setStyle(CustomStyle())

window = home()    
window.show()
sys.exit(app.exec())