# --- START OF FILE Parameters.py ---

"""
Parameters class for managing parameter configurations in aivalanche_lib.

This module provides functionality to parse, manage, and manipulate parameter
configurations from different file formats (JSON, CSV). Includes support
for continuous, discrete (numeric only), and categorical parameters.

Author: Gazmend Alia
"""

import json
import random
import logging
import pandas as pd
import numpy as np
import math # Added for isnan checks
from typing import Dict, List, Optional, Union, Any

# Import IO functions from io.py
from .io import (
    parse_json, parse_csv, load_dataframe, load_dict_list
)
# Import scaling and normalization functions from scale_norm.py
from .scale_norm import (
    scale_parameter_row,
    normalize_parameter_row,
    normalize_parameter_value, denormalize_parameter_value,
    snap_discrete_value,
    normalize_categorical_value, denormalize_categorical_value,
)
# Import the validation functions
from .validation import run_all_validations, _expected_cols as expected_cols_structure

# Setup logger (as before)
logger = logging.getLogger(__name__)
if not logger.handlers:
    handler = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)


class Parameters:
    """
    A class for parsing and managing parameter configurations including continuous,
    discrete (numeric), and categorical types.

    Provides functionality to load parameters, access different types, scale,
    normalize, denormalize, descale, and generate random values.

    Attributes:
        file (str | None): Path to the parameter file (if loaded from one).
        all_parameters (pd.DataFrame): DataFrame containing original parameter definitions.
        all_parameters_scaled (pd.DataFrame): DataFrame with scaled parameters (log/neglog/index applied).
        all_parameters_normed (pd.DataFrame): DataFrame with normalized parameters ([0,1] range).
        error_parsing (Optional[str]): Error message if loading/processing fails.
    """

    # Reference the structure for potential internal use if needed, but validation handles it
    _expected_cols = expected_cols_structure

    def __init__(self, data: Optional[Union[str, pd.DataFrame, List[Dict[str, Any]]]] = None):
        """
        Initialize the Parameters class.

        Args:
            data: Input data in one of the following formats:
                - str: Path to a parameter file (JSON or CSV)
                - pd.DataFrame: DataFrame with parameter data
                - List[Dict[str, Any]]: List of parameter dictionaries
        """
        self.file = None
        self.all_parameters = pd.DataFrame()
        self.all_parameters_scaled = pd.DataFrame()
        self.all_parameters_normed = pd.DataFrame()
        self.error_parsing = None

        # Required base columns needed before validation can fully run
        self._required_base_cols = ['name']

        if data is not None:
            self.load_data(data)

    # --- Properties ---
    # [Properties remain unchanged - parameters_names, nr_parameters, fixed_*, variable_*, etc.]
    @property
    def parameters_names(self) -> List[str]:
        """Get names of all parameters."""
        if self.all_parameters.empty or 'name' not in self.all_parameters.columns: return []
        return self.all_parameters['name'].dropna().astype(str).tolist()

    @property
    def nr_parameters(self) -> int:
        """Get total number of parameters."""
        return len(self.all_parameters.index) if not self.all_parameters.empty else 0

    @property
    def fixed_parameters(self) -> pd.DataFrame:
        """Get parameters with mode 'fixed'."""
        if self.all_parameters.empty or 'mode' not in self.all_parameters.columns: return pd.DataFrame()
        return self.all_parameters[self.all_parameters['mode'] == 'fixed']

    @property
    def fixed_parameters_names(self) -> List[str]:
        """Get names of fixed parameters."""
        fixed_df = self.fixed_parameters
        if fixed_df.empty or 'name' not in fixed_df.columns: return []
        return fixed_df['name'].dropna().astype(str).tolist()

    @property
    def nr_fixed_parameters(self) -> int:
        """Get number of fixed parameters."""
        return len(self.fixed_parameters.index)

    @property
    def variable_parameters(self) -> pd.DataFrame:
        """Get parameters with mode 'variable'."""
        if self.all_parameters.empty or 'mode' not in self.all_parameters.columns: return pd.DataFrame()
        return self.all_parameters[self.all_parameters['mode'] == 'variable']

    @property
    def variable_parameters_names(self) -> List[str]:
        """Get names of variable parameters."""
        var_df = self.variable_parameters
        if var_df.empty or 'name' not in var_df.columns: return []
        return var_df['name'].dropna().astype(str).tolist()

    @property
    def nr_variable_parameters(self) -> int:
        """Get number of variable parameters."""
        return len(self.variable_parameters.index)

    @property
    def continuous_parameters(self) -> pd.DataFrame:
        """Get parameters with type 'continuous'."""
        if self.all_parameters.empty or 'type' not in self.all_parameters.columns: return pd.DataFrame()
        return self.all_parameters[self.all_parameters['type'] == 'continuous']

    @property
    def discrete_parameters(self) -> pd.DataFrame:
        """Get parameters with type 'discrete'."""
        if self.all_parameters.empty or 'type' not in self.all_parameters.columns: return pd.DataFrame()
        return self.all_parameters[self.all_parameters['type'] == 'discrete']

    @property
    def categorical_parameters(self) -> pd.DataFrame:
        """Get parameters with type 'categorical'."""
        if self.all_parameters.empty or 'type' not in self.all_parameters.columns: return pd.DataFrame()
        return self.all_parameters[self.all_parameters['type'] == 'categorical']

    @property
    def columns(self) -> List[str]:
        """Get column names of the main parameters DataFrame."""
        return list(self.all_parameters.columns) if not self.all_parameters.empty else []

    @property
    def variable_parameters_scaled(self) -> pd.DataFrame:
        """Get scaled parameters with mode 'variable'."""
        if self.all_parameters_scaled.empty: return pd.DataFrame()
        # Need mode column after scaling
        if 'mode' not in self.all_parameters_scaled.columns:
             # Attempt to merge mode from original if missing in scaled
             if not self.all_parameters.empty and 'name' in self.all_parameters.columns and 'mode' in self.all_parameters.columns:
                 modes = self.all_parameters[['name', 'mode']].set_index('name')
                 if 'name' in self.all_parameters_scaled.columns:
                      # Use join to add the mode column based on name
                      temp_scaled = self.all_parameters_scaled.join(modes, on='name')
                      # Check if join worked and mode column exists now
                      if 'mode' in temp_scaled.columns:
                           return temp_scaled[temp_scaled['mode'] == 'variable']
             logger.warning("Could not determine mode for scaled parameters.")
             return pd.DataFrame() # Fallback if mode cannot be determined
        return self.all_parameters_scaled[self.all_parameters_scaled['mode'] == 'variable']

    @property
    def variable_parameters_normed(self) -> pd.DataFrame:
        """Get normalized parameters with mode 'variable'."""
        if self.all_parameters_normed.empty: return pd.DataFrame()
        if 'mode' not in self.all_parameters_normed.columns:
             # Attempt to merge mode from original if missing in normed
             if not self.all_parameters.empty and 'name' in self.all_parameters.columns and 'mode' in self.all_parameters.columns:
                 modes = self.all_parameters[['name', 'mode']].set_index('name')
                 if 'name' in self.all_parameters_normed.columns:
                      temp_normed = self.all_parameters_normed.join(modes, on='name')
                      if 'mode' in temp_normed.columns:
                           return temp_normed[temp_normed['mode'] == 'variable']
             logger.warning("Could not determine mode for normalized parameters.")
             return pd.DataFrame() # Fallback
        return self.all_parameters_normed[self.all_parameters_normed['mode'] == 'variable']

    # --- Loading and Initialization ---

    def load_data(self, data: Union[str, pd.DataFrame, List[Dict[str, Any]]]) -> None:
        """
        Load parameters from various data sources, validate, and process.
        """
        self.error_parsing = None
        self.file = None # Reset file path
        parsed_df = None # DataFrame returned by loading utilities

        try:
            # === Step 1: Load data into initial DataFrame using utils ===
            if isinstance(data, str):
                self.file = data # Store file path
                ext = data.split('.')[-1].lower()
                if ext == 'json':
                     parsed_df, self.error_parsing = parse_json(data)
                elif ext == 'csv':
                     parsed_df, self.error_parsing = parse_csv(data)
                else:
                     self.error_parsing = f"Unsupported file format: {ext}"

            elif isinstance(data, pd.DataFrame): parsed_df, self.error_parsing = load_dataframe(data)
            elif isinstance(data, list): parsed_df, self.error_parsing = load_dict_list(data)
            else: self.error_parsing = f"Unsupported data type for loading: {type(data)}"

            # Check for errors from loading utilities
            if self.error_parsing:
                raise ValueError(f"Loading Error: {self.error_parsing}")
            if parsed_df is None: # Safety check
                 raise ValueError("Internal loading error: DataFrame is None but no error was reported.")

            # --- Assign loaded data ---
            self.all_parameters = parsed_df # Assign the initially loaded DataFrame

            # Handle potentially empty DataFrame after loading but before validation
            if self.all_parameters.empty:
                logger.warning("Loaded data resulted in an empty parameter set.")
                # Ensure minimal columns for an empty df - validation handles this now
                # self.all_parameters = pd.DataFrame(columns=list(self._expected_cols.keys()))
                # Ensure object types where necessary
                # for col in ['values', 'default']:
                #     if col in self.all_parameters.columns:
                #          self.all_parameters[col] = self.all_parameters[col].astype(object)

            # === Step 2: Validate the loaded DataFrame using external functions ===
            # The validation functions modify self.all_parameters in place
            run_all_validations(self)

             # Handle case where validation was skipped because df was empty
            if self.all_parameters.empty:
                self.all_parameters_scaled = pd.DataFrame()
                self.all_parameters_normed = pd.DataFrame()
                return # Nothing more to process if empty

            # === Step 3: Post-Validation Processing (Sorting, Scaling, Norm) ===
            self.sort_parameters_by_name() # Sort after validation/preprocessing
            self._scale_parameters() # Apply log/neglog and CATEGORICAL INDEXING
            self._normalize_parameters() # Apply [0,1] normalization to scaled values

        except Exception as e:
            # Catch any error during loading or processing
            if not self.error_parsing: self.error_parsing = f"Failed to load or process parameters: {str(e)}"
            logger.error(self.error_parsing, exc_info=True)
            # Reset state on critical error
            self.all_parameters = pd.DataFrame()
            self.all_parameters_scaled = pd.DataFrame()
            self.all_parameters_normed = pd.DataFrame()

    def sort_parameters_by_name(self) -> None:
        """Sort the parameters DataFrame by name."""
        if not self.all_parameters.empty and 'name' in self.all_parameters.columns:
            self.all_parameters = self.all_parameters.sort_values(by='name').reset_index(drop=True)
        elif not self.all_parameters.empty: logger.warning("Cannot sort: 'name' column missing.")

    # --- Scaling and Normalization ---
    def _scale_parameters(self) -> None:
        """
        Scale parameters based on transform type (log/neglog for numeric,
        index mapping for categorical). Modifies min, max, default.
        Uses the validated `self.all_parameters`.
        """
        if self.all_parameters.empty:
            self.all_parameters_scaled = pd.DataFrame()
            return
        try:
            # Ensure required columns exist before applying row-wise function
            # These columns should be guaranteed by the validator now
            cols_needed = ['name', 'type', 'min', 'max', 'default', 'values', 'scale', 'transform', 'mode'] # Added mode for property
            missing_cols = [col for col in cols_needed if col not in self.all_parameters.columns]
            if missing_cols:
                # This indicates a potential issue in the validator or loading if columns are missing here
                raise ValueError(f"Cannot scale: Missing required columns after validation: {missing_cols}")

            # Ensure correct dtypes before apply (especially object for values/default)
            # Validation should have handled basic types, but re-check object just in case
            if 'values' in self.all_parameters.columns and self.all_parameters['values'].dtype != object:
                 self.all_parameters['values'] = self.all_parameters['values'].astype(object)
            if 'default' in self.all_parameters.columns and self.all_parameters['default'].dtype != object:
                 self.all_parameters['default'] = self.all_parameters['default'].astype(object)

            # Apply the scaling function row by row (using scale_parameter_row from utils)
            self.all_parameters_scaled = self.all_parameters.apply(scale_parameter_row, axis=1)

            # --- Post-Scaling Type Conversion ---
            # Convert scaled min/max/step to numeric where appropriate
            for col in ['min', 'max', 'step']:
                 if col in self.all_parameters_scaled.columns:
                      self.all_parameters_scaled[col] = pd.to_numeric(self.all_parameters_scaled[col], errors='coerce')

            # Ensure 'default' remains object type as it can be index (int) or scaled float
            if 'default' in self.all_parameters_scaled.columns:
                 self.all_parameters_scaled['default'] = self.all_parameters_scaled['default'].astype(object)
            # Ensure 'values' remains object type (contains original list for categoricals)
            if 'values' in self.all_parameters_scaled.columns:
                 self.all_parameters_scaled['values'] = self.all_parameters_scaled['values'].astype(object)
            # Ensure 'mode' is carried over correctly
            if 'mode' in self.all_parameters.columns and 'mode' not in self.all_parameters_scaled.columns:
                 logger.warning("Mode column lost during scaling, attempting to re-add.")
                 if 'name' in self.all_parameters.columns and 'name' in self.all_parameters_scaled.columns:
                     modes = self.all_parameters[['name', 'mode']].set_index('name')
                     self.all_parameters_scaled = self.all_parameters_scaled.join(modes, on='name')

            # Log scaling summary
            log_count = (self.all_parameters_scaled['transform'] == 'log').sum()
            neglog_count = (self.all_parameters_scaled['transform'] == 'neglog').sum()
            cat_count = (self.all_parameters_scaled['type'] == 'categorical').sum()
            msg = f"Applied scaling: log ({log_count}), neglog ({neglog_count}), categorical indexing ({cat_count})."
            logger.info(msg)

        except Exception as e:
             logger.error(f"Error during parameter scaling: {e}", exc_info=True)
             self.error_parsing = f"Scaling error: {e}"
             self.all_parameters_scaled = pd.DataFrame()

    def _normalize_parameters(self) -> None:
        """
        Normalize scaled parameters to the [0,1] range based on type.
        Uses standard numeric normalization for continuous, discrete, and
        index-scaled categorical parameters.
        """
        if self.all_parameters_scaled.empty:
            self.all_parameters_normed = pd.DataFrame()
            return
        try:
            # Copy scaled parameters to start normalization
            self.all_parameters_normed = self.all_parameters_scaled.copy()

            # Ensure required columns for normalization exist
            required_for_norm = ['type', 'min', 'max', 'default', 'values', 'name', 'mode'] # Added mode
            missing_norm_cols = [c for c in required_for_norm if c not in self.all_parameters_normed.columns]
            if missing_norm_cols:
                 raise ValueError(f"Cannot normalize: Missing columns in scaled df: {missing_norm_cols}")

            # Ensure correct dtypes before apply (especially object for values/default)
            if 'values' in self.all_parameters_normed.columns and self.all_parameters_normed['values'].dtype != object:
                 self.all_parameters_normed['values'] = self.all_parameters_normed['values'].astype(object)
            if 'default' in self.all_parameters_normed.columns and self.all_parameters_normed['default'].dtype != object:
                 self.all_parameters_normed['default'] = self.all_parameters_normed['default'].astype(object)

            # Apply the normalization function row by row (using normalize_parameter_row from utils)
            self.all_parameters_normed = self.all_parameters_normed.apply(normalize_parameter_row, axis=1)

            # --- Post-Normalization Type Conversion ---
            # Normalized min/max/default should all be float
            for col in ['min', 'max', 'default']:
                 if col in self.all_parameters_normed.columns:
                      self.all_parameters_normed[col] = pd.to_numeric(self.all_parameters_normed[col], errors='coerce')

            # Ensure 'values' remains object type (contains original list for categoricals)
            if 'values' in self.all_parameters_normed.columns:
                 self.all_parameters_normed['values'] = self.all_parameters_normed['values'].astype(object)
            # Ensure 'mode' is carried over correctly
            if 'mode' in self.all_parameters_scaled.columns and 'mode' not in self.all_parameters_normed.columns:
                  logger.warning("Mode column lost during normalization, attempting to re-add.")
                  if 'name' in self.all_parameters_scaled.columns and 'name' in self.all_parameters_normed.columns:
                      modes = self.all_parameters_scaled[['name', 'mode']].set_index('name')
                      self.all_parameters_normed = self.all_parameters_normed.join(modes, on='name')

            msg = f"Normalized {len(self.all_parameters_normed)} parameters to [0,1] range."
            logger.info(msg)

        except Exception as e:
             logger.error(f"Error during parameter normalization: {e}", exc_info=True)
             self.error_parsing = f"Normalization error: {e}"
             self.all_parameters_normed = pd.DataFrame()

    # --- Value Generation ---
    # [generate_random_parameters, get_default_parameters, _generate_random_value remain unchanged from previous version]
    def generate_random_parameters(self) -> Dict[str, Any]:
        """Generate random values for all parameters according to their type and mode."""
        if self.all_parameters.empty: return {}
        results = {}
        if 'name' not in self.all_parameters.columns: return {} # Need name column
        for index, row in self.all_parameters.iterrows():
             name = row['name']
             try:
                 # Generate random value based on ORIGINAL parameter definition
                 results[name] = self._generate_random_value(row)
             except Exception as e:
                 logger.error(f"Error generating random for '{name}': {e}. Using default.", exc_info=True)
                 results[name] = row['default'] if pd.notna(row['default']) else None # Use original default
        return results

    def get_default_parameters(self) -> Dict[str, Any]:
        """Get ORIGINAL default values for all parameters."""
        if self.all_parameters.empty: return {}
        if 'name' not in self.all_parameters.columns or 'default' not in self.all_parameters.columns: return {}
        try:
            # Ensure default column is suitable for direct to_dict
            # It should be object type containing potentially mixed types
            # Use .where to replace potential pd.NA with None before to_dict
            default_series = self.all_parameters.set_index('name')['default']
            return default_series.where(pd.notna(default_series), None).to_dict()
        except Exception as e:
            logger.error(f"Error getting default dict: {e}")
            # Fallback: iterate rows (handles potential issues with direct to_dict)
            return {r['name']: (r['default'] if pd.notna(r['default']) else None)
                    for i, r in self.all_parameters.iterrows()}


    def _generate_random_value(self, row: pd.Series) -> Any:
        """Generate a random value for a single parameter row based on its ORIGINAL definition."""
        if row.get('mode') == 'fixed':
            # Return the original default value, handling potential None
            return row['default'] if pd.notna(row['default']) else None

        param_type = row['type']
        name = row.get('name', 'UNKNOWN')

        try:
            if param_type == 'continuous':
                # Use original min/max and transform from the original definition
                transform = row.get('transform') # Should be None, 'log', or 'neglog'
                min_val = row['min']
                max_val = row['max']
                # Ensure min/max are numeric
                min_val_num = pd.to_numeric(min_val, errors='raise')
                max_val_num = pd.to_numeric(max_val, errors='raise')

                if np.isclose(min_val_num, max_val_num): return min_val_num # Handle single point case

                if transform == 'log':
                     if min_val_num <= 0 or max_val_num <= 0: raise ValueError("min/max must be positive for log")
                     # Generate random in scaled space, then descale
                     s_min, s_max = np.log10(min_val_num), np.log10(max_val_num)
                     return 10**random.uniform(s_min, s_max)
                elif transform == 'neglog':
                     if min_val_num >= 0 or max_val_num >= 0: raise ValueError("min/max must be negative for neglog")
                     # Generate random in scaled space, then descale
                     # Scaled min/max are swapped relative to original for neglog
                     s_min, s_max = -np.log10(-max_val_num), -np.log10(-min_val_num) # Note the swapped order
                     scaled_rand = random.uniform(s_min, s_max)
                     return -(10**(-scaled_rand)) # Corrected logic
                else: # Linear scale
                     return random.uniform(min_val_num, max_val_num)

            elif param_type == 'discrete':
                values = row['values'] # Original list or None
                step = row['step']     # Original step or NaN

                if isinstance(values, list) and values:
                     # Choose randomly from the original numeric values list
                     numeric_values = [v for v in values if isinstance(v, (int, float)) and not math.isnan(v)]
                     if not numeric_values: raise ValueError("No valid numeric values in discrete list to choose from.")
                     return random.choice(numeric_values)
                elif pd.notna(step):
                    # Generate random step-based value using original min/max/step
                    min_val = row['min']
                    max_val = row['max']
                    min_val_num = pd.to_numeric(min_val, errors='raise')
                    max_val_num = pd.to_numeric(max_val, errors='raise')
                    step_num = pd.to_numeric(step, errors='raise')

                    if np.isclose(max_val_num, min_val_num): return min_val_num # Single point
                    if step_num <= 0: raise ValueError("Step must be positive")
                    if max_val_num < min_val_num: raise ValueError("Max cannot be less than Min for step") # Should be caught by validation

                    # Calculate number of possible steps
                    # Add epsilon for float precision issues when calculating num_steps
                    num_steps_float = (max_val_num - min_val_num) / step_num
                    num_steps = math.floor(num_steps_float + 1e-9) # Use floor for index
                    if num_steps < 0: num_steps = 0 # Handle edge case

                    # Generate random index and calculate value
                    rand_step_index = random.randint(0, int(num_steps))
                    val = min_val_num + rand_step_index * step_num

                    # Ensure result is within bounds due to potential float issues
                    val = max(min_val_num, min(val, max_val_num))

                    # Optional: Return int if min/step were int?
                    if isinstance(min_val, int) and isinstance(step, int):
                        return int(round(val))
                    else:
                        return float(val) # Return float otherwise

                else:
                    raise ValueError(f"Invalid discrete definition for '{name}'. Needs 'values' list or 'step'.")

            elif param_type == 'categorical':
                values = row['values'] # Original list
                if not isinstance(values, list) or not values:
                    raise ValueError(f"Invalid categorical definition for '{name}'. Needs non-empty 'values' list.")
                # Choose randomly from the original values list
                return random.choice(values)
            else:
                raise ValueError(f"Unknown parameter type '{param_type}' for '{name}'.")
        except Exception as e:
            logger.error(f"Error in _generate_random_value for '{name}': {e}", exc_info=True)
             # Return the original default value, handling potential None
            return row['default'] if pd.notna(row['default']) else None # Fallback to original default on error


    # --- Parameter Manipulation ---
    # [add_parameter, remove_parameter remain unchanged, they trigger load_data]
    def add_parameter(self, name: str, type: str, min_val: Optional[float] = None, max_val: Optional[float] = None,
                     default: Any = None, values: Optional[List[Any]] = None, step: Optional[float] = None,
                     scale: str = 'lin', mode: str = 'variable') -> None:
        """Add or update a parameter. Performs validation and recalculates scaled/normed forms."""
        # --- Basic Input Validation ---
        if type not in ['continuous', 'discrete', 'categorical']: raise ValueError(f"Invalid type '{type}'")
        # Add other basic checks as needed based on type...

        # --- Create Parameter Dictionary ---
        new_param_dict = {
            'name': name, 'type': type, 'min': min_val, 'max': max_val,
            'default': default, 'values': values, 'step': step,
            'scale': scale, 'mode': mode, 'transform': None # Transform determined later
        }

        # Convert potentially NaN floats for min/max/step to None for consistency if needed
        for key in ['min', 'max', 'step']:
            if isinstance(new_param_dict[key], float) and math.isnan(new_param_dict[key]):
                new_param_dict[key] = None
        # Ensure values is a list or None
        if values is not None and not isinstance(values, list):
             logger.warning(f"Forcing 'values' to list for '{name}'. Input was: {values}")
             values = [values]
             new_param_dict['values'] = values

        # --- Add or Update in DataFrame ---
        current_df = self.all_parameters.copy() # Work on a copy

        if current_df.empty and 'name' not in current_df.columns:
            # Initialize DataFrame if completely empty
            current_df = pd.DataFrame(columns=list(self._expected_cols.keys()))
            # Ensure object columns are object type
            for col in ['values', 'default']:
                 if col in current_df.columns:
                     current_df[col] = current_df[col].astype(object)

        # Check if name exists
        existing_indices = current_df[current_df['name'] == name].index
        if not existing_indices.empty:
            # Update existing parameter
            idx = existing_indices[0]
            for key, value in new_param_dict.items():
                if key not in current_df.columns: current_df[key] = None; # Add column if missing
                # Ensure object type before setting if needed
                if key in ['values', 'default'] and current_df[key].dtype != object:
                    current_df[key] = current_df[key].astype(object)
                try: current_df.at[idx, key] = value
                except Exception as e: logger.error(f"Error setting {key}={value} for {name} at {idx}: {e}"); raise e
            logger.info(f"Updated parameter '{name}'.")
        else:
            # Add new parameter
            # Create a temporary DataFrame for the new row
            temp_df = pd.DataFrame([new_param_dict])
            # Ensure object columns in temp_df are object type
            for col in ['values', 'default']:
                 if col in temp_df.columns: temp_df[col] = temp_df[col].astype(object)
            # Ensure all expected columns exist in temp_df, adding None if missing
            for col in self._expected_cols:
                 if col not in temp_df.columns: temp_df[col] = None;
                 # Ensure object types in new row match if needed
                 if col in ['values', 'default'] and temp_df[col].dtype != object:
                      temp_df[col] = temp_df[col].astype(object)


            # Align columns before concat
            existing_cols = current_df.columns if not current_df.empty else []
            all_cols = pd.Index(existing_cols).union(temp_df.columns)
            # Reindex both DataFrames to have the same columns in the same order
            current_df = current_df.reindex(columns=all_cols, fill_value=None) # Use fill_value=None
            temp_df = temp_df.reindex(columns=all_cols, fill_value=None)

             # Ensure consistent dtypes before concat (especially object columns)
            for col in ['values', 'default']:
                if col in all_cols:
                    if current_df[col].dtype != object: current_df[col] = current_df[col].astype(object)
                    if temp_df[col].dtype != object: temp_df[col] = temp_df[col].astype(object)

            # Concatenate
            current_df = pd.concat([current_df, temp_df], ignore_index=True)
            logger.info(f"Added new parameter '{name}'.")

        # --- Reprocess the entire parameter set ---
        original_error = self.error_parsing
        original_state = self.all_parameters.copy() # Keep original state for potential revert
        try:
            # Use the modified DataFrame (`current_df`) as input for reprocessing
            self.load_data(current_df)
        except Exception as e:
            # Reprocessing failed, revert state using the original self.all_parameters and report error
            self.error_parsing = f"Reprocessing after add/update of '{name}' failed: {e}. State reverted."
            logger.error(self.error_parsing, exc_info=True)
            # Re-run load_data with the *original* DataFrame to restore previous state
            try:
                 self.load_data(original_state) # Use the saved original state
            except Exception as revert_e:
                 logger.error(f"Failed to revert state after add/update failure: {revert_e}", exc_info=True)
                 # Critical state - clear everything?
                 self.all_parameters = pd.DataFrame()
                 self.all_parameters_scaled = pd.DataFrame()
                 self.all_parameters_normed = pd.DataFrame()
            return # Exit the function after failed add/update

        # Check if reprocessing itself introduced an error state
        if self.error_parsing and not original_error:
            logger.error(f"Adding/Updating '{name}' caused error during reprocessing: {self.error_parsing}.")


    def remove_parameter(self, name: str) -> bool:
        """Remove a parameter by name and reprocess."""
        original_df_state = self.all_parameters.copy() # Preserve original state in case of failure

        if original_df_state.empty or 'name' not in original_df_state.columns or name not in original_df_state['name'].values:
            logger.warning(f"Param '{name}' not found for removal.")
            return False

        original_size = len(original_df_state)
        # Filter out the parameter from the *copy*
        current_df = original_df_state[original_df_state['name'] != name].reset_index(drop=True)

        if len(current_df) < original_size:
            logger.info(f"Removed parameter '{name}'. Reprocessing...")
            original_error = self.error_parsing

            # --- Reprocess ---
            try:
                # Reprocess using the DataFrame *after* removal (`current_df`)
                self.load_data(current_df)
                # Restore original error state only if reprocessing succeeded without new errors
                if not self.error_parsing: self.error_parsing = original_error
                return True # Indicate success
            except Exception as e:
                # Reprocessing failed, revert to state before removal attempt and report error
                self.error_parsing = f"Reprocessing after removal of '{name}' failed: {e}. State reverted."
                logger.error(self.error_parsing, exc_info=True)
                # Reload the original state
                try:
                    self.load_data(original_df_state) # Use the saved original state
                except Exception as revert_e:
                    logger.error(f"Failed to revert state after removal failure: {revert_e}", exc_info=True)
                    # Critical state - clear everything?
                    self.all_parameters = pd.DataFrame()
                    self.all_parameters_scaled = pd.DataFrame()
                    self.all_parameters_normed = pd.DataFrame()
                return False # Indicate failure
        else:
            # Should not happen if name was found initially
            logger.warning(f"Param '{name}' found but removal filter did not change DataFrame size.")
            return False


    # --- Parameter Info Getters ---
    # [get_parameter, get_parameter_scaled, get_parameter_normed remain unchanged from previous version]
    def get_parameter(self, name: str) -> Optional[Dict[str, Any]]:
        """Get original parameter definition by name."""
        if self.all_parameters.empty or 'name' not in self.all_parameters.columns or name not in self.all_parameters['name'].values: return None
        try:
            # Use .loc for label-based lookup, iloc[0] to get the Series
            param_series = self.all_parameters.loc[self.all_parameters['name'] == name].iloc[0]
            # Convert to dictionary, handle potential NaNs if needed (replace with None)
            return param_series.where(pd.notna(param_series), None).to_dict()
        except IndexError: # Handle case where name might be in index but filter yields empty
            return None
        except Exception as e:
            logger.error(f"Error in get_parameter for '{name}': {e}")
            return None

    def get_parameter_scaled(self, name: str) -> Optional[Dict[str, Any]]:
        """Get scaled parameter definition by name."""
        if self.all_parameters_scaled.empty or 'name' not in self.all_parameters_scaled.columns or name not in self.all_parameters_scaled['name'].values: return None
        try:
            param_series = self.all_parameters_scaled.loc[self.all_parameters_scaled['name'] == name].iloc[0]
            # Convert to dictionary, handle potential NaNs
            return param_series.where(pd.notna(param_series), None).to_dict()
        except IndexError:
            return None
        except Exception as e:
            logger.error(f"Error in get_parameter_scaled for '{name}': {e}")
            return None

    def get_parameter_normed(self, name: str) -> Optional[Dict[str, Any]]:
        """Get normalized parameter definition by name."""
        if self.all_parameters_normed.empty or 'name' not in self.all_parameters_normed.columns or name not in self.all_parameters_normed['name'].values: return None
        try:
            param_series = self.all_parameters_normed.loc[self.all_parameters_normed['name'] == name].iloc[0]
            # Convert to dictionary, handle potential NaNs
            return param_series.where(pd.notna(param_series), None).to_dict()
        except IndexError:
            return None
        except Exception as e:
            logger.error(f"Error in get_parameter_normed for '{name}': {e}")
            return None

    # --- Array Denormalization / Descaling ---
    # [_get_param_info, denormalize_parameters_array, descale_parameters_array, denormalize_and_descale_parameters_array remain unchanged from previous version]
    def _get_param_info(self, param_name: str, df_type='original') -> Dict:
        """Helper to get parameter info dict from specified DataFrame."""
        df = None
        if df_type == 'original': df = self.all_parameters
        elif df_type == 'scaled': df = self.all_parameters_scaled
        elif df_type == 'normed': df = self.all_parameters_normed
        else: raise ValueError(f"Invalid df_type specified: {df_type}")

        if df is None or df.empty or 'name' not in df.columns:
             raise ValueError(f"Parameter source DataFrame ('{df_type}') is invalid or missing 'name' column.")

        # Check if param_name exists efficiently
        if param_name not in df['name'].values:
             raise ValueError(f"Parameter '{param_name}' not found in {df_type} parameters DataFrame.")

        try:
            # Get the parameter row as a Series
            param_series = df.loc[df['name'] == param_name].iloc[0]
            # Convert to dictionary, replacing NaNs/pd.NA with None
            info = param_series.where(pd.notna(param_series), None).to_dict()
        except IndexError: # Should be caught by check above, but safety
             raise ValueError(f"Parameter '{param_name}' lookup failed unexpectedly in {df_type} parameters DataFrame.")

        return info

    def denormalize_parameters_array(self, data: Union[pd.DataFrame, List[Dict[str, float]]], target_params: Optional[List[str]] = None) -> Union[pd.DataFrame, List[Dict[str, float]]]:
        """
        Convert normalized [0,1] values back to their SCALED range.
        For numeric types, this is the potentially log/neglog scaled range.
        For categorical types, this is the index range [0, N-1].
        Does NOT perform descaling (10^x) or snapping/category lookup.
        Clamping of input [0,1] is applied only for categorical and discrete-list types.
        """
        if self.all_parameters_scaled.empty or self.all_parameters_normed.empty:
             raise ValueError("Parameters must be loaded, scaled, and normalized first.")

        is_dataframe = isinstance(data, pd.DataFrame)
        df = pd.DataFrame(data) if not is_dataframe else data.copy()

        variable_names_set = set(self.variable_parameters_names)

        if target_params is None:
            target_params = [col for col in df.columns if col in variable_names_set] # Auto-detect from input cols
            if not target_params:
                 logger.warning("No variable parameters found in input data columns for denormalization.")
                 return pd.DataFrame(index=df.index) if is_dataframe else [] # Return empty with correct structure

        invalid_params = [p for p in target_params if p not in variable_names_set]
        if invalid_params: raise ValueError(f"Target parameters {invalid_params} are not variable or do not exist.")

        result_df = pd.DataFrame(index=df.index)
        processed_cols = set()

        for param_name in target_params:
             if param_name not in df.columns:
                 logger.warning(f"Target parameter '{param_name}' not found in input data. Skipping.")
                 continue

             norm_values = df[param_name]
             try:
                 # Get SCALED parameter info (contains scaled min/max, including index range for categoricals)
                 # We also need original info to distinguish discrete types
                 scaled_info = self._get_param_info(param_name, 'scaled')
                 original_info = self._get_param_info(param_name, 'original') # Needed for discrete type check
                 param_type = scaled_info.get('type')

                 # --- Determine if clamping should be applied ---
                 should_clamp = True # Default to clamp (safe for categorical/discrete-list indices)
                 if param_type == 'continuous':
                     should_clamp = False
                 elif param_type == 'discrete':
                     # Check if discrete is step-based (no clamp) or list-based (clamp index range)
                     if pd.notna(original_info.get('step')):
                         should_clamp = False
                     # else: keep should_clamp = True for list-based

                 # --- Proceed with denormalization ---
                 if param_type in ['continuous', 'discrete', 'categorical']: # All types use numeric denorm on scaled range
                     min_val_s = pd.to_numeric(scaled_info['min'], errors='raise')
                     max_val_s = pd.to_numeric(scaled_info['max'], errors='raise')

                     # Ensure input normalized values are numeric
                     numeric_norm = pd.to_numeric(norm_values, errors='coerce')
                     na_mask = numeric_norm.isna()
                     if na_mask.any():
                          logger.warning(f"Input normalized values for '{param_name}' contain non-numeric data. NaNs will propagate.")

                     # Apply standard numeric denormalization, passing the clamp flag
                     denormed_values = pd.Series(np.nan, index=numeric_norm.index) # Initialize with NaN
                     if not na_mask.all(): # Avoid apply if all NaN
                        denormed_values[~na_mask] = numeric_norm[~na_mask].apply(
                            lambda x: denormalize_parameter_value(x, min_val_s, max_val_s, clamp=should_clamp) # Pass clamp flag
                        )
                     result_df[param_name] = denormed_values
                 else:
                      # Should not happen with validation
                      raise TypeError(f"Unsupported parameter type '{param_type}' encountered during denormalization for '{param_name}'.")

                 processed_cols.add(param_name)

             except Exception as e:
                 logger.error(f"Error denormalizing parameter '{param_name}': {e}", exc_info=True)
                 raise e # Re-raise the error

        # Add back unprocessed columns
        for col in df.columns:
             if col not in processed_cols:
                 result_df[col] = df[col]

        return result_df if is_dataframe else result_df.to_dict('records')

    def descale_parameters_array(self, data: Union[pd.DataFrame, List[Dict[str, float]]], target_params: Optional[List[str]] = None) -> Union[pd.DataFrame, List[Dict[str, float]]]:
        """
        Apply inverse scaling (e.g., 10^x for log/neglog) to SCALED values.
        Does NOT perform snapping or categorical index->value mapping.
        Input data should be in the SCALED space (e.g., output of denormalize_parameters_array).
        """
        if self.all_parameters.empty: # Need original info for transform type
             raise ValueError("Original parameter definitions are required for descaling.")

        is_dataframe = isinstance(data, pd.DataFrame)
        df = pd.DataFrame(data) if not is_dataframe else data.copy()

        variable_names_set = set(self.variable_parameters_names)

        if target_params is None:
            target_params = [col for col in df.columns if col in variable_names_set] # Auto-detect
            if not target_params:
                 logger.warning("No variable parameters found in input data columns for descaling.")
                 return pd.DataFrame(index=df.index) if is_dataframe else []

        invalid_params = [p for p in target_params if p not in variable_names_set]
        if invalid_params: raise ValueError(f"Target parameters {invalid_params} are not variable or do not exist.")

        result_df = pd.DataFrame(index=df.index) # Initialize result
        processed_cols = set()

        for param_name in target_params:
             if param_name not in df.columns:
                 logger.warning(f"Target parameter '{param_name}' not found in input data for descaling. Skipping.")
                 continue
             try:
                 # Get ORIGINAL parameter info to check the transform type
                 original_info = self._get_param_info(param_name, 'original')
                 transform = original_info.get('transform') # 'log', 'neglog', or None
                 param_type = original_info.get('type')

                 scaled_values = df[param_name] # Values from input (assumed scaled)

                 # Descaling only applies to numeric types with a transform
                 if transform and param_type in ['continuous', 'discrete']:
                     # Ensure input values are numeric
                     numeric_col = pd.to_numeric(scaled_values, errors='coerce')
                     na_mask = numeric_col.isna()
                     if na_mask.any():
                          logger.warning(f"Non-numeric values encountered in column '{param_name}' before descaling. NaNs will propagate.")

                     # Apply inverse transform only to non-NaN values
                     descaled_values = pd.Series(np.nan, index=numeric_col.index)
                     if transform == 'log':
                         descaled_values[~na_mask] = 10 ** numeric_col[~na_mask]
                     elif transform == 'neglog':
                         # Careful with the sign: scaled = -log10(-original) => original = -(10**(-scaled))
                         descaled_values[~na_mask] = -(10 ** (-numeric_col[~na_mask]))

                     result_df[param_name] = descaled_values
                 else:
                      # No transform or not numeric/discrete: copy original scaled values
                      # Ensure numeric conversion if expected type suggests it
                      if param_type in ['continuous', 'discrete', 'categorical']: # Categorical index is numeric
                          result_df[param_name] = pd.to_numeric(scaled_values, errors='coerce')
                          # Check if NaNs were introduced unnecessarily
                          if result_df[param_name].isna().sum() > scaled_values.isna().sum():
                              logger.warning(f"NaNs generated during numeric conversion for '{param_name}' (type: {param_type}, transform: {transform}). Input: {scaled_values.dtype}, Output: {result_df[param_name].dtype}")
                      else: # Should not happen
                           result_df[param_name] = scaled_values # Keep as is otherwise

                 processed_cols.add(param_name)

             except Exception as e:
                 logger.error(f"Error descaling parameter '{param_name}': {e}", exc_info=True)
                 raise e # Re-raise the error

        # Add back any columns from input df that were not processed (e.g., fixed params if present)
        for col in df.columns:
             if col not in processed_cols:
                 result_df[col] = df[col]

        return result_df if is_dataframe else result_df.to_dict('records')

    def denormalize_and_descale_parameters_array(self, data: Union[pd.DataFrame, List[Dict[str, float]]],
                                                 target_params: Optional[List[str]] = None,
                                                 include_fixed: bool = True) -> Union[pd.DataFrame, List[Dict[str, Any]]]:
        """
        Convert normalized parameter values [0,1] back to their original types and ranges.
        Combines denormalization (to scaled space), descaling (if applicable),
        and snapping (for discrete) or index-to-value mapping (for categorical).
        Input [0,1] clamping during denormalization is applied only for categorical and discrete-list types.
        Args:
            data: DataFrame or list of dicts with normalized [0,1] values for variable parameters.
            target_params: Optional list of variable parameter names to process. If None, processes all
                           variable parameters present as columns in the input data.
            include_fixed: If True, adds columns for fixed parameters with their default values.

        Returns:
            DataFrame or list of dicts with values in their original space and types.
        """
        if self.all_parameters.empty or self.all_parameters_scaled.empty or self.all_parameters_normed.empty:
            raise ValueError("Parameters must be loaded, scaled, and normalized first.")

        is_dataframe = isinstance(data, pd.DataFrame)
        df = pd.DataFrame(data) if not is_dataframe else data.copy()

        variable_names_set = set(self.variable_parameters_names)
        fixed_names_set = set(self.fixed_parameters_names)

        if target_params is None:
            # Automatically select variable parameters present in the input data
            target_params = [col for col in df.columns if col in variable_names_set]
            if not target_params:
                 logger.warning("No variable parameters found in input data columns. Only processing fixed parameters if requested.")
                 # Continue processing if include_fixed is True, otherwise return empty df/list
        else:
            # Validate that provided target_params are indeed variable parameters
            invalid_params = [p for p in target_params if p not in variable_names_set]
            if invalid_params:
                raise ValueError(f"Target parameters {invalid_params} are not variable or do not exist.")

        result_df = pd.DataFrame(index=df.index) # Initialize empty result DataFrame
        processed_variable_cols = set()

        # Process each target variable parameter
        for param_name in target_params:
            if param_name not in df.columns:
                logger.warning(f"Target variable parameter '{param_name}' not found in input data. Skipping.")
                continue
            try:
                # Get normalized values from input data
                norm_values = pd.to_numeric(df[param_name], errors='coerce')
                na_mask = norm_values.isna()
                if na_mask.any():
                    logger.warning(f"Input normalized data for '{param_name}' contains non-numeric values. NaNs will propagate.")

                # Get necessary info (original needed for type, transform, values, step; scaled for denorm range)
                original_info = self._get_param_info(param_name, 'original')
                scaled_info = self._get_param_info(param_name, 'scaled') # contains scaled range [min_s, max_s]
                param_type = original_info['type']
                transform = original_info.get('transform')

                # Initialize series for final values of this parameter
                final_values = pd.Series(index=norm_values.index, dtype=object) # Use object for mixed types

                # --- Determine if clamping should be applied during denorm step ---
                should_clamp_denorm = True # Default clamp (for categorical index, discrete-list index)
                if param_type == 'continuous':
                    should_clamp_denorm = False
                elif param_type == 'discrete':
                    if pd.notna(original_info.get('step')): # Check if step-based
                        should_clamp_denorm = False
                    # else: it's list-based, keep should_clamp_denorm = True

                # --- Step 1: Denormalize to SCALED space ---
                min_val_s = pd.to_numeric(scaled_info['min'], errors='raise')
                max_val_s = pd.to_numeric(scaled_info['max'], errors='raise')
                denormalized_scaled_values = pd.Series(np.nan, index=norm_values.index)
                if not na_mask.all(): # Avoid apply if all values are NaN
                    denormalized_scaled_values[~na_mask] = norm_values[~na_mask].apply(
                        # Pass the determined clamp flag
                        lambda x: denormalize_parameter_value(x, min_val_s, max_val_s, clamp=should_clamp_denorm)
                    )

                # --- Step 2: Descale (if applicable) ---
                # ... (Descaling logic remains the same) ...
                descaled_values = denormalized_scaled_values.copy() # Start with denormalized values
                if transform and param_type in ['continuous', 'discrete']:
                     # Check for NaNs *before* applying 10** or log10
                    current_na_mask = descaled_values.isna() # Mask might have changed
                    if not current_na_mask.all(): # Avoid operation if all NaN
                        if transform == 'log':
                            descaled_values[~current_na_mask] = 10 ** descaled_values[~current_na_mask]
                        elif transform == 'neglog':
                            descaled_values[~current_na_mask] = -(10 ** (-descaled_values[~current_na_mask]))

                # --- Step 3: Snap (discrete) or Map (categorical) ---
                if param_type == 'continuous':
                    # Final values are the descaled numeric values
                    final_values = pd.to_numeric(descaled_values, errors='coerce') # Ensure numeric type
                elif param_type == 'discrete':
                    # Prepare snap_info using ORIGINAL parameter details fetched earlier.
                    snap_info = {
                        'type': 'discrete',
                        'name': param_name,
                        'min': original_info.get('min'),    # Use standard key 'min'
                        'max': original_info.get('max'),    # Use standard key 'max'
                        'step': original_info.get('step'),   # Use standard key 'step'
                        'values': original_info.get('values') # Use standard key 'values'
                    }
                    # Ensure values are numeric before snapping
                    numeric_descaled = pd.to_numeric(descaled_values, errors='coerce')
                    snap_na_mask = numeric_descaled.isna()
                    if snap_na_mask.any():
                         logger.warning(f"Non-numeric value encountered before snapping for discrete '{param_name}'. NaNs will propagate.")

                    # Apply snapping to each non-NaN value using the prepared snap_info
                    # snap_discrete_value handles its own clamping based on original min/max or values list
                    if not snap_na_mask.all():
                        final_values[~snap_na_mask] = numeric_descaled[~snap_na_mask].apply(lambda x: snap_discrete_value(x, snap_info))
                    # Keep NaNs as NaN
                    final_values[snap_na_mask] = np.nan

                elif param_type == 'categorical':
                    # Map normalized [0,1] value back to original category using the utility function
                    # denormalize_categorical_value handles its own necessary clamping internally.
                    categories = original_info.get('values') # Use standard key 'values'
                    if not isinstance(categories, list):
                        raise TypeError(f"Invalid original categories list found for '{param_name}' during final mapping.")
                    # Apply denormalize_categorical_value only to non-NaN normalized values
                    if not na_mask.all(): # Use original na_mask from norm_values input
                        final_values[~na_mask] = norm_values[~na_mask].apply(lambda x: denormalize_categorical_value(x, categories))
                    # Keep NaNs as NaN
                    final_values[na_mask] = np.nan # or None, depending on desired output for NAs

                else:
                    raise TypeError(f"Unsupported parameter type '{param_type}' encountered during final processing step for '{param_name}'.")

                # Assign the final processed values to the result DataFrame
                result_df[param_name] = final_values
                processed_variable_cols.add(param_name)

            except Exception as e:
                logger.error(f"Error processing parameter '{param_name}' in denormalize_and_descale: {e}", exc_info=True)
                raise e # Re-raise the error

        # --- Add Fixed Parameters ---
        # ... (logic remains the same) ...
        if include_fixed:
            # Get fixed params directly using the property
            fixed_params_df = self.fixed_parameters
            if not fixed_params_df.empty:
                 # Ensure index alignment
                 if not result_df.index.equals(df.index):
                     result_df = result_df.reindex(df.index)
                 # Add fixed parameters with their original default values
                 for _, param in fixed_params_df.iterrows():
                     param_name = param['name']
                     if param_name not in result_df.columns: # Avoid overwriting if somehow present
                        # Use .where to handle potential pd.NA in default
                        default_val = param['default'] if pd.notna(param['default']) else None
                        result_df[param_name] = default_val


        # --- Final Ordering and Return ---
        # ... (logic remains the same) ...
        final_columns = df.columns.tolist() # Start with input order
        if include_fixed:
            # Add fixed names not already present (e.g., if only var params were in input)
            for fn in fixed_names_set:
                 if fn not in final_columns: final_columns.append(fn)

        # Ensure all desired columns exist in result_df before reindexing
        # Only add columns that should be in the output (processed variable + requested fixed)
        expected_output_cols = list(processed_variable_cols) + (list(fixed_names_set) if include_fixed else [])
        for col in expected_output_cols:
            if col not in result_df.columns:
                result_df[col] = np.nan # Or None? Use NaN for consistency if converting to dict later

        # Reorder using the combined list of input cols + potentially added fixed cols
        final_columns_ordered = [col for col in final_columns if col in result_df.columns] # Only include existing cols
        result_df = result_df[final_columns_ordered]


        return result_df if is_dataframe else result_df.to_dict('records')

    # --- Array Scaling / Normalization ---
    # [scale_parameters_array, normalize_parameters_array, scale_and_normalize_parameters_array remain unchanged from previous version]
    def scale_parameters_array(self, data: Union[pd.DataFrame, List[Dict[str, Any]]], target_params: Optional[List[str]] = None) -> Union[pd.DataFrame, List[Dict[str, float]]]:
        """
        Apply scaling (log/neglog for numeric, index mapping for categorical) to ORIGINAL values.
        Produces values in the SCALED space. Inverse of descale + category mapping.

        Args:
            data: DataFrame or list of dicts with values in the original space.
            target_params: Optional list of variable parameter names to scale. If None, processes all
                           variable parameters present as columns in the input data.

        Returns:
            DataFrame or list of dicts with values in the SCALED space (numeric or index).
        """
        if self.all_parameters.empty:
            raise ValueError("Original parameter definitions are required for scaling.")

        is_dataframe = isinstance(data, pd.DataFrame)
        df = pd.DataFrame(data) if not is_dataframe else data.copy()

        variable_names_set = set(self.variable_parameters_names)

        if target_params is None:
            target_params = [col for col in df.columns if col in variable_names_set]
            if not target_params:
                logger.warning("No variable parameters found in input data for scaling.")
                return pd.DataFrame(index=df.index) if is_dataframe else []

        invalid_params = [p for p in target_params if p not in variable_names_set]
        if invalid_params: raise ValueError(f"Target parameters {invalid_params} are not variable or do not exist.")

        result_df = pd.DataFrame(index=df.index) # Initialize empty result
        processed_cols = set()

        for param_name in target_params:
            if param_name not in df.columns:
                logger.warning(f"Target parameter '{param_name}' not found in input data for scaling. Skipping.")
                continue
            try:
                original_info = self._get_param_info(param_name, 'original')
                transform = original_info.get('transform')
                param_type = original_info['type']
                values_col = df[param_name] # Original values from input

                scaled_values = pd.Series(index=values_col.index, dtype=float) # Expect float output generally

                if param_type in ['continuous', 'discrete']:
                    # Ensure input is numeric before applying transform
                    numeric_vals = pd.to_numeric(values_col, errors='coerce')
                    na_mask = numeric_vals.isna()
                    if na_mask.any():
                        logger.warning(f"Non-numeric values encountered in column '{param_name}' before scaling. NaNs will propagate.")

                    if transform in ['log', 'neglog']:
                        if transform == 'log':
                            # Check for non-positive values before log10
                            invalid_log_mask = numeric_vals <= 0
                            if invalid_log_mask[~na_mask].any(): # Check only non-NaN values
                                logger.warning(f"Non-positive values found for log transform in '{param_name}'. Resulting NaNs or -inf.")
                            # Apply log10 only to valid positive numbers
                            valid_mask = ~na_mask & ~invalid_log_mask
                            scaled_values[valid_mask] = np.log10(numeric_vals[valid_mask])
                        elif transform == 'neglog':
                            # Check for non-negative values before -log10(-x)
                            invalid_neglog_mask = numeric_vals >= 0
                            if invalid_neglog_mask[~na_mask].any(): # Check only non-NaN values
                                logger.warning(f"Non-negative values found for neglog transform in '{param_name}'. Resulting NaNs or -inf.")
                            # Apply neglog only to valid negative numbers
                            valid_mask = ~na_mask & ~invalid_neglog_mask
                            scaled_values[valid_mask] = -np.log10(-numeric_vals[valid_mask])
                    else: # Linear scale for numeric types
                        scaled_values = numeric_vals # Use the already coerced numeric values

                elif param_type == 'categorical':
                    # Map original category value to its index
                    categories = original_info.get('values') # Use original values from info
                    if not isinstance(categories, list):
                        raise TypeError(f"Invalid original categories list for '{param_name}' during scaling.")
                    try:
                        # Use normalize_categorical_value utility (which returns float index)
                        mapped_indices = pd.Series(index=values_col.index, dtype=float)
                        for idx, val in values_col.items():
                            # Allow NaN propagation if the original value was NaN/None
                            # and None is not explicitly a category
                            is_input_na = pd.isna(val)
                            if is_input_na and (None not in categories):
                                mapped_indices.loc[idx] = np.nan
                                continue
                            # If input is NaN and None *is* a category, map it
                            elif is_input_na and (None in categories):
                                val_to_map = None # Map the actual None value
                            else:
                                val_to_map = val

                            try:
                                mapped_indices.loc[idx] = normalize_categorical_value(val_to_map, categories)
                            except ValueError as map_err:
                                logger.error(f"Error mapping categorical value {repr(val_to_map)} for '{param_name}' at index {idx}: {map_err}")
                                mapped_indices.loc[idx] = np.nan # Assign NaN on mapping error

                        scaled_values = mapped_indices

                    except Exception as e_map: # Catch broader errors during apply
                        raise ValueError(f"Error mapping categorical values to indices for '{param_name}': {e_map}") from e_map
                else:
                    raise TypeError(f"Unsupported parameter type '{param_type}' for '{param_name}' during scaling.")

                result_df[param_name] = scaled_values
                processed_cols.add(param_name)
            except Exception as e:
                logger.error(f"Error scaling parameter '{param_name}': {e}", exc_info=True)
                raise e

        # Add back any columns from input df that were not processed
        for col in df.columns:
             if col not in processed_cols:
                 result_df[col] = df[col]


        return result_df if is_dataframe else result_df.to_dict('records')

    def normalize_parameters_array(self, data: Union[pd.DataFrame, List[Dict[str, Any]]], target_params: Optional[List[str]] = None) -> Union[pd.DataFrame, List[Dict[str, float]]]:
        """
        Normalize SCALED values to the [0,1] range.
        Applies standard numeric normalization to all types (continuous, discrete, categorical)
        based on their SCALED min/max range (which is [0, N-1] for categorical).
        Inverse of denormalize_parameters_array.

        Args:
            data: DataFrame or list of dicts with values in the SCALED space.
            target_params: Optional list of variable parameter names to normalize. If None, processes all
                           variable parameters present as columns in the input data.

        Returns:
            DataFrame or list of dicts with values normalized to [0,1].
        """
        if self.all_parameters_scaled.empty:
             raise ValueError("Parameters must be scaled first before normalizing array.")

        is_dataframe = isinstance(data, pd.DataFrame)
        df = pd.DataFrame(data) if not is_dataframe else data.copy()

        variable_names_set = set(self.variable_parameters_names)

        if target_params is None:
            target_params = [col for col in df.columns if col in variable_names_set]
            if not target_params:
                logger.warning("No variable parameters found in input data for normalization.")
                return pd.DataFrame(index=df.index) if is_dataframe else []

        invalid_params = [p for p in target_params if p not in variable_names_set]
        if invalid_params: raise ValueError(f"Target parameters {invalid_params} are not variable or do not exist.")

        result_df = pd.DataFrame(index=df.index) # Initialize empty result
        processed_cols = set()


        for param_name in target_params:
            if param_name not in df.columns:
                logger.warning(f"Target parameter '{param_name}' not found in input data for normalization. Skipping.")
                continue
            try:
                # Get SCALED parameter info (min/max are scaled numeric or index range)
                scaled_info = self._get_param_info(param_name, 'scaled')
                param_type = scaled_info['type']
                values_col = df[param_name] # Scaled values from input

                # All types are normalized using the standard numeric method on their scaled range
                if param_type in ['continuous', 'discrete', 'categorical']:
                    min_val_s = pd.to_numeric(scaled_info['min'], errors='raise')
                    max_val_s = pd.to_numeric(scaled_info['max'], errors='raise')

                    # Ensure input scaled values are numeric
                    numeric_vals = pd.to_numeric(values_col, errors='coerce')
                    na_mask = numeric_vals.isna()
                    if na_mask.any():
                        logger.warning(f"Input scaled values for '{param_name}' contain non-numeric data. NaNs will propagate.")

                    # Apply standard numeric normalization only to non-NaN values
                    normed_values = pd.Series(np.nan, index=numeric_vals.index)
                    normed_values[~na_mask] = numeric_vals[~na_mask].apply(
                        lambda x: normalize_parameter_value(x, min_val_s, max_val_s)
                    )
                    result_df[param_name] = normed_values
                else:
                    raise TypeError(f"Unsupported parameter type '{param_type}' for '{param_name}' during normalization.")

                processed_cols.add(param_name)
            except Exception as e:
                logger.error(f"Error normalizing parameter '{param_name}': {e}", exc_info=True)
                raise e

        # Add back any columns from input df that were not processed
        for col in df.columns:
             if col not in processed_cols:
                 result_df[col] = df[col]

        return result_df if is_dataframe else result_df.to_dict('records')

    def scale_and_normalize_parameters_array(self, data: Union[pd.DataFrame, List[Dict[str, Any]]], target_params: Optional[List[str]] = None, include_fixed: bool = True) -> Union[pd.DataFrame, List[Dict[str, float]]]:
        """
        Scale ORIGINAL values (log/neglog/index) then normalize the result to [0,1].
        Inverse of denormalize_and_descale_parameters_array.

        Args:
            data: DataFrame or list of dicts with values in the ORIGINAL space.
            target_params: Optional list of variable parameter names to process. If None, processes all
                           variable parameters present as columns in the input data.
            include_fixed: If True, adds columns for fixed parameters with their normalized default values.

        Returns:
            DataFrame or list of dicts with values normalized to [0,1].
        """
        if self.all_parameters.empty or self.all_parameters_scaled.empty or self.all_parameters_normed.empty:
             raise ValueError("Parameters must be loaded, scaled, and normalized first.")

        is_dataframe = isinstance(data, pd.DataFrame)
        df = pd.DataFrame(data) if not is_dataframe else data.copy()

        all_var_names_set = set(self.variable_parameters_names)
        all_fixed_names_set = set(self.fixed_parameters_names)

        if target_params is None:
            # Auto-detect variable cols present in input data
            target_params = [p for p in df.columns if p in all_var_names_set]
        else:
            # Validate provided target_params
            invalid = [p for p in target_params if p not in all_var_names_set]
            if invalid: raise ValueError(f"Target parameters {invalid} are not variable or do not exist.")

        # Identify fixed and ignored columns from input
        fixed_in_input = [p for p in df.columns if p in all_fixed_names_set]
        ignored_cols = [p for p in df.columns if p not in target_params and p not in all_fixed_names_set]
        if fixed_in_input and not include_fixed: logger.warning(f"Fixed parameters in input {fixed_in_input} ignored (include_fixed=False).")
        if ignored_cols: logger.warning(f"Input columns {ignored_cols} ignored (not variable or fixed).")

        if not target_params and not (include_fixed and all_fixed_names_set):
             logger.warning("No variable parameters selected for processing and no fixed parameters requested/available.")
             return pd.DataFrame(index=df.index) if is_dataframe else []

        # Define the columns expected in the final output
        final_output_cols = sorted(list(set(target_params + (list(all_fixed_names_set) if include_fixed else []))))

        # --- Step 1: Scale Original Data ---
        # Use the scale_parameters_array method which handles all types correctly
        # This method now also handles unprocessed columns correctly
        scaled_df = self.scale_parameters_array(df, target_params=target_params)

        # --- Step 2: Normalize Scaled Data ---
        # Use the normalize_parameters_array method
        # Pass only the columns that were intended to be scaled (target_params)
        # This method also handles unprocessed columns
        scaled_target_cols = [c for c in target_params if c in scaled_df.columns] # Columns successfully scaled
        normed_df = self.normalize_parameters_array(scaled_df, target_params=scaled_target_cols)

        # normed_df now contains normalized versions of target_params and potentially unprocessed columns from input

        # --- Step 3: Add Fixed Parameters (Normalized Defaults) ---
        if include_fixed:
             try:
                  # Get normalized defaults for fixed parameters
                  fixed_param_details = self.all_parameters_normed[self.all_parameters_normed['mode'] == 'fixed']
                  if not fixed_param_details.empty:
                      fixed_norms = fixed_param_details.set_index('name')['default'].to_dict()
                      # Add columns to normed_df, broadcasting the default value
                      for fixed_name, norm_def in fixed_norms.items():
                          if fixed_name not in normed_df.columns: # Avoid overwriting variable params accidentally
                               # Ensure index alignment before adding column
                               if not normed_df.index.equals(df.index): normed_df = normed_df.reindex(df.index)
                               normed_df[fixed_name] = norm_def
                          elif fixed_name in fixed_in_input:
                              # If fixed param was in input and processed (unlikely but possible), overwrite with default norm value
                              logger.debug(f"Overwriting fixed parameter '{fixed_name}' from input with normalized default.")
                              if not normed_df.index.equals(df.index): normed_df = normed_df.reindex(df.index) # Align index if needed
                              normed_df[fixed_name] = norm_def

             except Exception as e:
                  logger.error(f"Error adding fixed parameters during scale/normalize: {e}", exc_info=True)
                  logger.warning("Could not include fixed parameters due to error.")


        # --- Step 4: Reorder and Return ---
        # Ensure all expected columns are present, adding NaNs if missing
        # Reindex using the final desired output columns
        final_df = normed_df.reindex(columns=final_output_cols, fill_value=np.nan)

        # Ensure final dtypes are float where expected
        for col in final_df.columns:
             # Check if column contains only numeric-like data (allowing NaN)
             try:
                 # Attempt conversion, check if any non-NA value exists or if all are NA
                 numeric_col = pd.to_numeric(final_df[col], errors='coerce')
                 is_numeric_like = numeric_col.notna().any() or final_df[col].isna().all()
                 if is_numeric_like and final_df[col].dtype != float :
                     final_df[col] = numeric_col # Assign the coerced column
             except Exception: # Handle columns that cannot be converted at all (e.g., lists)
                 pass


        return final_df if is_dataframe else final_df.to_dict('records')


    # --- Utility and Representation ---
    # [get_parameter_info, write_to_file, __str__, __repr__ remain unchanged from previous version]
    def get_parameter_info(self, param_name: str) -> Optional[Dict[str, Any]]:
        """Get detailed original information about a parameter by name."""
        return self.get_parameter(param_name) # Use the existing method

    def write_to_file(self, file_path: str) -> None:
        """Write the *original* parameters definition to a file (JSON or CSV)."""
        if self.all_parameters.empty:
            logger.warning("No parameters to write.")
            return
        try:
            ext = file_path.split('.')[-1].lower()
            # Make a copy to safely modify for writing
            df_write = self.all_parameters.copy()

            # --- Prepare DataFrame for Writing ---
            # Replace actual NaN/None with a consistent representation if needed by format

            # Convert numeric columns: replace NaN with None (JSON/Dict compatibility)
            num_cols = ['min', 'max', 'step']
            for col in num_cols:
                 if col in df_write.columns: # Check if column exists
                      # Identify numeric columns carefully (avoid object columns with numbers)
                      if pd.api.types.is_numeric_dtype(df_write[col]) and df_write[col].dtype != object:
                         # Apply where pd.notna to keep numbers, else None
                         df_write[col] = df_write[col].where(pd.notna(df_write[col]), None)
                      else: # Handle object columns that might contain numbers/NaNs
                          # Coerce to numeric where possible, keep others, then replace NaN
                          # Be careful not to convert actual strings/objects that aren't numbers
                          def safe_convert_numeric(x):
                              if isinstance(x, (int, float, np.number)):
                                  return None if pd.isna(x) else x
                              # Attempt conversion for strings only if they look like numbers
                              # This part is tricky, might be better to rely on earlier validation
                              # For writing, let's just replace pd.NA/np.nan with None
                              return None if pd.isna(x) else x

                          df_write[col] = df_write[col].apply(safe_convert_numeric)


            # Ensure object columns have None instead of NaN/pd.NA
            obj_cols = ['values', 'default', 'scale', 'mode', 'transform', 'type', 'name'] # Cover all potential object/string types
            for col in obj_cols:
                 if col in df_write.columns:
                      # Apply generic replacement: pd.NA/NaN -> None
                      df_write[col] = df_write[col].apply(lambda x: None if pd.isna(x) else x)


            # --- Write File ---
            if ext == 'json':
                # Convert DataFrame to list of dicts
                records = df_write.to_dict(orient='records')
                # Writing with None might be better for preserving column structure if re-read
                with open(file_path, 'w', encoding='utf-8') as f:
                    # Use custom handler for potential numpy types if they sneak in
                    def default_serializer(obj):
                        if isinstance(obj, np.integer): return int(obj)
                        elif isinstance(obj, np.floating): return float(obj)
                        elif isinstance(obj, np.ndarray): return obj.tolist()
                        elif pd.isna(obj): return None
                        raise TypeError(f"Object of type {obj.__class__.__name__} is not JSON serializable")

                    json.dump(records, f, indent=4, allow_nan=False, default=default_serializer)
            elif ext == 'csv':
                 # Special handling for 'values' column: dump lists as JSON strings
                if 'values' in df_write.columns:
                     def format_values_for_csv(x):
                         if isinstance(x, list):
                             # Ensure internal Nones are represented as 'null' in JSON string
                             cleaned_list = [None if pd.isna(item) else item for item in x]
                             try:
                                return json.dumps(cleaned_list) # Dump list as JSON string
                             except TypeError:
                                 # Fallback for non-serializable items in list (shouldn't happen ideally)
                                 return json.dumps([str(i) for i in cleaned_list])
                         elif pd.isna(x):
                             return '' # Pandas default NA rep is empty string
                         else:
                             return x # Keep single values as they are

                     df_write['values'] = df_write['values'].apply(format_values_for_csv)

                # Write to CSV, using standard NA rep (empty string)
                df_write.to_csv(path_or_buf=file_path, index=False, encoding='utf-8')

            else:
                raise ValueError(f"Unsupported file format for writing: {ext}. Use 'json' or 'csv'.")

            logger.info(f"Original parameter definitions written to {file_path}")

        except Exception as e:
            logger.error(f"Error writing parameters to file '{file_path}': {e}", exc_info=True)

    def __str__(self) -> str:
        """Return a string representation of the Parameters object."""
        if self.error_parsing: return f"Parameters (Error: {self.error_parsing})"
        if self.all_parameters.empty: return "Parameters (empty)"
        cont, disc, cat = 0, 0, 0
        if 'type' in self.all_parameters.columns:
            counts = self.all_parameters['type'].value_counts()
            cont = counts.get('continuous', 0); disc = counts.get('discrete', 0); cat = counts.get('categorical', 0)
        # Access properties safely
        nr_total = self.nr_parameters
        nr_var = self.nr_variable_parameters
        nr_fixed = self.nr_fixed_parameters
        return (f"Parameters: {nr_total} total ({nr_var} variable, {nr_fixed} fixed) | Types: {cont} continuous, {disc} discrete, {cat} categorical")

    def __repr__(self) -> str:
        """Return a string representation suitable for debugging."""
        source = f"file='{self.file}'" if self.file else "from_data"
        status = f"Error='{self.error_parsing}'" if self.error_parsing else f"parameters={self.nr_parameters}"
        # Add scaled/normed status
        scaled_status = "scaled" if not self.all_parameters_scaled.empty else "not scaled"
        normed_status = "normalized" if not self.all_parameters_normed.empty else "not normalized"
        return f"Parameters({source}, {status}, {scaled_status}, {normed_status})"


# --- End of File Parameters.py ---
