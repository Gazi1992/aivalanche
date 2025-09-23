"""
Plot Capabilities and Types Registry

This module defines all available plot types, their capabilities, and categorization.
It serves as the single source of truth for understanding what each plot type can do.
"""

from typing import Dict, List, Set
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

@dataclass
class PlotCapability:
    """Defines what a plot type can do"""
    name: str
    display_name: str
    category: PlotCategory
    description: str

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
        description="Points plotted on X-Y axes. Can show correlation, clusters, or outliers. Bubble charts are scatter plots with sized markers.",
        has_markers=True,
        aliases=["bubble", "scatter2d", "points"]
    ),

    "line": PlotCapability(
        name="line",
        display_name="Line Plot",
        category=PlotCategory.BASIC_2D,
        description="Connected points showing trends over continuous data. Ideal for time series and continuous functions.",
        has_lines=True,
        aliases=["line_chart", "line_graph"]
    ),

    "bar": PlotCapability(
        name="bar",
        display_name="Bar Chart",
        category=PlotCategory.BASIC_2D,
        description="Rectangular bars comparing categorical data. Can be vertical or horizontal, grouped or stacked.",
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
        description="Shows distribution quartiles, median, and outliers. Excellent for comparing distributions.",
        supports_categorical_x=True,
        aliases=["box_plot", "box_and_whisker"]
    ),

    "violin": PlotCapability(
        name="violin",
        display_name="Violin Plot",
        category=PlotCategory.STATISTICAL,
        description="Combines box plot with kernel density estimation. Shows full distribution shape.",
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
        aliases=["pie_chart", "donut"]  # Donut is just pie with hole
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
        description="Hierarchical data as nested rectangles. Size shows values.",
        has_axes=False,
        min_dimensions=2,
        aliases=["tree_map"]
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
        description="Matrix visualization with values as colors. Great for correlation matrices.",
        has_colorscale=True,
        aliases=["heat_map", "matrix_plot"]
    ),

    "contour": PlotCapability(
        name="contour",
        display_name="Contour Plot",
        category=PlotCategory.DENSITY,
        description="Shows 3D surface as 2D with contour lines. Like topographic maps.",
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
        max_dimensions=4,  # 4th can be color
        supports_3d_rotation=True,
        has_markers=True,
        aliases=["scatter_3d", "3d_scatter"]
    ),

    "surface": PlotCapability(
        name="surface",
        display_name="3D Surface Plot",
        category=PlotCategory.THREE_D,
        description="Continuous surface in 3D space. Great for mathematical functions.",
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
        description="3D shape from triangular mesh. Used for complex 3D objects.",
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
        description="Shows cumulative effect of sequential positive/negative values.",
        has_fill=True,
        aliases=["waterfall_chart", "bridge_chart"]
    ),

    # Multidimensional
    "parcoords": PlotCapability(
        name="parcoords",
        display_name="Parallel Coordinates",
        category=PlotCategory.MULTIDIMENSIONAL,
        description="Multiple vertical axes for high-dimensional data. Lines connect values.",
        min_dimensions=3,
        max_dimensions=20,
        has_lines=True,
        aliases=["parallel_coordinates", "pcp"]
    ),

    "parcats": PlotCapability(
        name="parcats",
        display_name="Parallel Categories",
        category=PlotCategory.MULTIDIMENSIONAL,
        description="Like parallel coordinates but for categorical data. Shows flow between categories.",
        min_dimensions=2,
        max_dimensions=10,
        aliases=["parallel_categories", "alluvial"]
    ),

    "splom": PlotCapability(
        name="splom",
        display_name="Scatterplot Matrix",
        category=PlotCategory.MULTIDIMENSIONAL,
        description="Grid of scatter plots for all variable pairs. Great for correlation analysis.",
        min_dimensions=3,
        max_dimensions=10,
        has_markers=True,
        aliases=["scatter_matrix", "pairs_plot"]
    ),

    # Flow & Network
    "sankey": PlotCapability(
        name="sankey",
        display_name="Sankey Diagram",
        category=PlotCategory.FLOW,
        description="Flow diagram where width shows quantity. Great for energy/material flow.",
        has_axes=False,
        min_dimensions=3,  # source, target, value
        aliases=["sankey_diagram", "flow_diagram"]
    ),

    # Specialized
    "indicator": PlotCapability(
        name="indicator",
        display_name="Indicator/Gauge",
        category=PlotCategory.SPECIALIZED,
        description="Single value display with optional gauge, delta, or progress bar.",
        has_axes=False,
        min_dimensions=1,
        max_dimensions=1,
        supports_zoom=False,
        supports_pan=False,
        aliases=["gauge", "kpi", "metric"]
    ),

    "scatterpolar": PlotCapability(
        name="scatterpolar",
        display_name="Polar Scatter Plot",
        category=PlotCategory.SPECIALIZED,
        description="Scatter plot on polar coordinates. Good for cyclical data.",
        min_dimensions=2,
        has_markers=True,
        aliases=["polar_scatter", "radar_scatter"]
    ),

    "scatterternary": PlotCapability(
        name="scatterternary",
        display_name="Ternary Plot",
        category=PlotCategory.SPECIALIZED,
        description="Three-component compositions on triangular coordinates.",
        min_dimensions=3,
        max_dimensions=3,
        has_markers=True,
        aliases=["ternary_plot", "triangle_plot"]
    ),
}

# Capability lookup functions
def get_plot_capability(plot_type: str) -> PlotCapability:
    """Get capability for a plot type, checking aliases too"""
    # Direct lookup
    if plot_type in PLOT_TYPES:
        return PLOT_TYPES[plot_type]

    # Check aliases
    for key, capability in PLOT_TYPES.items():
        if plot_type in capability.aliases:
            return capability

    return None

def get_plots_by_category(category: PlotCategory) -> List[PlotCapability]:
    """Get all plots in a category"""
    return [cap for cap in PLOT_TYPES.values() if cap.category == category]

def get_plots_for_data_type(
    num_dimensions: int,
    has_categorical: bool = False,
    has_temporal: bool = False,
    has_hierarchical: bool = False
) -> List[PlotCapability]:
    """Get suitable plots for data characteristics"""
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

        # Check hierarchical (sunburst, treemap)
        if has_hierarchical and capability.name not in ['sunburst', 'treemap', 'sankey']:
            continue

        suitable.append(capability)

    return suitable

# Real-world demo categories
DEMO_CATEGORIES = {
    "engineering_analysis": {
        "name": "Engineering Analysis",
        "description": "Sensor data, stress analysis, and system performance",
        "plots": ["scatter", "line", "surface", "contour", "heatmap", "scatter3d", "mesh3d", "waterfall"],
        "examples": [
            "Stress-strain curves",
            "Temperature distribution",
            "Vibration analysis",
            "Flow simulation",
            "Circuit response",
            "Material properties",
            "Load testing",
            "Signal processing"
        ]
    },
    "business_metrics": {
        "name": "Business Metrics",
        "description": "Sales, KPIs, and business performance tracking",
        "plots": ["bar", "line", "pie", "funnel", "waterfall", "indicator", "treemap", "sunburst"],
        "examples": [
            "Sales dashboard",
            "Revenue breakdown",
            "Conversion funnel",
            "Market share",
            "Performance KPIs",
            "Budget allocation",
            "Growth metrics",
            "Customer segments"
        ]
    },
    "financial_markets": {
        "name": "Financial Markets",
        "description": "Stock prices, portfolio analysis, and risk metrics",
        "plots": ["candlestick", "ohlc", "line", "area", "scatter", "heatmap", "indicator", "scatterternary"],
        "examples": [
            "Stock price charts",
            "Portfolio composition",
            "Risk correlation",
            "Trading volume",
            "Market indicators",
            "Asset allocation",
            "Volatility analysis",
            "Currency exchange"
        ]
    },
    "scientific_research": {
        "name": "Scientific Research",
        "description": "Experimental data, statistical analysis, and modeling",
        "plots": ["scatter", "box", "violin", "histogram", "contour", "surface", "scatter3d", "parcoords"],
        "examples": [
            "Experimental results",
            "Distribution analysis",
            "Correlation studies",
            "Regression models",
            "Multivariate analysis",
            "Chemical compositions",
            "Particle distributions",
            "Climate data"
        ]
    },
    "manufacturing_quality": {
        "name": "Manufacturing & Quality",
        "description": "Process control, defect analysis, and production metrics",
        "plots": ["histogram", "box", "scatter", "heatmap", "pareto", "waterfall", "indicator", "sankey"],
        "examples": [
            "Quality control charts",
            "Defect analysis",
            "Process capability",
            "Production flow",
            "Yield analysis",
            "Batch comparison",
            "Supply chain flow",
            "Equipment efficiency"
        ]
    },
    "healthcare_analytics": {
        "name": "Healthcare Analytics",
        "description": "Patient data, clinical trials, and epidemiology",
        "plots": ["scatter", "box", "violin", "line", "heatmap", "sankey", "sunburst", "parcats"],
        "examples": [
            "Patient outcomes",
            "Drug efficacy",
            "Disease spread",
            "Treatment pathways",
            "Clinical trial results",
            "Demographic analysis",
            "Hospital metrics",
            "Symptom correlation"
        ]
    },
    "geospatial_data": {
        "name": "Geospatial Data",
        "description": "Geographic distributions and location-based analysis",
        "plots": ["scattergeo", "density_map", "choropleth", "scatter", "heatmap", "contour", "bubble_map", "line"],
        "examples": [
            "Population density",
            "Weather patterns",
            "Traffic flow",
            "Sales by region",
            "Earthquake data",
            "Flight paths",
            "Resource distribution",
            "Urban planning"
        ]
    },
    "network_systems": {
        "name": "Network & Systems",
        "description": "Network traffic, system logs, and connectivity analysis",
        "plots": ["sankey", "scatter", "line", "heatmap", "parcats", "indicator", "area", "histogram"],
        "examples": [
            "Network traffic flow",
            "System performance",
            "Error rates",
            "User behavior flow",
            "API latency",
            "Database queries",
            "Server load",
            "Connection paths"
        ]
    }
}