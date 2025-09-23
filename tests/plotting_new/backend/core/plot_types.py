"""
Centralized Plot Types and Capabilities Registry

This module is the single source of truth for all plot types, their capabilities,
and characteristics. It defines what each plot type can do and how it behaves.
"""

from typing import Dict, List, Optional
from dataclasses import dataclass
from enum import Enum


class PlotCategory(Enum):
    """Main categories of plot types"""
    BASIC_2D = "basic_2d"
    STATISTICAL = "statistical"
    PROPORTIONAL = "proportional"  # Part-to-whole
    DENSITY = "density"
    THREE_D = "3d"
    TEMPORAL = "temporal"  # Time series
    MULTIDIMENSIONAL = "multidimensional"
    FLOW = "flow"
    SPECIALIZED = "specialized"
    GEOGRAPHIC = "geographic"
    D3 = "d3"  # D3.js visualizations
    OTHER = "other"  # Unknown or uncategorized


@dataclass
class PlotCapability:
    """Defines what a plot type can do"""
    name: str
    display_name: str
    category: PlotCategory
    description: str
    library: str = "plotly"  # plotly, d3, or other

    # Interaction capabilities
    supports_zoom: bool = True
    supports_pan: bool = True
    supports_hover: bool = True
    supports_selection: bool = True
    supports_3d_rotation: bool = False

    # Data capabilities
    min_dimensions: int = 2
    max_dimensions: int = 2
    supports_categorical_x: bool = True
    supports_categorical_y: bool = False
    supports_datetime: bool = True
    supports_multiple_traces: bool = True

    # Visual capabilities
    has_axes: bool = True
    has_legend: bool = True
    has_colorscale: bool = False
    has_markers: bool = False
    has_lines: bool = False
    has_fill: bool = False

    # Edit capabilities
    is_editable: bool = True  # Can be edited through EditPane

    # Special features
    requires_special_data: List[str] = None  # e.g., ['open', 'high', 'low', 'close'] for candlestick
    aliases: List[str] = None  # Alternative names

    def __post_init__(self):
        if self.requires_special_data is None:
            self.requires_special_data = []
        if self.aliases is None:
            self.aliases = []


# Define all plot types with their capabilities
PLOT_TYPES = {
    # Basic 2D Plots
    "scatter": PlotCapability(
        name="scatter",
        display_name="Scatter Plot",
        category=PlotCategory.BASIC_2D,
        description="Points plotted on X-Y axes. Can show correlation, clusters, or outliers.",
        has_markers=True,
        aliases=["bubble", "scatter2d", "points"]
    ),

    "line": PlotCapability(
        name="line",
        display_name="Line Plot",
        category=PlotCategory.BASIC_2D,
        description="Connected points showing trends over continuous data. Ideal for time series.",
        has_lines=True,
        aliases=["line_chart", "line_graph"]
    ),

    "bar": PlotCapability(
        name="bar",
        display_name="Bar Chart",
        category=PlotCategory.BASIC_2D,
        description="Rectangular bars comparing categorical data. Can be vertical or horizontal.",
        supports_categorical_y=True,
        has_fill=True,
        aliases=["bar_chart", "column_chart"]
    ),

    "area": PlotCapability(
        name="area",
        display_name="Area Chart",
        category=PlotCategory.BASIC_2D,
        description="Line chart with filled area below. Shows cumulative totals and trends.",
        has_lines=True,
        has_fill=True,
        aliases=["area_chart", "filled_line"]
    ),

    # Statistical Plots
    "box": PlotCapability(
        name="box",
        display_name="Box Plot",
        category=PlotCategory.STATISTICAL,
        description="Shows distribution quartiles, median, and outliers.",
        supports_categorical_x=True,
        aliases=["box_plot", "box_and_whisker"]
    ),

    "violin": PlotCapability(
        name="violin",
        display_name="Violin Plot",
        category=PlotCategory.STATISTICAL,
        description="Combines box plot with kernel density estimation.",
        supports_categorical_x=True,
        aliases=["violin_plot"]
    ),

    "histogram": PlotCapability(
        name="histogram",
        display_name="Histogram",
        category=PlotCategory.STATISTICAL,
        description="Shows frequency distribution of continuous data in bins.",
        min_dimensions=1,
        supports_categorical_x=False,
        aliases=["hist", "frequency_plot"]
    ),

    "histogram2d": PlotCapability(
        name="histogram2d",
        display_name="2D Histogram",
        category=PlotCategory.DENSITY,
        description="2D binning of data points showing density as color.",
        has_colorscale=True,
        supports_categorical_x=False,
        supports_categorical_y=False,
        aliases=["hist2d", "density_plot_2d"]
    ),

    # Proportional (Part-to-Whole)
    "pie": PlotCapability(
        name="pie",
        display_name="Pie Chart",
        category=PlotCategory.PROPORTIONAL,
        description="Shows proportions of a whole. Best for up to 6-7 categories.",
        has_axes=False,
        supports_zoom=False,
        supports_pan=False,
        min_dimensions=1,
        aliases=["pie_chart", "donut"]
    ),

    "sunburst": PlotCapability(
        name="sunburst",
        display_name="Sunburst Chart",
        category=PlotCategory.PROPORTIONAL,
        description="Hierarchical pie chart showing nested categories.",
        has_axes=False,
        supports_zoom=True,
        min_dimensions=2,
        aliases=["sunburst_chart", "radial_treemap"]
    ),

    "treemap": PlotCapability(
        name="treemap",
        display_name="Treemap",
        category=PlotCategory.PROPORTIONAL,
        description="Hierarchical data as nested rectangles.",
        has_axes=False,
        min_dimensions=2,
        aliases=["tree_map"]
    ),

    "icicle": PlotCapability(
        name="icicle",
        display_name="Icicle Chart",
        category=PlotCategory.PROPORTIONAL,
        description="Hierarchical data as nested rectangles in icicle layout.",
        has_axes=False,
        min_dimensions=2,
        aliases=["icicle_chart"]
    ),

    "funnel": PlotCapability(
        name="funnel",
        display_name="Funnel Chart",
        category=PlotCategory.PROPORTIONAL,
        description="Shows progressive reduction of data through stages.",
        aliases=["funnel_chart", "funnel_plot"]
    ),

    # Density & Heatmaps
    "heatmap": PlotCapability(
        name="heatmap",
        display_name="Heatmap",
        category=PlotCategory.DENSITY,
        description="Matrix visualization with values as colors.",
        has_colorscale=True,
        aliases=["heat_map", "matrix_plot"]
    ),

    "contour": PlotCapability(
        name="contour",
        display_name="Contour Plot",
        category=PlotCategory.DENSITY,
        description="Shows 3D surface as 2D with contour lines.",
        has_colorscale=True,
        supports_categorical_x=False,
        supports_categorical_y=False,
        aliases=["contour_plot", "level_plot"]
    ),

    # 3D Plots
    "scatter3d": PlotCapability(
        name="scatter3d",
        display_name="3D Scatter Plot",
        category=PlotCategory.THREE_D,
        description="Points in 3D space. Can rotate and zoom in 3D.",
        min_dimensions=3,
        max_dimensions=4,
        supports_3d_rotation=True,
        has_markers=True,
        aliases=["scatter_3d", "3d_scatter"]
    ),

    "surface": PlotCapability(
        name="surface",
        display_name="3D Surface Plot",
        category=PlotCategory.THREE_D,
        description="Continuous surface in 3D space.",
        min_dimensions=3,
        max_dimensions=3,
        supports_3d_rotation=True,
        has_colorscale=True,
        supports_categorical_x=False,
        supports_categorical_y=False,
        aliases=["surface_plot", "3d_surface"]
    ),

    "mesh3d": PlotCapability(
        name="mesh3d",
        display_name="3D Mesh",
        category=PlotCategory.THREE_D,
        description="3D shape from triangular mesh.",
        min_dimensions=3,
        supports_3d_rotation=True,
        has_colorscale=True,
        aliases=["mesh_3d", "3d_mesh"]
    ),

    # Financial/Temporal
    "candlestick": PlotCapability(
        name="candlestick",
        display_name="Candlestick Chart",
        category=PlotCategory.TEMPORAL,
        description="Financial chart showing open, high, low, close prices.",
        requires_special_data=["open", "high", "low", "close"],
        supports_categorical_x=False,
        aliases=["candle", "candlestick_chart"]
    ),

    "ohlc": PlotCapability(
        name="ohlc",
        display_name="OHLC Chart",
        category=PlotCategory.TEMPORAL,
        description="Financial chart with lines for open, high, low, close.",
        requires_special_data=["open", "high", "low", "close"],
        supports_categorical_x=False,
        aliases=["ohlc_chart"]
    ),

    "waterfall": PlotCapability(
        name="waterfall",
        display_name="Waterfall Chart",
        category=PlotCategory.TEMPORAL,
        description="Shows cumulative effect of sequential values.",
        has_fill=True,
        aliases=["waterfall_chart", "bridge_chart"]
    ),

    # Multidimensional
    "parcoords": PlotCapability(
        name="parcoords",
        display_name="Parallel Coordinates",
        category=PlotCategory.MULTIDIMENSIONAL,
        description="Multiple vertical axes for high-dimensional data.",
        min_dimensions=3,
        max_dimensions=20,
        has_axes=False,
        has_lines=True,
        aliases=["parallel_coordinates", "pcp"]
    ),

    "parcats": PlotCapability(
        name="parcats",
        display_name="Parallel Categories",
        category=PlotCategory.MULTIDIMENSIONAL,
        description="Like parallel coordinates but for categorical data.",
        min_dimensions=2,
        max_dimensions=10,
        has_axes=False,
        aliases=["parallel_categories", "alluvial"]
    ),

    "splom": PlotCapability(
        name="splom",
        display_name="Scatterplot Matrix",
        category=PlotCategory.MULTIDIMENSIONAL,
        description="Grid of scatter plots for all variable pairs.",
        min_dimensions=3,
        max_dimensions=10,
        has_axes=False,
        has_markers=True,
        aliases=["scatter_matrix", "pairs_plot"]
    ),

    # Flow & Network
    "sankey": PlotCapability(
        name="sankey",
        display_name="Sankey Diagram",
        category=PlotCategory.FLOW,
        description="Flow diagram where width shows quantity.",
        has_axes=False,
        min_dimensions=3,
        aliases=["sankey_diagram", "flow_diagram"]
    ),

    # Polar
    "scatterpolar": PlotCapability(
        name="scatterpolar",
        display_name="Polar Scatter Plot",
        category=PlotCategory.SPECIALIZED,
        description="Scatter plot on polar coordinates.",
        min_dimensions=2,
        has_axes=False,
        has_markers=True,
        aliases=["polar_scatter", "radar_scatter"]
    ),

    "barpolar": PlotCapability(
        name="barpolar",
        display_name="Polar Bar Chart",
        category=PlotCategory.SPECIALIZED,
        description="Bar chart on polar coordinates.",
        has_axes=False,
        has_fill=True,
        aliases=["polar_bar", "radial_bar"]
    ),

    "scatterternary": PlotCapability(
        name="scatterternary",
        display_name="Ternary Plot",
        category=PlotCategory.SPECIALIZED,
        description="Three-component compositions on triangular coordinates.",
        min_dimensions=3,
        max_dimensions=3,
        has_axes=False,
        has_markers=True,
        aliases=["ternary_plot", "triangle_plot"]
    ),

    # Geographic
    "scattergeo": PlotCapability(
        name="scattergeo",
        display_name="Geographic Scatter",
        category=PlotCategory.GEOGRAPHIC,
        description="Points on a world map.",
        has_axes=False,
        has_markers=True,
        aliases=["geo_scatter", "map_scatter"]
    ),

    "choropleth": PlotCapability(
        name="choropleth",
        display_name="Choropleth Map",
        category=PlotCategory.GEOGRAPHIC,
        description="Geographic regions colored by data values.",
        has_axes=False,
        has_colorscale=True,
        aliases=["choropleth_map", "filled_map"]
    ),

    "scattermapbox": PlotCapability(
        name="scattermapbox",
        display_name="Mapbox Scatter",
        category=PlotCategory.GEOGRAPHIC,
        description="Points on detailed street maps.",
        has_axes=False,
        has_markers=True,
        aliases=["mapbox_scatter"]
    ),

    # Specialized
    "indicator": PlotCapability(
        name="indicator",
        display_name="Indicator/Gauge",
        category=PlotCategory.SPECIALIZED,
        description="Single value display with optional gauge or delta.",
        has_axes=False,
        min_dimensions=1,
        max_dimensions=1,
        supports_zoom=False,
        supports_pan=False,
        aliases=["gauge", "kpi", "metric"]
    ),

    "table": PlotCapability(
        name="table",
        display_name="Table",
        category=PlotCategory.SPECIALIZED,
        description="Tabular data display.",
        has_axes=False,
        has_legend=False,
        supports_zoom=False,
        supports_pan=False,
        aliases=["data_table"]
    ),

    # D3.js visualizations
    "d3": PlotCapability(
        name="d3",
        display_name="D3 Visualization",
        category=PlotCategory.D3,
        description="Custom D3.js visualization with full control.",
        library="d3",
        has_axes=False,
        has_legend=False,
        is_editable=False,  # D3 plots are not editable through EditPane
        supports_zoom=True,
        supports_pan=True,
        aliases=["d3js", "d3_custom"]
    ),

    # Unknown type fallback
    "unknown": PlotCapability(
        name="unknown",
        display_name="Unknown Plot Type",
        category=PlotCategory.OTHER,
        description="Unrecognized plot type.",
        library="unknown",
        aliases=[]
    )
}


# Helper functions for working with plot types
def get_plot_capabilities(plot_type: str) -> Dict:
    """
    Get the capabilities for a given plot type as a dictionary.

    Args:
        plot_type: The type of plot

    Returns:
        Dictionary of capabilities for the plot type
    """
    # Normalize plot type
    plot_type = plot_type.lower() if plot_type else 'unknown'

    # Get capability object
    capability = get_plot_capability(plot_type)
    if not capability:
        capability = PLOT_TYPES['unknown']

    # Convert to dictionary for JSON serialization
    return {
        'name': capability.name,
        'display_name': capability.display_name,
        'category': capability.category.value,
        'description': capability.description,
        'library': capability.library,
        'supports_zoom': capability.supports_zoom,
        'supports_pan': capability.supports_pan,
        'supports_hover': capability.supports_hover,
        'supports_selection': capability.supports_selection,
        'supports_3d_rotation': capability.supports_3d_rotation,
        'has_axes': capability.has_axes,
        'has_legend': capability.has_legend,
        'has_colorscale': capability.has_colorscale,
        'is_editable': capability.is_editable,
        'min_dimensions': capability.min_dimensions,
        'max_dimensions': capability.max_dimensions
    }


def get_plot_capability(plot_type: str) -> Optional[PlotCapability]:
    """
    Get capability object for a plot type, checking aliases too.

    Args:
        plot_type: The type of plot

    Returns:
        PlotCapability object or None if not found
    """
    plot_type = plot_type.lower() if plot_type else 'unknown'

    # Direct lookup
    if plot_type in PLOT_TYPES:
        return PLOT_TYPES[plot_type]

    # Check aliases
    for key, capability in PLOT_TYPES.items():
        if plot_type in capability.aliases:
            return capability

    return None


def get_plot_category(plot_type: str) -> str:
    """Get the category for a plot type"""
    capability = get_plot_capability(plot_type)
    if capability:
        return capability.category.value
    return PlotCategory.OTHER.value


def is_plot_editable(plot_type: str) -> bool:
    """Check if a plot type is editable through EditPane"""
    capability = get_plot_capability(plot_type)
    if capability:
        return capability.is_editable
    return True  # Default to editable for unknown types


def get_all_plot_types() -> List[str]:
    """Get a list of all supported plot types"""
    return list(PLOT_TYPES.keys())


def get_plotly_plot_types() -> List[str]:
    """Get all Plotly plot types"""
    return [k for k, v in PLOT_TYPES.items() if v.library == 'plotly']


def get_d3_plot_types() -> List[str]:
    """Get all D3 plot types"""
    return [k for k, v in PLOT_TYPES.items() if v.library == 'd3']


def get_plots_by_category(category: PlotCategory) -> List[PlotCapability]:
    """Get all plots in a category"""
    return [cap for cap in PLOT_TYPES.values() if cap.category == category]


def get_plots_for_data_type(
    num_dimensions: int,
    has_categorical: bool = False,
    has_temporal: bool = False,
    has_hierarchical: bool = False
) -> List[PlotCapability]:
    """
    Get suitable plots for data characteristics.

    Args:
        num_dimensions: Number of data dimensions
        has_categorical: Whether data has categorical variables
        has_temporal: Whether data has time series
        has_hierarchical: Whether data has hierarchical structure

    Returns:
        List of suitable PlotCapability objects
    """
    suitable = []

    for capability in PLOT_TYPES.values():
        # Check dimension compatibility
        if not (capability.min_dimensions <= num_dimensions <= capability.max_dimensions):
            continue

        # Check categorical compatibility
        if has_categorical and not (capability.supports_categorical_x or capability.supports_categorical_y):
            continue

        # Check temporal compatibility
        if has_temporal and not capability.supports_datetime:
            continue

        # Check hierarchical (sunburst, treemap, sankey)
        if has_hierarchical and capability.name not in ['sunburst', 'treemap', 'sankey', 'icicle']:
            continue

        suitable.append(capability)

    return suitable