import numpy as np

def scale_parameter_row(row):
    """
    Scale a parameter row according to its transform type.

    Args:
        row (pd.Series): A row from the parameters DataFrame

    Returns:
        pd.Series: The transformed row with additional metadata
    """
    transform = row['transform']

    if transform == 'log': # Apply log10 transformation
        row['min'] = np.log10(row['min'])
        row['max'] = np.log10(row['max'])
        row['default'] = np.log10(row['default'])
    elif transform == 'neglog': # Apply -log10(-x) transformation
        row['min'] = -np.log10(-row['min'])
        row['max'] = -np.log10(-row['max'])
        row['default'] = -np.log10(-row['default'])

    return row

def determine_scale(min_val, max_val):
    """
    Determine the appropriate scale type for a parameter based on its min and max values.

    Args:
        min_val (float): Minimum value of the parameter
        max_val (float): Maximum value of the parameter

    Returns:
        str: Scale type ('lin' or 'log')
    """
    # Different signs
    if min_val * max_val < 0:
        return 'lin'
    # Same sign and ratio > 100
    elif min_val != 0 and max_val != 0 and abs(max_val / min_val) > 100:
        return 'log'
    # Default to linear
    else:
        return 'lin'

def determine_transform(row):
    """
    Determine the appropriate transform type for a parameter based on its scale and value range.

    Args:
        row (pd.Series): Row from parameters DataFrame containing 'scale', 'min', 'max'

    Returns:
        str or None: 'log' for positive log-scale, 'neglog' for negative log-scale,
                    None for linear or incompatible ranges
    """
    if row['scale'] == 'log':
        min_val = row['min']
        max_val = row['max']
        if min_val > 0 and max_val > 0:
            return 'log'
        elif min_val < 0 and max_val < 0:
            return 'neglog'
        else:
            # Mixed signs can't use log scale
            return None
    return None

def normalize_scale_value(scale_value):
    """
    Normalize scale value to standard format ('lin' or 'log').

    Args:
        scale_value (str): Scale value to normalize

    Returns:
        str: Normalized scale value ('lin' or 'log')
    """
    if isinstance(scale_value, str):
        if scale_value.lower() == 'linear':
            return 'lin'
        elif scale_value.lower() == 'logarithmic':
            return 'log'
        elif scale_value.lower() in ['lin', 'log']:
            return scale_value.lower()
    return None  # Invalid scale

def normalize_parameter_value(value, min_val, max_val):
    """
    Normalize a parameter value to the range [0, 1].

    Args:
        value (float): Value to normalize
        min_val (float): Minimum value of the parameter range
        max_val (float): Maximum value of the parameter range

    Returns:
        float: Normalized value between 0 and 1
    """
    if min_val == max_val:
        return 0.5  # Handle edge case where min equals max
    return (value - min_val) / (max_val - min_val)

def denormalize_parameter_value(norm_value, min_val, max_val):
    """
    Convert a normalized parameter value (0-1) back to its original range.

    Args:
        norm_value (float): Normalized value between 0 and 1
        min_val (float): Minimum value of the parameter range
        max_val (float): Maximum value of the parameter range

    Returns:
        float: Value in original range
    """
    return min_val + norm_value * (max_val - min_val)

def normalize_parameter_row(row):
    """
    Normalize a parameter row to the [0,1] range.

    Args:
        row (pd.Series): A row from the parameters DataFrame

    Returns:
        pd.Series: The normalized row with min_norm, max_norm, and default_norm values
    """
    # Normalize min, max, default to [0, 1] range
    # Since min and max define the range, they become 0 and 1
    min_val = row['min']
    max_val = row['max']

    # Normalize default to [0, 1]
    row['default'] = normalize_parameter_value(row['default'], min_val, max_val)

    # Standard normalized values
    row['min'] = 0.0
    row['max'] = 1.0

    return row
