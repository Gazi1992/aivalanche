# themes.py
import logging
from PyQt6.QtGui import QColor
import re

logger = logging.getLogger(__name__)

# -----------------------------------------------------------------------------
# Theme dictionaries
# -----------------------------------------------------------------------------

# --- 1. Light Theme (Clean & Bright) ---
light_theme = {
    'name': 'Light', 'config_key': 'light', 'is_dark': False,
    'window_bg': '#F3F4F6',     # light warm grey similar to screenshot bg
    'frame_bg':  '#FFFFFF',
    'plot_bg':   '#FFFFFF',
    'frame_border': '#E1E4E8',
    'border_radius': 8,
    'shadow_color': '#20000000', # slightly softer shadow
    'shadow_blur': 12,
    'shadow_offset': 3,
    'axis_fg': '#3C3F44', 'plot_title_font_size': '13pt', 'plot_title_margin_bottom': '8',
    'axis_label_font_size': '10pt', 'axis_tick_font_size': '8pt',
    'legend_font_size': '8pt', 'legend_text_color': '#3C3F44',
    'sidebar_bg': '#EDEFF2', 'sidebar_text_color': '#141821',
    'sidebar_button_bg': '#F7F9FA',  # very light grey tab background
    'sidebar_button_text_color': '#141821',
    'sidebar_button_border_color': '#E1E4E8',
    'sidebar_border': '#E1E4E8',
    'options_panel_border': '#E2E6EA',
    'options_panel_title_text': '#FF6D3D',  # orange accent for section titles
    'options_panel_label_text': '#3C3F44',
    'combo_box_bg': '#FFFFFF', 'combo_box_text': '#141821',
    'combo_box_border': '#E1E4E8', 'combo_box_selection_bg': '#F1F3F6',
    'error_frame_bg_light': "#FFEBEE",
    'selected_frame_border': '#FF6D3D', 'selected_frame_border_width': 2,
    'checkbox_border': '#3C3F44',
    'checkbox_bg_checked': '#F1F3F6',
    'checkbox_hover': '#2A2D32',
    'dialog_bg': '#FFFFFF',
    'dialog_text_color': '#141821',
    'dialog_button_bg': '#F7F9FA',
    'dialog_button_text': '#141821',
}

# --- 2. Dark Theme (Classic Dark) ---
dark_theme = {
    'name': 'Dark', 'config_key': 'dark', 'is_dark': True,
    'window_bg': '#0F172A',  # almost-black navy
    'frame_bg':  '#1E293B',  # dark slate surface
    'plot_bg':   '#1E293B',
    'frame_border': '#334155',
    'border_radius': 6,
    'shadow_color': '#80000000',
    'shadow_blur': 14,
    'shadow_offset': 2,
    'axis_fg': '#E2E8F0', 'plot_title_font_size': '13pt', 'plot_title_margin_bottom': '8',
    'axis_label_font_size': '10pt', 'axis_tick_font_size': '8pt',
    'legend_font_size': '8pt', 'legend_text_color': '#E2E8F0',
    'sidebar_bg': '#162033', 'sidebar_text_color': '#E2E8F0',
    'sidebar_button_bg': '#273447',
    'sidebar_button_text_color': '#E2E8F0',
    'sidebar_button_border_color': '#334155',
    'sidebar_border': '#334155',
    'options_panel_border': '#334155',
    'options_panel_title_text': '#0EA5E9',
    'options_panel_label_text': '#E2E8F0',
    'combo_box_bg': '#273447', 'combo_box_text': '#E2E8F0',
    'combo_box_border': '#334155', 'combo_box_selection_bg': '#324158',
    'error_frame_bg_dark': "#BF616A40",
    'selected_frame_border': '#0EA5E9', 'selected_frame_border_width': 2,
    'checkbox_border': '#334155',
    'checkbox_bg_checked': '#324158',
    'checkbox_hover': '#0EA5E9',
    'dialog_bg': '#1E293B',
    'dialog_text_color': '#E2E8F0',
    'dialog_button_bg': '#273447',
    'dialog_button_text': '#E2E8F0',
}


# --- Registry of all available themes ---
AVAILABLE_THEMES = {
    "light": light_theme,
    "dark": dark_theme,
}

DEFAULT_THEME_KEY = "light"

# --- Helper Functions (Unchanged) ---
def get_theme_config(theme_key: str) -> dict:
    if theme_key not in AVAILABLE_THEMES:
        logger.warning(f"Theme key '{theme_key}' not found. Falling back to default theme '{DEFAULT_THEME_KEY}'.")
        default_theme = AVAILABLE_THEMES.get(DEFAULT_THEME_KEY)
        if default_theme is None:
            logger.critical(f"Default theme key '{DEFAULT_THEME_KEY}' does not map to a valid theme. Returning empty dict.")
            return {} # Should not happen if DEFAULT_THEME_KEY is always in AVAILABLE_THEMES
        return default_theme
    return AVAILABLE_THEMES[theme_key]

def get_theme_display_names() -> list[str]:
    return [theme.get('name', key.capitalize()) for key, theme in AVAILABLE_THEMES.items()]

def get_theme_key_from_display_name(display_name: str) -> str | None:
    for key, theme_dict in AVAILABLE_THEMES.items():
        if theme_dict.get('name') == display_name:
            return key
    logger.warning(f"Could not find theme key for display name '{display_name}'.")
    return None

# -----------------------------------------------------------------------------
# Global application style sheet helpers
# -----------------------------------------------------------------------------

def _color_to_hex(col: str | QColor) -> str:
    """Return hex string (e.g. ``#AABBCC``) for any given colour input."""
    if isinstance(col, QColor):
        return col.name(QColor.NameFormat.HexRgb)
    return str(col)


def _adjust_color(col: str | QColor, factor: float) -> str:
    """Lighten (factor>1) or darken (factor<1) the colour and return hex."""
    qcol = QColor(col) if not isinstance(col, QColor) else QColor(col)
    if factor >= 1:
        qcol = qcol.lighter(int(factor * 100))
    else:
        if factor <= 0:
            factor = 0.01
        qcol = qcol.darker(int(100 / factor))
    return qcol.name(QColor.NameFormat.HexRgb)


_STYLE_TEMPLATE = """
/* -------------------------------------------------------------------------
   Base colours
   --------------------------------------------------------------------- */
QWidget {{
    background-color: {window_bg};
    color: {axis_fg};
    font-size: 9pt;
}}

/* -------------------------------------------------------------------------
   Generic push buttons ---------------------------------------------------- */
QPushButton {{
    /* generic styles, border removed to avoid shadows on specialised buttons */
    background: {sidebar_button_bg};
    color: {sidebar_button_text_color};
    border: none;
    border-radius: 3px;
    padding: 4px;
}}
QPushButton:hover:enabled {{ background: {sidebar_button_bg_hover}; }}
QPushButton:pressed:enabled {{ background: {sidebar_button_bg_active}; }}

/* -------------------------------------------------------------------------
   Sidebar (object name set by our code)
   --------------------------------------------------------------------- */
#Sidebar {{
    background-color: {sidebar_bg};
    border-right: 1px solid {sidebar_border};
}}

/* Sidebar navigation buttons ------------------------------------------------ */
#Sidebar QPushButton#SidebarButton,
#Sidebar QPushButton#SidebarButton:hover,
#Sidebar QPushButton#SidebarButton:checked,
#Sidebar QPushButton#SidebarButton:pressed,
#Sidebar QPushButton#SidebarButton:focus {{
    border: none;
    width: 100%;
    padding: 6px 20px 6px 20px;
    background-color: {sidebar_button_bg};
    color: {sidebar_button_text_color};
    text-align: left;
    border-radius: 0;
}}
#Sidebar QPushButton#SidebarButton:hover  {{ background-color: {sidebar_button_bg_hover}; }}
#Sidebar QPushButton#SidebarButton:checked {{ background-color: {sidebar_button_bg_active}; }}
#Sidebar QPushButton#SidebarButton:pressed {{ background-color: {sidebar_button_bg_active}; }}

/* Logo button in sidebar (inherits transparent bg, no border) */
#Sidebar QPushButton#SvgButton,
#Sidebar QPushButton#SvgButton:hover,
#Sidebar QPushButton#SvgButton:pressed,
#Sidebar QPushButton#SvgButton:checked,
#Sidebar QPushButton#SvgButton:focus {{
    background: transparent;
    border: none;
    padding: 0px;
}}

/* Comboboxes --------------------------------------------------------------- */
QComboBox {{
    background: {combo_box_bg};
    color: {combo_box_text};
    border: 1px solid {combo_box_border};
}}
QComboBox QAbstractItemView {{
    selection-background-color: {combo_box_selection_bg};
}}

/* Options panel ------------------------------------------------------------ */
#OptionsPanel {{
    background: {options_panel_bg};
    border: none;
    border-radius: 4px;
}}

#OptionsPanel QWidget {{
    background: transparent;
    border: none;
}}

/* Labels inside options panel */
#OptionsPanel QLabel {{
    color: {options_panel_label_text};
    background: transparent;
    border: none;
}}

/* Section headers inside options panel */
#OptionsPanel QLabel[objectName^="AppearanceSectionHeader"],
#OptionsPanel QLabel[objectName="LightThemeLabel"],
#OptionsPanel QLabel[objectName="DarkThemeLabel"] {{
    color: {options_panel_title_text};
    font-weight: bold;
    font-size: 11pt;
}}

/* Line edits --------------------------------------------------------------- */
QLineEdit {{
    background: {combo_box_bg};
    color: {combo_box_text};
    border: 1px solid {combo_box_border};
    border-radius: 3px;
    padding: 4px;
}}
QLineEdit:focus {{ border-color: {checkbox_hover}; }}

/* Combo boxes -------------------------------------------------------------- */
QComboBox {{
    background: {combo_box_bg};
    color: {combo_box_text};
    border: 1px solid {combo_box_border};
}}
QComboBox QAbstractItemView {{
    selection-background-color: {combo_box_selection_bg};
}}

/* Check boxes -------------------------------------------------------------- */
QCheckBox::indicator {{ width: 16px; height: 16px; }}
QCheckBox::indicator:unchecked {{
    border: 1px solid {checkbox_border};
    border-radius: 3px;
    background: transparent;
}}
QCheckBox::indicator:unchecked:hover {{ border: 1px solid {checkbox_hover}; }}
QCheckBox::indicator:checked {{
    border: 1px solid {options_panel_title_text};
    border-radius: 3px;
    background: {options_panel_title_text};
}}
QCheckBox::indicator:checked:hover {{
    border: 1px solid {checkbox_hover};
    background: {options_panel_title_text};
}}

/* Radio buttons ------------------------------------------------------------ */
QRadioButton {{
    color: {options_panel_label_text};
    background: transparent;
    padding: 4px;
}}
QRadioButton::indicator {{
    width: 14px;
    height: 14px;
    border: 1px solid {options_panel_border};
    background: {options_panel_bg};
    border-radius: 7px;
}}
QRadioButton::indicator:hover {{ border: 1px solid {checkbox_hover}; }}
QRadioButton::indicator:checked {{
    background: {selected_frame_border};
    border: 1px solid {selected_frame_border};
}}

/* Sliders ------------------------------------------------------------------ */
QSlider::groove:horizontal {{
    border: 1px solid {options_panel_border};
    height: 4px;
    background: {options_panel_bg_darker};
    margin: 2px 0;
    border-radius: 2px;
}}
QSlider::handle:horizontal {{
    background: {options_panel_label_text};
    border: 1px solid {options_panel_border};
    width: 12px;
    margin: -4px 0;
    border-radius: 6px;
}}

/* Primary buttons inside OptionsPanel ------------------------------------ */
#OptionsPanel QPushButton {{
    background: {primary_btn_bg};
    color: {primary_btn_text_color};
    border: none;
    border-radius: 4px;
    padding: 6px 12px;
    font-weight: bold;
}}
#OptionsPanel QPushButton:hover:enabled {{ background: {primary_btn_bg_hover}; }}
#OptionsPanel QPushButton:pressed:enabled {{ background: {primary_btn_bg_active}; }}
#OptionsPanel QPushButton:disabled {{
    background: {primary_btn_bg_disabled};
    color: {combo_box_text};
}}

/* ColorSwatch keeps its own appearance ------------------------------------ */
#OptionsPanel QPushButton#ColorSwatchButton {{
    background: transparent;
    border: 1px solid {options_panel_border};
    border-radius: 3px;
}}
#OptionsPanel QPushButton#ColorSwatchButton:hover {{ border-color: {checkbox_hover}; }}

/* Export (primary) button -------------------------------------------------- */
#OptionsPanel QPushButton#ExportButton,
#OptionsPanel QPushButton#ExportButton:disabled {{
    background: {export_btn_bg};
    color: {export_btn_text_color};
    border: none;
    border-radius: 4px;
    padding: 6px 12px;
    font-weight: bold;
}}
#OptionsPanel QPushButton#ExportButton:hover:enabled {{ background: {export_btn_bg_hover}; }}
#OptionsPanel QPushButton#ExportButton:pressed:enabled {{ background: {export_btn_bg_active}; }}

/* -------------------------------------------------------------------------
   Enhanced Dialog Styling - QMessageBox, QColorDialog, and QFileDialog
   --------------------------------------------------------------------- */

/* Base dialog styling */
QDialog, QColorDialog, QMessageBox, QFileDialog {{
    background-color: {dialog_bg};
    color: {dialog_text_color};
    border: 1px solid {sidebar_border};
}}

/* Force all dialog child widgets to inherit colors */
QDialog *, QColorDialog *, QMessageBox *, QFileDialog * {{
    background-color: {dialog_bg};
    color: {dialog_text_color};
}}

/* Dialog specific widget styling */
QDialog QWidget, QColorDialog QWidget, QMessageBox QWidget, QFileDialog QWidget {{
    background-color: {dialog_bg};
    color: {dialog_text_color};
}}

QDialog QFrame, QColorDialog QFrame, QMessageBox QFrame, QFileDialog QFrame {{
    background-color: {dialog_bg};
    border: none;
}}

QDialog QLabel, QColorDialog QLabel, QMessageBox QLabel, QFileDialog QLabel {{
    background-color: transparent;
    color: {dialog_text_color};
}}

/* Dialog button styling */
QDialog QPushButton, QColorDialog QPushButton, QMessageBox QPushButton, QFileDialog QPushButton {{
    background: {dialog_button_bg};
    color: {dialog_button_text};
    border: 1px solid {sidebar_border};
    border-radius: 3px;
    padding: 6px 12px;
    min-width: 60px;
}}

QDialog QPushButton:hover, QColorDialog QPushButton:hover, QMessageBox QPushButton:hover, QFileDialog QPushButton:hover {{
    background: {dialog_button_bg_hover};
}}

QDialog QPushButton:pressed, QColorDialog QPushButton:pressed, QMessageBox QPushButton:pressed, QFileDialog QPushButton:pressed {{
    background: {dialog_button_bg_active};
}}

/* Dialog input fields */
QDialog QLineEdit, QColorDialog QLineEdit, QFileDialog QLineEdit {{
    background: {combo_box_bg};
    color: {combo_box_text};
    border: 1px solid {combo_box_border};
    border-radius: 3px;
    padding: 4px;
}}

QDialog QSpinBox, QColorDialog QSpinBox, QFileDialog QSpinBox {{
    background: {combo_box_bg};
    color: {combo_box_text};
    border: 1px solid {combo_box_border};
    border-radius: 3px;
    padding: 4px;
}}

/* QFileDialog specific styling */
QFileDialog QTreeView, QFileDialog QListView {{
    background: {combo_box_bg};
    color: {combo_box_text};
    border: 1px solid {combo_box_border};
    selection-background-color: {combo_box_selection_bg};
}}

QFileDialog QComboBox {{
    background: {combo_box_bg};
    color: {combo_box_text};
    border: 1px solid {combo_box_border};
}}

/* QColorDialog specific styling */
QColorDialog QTabWidget {{
    background-color: {dialog_bg};
}}

QColorDialog QTabWidget::pane {{
    background-color: {dialog_bg};
    border: 1px solid {sidebar_border};
}}

QColorDialog QTabBar::tab {{
    background: {dialog_button_bg};
    color: {dialog_button_text};
    border: 1px solid {sidebar_border};
    padding: 4px 8px;
}}

QColorDialog QTabBar::tab:selected {{
    background: {dialog_button_bg_hover};
}}

/* QMessageBox specific icon area */
QMessageBox QLabel#qt_msgbox_label {{
    color: {dialog_text_color};
    background-color: transparent;
}}

QMessageBox QLabel#qt_msgboxex_icon_label {{
    background-color: transparent;
}}

/* Tab widget --------------------------------------------------------------- */
QTabWidget, QTabWidget::pane {{
    background-color: transparent;
    border: none;
}}

/* Input backgrounds ------------------------------------------------------- */
#OptionsPanel QLineEdit {{
    background: {combo_box_bg};
    color: {combo_box_text};
    border: 1px solid {combo_box_border};
    border-radius: 3px;
    padding: 4px;
}}
#OptionsPanel QLineEdit:focus {{ border-color: {checkbox_hover}; }}

#OptionsPanel QComboBox {{
    background: {combo_box_bg};
    color: {combo_box_text};
    border: 1px solid {combo_box_border};
    border-radius: 3px;
    padding: 2px 4px;
}}
#OptionsPanel QComboBox QAbstractItemView {{ selection-background-color: {combo_box_selection_bg}; }}

/* Spin boxes (look like line-edits) --------------------------------------- */
#OptionsPanel QSpinBox {{
    background: {combo_box_bg};
    color: {combo_box_text};
    border: 1px solid {combo_box_border};
    border-radius: 3px;
    padding: 4px 4px; /* leave room for text */
}}
#OptionsPanel QSpinBox::up-button,
#OptionsPanel QSpinBox::down-button {{ /* hide the tiny arrow buttons */
    width: 0px;
    height: 0px;
    border: none;
}}
#OptionsPanel QSpinBox::up-arrow,
#OptionsPanel QSpinBox::down-arrow {{ /* ensure no leftover arrows */
    image: none;
}}

/* PlotWidget inner frame ----------------------------------------------- */
PlotWidget > QFrame {{ border: 0px; }}

/* FigureComponent plot frame -------------------------------------------- */
QFrame[role="plot"] {{
    background: {frame_bg};
    border: 1px solid {frame_border};
    border-radius: {border_radius}px;
}}
QFrame[role="plot"][selected="true"] {{
    border: {selected_frame_border_width}px solid {selected_frame_border};
}}
"""


# -----------------------------------------------------------------------------
# Dialog styling utilities
# -----------------------------------------------------------------------------

def apply_dialog_theme(dialog, theme_props: dict):
    """Apply theme styling to a dialog widget and all its children.
    
    This function manually applies styling to ensure dialogs properly inherit
    the application theme, which can be problematic on some platforms.
    The styling is applied immediately and also once more when the dialog is
    shown to cover widgets that are lazily created by Qt *after* the initial
    construction (e.g. QColorDialog internals).
    """
    from PyQt6.QtCore import Qt, QObject, QEvent, QTimer
    from PyQt6.QtWidgets import QWidget

    if not dialog or not theme_props:
        return

    dialog_style = f"background-color: {theme_props.get('dialog_bg', '#FFFFFF')};\ncolor: {theme_props.get('dialog_text_color', '#000000')};"

    def _style_widget_tree(root: QWidget):
        """Recursively apply WA_StyledBackground + inline stylesheet."""
        if not root:
            return
        root.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        root.setStyleSheet(dialog_style)
        for child in root.findChildren(QWidget):
            child.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
            child.setStyleSheet(dialog_style)

    # Apply immediately (for already-created children)
    _style_widget_tree(dialog)

    # Ensure styling also occurs once the dialog is about to be shown — this
    # covers widgets that Qt creates lazily (common in QFileDialog/QColorDialog)
    class _StyleEventFilter(QObject):
        def eventFilter(self, obj, event):
            if obj is dialog and event.type() == QEvent.Type.Show:
                # Use single-shot timer so that it runs *after* Qt finished
                # laying out late-created children.
                QTimer.singleShot(0, lambda: _style_widget_tree(dialog))
            return False  # continue processing

    filter_obj = _StyleEventFilter(dialog)
    dialog.installEventFilter(filter_obj)
    # Keep a reference to avoid garbage collection
    dialog._theme_style_filter = filter_obj


def build_stylesheet(theme: dict) -> str:
    """Return a complete QSS string for *theme* suitable for
    ``QApplication.setStyleSheet``.  A few derived colours (hover / active)
    are generated on the fly so individual themes do not need to store them."""
    theme = theme.copy()  # do not mutate caller's dict

    # Resolve derived colours -------------------------------------------------
    base_btn_bg = theme.get("sidebar_button_bg", "#CCCCCC")
    theme["sidebar_button_bg_hover"] = _adjust_color(base_btn_bg, 1.15)
    theme["sidebar_button_bg_active"] = _adjust_color(base_btn_bg, 0.85)

    # Make options panel background match the 'pressed' state of sidebar buttons
    theme["options_panel_bg"] = theme["sidebar_button_bg_active"]

    # Derived darker shade of options panel bg for slider groove
    op_bg = theme["options_panel_bg"]
    theme["options_panel_bg_darker"] = _adjust_color(op_bg, 0.9)

    # Dialog defaults -------------------------------------------------------
    theme.setdefault("dialog_bg", theme.get("sidebar_bg", theme.get("window_bg", "#FFFFFF")))
    theme.setdefault("dialog_text_color", theme.get("axis_fg", "#000000"))

    dlg_btn_base = theme.get("dialog_button_bg", theme.get("sidebar_button_bg", base_btn_bg))
    theme.setdefault("dialog_button_bg", dlg_btn_base)
    theme.setdefault("dialog_button_text", theme.get("sidebar_button_text_color", theme.get("axis_fg", "#000000")))
    theme["dialog_button_bg_hover"] = _adjust_color(theme["dialog_button_bg"], 1.15)
    theme["dialog_button_bg_active"] = _adjust_color(theme["dialog_button_bg"], 0.85)

    # Primary accent button colours (used for all buttons in the options panel
    # and for dialog buttons)
    theme.setdefault("primary_btn_bg", theme.get("options_panel_title_text", "#FF6D3D"))
    theme["primary_btn_bg_hover"] = _adjust_color(theme["primary_btn_bg"], 1.15)
    theme["primary_btn_bg_active"] = _adjust_color(theme["primary_btn_bg"], 0.85)
    theme.setdefault("primary_btn_text_color", "#FFFFFF")

    # Disabled state (lighter) of primary button background
    theme["primary_btn_bg_disabled"] = _adjust_color(theme["primary_btn_bg"], 1.4)

    # Re-map legacy names so existing QSS selectors keep working -------------
    theme["export_btn_bg"] = theme["primary_btn_bg"]
    theme["export_btn_bg_hover"] = theme["primary_btn_bg_hover"]
    theme["export_btn_bg_active"] = theme["primary_btn_bg_active"]
    theme["export_btn_text_color"] = theme["primary_btn_text_color"]

    # Make dialog buttons share the accent colour ---------------------------
    theme["dialog_button_bg"] = theme["primary_btn_bg"]
    theme["dialog_button_bg_hover"] = theme["primary_btn_bg_hover"]
    theme["dialog_button_bg_active"] = theme["primary_btn_bg_active"]
    theme["dialog_button_text"] = theme["primary_btn_text_color"]

    # Ensure every placeholder in template exists in the mapping --------------
    required_keys = set(re.findall(r"{([a-zA-Z0-9_]+)}", _STYLE_TEMPLATE))
    missing_keys = required_keys - set(theme)
    if missing_keys:
        logger.debug("build_stylesheet: theme missing keys %s", sorted(missing_keys))

    # Finally produce sheet ----------------------------------------------------
    return _STYLE_TEMPLATE.format(**{k: _color_to_hex(v) for k, v in theme.items()})
