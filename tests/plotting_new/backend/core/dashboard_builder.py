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

                    trace = go.Bar(
                        x=x_vals,
                        y=y_vals,
                        name=item.get("legend_name"),
                        marker_color=item.get("bar_color"),
                        **extra_kwargs,
                    )

                    fig_obj.add_trace(trace)
                    logger.debug(
                        "Bar trace added id=%s offsetgroup=%s y[0]=%s",
                        item.get("id"),
                        trace.offsetgroup,
                        y_vals[0] if y_vals else None,
                    )

                elif ptype in ("line", "scatter"):
                    
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
                        
                        trace = go.Scatter(
                            x=df[x_col],
                            y=df[y_col],
                            mode=mode,
                            name=item.get("legend_name"),
                            showlegend=item.get("legend_visible"),
                            marker=marker_opts,
                            line=dict(width=item.get("line_width")) # Only width is relevant here
                        )
                        fig_obj.add_trace(trace)
                        
                        if marker_opts['showscale']:
                            colorbar_count += 1
                        
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
                        logger.debug("Added %d '%s' traces grouped by column '%s'", len(z_vals), ptype, z_col)
                    
                    # --- Simple plot (single trace, single color) ---
                    else:
                        color = item.get("line_color") if ptype == 'line' else item.get("symbol_color")
                        trace = go.Scatter(
                            x=df[x_col],
                            y=df[y_col],
                            mode=mode,
                            name=item.get("legend_name"),
                            showlegend=item.get("legend_visible"),
                            marker=dict(color=color, size=item.get("symbol_size")),
                            line=dict(color=color, width=item.get("line_width"))
                        )
                        fig_obj.add_trace(trace)
                        logger.debug("Added single '%s' trace with solid color", ptype)

            elif ptype == "histogram":
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

                _merge_factory_fig(fig_obj, trace_fig)
                logger.debug("Histogram trace %s added bins=%s", item.get("id"), bins)

            elif ptype == "scatter_matrix":
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
                    # Replace current fig_obj entirely because scatter matrix is a self-contained figure
                    fig_obj = go.Figure(sm_fig)
                    logger.debug("Scatter matrix figure %s built with %d columns", item.get("id"), len(data_cols))
                except Exception as exc:
                    logger.error("Failed to build scatter matrix for %s: %s", item.get("id"), exc)
                    continue

            elif ptype == "parallel_coordinates":
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

        fig_obj.update_layout(
            title=fig_title,
            xaxis_title=fig_cfg.get("x_label"),
            yaxis_title=fig_cfg.get("y_label"),
        )

        figures_json.append({
            "id": fig_cfg.get("id"),
            "title": fig_title,
            "figure": json.loads(fig_obj.to_json()),
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