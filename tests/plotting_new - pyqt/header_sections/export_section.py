# header_sections/export_section.py
"""Export options section for the header panel.

This module provides ``ExportSectionWidget``—a rich UI that lets the user
configure export parameters before triggering an export of the *currently
selected* figure.

The widget groups parameters into 3 areas:
    1. File target – type (image / CSV), directory, filename
    2. File-type-specific options
       * Image: output format (png, jpeg, …), dpi, width, height
       * CSV:   separator (, / \t), numeric precision

When the user presses the final *Export* button, all parameters are packed
into a ``dict`` and emitted via the ``export_requested`` signal. Down-stream
handlers (header → main window → figure component) can then perform the actual
export.
"""

from __future__ import annotations

import logging
import os
from functools import partial
from typing import Dict, Any, Optional

from PyQt6.QtCore import Qt, pyqtSignal, QTimer
from PyQt6.QtGui import QColor
from PyQt6.QtWidgets import (
    QWidget,
    QLabel,
    QLineEdit,
    QPushButton,
    QGridLayout,
    QHBoxLayout,
    QVBoxLayout,
    QComboBox,
    QFileDialog,
    QSpinBox,
    QStackedWidget,
    QGroupBox,
    QSpacerItem,
    QSizePolicy,
    QRadioButton,
    QButtonGroup,
    QProgressBar,
    QMessageBox,
    QFrame,
)

logger = logging.getLogger(__name__)

# -----------------------------------------------------------------------------
# Constants
# -----------------------------------------------------------------------------
_IMAGE_FORMATS = [
    "png",
    "jpeg",
    "jpg",
    "bmp",
    "pbm",
    "tif",
    "cur",
    "ico",
    "icns",
]
_CSV_SEPARATORS = {
    "Comma ( , )": ",",
    "Tab ( \t )": "\t",
}

# -----------------------------------------------------------------------------
# Helper functions
# -----------------------------------------------------------------------------

def _make_spinbox(min_val: int, max_val: int, step: int, default: int) -> QSpinBox:
    sb = QSpinBox()
    sb.setRange(min_val, max_val)
    sb.setSingleStep(step)
    sb.setValue(default)
    return sb


# -----------------------------------------------------------------------------
# Export section widget
# -----------------------------------------------------------------------------

class ExportSectionWidget(QWidget):
    """Widget allowing configuration of export parameters.

    The signal *export_requested* is emitted with a ``dict`` when the user
    clicks the final *Export* button.
    """

    export_requested = pyqtSignal(dict)  # Emits a dict with all export params

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        self.setObjectName("ExportSectionWidget")

        # ------------------------------------------------------------------ UI
        parent_layout = QVBoxLayout(self)
        parent_layout.setContentsMargins(0, 0, 0, 0)
        parent_layout.setSpacing(10)

        # Container with all option controls so we can toggle visibility
        self.controls_container = QWidget()
        root_layout = QVBoxLayout(self.controls_container)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(10)

        # 1) File target area -------------------------------------------------
        target_group = QWidget()
        target_layout = QGridLayout(target_group)
        target_layout.setContentsMargins(6, 6, 6, 6)
        target_layout.setHorizontalSpacing(8)
        target_layout.setVerticalSpacing(6)

        lbl_type = QLabel("Type:")
        self.rb_image = QRadioButton("Image")
        self.rb_csv = QRadioButton("CSV")
        self.rb_image.setChecked(True)

        self.type_group = QButtonGroup(self)
        self.type_group.addButton(self.rb_image)
        self.type_group.addButton(self.rb_csv)

        # connect toggles
        self.rb_image.toggled.connect(lambda checked: checked and self._on_type_changed("Image"))
        self.rb_csv.toggled.connect(lambda checked: checked and self._on_type_changed("CSV"))

        lbl_dir = QLabel("Directory:")
        self.le_directory = QLineEdit()
        self.btn_browse_dir = QPushButton("…")
        self.btn_browse_dir.setFixedWidth(28)
        self.btn_browse_dir.clicked.connect(self._browse_directory)

        lbl_fname = QLabel("Filename:")
        self.le_filename = QLineEdit("figure")

        target_layout.addWidget(lbl_type, 0, 0)
        btns_row = QHBoxLayout()
        btns_row.setContentsMargins(0, 0, 0, 0)
        btns_row.setSpacing(4)
        btns_row.addWidget(self.rb_image)
        btns_row.addWidget(self.rb_csv)
        target_layout.addLayout(btns_row, 0, 1, 1, 2)
        target_layout.addWidget(lbl_dir, 1, 0)
        target_layout.addWidget(self.le_directory, 1, 1)
        target_layout.addWidget(self.btn_browse_dir, 1, 2)
        target_layout.addWidget(lbl_fname, 2, 0)
        target_layout.addWidget(self.le_filename, 2, 1, 1, 2)

        # Cap widths so panel never grows excessively
        target_group.setMaximumWidth(330)

        # 2) Stacked widget with type-specific options -----------------------
        self.stacked_opts = QStackedWidget()
        self.stacked_opts.setMaximumWidth(330)

        # -- Image options page
        img_opts_widget = QWidget()
        img_layout = QGridLayout(img_opts_widget)
        img_layout.setContentsMargins(6, 6, 6, 6)
        img_layout.setHorizontalSpacing(8)
        img_layout.setVerticalSpacing(6)

        lbl_img_format = QLabel("Format:")
        self.combo_img_format = QComboBox()
        self.combo_img_format.addItems(_IMAGE_FORMATS)
        self.combo_img_format.setCurrentText("png")

        lbl_dpi = QLabel("DPI:")
        self.spin_dpi = _make_spinbox(50, 1200, 50, 300)
        self.spin_dpi.valueChanged.connect(partial(self._sync_dims, trigger="dpi"))

        lbl_width = QLabel("Width (px):")
        self.spin_width = _make_spinbox(20, 10000, 10, 800)
        self.spin_width.valueChanged.connect(partial(self._sync_dims, trigger="width"))

        lbl_height = QLabel("Height (px):")
        self.spin_height = _make_spinbox(20, 10000, 10, 600)
        self.spin_height.valueChanged.connect(partial(self._sync_dims, trigger="height"))

        img_layout.addWidget(lbl_img_format, 0, 0)
        img_layout.addWidget(self.combo_img_format, 0, 1)
        img_layout.addWidget(lbl_dpi, 1, 0)
        img_layout.addWidget(self.spin_dpi, 1, 1)
        img_layout.addWidget(lbl_width, 2, 0)
        img_layout.addWidget(self.spin_width, 2, 1)
        img_layout.addWidget(lbl_height, 3, 0)
        img_layout.addWidget(self.spin_height, 3, 1)

        self.stacked_opts.addWidget(img_opts_widget)  # index 0

        # -- CSV options page
        csv_opts_widget = QWidget()
        csv_layout = QGridLayout(csv_opts_widget)
        csv_layout.setContentsMargins(6, 6, 6, 6)
        csv_layout.setHorizontalSpacing(8)
        csv_layout.setVerticalSpacing(6)

        lbl_sep = QLabel("Separator:")
        self.combo_sep = QComboBox()
        self.combo_sep.addItems(_CSV_SEPARATORS.keys())
        self.combo_sep.setCurrentIndex(0)

        lbl_prec = QLabel("Precision:")
        self.spin_precision = _make_spinbox(0, 20, 1, 10)

        csv_layout.addWidget(lbl_sep, 0, 0)
        csv_layout.addWidget(self.combo_sep, 0, 1)
        csv_layout.addWidget(lbl_prec, 1, 0)
        csv_layout.addWidget(self.spin_precision, 1, 1)

        self.stacked_opts.addWidget(csv_opts_widget)  # index 1

        # 3) Export button ----------------------------------------------------
        self.btn_export = QPushButton("Export")
        self.btn_export.setObjectName("ExportButton")
        self.btn_export.clicked.connect(self._emit_request)

        # Add sections vertically -------------------------------------------
        root_layout.addWidget(target_group)

        # Separator line between target and extra options
        separator1 = QFrame()
        separator1.setFrameShape(QFrame.Shape.HLine)
        separator1.setFrameShadow(QFrame.Shadow.Sunken)
        root_layout.addWidget(separator1)

        root_layout.addWidget(self.stacked_opts)

        # Separator line before export button
        separator2 = QFrame()
        separator2.setFrameShape(QFrame.Shape.HLine)
        separator2.setFrameShadow(QFrame.Shadow.Sunken)
        root_layout.addWidget(separator2)

        root_layout.addWidget(self.btn_export, alignment=Qt.AlignmentFlag.AlignRight)

        # Spacer to push everything up (helps OptionsPanel auto-sizing)
        root_layout.addItem(QSpacerItem(1, 1, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))

        # Progress bar -------------------------------------------------------
        self.progress = QProgressBar()
        self.progress.setMaximum(100)
        self.progress.setMinimum(0)
        self.progress.setValue(0)
        self.progress.setTextVisible(False)
        self.progress.setFixedHeight(4)
        self.progress.hide()
        root_layout.addWidget(self.progress)

        # Keep aspect ratio (needs spin boxes created above)
        self._aspect_ratio = self.spin_width.value() / self.spin_height.value()
        self._last_dpi = self.spin_dpi.value()

        # Add controls container to parent layout ---------------------------
        parent_layout.addWidget(self.controls_container)

        # Prompt label when no figure selected ------------------------------
        self.no_fig_prompt = QLabel("No figure selected.\nClick on a figure's border to select one.")
        self.no_fig_prompt.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.no_fig_prompt.setWordWrap(True)
        self.no_fig_prompt.setStyleSheet("font-style: italic; color: gray;")
        parent_layout.addWidget(self.no_fig_prompt)

        # Start with prompt visible, controls hidden until a figure is chosen
        self.controls_container.hide()
        self.no_fig_prompt.show()

        # Widget starts disabled until a figure is selected -----------------
        self._panel_enabled = False  # store internally
        self.set_enabled(False)

    # ------------------------------------------------------------------ Slots
    def _on_type_changed(self, text: str):
        self.stacked_opts.setCurrentIndex(0 if text == "Image" else 1)
        self._validate_inputs()

    def _browse_directory(self):
        start_dir = self.le_directory.text() or os.getcwd()
        
        # Create dialog with theming options
        dialog = QFileDialog(self, "Select Export Directory", start_dir)
        dialog.setFileMode(QFileDialog.FileMode.Directory)
        dialog.setOption(QFileDialog.Option.ShowDirsOnly, True)
        dialog.setOption(QFileDialog.Option.DontUseNativeDialog, True)
        
        # Apply theming
        from PyQt6.QtCore import Qt
        dialog.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        
        try:
            from themes import apply_dialog_theme
            main_win = self.window()
            if hasattr(main_win, 'current_theme_props') and main_win.current_theme_props:
                apply_dialog_theme(dialog, main_win.current_theme_props)
        except Exception as e:
            logger.debug(f"Could not apply dialog theme to file dialog: {e}")
        
        if dialog.exec():
            selected_dirs = dialog.selectedFiles()
            if selected_dirs:
                self.le_directory.setText(selected_dirs[0])

        # bring panel back to front / keep focus
        self.window().activateWindow()
        self.window().raise_()
        self._validate_inputs()

    def _sync_dims(self, _value: int, *, trigger: str):
        """Maintain aspect ratio between width/height and propagate DPI changes.

        The *_value* parameter is required because ``QSpinBox.valueChanged``
        passes the new numeric value.  We do not use it directly because all
        relevant data is obtained from the spin boxes themselves.
        """
        if trigger == "width":
            # Update height using stored aspect ratio
            new_width = self.spin_width.value()
            self.spin_height.blockSignals(True)
            self.spin_height.setValue(int(new_width / self._aspect_ratio))
            self.spin_height.blockSignals(False)
        elif trigger == "height":
            new_height = self.spin_height.value()
            self.spin_width.blockSignals(True)
            self.spin_width.setValue(int(new_height * self._aspect_ratio))
            self.spin_width.blockSignals(False)
        elif trigger == "dpi":
            # Scale width & height proportionally to DPI change
            new_dpi = self.spin_dpi.value()
            factor = new_dpi / self._last_dpi if self._last_dpi else 1.0
            self.spin_width.blockSignals(True)
            self.spin_height.blockSignals(True)
            self.spin_width.setValue(int(self.spin_width.value() * factor))
            self.spin_height.setValue(int(self.spin_height.value() * factor))
            self.spin_width.blockSignals(False)
            self.spin_height.blockSignals(False)
            self._last_dpi = new_dpi

        # Recalculate aspect ratio after each change
        self._aspect_ratio = self.spin_width.value() / max(1.0, self.spin_height.value())

        self._validate_inputs()

    # ------------------------------------------------------------------ Public
    def set_enabled(self, enabled: bool):
        """Show/hide controls & prompt and enable/disable interactive widgets."""
        self._panel_enabled = enabled

        # Visibility toggle ------------------------------------------------
        self.controls_container.setVisible(enabled)
        self.no_fig_prompt.setVisible(not enabled)

        # Enable/disable interactive widgets ------------------------------
        for child in self.controls_container.findChildren((QPushButton, QComboBox, QLineEdit, QSpinBox, QRadioButton)):
            child.setEnabled(enabled)

        self._validate_inputs()

    def update_controls(self, fig_config: Optional[dict], theme_props: dict):
        """Show prompt if *fig_config* is None. Otherwise apply theme and enable controls."""
        self.set_enabled(fig_config is not None)

    # ---------------------------------------------------------------- Validation
    def _validate_inputs(self):
        """Enable/disable export button based on required inputs."""
        if not self._panel_enabled:
            self.btn_export.setEnabled(False)
            return

        dir_ok = bool(self.le_directory.text().strip())
        fname_ok = bool(self.le_filename.text().strip())

        self.btn_export.setEnabled(dir_ok and fname_ok)

    # ---------------------------------------------------------------- Progress
    def _start_progress(self):
        self.progress.setValue(0)
        self.progress.show()
        self._progress_timer = QTimer(self)
        self._progress_timer.timeout.connect(self._advance_progress)
        self._progress_timer.start(50)  # ~1s to fill

    def _advance_progress(self):
        step = 5
        val = self.progress.value() + step
        if val >= 100:
            self.progress.setValue(100)
            self._progress_timer.stop()
            self.progress.hide()
        else:
            self.progress.setValue(val)

    # ---------------------------------------------------------------- Export
    def _emit_request(self):
        if not self.btn_export.isEnabled():
            return

        export_type = "Image" if self.rb_image.isChecked() else "CSV"
        directory = self.le_directory.text() or os.getcwd()
        filename = self.le_filename.text().strip() or "figure"

        req: Dict[str, Any] = {
            "file_type": export_type.lower(),
            "directory": directory,
            "file_name": filename,
        }

        if export_type == "Image":
            req.update(
                {
                    "image_format": self.combo_img_format.currentText().lower(),
                    "dpi": self.spin_dpi.value(),
                    "width": self.spin_width.value(),
                    "height": self.spin_height.value(),
                }
            )
        else:  # CSV
            req.update(
                {
                    "separator": _CSV_SEPARATORS[self.combo_sep.currentText()],
                    "precision": self.spin_precision.value(),
                }
            )

        logger.debug("Export request built: %s", req)

        # Overwrite check ----------------------------------------------------
        if req["file_type"] == "image":
            ext = req["image_format"]
            candidate_path = os.path.join(directory, f"{filename}.{ext}")
        else:
            candidate_path = os.path.join(directory, f"{filename}.csv")

        if os.path.exists(candidate_path):
            # Create custom message box with proper theming
            msg_box = QMessageBox(self)
            msg_box.setWindowTitle("Overwrite File?")
            msg_box.setText(f"File '{candidate_path}' already exists.\nDo you want to replace it?")
            msg_box.setIcon(QMessageBox.Icon.Question)
            msg_box.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            msg_box.setDefaultButton(QMessageBox.StandardButton.No)
            
            # Apply theming
            from PyQt6.QtCore import Qt
            msg_box.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
            
            try:
                from themes import apply_dialog_theme
                main_win = self.window()
                if hasattr(main_win, 'current_theme_props') and main_win.current_theme_props:
                    apply_dialog_theme(msg_box, main_win.current_theme_props)
            except Exception as e:
                logger.debug(f"Could not apply dialog theme to message box: {e}")
            
            resp = msg_box.exec()
            if resp != QMessageBox.StandardButton.Yes:
                return  # user cancelled export

        # Start progress animation
        self._start_progress()

        # Emit request to application
        self.export_requested.emit(req) 