# plot_types/line_plot.py
import pyqtgraph as pg
# Ensure you're using the correct Qt bindings if using explicit types
from PyQt6 import QtCore # Or from PyQt5 import QtCore

# --- Map string names to Qt PenStyle constants ---
LINE_STYLE_MAP = {
    "SolidLine": QtCore.Qt.PenStyle.SolidLine,
    "DashLine": QtCore.Qt.PenStyle.DashLine,
    "DotLine": QtCore.Qt.PenStyle.DotLine,
    "DashDotLine": QtCore.Qt.PenStyle.DashDotLine,
    "DashDotDotLine": QtCore.Qt.PenStyle.DashDotDotLine,
    # Add others if needed, ensure names match JSON options
    "NoPen": QtCore.Qt.PenStyle.NoPen # If you want symbols only later
}
# Default style if lookup fails
DEFAULT_LINE_STYLE = QtCore.Qt.PenStyle.SolidLine
# ---

# Update function signature to accept style_str
def add_line_plot(plot_widget, x_data, y_data, name="Line Plot", color='b', width=1, style_str="SolidLine"):
    """
    Adds a line plot to a given PlotWidget.

    Args:
        plot_widget (pg.PlotWidget): The target widget to add the plot to.
        x_data (np.ndarray): X-axis data.
        y_data (np.ndarray): Y-axis data.
        name (str): Name for the plot item (used in legends).
        color (str or QColor): Color of the line.
        width (int): Width of the line pen.
        style_str (str): String representation of the line style (e.g., "SolidLine").
                         Defaults to "SolidLine".
    """
    # Look up the Qt style constant from the map
    style = LINE_STYLE_MAP.get(style_str, DEFAULT_LINE_STYLE)
    if style_str not in LINE_STYLE_MAP:
        print(f"Warning: Unknown line_style '{style_str}'. Using default.")

    pen = pg.mkPen(color=color, width=width, style=style)
    plot_item = plot_widget.getPlotItem()
    line = plot_item.plot(x_data, y_data, pen=pen, name=name)

    return line
