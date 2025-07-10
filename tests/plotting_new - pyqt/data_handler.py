"""
Data handler for the visualization tool.
Loads and processes data from various sources.
"""
import os
import sys
import pandas as pd
import logging
from typing import Dict, Tuple, Optional, List, Any, Callable, Set

# Qt imports for asynchronous loading
from PyQt6.QtCore import QObject, pyqtSignal, QThread, QTimer

logger = logging.getLogger(__name__)

# -----------------------------------------------------------------------------
# Internal worker for background data loading
# -----------------------------------------------------------------------------

class _DataLoadWorker(QObject):
    """Worker object that reads a single data *source* in a background thread."""

    finished = pyqtSignal(str, object)  # source, pd.DataFrame | None

    def __init__(self, source: str):
        super().__init__()
        self._source = source

    def run(self):  # slot connected to thread.started
        df = DataHandler._read_source(self._source)
        # Emit on worker's thread; Qt signal will marshal back to UI thread if connected across threads
        self.finished.emit(self._source, df)

# -----------------------------------------------------------------------------
# Public DataHandler API
# -----------------------------------------------------------------------------

class DataHandler:
    """Handles loading and processing data from various sources."""

    def __init__(self):
        self.data_cache: Dict[str, pd.DataFrame] = {}
        # Keep references to live QThreads to avoid premature GC
        self._threads: Set[QThread] = set()

    # --------------------------------- Utility ---------------------------------

    @staticmethod
    def _read_source(source: str) -> Optional[pd.DataFrame]:
        """Read *source* synchronously and return a DataFrame or *None* on error."""
        file_ext = os.path.splitext(source)[1].lower()

        try:
            if file_ext == ".csv":
                return pd.read_csv(source)
            if file_ext in [".xls", ".xlsx"]:
                return pd.read_excel(source)
            if file_ext == ".json":
                return pd.read_json(source)
            logger.error(
                "Unsupported file format: '%s' for source: %s", file_ext, source
            )
            return None
        except FileNotFoundError:
            logger.error("Data source not found during load attempt: %s", source)
            return None
        except pd.errors.EmptyDataError:
            logger.warning("Data source file is empty: %s", source)
            return None
        except Exception as exc:  # pragma: no cover – generic catch
            logger.error("Error loading data from %s: %s", source, exc, exc_info=True)
            return None

    # -------------------------------- Sync API ---------------------------------

    def load_data(self, source: str) -> Optional[pd.DataFrame]:
        """Synchronous data loading with caching (existing behaviour)."""
        if source in self.data_cache:
            return self.data_cache[source]

        if not os.path.exists(source):
            logger.error("Data source not found: %s", source)
            return None

        logger.info("Loading data from: %s", source)
        df = self._read_source(source)
        if df is not None:
            logger.info("Successfully loaded %d rows from %s", len(df), source)
            self.data_cache[source] = df
        return df

    # ------------------------------ Async API ----------------------------------

    def load_data_async(
        self,
        source: str,
        callback: Callable[[Optional[pd.DataFrame]], None],
    ) -> None:
        """Load *source* in a background thread and invoke *callback* (on the GUI thread).

        The *callback* receives the resulting ``pd.DataFrame`` or ``None`` if a problem
        occurred. If the data is already cached, *callback* is executed immediately
        via the Qt event loop (non-blocking).
        """
        if source in self.data_cache:
            logger.debug("Using cached data for source (async): %s", source)

            # Ensure we call the callback asynchronously to maintain contract
            QTimer.singleShot(0, lambda: callback(self.data_cache[source]))
            return

        if not os.path.exists(source):
            logger.error("Data source not found (async): %s", source)
            QTimer.singleShot(0, lambda: callback(None))
            return

        # ---------- Spin up worker thread ----------
        thread = QThread()
        worker = _DataLoadWorker(source)
        worker.moveToThread(thread)

        # Connect signals
        thread.started.connect(worker.run)

        def _on_finished(src: str, df):
            # Cache result then call user callback on main thread automatically
            if df is not None:
                self.data_cache[src] = df
            callback(df)

        worker.finished.connect(_on_finished)
        worker.finished.connect(thread.quit)
        worker.finished.connect(worker.deleteLater)
        thread.finished.connect(thread.deleteLater)

        # Keep reference so thread isn't GC'd.
        self._threads.add(thread)

        def _cleanup():
            self._threads.discard(thread)

        thread.finished.connect(_cleanup)

        thread.start()

    def get_plot_data(self, item_config: Dict) -> Tuple[Optional[List], Optional[List]]:
        """
        Extract x and y data from a data source based on item configuration.
        """
        item_id = item_config.get('id', 'unknown_item')
        source = item_config.get('source')
        x_column = item_config.get('x_column')
        y_column = item_config.get('y_column')

        if not all([source, x_column, y_column]):
             logger.error(f"Item '{item_id}' configuration missing required fields ('source', 'x_column', or 'y_column').")
             return None, None

        df = self.load_data(source)
        if df is None:
            # Error already logged by load_data
            return None, None

        if df.empty:
             logger.warning(f"Data source '{source}' for item '{item_id}' loaded successfully but is empty.")
             return [], []

        missing_cols = []
        if x_column not in df.columns:
            missing_cols.append(x_column)
        if y_column not in df.columns:
             missing_cols.append(y_column)

        if missing_cols:
            logger.error(f"Item '{item_id}': Column(s) {missing_cols} not found in data source '{source}'. Available columns: {list(df.columns)}")
            return None, None

        try:
            # A safer approach is to drop rows where EITHER x or y is NaN from the relevant subset
            df_clean = df[[x_column, y_column]].dropna()
            x_data_clean = df_clean[x_column].tolist()
            y_data_clean = df_clean[y_column].tolist()

            if len(x_data_clean) != len(df): # Check if any rows were dropped from original df
                 original_relevant_rows = len(df[[x_column, y_column]])
                 nan_count_in_pair = original_relevant_rows - len(df_clean)
                 if nan_count_in_pair > 0 :
                     logger.warning(f"Item '{item_id}': Dropped {nan_count_in_pair} row(s) from '{source}' due to NaN values in '{x_column}' or '{y_column}'.")

            if not x_data_clean: # Could be empty if all had NaNs or original was empty
                 logger.warning(f"Item '{item_id}': No valid data points remain in '{source}' for columns '{x_column}', '{y_column}' after dropping NaN values (or source was empty).")
                 return [], []

            # logger.debug(f"Extracted {len(x_data_clean)} data points for item '{item_id}' from '{source}'.") # Can be verbose
            return x_data_clean, y_data_clean

        except Exception as e:
             logger.error(f"Item '{item_id}': Error extracting data columns '{x_column}', '{y_column}' from '{source}': {e}", exc_info=True)
             return None, None

    def clear_cache(self):
        """Clears both the data cache and any finished worker threads list."""
        logger.info("Clearing data cache.")
        self.data_cache.clear()
