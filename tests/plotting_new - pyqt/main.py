# --- START OF FILE main.py ---
import sys
import os
import logging
from typing import Dict, Optional, Any

from PyQt6 import QtWidgets
from PyQt6.QtWidgets import ( QApplication, QMainWindow, QWidget, QVBoxLayout,
                              QGridLayout, QLabel, QMessageBox, QHBoxLayout )
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor

import pyqtgraph as pg

from config_loader import ConfigLoader
from data_handler import DataHandler
from figure_component import FigureComponent
from sidebar import Sidebar
from utils.layout_utils import determine_grid_dimensions
import themes
from utils.message_utils import show_critical, show_error, show_warning

# Logging Setup
def setup_logging():
    log_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    root_logger = logging.getLogger()
    if not root_logger.hasHandlers():
        log_handler = logging.StreamHandler(sys.stdout)
        log_handler.setFormatter(log_formatter)
        root_logger.addHandler(log_handler)
    root_logger.setLevel(logging.DEBUG)

setup_logging()

logger = logging.getLogger(__name__)

# -----------------------------------------------------------------------------
# Centralised user-facing message helpers
# -----------------------------------------------------------------------------

class VisualizationApp(QtWidgets.QMainWindow):
    def __init__(self, config_file: str):
        super().__init__()
        self.config_file = config_file
        self.config_loader: Optional[ConfigLoader] = None
        self.data_handler: Optional[DataHandler] = None
        self.figure_components: Dict[str, FigureComponent] = {}
        self.app_header: Optional[Sidebar] = None
        self.main_grid_layout: Optional[QGridLayout] = None
        self.plot_area_widget: Optional[QWidget] = None
        self.selected_figure_id: Optional[str] = None
        self.current_theme_props: Optional[Dict[str, Any]] = None

        try:
            logger.info(f"Initializing Application with config: {os.path.basename(config_file)}")
            if not self._load_and_validate_config():
                # Error messages are handled inside the method
                sys.exit(1)

            self.data_handler = DataHandler()
            self.setup_ui()
            self.create_figure_components()
            self.apply_theme()
            self._connect_signals()

        except Exception as e:
            msg = f"A critical error occurred during initialization:\n{e}\n\nPlease check the logs."
            show_critical("Application Error", msg, exc=e)
            sys.exit(1)

    def _load_and_validate_config(self) -> bool:
        self.config_loader = ConfigLoader(self.config_file)
        if not self.config_loader.config:
             msg = f"Configuration loading failed for {self.config_file}.\nApplication cannot start."
             show_critical("Config Error", msg)
             return False

        self.config_loader.apply_defaults()

        current_config_theme = self.config_loader.get_theme()
        if current_config_theme not in themes.AVAILABLE_THEMES:
            logger.warning(
                f"Theme '{current_config_theme}' from config.json is not defined. "
                f"Falling back to default: '{themes.DEFAULT_THEME_KEY}'."
            )
            self.config_loader.set_theme(themes.DEFAULT_THEME_KEY)

        if not self.config_loader.validate_config():
            errors = self.config_loader.get_validation_errors()
            error_str = "\n".join(errors)
            msg = f"Configuration validation failed:\n{error_str}\n\nApplication might not behave as expected."
            show_error("Config Validation Error", msg)
        return True

    def _connect_signals(self):
        if not self.app_header:
            logger.error("Sidebar not initialized, cannot connect signals.")
            return

        connections = {
            'theme_selected': self.on_theme_changed_by_key,
            'grid_x_visibility_changed': self.on_header_grid_x_visibility_changed,
            'grid_y_visibility_changed': self.on_header_grid_y_visibility_changed,
            'grid_color_changed': self.on_header_grid_color_changed,
            'grid_opacity_changed': self.on_header_grid_opacity_changed,
            'title_changed': self.on_header_title_changed,
            'x_label_changed': self.on_header_x_label_changed,
            'y_label_changed': self.on_header_y_label_changed,
            'export_requested': self.on_export_requested,
        }

        for signal_name, slot in connections.items():
            signal = getattr(self.app_header, signal_name, None)
            if signal:
                signal.connect(slot)
            else:
                logger.warning(f"Sidebar does not have '{signal_name}' signal.")

    def setup_ui(self):
        if not self.config_loader:
            logger.critical("Cannot setup UI: ConfigLoader not initialized.")
            return

        try:
            # Setup main window properties
            app_title = self.config_loader.get_app_title()
            self.setWindowTitle(app_title)
            # Set maximized state before any showing
            self.setWindowState(Qt.WindowState.WindowMaximized)

            # Setup main layout
            self.overall_central_widget = QWidget()
            self.setCentralWidget(self.overall_central_widget)
            self.overall_central_widget.setAutoFillBackground(True)

            main_h_layout = QHBoxLayout(self.overall_central_widget)
            main_h_layout.setContentsMargins(0, 0, 0, 0)
            main_h_layout.setSpacing(0)

            # Add sidebar
            self.app_header = Sidebar(parent=self.overall_central_widget)
            main_h_layout.addWidget(self.app_header)

            # Setup plot area
            margins_config = self.config_loader.get_margins()
            grid_layout_config = self.config_loader.get_grid_layout()
            h_spacing_grid = grid_layout_config.get('horizontal_spacing', 10)
            v_spacing_grid = grid_layout_config.get('vertical_spacing', 10)

            self.plot_area_widget = QWidget(objectName="PlotAreaWidget")
            main_h_layout.addWidget(self.plot_area_widget, 1)

            self.main_grid_layout = QGridLayout(self.plot_area_widget)
            self.main_grid_layout.setContentsMargins(
                margins_config['left'], margins_config['top'],
                margins_config['right'], margins_config['bottom']
            )
            self.main_grid_layout.setHorizontalSpacing(int(h_spacing_grid))
            self.main_grid_layout.setVerticalSpacing(int(v_spacing_grid))

        except KeyError as e:
            msg = f"Missing configuration for UI: {e}"
            show_error("UI Setup Error", msg, exc=e)
            self.main_grid_layout = None
        except Exception as e:
            msg = f"An error occurred during UI setup: {e}"
            show_error("UI Setup Error", msg, exc=e)
            self.main_grid_layout = None

    def _handle_figure_selection(self, clicked_fig_id: str):
        if self.selected_figure_id == clicked_fig_id:
            self.selected_figure_id = None
            logger.info(f"Figure '{clicked_fig_id}' deselected. Options will apply to all figures.")
        else:
            self.selected_figure_id = clicked_fig_id
            logger.info(f"Figure '{self.selected_figure_id}' selected.")

        for fig_id, component in self.figure_components.items():
            if component:
                component.set_selected(fig_id == self.selected_figure_id)

        selected_fig_conf = None
        if self.selected_figure_id:
            selected_component = self.figure_components.get(self.selected_figure_id)
            if selected_component:
                selected_fig_conf = selected_component.figure_config

        if self.app_header and self.current_theme_props:
            self.app_header.update_controls(selected_fig_conf, self.current_theme_props)

    def on_theme_changed_by_key(self, new_theme_key: str):
        if not self.config_loader:
            logger.error("ConfigLoader not available in on_theme_changed_by_key.")
            return
        if not new_theme_key:
            logger.error("Received empty theme key from Sidebar.")
            return

        current_theme_key = self.config_loader.get_theme()
        if new_theme_key != current_theme_key:
            logger.info(f"Global theme changed to: {new_theme_key} via UI (Sidebar).")
            self.config_loader.set_theme(new_theme_key)

            logger.info("Resetting all component style overrides before applying new global theme.")
            for component in self.figure_components.values():
                if component and hasattr(component, 'reset_style_overrides_to_theme'):
                   try: component.reset_style_overrides_to_theme()
                   except Exception as e:
                       logger.error(f"Error resetting overrides for component {component.figure_id}: {e}", exc_info=True)
            self.apply_theme()
        else:
            logger.debug(f"Theme selection '{new_theme_key}' is already active.")

    def apply_theme(self):
        if not self.config_loader:
            logger.error("ConfigLoader not available in apply_theme.")
            return

        current_theme_key = self.config_loader.get_theme()
        self.current_theme_props = themes.get_theme_config(current_theme_key)

        if not self.current_theme_props:
            logger.error(f"Failed to load theme properties for key: {current_theme_key}. Cannot apply theme.")
            return

        logger.info(f"Applying global theme: {self.current_theme_props.get('name', current_theme_key)}")

        pg.setConfigOption('background', self.current_theme_props['plot_bg'])
        pg.setConfigOption('foreground', self.current_theme_props['axis_fg'])

        if self.app_header:
            self.app_header.update_logo_color(self.current_theme_props)
            self.app_header.set_current_theme_in_controls(current_theme_key)

        for fig_id, component in self.figure_components.items():
             if component:
                 try: component.apply_theme(self.current_theme_props)
                 except Exception as e:
                      logger.error(f"Error applying theme to component {fig_id}: {e}", exc_info=True)
             else:
                logger.warning(f"Found None component for ID {fig_id} during theme application.")

        # NEW: apply global stylesheet ------------------------------------------------
        try:
            q_app = QtWidgets.QApplication.instance()
            if q_app:
                stylesheet = themes.build_stylesheet(self.current_theme_props)
                q_app.setStyleSheet(stylesheet)
        except Exception as e:
            logger.error(f"Failed to build/apply stylesheet: {e}", exc_info=True)

        # Update header controls only if a single figure is selected; otherwise
        # keep the user's current multi-figure control state intact.
        if (
            self.app_header
            and self.current_theme_props
            and self.selected_figure_id
            and self.selected_figure_id in self.figure_components
        ):
            current_fig_conf_for_header = self.figure_components[self.selected_figure_id].figure_config
            self.app_header.update_controls(current_fig_conf_for_header, self.current_theme_props)

    def create_figure_components(self):
       if not self.config_loader or not self.data_handler:
            logger.critical("Cannot create figure components: ConfigLoader or DataHandler not ready.")
            return
       if self.main_grid_layout is None:
            logger.critical("Cannot create figure components: Main grid layout (self.main_grid_layout) is None.")
            if self.plot_area_widget and self.plot_area_widget.layout() is None:
                # If the main grid layout failed, we can't add plots. Show an error in the plot area.
                error_layout = QVBoxLayout(self.plot_area_widget)
                error_label = QLabel("Error: Plot grid could not be initialized.")
                error_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                error_layout.addWidget(error_label)
            return

       figures = self.config_loader.get_figures()
       num_figures = len(figures)
       if num_figures == 0:
            logger.warning("No figures found in configuration.")
            self.main_grid_layout.addWidget(QLabel("No figures defined in configuration."), 0, 0, alignment=Qt.AlignmentFlag.AlignCenter)
            return

       grid_config = self.config_loader.get_grid_layout()
       rows, cols = determine_grid_dimensions(num_figures, grid_config)

       if rows <= 0 or cols <= 0:
            logger.error(f"Invalid grid dimensions ({rows}x{cols}) for {num_figures} figures. Defaulting to 1x{num_figures}.")
            rows = 1; cols = num_figures

       figures_added_count = 0
       for i, figure_config_item in enumerate(figures):
           if not isinstance(figure_config_item, dict):
               logger.warning(f"Figure config at index {i} is not a dictionary. Skipping.")
               continue
           figure_id = figure_config_item.get('id')
           if not figure_id:
               logger.error(f"Skipping figure config at index {i}: Missing 'id'.")
               continue
           if figures_added_count >= rows * cols:
               logger.warning(f"Figure '{figure_id}' (index {i}) skipped: Exceeds grid capacity ({rows}x{cols}).")
               continue

           figure_comp = None
           try:
               figure_comp = FigureComponent(
                   figure_id=figure_id,
                   figure_config=figure_config_item,
                   data_handler=self.data_handler,
                   parent=self.plot_area_widget
               )
               figure_comp.figure_clicked.connect(self._handle_figure_selection)

               if figure_comp.getPlotWidget() is None:
                    logger.error(f"Component '{figure_id}' failed internal PlotWidget setup. Skipping add.")
                    if figure_comp: figure_comp.deleteLater()
                    continue
           except Exception as e:
               logger.error(f"Failed to instantiate FigureComponent '{figure_id}': {e}", exc_info=True)
               if figure_comp: figure_comp.deleteLater()
               error_label = QLabel(f"Error loading figure '{figure_id}'")
               error_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
               self.main_grid_layout.addWidget(error_label, figures_added_count // cols, figures_added_count % cols)
               figures_added_count +=1
               continue

           self.figure_components[figure_id] = figure_comp
           row_idx = figures_added_count // cols
           col_idx = figures_added_count % cols
           self.main_grid_layout.addWidget(figure_comp, row_idx, col_idx)
           figures_added_count += 1
           logger.info(f"Added FigureComponent '{figure_id}' to grid at ({row_idx}, {col_idx}).")

       if figures_added_count > 0:
            actual_rows_used = (figures_added_count + cols - 1) // cols
            for r_idx in range(actual_rows_used): self.main_grid_layout.setRowStretch(r_idx, 1)
            for c_idx in range(cols): self.main_grid_layout.setColumnStretch(c_idx, 1)
            for r_idx_unused in range(actual_rows_used, rows):
                 self.main_grid_layout.setRowStretch(r_idx_unused, 0)
       elif num_figures > 0 :
           logger.warning("No figure components successfully created, despite figures being defined.")
           self.main_grid_layout.addWidget(QLabel("No figures could be displayed. Check logs."), 0,0, alignment=Qt.AlignmentFlag.AlignCenter)

    def _apply_option_to_figures(self, option_key: str, value: Any, update_method_name: str):
        target_components: list[FigureComponent] = []
        target_description = ""

        if self.selected_figure_id and self.selected_figure_id in self.figure_components:
            component = self.figure_components[self.selected_figure_id]
            if component:
                target_components.append(component)
                target_description = f"selected figure '{self.selected_figure_id}'"
        else:
            target_components.extend(c for c in self.figure_components.values() if c)
            target_description = "all figures"

        if not target_components:
            logger.warning(f"No target figures found to apply option '{option_key}'.")
            return

        logger.info(f"Applying '{option_key}' = {value} to {target_description}.")

        for fig_comp in target_components:
            fig_comp.figure_config[option_key] = value # Update the component's internal config

            update_method = getattr(fig_comp, update_method_name, None)
            if update_method and callable(update_method):
                if option_key == 'grid_color': # Special case: on_grid_color_changed expects QColor
                    q_value = QColor(value) if isinstance(value, str) else value # Ensure QColor
                    update_method(q_value)
                else:
                    update_method(value)
            else:
                logger.warning(f"No specific update method '{update_method_name}' found on FigureComponent '{fig_comp.figure_id}'. Re-applying theme.")
                if self.current_theme_props:
                    fig_comp.apply_theme(self.current_theme_props)

        # Update header controls only if a single figure is selected; otherwise
        # keep the user's current multi-figure control state intact.
        if (
            self.app_header
            and self.current_theme_props
            and self.selected_figure_id
            and self.selected_figure_id in self.figure_components
        ):
            current_fig_conf_for_header = self.figure_components[self.selected_figure_id].figure_config
            self.app_header.update_controls(current_fig_conf_for_header, self.current_theme_props)

    def on_header_grid_x_visibility_changed(self, visible: bool):
        self._apply_option_to_figures('grid_x', visible, 'on_grid_x_visibility_changed')

    def on_header_grid_y_visibility_changed(self, visible: bool):
        self._apply_option_to_figures('grid_y', visible, 'on_grid_y_visibility_changed')

    def on_header_grid_color_changed(self, color: QColor):
        # Store as hex string in config, but pass QColor to component's slot
        self._apply_option_to_figures('grid_color', color.name(QColor.NameFormat.HexArgb), 'on_grid_color_changed')

    def on_header_grid_opacity_changed(self, opacity: float):
        self._apply_option_to_figures('grid_alpha', opacity, 'on_grid_opacity_changed')

    def on_header_title_changed(self, title: str):
        self._apply_option_to_figures('title', title, 'on_title_changed')

    def on_header_x_label_changed(self, label: str):
        self._apply_option_to_figures('x_label', label, 'on_x_label_changed')

    def on_header_y_label_changed(self, label: str):
        self._apply_option_to_figures('y_label', label, 'on_y_label_changed')

    def on_export_requested(self, export_request: dict):
        """Handle export requests coming from the header options panel.

        The *export_request* dict carries all parameters assembled in
        ``ExportSectionWidget``.  If no figure is selected, the method logs a
        warning and returns silently.
        """
        if not self.selected_figure_id or self.selected_figure_id not in self.figure_components:
            logger.warning("Export requested but no figure is selected.")
            return

        fig_comp = self.figure_components[self.selected_figure_id]

        try:
            fig_comp.export(export_request)
        except Exception as e:
            logger.error(
                "Failed exporting figure %s with params %s: %s",
                self.selected_figure_id,
                export_request,
                e,
                exc_info=True,
            )
            fmt_readable = export_request.get("image_format", export_request.get("file_type", "")).upper()
            show_error("Export Error", f"Failed to export figure to {fmt_readable}: {e}")

def main():
    app = QApplication(sys.argv)
    pg.setConfigOptions(antialias=True)

    try:
        if len(sys.argv) < 2:
            script_dir = os.path.dirname(os.path.abspath(__file__))
            default_config_path = os.path.join(script_dir, "data", "configs", "sample_config.json")
            # default_config_path = os.path.join(script_dir, "data", "configs", "avg_temp_config.json")
            if not os.path.exists(default_config_path):
                 msg = f"Default configuration file not found:\n{default_config_path}\nPlease provide a config file path."
                 show_critical("Config Error", msg)
                 sys.exit(1)
            config_file = default_config_path
            logger.info(f"No config file specified. Using default: {config_file}")
        else:
            config_file = sys.argv[1]
            if not os.path.exists(config_file):
                 msg = f"Specified configuration file not found:\n{config_file}"
                 show_critical("Config Error", msg)
                 sys.exit(1)

        window = VisualizationApp(config_file)
        window.show()

        logger.info("Starting application event loop...")
        exit_code = app.exec()
        logger.info(f"Application finished with exit code {exit_code}.")
        sys.exit(exit_code)

    except ImportError as e:
        msg = (
            f"ImportError: {e}. Please ensure all dependencies are installed "
            "(e.g., pip install pyqtgraph pandas numpy PyQt6 openpyxl)."
        )
        show_critical("Import Error", msg, exc=e)
        sys.exit(1)
    except SystemExit:
        raise
    except Exception as e:
        msg = f"An unexpected error occurred:\n{e}\n\nPlease check the logs for details."
        show_critical("Unhandled Error", msg, exc=e)
        sys.exit(1)

if __name__ == "__main__":
    main()
# --- END OF FILE main.py ---
