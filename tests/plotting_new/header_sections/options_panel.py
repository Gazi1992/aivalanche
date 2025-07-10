import logging
from typing import Optional, Dict, Any

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QTabWidget
from PyQt6.QtCore import QTimer, QPoint, Qt
from PyQt6.QtGui import QCursor

from .themes_section import ThemesSectionWidget
from .appearance_section import AppearanceSectionWidget
from .export_section import ExportSectionWidget


logger = logging.getLogger(__name__)

class OptionsPanel(QWidget):
    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        self.setObjectName("OptionsPanel")
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.NoDropShadowWindowHint | Qt.WindowType.Window)
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)

        self.current_theme_props: Dict[str, Any] = {}
        self.active_button_name: Optional[str] = None

        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(10, 10, 10, 10)
        self.main_layout.setSpacing(0)

        self.tab_widget = QTabWidget()
        self.tab_widget.setObjectName("OptionsTabWidget")
        self.tab_widget.tabBar().hide()
        self.main_layout.addWidget(self.tab_widget)

        self.themes_section = ThemesSectionWidget()
        self.tab_widget.addTab(self.themes_section, "Themes")

        self.appearance_section = AppearanceSectionWidget()
        self.tab_widget.addTab(self.appearance_section, "Appearance")

        self.export_section = ExportSectionWidget()
        self.tab_widget.addTab(self.export_section, "Export")
        
        self.setMouseTracking(True)
        self.hide_options_timer = QTimer(self)
        self.hide_options_timer.setInterval(1000)
        self.hide_options_timer.setSingleShot(True)
        self.hide_options_timer.timeout.connect(self.attempt_hide)

    def paintEvent(self, event):
        # Only paint background; no custom border (shadow provides edge)
        super().paintEvent(event)

    def enterEvent(self, event):
        logger.debug("Mouse entered OptionsPanel")
        self.hide_options_timer.stop()
        super().enterEvent(event)

    def leaveEvent(self, event):
        logger.debug("Mouse left OptionsPanel")
        if self.isVisible():
             self.hide_options_timer.start()
        super().leaveEvent(event)

    def attempt_hide(self):
        logger.debug("OptionsPanel hide timer timed out.")
        if not self.rect().contains(self.mapFromGlobal(QCursor.pos())) and self.isVisible():
            logger.debug("Mouse confirmed outside OptionsPanel. Hiding panel.")
            self.hide()
        else:
            logger.debug("Mouse re-entered OptionsPanel or check failed; not hiding.")
            self.hide_options_timer.stop()

    def show_options(self, section_name: str, position: QPoint, width: int, button_name: str):
        self.active_button_name = button_name

        if section_name == "Themes":
            self.tab_widget.setCurrentWidget(self.themes_section)
        elif section_name == "Appearance":
            self.tab_widget.setCurrentWidget(self.appearance_section)
        elif section_name == "Export":
            self.tab_widget.setCurrentWidget(self.export_section)
        else:
            logger.warning(f"Unknown section name: {section_name}")
            return

        # Adjust size to fit content
        current_tab = self.tab_widget.currentWidget()
        if not current_tab: return

        # Get margins from the panel's layout
        margins = self.main_layout.contentsMargins()
        content_height = current_tab.sizeHint().height()
        total_height = content_height + margins.top() + margins.bottom()

        self.setGeometry(position.x(), position.y(), width, total_height)
        self.show()
        self.raise_()

    def update_controls(self, fig_config: Optional[dict], theme_props: dict):
        self.current_theme_props = theme_props
        if hasattr(self.themes_section, 'update_controls'):
            self.themes_section.update_controls(fig_config, theme_props)
        if hasattr(self.appearance_section, 'update_controls'):
            self.appearance_section.update_controls(fig_config, theme_props)
        if hasattr(self.export_section, 'update_controls'):
            self.export_section.update_controls(fig_config, theme_props)

    def set_current_theme_in_controls(self, theme_key: str):
        if hasattr(self.themes_section, 'set_current_theme'):
            self.themes_section.set_current_theme(theme_key) 