"""
Parameters class for managing parameter configurations in aivalanche_lib.

This module provides functionality to parse, manage, and manipulate parameter
configurations from different file formats (JSON, CSV).

Author: Gazmend Alia
"""

import os, json, random, logging, pandas as pd, numpy as np
from typing import Dict, List, Optional, Union, Any
from .utils import scale_parameter_row, determine_scale, normalize_scale_value, normalize_parameter_row, determine_transform

# Set up logging
logger = logging.getLogger(__name__)

class Parameters:
    """
    A class for parsing and managing parameter configurations.

    This class provides functionality to load parameters from JSON or CSV files,
    access fixed and variable parameters separately, and generate random parameter values.

    Attributes:
        file (str): Path to the parameter file.
        all_parameters (pd.DataFrame): DataFrame containing all parameters.
        all_parameters_scaled (pd.DataFrame): DataFrame containing scaled parameters.
        error_parsing (Optional[str]): Error message if parsing fails.
    """

    def __init__(self, data: Optional[Union[str, pd.DataFrame, List[Dict[str, Any]]]] = None):
        """
        Initialize the Parameters class.

        Args:
            data: Input data in one of the following formats:
                - str: Path to a parameter file (JSON or CSV)
                - pd.DataFrame: DataFrame with parameter data
                - List[Dict[str, Any]]: List of parameter dictionaries
        """
        self.file = None  # Keep track of file if loaded from file
        self.all_parameters = pd.DataFrame()
        self.all_parameters_scaled = pd.DataFrame()  # Store scaled parameters
        self.all_parameters_normed = pd.DataFrame()  # Store normalized parameters (0-1 range)
        self.error_parsing = None
        self.raw_data = None

        if data is not None:
            self.load_data(data)

    @property
    def parameters_names(self) -> List[str]:
        """Get names of variable parameters."""
        return self.all_parameters['name'].tolist()

    @property
    def nr_parameters(self) -> int:
        """Get total number of parameters."""
        return len(self.all_parameters.index)

    @property
    def fixed_parameters(self) -> pd.DataFrame:
        """Get parameters with mode 'fixed'."""
        return self.all_parameters[self.all_parameters['mode'] == 'fixed']

    @property
    def fixed_parameters_names(self) -> List[str]:
        """Get names of variable parameters."""
        return self.fixed_parameters['name'].tolist()

    @property
    def nr_fixed_parameters(self) -> int:
        """Get number of fixed parameters."""
        return len(self.fixed_parameters.index)

    @property
    def variable_parameters(self) -> pd.DataFrame:
        """Get parameters with mode 'variable'."""
        return self.all_parameters[self.all_parameters['mode'] == 'variable']

    @property
    def variable_parameters_names(self) -> List[str]:
        """Get names of variable parameters."""
        return self.variable_parameters['name'].tolist()

    @property
    def nr_variable_parameters(self) -> int:
        """Get number of variable parameters."""
        return len(self.variable_parameters.index)

    @property
    def columns(self) -> List[str]:
        """Get column names of the parameters DataFrame."""
        return list(self.all_parameters.columns)

    @property
    def fixed_parameters_scaled(self) -> pd.DataFrame:
        """Get scaled parameters with mode 'fixed'."""
        if self.all_parameters_scaled.empty:
            return pd.DataFrame()
        return self.all_parameters_scaled[self.all_parameters_scaled['mode'] == 'fixed']

    @property
    def variable_parameters_scaled(self) -> pd.DataFrame:
        """Get scaled parameters with mode 'variable'."""
        if self.all_parameters_scaled.empty:
            return pd.DataFrame()
        return self.all_parameters_scaled[self.all_parameters_scaled['mode'] == 'variable']

    @property
    def fixed_parameters_normed(self) -> pd.DataFrame:
        """Get normalized parameters with mode 'fixed'."""
        if self.all_parameters_normed.empty:
            return pd.DataFrame()
        return self.all_parameters_normed[self.all_parameters_normed['mode'] == 'fixed']

    @property
    def variable_parameters_normed(self) -> pd.DataFrame:
        """Get normalized parameters with mode 'variable'."""
        if self.all_parameters_normed.empty:
            return pd.DataFrame()
        return self.all_parameters_normed[self.all_parameters_normed['mode'] == 'variable']

    def load_data(self, data: Union[str, pd.DataFrame, List[Dict[str, Any]]]) -> None:
        """
        Load parameters from various data sources.

        Args:
            data: Input data in one of the following formats:
                - str: Path to a parameter file (JSON or CSV)
                - pd.DataFrame: DataFrame with parameter data
                - List[Dict[str, Any]]: List of parameter dictionaries
        """
        self.error_parsing = None

        if isinstance(data, str):
            # Input is a file path
            self.file = data
            self.parse_file(data)
        elif isinstance(data, pd.DataFrame):
            # Input is a DataFrame
            self.load_from_dataframe(data)
        elif isinstance(data, list) and all(isinstance(item, dict) for item in data):
            # Input is a list of dictionaries
            self.load_from_dict_list(data)
        else:
            self.error_parsing = f"Unsupported data type: {type(data)}"
            return

        # If we successfully loaded the data, validate and normalize it
        if not self.error_parsing and not self.all_parameters.empty:
            self._check_min_max_order()
            self._check_default_values()
            self._check_mode_values()
            self._check_scale_values()
            self._set_transform_types()
            self.sort_parameters_by_name()
            self._scale_parameters()  # Scale parameters based on their scale type
            self._normalize_parameters()  # Normalize parameters to [0,1] range

    def load_from_dataframe(self, df: pd.DataFrame) -> None:
        """
        Load parameters from a DataFrame.

        Args:
            df (pd.DataFrame): DataFrame containing parameter data.
        """
        required_columns = ['name', 'min', 'max']
        missing_columns = [col for col in required_columns if col not in df.columns]

        if missing_columns:
            self.error_parsing = f"DataFrame missing required columns: {', '.join(missing_columns)}"
            return

        self.all_parameters = df.copy()

    def load_from_dict_list(self, dict_list: List[Dict[str, Any]]) -> None:
        """
        Load parameters from a list of dictionaries.

        Args:
            dict_list (List[Dict[str, Any]]): List of parameter dictionaries.
        """
        try:
            # Check that each dictionary has the required keys
            required_keys = ['name', 'min', 'max']
            for i, param_dict in enumerate(dict_list):
                missing_keys = [key for key in required_keys if key not in param_dict]
                if missing_keys:
                    self.error_parsing = f"Dictionary at index {i} missing required keys: {', '.join(missing_keys)}"
                    return

            self.all_parameters = pd.DataFrame(dict_list)
        except Exception as e:
            self.error_parsing = f"Error loading from dictionary list: {str(e)}"

    def parse_file(self, file_path: str) -> None:
        """
        Parse the parameter file based on its extension.

        Supported formats: JSON, CSV

        Args:
            file_path (str): Path to the parameter file.
        """
        if not os.path.exists(file_path):
            self.error_parsing = f"File not found: {file_path}"
            return

        try:
            ext = file_path.split('.')[-1].lower()
            if ext == 'json':
                self.parse_json(file_path)
            elif ext == 'csv':
                self.parse_csv(file_path)
            else:
                self.error_parsing = f"Unsupported file format: {ext}"
        except Exception as e:
            self.error_parsing = f"Error parsing file: {str(e)}"

    def parse_json(self, file_path: str) -> None:
        """
        Parse a JSON file into the parameters DataFrame.

        Args:
            file_path (str): Path to the JSON file.
        """
        try:
            with open(file_path) as json_file:
                self.raw_data = json.load(json_file)

                # Convert to DataFrame if it's a list of dictionaries
                if isinstance(self.raw_data, list):
                    self.all_parameters = pd.DataFrame.from_dict(self.raw_data)
                # Handle case where it's a dictionary with parameter names as keys
                elif isinstance(self.raw_data, dict):
                    param_list = []
                    for name, values in self.raw_data.items():
                        if isinstance(values, dict):
                            values['name'] = name
                            param_list.append(values)
                    self.all_parameters = pd.DataFrame(param_list)

        except json.JSONDecodeError as e:
            self.error_parsing = f"Invalid JSON format: {str(e)}"
        except Exception as e:
            self.error_parsing = f"Error parsing JSON: {str(e)}"

    def parse_csv(self, file_path: str) -> None:
        """
        Parse a CSV file into the parameters DataFrame.

        Args:
            file_path (str): Path to the CSV file.
        """
        try:
            self.raw_data = pd.read_csv(filepath_or_buffer=file_path, comment='#')
            self.all_parameters = self.raw_data
        except Exception as e:
            self.error_parsing = f"Error parsing CSV: {str(e)}"

    def _check_min_max_order(self) -> None:
        """
        Check if min is larger than max and swap them if needed.
        """
        # Convert min and max to numeric if not already
        self.all_parameters['min'] = pd.to_numeric(self.all_parameters['min'], errors='coerce')
        self.all_parameters['max'] = pd.to_numeric(self.all_parameters['max'], errors='coerce')

        # Find parameters where min > max
        swap_needed = self.all_parameters['min'] > self.all_parameters['max']
        swap_params = self.all_parameters.loc[swap_needed, 'name'].tolist()

        if swap_params:
            # Swap min and max values
            temp = self.all_parameters.loc[swap_needed, 'min'].copy()
            self.all_parameters.loc[swap_needed, 'min'] = self.all_parameters.loc[swap_needed, 'max']
            self.all_parameters.loc[swap_needed, 'max'] = temp

            # Log the swapped parameters
            logger.info(f"Swapped min and max values for parameters: {', '.join(swap_params)}")
            print(f"INFO: Swapped min and max values for parameters: {', '.join(swap_params)}")

    def _check_default_values(self) -> None:
        """
        Check if default values are provided and valid.
        If not provided, set to middle value between min and max.
        If not within min-max range, issue a warning.
        """
        # Create default column if it doesn't exist
        if 'default' not in self.all_parameters.columns:
            self.all_parameters['default'] = (self.all_parameters['min'] + self.all_parameters['max']) / 2
            logger.info("Default values were not provided. Using middle values between min and max.")
            print("INFO: Default values were not provided. Using middle values between min and max.")
        else:
            # Convert default to numeric
            self.all_parameters['default'] = pd.to_numeric(self.all_parameters['default'], errors='coerce')

            # Check if default values are outside the min-max range
            below_min = self.all_parameters['default'] < self.all_parameters['min']
            above_max = self.all_parameters['default'] > self.all_parameters['max']

            out_of_range_params_below = self.all_parameters.loc[below_min, 'name'].tolist()
            out_of_range_params_above = self.all_parameters.loc[above_max, 'name'].tolist()

            if out_of_range_params_below:
                logger.warning(f"Default values below min for parameters: {', '.join(out_of_range_params_below)}")
                print(f"WARNING: Default values below min for parameters: {', '.join(out_of_range_params_below)}")

            if out_of_range_params_above:
                logger.warning(f"Default values above max for parameters: {', '.join(out_of_range_params_above)}")
                print(f"WARNING: Default values above max for parameters: {', '.join(out_of_range_params_above)}")

    def _check_mode_values(self) -> None:
        """
        Check if mode values are provided and valid.
        If not provided, set to 'variable'.
        If not 'fixed' or 'variable', set to 'variable'.
        """
        if 'mode' not in self.all_parameters.columns:
            self.all_parameters['mode'] = 'variable'
            logger.info("Mode values were not provided. All parameters set to 'variable'.")
            print("INFO: Mode values were not provided. All parameters set to 'variable'.")
        else:
            # Check for invalid mode values
            valid_modes = ['fixed', 'variable']
            invalid_mode_mask = ~self.all_parameters['mode'].isin(valid_modes)
            invalid_mode_params = self.all_parameters.loc[invalid_mode_mask, 'name'].tolist()

            if invalid_mode_params:
                self.all_parameters.loc[invalid_mode_mask, 'mode'] = 'variable'
                logger.info(f"Invalid mode values for parameters: {', '.join(invalid_mode_params)}. Set to 'variable'.")
                print(f"INFO: Invalid mode values for parameters: {', '.join(invalid_mode_params)}. Set to 'variable'.")

    def _check_scale_values(self) -> None:
        """
        Check if scale values are provided and valid.
        If not provided, determine based on min/max values:
        - If min and max have different signs, set to 'lin'
        - If same sign and ratio > 100, set to 'log'
        - Otherwise, set to 'lin'
        """
        if 'scale' not in self.all_parameters.columns:
            # If scale column doesn't exist, create it and determine scales
            self.all_parameters['scale'] = self.all_parameters.apply(
                lambda row: determine_scale(row['min'], row['max']), axis=1
                )

            # Log the determined scales
            scale_counts = self.all_parameters['scale'].value_counts()
            logger.info(f"Scale values were determined automatically: {dict(scale_counts)}")
            print(f"INFO: Scale values were determined automatically: {dict(scale_counts)}")
        else:
            # Normalize existing scale values
            self.all_parameters['scale'] = self.all_parameters['scale'].apply(normalize_scale_value)

            # Find rows with invalid scale values
            invalid_mask = self.all_parameters['scale'].isna()
            invalid_count = invalid_mask.sum()

            if invalid_count > 0:
                # Fix invalid scales
                self.all_parameters.loc[invalid_mask, 'scale'] = self.all_parameters[invalid_mask].apply(
                    lambda row: determine_scale(row['min'], row['max']), axis=1
                )

                logger.info(f"Fixed {invalid_count} invalid scale values")
                print(f"INFO: Fixed {invalid_count} invalid scale values")

    def _set_transform_types(self) -> None:
        """
        Determine the appropriate transform type for each parameter.

        For log-scaled parameters:
        - If min and max are both positive: use 'log' transform
        - If min and max are both negative: use 'neglog' transform
        - If min and max have different signs: keep 'lin' scale
        """

        # Add transform column and set values
        self.all_parameters['transform'] = self.all_parameters.apply(determine_transform, axis=1)

        # Reset scale to 'lin' for parameters with mixed sign range that were marked as 'log'
        mixed_sign_mask = (self.all_parameters['scale'] == 'log') & (self.all_parameters['transform'].isna())
        if mixed_sign_mask.any():
            mixed_params = self.all_parameters.loc[mixed_sign_mask, 'name'].tolist()
            self.all_parameters.loc[mixed_sign_mask, 'scale'] = 'lin'
            logger.info(f"Changed scale to 'lin' for parameters with mixed sign range: {', '.join(mixed_params)}")
            print(f"INFO: Changed scale to 'lin' for parameters with mixed sign range: {', '.join(mixed_params)}")

        # Log information about transformations
        log_transforms = self.all_parameters[self.all_parameters['transform'] == 'log']
        neglog_transforms = self.all_parameters[self.all_parameters['transform'] == 'neglog']

        if not log_transforms.empty:
            log_params = log_transforms['name'].tolist()
            logger.info(f"Using log transform for positive parameters: {', '.join(log_params)}")
            print(f"INFO: Using log transform for positive parameters: {', '.join(log_params)}")

        if not neglog_transforms.empty:
            neglog_params = neglog_transforms['name'].tolist()
            logger.info(f"Using negative log transform for negative parameters: {', '.join(neglog_params)}")
            print(f"INFO: Using negative log transform for negative parameters: {', '.join(neglog_params)}")

    def _scale_parameters(self) -> None:
        """
        Scale parameters according to their scale type.

        For parameters with scale='log', takes the log10 of min, max, and default values.
        This primarily affects variable parameters. Results are stored in self.all_parameters_scaled.
        """
        if self.all_parameters.empty:
            self.all_parameters_scaled = pd.DataFrame()
            return

        # Create a copy of the original parameters
        self.all_parameters_scaled = self.all_parameters.copy()

        # Apply scaling function to all rows
        self.all_parameters_scaled = self.all_parameters_scaled.apply(scale_parameter_row, axis=1)

        # Log information
        log_params = self.all_parameters[self.all_parameters['scale'] == 'log']
        logger.info(f"Scaled {len(log_params)} parameters with log scale")
        if len(log_params) > 0:
            print(f"INFO: Scaled {len(log_params)} parameters with log scale: {', '.join(log_params['name'].tolist())}")

    def _normalize_parameters(self) -> None:
        """
        Normalize parameters to the [0,1] range.

        This uses the scaled parameters (if log scaling is applied) and normalizes them to [0,1].
        Results are stored in self.all_parameters_normed.
        """
        if self.all_parameters_scaled.empty:
            self.all_parameters_normed = pd.DataFrame()
            return

        # Create a copy of the scaled parameters
        self.all_parameters_normed = self.all_parameters_scaled.copy()

        # Apply normalization to all rows
        self.all_parameters_normed = self.all_parameters_normed.apply(normalize_parameter_row, axis=1)

        logger.info(f"Normalized {len(self.all_parameters_normed)} parameters to [0,1] range")
        print(f"INFO: Normalized {len(self.all_parameters_normed)} parameters to [0,1] range")

    def generate_random_parameters(self) -> Dict[str, float]:
        """
        Generate random values for all parameters.

        For fixed parameters, uses the default value.
        For variable parameters, generates a random value between min and max.

        Returns:
            Dict[str, float]: Dictionary mapping parameter names to their values.
        """
        if self.all_parameters.empty:
            return {}

        return self.all_parameters.set_index('name').apply(self._generate_random_value, axis=1).to_dict()

    def get_default_parameters(self) -> Dict[str, float]:
        """
        Get default values for all parameters.

        Returns:
            Dict[str, float]: Dictionary mapping parameter names to their default values.
        """
        if self.all_parameters.empty:
            return {}

        return self.all_parameters.set_index('name')['default'].to_dict()

    def _generate_random_value(self, row: pd.Series) -> float:
        """
        Generate a random value for a parameter based on its mode.

        Args:
            row (pd.Series): Row from the parameters DataFrame.

        Returns:
            float: Random value or default value based on the parameter's mode.
        """
        if row['mode'] == 'fixed':
            return row['default']
        else:
            return random.uniform(row['min'], row['max'])

    def write_to_file(self, file_path: str) -> None:
        """
        Write parameters to a file.

        Args:
            file_path (str): Path to the output file.
        """
        if self.all_parameters.empty:
            return

        try:
            ext = file_path.split('.')[-1].lower()
            if ext == 'json':
                self.all_parameters.to_json(path_or_buf=file_path, orient='records', indent=4)
            elif ext == 'csv':
                self.all_parameters.to_csv(path_or_buf=file_path, index=False)
            else:
                raise ValueError(f"Unsupported file format: {ext}")
        except Exception as e:
            logger.error(f"Error writing to file: {str(e)}")
            print(f"ERROR: Error writing to file: {str(e)}")

    def sort_parameters_by_name(self) -> None:
        """Sort the parameters DataFrame by name."""
        self.all_parameters = self.all_parameters.sort_values(by='name').reset_index(drop=True)

    def add_parameter(self, name: str, min_val: float, max_val: float, default: float = None,
                     scale: str = 'lin', mode: str = 'variable') -> None:
        """
        Add a new parameter to the parameters DataFrame.

        Args:
            name (str): Name of the parameter.
            min_val (float): Minimum value.
            max_val (float): Maximum value.
            default (float, optional): Default value. If None, uses middle of range.
            scale (str, optional): Scale type ('lin', 'log'). Defaults to 'lin'.
            mode (str, optional): Parameter mode ('fixed', 'variable'). Defaults to 'variable'.
        """
        # Apply checks to the new parameter values
        if min_val > max_val:
            min_val, max_val = max_val, min_val
            print(f"INFO: Swapped min and max values for parameter '{name}'")

        # Set default to middle value if not provided
        if default is None:
            default = (min_val + max_val) / 2
            print(f"INFO: Default value not provided for parameter '{name}'. Using middle value.")
        elif default < min_val:
            print(f"WARNING: Default value below min for parameter '{name}'")
        elif default > max_val:
            print(f"WARNING: Default value above max for parameter '{name}'")

        # Check for invalid mode
        if mode not in ['fixed', 'variable']:
            mode = 'variable'
            print(f"INFO: Invalid mode value for parameter '{name}'. Set to 'variable'.")

        # Check for invalid scale
        if scale.lower() not in ['lin', 'log', 'linear', 'logarithmic']:
            scale = 'lin'
            print(f"INFO: Invalid scale value for parameter '{name}'. Set to 'lin'.")
        elif scale.lower() == 'linear':
            scale = 'lin'
        elif scale.lower() == 'logarithmic':
            scale = 'log'

        # Determine scale automatically if not specified or if it's 'auto'
        if scale == 'auto':
            if min_val * max_val < 0:
                scale = 'lin'
                reason = "different signs"
            elif min_val != 0 and max_val != 0 and abs(max_val / min_val) > 100:
                scale = 'log'
                reason = "ratio > 100"
            else:
                scale = 'lin'
                reason = "default case"
            print(f"INFO: Scale for parameter '{name}' automatically set to '{scale}' ({reason})")

        new_param = {
            'name': name,
            'min': min_val,
            'max': max_val,
            'default': default,
            'scale': scale,
            'mode': mode
        }

        # If parameter already exists, update it
        if name in self.all_parameters['name'].values:
            idx = self.all_parameters[self.all_parameters['name'] == name].index[0]
            for key, value in new_param.items():
                self.all_parameters.at[idx, key] = value
        else:
            # Otherwise add it as a new row
            self.all_parameters = pd.concat([
                self.all_parameters,
                pd.DataFrame([new_param])
            ], ignore_index=True)

        self.sort_parameters_by_name()
        self._scale_parameters()  # Update scaled parameters
        self._normalize_parameters()  # Update normalized parameters

    def remove_parameter(self, name: str) -> bool:
        """
        Remove a parameter from the parameters DataFrame.

        Args:
            name (str): Name of the parameter to remove.

        Returns:
            bool: True if the parameter was found and removed, False otherwise.
        """
        if name in self.all_parameters['name'].values:
            self.all_parameters = self.all_parameters[self.all_parameters['name'] != name]
            # Update scaled parameters
            if not self.all_parameters.empty:
                self._scale_parameters()
                self._normalize_parameters()
            else:
                self.all_parameters_scaled = pd.DataFrame()
                self.all_parameters_normed = pd.DataFrame()
            return True
        return False

    def get_parameter(self, name: str) -> Optional[Dict[str, Any]]:
        """
        Get a parameter by name.

        Args:
            name (str): Name of the parameter.

        Returns:
            Optional[Dict[str, Any]]: Dictionary with parameter values or None if not found.
        """
        if self.all_parameters.empty or name not in self.all_parameters['name'].values:
            return None
        param = self.all_parameters[self.all_parameters['name'] == name].iloc[0]
        return param.to_dict()

    def get_parameter_scaled(self, name: str) -> Optional[Dict[str, Any]]:
        """
        Get a scaled parameter by name.

        Args:
            name (str): Name of the parameter.

        Returns:
            Optional[Dict[str, Any]]: Dictionary with scaled parameter values or None if not found.
        """
        if self.all_parameters_scaled.empty or name not in self.all_parameters_scaled['name'].values:
            return None
        param = self.all_parameters_scaled[self.all_parameters_scaled['name'] == name].iloc[0]
        return param.to_dict()

    def get_parameter_normed(self, name: str) -> Optional[Dict[str, Any]]:
        """
        Get a normalized parameter by name.

        Args:
            name (str): Name of the parameter.

        Returns:
            Optional[Dict[str, Any]]: Dictionary with normalized parameter values or None if not found.
        """
        if self.all_parameters_normed.empty or name not in self.all_parameters_normed['name'].values:
            return None
        param = self.all_parameters_normed[self.all_parameters_normed['name'] == name].iloc[0]
        return param.to_dict()

    def denormalize_parameters_array(self, data: Union[pd.DataFrame, List[Dict[str, float]]], validate_data: bool = True,
                                     include_fixed_parameters: bool = True) -> Union[pd.DataFrame, List[Dict[str, float]]]:
        """
        Convert normalized parameter values (0-1 range) back to their scaled range.
        Does NOT apply inverse transformations (log, neglog).

        Args:
            data: Input data in one of the following formats:
                - pd.DataFrame: DataFrame with parameter names as columns
                - List[Dict[str, float]]: List of dictionaries with parameter names as keys
            include_fixed_parameters: If True, adds fixed parameters with their default values

        Returns:
            Same type as input, with values denormalized to their scaled ranges
        """
        if self.all_parameters_normed.empty:
            raise ValueError("Parameters have not been normalized yet")

        # Track the input type to return the same type
        is_dataframe = isinstance(data, pd.DataFrame)

        # Convert list of dicts to DataFrame if needed
        if not is_dataframe:
            try:
                df = pd.DataFrame(data)
            except Exception as e:
                raise ValueError(f"Failed to convert input to DataFrame: {str(e)}")
        else:
            df = data.copy()

        if validate_data:
            # Get all parameter names from the input data
            input_param_names = set(df.columns)

            # Get fixed parameters names
            fixed_param_names = set(self.fixed_parameters_names)

            # Get variable parameters names
            variable_param_names = set(self.variable_parameters_names)

            # Check if all input parameters are valid variable parameters
            if not input_param_names - fixed_param_names == variable_param_names:
                # Find the invalid parameters
                invalid_params = input_param_names - variable_param_names
                raise ValueError(f"Parameters {list(invalid_params)} are not valid variable parameters and cannot be scaled")

        # Keep only the variable parameters
        df = df[self.variable_parameters_names]

        # Get parameter info for all parameters in one step
        param_info_dict = {row['name']: {'min': row['min'], 'max': row['max']} for _, row in self.variable_parameters_scaled.iterrows()}

        # Apply denormalization to each column using vectorized operations
        for param_name in self.variable_parameters_names:
            min_val = param_info_dict[param_name]['min']
            max_val = param_info_dict[param_name]['max']
            df[param_name] = min_val + df[param_name] * (max_val - min_val)

        # Add fixed parameters if requested
        if include_fixed_parameters and not self.fixed_parameters_scaled.empty:
            for _, param in self.fixed_parameters_scaled.iterrows():
                df[param['name']] = param['default']

        # Return in the same format as input
        if is_dataframe:
            return df
        else:
            return df.to_dict('records')

    def descale_parameters_array(self, data: Union[pd.DataFrame, List[Dict[str, float]]], validate_data: bool = True,
                                 include_fixed_parameters: bool = True) -> Union[pd.DataFrame, List[Dict[str, float]]]:
        """
        Apply inverse scaling transformations to parameters (e.g., 10^x for log-scaled parameters).

        Args:
            data: Input data in one of the following formats:
                - pd.DataFrame: DataFrame with parameter names as columns
                - List[Dict[str, float]]: List of dictionaries with parameter names as keys

        Returns:
            Same type as input, with inverse scaling applied
        """
        # Track the input type to return the same type
        is_dataframe = isinstance(data, pd.DataFrame)

        # Convert list of dicts to DataFrame if needed
        if not is_dataframe:
            try:
                df = pd.DataFrame(data)
            except Exception as e:
                raise ValueError(f"Failed to convert input to DataFrame: {str(e)}")
        else:
            df = data.copy()

        if validate_data:
            # Get all parameter names from the input data
            input_param_names = set(df.columns)

            # Get fixed parameters names
            fixed_param_names = set(self.fixed_parameters_names)

            # Get variable parameters names
            variable_param_names = set(self.variable_parameters_names)

            # Check if all input parameters are valid variable parameters
            if not input_param_names - fixed_param_names == variable_param_names:
                # Find the invalid parameters
                invalid_params = input_param_names - variable_param_names
                raise ValueError(f"Parameters {list(invalid_params)} are not valid variable parameters and cannot be scaled")

        # Keep only the variable parameters
        df = df[self.variable_parameters_names]

        # Get transform info for all parameters in one step
        transform_dict = {row['name']: row.get('transform') for _, row in self.variable_parameters.iterrows()}

        # Process parameters by transform type
        log_params = [name for name, transform in transform_dict.items() if transform == 'log']
        neglog_params = [name for name, transform in transform_dict.items() if transform == 'neglog']

        # Apply inverse transformations using vectorized operations
        for param_name in log_params:
            df[param_name] = 10 ** df[param_name]

        for param_name in neglog_params:
            df[param_name] = -10 ** -df[param_name]

        # Add fixed parameters if requested
        if include_fixed_parameters and not self.fixed_parameters.empty:
            for _, param in self.fixed_parameters.iterrows():
                df[param['name']] = param['default']

        # Return in the same format as input
        if is_dataframe:
            return df
        else:
            return df.to_dict('records')

    def denormalize_and_descale_parameters_array(self, data: Union[pd.DataFrame, List[Dict[str, float]]], validate_data: bool = True,
                                                 include_fixed_parameters: bool = True) -> Union[pd.DataFrame, List[Dict[str, float]]]:
        """
        Convert normalized parameter values back to their original ranges and apply
        inverse scaling transformations.

        This is a convenience method that combines de_normalize_parameters and de_scale_parameters.

        Args:
            data: Input data in one of the following formats:
                - pd.DataFrame: DataFrame with parameter names as columns
                - List[Dict[str, float]]: List of dictionaries with parameter names as keys
            include_fixed_parameters: If True, adds fixed parameters with their default values

        Returns:
            Same type as input, with values converted back to their original ranges
        """
        # First denormalize (0-1 to min-max in scaled space)
        denormalized = self.denormalize_parameters_array(data, validate_data, include_fixed_parameters = False)

        # Then descale (apply inverse transformations)
        return self.descale_parameters_array(denormalized, validate_data = False, include_fixed_parameters = include_fixed_parameters)


    def scale_parameters_array(self, data: Union[pd.DataFrame, List[Dict[str, float]]], validate_data: bool = True,
                               include_fixed_parameters: bool = True) -> Union[pd.DataFrame, List[Dict[str, float]]]:
        """
        Apply scaling transformations to parameters (e.g., log10(x) for log-scaled parameters).
        This is the inverse of descale_parameters_array.

        Args:
            data: Input data in one of the following formats:
                - pd.DataFrame: DataFrame with parameter names as columns
                - List[Dict[str, float]]: List of dictionaries with parameter names as keys
            validate_data: If True, validates that all input parameters are valid variable parameters
            include_fixed_parameters: If True, includes fixed parameters with their scaled values

        Returns:
            Same type as input, with scaling applied
        """
        # Track the input type to return the same type
        is_dataframe = isinstance(data, pd.DataFrame)

        # Convert list of dicts to DataFrame if needed
        if not is_dataframe:
            try:
                df = pd.DataFrame(data)
            except Exception as e:
                raise ValueError(f"Failed to convert input to DataFrame: {str(e)}")
        else:
            df = data.copy()

        if validate_data:
            # Get all parameter names from the input data
            input_param_names = set(df.columns)

            # Get fixed parameters names
            fixed_param_names = set(self.fixed_parameters_names)

            # Get variable parameters names
            variable_param_names = set(self.variable_parameters_names)

            # Check if all input parameters are valid variable parameters
            if not input_param_names - fixed_param_names == variable_param_names:
                # Find the invalid parameters
                invalid_params = input_param_names - variable_param_names
                raise ValueError(f"Parameters {list(invalid_params)} are not valid variable parameters and cannot be scaled")

        # Keep only the variable parameters
        df = df[self.variable_parameters_names]

        # Get transform info for all parameters in one step
        transform_dict = {row['name']: row.get('transform') for _, row in self.variable_parameters.iterrows()}

        # Process parameters by transform type
        log_params = [name for name, transform in transform_dict.items() if transform == 'log' and name in df.columns]
        neglog_params = [name for name, transform in transform_dict.items() if transform == 'neglog' and name in df.columns]

        # Apply transformations using vectorized operations
        for param_name in log_params:
            # Ensure values are positive before taking log
            if (df[param_name] <= 0).any():
                min_positive = 1e-20  # Small positive value
                invalid_indices = df[param_name] <= 0
                if invalid_indices.any():
                    logger.warning(f"Found {invalid_indices.sum()} non-positive values in log-scaled parameter '{param_name}'. Setting to {min_positive}.")
                    df.loc[invalid_indices, param_name] = min_positive

            df[param_name] = np.log10(df[param_name])

        for param_name in neglog_params:
            # Ensure values are negative before taking neglog
            if (df[param_name] >= 0).any():
                max_negative = -1e-20  # Small negative value
                invalid_indices = df[param_name] >= 0
                if invalid_indices.any():
                    logger.warning(f"Found {invalid_indices.sum()} non-negative values in neglog-scaled parameter '{param_name}'. Setting to {max_negative}.")
                    df.loc[invalid_indices, param_name] = max_negative

            df[param_name] = -np.log10(-df[param_name])

        # Add fixed parameters if requested
        if include_fixed_parameters and not self.fixed_parameters_scaled.empty:
                for _, param in self.fixed_parameters_scaled.iterrows():
                    df[param['name']] = param['default']

        # Return in the same format as input
        if is_dataframe:
            return df
        else:
            return df.to_dict('records')

    def normalize_parameters_array(self, data: Union[pd.DataFrame, List[Dict[str, float]]], validate_data: bool = True,
                                   include_fixed_parameters: bool = True) -> Union[pd.DataFrame, List[Dict[str, float]]]:
        """
        Normalize parameter values to the 0-1 range based on min and max values.
        This is the inverse of denormalize_parameters_array.

        Args:
            data: Input data in one of the following formats:
                - pd.DataFrame: DataFrame with parameter names as columns
                - List[Dict[str, float]]: List of dictionaries with parameter names as keys
            validate_data: If True, validates that all input parameters are valid parameters
            include_fixed_parameters: If True, includes fixed parameters with their normalized values

        Returns:
            Same type as input, with values normalized to the 0-1 range
        """
        # Track the input type to return the same type
        is_dataframe = isinstance(data, pd.DataFrame)

        # Convert list of dicts to DataFrame if needed
        if not is_dataframe:
            try:
                df = pd.DataFrame(data)
            except Exception as e:
                raise ValueError(f"Failed to convert input to DataFrame: {str(e)}")
        else:
            df = data.copy()

        if validate_data:
            # Get all parameter names from the input data
            input_param_names = set(df.columns)

            # Get fixed parameters names
            fixed_param_names = set(self.fixed_parameters_names)

            # Get variable parameters names
            variable_param_names = set(self.variable_parameters_names)

            # Check if all input parameters are valid variable parameters
            if not input_param_names - fixed_param_names == variable_param_names:
                # Find the invalid parameters
                invalid_params = input_param_names - variable_param_names
                raise ValueError(f"Parameters {list(invalid_params)} are not valid variable parameters and cannot be scaled")

        # Keep only the variable parameters
        df = df[self.variable_parameters_names]

        # Get parameter info for all parameters in one step
        param_info_dict = {row['name']: {'min': row['min'], 'max': row['max']} for _, row in self.variable_parameters_scaled.iterrows()}

        # Apply normalization to each column using vectorized operations
        for param_name, info in param_info_dict.items():
            min_val = info['min']
            max_val = info['max']
            range_val = max_val - min_val

            if range_val == 0:
                logger.warning(f"Parameter '{param_name}' has equal min and max values ({min_val}). Normalization will set all values to 0.5.")
                df[param_name] = 0.5
            else:
                df[param_name] = (df[param_name] - min_val) / range_val

        # Add fixed parameters if requested
        if include_fixed_parameters and not self.fixed_parameters_normed.empty:
                for _, param in self.fixed_parameters_normed.iterrows():
                    df[param['name']] = param['default']

        # Return in the same format as input
        if is_dataframe:
            return df
        else:
            return df.to_dict('records')

    def scale_and_normalize_parameters_array(self, data: Union[pd.DataFrame, List[Dict[str, float]]], validate_data: bool = True,
                                             include_fixed_parameters: bool = True) -> Union[pd.DataFrame, List[Dict[str, float]]]:
        """
        Apply scaling transformations to parameters and then normalize to the 0-1 range.
        This is the inverse of denormalize_and_descale_parameters_array.

        Args:
            data: Input data in one of the following formats:
                - pd.DataFrame: DataFrame with parameter names as columns
                - List[Dict[str, float]]: List of dictionaries with parameter names as keys
            validate_data: If True, validates that all input parameters are valid parameters
            include_fixed_parameters: If True, includes fixed parameters with their scaled and normalized values

        Returns:
            Same type as input, with values scaled and normalized
        """
        # First apply scaling transformations (log, neglog)
        scaled_data = self.scale_parameters_array(data, validate_data, include_fixed_parameters=False)

        # Then normalize to 0-1 range
        return self.normalize_parameters_array(scaled_data, validate_data=False, include_fixed_parameters=include_fixed_parameters)

    def __str__(self) -> str:
        """
        Return a string representation of the Parameters object.

        Returns:
            str: String representation with key information.
        """
        if self.error_parsing:
            return f"Parameters (Error: {self.error_parsing})"

        return (f"Parameters: {self.nr_parameters} total "
                f"({self.nr_variable_parameters} variable, "
                f"{self.nr_fixed_parameters} fixed)")

    def __repr__(self) -> str:
        """
        Return a string representation suitable for debugging.

        Returns:
            str: Detailed string representation.
        """
        source = f"file='{self.file}'" if self.file else "from_data"
        return f"Parameters({source}, parameters={self.nr_parameters})"
