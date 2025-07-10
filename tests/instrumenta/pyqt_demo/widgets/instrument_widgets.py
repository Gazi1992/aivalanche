# widgets/instrument_widgets.py

import json
import os
import sys
from PyQt6.QtWidgets import (
    QWidget, QLabel, QVBoxLayout, QHBoxLayout, QLineEdit,
    QPushButton, QFrame, QScrollArea, QSizePolicy, QStyle, QSpacerItem # Added QSpacerItem
)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QFont, QPixmap # Keep QPixmap if needed by other parts or future icons

# --- Configuration ---
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
DEFAULT_CARD_WIDTH = 250
# IMAGE_WIDTH/HEIGHT based on card width, used for scaling icon
IMAGE_WIDTH = DEFAULT_CARD_WIDTH - 24 # Based on 12px padding left/right
IMAGE_HEIGHT = IMAGE_WIDTH // 2
DEFAULT_IMAGE_SIZE = QSize(IMAGE_WIDTH, IMAGE_HEIGHT) # Target size for pixmap display area
ICON_SIZE = QSize(64, 64) # Base size to request from standard icon (can be larger than display area)
DEFAULT_COLUMN_SPACING = 20 # Spacing between columns AND between headers
DEFAULT_COL_PAGE_MARGINS = 5 # Left/right margin for headers and columns

# --- Instrument Card Widget ---
class InstrumentCard(QFrame):
    """Displays details for a single instrument."""
    # Add category_name parameter
    def __init__(self, instrument_data, category_name="Unknown", parent=None):
        super().__init__(parent)
        self.setObjectName("InstrumentCard")
        self.setFrameShape(QFrame.Shape.StyledPanel)
        self.setFrameShadow(QFrame.Shadow.Plain)
        self.data = instrument_data
        self.category_name = category_name # Store category name

        # --- Main Layout (Vertical) ---
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(12, 12, 12, 12) # Padding inside the card frame
        self.main_layout.setSpacing(10) # Overall spacing between elements

        # --- Widgets ---
        self.name_label = QLabel(self.data.get("name", "N/A"))
        self.name_label.setObjectName("CardName")
        font = self.name_label.font(); font.setBold(True)
        self.name_label.setFont(font)
        self.name_label.setWordWrap(True)
        self.name_label.setProperty("font-weight", "bold")
        self.name_label.setAlignment(Qt.AlignmentFlag.AlignCenter) # Center the name
        self.name_label.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)

        self.image_label = QLabel()
        self.image_label.setObjectName("CardImage")
        self.image_label.setFixedSize(DEFAULT_IMAGE_SIZE) # Set fixed size for the display area
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        # Background color is handled by theme.py's #CardImage rule

        # Use Standard Icons
        icon = self._get_instrument_icon() # Get icon based on category
        if not icon.isNull():
            # Get pixmap from icon, scaled to fit display area while keeping aspect ratio
            pixmap = icon.pixmap(ICON_SIZE).scaled(DEFAULT_IMAGE_SIZE,
                                                   Qt.AspectRatioMode.KeepAspectRatio,
                                                   Qt.TransformationMode.SmoothTransformation)
            self.image_label.setPixmap(pixmap)
        else:
            # Fallback if no suitable icon is found
            self.image_label.setText("[ ? ]") # Simple text fallback
            self.image_label.setStyleSheet("color: gray; font-size: 20pt;")


        self.desc_label = QLabel(self.data.get("description", ""))
        self.desc_label.setObjectName("CardDescription")
        self.desc_label.setWordWrap(True) # Allow wrapping
        desc_font = self.desc_label.font()
        self.desc_label.setFont(desc_font)
        # Set vertical policy to Preferred, not Expanding
        self.desc_label.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
        # Set alignment AFTER setting text for it to take effect properly with wrap
        self.desc_label.setAlignment(Qt.AlignmentFlag.AlignCenter)


        # --- Bottom Row ---
        self.bottom_widget = QWidget()
        self.bottom_layout = QHBoxLayout(self.bottom_widget)
        self.bottom_layout.setContentsMargins(0, 8, 0, 0) # Top margin before status/button
        self.bottom_layout.setSpacing(8)

        self.status_label = QLabel()
        self.status_label.setObjectName("CardStatus")
        status_font = self.status_label.font()
        self.status_label.setFont(status_font)
        self.status_label.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)

        self.connect_button = QPushButton()
        self.connect_button.setObjectName("ConnectButton")
        self.connect_button.setMinimumHeight(30) # Slightly taller button
        self.connect_button.setSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Fixed) # Don't expand horizontally
        self.connect_button.clicked.connect(self._toggle_connection)

        self.bottom_layout.addWidget(self.status_label)
        self.bottom_layout.addStretch(1) # Push button to the right
        self.bottom_layout.addWidget(self.connect_button)

        # --- Add Widgets to Main Vertical Layout ---
        self.main_layout.addWidget(self.name_label)
        self.main_layout.addWidget(self.image_label, 0, Qt.AlignmentFlag.AlignCenter) # Center image horizontally
        self.main_layout.addWidget(self.desc_label)
        # Stretch pushes the bottom_widget down, allowing desc_label space
        self.main_layout.addStretch(1)
        self.main_layout.addWidget(self.bottom_widget)

        # Set initial state
        self._update_ui_state()
        self.setLayout(self.main_layout)
        # Use dynamic height, keep fixed width
        self.setFixedWidth(DEFAULT_CARD_WIDTH)


    def _get_instrument_icon(self):
        """Selects a standard icon based on category name."""
        style = self.style()
        cat_lower = self.category_name.lower()
        icon = QPixmap() # Start with an invalid icon

        if "spectro" in cat_lower:
            icon = style.standardIcon(QStyle.StandardPixmap.SP_FileDialogDetailedView)
        elif "power" in cat_lower:
            icon = style.standardIcon(QStyle.StandardPixmap.SP_ToolBarHorizontalExtensionButton)
        elif "camera" in cat_lower:
            icon = style.standardIcon(QStyle.StandardPixmap.SP_ComputerIcon)
        elif "stage" in cat_lower or "actuator" in cat_lower:
            icon = style.standardIcon(QStyle.StandardPixmap.SP_ArrowRight)
        elif "scope" in cat_lower:
             icon = style.standardIcon(QStyle.StandardPixmap.SP_FileDialogInfoView)
        else:
            icon = style.standardIcon(QStyle.StandardPixmap.SP_DriveHDIcon)

        if icon.isNull():
             print(f"Warning: Could not find standard icon for category '{self.category_name}'. Using final fallback.")
             icon = style.standardIcon(QStyle.StandardPixmap.SP_MessageBoxQuestion)

        return icon

    def _update_ui_state(self):
        """Updates the status label and button based on self.data['connected']"""
        connected = self.data.get("connected", False)
        if connected:
            self.status_label.setText("● Connected")
            self.status_label.setProperty("connectionStatus", "connected") # For QSS
            self.connect_button.setText("Disconnect")
            self.connect_button.setToolTip("Click to disconnect this instrument")
        else:
            self.status_label.setText("○ Disconnected")
            self.status_label.setProperty("connectionStatus", "disconnected") # For QSS
            self.connect_button.setText("Connect")
            self.connect_button.setToolTip("Click to connect this instrument")
        # Re-apply stylesheet properties for the status label
        self.status_label.style().unpolish(self.status_label); self.status_label.style().polish(self.status_label)


    def _toggle_connection(self):
        """Handles the button click: toggles state and updates UI."""
        current_state = self.data.get("connected", False); new_state = not current_state
        self.data["connected"] = new_state # Update the internal data state
        print(f"Toggling connection for '{self.data.get('name')}': {current_state} -> {new_state}")
        self._update_ui_state() # Update the UI elements


# --- Instrument Column Widget (Formerly CategoryColumn) ---
class InstrumentColumnWidget(QWidget):
    """A widget holding a vertical list of InstrumentCards for one category."""
    def __init__(self, category_data, category_name, parent=None):
        super().__init__(parent)
        self.setObjectName("InstrumentColumnWidget")
        self.data = category_data
        self.category_name = category_name
        self.instrument_widgets = {}

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0) # No internal margins for the column itself
        layout.setSpacing(10) # Spacing between cards (matches card margin-bottom)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        # --- Cards ---
        instruments = self.data.get("instruments", [])
        if instruments:
            for instrument_data in instruments:
                # Pass category_name for icon selection
                card = InstrumentCard(instrument_data, category_name=self.category_name)
                layout.addWidget(card)
                self.instrument_widgets[instrument_data.get("name")] = card
        else:
            # Fallback label if created despite being empty
            no_instruments_label = QLabel("No instruments.")
            no_instruments_label.setObjectName("EmptyColumnLabel")
            layout.addWidget(no_instruments_label)

        # Add stretch to push cards up if the column is taller than content
        layout.addStretch(1)

        self.setLayout(layout)
        # --- Set Fixed Width (Crucial for alignment with header) ---
        self.setFixedWidth(DEFAULT_CARD_WIDTH + 10) # Use same calculation as header label
        self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Preferred)


# --- Instruments Page Widget ---
class InstrumentsPage(QWidget):
    """The main widget for the Instruments tab with sticky headers."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("InstrumentsPage")

        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(15, 15, 15, 15) # Overall page padding
        self.main_layout.setSpacing(10) # Reduced spacing between sections

        # 1. Search Header Section
        self.search_header_widget = self._create_header()
        self.main_layout.addWidget(self.search_header_widget)

        # --- 2. Sticky Category Header Row ---
        self.category_header_container = QWidget()
        self.category_header_container.setObjectName("CategoryHeaderContainer")
        self.category_header_layout = QHBoxLayout(self.category_header_container)
        self.category_header_layout.setContentsMargins(DEFAULT_COL_PAGE_MARGINS, 5, DEFAULT_COL_PAGE_MARGINS, 5)
        self.category_header_layout.setSpacing(DEFAULT_COLUMN_SPACING) # Match column spacing
        self.category_header_layout.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        self.category_header_container.setLayout(self.category_header_layout)
        self.category_header_container.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Maximum)
        self.main_layout.addWidget(self.category_header_container) # Add before scroll area


        # --- 3. Instrument Display Area (Scrollable Content ONLY) ---
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.scroll_area.setObjectName("InstrumentScrollArea")
        self.scroll_area.setFrameShape(QFrame.Shape.NoFrame)

        # Container widget for the instrument columns inside the scroll area
        self.scroll_content_widget = QWidget()
        self.scroll_content_widget.setObjectName("ScrollContentContainer")
        # This layout holds InstrumentColumnWidget instances
        self.columns_layout = QHBoxLayout(self.scroll_content_widget)
        self.columns_layout.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
        self.columns_layout.setSpacing(DEFAULT_COLUMN_SPACING) # Match header spacing
        self.columns_layout.setContentsMargins(DEFAULT_COL_PAGE_MARGINS, 0, DEFAULT_COL_PAGE_MARGINS, DEFAULT_COL_PAGE_MARGINS) # Match header margins (except top)
        self.scroll_content_widget.setLayout(self.columns_layout)

        self.scroll_area.setWidget(self.scroll_content_widget)
        # Add scroll area to main layout *after* the category header
        self.main_layout.addWidget(self.scroll_area)


        # 4. Load data and populate both header and content
        self._load_and_display_instruments()

        self.setLayout(self.main_layout)

    # --- _create_header method ---
    def _create_header(self):
        header_widget = QWidget()
        header_layout = QHBoxLayout(header_widget)
        header_layout.setContentsMargins(0, 0, 0, 0)
        header_layout.setSpacing(10)
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search instruments...")
        self.search_input.setObjectName("SearchInput")
        self.search_input.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.discover_button = QPushButton("Discover Instruments")
        self.discover_button.setObjectName("DiscoverButton")
        self.discover_button.setSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Fixed)
        header_layout.addWidget(self.search_input)
        header_layout.addWidget(self.discover_button)
        header_widget.setLayout(header_layout)
        return header_widget

    # --- _load_and_display_instruments method ---
    def _load_and_display_instruments(self):
        """Loads data and populates category headers and instrument columns separately."""
        # --- Clear previous headers and columns ---
        while self.category_header_layout.count() > 0:
            item = self.category_header_layout.takeAt(0)
            if item:
                widget = item.widget()
                if widget and isinstance(widget, QWidget): widget.deleteLater()
                elif isinstance(item, QSpacerItem): pass # Handle stretch
        while self.columns_layout.count() > 0:
            item = self.columns_layout.takeAt(0)
            if item:
                widget = item.widget()
                if widget and isinstance(widget, QWidget): widget.deleteLater()
                elif isinstance(item, QSpacerItem): pass # Handle stretch

        data_file = os.path.join(CURRENT_DIR, '..', "dummy_data.json")
        categories = []
        absolute_data_file_path = os.path.abspath(data_file)
        found_valid_category = False

        # --- Load Data ---
        if not os.path.exists(absolute_data_file_path):
            error_text = f"Error: Cannot find '{os.path.basename(data_file)}'."
            print(f"Error: Data file not found at '{absolute_data_file_path}'", file=sys.stderr)
            self.category_header_layout.addWidget(QLabel(error_text))
            self.columns_layout.addWidget(QLabel(" ")) # Add empty label to keep structure
            return
        else:
            try:
                with open(absolute_data_file_path, 'r', encoding='utf-8') as f:
                    loaded_data = json.load(f)
                if isinstance(loaded_data, list): categories = loaded_data
                else: raise TypeError("JSON data is not a list")
            except Exception as e:
                 error_text = f"Error loading data from '{os.path.basename(data_file)}'."
                 print(f"Error loading/parsing '{absolute_data_file_path}': {e}", file=sys.stderr)
                 self.category_header_layout.addWidget(QLabel(error_text))
                 self.columns_layout.addWidget(QLabel(" "))
                 return

        # --- Populate Headers and Columns ---
        if categories:
            for category_data in categories:
                 if isinstance(category_data, dict):
                    category_name = category_data.get("name", "Unknown")
                    instruments = category_data.get("instruments", [])

                    # Only add if category is NOT empty
                    if instruments:
                        found_valid_category = True
                        # Add Title to Header Row
                        title_label = QLabel(category_name)
                        title_label.setObjectName("CategoryHeaderLabel") # New object name for title
                        title_label.setToolTip(category_data.get("description", ""))
                        # Set fixed width to match the column width
                        title_label.setFixedWidth(DEFAULT_CARD_WIDTH + 10)
                        title_label.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Preferred) # Fixed width
                        self.category_header_layout.addWidget(title_label)

                        # Add Instrument Column (cards only) to Scroll Area Content
                        column_widget = InstrumentColumnWidget(category_data, category_name)
                        self.columns_layout.addWidget(column_widget)
                 else:
                    print(f"Warning: Skipping invalid category entry: {category_data}", file=sys.stderr)

        # Add stretch to push headers/columns left if content doesn't fill width
        if found_valid_category:
            self.category_header_layout.addStretch(1)
            self.columns_layout.addStretch(1)
        else:
             if self.category_header_layout.count() == 0:
                 no_data_label = QLabel("No instrument categories found.")
                 no_data_label.setObjectName("EmptyCategoryLabel")
                 self.category_header_layout.addWidget(no_data_label)

    # --- filter_instruments and run_discovery ---
    def filter_instruments(self, text):
        print(f"Search: {text}")

    def run_discovery(self):
        print("Discover clicked")
