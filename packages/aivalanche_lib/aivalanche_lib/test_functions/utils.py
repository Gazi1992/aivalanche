"""
Utility functions for the optimization_test_functions package.
"""

from typing import List, Dict, Any

def generate_parameters_config(details: dict) -> List[Dict[str, Any]]:
    """
    Generates a parameter configuration list suitable for aivalanche_lib.Parameters.

    Args:
        details (dict): The dictionary containing function details
                        (obtained from get_function_details).

    Returns:
        List[Dict[str, Any]]: A list of parameter definition dictionaries.
    """
    config = []
    dim = details['dim']
    bounds = details['bounds'] # Should be resolved to list of tuples by get_function_details

    if not isinstance(dim, int) or dim <= 0:
        raise ValueError(f"Cannot generate config: Invalid dimension '{dim}' in details.")

    if len(bounds) != dim:
         raise ValueError(f"Dimension mismatch: details['dim']={dim} but "
                          f"len(details['bounds'])={len(bounds)}.")

    for i in range(dim):
        param_name = f"x{i+1}" # Naming convention x1, x2, ...
        min_val, max_val = bounds[i]
        config.append({
            "name": param_name,
            "min": min_val,
            "max": max_val,
            "default": (min_val + max_val) / 2.0, # Default to midpoint
            "scale": "lin", # Assume linear scale unless specified otherwise
            "mode": "variable"
        })
    return config
