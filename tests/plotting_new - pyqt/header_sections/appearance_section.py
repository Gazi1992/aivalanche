# header_sections/appearance_section.py
import logging
from typing import Dict, Optional, Any
from PyQt6.QtWidgets import (
    QWidget, QLabel, QPushButton, QSlider, QCheckBox, QLineEdit,
    QColorDialog, QHBoxLayout, QVBoxLayout, QFrame, QSizePolicy, QSpacerItem
)
from PyQt6.QtCore import pyqtSignal, Qt, QSize
from PyQt6.QtGui import QColor, QPixmap, QIcon

logger = logging.getLogger(__name__)

class AppearanceSectionWidget(QWidget):
    # Grid signals
    grid_x_visibility_changed = pyqtSignal(bool)
    grid_y_visibility_changed = pyqtSignal(bool)
    grid_color_changed = pyqtSignal(QColor)
    grid_opacity_changed = pyqtSignal(float)
    
    # Title and axis signals
    title_changed = pyqtSignal(str)
    x_label_changed = pyqtSignal(str)
    y_label_changed = pyqtSignal(str)

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        self.setObjectName("AppearanceSectionWidget")
        self._current_grid_color = QColor(Qt.GlobalColor.gray)

        # Parent layout
        parent_layout = QVBoxLayout(self)
        parent_layout.setContentsMargins(0, 0, 0, 0)
        parent_layout.setSpacing(10)

        # Container that holds all option controls so we can toggle visibility
        self.controls_container = QWidget()
        layout = QVBoxLayout(self.controls_container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)
        
        # === LABELS SECTION ===
        self.labels_header = QLabel("Labels")
        self.labels_header.setObjectName("AppearanceSectionHeaderLabels")
        layout.addWidget(self.labels_header)
        
        # Title
        self.label_title = QLabel("Title:")
        self.edit_title = QLineEdit()
        self.edit_title.setPlaceholderText("Plot title")
        self.edit_title.textChanged.connect(self.title_changed.emit)
        row_title = QHBoxLayout()
        row_title.setContentsMargins(0, 0, 0, 0)
        row_title.addWidget(self.label_title)
        row_title.addStretch(1)
        row_title.addWidget(self.edit_title)
        self.edit_title.setMinimumWidth(150)
        layout.addLayout(row_title)
        
        # X Label
        self.label_x_axis = QLabel("X Axis Label:")
        self.edit_x_label = QLineEdit()
        self.edit_x_label.setPlaceholderText("X axis label")
        self.edit_x_label.textChanged.connect(self.x_label_changed.emit)
        row_x_label = QHBoxLayout()
        row_x_label.setContentsMargins(0, 0, 0, 0)
        row_x_label.addWidget(self.label_x_axis)
        row_x_label.addStretch(1)
        row_x_label.addWidget(self.edit_x_label)
        self.edit_x_label.setMinimumWidth(150)
        layout.addLayout(row_x_label)
        
        # Y Label
        self.label_y_axis = QLabel("Y Axis Label:")
        self.edit_y_label = QLineEdit()
        self.edit_y_label.setPlaceholderText("Y axis label")
        self.edit_y_label.textChanged.connect(self.y_label_changed.emit)
        row_y_label = QHBoxLayout()
        row_y_label.setContentsMargins(0, 0, 0, 0)
        row_y_label.addWidget(self.label_y_axis)
        row_y_label.addStretch(1)
        row_y_label.addWidget(self.edit_y_label)
        self.edit_y_label.setMinimumWidth(150)
        layout.addLayout(row_y_label)

        # Separator between sections
        sep_labels = QFrame()
        sep_labels.setFrameShape(QFrame.Shape.HLine)
        sep_labels.setFrameShadow(QFrame.Shadow.Sunken)
        layout.addWidget(sep_labels)
        
        # === GRID SECTION ===
        self.grid_header_lbl = QLabel("Grid")
        self.grid_header_lbl.setObjectName("AppearanceSectionHeaderGrid")
        layout.addWidget(self.grid_header_lbl)
        
        # Grid visibility
        self.label_grid_x = QLabel("X Grid Visible:")
        self.cb_grid_x_visible = QCheckBox()
        self.cb_grid_x_visible.setCursor(Qt.CursorShape.PointingHandCursor)
        self.cb_grid_x_visible.setText("")
        self.cb_grid_x_visible.stateChanged.connect(
            lambda state: self.grid_x_visibility_changed.emit(state == Qt.CheckState.Checked.value))
        row_x = QHBoxLayout()
        row_x.setContentsMargins(0, 0, 0, 0)
        row_x.addWidget(self.label_grid_x)
        row_x.addStretch(1)
        row_x.addWidget(self.cb_grid_x_visible)
        layout.addLayout(row_x)

        self.label_grid_y = QLabel("Y Grid Visible:")
        self.cb_grid_y_visible = QCheckBox()
        self.cb_grid_y_visible.setCursor(Qt.CursorShape.PointingHandCursor)
        self.cb_grid_y_visible.setText("")
        self.cb_grid_y_visible.stateChanged.connect(
            lambda state: self.grid_y_visibility_changed.emit(state == Qt.CheckState.Checked.value))
        row_y = QHBoxLayout()
        row_y.setContentsMargins(0, 0, 0, 0)
        row_y.addWidget(self.label_grid_y)
        row_y.addStretch(1)
        row_y.addWidget(self.cb_grid_y_visible)
        layout.addLayout(row_y)
        
        # Grid color
        self.label_grid_color = QLabel("Grid Color:")
        self.btn_grid_color = QPushButton()
        self.btn_grid_color.setToolTip("Select grid color")
        self.btn_grid_color.setFixedSize(60, 24)
        self.btn_grid_color.clicked.connect(self._on_select_grid_color)
        self._update_color_button_visual(self._current_grid_color)
        self.btn_grid_color.setObjectName("ColorSwatchButton")
        row_color = QHBoxLayout()
        row_color.setContentsMargins(0, 0, 0, 0)
        row_color.addWidget(self.label_grid_color)
        row_color.addStretch(1)
        row_color.addWidget(self.btn_grid_color)
        layout.addLayout(row_color)

        # Grid opacity
        self.label_grid_opacity_title = QLabel("Grid Opacity:")
        self.slider_grid_opacity = QSlider(Qt.Orientation.Horizontal)
        self.slider_grid_opacity.setMinimum(0); self.slider_grid_opacity.setMaximum(100)
        self.slider_grid_opacity.setTickInterval(10)
        self.slider_grid_opacity.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.slider_grid_opacity.valueChanged.connect(self._on_opacity_slider_changed)
        self.slider_grid_opacity.setMaximumWidth(150)

        self.label_grid_opacity_value = QLabel("0.00")
        self.label_grid_opacity_value.setFixedWidth(35)
        
        opacity_row_layout = QHBoxLayout()
        opacity_row_layout.setContentsMargins(0, 0, 0, 0)
        opacity_row_layout.addWidget(self.slider_grid_opacity)
        opacity_row_layout.addWidget(self.label_grid_opacity_value)

        row_opacity = QHBoxLayout()
        row_opacity.setContentsMargins(0, 0, 0, 0)
        row_opacity.addWidget(self.label_grid_opacity_title)
        row_opacity.addStretch(1)
        row_opacity.addLayout(opacity_row_layout)
        layout.addLayout(row_opacity)

        # Spacer at end to push items up if needed
        layout.addStretch(1)

        # Add controls container to parent layout
        parent_layout.addWidget(self.controls_container)

        # Prompt label shown when no figure is selected --------------------
        self.no_fig_prompt = QLabel("No figure selected.\nClick on a figure's border to select one.")
        self.no_fig_prompt.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.no_fig_prompt.setWordWrap(True)
        self.no_fig_prompt.setStyleSheet("font-style: italic; color: gray;")
        parent_layout.addWidget(self.no_fig_prompt)

        # Start with prompt visible, controls hidden until a figure is chosen
        self.controls_container.hide()
        self.no_fig_prompt.show()

    def _update_color_button_visual(self, color: QColor):
        self._current_grid_color = color
        pixmap_size = self.btn_grid_color.size() - QSize(8,8) # Inner color swatch
        if pixmap_size.width() < 1 or pixmap_size.height() < 1: pixmap_size = QSize(1,1)
        pixmap = QPixmap(pixmap_size)
        pixmap.fill(color if color.isValid() else Qt.GlobalColor.transparent) # Show transparency if invalid
        self.btn_grid_color.setIcon(QIcon(pixmap))
        self.btn_grid_color.setText("")

    def _on_select_grid_color(self):
        dialog = QColorDialog(self._current_grid_color if self._current_grid_color.isValid() else Qt.GlobalColor.gray, self)
        dialog.setOption(QColorDialog.ColorDialogOption.ShowAlphaChannel, True)
        dialog.setOption(QColorDialog.ColorDialogOption.DontUseNativeDialog, True)
        dialog.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        
        # Apply enhanced theme styling
        try:
            from themes import apply_dialog_theme
            main_win = self.window()
            if hasattr(main_win, 'current_theme_props') and main_win.current_theme_props:
                apply_dialog_theme(dialog, main_win.current_theme_props)
        except Exception as e:
            logger.debug(f"Could not apply dialog theme to color dialog: {e}")
        
        # Ensure the main window regains focus after dialog closes (either OK or Cancel)
        main_win = self.window()
        if main_win is not None:
            dialog.finished.connect(lambda _ignored: (main_win.activateWindow(), main_win.raise_(), main_win.setFocus()))
        
        if dialog.exec():
            new_color = dialog.currentColor()
            if new_color.isValid():
                self._update_color_button_visual(new_color)
                self.grid_color_changed.emit(new_color)

    def _on_opacity_slider_changed(self, value: int):
        opacity_float = value / 100.0
        self.label_grid_opacity_value.setText(f"{opacity_float:.2f}")
        self.grid_opacity_changed.emit(opacity_float)

    def update_controls(self, fig_config: Optional[dict], theme_props: dict):
        """Updates controls based on figure config or defaults."""
        # Toggle prompt / controls visibility first
        has_figure = fig_config is not None
        self.controls_container.setVisible(has_figure)
        self.no_fig_prompt.setVisible(not has_figure)

        if not has_figure:
            return  # Nothing else to update when no figure is selected

        # Block signals while setting programmatically
        self.edit_title.blockSignals(True)
        self.edit_x_label.blockSignals(True)
        self.edit_y_label.blockSignals(True)
        self.cb_grid_x_visible.blockSignals(True)
        self.cb_grid_y_visible.blockSignals(True)
        self.slider_grid_opacity.blockSignals(True)

        if fig_config: # A specific figure is selected
            # Update labels
            self.edit_title.setText(fig_config.get('title', ''))
            self.edit_x_label.setText(fig_config.get('x_label', ''))
            self.edit_y_label.setText(fig_config.get('y_label', ''))
            
            # Update grid settings
            self.cb_grid_x_visible.setChecked(fig_config.get('grid_x', True))
            self.cb_grid_y_visible.setChecked(fig_config.get('grid_y', True))

            grid_color_hex = fig_config.get('grid_color')
            current_color = QColor() # Invalid default
            if grid_color_hex and QColor.isValidColor(grid_color_hex):
                current_color = QColor(grid_color_hex)
            else: # Fallback to theme's axis_fg
                theme_fg_hex = theme_props.get('axis_fg', '#808080')
                current_color = QColor(theme_fg_hex) if QColor.isValidColor(theme_fg_hex) else QColor(Qt.GlobalColor.gray)
            self._update_color_button_visual(current_color)

            grid_alpha = fig_config.get('grid_alpha', 0.3)
            self.slider_grid_opacity.setValue(int(grid_alpha * 100))
            self.label_grid_opacity_value.setText(f"{grid_alpha:.2f}")
        else: # No figure selected (apply to all mode), show defaults
            # Clear labels
            self.edit_title.setText('')
            self.edit_x_label.setText('')
            self.edit_y_label.setText('')
            
            # Grid defaults
            self.cb_grid_x_visible.setChecked(True) # Default
            self.cb_grid_y_visible.setChecked(True) # Default

            theme_fg_hex = theme_props.get('axis_fg', '#808080') # Default from theme for color
            default_color = QColor(theme_fg_hex) if QColor.isValidColor(theme_fg_hex) else QColor(Qt.GlobalColor.gray)
            self._update_color_button_visual(default_color)

            default_alpha = 0.3 # Default
            self.slider_grid_opacity.setValue(int(default_alpha * 100))
            self.label_grid_opacity_value.setText(f"{default_alpha:.2f}")

        # Unblock signals
        self.edit_title.blockSignals(False)
        self.edit_x_label.blockSignals(False)
        self.edit_y_label.blockSignals(False)
        self.cb_grid_x_visible.blockSignals(False)
        self.cb_grid_y_visible.blockSignals(False)
        self.slider_grid_opacity.blockSignals(False) 