# --- START OF FILE validation.py ---

import pandas as pd
import numpy as np
import math
import logging
from typing import TYPE_CHECKING

# Use TYPE_CHECKING to avoid runtime circular import errors
# while still allowing type checkers to see the Parameters type hint.
if TYPE_CHECKING:
    from .Parameters import Parameters

# Assuming utils.py is in the same directory or accessible in the python path
# If validation.py and utils.py are in a package, use relative imports:
from .scale_norm import determine_scale, normalize_scale_value, snap_discrete_value

logger = logging.getLogger(__name__) # Logger for validation logic

# Define expected columns and their potential types (copied for reference)
_expected_cols = {
    'name': str,
    'type': str, # 'continuous', 'discrete', 'categorical'
    'min': float,
    'max': float,
    'default': object, # Can be float, int, str, bool, None etc.
    'values': object, # List for discrete/categorical
    'step': float, # Float for discrete step
    'scale': str, # 'lin', 'log'
    'mode': str, # 'fixed', 'variable'
    'transform': str # 'log', 'neglog', 'symlog', None
}

def run_all_validations(params_obj: 'Parameters') -> None:
    """
    Run all validation and preprocessing steps in the correct order
    on the provided Parameters object's DataFrame.

    Modifies `params_obj.all_parameters` in place.

    Args:
        params_obj (Parameters): The Parameters instance to validate.

    Raises:
        ValueError: If critical validation checks fail.
    """
    # Operate directly on params_obj.all_parameters
    df = params_obj.all_parameters

    if df.empty:
        logger.warning("Validation skipped: Parameters DataFrame is empty.")
        # Ensure essential columns exist even if empty
        for col in _expected_cols:
            if col not in df.columns: df[col] = None
        # Reassign potentially modified empty df back (though likely unchanged)
        params_obj.all_parameters = df
        return

    # Call individual internal validation functions, passing the Parameters object
    _ensure_columns(params_obj)
    _check_type_values(params_obj)
    _check_min_max_order(params_obj) # Check numeric min/max after type check confirms they should be numeric
    _check_default_values(params_obj) # Check default after type/min/max are validated
    _check_mode_values(params_obj)
    _check_scale_values(params_obj) # Check/determine scale after min/max are potentially fixed
    _set_transform_types(params_obj) # Set transform based on final scale and range

    # No need to return df, as params_obj.all_parameters was modified in place


# --- Internal Validation and Setup Functions (Take Parameters instance as input) ---
# Added leading underscore to indicate internal use within this module

def _ensure_columns(params_obj: 'Parameters') -> None:
    """Ensure all expected columns exist, adding defaults if necessary."""
    df = params_obj.all_parameters # Work directly on the instance's DataFrame
    for col, dtype in _expected_cols.items():
        if col not in df.columns:
            default_value = None
            if col == 'type': default_value = 'continuous'
            elif col == 'mode': default_value = 'variable'
            elif col == 'scale': default_value = 'lin' # Default scale is lin
            df[col] = default_value

    # Ensure 'values' and 'default' are object type and handle NaNs
    for col in ['values', 'default']:
            if col in df.columns:
                if df[col].dtype != object:
                    try:
                        # Replace various NaN representations with None before converting to object
                        df[col] = df[col].fillna(np.nan).replace([np.nan], [None])
                        df[col] = df[col].astype(object)
                    except Exception as e:
                        logger.warning(f"Could not convert '{col}' column to object dtype: {e}.")
            elif col not in df.columns:
                df[col] = None
                df[col] = df[col].astype(object)

    # Ensure other columns have appropriate basic types (numeric or string)
    for col, dtype in _expected_cols.items():
            if col in df.columns and col not in ['values', 'default']:
                if dtype == float:
                    # Coerce to numeric, leave non-convertible as NaN
                    df[col] = pd.to_numeric(df[col], errors='coerce')
                elif dtype == str and df[col].dtype != object and df[col].dtype != str:
                    # Convert to string, handle pandas' <NA> if necessary
                    df[col] = df[col].astype(str).replace('nan', None).replace('<NA>', None)
    # No need to reassign df to params_obj.all_parameters, modification happens in place


def _check_type_values(params_obj: 'Parameters') -> None:
    """Validate the 'type' column and associated 'values'/'step'/'min'/'max'."""
    df = params_obj.all_parameters
    allowed_types = ['continuous', 'discrete', 'categorical']
    # Ensure 'type' exists and fill NaNs with default 'continuous'
    if 'type' not in df.columns: df['type'] = 'continuous'
    df['type'] = df['type'].fillna('continuous').astype(str)
    df['type'] = df['type'].replace(['nan', 'None', 'null'], 'continuous') # Replace string 'nan'/'None'/'null

    # Validate allowed types
    invalid_type_mask = ~df['type'].isin(allowed_types)
    if invalid_type_mask.any():
        invalid_names = df.loc[invalid_type_mask, 'name'].tolist()
        raise ValueError(f"Invalid 'type' specified for parameters: {invalid_names}. Allowed: {allowed_types}")

    # Ensure numeric step if column exists
    if 'step' in df.columns:
        df['step'] = pd.to_numeric(df['step'], errors='coerce')
    else: # Add step column if missing
            df['step'] = np.nan

    # Ensure 'values' column exists and is object type
    if 'values' not in df.columns: df['values'] = None
    df['values'] = df['values'].astype(object) # Re-ensure object type after potential load issues

    # Iterate and validate each parameter
    for index, row in df.iterrows():
        param_name = row['name']
        param_type = row['type']
        values = row['values'] # Should be list or None now
        step = row['step']     # Should be float or NaN
        min_val = row['min']   # Could be float or NaN
        max_val = row['max']   # Could be float or NaN

        # --- Clean 'values' list: handle potential NaNs inside lists ---
        if isinstance(values, list):
            values = [None if pd.isna(v) else v for v in values]
            # Store cleaned list back - USE .at for direct modification
            try: df.at[index, 'values'] = values
            except Exception as e: logger.error(f"Error setting cleaned 'values' for {param_name}: {e}"); raise e

        # --- Type-specific Validation ---
        min_val_num = pd.to_numeric(min_val, errors='coerce')
        max_val_num = pd.to_numeric(max_val, errors='coerce')

        if param_type == 'continuous':
            if values is not None or pd.notna(step):
                logger.warning(f"Param '{param_name}' (continuous): 'values'/'step' ignored. Resetting.")
                df.at[index, 'values'] = None
                df.at[index, 'step'] = np.nan
            if pd.isna(min_val_num) or pd.isna(max_val_num):
                    raise ValueError(f"Param '{param_name}' (continuous): Numeric 'min'/'max' required.")

        elif param_type == 'discrete':
            step_num = step # Already coerced to float or NaN
            has_values = isinstance(values, list) and len(values) > 0
            has_step = pd.notna(step_num) and step_num > 0

            if not has_values and not has_step:
                raise ValueError(f"Param '{param_name}' (discrete): Needs numeric 'values' list OR positive numeric 'step' + numeric 'min'/'max'.")
            if has_values and has_step:
                logger.warning(f"Param '{param_name}' (discrete): Both 'values' and 'step' provided. Using 'values'. Resetting step.")
                df.at[index, 'step'] = np.nan
                has_step = False # Update flag after reset

            if has_values:
                # Use cleaned values list
                non_none_values = [v for v in values if v is not None]
                # Check if *all* non-None values are numeric (int or float, excluding NaN)
                are_numeric = all(isinstance(v, (int, float)) and not math.isnan(v) for v in non_none_values)
                if not are_numeric and non_none_values: # If list has non-None items, they must be numeric
                        raise ValueError(f"Param '{param_name}' (discrete): 'values' list must contain only numeric items (or None). Got: {values}")
                # Infer min/max from values if not provided or invalid
                if non_none_values:
                        inferred_min = min(non_none_values)
                        inferred_max = max(non_none_values)
                        if pd.isna(min_val_num): df.at[index, 'min'] = inferred_min
                        if pd.isna(max_val_num): df.at[index, 'max'] = inferred_max
                else: # If values is empty or only None
                        if pd.isna(min_val_num): df.at[index, 'min'] = np.nan
                        if pd.isna(max_val_num): df.at[index, 'max'] = np.nan
                 # Update min_val_num/max_val_num if they were inferred
                min_val_num = pd.to_numeric(df.at[index, 'min'], errors='coerce')
                max_val_num = pd.to_numeric(df.at[index, 'max'], errors='coerce')

            # Re-evaluate step requirement after potentially using values
            if has_step: # Only check this if values weren't used or step wasn't reset
                if pd.isna(min_val_num) or pd.isna(max_val_num):
                        raise ValueError(f"Param '{param_name}' (discrete) with 'step': Needs numeric 'min'/'max'.")
                # Allow min == max for step-based discrete (represents a single valid point)
                if min_val_num > max_val_num:
                        raise ValueError(f"Param '{param_name}' (discrete) with 'step': 'min' ({min_val_num}) cannot be greater than 'max' ({max_val_num}).")


        elif param_type == 'categorical':
            if not isinstance(values, list) or not values: # Must be a non-empty list
                raise ValueError(f"Param '{param_name}' (categorical): Needs non-empty 'values' list.")
            if pd.notna(step):
                logger.warning(f"Param '{param_name}' (categorical): 'step' ignored. Resetting.")
                df.at[index, 'step'] = np.nan
            # Min/max are not relevant for categorical originals, set to NaN
            df.at[index, 'min'] = np.nan
            df.at[index, 'max'] = np.nan


def _check_min_max_order(params_obj: 'Parameters') -> None:
    """Check min/max order for numeric types (continuous/discrete with step)."""
    df = params_obj.all_parameters
    # Only apply to types where numeric min/max are strictly required and ordered
    numeric_mask = (df['type'] == 'continuous') | \
                    ( (df['type'] == 'discrete') & pd.notna(df['step']) )

    # Use already coerced numeric min/max if available, otherwise coerce again
    min_col = pd.to_numeric(df['min'], errors='coerce')
    max_col = pd.to_numeric(df['max'], errors='coerce')

    # Find indices where min/max are both valid numbers AND min > max
    indices_to_swap = df[
        numeric_mask & min_col.notna() & max_col.notna() & (min_col > max_col)
    ].index

    if not indices_to_swap.empty:
        swap_names = df.loc[indices_to_swap, 'name'].tolist()
        # Get original values at these indices before swapping
        min_vals_to_swap = df.loc[indices_to_swap, 'min'].copy()
        max_vals_to_swap = df.loc[indices_to_swap, 'max'].copy()
        # Perform the swap using .loc
        df.loc[indices_to_swap, 'min'] = max_vals_to_swap
        df.loc[indices_to_swap, 'max'] = min_vals_to_swap
        logger.info(f"Swapped min and max for parameters: {', '.join(swap_names)}")


def _check_default_values(params_obj: 'Parameters') -> None:
    """Check default values based on parameter type and range/values."""
    df = params_obj.all_parameters
    # Ensure 'default' column exists and is object type
    if 'default' not in df.columns: df['default'] = None
    # Ensure column exists before trying to set dtype
    if 'default' in df.columns:
        # Handle case where column might exist but be all NaN initially
        if df['default'].dtype != object and not df['default'].isnull().all():
            try:
                 df['default'] = df['default'].astype(object)
            except Exception as e:
                 logger.error(f"Could not convert 'default' column to object type: {e}")
                 # Potentially raise error here if conversion is critical?
        elif df['default'].isnull().all(): # If all NaN, ensure object type anyway
             df['default'] = df['default'].astype(object)


    # Helper to attempt type conversion (e.g., "true"->True, "1.0"->1.0)
    def try_convert_value(item):
            if isinstance(item, (bool, int, float, list)) or item is None: return item
            if isinstance(item, str):
                item_str = item.strip()
                if item_str.lower() == 'true': return True
                if item_str.lower() == 'false': return False
                if item_str.lower() in ['none', 'na', 'nan', '<na>', '', 'null']: return None
                try: return int(item_str)
                except ValueError:
                    try: return float(item_str)
                    except ValueError: return item_str # Keep as string if nothing else matches
            # Handle pandas NA if it slips through
            if pd.isna(item): return None
            return item # Return original for other types

    # Iterate and check/set defaults
    for index, row in df.iterrows():
        param_name = row['name']
        param_type = row['type']
        # Make sure to handle pd.NA correctly from row before try_convert_value
        default = row['default'] if pd.notna(row['default']) else None
        min_val = df.at[index, 'min'] # Use .at for direct access
        max_val = df.at[index, 'max']
        values = df.at[index, 'values'] # Already cleaned list or None
        step = df.at[index, 'step']     # Float or NaN
        set_default = False # Flag if default was auto-generated

        # --- Convert loaded default value type ---
        original_default_repr = repr(default)
        default = try_convert_value(default)
        if repr(default) != original_default_repr:
                logger.debug(f"Converted default for '{param_name}' from {original_default_repr} to {repr(default)}")
        # Handle potential NaN float default from loading/conversion explicitly
        if isinstance(default, float) and math.isnan(default): default = None

        # --- Set Default if Missing ---
        if default is None:
                set_default = True
                min_val_num = pd.to_numeric(min_val, errors='coerce')
                max_val_num = pd.to_numeric(max_val, errors='coerce')
                if param_type == 'continuous':
                    if pd.isna(min_val_num) or pd.isna(max_val_num): raise ValueError(f"Cannot set default for '{param_name}': continuous needs numeric min/max.")
                    default = (min_val_num + max_val_num) / 2
                elif param_type == 'discrete':
                    if isinstance(values, list) and values:
                        # Get non-None numeric values only
                        numeric_non_none = [v for v in values if isinstance(v, (int, float)) and not math.isnan(v)]
                        if not numeric_non_none: raise ValueError(f"Cannot set default for discrete '{param_name}': 'values' list has no valid numeric entries.")
                        # Take middle element of numeric values
                        default = numeric_non_none[len(numeric_non_none) // 2]
                    elif pd.notna(step):
                        if pd.isna(min_val_num) or pd.isna(max_val_num): raise ValueError(f"Cannot set default for '{param_name}': discrete with step needs numeric min/max.")
                        # Handle min == max case
                        if np.isclose(min_val_num, max_val_num):
                                default_candidate = min_val_num
                        else:
                                default_candidate = (min_val_num + max_val_num) / 2
                        # Snap the candidate default (snap_discrete_value needs dict)
                        # Construct snap_info using standard keys and values from the current scope
                        snap_info = {
                            'type': 'discrete',
                            'name': param_name,
                            'min': min_val_num,  # Use numeric min for this row
                            'max': max_val_num,  # Use numeric max for this row
                            'step': step,       # Use step for this row
                            'values': values     # Use values list for this row (might be None)
                        }
                        default = snap_discrete_value(default_candidate, snap_info)
                    else: raise ValueError(f"Cannot set default for discrete '{param_name}': No valid 'values' list or 'step' defined.")
                elif param_type == 'categorical':
                    if not isinstance(values, list) or not values: raise ValueError(f"Cannot set default for '{param_name}': No 'values' defined.")
                    # Filter out None values for default selection unless it's the only option
                    non_none_values = [v for v in values if v is not None]
                    if non_none_values: default = non_none_values[0] # Pick first non-None
                    elif None in values: default = None # Only None is available
                    else: raise ValueError(f"Cannot set default for categorical '{param_name}': 'values' list is empty or invalid after filtering.")
                logger.info(f"Default value not provided for '{param_name}'. Set to '{default}'.")

        # --- Validate existing or newly set default ---
        validation_passed = False
        # Re-fetch numeric min/max in case they were inferred for discrete/values
        min_val_num = pd.to_numeric(df.at[index, 'min'], errors='coerce')
        max_val_num = pd.to_numeric(df.at[index, 'max'], errors='coerce')

        if param_type == 'continuous':
            default_num = pd.to_numeric(default, errors='coerce')
            if pd.isna(default_num): raise ValueError(f"Param '{param_name}' (continuous): Default '{default}' must be numeric.")
            # Check bounds (use original min/max for warning)
            if pd.notna(min_val_num) and default_num < min_val_num: logger.warning(f"Default {default_num} < min {min_val_num} for '{param_name}'. Clamping check occurs later if needed.")
            if pd.notna(max_val_num) and default_num > max_val_num: logger.warning(f"Default {default_num} > max {max_val_num} for '{param_name}'. Clamping check occurs later if needed.")
            validation_passed = True

        elif param_type == 'discrete':
                default_num = pd.to_numeric(default, errors='coerce') # Use potentially updated default
                if pd.isna(default_num): raise ValueError(f"Param '{param_name}' (discrete): Default '{default}' must be numeric.")

                if isinstance(values, list) and values: # Using values from loop scope
                    # Check if default is close to any numeric value in the list
                    is_in_list = any(isinstance(v, (int, float)) and not math.isnan(v) and np.isclose(v, default_num, atol=1e-9) for v in values)
                    if not is_in_list: raise ValueError(f"Param '{param_name}' (discrete): Default {default_num} not found (within tolerance) in 'values': {values}.")
                    validation_passed = True
                elif pd.notna(step): # Using step from loop scope
                    # Check bounds (use numeric min/max for this row)
                    if pd.notna(min_val_num) and default_num < min_val_num: logger.warning(f"Default {default_num} < min {min_val_num} for '{param_name}' (step).")
                    if pd.notna(max_val_num) and default_num > max_val_num: logger.warning(f"Default {default_num} > max {max_val_num} for '{param_name}' (step).")
                    # Check if default aligns with step, snap if necessary
                    # Construct snap_info using standard keys and values from the current scope
                    snap_info = {
                        'type': 'discrete',
                        'name': param_name,
                        'min': min_val_num,  # Use numeric min for this row
                        'max': max_val_num,  # Use numeric max for this row
                        'step': step,       # Use step for this row
                        'values': values     # Use values list for this row (might be None)
                    }
                    # Snap the *current* default value to check alignment
                    snapped_check_default = snap_discrete_value(default_num, snap_info)
                    if not np.isclose(default_num, snapped_check_default, atol=1e-9):
                        logger.warning(f"Provided default {default_num} for step-discrete '{param_name}' doesn't align with step {step}. Snapping to {snapped_check_default}.")
                        default = snapped_check_default # Update default to snapped value
                        set_default = True # Mark as modified
                    validation_passed = True
                else:
                    # Should not happen if _check_type_values worked
                    raise ValueError(f"Invalid state for discrete '{param_name}' during default check.")

        elif param_type == 'categorical':
                if not isinstance(values, list): raise ValueError(f"Categorical param '{param_name}' missing 'values' list during default check.")
                # Robust check if default exists in the values list (handles None) using strict type/value match
                found_strict = False
                for cat_val in values: # Using values from loop scope
                    # Handle None specifically
                    if default is None and cat_val is None:
                        found_strict = True
                        break
                    # Compare types AND values for non-None items
                    elif cat_val is not None and default is not None and \
                        type(default) is type(cat_val) and default == cat_val:
                        found_strict = True
                        break

                if not found_strict:
                    # Check if float version exists (e.g. 1.0 vs 1) only if not found strictly
                    try_float_match = False
                    if isinstance(default, (int, float)) and not isinstance(default, bool): # Exclude bools from float check
                        for v in values:
                            # Check float match carefully avoiding type errors and bools
                            if isinstance(v, (int, float)) and not isinstance(v, bool) and np.isclose(default, v):
                                try_float_match = True; break
                    if not try_float_match:
                        raise ValueError(f"Param '{param_name}' (categorical): Default value {repr(default)} (type: {type(default)}) not found in the allowed 'values': {repr(values)} using strict matching.")
                validation_passed = True


        if not validation_passed:
                # This should ideally not be reached if logic above is correct
                raise RuntimeError(f"Default value validation failed unexpectedly for '{param_name}'. Default: {repr(default)}")

        # Store the validated (potentially type-converted or snapped) default back using .at
        df.at[index, 'default'] = default


def _check_mode_values(params_obj: 'Parameters') -> None:
    """Check and normalize 'mode' values."""
    df = params_obj.all_parameters
    if 'mode' not in df.columns:
        df['mode'] = 'variable'
        logger.info("Mode not provided. All set to 'variable'.")
    else:
        # Fill NaNs, convert to string, replace string 'nan'/'None'/'null'
        df['mode'] = df['mode'].fillna('variable').astype(str).replace(['nan', 'None', 'null'], 'variable')
        valid_modes = ['fixed', 'variable']
        invalid_mask = ~df['mode'].isin(valid_modes)
        if invalid_mask.any():
            invalid_names = df.loc[invalid_mask, 'name'].tolist()
            df.loc[invalid_mask, 'mode'] = 'variable' # Force invalid modes to variable
            logger.warning(f"Invalid mode for params: {invalid_names}. Set to 'variable'.")


def _check_scale_values(params_obj: 'Parameters') -> None:
    """Check 'scale' values ('lin', 'log'), determine automatically if needed for numeric types."""
    df = params_obj.all_parameters
    if 'scale' not in df.columns: df['scale'] = None

    determined_count = 0
    fixed_count = 0
    for index, row in df.iterrows():
        scale = row['scale']
        param_type = row['type']
        param_name = row['name']
        min_val = row['min']
        max_val = row['max']

        # Scale ('lin'/'log') is primarily relevant for continuous and numeric discrete
        scale_relevant_type = False
        if param_type == 'continuous':
            scale_relevant_type = True
        elif param_type == 'discrete':
            # Check if discrete definition implies numeric range (step or numeric values)
            values = row['values']
            step = row['step']
            min_val_num = pd.to_numeric(min_val, errors='coerce')
            max_val_num = pd.to_numeric(max_val, errors='coerce')
            if isinstance(values, list) and any(isinstance(v, (int, float)) and not math.isnan(v) for v in values if v is not None):
                scale_relevant_type = True
            elif pd.notna(step) and pd.notna(min_val_num) and pd.notna(max_val_num):
                scale_relevant_type = True

        # --- Normalize or Determine Scale ---
        if scale_relevant_type:
            needs_determination = pd.isna(scale) or scale is None or str(scale).lower() in ['none', 'nan', '', 'null']
            if needs_determination:
                # Attempt to determine scale automatically based on numeric min/max
                min_val_num = pd.to_numeric(min_val, errors='coerce')
                max_val_num = pd.to_numeric(max_val, errors='coerce')
                if pd.notna(min_val_num) and pd.notna(max_val_num):
                    determined_scale = determine_scale(min_val_num, max_val_num)
                    df.at[index, 'scale'] = determined_scale
                    determined_count += 1
                else:
                    # Cannot determine if min/max are not numeric, default to 'lin'
                    df.at[index, 'scale'] = 'lin'
            else:
                # Validate provided scale
                normalized_scale = normalize_scale_value(scale) # Returns 'lin', 'log', or None
                if normalized_scale is None:
                    logger.warning(f"Invalid scale '{scale}' for '{param_name}'. Determining automatically.")
                    min_val_num = pd.to_numeric(min_val, errors='coerce')
                    max_val_num = pd.to_numeric(max_val, errors='coerce')
                    if pd.notna(min_val_num) and pd.notna(max_val_num):
                        df.at[index, 'scale'] = determine_scale(min_val_num, max_val_num)
                    else:
                        df.at[index, 'scale'] = 'lin'
                    fixed_count += 1
                elif normalized_scale != scale: # Store the normalized form ('Linear' -> 'lin')
                        df.at[index, 'scale'] = normalized_scale
        else: # Scale not relevant (e.g., categorical)
            if scale is not None and normalize_scale_value(scale) != 'lin':
                logger.warning(f"Scale '{scale}' ignored for non-numeric/categorical param '{param_name}'. Using 'lin'.")
            df.at[index, 'scale'] = 'lin' # Set non-relevant types to 'lin'

    if determined_count > 0: logger.info(f"Scale determined automatically for {determined_count} numeric params.")
    if fixed_count > 0: logger.info(f"Fixed {fixed_count} invalid scale values for numeric params.")


def _set_transform_types(params_obj: 'Parameters') -> None:
    """Determine 'transform' ('log', 'neglog', 'symlog') based on 'scale' and range, only for numeric types."""
    df = params_obj.all_parameters
    if 'transform' not in df.columns: df['transform'] = None
    # Ensure it's None initially before checking, handle existing values if needed? Better to just overwrite.
    df['transform'] = None

    mixed_sign_fixed = []; log_params = []; neglog_params = []; symlog_params = []
    for index, row in df.iterrows():
        param_type = row['type']
        scale = row['scale']
        param_name = row['name']

        # Transform only applies if scale is 'log' and type is numeric-compatible
        transform = None # Default to no transform
        if scale == 'log':
            is_numeric_compatible = False
            min_val = pd.to_numeric(row['min'], errors='coerce') # Coerce here for check
            max_val = pd.to_numeric(row['max'], errors='coerce')

            if param_type == 'continuous':
                if pd.notna(min_val) and pd.notna(max_val): is_numeric_compatible = True
            elif param_type == 'discrete':
                # Check if discrete has numeric definition (step or values)
                values = row['values']; step = row['step']
                # Need valid min/max range for transform check
                if pd.notna(min_val) and pd.notna(max_val):
                    if isinstance(values, list) and any(isinstance(v, (int, float)) and not math.isnan(v) for v in values if v is not None):
                            is_numeric_compatible = True
                    elif pd.notna(step):
                            is_numeric_compatible = True

            if is_numeric_compatible:
                # Already have coerced min_val, max_val from above
                if pd.isna(min_val) or pd.isna(max_val): # Should not happen if is_numeric_compatible is true, but safety check
                    logger.warning(f"Cannot apply log transform to '{param_name}': min/max not numeric despite numeric compatibility check.")
                    df.at[index, 'scale'] = 'lin' # Revert scale
                elif min_val > 0 and max_val > 0:
                    transform = 'log'
                    log_params.append(param_name)
                elif min_val < 0 and max_val < 0:
                    transform = 'neglog'
                    neglog_params.append(param_name)
                else:
                    # Mixed signs - use symlog transform
                    transform = 'symlog'
                    symlog_params.append(param_name)
                    logger.info(f"Using symlog transform for '{param_name}' with range [{min_val}, {max_val}]")
            elif scale == 'log': # Log scale specified but type isn't numeric compatible or min/max missing
                    logger.warning(f"Log scale specified for non-numeric compatible param '{param_name}' or missing min/max. Changing scale to 'lin'.")
                    df.at[index, 'scale'] = 'lin'


        # Store the determined transform (will be None if not applicable)
        df.at[index, 'transform'] = transform

    # Log summary messages
    if mixed_sign_fixed: msg = f"Changed scale to 'lin' for params with incompatible range for log/neglog: {', '.join(mixed_sign_fixed)}"; logger.info(msg)
    if log_params: msg = f"Using 'log' transform for params: {', '.join(log_params)}"; logger.info(msg)
    if neglog_params: msg = f"Using 'neglog' transform for params: {', '.join(neglog_params)}"; logger.info(msg)
    if symlog_params: msg = f"Using 'symlog' transform for params: {', '.join(symlog_params)}"; logger.info(msg)


# --- END OF FILE validation.py ---
