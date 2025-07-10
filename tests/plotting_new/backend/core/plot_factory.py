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

__all__ = [
    "line_plot",
    "scatter_plot",
    "histogram_plot",
    "bar_plot",
]


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
# Line plot
# ---------------------------------------------------------------------------

def line_plot(x: List, y: List, *, name: str | None = None, color: str | None = None) -> Dict[str, Any]:
    fig = go.Figure(
        data=[
            go.Scatter(x=x, y=y, mode="lines+markers", name=name, line=dict(color=color)),
        ]
    )
    fig.update_layout(_apply_common_layout(go.Layout()))
    import json
    return json.loads(fig.to_json())


# ---------------------------------------------------------------------------
# Scatter plot
# ---------------------------------------------------------------------------

def scatter_plot(x: List, y: List, *, name: str | None = None, color: str | None = None) -> Dict[str, Any]:
    fig = go.Figure(
        data=[
            go.Scatter(x=x, y=y, mode="markers", name=name, marker=dict(color=color)),
        ]
    )
    fig.update_layout(_apply_common_layout(go.Layout()))
    import json
    return json.loads(fig.to_json())


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
    import json
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
    import json
    return json.loads(fig.to_json()) 