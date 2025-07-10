"""Utility helpers for logging and user-visible message boxes.

This centralises all UI-facing error / info dialogs so that they can be
configured or mocked from a single place.
"""

from __future__ import annotations

import sys
import logging
from typing import Optional

from PyQt6.QtWidgets import QApplication, QMessageBox
from PyQt6.QtCore import Qt

logger = logging.getLogger(__name__)

__all__ = ["show_critical", "show_error", "show_warning"]


def _show_message(level: str, title: str, msg: str, *, exc: Optional[Exception] = None) -> None:
    """Log *msg* at *level* and present it to the user.

    Falls back to printing to *stderr* if the Qt application has not been
    instantiated yet (headless / test mode).
    """
    level = level.lower()
    log_func = {
        "critical": logger.critical,
        "error": logger.error,
        "warning": logger.warning,
        "info": logger.info,
    }.get(level, logger.info)

    log_func(msg, exc_info=bool(exc))

    if QApplication.instance():
        # Create custom message box so we can enforce stylesheet attributes
        mbox = QMessageBox()
        mbox.setWindowTitle(title)
        mbox.setText(msg)
        mbox.setIcon({
            "critical": QMessageBox.Icon.Critical,
            "error": QMessageBox.Icon.Critical,
            "warning": QMessageBox.Icon.Warning,
            "info": QMessageBox.Icon.Information,
        }.get(level, QMessageBox.Icon.Information))
        
        # Apply theme styling
        mbox.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        
        # Try to get current theme and apply dialog styling
        try:
            from themes import get_theme_config, apply_dialog_theme
            
            # Get the main window to access current theme
            app = QApplication.instance()
            if app:
                for widget in app.topLevelWidgets():
                    if hasattr(widget, 'current_theme_props') and widget.current_theme_props:
                        apply_dialog_theme(mbox, widget.current_theme_props)
                        break
                else:
                    # Fallback: try to get default theme
                    default_theme = get_theme_config("light")
                    if default_theme:
                        apply_dialog_theme(mbox, default_theme)
        except Exception as e:
            logger.debug(f"Could not apply dialog theme: {e}")
        
        mbox.exec()
    else:
        print(f"{level.upper()}: {msg}", file=sys.stderr)


def show_critical(title: str, msg: str, *, exc: Optional[Exception] = None) -> None:
    """Present critical error message to user."""
    _show_message("critical", title, msg, exc=exc)


def show_error(title: str, msg: str, *, exc: Optional[Exception] = None) -> None:
    """Present error message to user."""
    _show_message("error", title, msg, exc=exc)


def show_warning(title: str, msg: str, *, exc: Optional[Exception] = None) -> None:
    """Present warning message to user."""
    _show_message("warning", title, msg, exc=exc) 