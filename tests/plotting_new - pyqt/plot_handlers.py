import pyqtgraph as pg
import logging
from typing import Dict, List, Optional, Any
import numpy as np

from PyQt6 import QtCore # For Qt.PenStyle constants
from utils.color_utils import get_color_with_default_alpha
from utils.validators import is_valid_hex_color # For fallback logic
from utils.data_fittings import DataFittings

logger = logging.getLogger(__name__)

QT_LINE_STYLES = {
    'solid': QtCore.Qt.PenStyle.SolidLine,
    'dash': QtCore.Qt.PenStyle.DashLine,
    'dot': QtCore.Qt.PenStyle.DotLine,
    'dashdot': QtCore.Qt.PenStyle.DashDotLine
}

def create_line_plot_item(item_config: Dict, x_data: List, y_data: List) -> Optional[pg.PlotDataItem]:
    """ Creates a PlotDataItem configured for a line plot. Assumes defaults applied by ConfigLoader. """
    item_id = item_config.get('id', 'unknown_line_item')
    try:
        # Access config values directly, assuming ConfigLoader.apply_defaults() has run
        line_color = item_config['line_color']
        line_width = item_config['line_width']
        line_style_str = item_config['line_style']
        pen_style = QT_LINE_STYLES.get(line_style_str, QtCore.Qt.PenStyle.SolidLine)

        symbol = item_config['symbol'] # Can be None
        symbol_size = item_config['symbol_size']
        # symbol_color defaults to line_color if None
        symbol_color = item_config.get('symbol_color') or line_color
        # symbol_outline defaults to line_color if None
        symbol_outline = item_config.get('symbol_outline') or line_color

        fill_level = item_config.get('fill_level') # Can be None
        fill_color_config = item_config.get('fill_color') # Can be None
        # fill_color defaults to line_color with alpha if None
        fill_color = fill_color_config or get_color_with_default_alpha(line_color, "4D") # "4D" is ~30% alpha

        fill_outline = item_config['fill_outline']
        legend_name = item_config.get('legend_name') # Can be None

        pen = pg.mkPen(color=line_color, width=float(line_width), style=pen_style) if line_width > 0 else None

        # Validate colors before creating pens/brushes if they could be invalid despite schema
        # However, schema validation + defaults should ensure valid hex or handled None
        symbol_pen_color_final = symbol_outline if is_valid_hex_color(symbol_outline) else line_color
        symbol_brush_color_final = symbol_color if is_valid_hex_color(symbol_color) else line_color

        symbol_pen = pg.mkPen(color=symbol_pen_color_final)
        symbol_brush = pg.mkBrush(color=symbol_brush_color_final)

        fill_brush = None
        if fill_level is not None:
             fill_brush = pg.mkBrush(fill_color) # fill_color is already validated or derived

        plot_item = pg.PlotDataItem(
            x=x_data, y=y_data, pen=pen,
            symbol=symbol, symbolSize=symbol_size, symbolBrush=symbol_brush, symbolPen=symbol_pen,
            fillLevel=fill_level, fillBrush=fill_brush, fillOutline=fill_outline,
            name=legend_name
        )
        # logger.debug(f"Created line plot item '{item_id}'. Name: '{plot_item.name()}'") # Reduced
        return plot_item

    except KeyError as e:
        logger.error(f"Config key missing for line item '{item_id}': {e}. This might indicate an issue with default application or schema definition.", exc_info=True)
        return None
    except Exception as e: # Catch any other error during pg item creation
         logger.error(f"Error creating PlotDataItem components for line item '{item_id}': {e}", exc_info=True)
         return None

def create_scatter_plot_item(item_config: Dict, x_data: List, y_data: List) -> Optional[pg.PlotDataItem]:
    """ Creates a PlotDataItem configured for a scatter plot. Assumes defaults applied. """
    item_id = item_config.get('id', 'unknown_scatter_item')
    try:
        symbol = item_config['symbol']
        symbol_size = item_config['symbol_size']
        symbol_color = item_config['symbol_color'] # Schema ensures this has a default
        # symbol_outline defaults to symbol_color if None
        symbol_outline = item_config.get('symbol_outline') or symbol_color
        legend_name = item_config.get('legend_name')

        symbol_pen_color_final = symbol_outline if is_valid_hex_color(symbol_outline) else symbol_color
        # symbol_brush_color_final is symbol_color, which has a schema default

        symbol_pen = pg.mkPen(color=symbol_pen_color_final)
        symbol_brush = pg.mkBrush(color=symbol_color)


        plot_item = pg.PlotDataItem(
            x=x_data, y=y_data, pen=None, # No connecting line for scatter
            symbol=symbol, symbolSize=symbol_size, symbolBrush=symbol_brush, symbolPen=symbol_pen,
            name=legend_name
        )
        # logger.debug(f"Created scatter plot item '{item_id}'. Name: '{plot_item.name()}'") # Reduced
        return plot_item

    except KeyError as e:
        logger.error(f"Config key missing for scatter item '{item_id}': {e}. Check defaults/schema.", exc_info=True)
        return None
    except Exception as e:
         logger.error(f"Error creating PlotDataItem components for scatter item '{item_id}': {e}", exc_info=True)
         return None

# --- New Plot Handler: Histogram ---

def create_histogram_plot_item(item_config: Dict, values: List, _unused: List = None) -> Optional[pg.GraphicsObject]:
    """Creates a GraphicsItem for a histogram plot using BarGraphItem.

    Parameters
    ----------
    item_config : Dict
        The configuration dict for this histogram item (defaults should already be applied).
    values : List
        A 1-D list/array of numeric values from which to compute the histogram.
    _unused : List, optional
        Ignored. Present so the call signature matches the other plot handlers.

    Returns
    -------
    Optional[pg.GraphicsObject]
        A BarGraphItem ready to be added to a PlotWidget, or *None* on error.
    """
    item_id = item_config.get("id", "unknown_hist_item")
    try:
        if not values:
            logger.warning(f"Histogram item '{item_id}' received empty data list. Skipping.")
            return None

        # Retrieve config with fallbacks
        bins = int(item_config.get("bins", 10))
        bar_color = item_config.get("hist_color", "#1f77b4")
        bar_border_color = item_config.get("bar_border_color", bar_color)
        bar_border_width = float(item_config.get("bar_border_width", 0))
        width_fraction = float(item_config.get("bar_width_fraction", 1.0))
        if width_fraction <= 0 or width_fraction > 1:
            logger.warning(f"Histogram item '{item_id}': 'bar_width_fraction' should be in (0,1]; got {width_fraction}. Clamping to range.")
            width_fraction = max(0.01, min(width_fraction, 1.0))

        show_fit = bool(item_config.get("show_fit", False))
        fitting_type = item_config.get("fitting_type", "normal").lower()
        fit_color = item_config.get("fit_color", "#000000")
        legend_name = item_config.get("legend_name")

        # Compute histogram
        counts, edges = np.histogram(values, bins=bins)
        if len(edges) < 2:
            logger.warning(f"Histogram item '{item_id}' produced insufficient bin edges.")
            return None

        # Use bin centers for x and (optionally reduced) widths
        centers = (edges[:-1] + edges[1:]) / 2.0
        widths = np.diff(edges) * width_fraction

        # Prepare pen (border)
        pen = None
        if bar_border_width > 0:
            pen = pg.mkPen(color=bar_border_color, width=bar_border_width)

        # Create BarGraphItem. Note: centers used for x.
        bar_item = pg.BarGraphItem(x=centers, height=counts, width=widths, brush=bar_color, pen=pen)
        if legend_name is not None:
            # BarGraphItem does not expose 'name' param in constructor like PlotDataItem, but we can set it as attribute.
            bar_item.opts = getattr(bar_item, 'opts', {})
            bar_item.opts['name'] = legend_name

        if not show_fit:
            return bar_item

        # ---------------- Compute requested fit ----------------
        try:
            bin_width_avg = np.mean(widths) if len(widths) else 1.0

            if fitting_type == "best":
                fit_result = DataFittings.best_fit(values, centers, counts, bin_width_avg)
            else:
                fit_result = DataFittings.get_fit(fitting_type, values, centers, counts, bin_width_avg)

            x_fit, y_fit = fit_result['x_fit'], fit_result['y_fit']

            fit_pen = pg.mkPen(color=fit_color, width=2)
            fit_item = pg.PlotDataItem(x_fit, y_fit, pen=fit_pen, name=None)

            return [bar_item, fit_item]
        except Exception as ef:
            logger.error(f"Histogram item '{item_id}': Error computing fit line: {ef}", exc_info=True)
            return bar_item

    except Exception as e:
        logger.error(f"Error creating histogram PlotItem for '{item_id}': {e}", exc_info=True)
        return None

# --- New Plot Handler: Bar Graph ---

def create_bar_plot_item(item_config: Dict, x_data: List, y_data: List, stack_ctx: Optional[Dict] = None) -> Optional[pg.GraphicsObject]:
    """Creates a BarGraphItem for a bar chart.

    The *x_data* can be numeric or categorical. Non-numeric categories are
    converted to sequential integer positions starting at 0. Optionally, the
    caller can set axis tick labels separately – this function only returns
    the bars.
    """
    item_id = item_config.get("id", "unknown_bar_item")
    try:
        if not x_data or not y_data or len(x_data) != len(y_data):
            logger.warning(f"Bar item '{item_id}' received mismatched or empty data lists. Skipping.")
            return None

        # Retrieve visual config
        bar_color = item_config.get("bar_color", "#1f77b4")
        bar_border_color = item_config.get("bar_border_color", bar_color)
        bar_border_width = float(item_config.get("bar_border_width", 0))
        bar_width = float(item_config.get("bar_width", 0.8))

        # Detect stacking
        is_stacked = stack_ctx is not None

        group_count = int(item_config.get("group_count", 1)) or 1
        group_index = int(item_config.get("group_index", 0))

        if group_index < 0:
            group_index = 0
        if group_index >= group_count:
            logger.warning(f"Bar item '{item_id}': group_index {group_index} >= group_count {group_count}. Clamping.")
            group_index = max(0, group_count - 1)

        # Width per individual bar within group
        individual_width = bar_width / group_count
        legend_name = item_config.get("legend_name")

        # Convert x_data to numeric positions (with possible category mapping)
        labels_for_ticks = None

        if is_stacked:
            # Use/extend category mapping in stack_ctx
            cat_map: Dict[Any, int] = stack_ctx.setdefault('cat_map', {})
            x_numeric = []
            for val in x_data:
                if val not in cat_map:
                    cat_map[val] = len(cat_map)
                x_numeric.append(cat_map[val])
            # Save labels only if this is the first stacked series (when totals dict empty)
            if not stack_ctx.get('totals'):
                labels_for_ticks = x_data
        else:
            # Independent (non-stacked) mapping
            try:
                x_numeric = [float(val) for val in x_data]
            except Exception:
                x_numeric = list(range(len(x_data)))
                labels_for_ticks = x_data

        try:
            y_numeric = [float(val) for val in y_data]
        except Exception as e:
            logger.error(f"Bar item '{item_id}': Y data contains non-numeric values: {e}")
            return None

        # Determine y0 for stacking if needed and apply horizontal offset for grouping/stacking
        y0_list = None
        if is_stacked:
            totals: Dict[int, float] = stack_ctx.setdefault('totals', {})
            y0_list = []
            for idx, x_val in enumerate(x_numeric):
                base = totals.get(x_val, 0.0)
                y0_list.append(base)
                totals[x_val] = base + y_numeric[idx]

        # Horizontal offset: always based on grouping so different stacks show side-by-side
        offset = (-bar_width / 2.0) + (group_index + 0.5) * individual_width

        x_numeric_shifted = [x + offset for x in x_numeric]

        pen = None
        if bar_border_width > 0:
            pen = pg.mkPen(color=bar_border_color, width=bar_border_width)

        bar_item = pg.BarGraphItem(x=x_numeric_shifted, height=y_numeric, width=individual_width, brush=bar_color, pen=pen, y0=y0_list if y0_list is not None else 0)
        if legend_name is not None:
            bar_item.opts = getattr(bar_item, 'opts', {})
            bar_item.opts['name'] = legend_name

        # Optionally attach tick labels info for later use by FigureComponent
        if labels_for_ticks is not None:
            bar_item._category_labels = labels_for_ticks  # non-standard attr

        return bar_item
    except Exception as e:
        logger.error(f"Error creating bar plot item '{item_id}': {e}", exc_info=True)
        return None
