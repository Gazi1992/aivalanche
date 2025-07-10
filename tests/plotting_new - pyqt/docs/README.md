# PyQtGraph Advanced Visualization Tool

A Python-based application for creating dynamic and configurable data visualizations using PyQt6 and PyQtGraph. It features a clean, tabbed header for global and per-figure controls, robust JSON-based configuration, and an extensive theming system.

## Core Features

*   **JSON Configuration:** Define complex multi-figure, multi-plot visualizations through simple JSON files.
*   **Centralized Tabbed Header (`AppHeader`):**
    *   **Global Controls:** Manage application-wide settings like themes.
    *   **Contextual Options:** Apply settings (e.g., grid properties) globally to all figures or specifically to a single selected figure.
*   **Interactive Figure Selection:**
    *   Click on any figure in the display area to select it.
    *   Selected figures are visually highlighted (border style defined by the current theme).
    *   Header controls dynamically update to reflect the state of the selected figure or global defaults.
*   **Modular UI Components:**
    *   `FigureComponent`: Encapsulates individual plot areas, handling data display and interaction.
    *   `AppHeader` & `header_sections/`: Manage the main control interface, with each tab's content delegated to a dedicated widget.
*   **Rich Theming System (`themes.py`):**
    *   Multiple built-in themes (Light, Dark, Solarized, Dracula, GitHub, Nord).
    *   Themes control nearly all visual aspects: window, figure frames (including selection highlight), plot backgrounds/axes, legends, and detailed styling for the header tabs themselves.
    *   Easily switch themes globally via the "Themes" tab.
*   **Data Handling (`data_handler.py`):**
    *   Supports loading data from CSV, Excel (`.xlsx`, `.xls` via `openpyxl`), and JSON files.
    *   Includes a caching mechanism for data sources.
*   **Plotting Capabilities (`plot_handlers.py`):**
    *   Currently supports line and scatter plots.
    *   Extensible for additional plot types.
*   **Configuration Validation & Defaults (`config_loader.py`, `config_schema.py`):**
    *   Ensures configuration files adhere to a defined structure.
    *   Automatically applies sensible defaults for optional fields.
*   **Dynamic Grid Layout (`utils/layout_utils.py`):**
    *   Figures are arranged in a grid.
    *   Supports explicit row/column configuration or automatic calculation for a balanced layout.
*   **Standard Plot Features:** Axis labels, titles, linear/log scales, and legends are configurable per figure.

## Installation

1.  **Clone the Repository:**
    ```bash
    git clone <your-repository-url>
    cd <repository-directory-name>
    ```

2.  **Install Dependencies:**
    It's recommended to use a virtual environment.
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    pip install pyqtgraph pandas numpy PyQt6 openpyxl
    ```
    *   `PyQt6`: For the GUI framework.
    *   `pyqtgraph`: For plotting.
    *   `pandas`: For data manipulation.
    *   `numpy`: Dependency for pandas and pyqtgraph.
    *   `openpyxl`: Required for reading `.xlsx` Excel files.

3.  **Directory Structure:**
    Ensure you have the following directory structure, especially for data and custom components:
    ```
    your_project_root/
    ├── main.py
    ├── app_header.py
    ├── figure_component.py
    ├── ... (other .py files)
    ├── header_sections/
    │   ├── themes_section.py
    │   └── grid_section.py
    ├── data/
    │   ├── configs/
    │   │   └── sample_config.json  # Or your own config
    │   └── your_data_file.csv      # Example data file
    └── utils/
        └── ... (utility .py files)
    ```

## Running the Application

Execute `main.py` from your project's root directory, optionally providing a path to a configuration file:

```bash
python main.py [path/to/your_config.json]
```

If no configuration file path is provided, the application will attempt to load `data/configs/sample_config.json` by default.

## User Interaction

*   **Global Theme Selection:** Use the "Themes" tab in the header to select a theme. This change applies to the entire application.
*   **Figure Interaction:**
    *   **Selection:** Click on any figure to select it. The selected figure will be visually highlighted (e.g., with a colored border, as defined by the theme's `selected_frame_border` and `selected_frame_border_width` properties).
    *   **Deselection:** Click the currently selected figure again to deselect it.
*   **Applying Options (e.g., Grid Settings):**
    *   **To a Selected Figure:** If a figure is selected, changes made in tabs like "Grid" will apply *only* to that specific figure. The controls in the header tab will update to show the current state of the selected figure.
    *   **To All Figures:** If no figure is selected, changes made in tabs like "Grid" will apply to *all* figures simultaneously. The controls in the header tab will typically show default values or a common state if all figures are uniform.

## Configuration (`config.json`)

The application's behavior and appearance are primarily driven by a JSON configuration file.

*   **Top-Level Settings:** Define `app_title`, `theme` (global theme key), and `margins` for the plot display area (these margins are applied *below* the header).
*   **`grid_layout`:** Specify hints for the number of `rows` and `cols` for the figure grid, and `horizontal_spacing`/`vertical_spacing` between figures.
*   **`figures` (Array):** Each object in this array defines a `FigureComponent`.
    *   Common properties: `id`, `title`, `x_label`, `y_label`, `x_scale`, `y_scale`.
    *   Grid properties: `grid_x` (boolean), `grid_y` (boolean), `grid_alpha` (0.0-1.0), `grid_color` (hex string or null to use theme default).
*   **`items` (Array within each `figure` object):** Each object defines a data series (plot) within that figure.
    *   Common properties: `id`, `type` ("line", "scatter"), `source` (data file path), `x_column`, `y_column`, `legend_name`.
    *   Plot-specific styling: e.g., `line_color`, `line_width`, `symbol`, `symbol_size`, etc.

Refer to `config_reference.md` for a comprehensive guide to all available configuration options and their schemas.

## Theming System (`themes.py`)

A key feature is the highly customizable theming system.

*   Themes are Python dictionaries defined in `themes.py`.
*   Each theme dictionary contains an extensive set of keys to control the appearance of:
    *   Main window and general backgrounds (`window_bg`).
    *   Figure frames: `frame_bg`, `frame_border`, `border_radius`, `shadow_color`, etc.
    *   **Selected Figure Highlight:** `selected_frame_border`, `selected_frame_border_width`.
    *   Plot elements: `plot_bg`, `axis_fg` (for axis lines, ticks, labels, and default grid lines), font sizes for titles, labels, ticks, and legends.
    *   **Header Area (`AppHeader`):**
        *   `header_bg`, `header_text_color`.
*   The application loads these properties and applies them dynamically.
*   Changing the global theme via the "Themes" tab will reset any figure-specific interactive overrides (like a custom grid color set via the "Grid" tab) to the new theme's defaults.

## File Structure Overview

```
.
├── main.py                 # Application entry point, main window
├── app_header.py           # Main tabbed header widget
├── figure_component.py     # Widget for a single figure/plot area
├── config_loader.py        # Loads, validates, and applies defaults to config
├── config_schema.py        # Defines the structure of the config JSON
├── data_handler.py         # Handles loading data from files
├── plot_handlers.py        # Functions to create pyqtgraph plot items
├── themes.py               # Contains all theme definitions
├── header_sections/        # Directory for individual tab content widgets
│   ├── __init__.py
│   ├── themes_section.py   # UI for the "Themes" tab
│   └── grid_section.py     # UI for the "Grid" tab
├── utils/                  # Utility modules
│   ├── __init__.py
│   ├── color_utils.py
│   ├── layout_utils.py
│   ├── schema_helpers.py
│   └── validators.py
├── data/                   # Default directory for data and configurations
│   ├── configs/            # Example: sample_config.json
│   └── ...                 # Example: data_file.csv
├── README.md               # This file
└── config_reference.md     # Detailed documentation of config.json structure
```

## Extending the Tool

### Adding New Themes

1.  Open `themes.py`.
2.  Define a new Python dictionary for your theme. Ensure you provide values for all keys used by the application, including general appearance, figure styling, selected figure highlights, and all `tab_*` keys for header styling. Refer to existing themes as a template.
3.  Add your new theme dictionary to the `AVAILABLE_THEMES` registry with a unique string key.
4.  The new theme will now be available in the "Themes" tab and can be set in `config.json`.

### Adding New Header Tabs & Options

1.  **Create Section Widget:** In the `header_sections/` directory, create a new Python file for your tab's UI (e.g., `axis_controls_section.py`). Define a `QWidget` subclass with the necessary controls (checkboxes, sliders, color pickers, etc.).
2.  **Define Signals:** In your new section widget, define `pyqtSignal`s for each interactive option that should affect the plots (e.g., `xAxisMinChanged = pyqtSignal(float)`).
3.  **Integrate into `AppHeader`:**
    *   In `app_header.py`, import your new section widget.
    *   Instantiate it in `AppHeader.__init__`.
    *   Add it as a new tab to `self.tab_widget` (e.g., `self.tab_widget.addTab(self.axis_controls_section, "Axes")`).
    *   In `AppHeader.apply_styling`, call an `apply_styling` method (that you'll add to your section widget) to ensure its controls are themed.
    *   In `AppHeader.update_controls`, call an `update_controls` method on your section widget to set its control states based on the selected figure's config or global defaults.
4.  **Handle in `VisualizationApp` (`main.py`):**
    *   Connect the signals from your new section instance (accessed via `self.app_header.your_section_instance.your_signal`) to new slot methods in `VisualizationApp`.
    *   Implement these new slot methods. They should typically use `self._apply_option_to_figures(option_key, value, update_method_name)` to:
        *   Update the corresponding key in the `figure_config` of the target figure(s).
        *   Call an appropriate method on the `FigureComponent`(s) to visually apply the change.
5.  **Update `FigureComponent`:**
    *   If necessary, add new methods to `FigureComponent` that directly apply the visual changes for the new options (e.g., `def set_x_axis_min(self, min_val): ...`). These methods should also update `self.figure_config`.
6.  **Update Configuration Schema:** If your new options require corresponding entries in `config.json` (e.g., for initial values), update `config_schema.py` and document them in `config_reference.md`.

### Adding New Plot Types

1.  **Create Handler:** In `plot_handlers.py`, add a new function that takes an item configuration dictionary and data, and returns a configured `pyqtgraph` graphics object (e.g., `BarPlotItem`).
2.  **Define Schema:** In `config_schema.py`, define a new schema dictionary for your plot type's specific configuration options (e.g., `BAR_PLOT_SCHEMA`). Add this schema to `SchemaRegistry.PLOT_TYPE_SCHEMAS` with a unique type key (e.g., `"bar"`).
3.  **Register Handler:** In `figure_component.py`, import your new handler and add it to the `self.plot_handlers_map` dictionary.

### Adding New Data Sources

1.  Modify the `load_data` method in `data_handler.py` to recognize and parse the new file format. Document any new library dependencies.
