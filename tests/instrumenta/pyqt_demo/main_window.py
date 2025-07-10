# main_window.py

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QStackedWidget,
    QDockWidget, QListWidget, QListWidgetItem, QLabel, QFrame, QStyle,
    QSizePolicy # Added QSizePolicy
)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QPixmap

# Import the page creation functions
from widgets.content_pages import (
    create_instruments_page, create_chat_page, create_history_page,
    create_templates_page
)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("PyQt Demo with Instrumenta")
        self.setGeometry(100, 100, 900, 700)

        self.stacked_widget = QStackedWidget()
        self.setCentralWidget(self.stacked_widget)

        # --- Navigation Bar (Dock Widget) ---
        self.nav_dock = QDockWidget(self)
        self.nav_dock.setTitleBarWidget(QWidget()) # Hide title bar
        self.nav_dock.setAllowedAreas(Qt.DockWidgetArea.LeftDockWidgetArea | Qt.DockWidgetArea.RightDockWidgetArea)

        self.nav_widget = QWidget()
        self.nav_widget.setObjectName("NavBarContainer")
        self.nav_layout = QVBoxLayout(self.nav_widget)
        # Increased top/bottom margins for header prominence
        self.nav_layout.setContentsMargins(5, 15, 5, 10)
        self.nav_layout.setSpacing(10) # Increased spacing

        # --- LOGO/HEADER SECTION (Vertical Layout) ---
        self.logo_header_widget = QWidget()
        # *** Use QVBoxLayout, Center horizontally ***
        self.logo_header_layout = QVBoxLayout(self.logo_header_widget)
        self.logo_header_layout.setContentsMargins(5, 0, 5, 0) # Reduced internal margins
        self.logo_header_layout.setSpacing(5) # Reduced spacing between icon/text
        self.logo_header_layout.setAlignment(Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop) # Center horizontally

        # Logo Icon (Top)
        self.logo_icon_label = QLabel()
        self.logo_icon_label.setObjectName("NavHeaderIcon")
        icon = self.style().standardIcon(QStyle.StandardPixmap.SP_ComputerIcon)
        if not icon.isNull():
            # *** Slightly larger icon ***
            pixmap = icon.pixmap(QSize(36, 36))
            self.logo_icon_label.setPixmap(pixmap)
        else:
            self.logo_icon_label.setText("?")
        # Allow icon label to center within layout
        self.logo_icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        # Fixed size might not be needed if layout handles centering well
        # self.logo_icon_label.setFixedSize(QSize(40, 40))

        # Logo Text (Bottom)
        self.logo_text_label = QLabel("instrumenta")
        self.logo_text_label.setObjectName("NavHeaderText")
        # *** Center text explicitly ***
        self.logo_text_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # *** Add icon first, then text ***
        self.logo_header_layout.addWidget(self.logo_icon_label)
        self.logo_header_layout.addWidget(self.logo_text_label)
        self.logo_header_widget.setLayout(self.logo_header_layout)
        # Allow header to take preferred size
        self.logo_header_widget.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Maximum)


        # Separator Line
        separator = QFrame()
        separator.setObjectName("NavSeparator")
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setFrameShadow(QFrame.Shadow.Sunken)

        # Add Header and Separator to the main nav layout
        self.nav_layout.addWidget(self.logo_header_widget)
        self.nav_layout.addWidget(separator)
        # *** END HEADER SECTION ***

        # Navigation List (add AFTER header/separator)
        self.nav_list = QListWidget()
        self.nav_list.setObjectName("NavList")
        self.nav_list.currentRowChanged.connect(self.change_page)
        # Add stretch *before* list to push header/separator up if space allows
        # self.nav_layout.addStretch(1) # Optional: pushes nav items down
        self.nav_layout.addWidget(self.nav_list)
        # Add stretch *after* list to push nav items up
        self.nav_layout.addStretch(1)


        self.nav_dock.setWidget(self.nav_widget)
        self.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, self.nav_dock)

        # --- Add Navigation Items and Content Pages ---
        self.pages_info = []
        self.add_nav_item("Instruments", create_instruments_page())
        self.add_nav_item("Chat", create_chat_page())
        self.add_nav_item("Templates", create_templates_page())
        self.add_nav_item("History", create_history_page())

        if self.nav_list.count() > 0:
            self.nav_list.setCurrentRow(0)

    def add_nav_item(self, name, widget):
        # ... (no change) ...
        list_item = QListWidgetItem(name)
        self.nav_list.addItem(list_item)
        index = self.stacked_widget.addWidget(widget)
        self.pages_info.append({"name": name, "widget": widget, "index": index})

    def change_page(self, current_row):
        # ... (no change) ...
        if 0 <= current_row < self.stacked_widget.count():
            self.stacked_widget.setCurrentIndex(current_row)
