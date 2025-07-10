# sidebar.py
"""Sidebar panel replacing the previous AppHeader widget.

The widget now sits vertically on the left side of the main window and exposes
exactly the same signals the header did.  For transitional compatibility an
alias *AppHeader* is also exported so the rest of the codebase can continue to
work until everything is renamed.
"""

import logging
from typing import Optional, Dict, Any
import os

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QSizePolicy, QGraphicsDropShadowEffect, QLabel
from PyQt6.QtCore import QPoint, Qt, pyqtSignal, QSize, QRectF, QSizeF, QPointF
from PyQt6.QtGui import QColor, QCursor, QPainter, QPen
from PyQt6.QtCore import QSize
from components.icon_manager import IconManager
from components.svg_button import SvgButton

from header_sections.options_panel import OptionsPanel

logger = logging.getLogger(__name__)

class Sidebar(QWidget):
    """Vertical sidebar containing navigation / option buttons."""

    # Re-export the same signals so the rest of the app keeps functioning
    theme_selected = pyqtSignal(str)
    grid_x_visibility_changed = pyqtSignal(bool)
    grid_y_visibility_changed = pyqtSignal(bool)
    grid_color_changed = pyqtSignal(QColor)
    grid_opacity_changed = pyqtSignal(float)
    # New appearance signals
    title_changed = pyqtSignal(str)
    x_label_changed = pyqtSignal(str)
    y_label_changed = pyqtSignal(str)
    export_requested = pyqtSignal(dict)  # export request dictionary

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        self.setObjectName("Sidebar")
        self.setAutoFillBackground(True)
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)

        self.current_theme_props: Dict[str, Any] = {}
        self.active_options_button: Optional[QPushButton] = None

        # Vertical layout for sidebar orientation
        self.main_layout = QVBoxLayout(self)
        # Center horizontally and align items to top within the sidebar
        self.main_layout.setAlignment(Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop)
        self.main_layout.setContentsMargins(0, 8, 0, 8)
        self.main_layout.setSpacing(0)

        self.buttons: Dict[str, QPushButton] = {}
        # Prepare icon manager and logo button
        self.icon_manager = IconManager(base_path=os.path.join(os.path.dirname(__file__), 'components', 'svg_templates'))
        self.icon_manager.register_icon('sidebar_logo', 'logo.svg')

        self._create_logo_button()
        self._create_buttons()

        self.main_layout.addStretch(1)

        panel_parent = self.parent() if self.parent() else self
        self.options_panel = OptionsPanel(panel_parent)
        self.options_panel.hide()

        self._connect_signals()

        # Make sidebar slightly wider for comfortable button labels
        self.setFixedWidth(160)

    # ------------------------------------------------------------------ UI helpers
    def _create_logo_button(self):
        # Create logo button – the aspect ratio is now automatically determined
        # from the SVG's viewBox via IconManager → SvgButton logic.
        button_size = 100

        self.logo_btn = SvgButton(
            'sidebar_logo',
            self.icon_manager,
            text="",
            size=QSize(button_size, button_size),
            enable_hover=False,
            enable_press=False,
        )
        
        # Style the button
        self.logo_btn.setFlat(True)
        self.logo_btn.setCursor(Qt.CursorShape.ArrowCursor)
        self.logo_btn.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        
        self.main_layout.addSpacing(30)
        self.main_layout.addWidget(self.logo_btn, alignment=Qt.AlignmentFlag.AlignHCenter)
        self.main_layout.addSpacing(50)

    def _create_buttons(self):
        button_definitions = [
            ("Themes", "SidebarButton", lambda: self.toggle_options_panel("Themes", self.buttons["Themes"])),
            ("Appearance", "SidebarButton", lambda: self.toggle_options_panel("Appearance", self.buttons["Appearance"])),
            ("Export", "SidebarButton", lambda: self.toggle_options_panel("Export", self.buttons["Export"]))
        ]
        for name, obj_name, callback in button_definitions:
            button = QPushButton(name)
            # Make button fill sidebar width
            button.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
            button.setMinimumHeight(36)
            button.setObjectName(obj_name)
            button.setCheckable(True)
            button.clicked.connect(callback)
            self.main_layout.addWidget(button)
            self.buttons[name] = button

    def _connect_signals(self):
        if hasattr(self.options_panel.themes_section, 'theme_selected'):
            self.options_panel.themes_section.theme_selected.connect(self.theme_selected)
        else:
            logger.warning("OptionsPanel.themes_section missing 'theme_selected' signal.")

        grid_signals = {
            'grid_x_visibility_changed': self.grid_x_visibility_changed,
            'grid_y_visibility_changed': self.grid_y_visibility_changed,
            'grid_color_changed': self.grid_color_changed,
            'grid_opacity_changed': self.grid_opacity_changed,
        }

        for signal_name, slot in grid_signals.items():
            if hasattr(self.options_panel.appearance_section, signal_name):
                getattr(self.options_panel.appearance_section, signal_name).connect(slot)
            else:
                logger.warning(f"OptionsPanel.appearance_section missing '{signal_name}' signal.")

        if hasattr(self.options_panel.export_section, 'export_requested'):
            self.options_panel.export_section.export_requested.connect(self.export_requested)
        else:
            logger.warning("OptionsPanel.export_section missing 'export_requested' signal.")

        # Connect new appearance signals
        appearance_signals = {
            'title_changed': self.title_changed,
            'x_label_changed': self.x_label_changed,
            'y_label_changed': self.y_label_changed,
        }

        for signal_name, slot in appearance_signals.items():
            if hasattr(self.options_panel.appearance_section, signal_name):
                getattr(self.options_panel.appearance_section, signal_name).connect(slot)
            else:
                logger.warning(f"OptionsPanel.appearance_section missing '{signal_name}' signal.")

    # ------------------------------------------------------------------ Behaviour
    def toggle_options_panel(self, section_name: str, button: QPushButton):
        """Show/hide the options panel next to the sidebar."""
        if self.options_panel.isVisible() and self.active_options_button == button:
            self.options_panel.hide()
            button.setChecked(False)
            self.active_options_button = None
        else:
            if self.active_options_button:
                self.active_options_button.setChecked(False)

            # Align top of options panel with the clicked button
            btn_top_global = button.mapToGlobal(QPoint(0, 0))
            sidebar_top_right_global = QPoint(self.mapToGlobal(QPoint(self.width(), 0)).x(), btn_top_global.y())
            panel_width = max(300, self.width())

            self.options_panel.show_options(section_name, sidebar_top_right_global, panel_width, section_name)
            button.setChecked(True)
            self.active_options_button = button

        # Refresh style
        self.style().unpolish(self)
        self.style().polish(self)

    # ------------------------------------------------------------------ Public API mirroring old header
    def update_controls(self, fig_config: Optional[dict], theme_props: dict):
        self.current_theme_props = theme_props
        self.options_panel.update_controls(fig_config, theme_props)
        # logo colour handled via update_logo_color; global styling covers visuals
        self.update_logo_color(theme_props)

    # ------------------------------------------------------------------ Logo colour update
    def update_logo_color(self, theme_props: dict):
        """Recolour the SVG logo to match the theme."""
        if not theme_props:
            return
        self.current_theme_props = theme_props
        logo_color = theme_props.get('sidebar_button_text_color', '#333333')
        self.logo_btn.set_icon_parameters(normal={"fill_color": logo_color})

    def set_current_theme_in_controls(self, theme_key: str):
        if self.options_panel:
            self.options_panel.set_current_theme_in_controls(theme_key)

    # ------------------------------------------------------------------ Event forwarding
    def mousePressEvent(self, event):
        if self.options_panel and self.options_panel.isVisible():
            if not self.options_panel.geometry().contains(event.globalPosition().toPoint()):
                clicked_button = None
                for button in self.buttons.values():
                    if button.geometry().contains(self.mapFromGlobal(event.globalPosition().toPoint())):
                        clicked_button = button
                        break
                if not clicked_button:
                    self.options_panel.hide()
                    if self.active_options_button:
                        self.active_options_button.setChecked(False)
                    self.active_options_button = None
        super().mousePressEvent(event)