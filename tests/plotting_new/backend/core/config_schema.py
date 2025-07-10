"""
Configuration schema for the visualization tool.
Defines the structure, types, defaults, and valid values for configuration.
"""
import re
import logging # Changed from print to logging
from typing import Dict, List, Any, Optional, Union, TypeVar, Callable, Type, Sequence
from backend.core.utils.validators import (
    is_non_negative, is_positive, is_valid_hex_color, is_between_0_and_1
)
import re
from pathlib import Path

logger = logging.getLogger(__name__) # Added logger

# ---------------------------------------------------------------------------
# Determine available themes by parsing *frontend/src/themes.css*.
# ---------------------------------------------------------------------------

# Locate project root (assumed two directories up: backend/core → backend → project root)
_project_root = Path(__file__).resolve().parents[2]
THEME_CSS_PATH = _project_root / "frontend" / "src" / "themes.css"

_fallback_themes = ["light", "dark"]

if THEME_CSS_PATH.exists():
    try:
        css_text = THEME_CSS_PATH.read_text(encoding="utf-8")

        # Preferred: read --available-themes css variable
        m = re.search(r"--available-themes:\s*\"([^\"]+)\"", css_text)
        if m:
            VALID_THEME_CONFIG_KEYS = [k.strip() for k in m.group(1).split(',') if k.strip()]
        else:
            # Fallback: extract selectors like [data-theme='dark']
            VALID_THEME_CONFIG_KEYS = re.findall(r"\[data-theme=['\"]([a-zA-Z0-9_-]+)['\"]\]", css_text)

        if "light" in VALID_THEME_CONFIG_KEYS:
            VALID_THEME_CONFIG_KEYS.remove("light")
            VALID_THEME_CONFIG_KEYS.insert(0, "light")

        if not VALID_THEME_CONFIG_KEYS:
            raise ValueError("No theme keys found in themes.css")
    except Exception as exc:
        logger.warning(
            "Failed to parse themes.css for theme keys (%s). Falling back to %s.",
            exc,
            _fallback_themes,
        )
        VALID_THEME_CONFIG_KEYS = _fallback_themes
else:
    logger.warning(
        "themes.css not found at %s. Theme validation will fall back to %s.",
        THEME_CSS_PATH,
        _fallback_themes,
    )
    VALID_THEME_CONFIG_KEYS = _fallback_themes

# Pick default theme
SCHEMA_DEFAULT_THEME = "light" if "light" in VALID_THEME_CONFIG_KEYS else VALID_THEME_CONFIG_KEYS[0]

ValidationFunction = Callable[[Any], bool]

class ConfigField:
    """Definition of a configuration field."""

    def __init__(
        self,
        field_type: Union[type, Sequence[type]],
        required: bool = False,
        default: Any = None,
        possible_values: Optional[List[Any]] = None,
        validator: Optional[ValidationFunction] = None,
        description: str = ""
    ):
        if isinstance(field_type, type):
            self.field_type = (field_type,)
        elif isinstance(field_type, Sequence) and not isinstance(field_type, (str, bytes)):
            self.field_type = tuple(type(None) if t is None else t for t in field_type)
        else:
             raise TypeError(f"field_type must be a type or a sequence of types, got {type(field_type)}")

        self.required = required
        self.default = default if not required else None
        self.possible_values = possible_values
        self.validator = validator
        self.description = description


class SchemaRegistry:
    """Registry of schemas for different parts of the configuration."""

    GENERAL_SCHEMA: Dict[str, ConfigField] = {
        "app_title": ConfigField(
            field_type=str,
            default="Visualization Tool",
            description="Title of the application window"
        ),
        "left_margin": ConfigField(
            field_type=(int, float),
            default=10,
            validator=is_non_negative,
            description="Left margin in pixels"
        ),
        "right_margin": ConfigField(
            field_type=(int, float),
            default=10,
            validator=is_non_negative,
            description="Right margin in pixels"
        ),
        "top_margin": ConfigField(
            field_type=(int, float),
            default=10,
            validator=is_non_negative,
            description="Top margin in pixels"
        ),
        "bottom_margin": ConfigField(
            field_type=(int, float),
            default=10,
            validator=is_non_negative,
            description="Bottom margin in pixels"
        ),
        "theme": ConfigField(
            field_type=str,
            default=SCHEMA_DEFAULT_THEME,
            possible_values=VALID_THEME_CONFIG_KEYS,
            description=f"Application theme. Available: {', '.join(VALID_THEME_CONFIG_KEYS)}"
        ),
    }

    GRID_LAYOUT_SCHEMA: Dict[str, ConfigField] = {
        "rows": ConfigField(
            field_type=(int, type(None)),
            default=None,
            validator=is_positive, # Validator needs to handle None if passed (current one returns False for None)
            description="Number of rows in the grid (calculated automatically if omitted)"
        ),
        "cols": ConfigField(
            field_type=(int, type(None)),
            default=None,
            validator=is_positive,
            description="Number of columns in the grid (calculated automatically if omitted)"
        ),
        "horizontal_spacing": ConfigField(
            field_type=(int, float),
            default=10,
            validator=is_non_negative,
            description="Horizontal spacing between plots in pixels"
        ),
        "vertical_spacing": ConfigField(
            field_type=(int, float),
            default=10,
            validator=is_non_negative,
            description="Vertical spacing between plots in pixels"
        ),
    }

    BASE_FIGURE_SCHEMA: Dict[str, ConfigField] = {
        "id": ConfigField(
            field_type=str,
            required=True,
            description="Unique identifier for the figure"
        ),
        "title": ConfigField(
            field_type=str,
            default="",
            description="Title of the figure"
        ),
        "x_label": ConfigField(
            field_type=str,
            default="",
            description="Label for the x-axis"
        ),
        "y_label": ConfigField(
            field_type=str,
            default="",
            description="Label for the y-axis"
        ),
        "x_scale": ConfigField(
            field_type=str,
            default="linear",
            possible_values=["linear", "log"],
            description="Scale type for the x-axis ('linear' or 'log')"
        ),
        "y_scale": ConfigField(
            field_type=str,
            default="linear",
            possible_values=["linear", "log"],
            description="Scale type for the y-axis ('linear' or 'log')"
        ),
        "grid_x": ConfigField(
            field_type=bool,
            default=True,
            description="Initial state for vertical grid line visibility (toggleable)"
        ),
        "grid_y": ConfigField(
            field_type=bool,
            default=True,
            description="Initial state for horizontal grid line visibility (toggleable)"
        ),
        "grid_alpha": ConfigField(
            field_type=(float, int),
            default=0.3,
            validator=is_between_0_and_1,
            description="Alpha (transparency) value for grid lines (0.0 to 1.0)"
        ),
        "grid_color": ConfigField(
            field_type=(str, type(None)),
            default=None,
            validator=is_valid_hex_color,
            description="Custom color for grid lines (hex format, e.g., #RRGGBBAA). If null, theme default is used."
        ),
    }

    BASE_PLOT_ITEM_SCHEMA: Dict[str, ConfigField] = {
        "id": ConfigField(
            field_type=str,
            required=True,
            description="Unique identifier for the plot item"
        ),
        "type": ConfigField(
            field_type=str,
            required=True,
            description="Type of plot (e.g., 'line', 'scatter')"
        ),
        "source": ConfigField(
            field_type=str,
            required=True,
            description="Path to the data source file (relative to execution or absolute)"
        ),
        "x_column": ConfigField(
            field_type=str,
            required=True,
            description="Column name for x-axis data in the source file"
        ),
        "y_column": ConfigField(
            field_type=str,
            required=True,
            description="Column name for y-axis data in the source file"
        ),
        "legend_name": ConfigField(
            field_type=(str, type(None)),
            default=None,
            description="Name to display in the legend (omit or set to null to hide from legend)"
        )
    }

    LINE_PLOT_SCHEMA: Dict[str, ConfigField] = {
        **BASE_PLOT_ITEM_SCHEMA,
        "type": ConfigField(
            field_type=str,
            required=True,
            default="line", # Default value for a required field is mainly for documentation/consistency
            possible_values=["line"],
            description="Type must be 'line'"
        ),
        "line_width": ConfigField(
            field_type=(int, float),
            default=1,
            validator=is_non_negative,
            description="Width of the line (use 0 for no line)"
        ),
        "line_style": ConfigField(
            field_type=str,
            default="solid",
            possible_values=["solid", "dash", "dot", "dashdot"],
            description="Style of the line ('solid', 'dash', 'dot', 'dashdot')"
        ),
        "line_color": ConfigField(
            field_type=str,
            default="#1f77b4",
            validator=is_valid_hex_color,
            description="Color of the line (hex format: #RGB, #RRGGBB, #RRGGBBAA)"
        ),
        "symbol": ConfigField(
            field_type=(str, type(None)),
            default=None,
            possible_values=[None, "o", "s", "t", "d", "+", "x", "star", "p", "h"],
            description="Symbol for data points (or null for none)"
        ),
        "symbol_size": ConfigField(
            field_type=(int, float),
            default=10,
            validator=is_positive,
            description="Size of the symbols in pixels"
        ),
        "symbol_color": ConfigField(
            field_type=(str, type(None)),
            default=None,
            validator=is_valid_hex_color,
            description="Fill color of the symbols (hex format). Defaults to line_color if null."
        ),
        "symbol_outline": ConfigField(
            field_type=(str, type(None)),
            default=None,
            validator=is_valid_hex_color,
            description="Outline color of the symbols (hex format). Defaults to line_color if null."
        ),
        "fill_level": ConfigField(
            field_type=(int, float, type(None)),
            default=None,
            description="Y-value to fill towards. Null for no fill."
        ),
        "fill_color": ConfigField(
            field_type=(str, type(None)),
            default=None,
            validator=is_valid_hex_color,
            description="Fill color (hex format). Defaults to line_color with alpha if null."
        ),
        "fill_outline": ConfigField(
            field_type=bool,
            default=False,
            description="Draw an outline around the filled area (using line_color)"
        ),
        "z_column": ConfigField(
            field_type=(str, type(None)),
            default=None,
            description="Optional third-axis column used to split the series into multiple curves (e.g. Vgs levels)."
        ),
        "color_scheme": ConfigField(
            field_type=str,
            default="single",  # 'single' keeps original colour, otherwise name of pyqtgraph colormap
            description="Either 'single' or the name of a supported pyqtgraph colormap (e.g. viridis, plasma)."
        ),
        "show_colorbar": ConfigField(
            field_type=bool,
            default=False,
            description="Show a colour bar when a colormap is used and z_column is provided. Ignored when color_scheme='single'."
        ),
        "legend_visible": ConfigField(
            field_type=bool,
            default=True,
            description="Whether to include this series (or expanded z-series) in the legend."
        )
    }

    SCATTER_PLOT_SCHEMA: Dict[str, ConfigField] = {
        **BASE_PLOT_ITEM_SCHEMA,
        "type": ConfigField(
            field_type=str,
            required=True,
            default="scatter",
            possible_values=["scatter"],
            description="Type must be 'scatter'"
        ),
        "symbol": ConfigField(
            field_type=str,
            default="o",
            possible_values=["o", "s", "t", "d", "+", "x", "star", "p", "h"],
            description="Symbol for data points"
        ),
        "symbol_size": ConfigField(
            field_type=(int, float),
            default=10,
            validator=is_positive,
            description="Size of the symbols in pixels"
        ),
        "symbol_color": ConfigField(
            field_type=str,
            default="#000000",
            validator=is_valid_hex_color,
            description="Fill color of the symbols (hex format)"
        ),
        "symbol_outline": ConfigField(
            field_type=(str, type(None)),
            default=None,
            validator=is_valid_hex_color,
            description="Outline color of the symbols (hex format). Defaults to symbol_color if null."
        ),
        "z_column": ConfigField(
            field_type=(str, type(None)),
            default=None,
            description="Optional third-axis column used to split the series into multiple scatter groups (e.g. Vgs levels)."
        ),
        "color_scheme": ConfigField(
            field_type=str,
            default="single",
            description="Either 'single' or the name of a supported pyqtgraph colormap."
        ),
        "show_colorbar": ConfigField(
            field_type=bool,
            default=False,
            description="Show a colour bar when using a colormap."
        ),
        "legend_visible": ConfigField(
            field_type=bool,
            default=True,
            description="Whether to include this series in the legend."
        )
    }

    # -------------------- Histogram Plot Schema --------------------
    HISTOGRAM_PLOT_SCHEMA: Dict[str, ConfigField] = {
        "id": ConfigField(
            field_type=str,
            required=True,
            description="Unique identifier for the histogram plot item"
        ),
        "type": ConfigField(
            field_type=str,
            required=True,
            default="histogram",
            possible_values=["histogram"],
            description="Type must be 'histogram'"
        ),
        "source": ConfigField(
            field_type=str,
            required=True,
            description="Path to the data source file"
        ),
        "column": ConfigField(
            field_type=str,
            required=True,
            description="Column in data source used to build the histogram"
        ),
        "bins": ConfigField(
            field_type=(int, type(None)),
            default=10,
            validator=is_positive,
            description="Number of histogram bins (positive integer)"
        ),
        "hist_color": ConfigField(
            field_type=str,
            default="#1f77b4",
            validator=is_valid_hex_color,
            description="Color of the histogram bars (hex string)"
        ),
        "bar_width_fraction": ConfigField(
            field_type=(float, int, type(None)),
            default=1.0,
            validator=is_between_0_and_1,
            description="Fraction of bin width occupied by each bar (0 < f ≤ 1). Allows spacing between bars."
        ),
        "bar_border_color": ConfigField(
            field_type=(str, type(None)),
            default=None,
            validator=is_valid_hex_color,
            description="Border color for the bars (hex). Defaults to hist_color if null."
        ),
        "bar_border_width": ConfigField(
            field_type=(int, float, type(None)),
            default=0,
            validator=is_non_negative,
            description="Width of the bar border in pixels (0 for no border)."
        ),
        "show_fit": ConfigField(
            field_type=bool,
            default=False,
            description="Whether to overlay a fitted normal distribution line on the histogram."
        ),
        "fit_color": ConfigField(
            field_type=(str, type(None)),
            default="#000000",
            validator=is_valid_hex_color,
            description="Color of the fitted distribution line."
        ),
        "fitting_type": ConfigField(
            field_type=str,
            default="normal",
            possible_values=[
                "normal",
                "linear",
                "quadratic",
                "cubic_spline",
                "hermite_cubic_spline",
                "pchip",
                "best"
            ],
            description="Algorithm used for the fit curve. 'best' tries all supported types and chooses the one with the lowest error. Default 'pchip' produces a Hermite cubic spline fit."
        ),
        "legend_name": ConfigField(
            field_type=(str, type(None)),
            default=None,
            description="Name to display in legend (or null to omit)"
        )
    }

    # -------------------- Bar Plot Schema --------------------
    BAR_PLOT_SCHEMA: Dict[str, ConfigField] = {
        "id": ConfigField(
            field_type=str,
            required=True,
            description="Unique identifier for the bar plot item"
        ),
        "type": ConfigField(
            field_type=str,
            required=True,
            default="bar",
            possible_values=["bar"],
            description="Type must be 'bar'"
        ),
        "source": ConfigField(
            field_type=str,
            required=True,
            description="Path to the data source file"
        ),
        "x_column": ConfigField(
            field_type=str,
            required=True,
            description="Column used for bar categories or X values"
        ),
        "y_column": ConfigField(
            field_type=str,
            required=True,
            description="Column used for bar heights (Y values)"
        ),
        "bar_color": ConfigField(
            field_type=str,
            default="#1f77b4",
            validator=is_valid_hex_color,
            description="Fill color of the bars (hex string)"
        ),
        "bar_width": ConfigField(
            field_type=(float, int),
            default=0.8,
            validator=is_between_0_and_1,
            description="Width of each bar (units of X spacing)."
        ),
        "bar_border_color": ConfigField(
            field_type=(str, type(None)),
            default=None,
            validator=is_valid_hex_color,
            description="Border color of the bars (hex). Defaults to bar_color if null."
        ),
        "bar_border_width": ConfigField(
            field_type=(int, float, type(None)),
            default=0,
            validator=is_non_negative,
            description="Border width in pixels (0 for none)."
        ),
        "offsetgroup": ConfigField(
            field_type=(str, type(None)),
            default=None,
            description="Identifier used to group bars side-by-side while still allowing stacking."
        ),
        "legend_name": ConfigField(
            field_type=(str, type(None)),
            default=None,
            description="Name to display in legend (or null to omit)"
        ),
    }

    PLOT_TYPE_SCHEMAS: Dict[str, Dict[str, ConfigField]] = {
        "line": LINE_PLOT_SCHEMA,
        "scatter": SCATTER_PLOT_SCHEMA,
        "histogram": HISTOGRAM_PLOT_SCHEMA,
        "bar": BAR_PLOT_SCHEMA,
    }

    @classmethod
    def get_general_schema(cls) -> Dict[str, ConfigField]:
        return cls.GENERAL_SCHEMA

    @classmethod
    def get_grid_layout_schema(cls) -> Dict[str, ConfigField]:
        return cls.GRID_LAYOUT_SCHEMA

    @classmethod
    def get_base_figure_schema(cls) -> Dict[str, ConfigField]:
        return cls.BASE_FIGURE_SCHEMA

    @classmethod
    def get_plot_type_schema(cls, plot_type: str) -> Optional[Dict[str, ConfigField]]:
        return cls.PLOT_TYPE_SCHEMAS.get(plot_type)

    @classmethod
    def is_valid_plot_type(cls, plot_type: str) -> bool:
        return plot_type in cls.PLOT_TYPE_SCHEMAS
