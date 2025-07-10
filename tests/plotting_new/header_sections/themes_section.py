# header_sections/themes_section.py
import logging
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QRadioButton, QButtonGroup, QLabel, QFrame
from PyQt6.QtCore import pyqtSignal, Qt
from PyQt6.QtGui import QColor
import themes # To get AVAILABLE_THEMES

logger = logging.getLogger(__name__)

class ThemesSectionWidget(QWidget):
    theme_selected = pyqtSignal(str)  # Emits theme_key

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        self.setObjectName("ThemesSectionWidget")

        # Switch to a vertical list layout for sidebar
        self.radio_layout = QVBoxLayout(self)
        self.radio_layout.setContentsMargins(0, 0, 0, 0)
        self.radio_layout.setSpacing(8)
        self.radio_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        self.radio_button_group = QButtonGroup(self)
        self.radio_button_group.setExclusive(True)
        self.radio_button_group.idClicked.connect(self._on_radio_button_clicked)

        self.theme_radios = {}

        # Section title labels
        self.light_theme_label = QLabel("Light Themes")
        self.light_theme_label.setObjectName("LightThemeLabel")
        self.dark_theme_label = QLabel("Dark Themes")
        self.dark_theme_label.setObjectName("DarkThemeLabel")

        self.radio_layout.addWidget(self.light_theme_label)

        # Separate themes into light and dark lists
        light_themes = []
        dark_themes = []
        for key, theme_dict in themes.AVAILABLE_THEMES.items():
            if theme_dict.get('is_dark', False):
                dark_themes.append((key, theme_dict))
            else:
                light_themes.append((key, theme_dict))
        
        button_id_counter = 0

        # Populate Light Themes list
        for (key, theme_dict) in light_themes:
            radio_button = self._create_radio_button(key, theme_dict, button_id_counter)
            self.radio_layout.addWidget(radio_button)
            button_id_counter += 1

        # Separator line between light and dark
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setFrameShadow(QFrame.Shadow.Sunken)
        self.radio_layout.addWidget(separator)

        self.radio_layout.addWidget(self.dark_theme_label)

        # Populate Dark Themes list
        for (key, theme_dict) in dark_themes:
            radio_button = self._create_radio_button(key, theme_dict, button_id_counter)
            self.radio_layout.addWidget(radio_button)
            button_id_counter += 1

    def _create_radio_button(self, key, theme_dict, button_id):
        display_name = theme_dict.get('name', key.capitalize())
        radio_button = QRadioButton(display_name)
        radio_button.setObjectName(f"ThemeRadioButton_{key}")
        self.radio_button_group.addButton(radio_button, button_id)
        self.theme_radios[button_id] = key
        return radio_button

    def _on_radio_button_clicked(self, button_id: int):
        theme_key = self.theme_radios.get(button_id)
        if theme_key:
            self.theme_selected.emit(theme_key)
        else:
            logger.warning(f"Clicked radio button with unmapped id: {button_id}")

    def set_current_theme(self, theme_key: str):
        self.radio_button_group.blockSignals(True)
        found_button = False
        for idx, key in self.theme_radios.items():
            if key == theme_key:
                button = self.radio_button_group.button(idx)
                if button:
                    button.setChecked(True)
                    found_button = True
                break
        if not found_button:
            logger.warning(f"Could not find radio button for theme key '{theme_key}' to set current.")
        self.radio_button_group.blockSignals(False)
