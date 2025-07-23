"""Translate a legacy *config.json* file into Plotly figures.

The JSON schema matches the original PyQt application.  We only implement
plot types that already exist in :pyfile:`plot_factory.py` (line, scatter,
histogram, bar).  Unrecognized plot types are skipped with a warning.
"""
from __future__ import annotations

import logging
import json
from pathlib import Path
from typing import List, Dict, Any

import numpy as np
import pandas as pd
import plotly.graph_objs as go

from backend.core.data_handler import load_dataset
from backend.core.plot_factory import (
    histogram_plot,
    bar_plot,
    scatter_matrix_plot,
    parallel_coordinates_plot,
)
from backend.core.utils.layout_utils import determine_grid_dimensions
from backend.core.config_loader import ConfigLoader

logger = logging.getLogger(__name__)

SUPPORTED_TYPES = {"line", "scatter", "histogram", "bar", "scatter_matrix", "parallel_coordinates"}


def _merge_factory_fig(target: go.Figure, factory_fig: Dict[str, Any]) -> None:
    """Merge *factory_fig* (from plot_factory) into *target* Plotly Figure.

    Copies layout keys (e.g., bargap) and appends data traces.
    """
    if isinstance(factory_fig, dict):
        layout = factory_fig.get("layout")
        if isinstance(layout, dict):
            target.update_layout(layout)  # type: ignore[arg-type]

        for trace in factory_fig.get("data", []):
            target.add_trace(trace)




def build_dashboard(config_path: Path) -> Dict[str, Any]:
    """Return a dict containing figure JSON + layout derived from *config_path*."""

    loader = ConfigLoader(str(config_path))
    loader.apply_defaults()
    if not loader.validate_config():
        logger.warning("Config validation reported issues – proceeding anyway.")

    figures_json: List[Dict[str, Any]] = []

    grid_cfg = loader.get_grid_layout()  # may contain rows, cols, spacing

    for fig_idx, fig_cfg in enumerate(loader.get_figures()):
        if not isinstance(fig_cfg, dict):
            continue

        # --------------------------------------------------------------
        # NEW: Skip figures where visibility flag is explicitly false.
        # This allows authors to keep optional analyses in the config
        # but hide them from the rendered dashboard without deletion.
        # --------------------------------------------------------------
        if fig_cfg.get("visibility", True) is False:
            logger.info("Skipping figure %s due to visibility=false", fig_cfg.get("id"))
            continue

        fig_title = fig_cfg.get("title", f"Figure {fig_idx+1}")
        items = fig_cfg.get("items", [])

        fig_obj = go.Figure()
        colorbar_count = 0
        trace_counter = 0  # Track trace indices
        
        # Initialize figure metadata
        fig_metadata = {
            "isPcp": False,
            "isSplom": False,
            "hasLine": False,
            "hasScatter": False,
            "hasBar": False,
            "hasHistogram": False,
            "hasAxes": True,  # Default to true, will be set to false for PCP/SPLOM
            "hasColorbar": False,
            "itemCount": len(items),
            "datasets": {}  # Will store dataframe data for table view
        }

        for item in items:
            if not isinstance(item, dict):
                continue
            ptype = item.get("type")
            if ptype not in SUPPORTED_TYPES:
                logger.warning("Unsupported plot type '%s' – skipping", ptype)
                continue
            try:
                source = item["source"]
                dataset_name = Path(source).name  # drop any dirs
                df = load_dataset(dataset_name)
                
                # Store dataset info in metadata if not already stored
                if dataset_name not in fig_metadata["datasets"]:
                    try:
                        # Convert dataframe to dict format for JSON serialization
                        # Limit to first 1000 rows for performance
                        df_subset = df.head(1000) if len(df) > 1000 else df
                        
                        # Convert to dict and ensure all values are JSON serializable
                        data_records = df_subset.to_dict('records')
                        
                        # Convert any numpy/pandas types to Python native types
                        def make_serializable(obj):
                            if isinstance(obj, (np.integer, np.int64)):
                                return int(obj)
                            elif isinstance(obj, (np.floating, np.float64)):
                                return float(obj)
                            elif isinstance(obj, np.ndarray):
                                return obj.tolist()
                            elif pd.isna(obj):
                                return None
                            return obj
                        
                        # Clean the data records
                        cleaned_records = []
                        for record in data_records:
                            cleaned_record = {}
                            for key, value in record.items():
                                cleaned_record[key] = make_serializable(value)
                            cleaned_records.append(cleaned_record)
                        
                        fig_metadata["datasets"][dataset_name] = {
                            "columns": df.columns.tolist(),
                            "data": cleaned_records,
                            "totalRows": len(df),
                            "truncated": len(df) > 1000
                        }
                        logger.debug(f"Successfully stored dataset {dataset_name} with {len(cleaned_records)} rows")
                    except Exception as e:
                        logger.error(f"Error storing dataset {dataset_name} in metadata: {e}")
                        # Don't fail the whole plot, just skip storing the dataset
                        pass
            except Exception as exc:
                logger.error("Error loading data for item %s: %s", item.get("id"), exc)
                continue

            if ptype in {"line", "scatter", "bar"}:
                x_col = item.get("x_column")
                y_col = item.get("y_column")
                if x_col not in df.columns or y_col not in df.columns:
                    logger.warning("Invalid columns for item %s", item.get("id"))
                    continue

                if ptype == "bar":
                    # Update metadata
                    fig_metadata["hasBar"] = True
                    # Build a bar trace respecting grouping/stacking metadata
                    x_vals = df[x_col].tolist()
                    y_vals = df[y_col].tolist()
                    # Only propagate *offsetgroup* to Plotly when it is
                    # explicitly defined and non-zero.  A missing or zero
                    # value means “no stacking / default grouping”, so we
                    # omit the keyword entirely to keep the trace minimal.
                    og_val = item.get("offsetgroup")
                    extra_kwargs = {}
                    if og_val not in (None, 0, "0", ""):
                        extra_kwargs["offsetgroup"] = str(og_val)

                    trace_name = item.get("legend_name", f"Trace {trace_counter + 1}")
                    trace = go.Bar(
                        x=x_vals,
                        y=y_vals,
                        name=trace_name,
                        marker_color=item.get("bar_color"),
                        **extra_kwargs,
                    )

                    fig_obj.add_trace(trace)
                    
                    trace_counter += 1
                    
                    logger.debug(
                        "Bar trace added id=%s offsetgroup=%s y[0]=%s",
                        item.get("id"),
                        trace.offsetgroup,
                        y_vals[0] if y_vals else None,
                    )

                elif ptype in ("line", "scatter"):
                    # Update metadata
                    if ptype == "line":
                        fig_metadata["hasLine"] = True
                    else:
                        fig_metadata["hasScatter"] = True
                    
                    color_col = item.get("color_column")
                    z_col = item.get("z_column")
                    mode = 'lines+markers' if ptype == 'line' else 'markers'

                    # For line plots, if symbol_size is 0, we only want lines.
                    if ptype == 'line' and item.get("symbol_size") == 0:
                        mode = 'lines'

                    # --- Data-driven coloring (single trace) ---
                    if color_col and color_col in df.columns and ptype == "scatter":
                        
                        colorbar_opts = dict(title=item.get("colorbar_title") or color_col)
                        if colorbar_count > 0:
                            colorbar_opts['x'] = 1.05 + (0.15 * colorbar_count)
                        
                        marker_opts = dict(
                            color=df[color_col],
                            colorscale=item.get("color_map"),
                            showscale=item.get("show_colorbar"),
                            colorbar=colorbar_opts,
                            size=item.get("symbol_size")
                        )
                        
                        trace_name = item.get("legend_name", f"Trace {trace_counter + 1}")
                        trace = go.Scatter(
                            x=df[x_col],
                            y=df[y_col],
                            mode=mode,
                            name=trace_name,
                            showlegend=item.get("legend_visible"),
                            marker=marker_opts,
                            line=dict(width=item.get("line_width")) # Only width is relevant here
                        )
                        fig_obj.add_trace(trace)
                        
                        trace_counter += 1
                        
                        if marker_opts['showscale']:
                            colorbar_count += 1
                            fig_metadata["hasColorbar"] = True
                        
                        logger.debug("Added single '%s' trace with continuous color from column '%s'", ptype, color_col)

                    # --- Z-column grouping (multiple traces) ---
                    elif z_col and z_col in df.columns:
                        z_vals = sorted(df[z_col].unique())
                        from plotly.colors import qualitative
                        palette = qualitative.Plotly

                        for zi, z_val in enumerate(z_vals):
                            sub = df[df[z_col] == z_val]
                            color = palette[zi % len(palette)]
                            name = f"{item.get('legend_name') or y_col} ({z_col}={z_val})"
                            
                            trace = go.Scatter(
                                x=sub[x_col],
                                y=sub[y_col],
                                mode=mode,
                                name=name,
                                showlegend=item.get("legend_visible"),
                                marker=dict(color=color, size=item.get("symbol_size")),
                                line=dict(color=color, width=item.get("line_width"))
                            )
                            fig_obj.add_trace(trace)
                            
                            trace_counter += 1
                        logger.debug("Added %d '%s' traces grouped by column '%s'", len(z_vals), ptype, z_col)
                    
                    # --- Simple plot (single trace, single color) ---
                    else:
                        color = item.get("line_color") if ptype == 'line' else item.get("symbol_color")
                        trace_name = item.get("legend_name", f"Trace {trace_counter + 1}")
                        trace = go.Scatter(
                            x=df[x_col],
                            y=df[y_col],
                            mode=mode,
                            name=trace_name,
                            showlegend=item.get("legend_visible"),
                            marker=dict(color=color, size=item.get("symbol_size")),
                            line=dict(color=color, width=item.get("line_width"))
                        )
                        fig_obj.add_trace(trace)
                        
                        trace_counter += 1
                        
                        logger.debug("Added single '%s' trace with solid color", ptype)

            elif ptype == "histogram":
                # Update metadata
                fig_metadata["hasHistogram"] = True
                column = item.get("column")
                if column not in df.columns:
                    continue
                values = df[column].dropna().tolist()
                bins = item.get("bins", 10)
                show_fit = item.get("show_fit", False)
                color = item.get("hist_color")
                name = item.get("legend_name")

                bar_width_fraction = item.get("bar_width_fraction")
                border_color = item.get("bar_border_color")
                border_width = item.get("bar_border_width")

                trace_fig = histogram_plot(
                    values,
                    bins=bins,
                    show_fit=show_fit,
                    color=color,
                    name=name,
                    bar_width_fraction=bar_width_fraction,
                    border_color=border_color,
                    border_width=border_width,
                )

                # Count how many traces are added by the histogram plot
                traces_before = len(fig_obj.data)
                _merge_factory_fig(fig_obj, trace_fig)
                traces_after = len(fig_obj.data)
                traces_added = traces_after - traces_before
                
                # Store original data for histogram traces
                # Note: Histogram data is different - it's the raw values, not x/y pairs
                for i in range(traces_added):
                    trace_idx = traces_before + i
                    trace_id = f"{item.get('id', 'hist')}_{i}" if i > 0 else item.get('id', f'hist_{trace_counter}')
                    trace_name = f"{name} (fit)" if i > 0 else name
                    
                    trace_counter += 1
                
                logger.debug("Histogram trace %s added bins=%s", item.get("id"), bins)

            elif ptype == "scatter_matrix":
                # Update metadata
                fig_metadata["isSplom"] = True
                fig_metadata["hasAxes"] = False
                data_cols = item.get("data_columns")
                if not isinstance(data_cols, list) or len(data_cols) < 2:
                    logger.warning("scatter_matrix item %s requires at least 2 data_columns", item.get("id"))
                    continue

                # Verify columns exist
                missing_cols = [c for c in data_cols if c not in df.columns]
                if missing_cols:
                    logger.warning("scatter_matrix item %s references missing columns: %s", item.get("id"), missing_cols)
                    continue

                try:
                    sm_fig = scatter_matrix_plot(
                        df,
                        data_cols,
                        title=fig_title,
                        diag_type=item.get("diag_type", "histogram"),
                        matrix_part=item.get("matrix_part", "both"),
                        show_diagonal=item.get("show_diagonal", True),
                        color=item.get("color"),
                        diag_bins=item.get("diag_bins"),
                        diag_border_width=item.get("diag_border_width"),
                        diag_border_color=item.get("diag_border_color"),
                        color_column=item.get("color_column"),
                        color_map=item.get("color_map"),
                        show_colorbar=item.get("show_colorbar", True),
                        colorbar_title=item.get("colorbar_title"),
                        diag_bar_width_fraction=item.get("diag_bar_width_fraction"),
                        marker_size=item.get("marker_size"),
                    )
                    # Check if colorbar is shown
                    if item.get("show_colorbar", True) and item.get("color_column"):
                        fig_metadata["hasColorbar"] = True
                    # Replace current fig_obj entirely because scatter matrix is a self-contained figure
                    fig_obj = go.Figure(sm_fig)
                    logger.debug("Scatter matrix figure %s built with %d columns", item.get("id"), len(data_cols))
                except Exception as exc:
                    logger.error("Failed to build scatter matrix for %s: %s", item.get("id"), exc)
                    continue

            elif ptype == "parallel_coordinates":
                # Update metadata
                fig_metadata["isPcp"] = True
                fig_metadata["hasAxes"] = False
                data_cols = item.get("data_columns")
                if not isinstance(data_cols, list) or len(data_cols) < 2:
                    logger.warning("parallel_coordinates item %s requires at least 2 data_columns", item.get("id"))
                    continue
                missing_cols = [c for c in data_cols if c not in df.columns]
                if missing_cols:
                    logger.warning("parallel_coordinates item %s references missing columns: %s", item.get("id"), missing_cols)
                    continue
                try:
                    pc_fig = parallel_coordinates_plot(
                        df,
                        data_cols,
                        color_column=item.get("color_column"),
                        color_map=item.get("color_map", "Viridis"),
                        show_colorbar=item.get("show_colorbar", True),
                        colorbar_title=item.get("colorbar_title"),
                    )
                    # Check if colorbar is shown
                    if item.get("show_colorbar", True) and item.get("color_column"):
                        fig_metadata["hasColorbar"] = True
                    _merge_factory_fig(fig_obj, pc_fig)
                    logger.debug("Parallel-coordinates trace %s added with %d dimensions", item.get("id"), len(data_cols))
                except Exception as exc:
                    logger.error("Failed to build parallel-coordinates for %s: %s", item.get("id"), exc)
                    continue

        # ------------------------------------------------------------------
        # Decide between *stacked* or *grouped* bar mode.
        # ------------------------------------------------------------------
        # Logic:
        # 1. Collect the *offsetgroup* value for every bar trace.  When the
        #    config file omits this field we store "0" (see above when the
        #    trace is added).  Hence a list full of "0" means *no explicit*
        #    stacking/grouping metadata was provided.
        # 2. If *all* offsetgroups are the default "0" → no stacking ⇒
        #    choose "group" barmode.
        # 3. Otherwise at least one trace specifies a non-zero offsetgroup →
        #    the author expects stacks ⇒ choose "stack".
        bar_offsetgroups = [getattr(t, "offsetgroup", "0")
                             for t in fig_obj.data
                             if getattr(t, "type", None) == "bar"]

        if bar_offsetgroups:
            all_default = all(str(g) in ("0", "None", "", None) for g in bar_offsetgroups)
            fig_obj.update_layout(barmode="group" if all_default else "stack")

        # Build layout updates including axis scales
        layout_updates = {
            "title": {
                "text": fig_title,
                "font": {
                    "size": fig_cfg.get("title_font_size", 18)
                },
                "xanchor": "center",
                "x": 0.5
            },
            "xaxis_title": "",  # Will be set later with formatting
            "yaxis_title": "",  # Will be set later with formatting
        }
        
        # Add figure and plot background colors if specified
        if fig_cfg.get("figure_background_color"):
            layout_updates["paper_bgcolor"] = fig_cfg.get("figure_background_color")
        if fig_cfg.get("plot_background_color"):
            layout_updates["plot_bgcolor"] = fig_cfg.get("plot_background_color")
        
        # Add title color if specified
        if fig_cfg.get("title_color"):
            layout_updates["title"]["font"]["color"] = fig_cfg.get("title_color")
            
        # Add title bold/italic styling using HTML tags
        styled_title = fig_title
        if fig_cfg.get("title_italic", False):
            styled_title = f"<i>{styled_title}</i>"
        if fig_cfg.get("title_bold", False):
            styled_title = f"<b>{styled_title}</b>"
        if styled_title != fig_title:
            layout_updates["title"]["text"] = styled_title
        
        # Build x-axis configuration
        xaxis_config = {}
        if fig_cfg.get("x_scale"):
            xaxis_config["type"] = fig_cfg.get("x_scale")
            
        x_min = fig_cfg.get("x_min")
        x_max = fig_cfg.get("x_max")
        x_reversed = fig_cfg.get("x_reversed", False)
        
        # Treat "auto" as None (auto-range)
        if x_min == "auto":
            x_min = None
        if x_max == "auto":
            x_max = None
            
        logger.debug(f"X-axis settings for {fig_cfg.get('id')}: min={x_min}, max={x_max}, reversed={x_reversed}")
        
        if x_min is not None or x_max is not None:
            if x_min is not None and x_max is not None:
                # Both values set - disable autorange
                if x_reversed:
                    xaxis_config["range"] = [x_max, x_min]  # Swap for reversed axis
                else:
                    xaxis_config["range"] = [x_min, x_max]
                xaxis_config["autorange"] = False
            else:
                # Only one value set - need to handle reversal differently
                if x_reversed:
                    # For partial range with reversal, we need to set autorange to reversed
                    # and use rangemode to respect the single boundary
                    xaxis_config["autorange"] = "reversed"
                    if x_min is not None:
                        xaxis_config["range"] = [x_min, None]
                    else:  # x_max is not None
                        xaxis_config["range"] = [None, x_max]
                else:
                    xaxis_config["range"] = [x_min, x_max]
        elif x_reversed:
            # No manual range set - use autorange reversed
            xaxis_config["autorange"] = "reversed"
            
        # Add grid configuration to x-axis
        grid_alpha = fig_cfg.get("grid_alpha", 0.3)
        grid_color = fig_cfg.get("grid_color")
        
        if fig_cfg.get("grid_x", True):
            xaxis_config["showgrid"] = True
            if grid_color:
                # Convert hex color to rgba
                if grid_color.startswith("#"):
                    r = int(grid_color[1:3], 16)
                    g = int(grid_color[3:5], 16) 
                    b = int(grid_color[5:7], 16)
                    xaxis_config["gridcolor"] = f"rgba({r}, {g}, {b}, {grid_alpha})"
                else:
                    xaxis_config["gridcolor"] = grid_color
        else:
            xaxis_config["showgrid"] = False
            
        # Configure zero line (vertical line at x=0)
        xaxis_config["zeroline"] = True
        xaxis_config["zerolinewidth"] = 1.5  # Slightly thicker than grid lines
        if grid_color:
            # Use exact same color as grid
            if grid_color.startswith("#"):
                r = int(grid_color[1:3], 16)
                g = int(grid_color[3:5], 16) 
                b = int(grid_color[5:7], 16)
                xaxis_config["zerolinecolor"] = f"rgba({r}, {g}, {b}, {grid_alpha})"
            else:
                xaxis_config["zerolinecolor"] = grid_color
        else:
            # If no custom grid color, use theme default
            xaxis_config["zerolinecolor"] = f"rgba(128, 128, 128, {grid_alpha})"
            
        # Configure plot border
        xaxis_config["showline"] = True
        xaxis_config["linewidth"] = 1
        xaxis_config["mirror"] = True  # Show border on all sides
        
        # Use plot border color if specified, otherwise use grid color
        plot_border_color = fig_cfg.get("plot_border_color")
        
        if plot_border_color:
            xaxis_config["linecolor"] = plot_border_color
        elif grid_color:
            if grid_color.startswith("#"):
                r = int(grid_color[1:3], 16)
                g = int(grid_color[3:5], 16) 
                b = int(grid_color[5:7], 16)
                xaxis_config["linecolor"] = f"rgba({r}, {g}, {b}, 1)"  # Always full opacity for border when using grid color
            else:
                xaxis_config["linecolor"] = grid_color
        else:
            xaxis_config["linecolor"] = "rgba(128, 128, 128, 1)"  # Always full opacity for border
            
        # Add font sizes and colors for x-axis
        xaxis_config["title"] = {"font": {"size": fig_cfg.get("axis_label_font_size", 14)}}
        if fig_cfg.get("axis_label_color"):
            xaxis_config["title"]["font"]["color"] = fig_cfg.get("axis_label_color")
            
        # Apply bold/italic styling to x-axis label using HTML tags
        x_label = fig_cfg.get("x_label", "")
        if x_label:
            if fig_cfg.get("axis_label_italic", False):
                x_label = f"<i>{x_label}</i>"
            if fig_cfg.get("axis_label_bold", False):
                x_label = f"<b>{x_label}</b>"
            xaxis_config["title"]["text"] = x_label
            
        xaxis_config["tickfont"] = {"size": fig_cfg.get("axis_tick_font_size", 12)}
        if fig_cfg.get("axis_tick_color"):
            xaxis_config["tickfont"]["color"] = fig_cfg.get("axis_tick_color")
            
        if xaxis_config:
            layout_updates["xaxis"] = xaxis_config
            logger.debug(f"X-axis config for {fig_cfg.get('id')}: {xaxis_config}")
            
        # Build y-axis configuration
        yaxis_config = {}
        if fig_cfg.get("y_scale"):
            yaxis_config["type"] = fig_cfg.get("y_scale")
            
        y_min = fig_cfg.get("y_min")
        y_max = fig_cfg.get("y_max")
        y_reversed = fig_cfg.get("y_reversed", False)
        
        # Treat "auto" as None (auto-range)
        if y_min == "auto":
            y_min = None
        if y_max == "auto":
            y_max = None
            
        logger.debug(f"Y-axis settings for {fig_cfg.get('id')}: min={y_min}, max={y_max}, reversed={y_reversed}")
        
        if y_min is not None or y_max is not None:
            if y_min is not None and y_max is not None:
                # Both values set - disable autorange
                if y_reversed:
                    yaxis_config["range"] = [y_max, y_min]  # Swap for reversed axis
                else:
                    yaxis_config["range"] = [y_min, y_max]
                yaxis_config["autorange"] = False
            else:
                # Only one value set - need to handle reversal differently
                if y_reversed:
                    # For partial range with reversal, we need to set autorange to reversed
                    # and use rangemode to respect the single boundary
                    yaxis_config["autorange"] = "reversed"
                    if y_min is not None:
                        yaxis_config["range"] = [y_min, None]
                    else:  # y_max is not None
                        yaxis_config["range"] = [None, y_max]
                else:
                    yaxis_config["range"] = [y_min, y_max]
        elif y_reversed:
            # No manual range set - use autorange reversed
            yaxis_config["autorange"] = "reversed"
            
        # Add grid configuration to y-axis
        if fig_cfg.get("grid_y", True):
            yaxis_config["showgrid"] = True
            if grid_color:
                # Convert hex color to rgba
                if grid_color.startswith("#"):
                    r = int(grid_color[1:3], 16)
                    g = int(grid_color[3:5], 16) 
                    b = int(grid_color[5:7], 16)
                    yaxis_config["gridcolor"] = f"rgba({r}, {g}, {b}, {grid_alpha})"
                else:
                    yaxis_config["gridcolor"] = grid_color
        else:
            yaxis_config["showgrid"] = False
            
        # Configure zero line (horizontal line at y=0)
        yaxis_config["zeroline"] = True
        yaxis_config["zerolinewidth"] = 1.5  # Slightly thicker than grid lines
        if grid_color:
            # Use exact same color as grid
            if grid_color.startswith("#"):
                r = int(grid_color[1:3], 16)
                g = int(grid_color[3:5], 16) 
                b = int(grid_color[5:7], 16)
                yaxis_config["zerolinecolor"] = f"rgba({r}, {g}, {b}, {grid_alpha})"
            else:
                yaxis_config["zerolinecolor"] = grid_color
        else:
            # If no custom grid color, use theme default
            yaxis_config["zerolinecolor"] = f"rgba(128, 128, 128, {grid_alpha})"
            
        # Configure plot border
        yaxis_config["showline"] = True
        yaxis_config["linewidth"] = 1
        yaxis_config["mirror"] = True  # Show border on all sides
        
        if plot_border_color:
            yaxis_config["linecolor"] = plot_border_color
        elif grid_color:
            if grid_color.startswith("#"):
                r = int(grid_color[1:3], 16)
                g = int(grid_color[3:5], 16) 
                b = int(grid_color[5:7], 16)
                yaxis_config["linecolor"] = f"rgba({r}, {g}, {b}, 1)"  # Always full opacity for border when using grid color
            else:
                yaxis_config["linecolor"] = grid_color
        else:
            yaxis_config["linecolor"] = "rgba(128, 128, 128, 1)"  # Always full opacity for border
            
        # Add font sizes and colors for y-axis
        yaxis_config["title"] = {"font": {"size": fig_cfg.get("axis_label_font_size", 14)}}
        if fig_cfg.get("axis_label_color"):
            yaxis_config["title"]["font"]["color"] = fig_cfg.get("axis_label_color")
            
        # Apply bold/italic styling to y-axis label using HTML tags
        y_label = fig_cfg.get("y_label", "")
        if y_label:
            if fig_cfg.get("axis_label_italic", False):
                y_label = f"<i>{y_label}</i>"
            if fig_cfg.get("axis_label_bold", False):
                y_label = f"<b>{y_label}</b>"
            yaxis_config["title"]["text"] = y_label
            
        yaxis_config["tickfont"] = {"size": fig_cfg.get("axis_tick_font_size", 12)}
        if fig_cfg.get("axis_tick_color"):
            yaxis_config["tickfont"]["color"] = fig_cfg.get("axis_tick_color")
            
        if yaxis_config:
            layout_updates["yaxis"] = yaxis_config
            logger.debug(f"Y-axis config for {fig_cfg.get('id')}: {yaxis_config}")
            
        # Add legend font configuration
        legend_config = {}
        legend_font_size = fig_cfg.get("legend_font_size")
        if legend_font_size is not None:
            legend_config["font"] = {"size": legend_font_size}
        
        legend_color = fig_cfg.get("legend_color")
        if legend_color is not None:
            if "font" not in legend_config:
                legend_config["font"] = {}
            legend_config["font"]["color"] = legend_color
        # Note: Legend text also doesn't support bold/italic in Plotly
        
        if legend_config:
            layout_updates["legend"] = legend_config
            
        fig_obj.update_layout(**layout_updates)
        
        # Apply axis configuration to all axes ONLY for 2D plots (not scatter matrix or parallel coordinates)
        is_scatter_matrix = fig_metadata.get("isSplom", False)
        is_parallel_coords = fig_metadata.get("isPcp", False)
        
        if not is_scatter_matrix and not is_parallel_coords:
            # For regular 2D plots, apply to all axes (in case of subplots)
            if xaxis_config:
                fig_obj.update_xaxes(**xaxis_config)
                logger.debug(f"Applied x-axis config to all x-axes for 2D plot {fig_cfg.get('id')}")
                
            if yaxis_config:
                fig_obj.update_yaxes(**yaxis_config)
                logger.debug(f"Applied y-axis config to all y-axes for 2D plot {fig_cfg.get('id')}")

        # Convert figure to JSON
        figure_dict = json.loads(fig_obj.to_json())
        
        fig_id = fig_cfg.get("id")
        figures_json.append({
            "id": fig_id,
            "title": fig_title,
            "figure": figure_dict,
            "metadata": fig_metadata
        })

    rows, cols = determine_grid_dimensions(len(figures_json), grid_cfg)

    h_gap = grid_cfg.get("h_gap", 20)
    v_gap = grid_cfg.get("v_gap", 20)

    return {
        "grid": {
            "rows": rows,
            "cols": cols,
            "h_gap": h_gap,
            "v_gap": v_gap,
        },
        "figures": figures_json,
    } 