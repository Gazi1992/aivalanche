# widgets/content_pages.py

from PyQt6.QtWidgets import QWidget, QLabel, QVBoxLayout
from PyQt6.QtCore import Qt

# Import specific page widgets
from .instrument_widgets import InstrumentsPage
from .chat_page import ChatPage

def create_content_page(text):
    """Creates a standard content page widget (used for History, Templates)."""
    page = QWidget()
    page.setObjectName("ContentPage")
    layout = QVBoxLayout(page)
    label = QLabel(text)
    label.setAlignment(Qt.AlignmentFlag.AlignCenter)
    layout.addWidget(label)
    layout.addStretch()
    page.setLayout(layout)
    return page

# --- Specific Page Creators ---

def create_instruments_page():
    """Creates the content widget for the Instruments tab."""
    return InstrumentsPage()

def create_chat_page():
    """Creates the content widget for the Chat tab."""
    return ChatPage()

def create_templates_page(): # New function
    """Creates the content widget for the Templates tab."""
    return create_content_page("Content for Templates Page")

def create_history_page():
    """Creates the content widget for the History tab."""
    return create_content_page("Content for History Page")
