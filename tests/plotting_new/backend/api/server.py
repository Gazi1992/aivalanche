from __future__ import annotations

# Standard Library
import copy
import json
import logging
import os
from pathlib import Path
from typing import List

# Third-party
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import plotly.graph_objs as go

# ---------------------------------------------------------------------------
# Logging setup
# ---------------------------------------------------------------------------

import logging

_root_logger = logging.getLogger()
# On each fresh start, overwrite the log file (mode="w") so we get a clean snapshot.
if not any(isinstance(h, logging.FileHandler) for h in _root_logger.handlers):
    file_handler = logging.FileHandler("backend_debug.log", mode="w", encoding="utf-8")
    file_handler.setFormatter(
        logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s")
    )
    _root_logger.addHandler(file_handler)
    _root_logger.setLevel(logging.DEBUG)

# Plot factory
from backend.core.plot_factory import (
    histogram_plot,
    bar_plot,
    scatter_matrix_plot,
)
# Dashboard builder
from backend.core.dashboard_builder import build_dashboard

# Schemas
from backend.api.schemas import (
    LinePlotRequest,
    ScatterPlotRequest,
    HistogramPlotRequest,
    BarPlotRequest,
)

# Local modules
from backend.core.data_handler import load_dataset, available_datasets


# ----------------------------------------------------------------------------
# Configuration
# ----------------------------------------------------------------------------

# Directory is taken from data_handler when imported
from backend.core.data_handler import DATA_DIR


# ----------------------------------------------------------------------------
# Pydantic models (request/response schemas)
# ----------------------------------------------------------------------------

# (old simple request kept for backward compat)
class SimpleBarPlotRequest(BaseModel):
    dataset: str
    x_column: str
    y_column: str


# ----------------------------------------------------------------------------
# FastAPI application & middleware
# ----------------------------------------------------------------------------

app = FastAPI(title="Aivalanche Backend API", version="0.1.0")

# Allow local Vite dev server and Electron file:// origin
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173", "*"],  # loosen when needed
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/config", summary="Get the full UI configuration")
def get_config():
    """
    Loads and returns the dashboard configuration from a default file.
    This is the primary endpoint for the frontend to fetch its layout and data sources.
    """
    # For simplicity, we'll hardcode the default config file.
    # This could be made dynamic (e.g., from a query parameter) if needed.
    config_name = "sample_config.json"
    config_path = (DATA_DIR / "configs" / config_name).resolve()

    if not config_path.exists():
        raise HTTPException(404, detail=f"Default config file '{config_name}' not found.")

    try:
        # The dashboard builder now handles loading, validation, and structuring.
        dashboard_json = build_dashboard(config_path)

        # Also persist payload for front-end debugging (same as /dashboard route)
        try:
            sanitized = copy.deepcopy(dashboard_json)

            for fig_entry in sanitized.get("figures", []):
                if isinstance(fig_entry, dict):
                    layout = fig_entry.get("figure", {}).get("layout", {})
                    if isinstance(layout, dict):
                        layout.pop("template", None)

            payload_path = Path("frontend_payload.json")

            json_text = json.dumps(sanitized, ensure_ascii=False, indent=2)

            def _inline_xy_lists(text: str) -> str:
                lines = text.splitlines()
                out_lines: list[str] = []
                i = 0
                while i < len(lines):
                    line = lines[i]
                    stripped = line.lstrip()
                    if stripped.startswith("\"x\": [") or stripped.startswith("\"y\": ["):
                        indent = line[: len(line) - len(stripped)]
                        collected = stripped
                        i += 1
                        while i < len(lines):
                            next_line = lines[i]
                            collected += next_line.strip()
                            if next_line.strip().endswith("],") or next_line.strip().endswith("]"):
                                break
                            i += 1
                        out_lines.append(indent + collected)
                        i += 1
                    else:
                        out_lines.append(line)
                        i += 1
                return "\n".join(out_lines)

            json_text = _inline_xy_lists(json_text)
            payload_path.write_text(json_text, encoding="utf-8")
        except Exception as exc:
            logging.getLogger(__name__).error("Failed to write frontend payload from /config: %s", exc)

        return dashboard_json
    except Exception as e:
        logging.getLogger(__name__).error(f"Error building dashboard from {config_name}: {e}", exc_info=True)
        raise HTTPException(500, detail="Failed to process configuration.")


@app.get("/health", summary="Health check")
def health() -> dict[str, str]:
    """Return simple *ok* status so front-end can verify connection."""
    return {"status": "ok"}


@app.get("/datasets", response_model=List[str], summary="List available datasets")
def list_datasets() -> List[str]:
    """Return dataset filenames available in *data* directory."""
    return available_datasets()


@app.get("/datasets/{name}", summary="Preview a dataset")
def preview_dataset(name: str) -> dict:
    """Return the first 10 rows of *name* as JSON for quick preview."""
    file_path = DATA_DIR / name
    if not file_path.exists():
        raise HTTPException(404, detail="Dataset not found")

    try:
        df = load_dataset(name)
        return {"columns": df.columns.tolist(), "preview": df.head(10).to_dict(orient="records")}
    except FileNotFoundError:
        raise HTTPException(404, detail="Dataset not found")
    except Exception as exc:
        raise HTTPException(500, detail=str(exc)) from exc


# --------------------------- Existing simple bar (compat) -------------------

@app.post("/plot/bar", summary="Bar plot (simple) – kept for backward compat")
def bar_plot_simple(req: SimpleBarPlotRequest) -> dict:
    """Construct a Plotly *bar* figure on the server and return its *fig.to_json()* dict."""

    try:
        df = load_dataset(req.dataset)
    except FileNotFoundError:
        raise HTTPException(404, detail="Dataset not found")
    except Exception as exc:
        raise HTTPException(500, detail=f"Error loading dataset: {exc}") from exc

    if req.x_column not in df.columns or req.y_column not in df.columns:
        raise HTTPException(
            400,
            detail=f"Columns '{req.x_column}' or '{req.y_column}' not found in dataset. Available columns: {list(df.columns)}",
        )

    fig = go.Figure(
        data=[
            go.Bar(x=df[req.x_column].tolist(), y=df[req.y_column].tolist()),
        ],
        layout=go.Layout(title=f"Bar Plot of {req.y_column} vs {req.x_column}"),
    )

    # Return JSON representation directly so the client can feed into Plotly.newPlot
    return json.loads(fig.to_json())


# ====================== New full-featured plot endpoints =====================


@app.post("/plot/line", summary="Line plot")
def line_plot_endpoint(req: LinePlotRequest) -> dict:
    df = _safe_load(req.dataset)
    if req.x_column not in df.columns or req.y_column not in df.columns:
        raise HTTPException(400, detail="Invalid columns")
    fig = line_plot(df[req.x_column].tolist(), df[req.y_column].tolist(), name=req.name, color=req.color)
    return fig


@app.post("/plot/scatter", summary="Scatter plot")
def scatter_plot_endpoint(req: ScatterPlotRequest) -> dict:
    df = _safe_load(req.dataset)
    if req.x_column not in df.columns or req.y_column not in df.columns:
        raise HTTPException(400, detail="Invalid columns")
    fig = scatter_plot(df[req.x_column].tolist(), df[req.y_column].tolist(), name=req.name, color=req.color)
    return fig


@app.post("/plot/histogram", summary="Histogram plot")
def histogram_plot_endpoint(req: HistogramPlotRequest) -> dict:
    df = _safe_load(req.dataset)
    if req.column not in df.columns:
        raise HTTPException(400, detail="Invalid column")
    values = df[req.column].dropna().tolist()
    fig = histogram_plot(values, bins=req.bins, show_fit=req.show_fit, name=req.name, color=req.color)
    return fig


@app.post("/plot/bar/full", summary="Bar plot (multi / stacked)")
def bar_plot_endpoint(req: BarPlotRequest) -> dict:
    df = _safe_load(req.dataset)
    if req.x_column not in df.columns:
        raise HTTPException(400, detail="Invalid x column")

    missing = [col for col in req.y_columns if col not in df.columns]
    if missing:
        raise HTTPException(400, detail=f"Missing y columns: {missing}")

    x_vals = df[req.x_column].tolist()
    ys = [df[col].tolist() for col in req.y_columns]
    fig = bar_plot(x_vals, ys, names=req.names, stacked=req.stacked)
    return fig


# --------------------------- Dashboard from config -------------------------








@app.get("/dashboard/{config_name}", summary="Render full dashboard from config")
def dashboard(config_name: str):
    """Return figures generated from *config_name* (looked up in data/configs)."""
    config_path = (DATA_DIR / "configs" / config_name).resolve()
    if not config_path.exists():
        raise HTTPException(404, detail="Config not found")

    dashboard_json = build_dashboard(config_path)
    import json, logging

    # -------------------------------------------------------------------
    # Persist full payload for front-end debugging
    # -------------------------------------------------------------------
    # The regular backend_debug.log only stores a short snippet of the
    # dashboard JSON to avoid megabytes of noise.  For in-depth inspection
    # we now write the complete payload to a dedicated file that can be
    # opened separately without clogging the main log.  The file is
    # overwritten on each request so that it always reflects the most
    # recent response.
    try:
        # Deep-copy to avoid mutating the response sent back to the client
        sanitized = copy.deepcopy(dashboard_json)

        # Remove Plotly's large default template from each figure layout to keep the
        # logged payload compact and diff-friendly.
        for fig_entry in sanitized.get("figures", []):
            if isinstance(fig_entry, dict):
                layout = fig_entry.get("figure", {}).get("layout", {})
                if isinstance(layout, dict):
                    layout.pop("template", None)

        payload_path = Path("frontend_payload.json")
        # Pretty-print overall structure but flatten just the large x/y arrays
        json_text = json.dumps(sanitized, ensure_ascii=False, indent=2)

        def _inline_xy_lists(text: str) -> str:
            """Return *text* with any '"x": [...]' or '"y": [...]' arrays collapsed
            onto a single line while preserving indentation for everything else."""
            lines = text.splitlines()
            out_lines: list[str] = []
            i = 0
            while i < len(lines):
                line = lines[i]
                stripped = line.lstrip()
                if stripped.startswith("\"x\": [") or stripped.startswith("\"y\": ["):
                    indent = line[: len(line) - len(stripped)]
                    # Begin collecting until we reach the closing ']' (might be '],' or ']')
                    collected = stripped  # already has opening '['
                    i += 1
                    while i < len(lines):
                        next_line = lines[i]
                        collected += next_line.strip()
                        if next_line.strip().endswith("],") or next_line.strip().endswith("]"):
                            break
                        i += 1
                    # Append the compressed array line with original indent
                    out_lines.append(indent + collected)
                    i += 1  # move past the closing line
                else:
                    out_lines.append(line)
                    i += 1
            return "\n".join(out_lines)

        json_text = _inline_xy_lists(json_text)

        with payload_path.open("w", encoding="utf-8") as fp:
            fp.write(json_text)
    except Exception as exc:
        logging.getLogger(__name__).error("Failed to write frontend payload: %s", exc)

    # Keep short diagnostics in the regular debug log
    logging.getLogger(__name__).debug("Dashboard response size=%d bytes", len(json.dumps(dashboard_json)))
    logging.getLogger(__name__).debug("Dashboard snippet: %s", json.dumps(dashboard_json)[:500])
    return dashboard_json


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _safe_load(name: str):
    try:
        return load_dataset(name)
    except FileNotFoundError:
        raise HTTPException(404, detail="Dataset not found") 