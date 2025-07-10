"""
Utilities for calculating layout properties, like grid dimensions.
"""
import logging
import math
from typing import Tuple, Dict, Optional, Any

logger = logging.getLogger(__name__)

def calculate_grid_dimensions(num_items: int) -> Tuple[int, int]:
    """
    Calculate reasonably balanced grid dimensions.
    Tries to keep the grid close to square and prefers wider over taller for some common small N.
    """
    if num_items <= 0: return (0, 0)
    if num_items == 1: return (1, 1)
    if num_items == 2: return (1, 2)
    if num_items == 3: return (1, 3)
    if num_items == 4: return (2, 2)
    if num_items <= 6: return (2, 3) # For 5 or 6 items
    if num_items <= 8: return (2, 4) # For 7 or 8 items
    if num_items == 9: return (3, 3)
    if num_items <= 12: return (3, 4) # For 10, 11, or 12 items

    # Generic approach for larger numbers:
    # Start by aiming for something close to a square
    cols = math.ceil(math.sqrt(num_items))
    rows = math.ceil(num_items / cols)

    # Refinement: Check if reducing columns by 1 and increasing rows is better (closer to square)
    # This helps avoid overly wide layouts if num_items is, e.g., 17 (sqrt ~4.12 -> 5 cols, 4 rows)
    # vs (4 cols, 5 rows)
    if cols > 1: # Ensure we don't go to 0 columns
        alt_cols = cols - 1
        alt_rows = math.ceil(num_items / alt_cols)
        # Prefer the layout that is closer to a 1:1 aspect ratio (rows/cols or cols/rows closer to 1)
        # This can be checked by comparing abs(aspect_ratio - 1)
        current_aspect_ratio_metric = abs(rows / cols - 1)
        alt_aspect_ratio_metric = abs(alt_rows / alt_cols - 1)

        if alt_aspect_ratio_metric < current_aspect_ratio_metric:
            rows, cols = alt_rows, alt_cols
        # If they are equally "square", prefer wider (more columns) if rows and cols are different
        elif alt_aspect_ratio_metric == current_aspect_ratio_metric and rows != cols and alt_cols > cols:
             rows, cols = alt_rows, alt_cols


    return (int(rows), int(cols))


def determine_grid_dimensions(num_items: int, grid_config: Optional[Dict[str, Any]]) -> Tuple[int, int]:
    """
    Determines the grid dimensions (rows, cols).
    Prioritizes valid config values, then calculates based on num_items.
    """
    if num_items <= 0:
        return 0, 0

    rows_cfg: Optional[int] = None
    cols_cfg: Optional[int] = None
    final_rows: int
    final_cols: int

    if grid_config:
        rows_raw = grid_config.get('rows')
        cols_raw = grid_config.get('cols')
        try:
             rows_cfg = int(rows_raw) if rows_raw is not None else None
             cols_cfg = int(cols_raw) if cols_raw is not None else None
             if rows_cfg is not None and rows_cfg <= 0:
                 logger.warning(f"Invalid config: 'rows' ({rows_cfg}) must be positive. Ignoring.")
                 rows_cfg = None
             if cols_cfg is not None and cols_cfg <= 0:
                 logger.warning(f"Invalid config: 'cols' ({cols_cfg}) must be positive. Ignoring.")
                 cols_cfg = None
        except (ValueError, TypeError):
             logger.warning(f"Invalid non-integer grid dimensions in config: rows='{rows_raw}', cols='{cols_raw}'. Ignoring.")
             rows_cfg = None; cols_cfg = None
    # else: logger.debug("No grid_layout config provided for dimension hints.") # Reduced

    if rows_cfg is not None and cols_cfg is not None:
        # logger.debug(f"Grid dimensions found in config: rows={rows_cfg}, cols={cols_cfg}") # Reduced
        if rows_cfg * cols_cfg >= num_items:
            final_rows, final_cols = rows_cfg, cols_cfg
            logger.info(f"Using grid dimensions from configuration: {final_rows}x{final_cols}")
        else:
            logger.warning(f"Provided grid ({rows_cfg}x{cols_cfg}) is too small for {num_items} items. Calculating balanced dimensions.")
            final_rows, final_cols = calculate_grid_dimensions(num_items)
            logger.info(f"Calculated grid dimensions: {final_rows}x{final_cols}")
    elif rows_cfg is not None:
        # logger.debug(f"Only 'rows' ({rows_cfg}) provided in config.") # Reduced
        final_rows = rows_cfg
        final_cols = math.ceil(num_items / final_rows)
        logger.info(f"Using {final_rows} rows (from config), calculated {final_cols} columns. Grid: {final_rows}x{final_cols}")
    elif cols_cfg is not None:
        # logger.debug(f"Only 'cols' ({cols_cfg}) provided in config.") # Reduced
        final_cols = cols_cfg
        final_rows = math.ceil(num_items / final_cols)
        logger.info(f"Using {final_cols} columns (from config), calculated {final_rows} rows. Grid: {final_rows}x{final_cols}")
    else:
        # logger.debug("Neither rows nor cols specified or valid in config. Calculating balanced dimensions.") # Reduced
        final_rows, final_cols = calculate_grid_dimensions(num_items)
        logger.info(f"Calculated grid dimensions: {final_rows}x{final_cols}")

    return final_rows, final_cols
