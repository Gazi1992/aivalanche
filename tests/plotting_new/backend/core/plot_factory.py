"""Plotly figure builders for different plot types.

Each function returns a Python dict that is JSON serialisable (``fig.to_dict()``)
so FastAPI can send it straight to the client.

We purposefully **do not** depend on Qt – everything is pure Plotly.
"""
from __future__ import annotations

from typing import List, Dict, Any, Optional

import numpy as np
import pandas as pd
import plotly.graph_objs as go
from scipy import stats
import json
from plotly.subplots import make_subplots

__all__ = [
    "histogram_plot",
    "bar_plot",
    "scatter_matrix_plot",
]

__all__.append("parallel_coordinates_plot")


def _apply_common_layout(layout: go.Layout, title: str | None = None) -> go.Layout:
    """Return *layout* with a shared baseline styling applied."""
    layout.update(
        template="plotly_white",
        title=title,
        hovermode="closest",
        legend=dict(orientation="h"),
    )
    return layout


# ---------------------------------------------------------------------------
# Histogram (optionally with normal-fit curve)
# ---------------------------------------------------------------------------

def histogram_plot(
    values: List[float],
    *,
    bins: int = 10,
    show_fit: bool = False,
    name: str | None = None,
    color: str | None = None,
    bar_width_fraction: float | None = None,
    border_color: str | None = None,
    border_width: int | None = None,
) -> Dict[str, Any]:
    """Return Plotly histogram.

    Parameters
    ----------
    values : list-like
        Data values for histogram.
    bins : int, default 10
        Number of bins.
    show_fit : bool, default False
        Whether to overlay a normal distribution fit.
    bar_width_fraction : float, optional
        Fraction (0–1] of column width filled by bars.  Plotly uses *bargap* in
        layout to achieve this: *bargap = 1 - fraction*.
    border_color : str, optional
        Hex/RGB color for bar outline.
    border_width : int, optional
        Outline width in pixels.
    """

    marker_kwargs: dict[str, Any] = {"color": color}
    if border_color is not None:
        marker_kwargs["line"] = dict(color=border_color, width=border_width or 1)

    # Determine bin settings
    hist_kwargs: dict[str, Any] = {
        "x": values,
        "name": name,
        "opacity": 0.75,
        "marker": marker_kwargs,
    }

    if isinstance(bins, int):
        # Build exact bin edges so we get precisely *bins* bins.
        if len(values) > 1 and bins > 0:
            vmin, vmax = min(values), max(values)
            if vmax == vmin:
                # All values equal – still render single bin
                hist_kwargs["nbinsx"] = 1
            else:
                bin_size = (vmax - vmin) / bins
                hist_kwargs.update({
                    "autobinx": False,
                    "xbins": dict(start=vmin, end=vmax, size=bin_size),
                })
        else:
            hist_kwargs["nbinsx"] = bins
    else:
        hist_kwargs["nbinsx"] = bins

    hist = go.Histogram(**hist_kwargs)

    fig = go.Figure(data=[hist])

    # Determine bargap from bar_width_fraction and force overlay so multiple histograms share the same space
    layout = go.Layout(barmode="overlay")
    if bar_width_fraction is not None:
        bar_width_fraction = max(0.0, min(1.0, bar_width_fraction))
        layout.update(bargap=1 - bar_width_fraction)

    if show_fit and len(values) > 1:
        mu, sigma = np.mean(values), np.std(values)
        x_fit = np.linspace(min(values), max(values), 200)
        y_fit = stats.norm.pdf(x_fit, mu, sigma)

        # Compute histogram counts to determine appropriate scaling
        counts, _ = np.histogram(values, bins=bins)
        if counts.size > 0 and y_fit.max() > 0:
            scale = counts.max() / y_fit.max()
            y_fit_scaled = y_fit * scale
        else:
            y_fit_scaled = y_fit

        fig.add_trace(
            go.Scatter(
                x=x_fit,
                y=y_fit_scaled,
                mode="lines",
                name="Normal fit",
                line=dict(color="black"),
            )
        )

    fig.update_layout(_apply_common_layout(layout))
    return json.loads(fig.to_json())


# ---------------------------------------------------------------------------
# Bar
# ---------------------------------------------------------------------------

def bar_plot(
    x: List,
    ys: List[List[float]] | List[float],
    *,
    names: Optional[List[str]] = None,
    stacked: bool = False,
) -> Dict[str, Any]:
    """Return standard or stacked/grouped bar plot.

    Parameters
    ----------
    x : list-like (categories)
    ys : Either a list of *y* values (single series) or a list of series (stack).
    names : Legend labels for each series.
    stacked : If *True*, uses barmode="stack", else default "group".
    """
    series_list: List[List[float]]
    if all(isinstance(y, (int, float)) for y in ys):  # type: ignore
        series_list = [ys]  # type: ignore
    else:
        series_list = ys  # type: ignore

    if names is None:
        names = [f"Series {i+1}" for i in range(len(series_list))]

    fig = go.Figure()
    for y_vals, name in zip(series_list, names):
        fig.add_bar(x=x, y=y_vals, name=name)

    barmode = "stack" if stacked else "group"
    fig.update_layout(_apply_common_layout(go.Layout(barmode=barmode)))
    return json.loads(fig.to_json())

# ---------------------------------------------------------------------------
# Scatter Matrix
# ---------------------------------------------------------------------------


def scatter_matrix_plot(
    df: "pd.DataFrame",
    columns: List[str],
    *,
    title: str | None = None,
    diag_type: str = "histogram",
    matrix_part: str = "both",
    show_diagonal: bool = True,
    color: str | None = None,
    diag_bins: int | None = None,
    diag_border_width: float | None = None,
    diag_border_color: str | None = None,
    color_column: str | None = None,
    color_map: str | None = None,
    show_colorbar: bool = True,
    colorbar_title: str | None = None,
    diag_bar_width_fraction: float | None = None,
    marker_size: float | None = None,
) -> Dict[str, Any]:
    """Return a Plotly scatter-matrix figure as a JSON-serialisable dict.

    Parameters
    ----------
    df : pandas.DataFrame
        Source data.
    columns : list of str
        Columns to include in the matrix (must contain ≥2, and exist in *df*).
    title : str, optional
        Figure title.
    diag_type : {'histogram', 'box', 'scatter'}, default 'histogram'
        Type of plot shown on the diagonal (histogram, box, scatter).  See
        Plotly Figure Factory `create_scatterplotmatrix` docs:
        https://plotly.com/python/v3/legacy/scatterplot-matrix/
    matrix_part : {'lower', 'upper', 'both'}, default 'both'
        Which part of the matrix to display.
    show_diagonal : bool, default True
        Whether to display the diagonal cells (histograms).
    color: str, optional
        Color for all markers in the plot. If None, a default is used.
    diag_bins : int, optional
        Number of bins for diagonal histograms.
    diag_border_width : float, optional
        Border width for diagonal histogram bars.
    diag_border_color : str, optional
        Border color for diagonal histogram bars.
    color_column : str, optional
        Column to use for coloring markers. Overrides `color`.
    color_map : str, optional
        Plotly colorscale name to use.
    show_colorbar : bool, default True
        Whether to display a color scale bar.
    colorbar_title : str, optional
        Title for the color bar. Defaults to `color_column` name if None.
    diag_bar_width_fraction : float, optional
        Fraction of bin width for diagonal histogram bars.
    marker_size : float, optional
        Size of scatter plot markers in pixels.
    """

    # Validate column list
    valid_cols = [c for c in columns if c in df.columns]
    if len(valid_cols) < 2:
        raise ValueError("scatter_matrix_plot requires at least two valid columns")

    if diag_type not in {"histogram", "box", "scatter"}:
        raise ValueError("diag_type must be 'histogram', 'box', or 'scatter'")

    # -------------------------------------------------------------------
    # Build the scatter-matrix manually with subplots
    # -------------------------------------------------------------------

    n = len(valid_cols)

    # Marker styles
    plot_color = color or '#636EFA'  # Use provided color or default Plotly blue
    hist_marker_style = {"opacity": 0.75, "color": plot_color}
    scatter_marker_style = {"opacity": 0.7, "size": marker_size or 4}
    box_marker_style = hist_marker_style.copy()

    # Data-driven coloring for scatter plots
    if color_column and color_column in df.columns:
        scatter_marker_style["color"] = df[color_column]
        scatter_marker_style["colorscale"] = color_map
        scatter_marker_style["showscale"] = show_colorbar
        if show_colorbar:
            scatter_marker_style["colorbar"] = dict(
                title=dict(
                    text=colorbar_title or color_column,
                    font=dict(
                        weight='normal'  # Explicitly set to normal weight
                    )
                ),
                tickfont=dict(
                    weight='normal'  # Also set normal weight for tick labels
                )
            )
        # Set color axis limits to the data's min/max to ensure full colorscale is used
        # Cast to standard int to prevent JSON serialization issues with numpy types.
        scatter_marker_style["cmin"] = int(df[color_column].min())
        scatter_marker_style["cmax"] = int(df[color_column].max())
    else:
        scatter_marker_style["color"] = plot_color

    # Create an n×n grid of sub-plots with minimal spacing
    fig = make_subplots(
        rows=n,
        cols=n,
        shared_xaxes=False,
        shared_yaxes=False,
        horizontal_spacing=0.04,
        vertical_spacing=0.04,
    )

    # Helper lambdas for matrix-part logic
    is_visible_offdiag = {
        "both": lambda r, c: True,
        "lower": lambda r, c: r > c,
        "upper": lambda r, c: c > r,
    }[matrix_part]

    for r, y_col in enumerate(valid_cols, start=1):
        for c, x_col in enumerate(valid_cols, start=1):
            if r == c:
                # Diagonal cell – render if requested
                if not show_diagonal:
                    continue

                if diag_type == "histogram":
                    
                    hist_marker = hist_marker_style.copy()
                    if diag_border_width and diag_border_color:
                        hist_marker["line"] = dict(width=diag_border_width, color=diag_border_color)
                    
                    trace_opts = dict(x=df[x_col], showlegend=False, marker=hist_marker)
                    if diag_bins:
                        trace_opts["nbinsx"] = diag_bins

                    fig.add_trace(go.Histogram(**trace_opts), row=r, col=c)

                elif diag_type == "box":
                    fig.add_trace(
                        go.Box(y=df[x_col], showlegend=False, marker=box_marker_style),
                        row=r,
                        col=c,
                    )
                else:  # diag_type == 'scatter'
                    # For diagonal scatter, we don't want a colorbar on every cell
                    diag_scatter_marker = scatter_marker_style.copy()
                    diag_scatter_marker["showscale"] = False
                    fig.add_trace(
                        go.Scatter(
                            x=df[x_col],
                            y=df[x_col],
                            mode="markers",
                            showlegend=False,
                            marker=diag_scatter_marker,
                        ),
                        row=r,
                        col=c,
                    )
            else:
                # Off-diagonal – check matrix_part rules
                if not is_visible_offdiag(r, c):
                    continue

                fig.add_trace(
                    go.Scatter(
                        x=df[x_col],
                        y=df[y_col],
                        mode="markers",
                        showlegend=False,
                        marker=scatter_marker_style,
                    ),
                    row=r,
                    col=c,
                )

    # Axis titles – bottom row & leftmost column only to avoid clutter
    for i, col_name in enumerate(valid_cols, start=1):
        fig.update_xaxes(title_text=col_name, row=n, col=i)
        fig.update_yaxes(title_text=col_name, row=i, col=1)

    # Remove gaps between histogram bars across cells
    if diag_type == "histogram" and show_diagonal:
        if diag_bar_width_fraction is not None:
            bargap = 1 - max(0.0, min(1.0, diag_bar_width_fraction))
            fig.update_layout(bargap=bargap)
        else:
            fig.update_layout(bargap=0.05) # Default spacing

    # Ensure every subplot has axis lines (borders)
    fig.update_xaxes(showline=True, mirror=True, linewidth=1)
    fig.update_yaxes(showline=True, mirror=True, linewidth=1)

    # Allow Plotly to resize dynamically
    fig.update_layout(autosize=True)
    fig.layout.pop("width", None)
    fig.layout.pop("height", None)

    # Apply shared styling / title
    fig.update_layout(_apply_common_layout(fig.layout, title=title))

    return json.loads(fig.to_json()) 

# ---------------------------------------------------------------------------
# Parallel Coordinates Plot
# ---------------------------------------------------------------------------
def parallel_coordinates_plot(
    df: "pd.DataFrame",
    columns: List[str],
    *,
    color_column: str | None = None,
    color_map: str | None = "Viridis",
    show_colorbar: bool = True,
    colorbar_title: str | None = None,
) -> Dict[str, Any]:
    """Return a Plotly parallel-coordinates trace wrapped in a figure dict.

    Parameters
    ----------
    df : pandas.DataFrame
        Source data.
    columns : list of str
        Dimensions to include (must exist in *df* and be numeric).
    color_column : str, optional
        If provided, values from this column encode the line colour.
    color_map : str, default 'Viridis'
        Name of a Plotly colourscale.
    show_colorbar : bool, default True
        Whether to display the colour-bar (only when *color_column* is given).
    colorbar_title : str, optional
        Title shown next to the colour-bar.  Defaults to *color_column*.
    """

    valid_cols = [c for c in columns if c in df.columns]
    if len(valid_cols) < 2:
        raise ValueError("parallel_coordinates_plot requires at least two valid columns")

    # Build dimensions list
    dimensions = []
    for col in valid_cols:
        series = df[col]
        if not np.issubdtype(series.dtype, np.number):
            continue  # skip non-numeric columns
        dim = dict(label=col, values=series)
        dimensions.append(dim)

    if len(dimensions) < 2:
        raise ValueError("All provided columns are non-numeric – cannot build parallel-coordinates plot")

    line_kwargs: Dict[str, Any] = {}
    if color_column and color_column in df.columns:
        line_kwargs.update(
            color=df[color_column],
            colorscale=color_map,
            showscale=show_colorbar,
            cmin=float(df[color_column].min()),
            cmax=float(df[color_column].max()),
            colorbar=dict(
                title=dict(
                    text=colorbar_title or color_column,
                    font=dict(
                        weight='normal'  # Explicitly set to normal weight
                    )
                ),
                tickfont=dict(
                    weight='normal'  # Also set normal weight for tick labels
                )
            ),
        )

    trace = go.Parcoords(dimensions=dimensions, line=line_kwargs)
    fig = go.Figure(data=[trace])
    
    # Apply common layout with custom margin for parallel coordinates
    layout = _apply_common_layout(go.Layout())
    layout.update(
        margin=dict(t=50, b=50),  # Extra top margin for column labels
    )
    fig.update_layout(layout)

    return json.loads(fig.to_json()) 