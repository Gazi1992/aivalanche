# --- START OF FILE io.py ---

import pandas as pd
import json
import os
import logging
from typing import Dict, List, Any, Tuple, Optional # Adjusted imports

logger = logging.getLogger(__name__) # Logger for io operations

# --- File/Data Loading Utilities ---

def parse_json(file_path: str) -> Tuple[Optional[pd.DataFrame], Optional[str]]:
    """
    Parse a JSON file containing parameter definitions.

    Accepts a list of parameter objects or a dictionary where keys are
    parameter names and values are parameter objects.

    Args:
        file_path (str): Path to the JSON file.

    Returns:
        Tuple[Optional[pd.DataFrame], Optional[str]]:
            A tuple containing the DataFrame of parameters if successful,
            otherwise None, and an error message string if unsuccessful,
            otherwise None.
    """
    if not os.path.exists(file_path):
        return None, f"JSON file not found: '{file_path}'"
    try:
        with open(file_path, 'r', encoding='utf-8') as json_file:
            data = json.load(json_file)

        df = None
        if isinstance(data, list):
            df = pd.DataFrame(data) if data else pd.DataFrame()
        elif isinstance(data, dict):
            param_list = []
            for name, values in data.items():
                if isinstance(values, dict):
                    values['name'] = name  # Add the key as the 'name' field
                    param_list.append(values)
                else:
                    logger.warning(f"Skipping non-dictionary item '{name}' in JSON dict structure.")
            df = pd.DataFrame(param_list) if param_list else pd.DataFrame()
        else:
            raise ValueError("JSON root must be a list of parameter objects or a dict of parameter objects.")

        # Ensure 'name' column exists, even if DataFrame is empty
        if df.empty:
            if 'name' not in df.columns:
                 df['name'] = pd.Series(dtype='object')
        elif 'name' not in df.columns:
             # If not empty but name is missing, it's an error from the structure check above
             # This case might be redundant due to checks inside dict/list processing
             raise ValueError("Parsed JSON data is missing the required 'name' column.")

        return df, None
    except json.JSONDecodeError as e:
        return None, f"Invalid JSON format in '{file_path}': {str(e)}"
    except ValueError as e:
        return None, f"Invalid data structure or content in JSON file '{file_path}': {str(e)}"
    except Exception as e:
        logger.error(f"Unexpected error reading JSON '{file_path}': {e}", exc_info=True)
        return None, f"Error reading or processing JSON '{file_path}': {str(e)}"


def parse_csv(file_path: str) -> Tuple[Optional[pd.DataFrame], Optional[str]]:
    """
    Parse a CSV file containing parameter definitions.

    Special handling for the 'values' column to interpret lists (JSON format,
    semicolon-separated, or single value). Handles basic type conversions.

    Args:
        file_path (str): Path to the CSV file.

    Returns:
        Tuple[Optional[pd.DataFrame], Optional[str]]:
            A tuple containing the DataFrame of parameters if successful,
            otherwise None, and an error message string if unsuccessful,
            otherwise None.
    """
    if not os.path.exists(file_path):
        return None, f"CSV file not found: '{file_path}'"

    def try_convert_item(item_str):
        """Helper to convert strings from CSV to Python types."""
        if not isinstance(item_str, str): # Handle non-string inputs directly if they occur
             return item_str
        item_str = item_str.strip()
        if item_str.lower() == 'true': return True
        if item_str.lower() == 'false': return False
        # Explicitly check for various NA strings
        na_strings = ['none', 'na', 'nan', '<na>', '', '#n/a', '<n/a>', 'null', 'nil'] # Added common NAs
        if item_str.lower() in na_strings: return None
        try: return int(item_str)
        except ValueError:
            try: return float(item_str)
            except ValueError: return item_str # Return as string if no conversion works

    def parse_list_string(x):
        """Converter for the 'values' column in CSV."""
        if pd.isna(x): return None # Handle pandas NA representation
        if isinstance(x, list): return x # Already a list (unlikely from read_csv but safe)

        # Convert input to string for consistent processing
        if not isinstance(x, str):
            try: x_str = str(x)
            except Exception: return x # Return original if cannot convert to string

        else: x_str = x

        x_strip = x_str.strip()
        if not x_strip: return [] # Empty string becomes empty list

        # Try parsing as JSON list first
        if (x_strip.startswith('[') and x_strip.endswith(']')):
            try:
                parsed_content = json.loads(x_strip)
                if isinstance(parsed_content, list):
                    # Apply type conversion to items within the parsed list
                    return [try_convert_item(str(item)) if not isinstance(item, (bool, int, float, type(None))) else item for item in parsed_content]
                else:
                    # Parsed as JSON but not a list - treat as single item list? Or error?
                    logger.warning(f"CSV 'values' field parsed as JSON but is not a list: '{x_strip}'. Treating as single element list.")
                    single_item = try_convert_item(str(parsed_content))
                    return [single_item]
            except json.JSONDecodeError:
                # Failed JSON parsing, fall through to other methods
                logger.debug(f"Could not parse '{x_strip}' as JSON list, trying other separators.")
                pass # Fall through to semicolon or single value

        # Try semicolon separation
        if ';' in x_strip:
            return [try_convert_item(item) for item in [part.strip() for part in x_strip.split(';')]]

        # Treat as a single value, potentially including NA conversion
        single_item = try_convert_item(x_strip)
        # If conversion resulted in None due to an NA string, return None (not list containing None)
        na_strings = ['none', 'na', 'nan', '<na>', '', '#n/a', '<n/a>', 'null', 'nil']
        if single_item is None and x_strip.lower() in na_strings:
            return None
        else:
            # Otherwise, wrap the single converted item in a list
            return [single_item]


    try:
        converters = {'values': parse_list_string}
        # Define NA values recognized by pandas during read_csv
        na_values = ['NA', 'NaN', 'None', '', '#N/A', '<N/A>', 'null', 'Null', 'none', 'na', 'nan', 'nil']
        df = pd.read_csv(
            filepath_or_buffer=file_path,
            comment='#',
            converters=converters,
            skipinitialspace=True,
            na_values=na_values,
            keep_default_na=True # Important to use with na_values
        )

        if 'name' not in df.columns:
            raise ValueError("Parsed CSV data is missing the required 'name' column.")
        # Ensure 'values' column exists, even if all were NaN
        if 'values' not in df.columns:
             df['values'] = None # Add as None initially

        # Ensure 'values' column is object type to hold lists/None
        df['values'] = df['values'].astype(object)

        return df, None
    except ValueError as e:
        return None, f"Invalid data or structure in CSV '{file_path}': {e}"
    except FileNotFoundError: # Should be caught by os.path.exists, but safeguard
        return None, f"CSV file not found: '{file_path}'"
    except Exception as e:
        logger.error(f"Error parsing CSV '{file_path}': {str(e)}", exc_info=True)
        return None, f"Error parsing CSV '{file_path}': {str(e)}"


def load_dataframe(df: pd.DataFrame) -> Tuple[Optional[pd.DataFrame], Optional[str]]:
    """
    Loads parameters from a pandas DataFrame. Performs basic validation.

    Args:
        df (pd.DataFrame): Input DataFrame.

    Returns:
        Tuple[Optional[pd.DataFrame], Optional[str]]:
            A tuple containing a copy of the DataFrame if valid,
            otherwise None, and an error message string if invalid,
            otherwise None.
    """
    if not isinstance(df, pd.DataFrame):
        return None, "Input is not a pandas DataFrame."

    df_copy = df.copy() # Work on a copy

    if 'name' not in df_copy.columns:
        if df_copy.index.name == 'name':
            df_copy = df_copy.reset_index() # Promote index 'name' to column
        else:
            return None, "DataFrame missing required column: 'name'."

    # Basic check complete, further validation happens later
    return df_copy, None


def load_dict_list(dict_list: List[Dict[str, Any]]) -> Tuple[Optional[pd.DataFrame], Optional[str]]:
    """
    Loads parameters from a list of dictionaries. Performs basic validation.

    Args:
        dict_list (List[Dict[str, Any]]): List of parameter dictionaries.

    Returns:
        Tuple[Optional[pd.DataFrame], Optional[str]]:
            A tuple containing the DataFrame if valid,
            otherwise None, and an error message string if invalid,
            otherwise None.
    """
    if not isinstance(dict_list, list):
        return None, "Input is not a list."

    if not dict_list:
        logger.info("Input dictionary list is empty. Returning empty DataFrame.")
        # Return empty DataFrame with 'name' column to meet downstream expectations
        return pd.DataFrame(columns=['name']), None

    if not all(isinstance(d, dict) for d in dict_list):
            bad_indices = [i for i, d in enumerate(dict_list) if not isinstance(d, dict)]
            return None, f"Items at indices {bad_indices} are not dictionaries."

    # Check for 'name' key in all dictionaries
    missing_indices = [i for i, d in enumerate(dict_list) if 'name' not in d]
    if missing_indices:
            example_missing = dict_list[missing_indices[0]] if missing_indices else {}
            return None, f"Dictionaries at indices {missing_indices} missing required key: 'name'. Example: {example_missing}"

    try:
        df = pd.DataFrame(dict_list)
        # Double check 'name' column exists after DataFrame creation
        if 'name' not in df.columns:
            # This case shouldn't happen if the check above worked, but safety first
            return None, "Failed to create DataFrame with 'name' column from dictionary list."
        return df, None
    except Exception as e:
        logger.error(f"Error creating DataFrame from dictionary list: {e}", exc_info=True)
        return None, f"Error creating DataFrame from dictionary list: {str(e)}"

# --- END OF FILE io.py ---
