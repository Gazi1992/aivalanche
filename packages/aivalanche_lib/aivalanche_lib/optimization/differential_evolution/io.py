"""
Input/Output operations for the DifferentialEvolution class.

This module contains functions for:
- Writing optimization history to files
- Writing optimization information to files
- Reading and writing population data
"""

import numpy as np, pandas as pd, json

def write_history_to_file(de_instance, which='trials', file_path=None):
    """
    Write optimization history to a file (CSV or JSON).

    Args:
        de_instance: Instance of DifferentialEvolution
        which (str): Which history data to export:
                     'trials', 'trials_normed', 'survivors', 'survivors_normed',
                     'bests', 'bests_normed', 'boundaries', 'boundaries_normed'
        file_path (str): Path to the output file.
                          The file extension (.csv or .json) determines the output format.

    Returns:
        None

    Raises:
        ValueError: If file_path is None, if which is not a valid option,
                   or if the file extension is not supported.
    """
    if file_path is None:
        raise ValueError('Please provide a file_path!')

    # Validate 'which' parameter
    valid_options = [
        'trials', 'trials_normed', 'survivors', 'survivors_normed',
        'bests', 'bests_normed', 'boundaries', 'boundaries_normed'
    ]

    if which not in valid_options:
        raise ValueError(f"Invalid 'which' parameter: {which}. "
                         f"Must be one of: {', '.join(valid_options)}")

    # Get history data
    history_data = de_instance.history

    # Select appropriate data based on 'which' parameter
    if which in ['boundaries', 'boundaries_normed']:
        if which == 'boundaries':
            data = history_data.get('boundaries')
        else:  # 'boundaries_normed'
            data = history_data.get('boundaries_normed')
    else:
        data = history_data.get(which)

    if data is None or data.empty:
        print(f"No {which} data available to write.")
        return

    # Determine file format from extension
    ext = file_path.lower().split('.')[-1]

    if ext == 'csv':
        # For boundaries data (which has MultiIndex), we need to reset the index
        if which in ['boundaries', 'boundaries_normed']:
            # Reset MultiIndex to convert to columns
            data = data.reset_index()

        # Write to CSV
        data.to_csv(file_path, index=False)
        print(f"{which} data written to {file_path}")

    elif ext == 'json':
        if which in ['boundaries', 'boundaries_normed']:
            # For MultiIndex DataFrames, we need to handle them differently for JSON
            # First reset the index to convert to columns
            json_data = data.reset_index()
            json_data.to_json(file_path, orient='records', indent=4)
        else:
            # Regular DataFrames can be written directly
            data.to_json(file_path, orient='records', indent=4)

        print(f"{which} data written to {file_path}")

    else:
        raise ValueError(f"Unsupported file extension: .{ext}. Use .csv or .json")

def write_optimization_info_to_file(de_instance, file_path=None):
    """
    Write optimization information to a JSON file.

    Args:
        de_instance: Instance of DifferentialEvolution
        file_path (str): Path to the output file.
                        If the extension is not .json, it will be added automatically.

    Returns:
        None

    Raises:
        ValueError: If file_path is None.
    """
    if file_path is None:
        raise ValueError('Please provide a file_path!')

    # Ensure the file has .json extension
    if not file_path.lower().endswith('.json'):
        file_path += '.json'

    # Get optimization info
    info = de_instance.optimization_info

    # JSON serialization helper for numpy types and other non-serializable objects
    def json_serialize(obj):
        if isinstance(obj, (np.int_, np.intc, np.intp, np.int8, np.int16, np.int32, np.int64,
                           np.uint8, np.uint16, np.uint32, np.uint64)):
            return int(obj)
        elif isinstance(obj, (np.float_, np.float16, np.float32, np.float64)):
            return float(obj)
        elif isinstance(obj, (np.bool_)):
            return bool(obj)
        elif isinstance(obj, (np.ndarray,)):
            return obj.tolist()
        elif isinstance(obj, (tuple, list)):
            return [json_serialize(item) for item in obj]
        elif isinstance(obj, dict):
            return {key: json_serialize(value) for key, value in obj.items()}
        elif obj is None:
            return None
        elif hasattr(obj, 'to_dict'):
            # For pandas Series/DataFrame
            return json_serialize(obj.to_dict())
        else:
            # Try to make it a string, if all else fails
            try:
                return str(obj)
            except:
                return "UNSERIALIZABLE OBJECT"

    # Write to JSON with custom serialization
    with open(file_path, 'w') as f:
        json.dump(json_serialize(info), f, indent=4)

    print(f"Optimization info written to {file_path}")

def write_best_parameters_to_file(de_instance, file_path=None):
    """
    Write best parameters to a file (CSV or JSON).

    Args:
        de_instance: Instance of DifferentialEvolution
        file_path (str): Path to the output file. If None, raises ValueError
                        The file extension (.csv or .json) determines the output format.

    Raises:
        ValueError: If file_path is None
    """
    if file_path is None:
        raise ValueError('Please provide a file_path!')

    best_parameters = de_instance.best_parameters
    best_parameters.name = 'value'
    best_parameters.index.name = 'param'

    # Write to file based on extension
    ext = file_path.lower().split('.')[-1]

    if ext == 'csv':
        best_parameters.to_csv(file_path)
        print(f"Best parameters written to {file_path}")
    elif ext == 'json':
        best_parameters.to_json(file_path, indent=4)
        print(f"Best parameters written to {file_path}")
    else:
        raise ValueError(f"Unsupported file extension: .{ext}. Use .csv or .json")

def write_current_population_to_file(de_instance, file_path=None):
    """
    Write current population to a file (CSV or JSON).

    Args:
        de_instance: Instance of DifferentialEvolution
        file_path (str): Path to the output file. If None, raises ValueError
                        The file extension (.csv or .json) determines the output format.

    Raises:
        ValueError: If file_path is None
    """
    if file_path is None:
        raise ValueError('Please provide a file_path!')

    # Write to file based on extension
    ext = file_path.lower().split('.')[-1]

    if ext == 'csv':
        de_instance.current_parameters.to_csv(file_path, index=False)
        print(f"Current population written to {file_path}")
    elif ext == 'json':
        de_instance.current_parameters.to_json(file_path, orient='records', indent=4)
        print(f"Current population written to {file_path}")
    else:
        raise ValueError(f"Unsupported file extension: .{ext}. Use .csv or .json")

def read_population_from_file(file_path):
    """
    Read population data from a file (CSV or JSON).

    Args:
        file_path (str): Path to the input file.
                        The file extension (.csv or .json) determines the format.

    Returns:
        pandas.DataFrame: DataFrame containing the population data

    Raises:
        ValueError: If the file extension is not supported.
        FileNotFoundError: If the file does not exist.
    """
    # Determine file format from extension
    ext = file_path.lower().split('.')[-1]

    if ext == 'csv':
        return pd.read_csv(file_path)
    elif ext == 'json':
        return pd.read_json(file_path)
    else:
        raise ValueError(f"Unsupported file extension: .{ext}. Use .csv or .json")
