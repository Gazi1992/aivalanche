"""Core data-access utilities used by the FastAPI layer (and potentially other front-ends).

This is a *stripped-down* version of the original ``DataHandler`` that had PyQt6
async helpers.  Here we only keep synchronous helpers because the API server is
already asynchronous at the *request* level and runs outside any Qt event loop.
"""
from __future__ import annotations

import logging
import os
from pathlib import Path
from functools import lru_cache
from typing import List, Optional

import pandas as pd

logger = logging.getLogger(__name__)

# Project root sits two levels up (core/ -> backend/ -> project root)
DATA_DIR: Path = Path(__file__).resolve().parents[2] / "data"


# ---------------------------------------------------------------------------
# Public helpers
# ---------------------------------------------------------------------------

@lru_cache(maxsize=128)
def load_dataset(name: str, data_dir: Optional[Path] = None) -> pd.DataFrame:
    """Return *name* (relative file name) as a pandas DataFrame.

    The result is cached (LRU) so repeated calls for the same file are fast.
    Raises ``FileNotFoundError`` if the path does not exist, or ``ValueError``
    for unsupported extensions.
    """
    directory = data_dir or DATA_DIR
    file_path = Path(directory) / name

    if not file_path.exists():
        raise FileNotFoundError(f"Dataset not found: {file_path}")

    ext = file_path.suffix.lower()
    logger.debug("Loading dataset '%s' (ext=%s)", name, ext)

    if ext == ".csv":
        return pd.read_csv(file_path)
    if ext in {".xls", ".xlsx"}:
        return pd.read_excel(file_path)
    if ext == ".json":
        return pd.read_json(file_path)

    raise ValueError(f"Unsupported data format: {ext}")


def available_datasets(data_dir: Optional[Path] = None) -> List[str]:
    """Return the list of dataset files present in *data_dir*.

    Only returns extensions that :pyfunc:`load_dataset` supports.
    """
    directory = data_dir or DATA_DIR
    if not directory.exists():
        logger.warning("DATA_DIR does not exist: %s", directory)
        return []

    allowed = {".csv", ".json", ".xls", ".xlsx"}
    return [f.name for f in directory.iterdir() if f.suffix.lower() in allowed] 