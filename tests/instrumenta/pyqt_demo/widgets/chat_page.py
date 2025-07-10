# widgets/chat_page.py

import json
import os
import sys
from PyQt6.QtWidgets import (
    QWidget, QLabel, QVBoxLayout, QHBoxLayout, QTextEdit,
    QPushButton, QFrame, QSizePolicy, QStyle, QSpacerItem # Removed QScrollArea, Added QSpacerItem
)
from PyQt6.QtCore import Qt, pyqtSignal, QEvent, QSize
from PyQt6.QtGui import QFont, QPixmap, QPainter, QColor, QPen # Ensure all needed QtGui classes are imported

# --- Configuration for Compact Bar ---
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
COMPACT_ICON_SIZE = QSize(14, 14) # Size for the small status icon
COMPACT_CATEGORY_WIDTH = 160 # Fixed width for each category column

# --- Helper to get status pixmap ---
def get_status_pixmap(connected: bool, size: QSize) -> QPixmap:
    """Creates a simple circle pixmap for status."""
    pixmap = QPixmap(size)
    pixmap.fill(Qt.GlobalColor.transparent) # Transparent background
    painter = QPainter(pixmap)
    try:
        painter.setRenderHint(QPainter.RenderHint.Antialiasing) # Smooth circle
        # Use specific colors for connected/disconnected
        color = QColor("#28A745") if connected else QColor("#DC3545") # Green/Red
        painter.setBrush(color)
        painter.setPen(Qt.PenStyle.NoPen) # No border
        # Calculate radius as float
        radius_float = (min(size.width(), size.height()) / 2) * 0.8
        # Cast radius to int before drawing
        radius_int = int(radius_float)
        center = pixmap.rect().center()
        # Draw using integer radii
        painter.drawEllipse(center, radius_int, radius_int)
    finally:
        painter.end() # Important to release resources
    return pixmap

# --- Compact Instrument Widget ---
class CompactInstrumentWidget(QWidget):
    """Displays a single instrument compactly with status icon and name."""
    def __init__(self, instrument_data, parent=None):
        super().__init__(parent)
        self.data = instrument_data
        self.setObjectName("CompactInstrumentWidget")

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 2, 0, 2) # Minimal vertical padding
        layout.setSpacing(4)

        # Status Icon
        self.status_icon_label = QLabel()
        self.status_icon_label.setObjectName("CompactStatusIcon")
        self.status_icon_label.setFixedSize(COMPACT_ICON_SIZE)

        # Name Label
        self.name_label = QLabel(self.data.get("name", "N/A"))
        self.name_label.setObjectName("CompactInstrumentName")
        self.name_label.setToolTip(self.data.get("description", "")) # Show full desc on hover
        self.name_label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)

        layout.addWidget(self.status_icon_label)
        layout.addWidget(self.name_label)

        self.update_status(self.data.get("connected", False))

    def update_status(self, connected: bool):
        """Updates the status icon."""
        self.data["connected"] = connected # Update internal data
        pixmap = get_status_pixmap(connected, COMPACT_ICON_SIZE)
        self.status_icon_label.setPixmap(pixmap)
        # Set property for potential QSS styling (though pixmap handles color now)
        self.setProperty("status", "connected" if connected else "disconnected")

# --- Compact Category Widget ---
class CompactCategoryWidget(QWidget):
    """Displays a category title and a list of compact instrument widgets."""
    def __init__(self, category_data, parent=None):
        super().__init__(parent)
        self.data = category_data
        self.instrument_widgets = {} # Store instrument widgets if needed later
        self.setObjectName("CompactCategoryWidget")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(3)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop) # Align instruments to top

        # Category Title
        title_label = QLabel(self.data.get("name", "Unknown"))
        title_label.setObjectName("CompactCategoryTitle")
        title_label.setToolTip(self.data.get("description", ""))
        layout.addWidget(title_label)

        # Separator
        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setFrameShadow(QFrame.Shadow.Sunken)
        line.setObjectName("CompactCategorySeparator")
        layout.addWidget(line)

        # Instruments
        instruments = self.data.get("instruments", [])
        # Note: We assume this widget is only created if instruments exist (checked in ChatPage)
        if instruments:
            for instrument_data in instruments:
                inst_widget = CompactInstrumentWidget(instrument_data)
                layout.addWidget(inst_widget)
                self.instrument_widgets[instrument_data.get("name")] = inst_widget
        # We removed the "None" label here because the parent checks for emptiness now

        self.setFixedWidth(COMPACT_CATEGORY_WIDTH) # Fix the width of the column

# --- Main Chat Page Widget ---
class ChatTextEdit(QTextEdit):
    """A QTextEdit that emits a signal when Enter is pressed (without Shift)."""
    enterPressed = pyqtSignal()

    def keyPressEvent(self, event):
        if event.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter) and not (event.modifiers() & Qt.KeyboardModifier.ShiftModifier):
            self.enterPressed.emit()
            event.accept() # Consume the event, don't insert newline
            return
        # Call base class implementation for other keys or Shift+Enter
        super().keyPressEvent(event)

class ChatPage(QWidget):
    """The main widget for the Chat tab interface."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("ChatPage")

        # --- Main Layout ---
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setSpacing(15) # Space between top bar, title, input

        # --- 1. Top Bar Container (Title + Instruments) ---
        self.top_bar_container = QWidget() # Use simple QWidget, styling via QSS
        self.top_bar_container.setObjectName("ChatTopBarContainer")
        self.top_bar_layout = QVBoxLayout(self.top_bar_container) # Vertical layout for title + instruments HBox
        self.top_bar_layout.setContentsMargins(8, 8, 8, 8) # Padding for the whole top bar
        self.top_bar_layout.setSpacing(6) # Space between title and instruments row

        # Top Bar Title
        self.top_bar_title_label = QLabel("Available Instruments")
        self.top_bar_title_label.setObjectName("ChatTopBarTitle")
        # Style via QSS

        # Instrument Categories Container (Horizontal Layout)
        self.instrument_bar_widget = QWidget()
        self.instrument_bar_widget.setObjectName("InstrumentBarContent") # For specific styling if needed
        self.instrument_bar_layout = QHBoxLayout(self.instrument_bar_widget)
        self.instrument_bar_layout.setContentsMargins(0, 0, 0, 0) # No internal margins needed
        self.instrument_bar_layout.setSpacing(10) # Spacing between category columns
        self.instrument_bar_layout.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
        # Note: This layout will NOT wrap horizontally

        # Add Title and Instrument Bar row to Top Bar Container
        self.top_bar_layout.addWidget(self.top_bar_title_label)
        self.top_bar_layout.addWidget(self.instrument_bar_widget)
        self.top_bar_container.setLayout(self.top_bar_layout)
        # Let the container determine its height automatically
        self.top_bar_container.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Maximum)


        # --- 2. Main Chat Title/Greeting ---
        self.title_label = QLabel("✨ I am your instrumenta assistant") # Added sparkle emoji
        self.title_label.setObjectName("ChatTitleLabel")
        title_font = self.title_label.font()
        title_font.setPointSize(title_font.pointSize() + 6)
        self.title_label.setFont(title_font)
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # --- 3. Input Area Container ---
        self.input_container = QFrame()
        self.input_container.setObjectName("ChatInputContainer")
        self.input_container.setFrameShape(QFrame.Shape.StyledPanel) # Allows border-radius etc.

        self.input_layout = QHBoxLayout(self.input_container)
        self.input_layout.setContentsMargins(5, 5, 5, 5) # Internal padding
        self.input_layout.setSpacing(5)

        # Text Input using custom class
        self.text_input = ChatTextEdit()
        self.text_input.setObjectName("ChatInputArea")
        self.text_input.setPlaceholderText("How can I help you today?")
        self.text_input.setFixedHeight(80) # Start with a fixed height
        self.text_input.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed) # Expand horizontally
        self.text_input.enterPressed.connect(self._send_message) # Connect custom signal

        # Send Button
        self.send_button = QPushButton()
        self.send_button.setObjectName("ChatSendButton")
        icon = self.style().standardIcon(QStyle.StandardPixmap.SP_ArrowUp)
        self.send_button.setIcon(icon)
        self.send_button.setFixedSize(36, 36) # Square-ish button
        self.send_button.setToolTip("Send message (Enter)")
        self.send_button.clicked.connect(self._send_message)

        # Add input and button to their layout
        self.input_layout.addWidget(self.text_input)
        self.input_layout.addWidget(self.send_button, 0, Qt.AlignmentFlag.AlignBottom) # Align button bottom
        self.input_container.setLayout(self.input_layout)
        self.input_container.setMaximumWidth(600) # Limit width


        # --- Add widgets to main page layout ---
        self.main_layout.addWidget(self.top_bar_container) # Add the container for the top bar first
        self.main_layout.addStretch(1) # Push title/input down slightly
        self.main_layout.addWidget(self.title_label, 0, Qt.AlignmentFlag.AlignCenter)
        self.main_layout.addWidget(self.input_container, 0, Qt.AlignmentFlag.AlignCenter)
        self.main_layout.addStretch(2) # More stretch below input keeps it below center

        self.setLayout(self.main_layout)

        # --- Load Instrument Data for the Top Bar ---
        self._load_and_display_instruments()


    def _load_and_display_instruments(self):
        """Loads data from JSON and populates the compact instrument bar, skipping empty categories."""
        # Clear previous widgets first
        while self.instrument_bar_layout.count() > 0:
            item = self.instrument_bar_layout.takeAt(0)
            if item is not None:
                widget = item.widget()
                if widget is not None and isinstance(widget, QWidget):
                    widget.deleteLater()
                elif isinstance(item, QSpacerItem):
                    # QBoxLayout::takeAt also removes spacers, no explicit removal needed
                    pass

        data_file = os.path.join(CURRENT_DIR, '..', "dummy_data.json")
        categories = []
        absolute_data_file_path = os.path.abspath(data_file)
        found_valid_category = False # Flag to track if we added any category

        if not os.path.exists(absolute_data_file_path):
            print(f"Error: Data file not found for chat instrument bar: '{absolute_data_file_path}'", file=sys.stderr)
            error_label = QLabel("Error loading instruments")
            self.instrument_bar_layout.addWidget(error_label)
            return

        try:
            with open(absolute_data_file_path, 'r', encoding='utf-8') as f: # Specify UTF-8 encoding
                loaded_data = json.load(f)
                if isinstance(loaded_data, list):
                    categories = loaded_data
                else:
                    print(f"Error: Expected list in '{data_file}', got {type(loaded_data)}.", file=sys.stderr)
        except Exception as e:
            print(f"Error loading/parsing '{absolute_data_file_path}' for chat bar: {e}", file=sys.stderr)
            # Optionally display an error message in the bar
            error_label = QLabel("Error parsing instrument data")
            self.instrument_bar_layout.addWidget(error_label)


        # Populate bar
        if categories:
            for category_data in categories:
                if isinstance(category_data, dict):
                    # Check if the category has instruments
                    instruments = category_data.get("instruments", [])
                    if instruments: # Only create widget if instruments list is not empty
                        cat_widget = CompactCategoryWidget(category_data)
                        self.instrument_bar_layout.addWidget(cat_widget)
                        found_valid_category = True # Mark that we found at least one
                else:
                    print(f"Warning (Chat Bar): Skipping invalid category entry: {category_data}", file=sys.stderr)

            # Only add stretch if we added categories to push them left
            if found_valid_category:
                self.instrument_bar_layout.addStretch(1)

        # Show "No instruments found" only if no error occurred AND no valid categories were found
        if not found_valid_category and self.instrument_bar_layout.count() == 0 :
             no_data_label = QLabel("No available instruments found.")
             no_data_label.setObjectName("CompactEmptyLabel")
             self.instrument_bar_layout.addWidget(no_data_label)
             # Add stretch after this label too if you want it pushed left
             self.instrument_bar_layout.addStretch(1)


    def _send_message(self):
        """Placeholder slot for handling message sending."""
        message = self.text_input.toPlainText().strip()
        if message:
            print(f"Sending message: {message}")
            self.text_input.clear() # Clear input after sending
        else:
            print("Cannot send empty message.")

    def eventFilter(self, obj, event):
        # Optional: Handle events like focus on text input
        return super().eventFilter(obj, event)
