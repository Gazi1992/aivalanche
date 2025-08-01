# --- START OF FILE scale_norm.py ---

import numpy as np
import pandas as pd
import math
import logging
from typing import Any, Union, Dict, List, Optional # Adjusted imports

logger = logging.getLogger(__name__) # Logger for scaling/norm operations

# Global constant for symlog transform threshold
SYMLOG_THRESHOLD = 1e-6

# --- Parameter Transformation/Normalization utils ---

def scale_parameter_row(row: pd.Series) -> pd.Series:
    """
    Scale a single parameter row according to its transform type or data type.

    Applies log/neglog transformation to min/max/default for numeric types
    if specified by the 'transform' column.
    Applies index mapping (0 to N-1) for categorical types, storing the
    index range in min/max and the default's index in 'default'.

    Important: This function expects the *original* parameter definition row
    as input and modifies the min/max/default fields to their *scaled*
    representation. It preserves the original 'values' list for categoricals.

    Args:
        row (pd.Series): A row from the original parameters DataFrame. It must
                         contain columns like 'name', 'type', 'min', 'max',
                         'default', 'values', 'transform'.

    Returns:
        pd.Series: The row with min/max/default values potentially modified
                   to the scaled space. Other columns are passed through.

    Raises:
        ValueError: If required columns are missing, if values are invalid for
                    the specified transformation (e.g., non-positive for log),
                    or if categorical definition is invalid.
        TypeError: If input types for numeric operations are incorrect.
    """
    # Make a copy to avoid modifying the original Series if it came from apply
    # Ensures modifications don't affect other operations on the original df
    row = row.copy()

    # --- Input Validation ---
    required_cols = ['name', 'type', 'min', 'max', 'default', 'values', 'transform']
    if not all(col in row.index for col in required_cols):
        missing = [col for col in required_cols if col not in row.index]
        raise ValueError(f"Input row is missing required columns for scaling: {missing}")

    param_type = row.get('type', 'continuous') # Default to continuous if type somehow missing after validation
    transform = row.get('transform') # None, 'log', 'neglog'
    param_name = row.get('name', 'UNKNOWN')

    if param_type == 'continuous' or param_type == 'discrete':
        # Scaling only applies if transform is log/neglog for numeric types
        # Ensure min/max/default are numeric before scaling if applicable
        min_val_orig = row.get('min')
        max_val_orig = row.get('max')
        default_orig = row.get('default')

        # Attempt conversion to numeric, raising errors if conversion fails unexpectedly
        try:
            min_val_num = pd.to_numeric(min_val_orig, errors='raise')
            max_val_num = pd.to_numeric(max_val_orig, errors='raise')
            default_num = pd.to_numeric(default_orig, errors='raise')
        except (ValueError, TypeError) as e:
            # This should ideally be caught earlier in validation, but safeguard here
            raise TypeError(f"Parameter '{param_name}' (type: {param_type}) has non-numeric min/max/default "
                            f"('{min_val_orig}', '{max_val_orig}', '{default_orig}') required for scaling.") from e

        if transform == 'symlog': # Apply symmetric log transformation
            # Symlog can handle any real numbers
            row['min'] = np.sign(min_val_num) * np.log10(1 + np.abs(min_val_num) / SYMLOG_THRESHOLD)
            row['max'] = np.sign(max_val_num) * np.log10(1 + np.abs(max_val_num) / SYMLOG_THRESHOLD)
            row['default'] = np.sign(default_num) * np.log10(1 + np.abs(default_num) / SYMLOG_THRESHOLD)

        elif transform == 'log': # Apply log10 transformation
            # Check for non-positive values before log
            if min_val_num <= 0 or max_val_num <= 0 or default_num <= 0:
                 raise ValueError(f"Parameter '{param_name}' has non-positive min/max/default "
                                  f"({min_val_num}, {max_val_num}, {default_num}) but is marked for 'log' transform.")
            # Scaled values are the log10 of the originals
            row['min'] = np.log10(min_val_num)
            row['max'] = np.log10(max_val_num)
            row['default'] = np.log10(default_num)

        elif transform == 'neglog': # Apply -log10(-x) transformation
             # Check for non-negative values before neglog
            if min_val_num >= 0 or max_val_num >= 0 or default_num >= 0:
                 raise ValueError(f"Parameter '{param_name}' has non-negative min/max/default "
                                  f"({min_val_num}, {max_val_num}, {default_num}) but is marked for 'neglog' transform.")
            # Careful with signs and order: neglog maps larger negative numbers (closer to 0) to smaller scaled values
            # and smaller negative numbers (further from 0) to larger scaled values.
            # Scaled min corresponds to original max (closer to 0).
            # Scaled max corresponds to original min (further from 0).
            row['min'] = -np.log10(-min_val_num) # Scaled min derived from original max
            row['max'] = -np.log10(-max_val_num) # Scaled max derived from original min
            row['default'] = -np.log10(-default_num)
        else:
            # For linear scale, the scaled values are the same as the original numeric values
            row['min'] = min_val_num
            row['max'] = max_val_num
            row['default'] = default_num
            # Check if values are NaN (should not happen if type is numeric and validation passed)
            if pd.isna(row['min']) or pd.isna(row['max']) or pd.isna(row['default']):
                 if param_type == 'continuous' or (param_type == 'discrete' and pd.notna(row.get('step'))):
                     # This case indicates a potential issue upstream (validation)
                     logger.warning(f"Parameter '{param_name}' (type: {param_type}, scale: lin) has NaN min/max/default after numeric conversion.")
                     # raise ValueError(f"Parameter '{param_name}' (type: {param_type}, scale: lin) has missing numeric min/max/default required for scaling step.")


    elif param_type == 'categorical':
        categories = row['values']
        default_val = row['default']

        if not isinstance(categories, list) or not categories:
            raise ValueError(f"Categorical parameter '{param_name}' must have a non-empty 'values' list.")

        try:
            # Find the index of the default value using the type-aware function
            # The result is the scaled default value (its index)
            default_index = normalize_categorical_value(default_val, categories)
        except ValueError as e:
            # Add context to the error if default isn't found strictly
            raise ValueError(f"Default value error for categorical '{param_name}': {e}. Ensure default value matches an item in 'values' exactly (including type).") from e

        n_cats = len(categories)
        # Scaled representation is the index range [0, N-1]
        row['min'] = 0.0
        row['max'] = float(n_cats - 1) if n_cats > 1 else 0.0 # Max index is N-1 (or 0 if only 1 category)
        row['default'] = default_index # Default is the found index (float)
        # Ensure scale/transform are set appropriately for categorical index space
        row['scale'] = 'lin' # Categorical indices are linearly spaced
        row['transform'] = None # No log/neglog transform applies to indices
        # Keep the original 'values' list in the scaled row - crucial for denormalization/mapping back
        row['values'] = categories # Ensure it's the original list preserved

    # For other potential future types or errors (should be caught by validation)
    else:
         raise ValueError(f"Unsupported parameter type '{param_type}' encountered during scaling for '{param_name}'.")

    return row


def determine_scale(min_val: Any, max_val: Any) -> str:
    """
    Determine the appropriate scale type ('lin' or 'log') for a NUMERIC parameter
    based on its min and max values. Defaults to 'lin' if cannot determine or invalid.

    Args:
        min_val: The minimum value of the parameter.
        max_val: The maximum value of the parameter.

    Returns:
        str: 'lin' or 'log'.
    """
    # Check if inputs are valid numbers
    if not isinstance(min_val, (int, float)) or not isinstance(max_val, (int, float)) \
            or math.isnan(min_val) or math.isnan(max_val):
        return 'lin'
    # Handle edge cases
    if min_val == max_val: return 'lin' # Single point is linear
    if min_val <= 0 and max_val >= 0: return 'lin' # Crosses zero, must be linear
    if min_val == 0 or max_val == 0: return 'lin' # Includes zero, typically linear

    # Both positive or both negative
    try:
        # Use absolute values for ratio calculation
        abs_min = abs(min_val)
        abs_max = abs(max_val)
        # Ensure ratio is > 1 for easier comparison
        ratio = max(abs_max / abs_min, abs_min / abs_max)

        # Heuristic: if range spans more than ~2 orders of magnitude, suggest log
        if ratio > 100: return 'log'
        else: return 'lin'
    except ZeroDivisionError:
        # Should have been caught by earlier checks, but safeguard
        return 'lin'
    except Exception:
        # Catch any other math errors
        logger.warning(f"Error calculating scale ratio for min={min_val}, max={max_val}. Defaulting to 'lin'.")
        return 'lin'


def determine_transform(row: Dict[str, Any]) -> Optional[str]:
    """
    Determine the appropriate scaling transform ('log', 'neglog') for a NUMERIC
    parameter based on its scale ('log') and value range.

    Args:
        row (Dict[str, Any]): A dictionary representing a parameter, must contain
                              'type', 'scale', 'min', 'max'. Can also have
                              'values', 'step' for discrete checks.

    Returns:
        Optional[str]: 'log', 'neglog', or None if no transform is applicable.
    """
    param_type = row.get('type', 'continuous')
    scale = row.get('scale')

    # Transform only applies if scale is explicitly 'log'
    if scale != 'log':
        return None

    # Check if parameter type is potentially numeric
    is_numeric_compatible = False
    min_val = pd.to_numeric(row.get('min'), errors='coerce') # Coerce here for check
    max_val = pd.to_numeric(row.get('max'), errors='coerce')

    if param_type == 'continuous':
        if pd.notna(min_val) and pd.notna(max_val): is_numeric_compatible = True
    elif param_type == 'discrete':
        # Check if discrete has numeric definition (step or values) and valid min/max
        values = row.get('values'); step = row.get('step')
        if pd.notna(min_val) and pd.notna(max_val): # Need min/max for range check
            if isinstance(values, list) and any(isinstance(v, (int, float)) and not math.isnan(v) for v in values if v is not None):
                 is_numeric_compatible = True
            elif pd.notna(step):
                 is_numeric_compatible = True

    if not is_numeric_compatible:
        return None # Not numeric, cannot apply log/neglog

    # Check range for applicability of log/neglog/symlog
    if pd.isna(min_val) or pd.isna(max_val): return None # Invalid range
    if min_val > 0 and max_val > 0: return 'log'
    elif min_val < 0 and max_val < 0: return 'neglog'
    else:
        # Range crosses zero - use symlog transform
        return 'symlog'


def normalize_scale_value(scale_value: Any) -> Optional[str]:
    """
    Normalize a user-provided scale value to standard format ('lin' or 'log').

    Args:
        scale_value: The input scale value (e.g., "Linear", "log", "LOG").

    Returns:
        Optional[str]: 'lin', 'log', or None if input is not recognized.
    """
    if isinstance(scale_value, str):
        lowered = scale_value.strip().lower()
        if lowered in ['linear', 'lin']: return 'lin'
        elif lowered in ['logarithmic', 'log']: return 'log'
    # Return None if input is not a known string representation or not a string
    return None

# --- Normalization/Denormalization for Continuous/Discrete (Scaled Space <-> [0,1]) ---

def normalize_parameter_value(value: float, min_val: float, max_val: float) -> float:
    """
    Normalize a numeric parameter value (from its SCALED space) to the range [0, 1].

    Handles the case where min_val equals max_val. Clamps value to [min_val, max_val].

    Args:
        value (float): The value in the scaled space to normalize.
        min_val (float): The minimum bound of the scaled space.
        max_val (float): The maximum bound of the scaled space.

    Returns:
        float: The normalized value in the range [0, 1].

    Raises:
        TypeError: If inputs are not valid, non-NaN numbers.
    """
    # Input Type/Value Checks
    if not isinstance(value, (int, float)) or math.isnan(value):
         raise TypeError(f"Value must be a non-NaN number for normalization, got {type(value)} ('{value}')")
    if not isinstance(min_val, (int, float)) or math.isnan(min_val):
         raise TypeError(f"min_val must be a non-NaN number for normalization, got {type(min_val)}")
    if not isinstance(max_val, (int, float)) or math.isnan(max_val):
         raise TypeError(f"max_val must be a non-NaN number for normalization, got {type(max_val)}")
    if min_val > max_val:
         # This shouldn't happen if scaling/validation worked, but good to check
         logger.warning(f"Normalization min_val ({min_val}) > max_val ({max_val}). Results may be unexpected.")
         # Allow proceeding but results might be outside [0, 1] or inverted

    # Handle single-point range
    if np.isclose(min_val, max_val):
        # If the range is a single point, any value within tolerance maps to 0.5
        # Values outside tolerance are clamped first.
        if np.isclose(value, min_val): return 0.5
        # Decide how to handle values far from the single point? Clamp to 0.5 seems reasonable.
        # Or return 0.0 if below, 1.0 if above? 0.5 is common for single point case.
        logger.debug(f"Normalizing value {value} in a single-point range [{min_val}, {max_val}] -> 0.5")
        return 0.5 # Represents the middle of the conceptual [0,1] range

    # Clamp value to the range [min_val, max_val] before normalization
    clamped_value = max(min_val, min(max_val, float(value)))
    if clamped_value != value:
        logger.debug(f"Value {value} clamped to {clamped_value} for normalization in range [{min_val}, {max_val}]")

    # Perform min-max normalization
    try:
        normalized = (clamped_value - min_val) / (max_val - min_val)
        # Clamp output to [0, 1] to handle potential floating point inaccuracies
        return max(0.0, min(1.0, normalized))
    except ZeroDivisionError: # Should be caught by isclose, but safeguard
        logger.error(f"ZeroDivisionError during normalization despite min/max check: {min_val}, {max_val}")
        return 0.5


def denormalize_parameter_value(norm_value: float, min_val: float, max_val: float, clamp: bool = True) -> float:
    """
    Convert a normalized parameter value ([0, 1]) back to its SCALED numeric range.

    Handles the case where min_val equals max_val. Optionally clamps norm_value to [0, 1].

    Args:
        norm_value (float): The normalized value (should be between 0 and 1 if clamping).
        min_val (float): The minimum bound of the scaled space.
        max_val (float): The maximum bound of the scaled space.
        clamp (bool): If True (default), clamp the input norm_value to [0, 1] before denormalizing.
                      If False, use the raw norm_value, potentially resulting in outputs
                      outside the [min_val, max_val] range if norm_value is outside [0, 1].

    Returns:
        float: The denormalized value in the scaled space.

    Raises:
        TypeError: If inputs are not valid, non-NaN numbers.
    """
    # Input Type/Value Checks
    if not isinstance(norm_value, (int, float)) or math.isnan(norm_value):
         raise TypeError(f"norm_value must be a non-NaN number for denormalization, got {type(norm_value)}")
    if not isinstance(min_val, (int, float)) or math.isnan(min_val):
         raise TypeError(f"min_val must be a non-NaN number for denormalization, got {type(min_val)}")
    if not isinstance(max_val, (int, float)) or math.isnan(max_val):
         raise TypeError(f"max_val must be a non-NaN number for denormalization, got {type(max_val)}")
    if min_val > max_val:
         logger.warning(f"Denormalization min_val ({min_val}) > max_val ({max_val}). Results may be unexpected.")

    value_to_process = float(norm_value) # Start with the raw value

    # --- Conditional Clamping ---
    if clamp:
        clamped_norm_value = max(0.0, min(1.0, value_to_process))
        if clamped_norm_value != value_to_process:
             logger.debug(f"Normalized value {value_to_process} clamped to {clamped_norm_value} for denormalization.")
        value_to_process = clamped_norm_value # Use the clamped value
    # If clamp is False, value_to_process remains the original norm_value

    # Handle single-point range
    if np.isclose(min_val, max_val):
        # If clamping is enabled, any value maps to the single point.
        # If clamping is disabled, values outside [0,1] might conceptually map differently,
        # but mapping to the single point is the only sensible option here.
        return min_val

    # Perform denormalization using the (potentially unclamped) value
    denormalized = min_val + value_to_process * (max_val - min_val)
    return denormalized

# --- Normalization/Denormalization for Categorical (Original Value <-> Index) ---

def normalize_categorical_value(value: Any, categories: list) -> float:
    """
    Map an original categorical value to its corresponding float index.

    Uses strict type and value checking. Handles None correctly.

    Args:
        value: The original category value to map (can be any type).
        categories (list): The list of allowed categories in order.

    Returns:
        float: The float index of the value in the categories list.

    Raises:
        ValueError: If categories list is invalid or value is not found with strict check.
        TypeError: If categories is not a list.
    """
    if not isinstance(categories, list):
        raise TypeError("Categories must be provided as a list.")
    if not categories:
        raise ValueError("Categories list cannot be empty.")

    # --- STRICT TYPE/VALUE SEARCH ---
    found_index = -1
    for i, cat_item in enumerate(categories):
        # Handle None specifically first
        if value is None and cat_item is None:
            found_index = i
            break
        # Compare types AND values for non-None items
        # Allow direct type comparison for strictness
        elif cat_item is not None and value is not None and \
             type(value) is type(cat_item) and value == cat_item:
             # Note: Using 'is' for type comparison is very strict.
             # Consider `type(value) == type(cat_item)` if numpy types might be involved.
             # Let's stick to `is` for now, assuming standard Python types.
            found_index = i
            break

    if found_index != -1:
        return float(found_index)
    else:
        # Value not found with strict check. Provide informative error.
        try:
            value_repr = repr(value)
            value_type = type(value)
            cat_repr = repr(categories)
        except Exception: # Handle potential errors in repr()
            value_repr = str(value)
            value_type = type(value)
            cat_repr = str(categories)

        raise ValueError(f"Value {value_repr} (type: {value_type}) not found in allowed categories: {cat_repr} using strict type matching.")
    # --- END STRICT SEARCH ---


def denormalize_categorical_value(norm_value: float, categories: list) -> Any:
    """
    Convert a normalized value [0, 1] back to its original categorical value
    by mapping through the corresponding index.

    Args:
        norm_value (float): The normalized value (expected between 0 and 1).
        categories (list): The list of allowed categories in the original order.

    Returns:
        Any: The original categorical value corresponding to the normalized input.

    Raises:
        TypeError: If categories is not a list or norm_value is not numeric.
        ValueError: If categories list is empty.
    """
    if not isinstance(categories, list):
        raise TypeError("Categories must be provided as a list.")
    if not categories:
        raise ValueError("Categories list cannot be empty.")
    if not isinstance(norm_value, (int, float)) or math.isnan(norm_value):
         raise TypeError(f"norm_value must be a non-NaN number for categorical denormalization, got {type(norm_value)}")

    n = len(categories)

    # Handle single category case
    if n == 1:
        return categories[0]

    # Clamp normalized value to [0, 1]
    clamped_norm_value = max(0.0, min(1.0, float(norm_value)))

    # Calculate the float index corresponding to the normalized value
    # The scaled space for indices is [0, n-1]
    float_index = clamped_norm_value * (n - 1)

    # Round the float index to the nearest integer index
    int_index = round(float_index)

    # Clamp the integer index to ensure it's within the valid range [0, n-1]
    clamped_index = int(max(0, min(n - 1, int_index)))

    # Return the category at the determined index
    return categories[clamped_index]


# --- Row-wise Normalization (Operates on SCALED row -> Normalized Row) ---

def normalize_parameter_row(row: pd.Series) -> pd.Series:
    """
    Normalize a SCALED parameter row to the [0,1] range based on its type.

    Takes a row where min/max/default are already in the scaled space
    (e.g., log-transformed values or categorical indices) and normalizes
    these using the scaled min/max. Modifies 'min', 'max', and 'default'
    columns to 0.0, 1.0, and the normalized default respectively.
    Preserves the original 'values' list if present (for categoricals).

    Args:
        row (pd.Series): A row from the scaled parameters DataFrame. Must
                         contain 'type', 'min', 'max', 'default', 'name'.
                         Should also contain 'values' for categoricals.

    Returns:
        pd.Series: The row with min/max/default values normalized to [0, 1].

    Raises:
        TypeError: If scaled min/max/default are not numeric.
        ValueError: If essential columns are missing.
    """
    row = row.copy() # Work on a copy

    # --- Input Validation ---
    required_cols = ['type', 'min', 'max', 'default', 'name']
    if not all(col in row.index for col in required_cols):
        missing = [col for col in required_cols if col not in row.index]
        raise ValueError(f"Input row is missing required columns for normalization: {missing}")

    param_type = row.get('type', 'continuous')
    min_val_s = row['min']  # Scaled min
    max_val_s = row['max']  # Scaled max
    default_s = row['default'] # Scaled default
    param_name = row.get('name', 'UNKNOWN')

    # Ensure scaled values are numeric before normalization
    try:
        min_val_num = pd.to_numeric(min_val_s, errors='raise')
        max_val_num = pd.to_numeric(max_val_s, errors='raise')
        default_num = pd.to_numeric(default_s, errors='raise')
    except (ValueError, TypeError) as e:
        raise TypeError(f"Parameter '{param_name}' (type: {param_type}) has non-numeric scaled min/max/default "
                        f"('{min_val_s}', '{max_val_s}', '{default_s}') required for normalization.") from e

    # Normalize the scaled default value using the scaled min/max range
    normalized_default = normalize_parameter_value(default_num, min_val_num, max_val_num)

    # Update the row fields for the normalized space
    row['default'] = normalized_default
    row['min'] = 0.0
    row['max'] = 1.0

    # Preserve 'values' column if it exists (needed for categorical denormalization)
    if 'values' in row:
        pass # Keep existing value
    else:
        # Log if values missing, might be needed later
        if param_type == 'categorical':
             logger.warning(f"Original 'values' list missing in row for categorical '{param_name}' during normalization. Denormalization might fail.")
        # Add values=None if column doesn't exist? Or assume it should exist?
        # Let's assume it should exist if type is categorical based on earlier steps.

    return row


# --- Snapping for Discrete Parameters ---
def snap_discrete_value(value: Union[int, float], param_info: Dict[str, Any]) -> Union[int, float]:
    """
    Snaps a potentially float value (in original, potentially descaled space)
    to the nearest valid discrete numeric value based on the ORIGINAL parameter
    definition provided in `param_info`.

    Args:
        value (Union[int, float]): The numeric value to snap.
        param_info (Dict[str, Any]): A dictionary containing the original
            parameter definition. Must include 'type' ('discrete'), 'name',
            and either 'values' (a list of numbers) or
            'step', 'min', 'max' (all numeric).

    Returns:
        Union[int, float]: The snapped value, matching the type of the
                           original definition where possible (int for int step/min).

    Raises:
        TypeError: If value is not numeric or param_info is missing required keys
                   or contains non-numeric definitions where numbers are expected.
        ValueError: If discrete definition is invalid (e.g., no values/step,
                    negative step, min > max).
    """
    param_name = param_info.get('name', 'UNKNOWN')
    param_type = param_info.get('type')

    # Basic checks
    if param_type != 'discrete':
        logger.warning(f"snap_discrete_value called for non-discrete param '{param_name}'. Returning original value.")
        return value
    if not isinstance(value, (int, float)) or math.isnan(value):
        raise TypeError(f"Value to snap must be a non-NaN number, got {type(value)} ('{value}') for {param_name}")

    value_f = float(value) # Work with float internally

    # Get definition details using standard keys ONLY
    values_list = param_info.get('values')
    step = param_info.get('step')
    min_val = param_info.get('min')
    max_val = param_info.get('max')

    # --- Snap based on 'values' list ---
    if isinstance(values_list, list):
        # Filter for valid numeric values in the list
        numeric_values = [v for v in values_list if isinstance(v, (int, float)) and not math.isnan(v)]
        if not numeric_values:
             raise ValueError(f"Cannot snap value for '{param_name}': No numeric values found in 'values' list: {values_list}")

        # Find the closest value in the list
        # Use float comparison for finding minimum distance
        closest_val = min(numeric_values, key=lambda x: abs(float(x) - value_f))

        # Return the closest value, preserving its original type if possible
        return closest_val # Return the item directly from the list


    # --- Snap based on 'step' ---
    elif pd.notna(step):
        # Ensure min, max, step are numeric
        try:
            min_val_f = float(min_val)
            max_val_f = float(max_val)
            step_f = float(step)
        except (TypeError, ValueError) as e:
             # Reference the standard keys in the error message
             raise TypeError(f"Cannot snap value for '{param_name}': Non-numeric or missing min/max/step ({min_val}, {max_val}, {step}) in definition for step-based discrete.") from e

        # Validate step and range
        if step_f <= 0:
            raise ValueError(f"Step must be positive for parameter '{param_name}', got {step_f}.")
        if min_val_f > max_val_f:
            # Allow equality for single-point discrete defined by step
            if not np.isclose(min_val_f, max_val_f):
                raise ValueError(f"Min ({min_val_f}) cannot be greater than Max ({max_val_f}) for step-defined discrete '{param_name}'.")
            else: # If min == max, the only valid value is min_val_f
                 return min_val_f


        # Calculate nearest step multiple from min_val
        # Add a small epsilon to handle floating point precision near step boundaries
        steps = round((value_f - min_val_f) / step_f)
        snapped_value = min_val_f + steps * step_f

        # Clamp the snapped value strictly to the [min_val, max_val] range
        # Use a small tolerance for comparison to avoid float issues at boundaries
        epsilon = 1e-9
        if snapped_value < min_val_f - epsilon: snapped_value = min_val_f
        if snapped_value > max_val_f + epsilon: snapped_value = max_val_f
        # Final clamp for safety
        snapped_value = max(min_val_f, min(max_val_f, snapped_value))


        # Return as integer if original min/step were integers
        # Check types directly from the param_info dictionary using standard keys
        orig_min_type = type(param_info.get('min'))
        orig_step_type = type(param_info.get('step'))
        if orig_min_type is int and orig_step_type is int:
            return int(round(snapped_value)) # Round carefully before int conversion
        else:
            return float(snapped_value)
    else:
         # Invalid definition if neither values nor step is provided correctly
         raise ValueError(f"Discrete parameter '{param_name}' has an invalid definition: lacks both valid 'values' list and numeric 'step'.")

# --- END OF FILE scale_norm.py ---
