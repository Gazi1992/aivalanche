**Objective:**

Define the precise structure, fields, data types, and allowed values for the `config.json` file required by the visualization application. Use this specification to generate a `config.json` file based on user requirements for plots and overall appearance.

**`config.json` Specification:**

The configuration is a single JSON object with the following top-level keys:

**1. Top-Level Keys:**

*   `"app_title"`:
    *   **Purpose:** Sets the main window title text.
    *   **Type:** String
    *   **Required:** No
    *   **Default:** "Visualization Tool" (applied by the application)

*   `"theme"`:
    *   **Purpose:** Selects the visual theme for the entire application (window, plots, controls). Changing the theme via the UI resets figure-specific style overrides (like custom grid colors) back to the new theme's defaults.
    *   **Type:** String
    *   **Required:** No
    *   **Default:** "light" (applied by the application, corresponds to 'Default Light' theme)
    *   **Allowed Values:** Must be one of the following exact strings:
        *   `"light"` (Default Light theme)
        *   `"dark"` (Default Dark theme)
        *   `"solarized_light"`
        *   `"solarized_dark"`
        *   `"dracula"`
        *   `"github_light"`
        *   `"nord_dark"`

*   `"left_margin"`, `"right_margin"`, `"top_margin"`, `"bottom_margin"`:
    *   **Purpose:** Defines padding (in pixels) around the main content area within the window.
    *   **Type:** Number (Integer or Float)
    *   **Required:** No
    *   **Default:** 10 (applied by the application)
    *   **Constraints:** Must be non-negative (>= 0).

*   `"grid_layout"`:
    *   **Purpose:** Contains optional settings for arranging the plot figures in a grid.
    *   **Type:** Object
    *   **Required:** No (If omitted, default spacing is used, and grid dimensions are calculated automatically).

*   `"figures"`:
    *   **Purpose:** Contains the definitions for all the plot figures to be displayed.
    *   **Type:** Array (of Figure Objects)
    *   **Required:** Yes (Must contain at least one Figure Object to display anything).

**2. `"grid_layout"` Object Keys:**

*   `"rows"`:
    *   **Purpose:** Hint for the desired number of rows in the figure grid.
    *   **Type:** Integer or `null`
    *   **Required:** No
    *   **Default:** `null` (Application calculates automatically)
    *   **Constraints:** Must be positive (> 0) if specified as an integer.

*   `"cols"`:
    *   **Purpose:** Hint for the desired number of columns in the figure grid.
    *   **Type:** Integer or `null`
    *   **Required:** No
    *   **Default:** `null` (Application calculates automatically)
    *   **Constraints:** Must be positive (> 0) if specified as an integer.
    *   **Note:** If both `rows` and `cols` are `null`, a balanced grid is calculated. If only one is specified, the other is calculated. If both are specified, they are used only if the total cells (`rows * cols`) are sufficient for the number of figures defined.

*   `"horizontal_spacing"`:
    *   **Purpose:** Space in pixels *between* adjacent figure frames horizontally.
    *   **Type:** Number (Integer or Float)
    *   **Required:** No
    *   **Default:** 10 (applied by the application)
    *   **Constraints:** Must be non-negative (>= 0).

*   `"vertical_spacing"`:
    *   **Purpose:** Space in pixels *between* adjacent figure frames vertically.
    *   **Type:** Number (Integer or Float)
    *   **Required:** No
    *   **Default:** 10 (applied by the application)
    *   **Constraints:** Must be non-negative (>= 0).

**3. Figure Object Keys (within `"figures"` Array):**

*   `"id"`:
    *   **Purpose:** A unique identifier string for this figure.
    *   **Type:** String
    *   **Required:** Yes

*   `"title"`:
    *   **Purpose:** Text displayed as the title above the plot area. Theme controls appearance.
    *   **Type:** String
    *   **Required:** No
    *   **Default:** "" (empty string)

*   `"x_label"`, `"y_label"`:
    *   **Purpose:** Text displayed on the bottom (X) and left (Y) axes. Theme controls text appearance (`axis_fg` color, font size).
    *   **Type:** String
    *   **Required:** No
    *   **Default:** "" (empty string)

*   `"x_scale"`, `"y_scale"`:
    *   **Purpose:** Sets the scale type for the respective axis. (UI control planned for future "Axis" menu section).
    *   **Type:** String
    *   **Required:** No
    *   **Default:** "linear"
    *   **Allowed Values:** `"linear"`, `"log"`

*   `"grid_x"`:
    *   **Purpose:** Sets the initial visibility state of the vertical grid lines. Controlled by a checkbox in the 'Grid' section of the hover menu.
    *   **Type:** Boolean
    *   **Required:** No
    *   **Default:** `true` (applied by the application)

*   `"grid_y"`:
    *   **Purpose:** Sets the initial visibility state of the horizontal grid lines. Controlled by a checkbox in the 'Grid' section of the hover menu.
    *   **Type:** Boolean
    *   **Required:** No
    *   **Default:** `true` (applied by the application)

*   `"grid_alpha"`:
    *   **Purpose:** Sets the transparency of grid lines (0.0 = fully transparent, 1.0 = fully opaque). Controlled by a slider in the 'Grid' section of the hover menu.
    *   **Type:** Number (Float or Integer 0/1)
    *   **Required:** No
    *   **Default:** 0.3
    *   **Constraints:** Value must be between 0.0 and 1.0 inclusive.

*   `"grid_color"`: (**NEW**)
    *   **Purpose:** Overrides the theme's default color for the axis lines, tick marks, and grid lines associated with this figure. Controlled by a color picker in the 'Grid' section of the hover menu. If `null`, the theme's `axis_fg` color is used. Changing the global theme resets this override.
    *   **Type:** String (Hex Color format: `#RGB`, `#RRGGBB`, `#RRGGBBAA`) or `null`
    *   **Required:** No
    *   **Default:** `null`

*   `"items"`:
    *   **Purpose:** Contains the definitions for individual data series (plots) within this figure.
    *   **Type:** Array (of Plot Item Objects)
    *   **Required:** Yes (Must contain at least one Plot Item Object).

**4. Plot Item Object Keys (within `"items"` Array):**

*   **Common Fields:**
    *   `"id"`: (Required String) Unique identifier for this plot item within the figure.
    *   `"type"`: (Required String) Specifies the plot type.
        *   **Allowed Values:** `"line"`, `"scatter"`, `"histogram"`, `"bar"`
    *   `"source"`: (Required String) File path (relative or absolute) to the data source (CSV, XLSX, JSON).
    *   `"x_column"`, `"y_column"`: (Required String) Exact, case-sensitive name of the column in the source file to use for X-axis and Y-axis data respectively.
    *   `"legend_name"`: (Optional String or `null`, Default: `null`) Text for the legend entry for this item. If `null`, excluded from legend. Theme controls legend text appearance.

*   **Styling Overrides for `type: "line"`:** (All optional)
    *   `"line_width"`: (Number >= 0, Default: 1) Width in pixels.
    *   `"line_style"`: (String, Default: "solid", Allowed: `"solid"`, `"dash"`, `"dot"`, `"dashdot"`)
    *   `"line_color"`: (String - Hex Color '#RGB', '#RRGGBB', '#RRGGBBAA', Default: Application picks color, e.g., '#1f77b4')
    *   `"symbol"`: (String or `null`, Default: `null`, Allowed: `null`, `"o"`, `"s"`, `"t"`, `"d"`, `"+"`, `"x"`, `"star"`, `"p"`, `"h"`)
    *   `"symbol_size"`: (Number > 0, Default: 10) Size in pixels. Applies only if `symbol` is not `null`.
    *   `"symbol_color"`: (String - Hex Color or `null`, Default: `null` - uses `line_color`) Fill color. Applies only if `symbol` is not `null`.
    *   `"symbol_outline"`: (String - Hex Color or `null`, Default: `null` - uses `line_color`) Outline color. Applies only if `symbol` is not `null`.
    *   `"fill_level"`: (Number or `null`, Default: `null`) Y-value boundary for fill. `null` means no fill.
    *   `"fill_color"`: (String - Hex Color or `null`, Default: `null` - uses `line_color` + alpha) Fill area color. Requires `fill_level`. Recommend using alpha (e.g., `#RRGGBBAA`).
    *   `"fill_outline"`: (Boolean, Default: `false`) Draw line border around fill. Requires `fill_level`.

*   **Styling Overrides for `type: "scatter"`:** (All optional)
    *   `"symbol"`: (String, Default: "o", Allowed: "o", "s", "t", "d", "+", "x", "star", "p", "h")
    *   `"symbol_size"`: (Number > 0, Default: 10) Size in pixels.
    *   `"symbol_color"`: (String - Hex Color, Default: "#000000") Fill color.
    *   `"symbol_outline"`: (String - Hex Color or `null`, Default: `null` - uses `symbol_color`) Outline color.

*   **Styling & Behaviour for `type: "histogram":**
    *   `"column": (Required String) Column in `source` file used to build histogram.
    *   `"bins": (Number > 0, Default: 10) Number of histogram bins.
    *   `"hist_color": (String - Hex Color, Default: "#1f77b4") Fill color of bars.
    *   `"bar_width_fraction": (Float 0 < f ≤ 1, Default: 1.0) Fraction of bin width occupied by bar – smaller values add spacing.
    *   `"bar_border_color": (String - Hex Color or `null`, Default: `null` – falls back to `hist_color`) Bar outline color.
    *   `"bar_border_width": (Number ≥ 0, Default: 0) Outline width in pixels; 0 = no border.
    *   `"show_fit": (Boolean, Default: `false`) Overlay a fitted distribution/curve.
    *   `"fitting_type": (String, Default: "normal") Algorithm when `show_fit` is true.
        *   Allowed: "normal", "linear", "quadratic", "cubic_spline", "hermite_cubic_spline", "pchip", "best".
        *   "best" tries all supported algorithms and selects lowest error (slowest).
    *   `"fit_color": (String - Hex Color, Default: "#000000") Color of fitted curve.

*   **Styling & Behaviour for `type: "bar":**
    *   `"x_column": (Required) Categories or X positions.
    *   `"y_column": (Required) Bar heights.
    *   `"bar_color": (String - Hex Color, Default: "#1f77b4") Fill color.
    *   `"bar_width": (Float 0 < w ≤ 1, Default: 0.8) Total width allocated *per category group*.
    *   `"bar_border_color": (String - Hex Color or `null`, Default: `null` – falls back to `bar_color`)
    *   `"bar_border_width": (Number ≥ 0, Default: 0) Outline width in pixels; 0 = no border.
    *   **Grouped (clustered) bars**:
        *   `"group_index": (Integer ≥ 0, Default: 0) Position of this series within a clustered group.
        *   `"group_count": (Integer > 0, Default: 1) Total number of clustered series sharing each category. All series in the cluster must set the same value.
        *   Bars are offset horizontally to appear side-by-side.
    *   **Stacked bars**:
        *   `"stack_group": (String or `null`, Default: `null`) Identifier for stacking. Give the same value to every series you want to stack vertically.
        *   Stacking *can* be combined with grouping: set `group_count` to the number of *stacks* you want per category, and give each stack its own `group_index` (0-based). All series that share both `stack_group` and `group_index` are drawn on top of each other at the same horizontal offset.
        *   Example – two stacks (Population, GDP) shown side-by-side (group_count = 2): see `figure9` in `sample_config.json`.

**Important Notes for Generation:**

*   Ensure the output is valid JSON syntax. Pay close attention to commas, braces `{}`, brackets `[]`, and double quotes `""` for all keys and string values.
*   The value for the top-level `"theme"` key *must* be one of the explicitly listed Allowed Values.
*   File paths provided for `"source"` must be accessible by the application (use absolute paths if possible).
*   Column names provided for `"x_column"` and `"y_column"` must exactly match the headers in the corresponding data source file (case-sensitive).
*   Hex color strings (`"grid_color"`, `"line_color"`, etc.) should follow standard formats (`#RGB`, `#RRGGBB`, `#RRGGBBAA`).
