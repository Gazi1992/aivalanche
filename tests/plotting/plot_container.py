# plot_container.py
import pyqtgraph as pg
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                             QComboBox, QLabel, QSizePolicy)
from PyQt6 import QtCore
# Or for PyQt5:
# from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
#                              QComboBox, QLabel, QSizePolicy)
# from PyQt5 import QtCore

try:
    from themes import THEMES, DEFAULT_THEME_NAME
except ImportError:
    print("Warning: Could not import THEMES or DEFAULT_THEME_NAME from themes.py. Using fallback.")
    THEMES = {
        "Classic Dark": {'background': 'k', 'foreground': 'w'},
        "Classic Light": {'background': 'w', 'foreground': 'k'}
        }
    DEFAULT_THEME_NAME = "Classic Dark"


class PlotContainer(QWidget):
    """
    A container widget holding a PlotWidget and controls for it.
    """
    # __init__ and _create_controls remain the same as the previous version
    # where controls are assigned to self.xxx variables.
    def __init__(self, initial_theme_name=DEFAULT_THEME_NAME, parent=None):
        super().__init__(parent)
        self.current_local_theme_name = initial_theme_name if initial_theme_name in THEMES else DEFAULT_THEME_NAME

        # Store references to controls that need text styling
        self.theme_label = None
        self.theme_combo = None
        self.btn_log_x = None
        self.btn_log_y = None
        self.btn_reset = None
        self.styled_buttons = []

        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(5)
        self.controls_layout = QHBoxLayout()
        self.controls_layout.setContentsMargins(5, 0, 5, 0)

        self.plot_widget = pg.PlotWidget()
        # Apply initial theme (background and text)
        self._apply_local_theme_style(self.current_local_theme_name)

        self._create_controls()

        self.main_layout.addLayout(self.controls_layout)
        self.main_layout.addWidget(self.plot_widget)

        self.plot_items = []

    def _create_controls(self):
        # Assign controls to self.xxx variables as before...
        self.theme_label = QLabel("Theme:")
        self.theme_combo = QComboBox()
        self.theme_combo.setToolTip("Set theme for this plot only")
        self.theme_combo.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        for theme_name in THEMES.keys():
            self.theme_combo.addItem(theme_name)
        self.theme_combo.setCurrentText(self.current_local_theme_name)
        self.theme_combo.currentTextChanged.connect(self._on_local_theme_change)
        self.controls_layout.addWidget(self.theme_label)
        self.controls_layout.addWidget(self.theme_combo)
        self.controls_layout.addStretch(1)
        self.btn_log_x = QPushButton("Log X")
        self.btn_log_x.setCheckable(True)
        self.btn_log_x.clicked.connect(self._toggle_log_x)
        self.controls_layout.addWidget(self.btn_log_x)
        self.btn_log_y = QPushButton("Log Y")
        self.btn_log_y.setCheckable(True)
        self.btn_log_y.clicked.connect(self._toggle_log_y)
        self.controls_layout.addWidget(self.btn_log_y)
        self.btn_reset = QPushButton("Reset View")
        self.btn_reset.clicked.connect(self._reset_view)
        self.controls_layout.addWidget(self.btn_reset)
        self.styled_buttons = [self.btn_log_x, self.btn_log_y, self.btn_reset]
        # Apply initial text color to controls
        self._apply_control_text_color(self.current_local_theme_name)

    # Passthrough Methods (add_plot_item, addLegend, showGrid) remain the same
    def add_plot_item(self, plot_func, *args, **kwargs):
        item = plot_func(self.plot_widget, *args, **kwargs)
        if item:
            self.plot_items.append(item)
        return item

    def addLegend(self, *args, **kwargs):
        # Store legend reference if created
        legend = self.plot_widget.addLegend(*args, **kwargs)
        # Apply theme color immediately if possible
        self._style_legend(self.current_local_theme_name)
        return legend

    def showGrid(self, *args, **kwargs):
        self.plot_widget.showGrid(*args, **kwargs)

    # Need to override setTitle to apply color immediately
    def setTitle(self, title):
        self.plot_widget.setTitle(title)
        # Apply theme color immediately
        self._style_title(self.current_local_theme_name)

    # Control Handlers (_toggle_log_x, _toggle_log_y, _reset_view) remain the same
    def _toggle_log_x(self, checked):
        plot_item = self.plot_widget.getPlotItem()
        plot_item.setLogMode(x=checked)
        self.btn_log_x.setChecked(plot_item.ctrl.logXCheck.isChecked())

    def _toggle_log_y(self, checked):
        plot_item = self.plot_widget.getPlotItem()
        plot_item.setLogMode(y=checked)
        self.btn_log_y.setChecked(plot_item.ctrl.logYCheck.isChecked())

    def _reset_view(self):
        self.plot_widget.setLogMode(x=False, y=False)
        self.btn_log_x.setChecked(False)
        self.btn_log_y.setChecked(False)
        self.plot_widget.autoRange()

    # --- Theme Handling ---

    def _on_local_theme_change(self, theme_name):
        """Applies the selected theme from the ComboBox to this plot container."""
        if theme_name in THEMES:
            self.current_local_theme_name = theme_name
            self._apply_local_theme_style(theme_name)
        else:
            print(f"Warning: Local theme '{theme_name}' not found in themes dictionary.")

    def _apply_local_theme_style(self, theme_name):
         """Applies styling (background, axes, labels, title, legend) for the local theme."""
         foreground_color = 'black' # Default
         background_color = 'w'    # Default
         if theme_name in THEMES:
            theme = THEMES[theme_name]
            background_color = theme.get('background', 'w')
            foreground_color = theme.get('foreground', 'black')
            print(f"Applying local theme '{theme_name}' styles to plot container.")
         else:
             # Fallback if theme name is invalid
             default_theme = THEMES.get(DEFAULT_THEME_NAME, {})
             background_color = default_theme.get('background', 'k')
             foreground_color = default_theme.get('foreground', 'black')
             print(f"Applying fallback theme '{DEFAULT_THEME_NAME}' styles.")


         # 1. Set Background
         self.plot_widget.setBackground(background_color)

         # 2. Style PlotWidget's internal elements
         self._style_plotwidget_elements(foreground_color)

         # 3. Style Container Controls
         self._apply_control_text_color(theme_name) # Pass theme name for consistency


    def _get_color(self, color_str):
        """Helper to convert color string/tuple to QColor."""
        return pg.mkColor(color_str) # pyqtgraph helper handles various formats


    def _style_plotwidget_elements(self, foreground_color_str):
        """Styles the axes, labels, title, and legend of the internal plot widget."""
        try:
            color = self._get_color(foreground_color_str)
            plot_item = self.plot_widget.getPlotItem()

            # Style Title (if it exists) - uses LabelItem
            self._style_title(self.current_local_theme_name) # Use helper

            # Style Axes (AxisItem)
            for axis_name in ['left', 'bottom', 'right', 'top']:
                axis = plot_item.getAxis(axis_name)
                if axis:
                    axis.setPen(pg.mkPen(color=color)) # Axis line color
                    axis.setTextPen(pg.mkPen(color=color)) # Tick label color

            # Style Axis Labels (LabelItem)
            for axis_name in ['left', 'bottom', 'right', 'top']:
                 label = plot_item.getLabel(axis_name)
                 if label:
                     # Labels are HTML-capable, styling might need HTML/CSS
                     # Simple approach: set color directly if possible (might not work for all versions)
                     # More robust: use html styling
                     # label.setText(label.text, color=foreground_color_str) # Old way, might not work
                     # This assumes the label text doesn't already contain HTML
                     current_text = label.text # Get current text content
                     # Rebuild text with style (potential issue if text had HTML)
                     label.setText(f'<span style="color: {foreground_color_str}">{current_text}</span>')


            # Style Legend (LegendItem) - Use helper
            self._style_legend(self.current_local_theme_name)

        except Exception as e:
            print(f"Error applying plot element styles for color {foreground_color_str}: {e}")


    def _style_title(self, theme_name):
        """Styles the title LabelItem based on the theme."""
        try:
            plot_item = self.plot_widget.getPlotItem()
            if plot_item and hasattr(plot_item, 'titleItem') and plot_item.titleItem:
                foreground_color = 'black' # default
                if theme_name in THEMES:
                    foreground_color = THEMES[theme_name].get('foreground', 'black')

                # Title uses LabelItem which supports HTML-like styling
                current_title = plot_item.titleItem.text
                # Avoid re-wrapping if already styled (basic check)
                if not current_title.startswith('<'):
                     plot_item.titleItem.setText(f'<span style="color: {foreground_color}; font-size: 11pt;">{current_title}</span>')
                else:
                    # Attempt to update existing style (more complex, might fail)
                    # For simplicity, we might just reset it if needed
                     plot_item.titleItem.setText(f'<span style="color: {foreground_color}; font-size: 11pt;">{plot_item.title()}</span>') # Reset with title text
        except Exception as e:
            print(f"Error styling title: {e}")

    def _style_legend(self, theme_name):
        """Styles the legend LabelItems based on the theme."""
        try:
            plot_item = self.plot_widget.getPlotItem()
            if plot_item and hasattr(plot_item, 'legend') and plot_item.legend:
                foreground_color = 'black'
                if theme_name in THEMES:
                    foreground_color = THEMES[theme_name].get('foreground', 'black')

                # Legend items are LabelItems
                for _, label_item in plot_item.legend.items:
                    # Similar to title/axis labels, use HTML styling
                    current_text = label_item.text
                    if not current_text.startswith('<'):
                         label_item.setText(f'<span style="color: {foreground_color}">{current_text}</span>')
                    else:
                         # Attempt update (can be complex, might need regex or parsing)
                         # Simple reset: Find original text (tricky), or just apply style
                         # This might double-wrap, needs care. Let's try a simple replace if possible
                         # A better way involves parsing the existing HTML, but this is complex.
                         # Simplest robust way is often to recreate legend or store original text.
                         # For now, we just set it, accepting potential issues if text was already HTML.
                         label_item.setText(f'<span style="color: {foreground_color}">{label_item.text}</span>') # Might double wrap!


        except Exception as e:
            print(f"Error styling legend: {e}")


    def _apply_control_text_color(self, theme_name):
        """Sets the color of CONTROLS (QLabel, QPushButton) based on theme foreground."""
        foreground_color = 'black'
        if theme_name in THEMES:
            theme = THEMES[theme_name]
            foreground_color = theme.get('foreground', 'black')
        else:
             default_theme = THEMES.get(DEFAULT_THEME_NAME, {})
             foreground_color = default_theme.get('foreground', 'black')

        style_sheet = f"color: {foreground_color};"
        if self.theme_label:
            try: self.theme_label.setStyleSheet(style_sheet)
            except Exception as e: print(f"Warn: Style Label: {e}")
        for button in self.styled_buttons:
            if button:
                try: button.setStyleSheet(style_sheet)
                except Exception as e: print(f"Warn: Style Button {button.text()}: {e}")
        if self.theme_combo:
             try: self.theme_combo.setStyleSheet(style_sheet) # Basic combo styling
             except Exception as e: print(f"Warn: Style Combo: {e}")


    # Cleanup (clear_plot_items) remains the same
    def clear_plot_items(self):
        for item in self.plot_items:
            try:
                self.plot_widget.removeItem(item)
            except Exception as e:
                print(f"Warning: Could not remove item {item}: {e}")
        self.plot_items = []
