from __future__ import annotations

from typing import List, Optional

from pydantic import BaseModel, Field


class DatasetColumns(BaseModel):
    dataset: str = Field(..., description="File name inside DATA_DIR")
    x_column: str
    y_column: str


class LinePlotRequest(DatasetColumns):
    color: Optional[str] = None
    name: Optional[str] = None


class ScatterPlotRequest(DatasetColumns):
    color: Optional[str] = None
    name: Optional[str] = None


class HistogramPlotRequest(BaseModel):
    dataset: str
    column: str  # single column
    bins: int = 10
    show_fit: bool = False
    color: Optional[str] = None
    name: Optional[str] = None


class BarPlotRequest(BaseModel):
    dataset: str
    x_column: str
    y_columns: List[str]  # allow multiple series for stacking/grouping
    stacked: bool = False
    names: Optional[List[str]] = None 