# main_app.py
import sys
import json # Import json module
import os   # Import os for path joining
import pandas as pd # Import pandas for reading CSV
import numpy as np
import pyqtgraph as pg
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QGridLayout,
                             QVBoxLayout, QComboBox, QLabel, QHBoxLayout, QMessageBox) # Added QMessageBox
# Or PyQt5.QtWidgets

from plot_types import line_plot # Only line plots for now
# from utils import sample_data # No longer needed for hardcoded data
from themes import THEMES, apply_theme
from plot_container import PlotContainer

# --- Configuration ---
CONFIG_FILE = "config.json" # Name of the configuration file
DEFAULT_COLUMNS = 2 # Number of columns for the grid layout

class PlottingWindow(QMainWindow):
    def __init__(self, initial_theme_name="Classic Dark", plot_config=None):
        super().__init__()
        self.current_theme_name = initial_theme_name # Global theme
        self.plot_config = plot_config if plot_config else [] # Store loaded config
        self.setWindowTitle(f"Generic Data Plotter")
        self.setGeometry(100, 100, 1200, 900)

        # --- Central Widget and Main Layout ---
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QVBoxLayout(self.central_widget)
        self.main_layout.setContentsMargins(5, 5, 5, 5)
        self.main_layout.setSpacing(10)

        # --- Create Global Header Controls (Theme Selector) ---
        self._create_global_header_controls()

        # --- Create Plot Grid Layout (nested inside main_layout) ---
        self.grid_layout = QGridLayout()
        self.grid_layout.setSpacing(10)
        self.main_layout.addLayout(self.grid_layout)

        # Keep track of PlotContainer instances
        self.plot_containers = []

        # --- Add Initial Plots based on config ---
        self._create_plots_from_config() # Renamed method

    # _create_global_header_controls remains the same as before...
    def _create_global_header_controls(self):
        global_theme_layout = QHBoxLayout()
        global_theme_layout.addWidget(QLabel("Global Theme:"))
        self.global_theme_combo_box = QComboBox()
        self.global_theme_combo_box.setToolTip("Select the theme for all plots (applied on creation/global change)")
        for theme_name in THEMES.keys():
            self.global_theme_combo_box.addItem(theme_name)
        self.global_theme_combo_box.setCurrentText(self.current_theme_name)
        self.global_theme_combo_box.currentTextChanged.connect(self._handle_global_theme_change)
        global_theme_layout.addWidget(self.global_theme_combo_box)
        global_theme_layout.addStretch(1)
        self.main_layout.addLayout(global_theme_layout)

    # _handle_global_theme_change remains the same (triggers recreation)...
    def _handle_global_theme_change(self, theme_name):
        if theme_name and theme_name != self.current_theme_name:
            print(f"Global Theme Change: Switching to: {theme_name}")
            apply_theme(theme_name)
            self.current_theme_name = theme_name
            self._update_plots_for_theme() # Recreate plots

    # _clear_grid_layout remains the same...
    def _clear_grid_layout(self):
        print("Clearing existing plot containers...")
        for container in self.plot_containers:
            self.grid_layout.removeWidget(container)
            container.deleteLater()
        self.plot_containers = []

    # _update_plots_for_theme remains the same (calls recreation)...
    def _update_plots_for_theme(self):
        self._clear_grid_layout()
        self._create_plots_from_config() # Call the config-based creation method
        print("Plot containers recreated with new global theme.")


    def _create_plots_from_config(self):
        """Creates PlotContainers based on the loaded self.plot_config."""

        print(f"Creating plots from config with global theme: {self.current_theme_name}")

        if self.plot_containers:
             self._clear_grid_layout()

        if not self.plot_config:
            print("Warning: No plot configuration loaded.")
            # Maybe show a message to the user?
            return

        for idx, plot_def in enumerate(self.plot_config):
            try:
                # Determine grid position (simple wrapping layout)
                row = idx // DEFAULT_COLUMNS
                col = idx % DEFAULT_COLUMNS

                # Get plot-specific details
                title = plot_def.get("title", f"Plot {idx+1}")
                # Use global theme if local isn't specified, otherwise use local
                local_theme = plot_def.get("local_theme", self.current_theme_name)
                if local_theme not in THEMES:
                    print(f"Warning: Invalid local_theme '{local_theme}' for '{title}'. Using global '{self.current_theme_name}'.")
                    local_theme = self.current_theme_name

                # Create the container
                container = PlotContainer(initial_theme_name=local_theme)
                container.setTitle(title)

                has_legend_items = False
                # Iterate through traces (lines) defined for this plot
                for trace_def in plot_def.get("traces", []):
                    if trace_def.get("type") == "line": # Check type
                        # --- Load Data ---
                        data_source = trace_def.get("data_source", {})
                        csv_path = data_source.get("csv_path")
                        x_col = data_source.get("x_col")
                        y_col = data_source.get("y_col")

                        if not all([csv_path, x_col, y_col]):
                            print(f"Error: Missing csv_path, x_col, or y_col for a trace in '{title}'. Skipping trace.")
                            continue

                        try:
                            # Construct full path if relative
                            if not os.path.isabs(csv_path):
                                base_path = os.path.dirname(__file__) # Get script's directory
                                csv_path = os.path.join(base_path, csv_path)

                            df = pd.read_csv(csv_path)
                            x_data = df[x_col].to_numpy()
                            y_data = df[y_col].to_numpy()
                        except FileNotFoundError:
                            print(f"Error: CSV file not found: '{csv_path}' for plot '{title}'. Skipping trace.")
                            QMessageBox.warning(self, "File Not Found", f"Could not find data file:\n{csv_path}\n\nFor plot: {title}")
                            continue # Skip this trace
                        except KeyError as e:
                            print(f"Error: Column '{e}' not found in '{csv_path}' for plot '{title}'. Skipping trace.")
                            QMessageBox.warning(self, "Column Not Found", f"Column '{e}' not found in:\n{csv_path}\n\nFor plot: {title}")
                            continue # Skip this trace
                        except Exception as e:
                             print(f"Error loading data for '{title}' from '{csv_path}': {e}. Skipping trace.")
                             QMessageBox.critical(self, "Data Load Error", f"Error loading data for '{title}':\n{e}\n\nFile: {csv_path}")
                             continue # Skip this trace


                        # --- Get Style ---
                        style = trace_def.get("style", {})
                        name = style.get("name", f"Trace {idx+1}")
                        color = style.get("color", 'b') # Default blue
                        width = style.get("width", 1)
                        line_style = style.get("line_style", "SolidLine")

                        # --- Add Plot Item ---
                        container.add_plot_item(
                            line_plot.add_line_plot, # Pass the function
                            x_data,                  # Pass data and style args
                            y_data,
                            name=name,
                            color=color,
                            width=width,
                            style_str=line_style     # Pass the string style
                        )
                        if name: # Only add legend if items have names
                            has_legend_items = True
                    else:
                        print(f"Warning: Unsupported trace type '{trace_def.get('type')}' in '{title}'. Skipping.")


                # Add legend only if there were named items
                if has_legend_items:
                    container.addLegend()
                container.showGrid(x=True, y=True)

                # Add the fully configured container to the grid
                self.grid_layout.addWidget(container, row, col)
                self.plot_containers.append(container)

            except Exception as e:
                print(f"Error creating plot container for definition {idx}: {e}")
                # Optionally show a critical error message to the user
                QMessageBox.critical(self, "Plot Creation Error", f"Failed to create plot {idx+1} defined in configuration:\n{e}")


if __name__ == "__main__":
    # --- Load Configuration from JSON ---
    config_data = None
    try:
        # Construct full path if relative
        config_path = CONFIG_FILE
        if not os.path.isabs(config_path):
            base_path = os.path.dirname(__file__) # Get script's directory
            config_path = os.path.join(base_path, config_path)

        with open(config_path, 'r') as f:
            config_data = json.load(f)
        print(f"Successfully loaded configuration from: {config_path}")
    except FileNotFoundError:
        print(f"Error: Configuration file '{CONFIG_FILE}' not found at expected location: {config_path}")
        # Exit or show error dialog? For now, let it proceed with empty config.
        config_data = [] # Proceed with empty config
        # Alternatively:
        # app_temp = QApplication(sys.argv) # Need app for message box
        # QMessageBox.critical(None, "Config Error", f"Configuration file not found:\n{config_path}")
        # sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"Error: Failed to parse JSON configuration file '{CONFIG_FILE}': {e}")
        config_data = []
        # app_temp = QApplication(sys.argv)
        # QMessageBox.critical(None, "Config Error", f"Error parsing configuration file:\n{e}\n\nFile: {config_path}")
        # sys.exit(1)
    except Exception as e:
        print(f"An unexpected error occurred loading configuration: {e}")
        config_data = []
        # Potentially show error and exit

    # --- Choose and Apply Initial Global Theme ---
    # Could potentially get default theme from config file too
    initial_theme = "Classic Light"
    apply_theme(initial_theme)
    # -----------------------------------

    app = QApplication(sys.argv)
    # Pass the loaded configuration data to the window
    main_window = PlottingWindow(initial_theme_name=initial_theme, plot_config=config_data)
    main_window.show()
    sys.exit(app.exec())
