"""
Common validation functions used throughout the visualization tool.
"""
import re
from typing import Any, Optional

def is_non_negative(value: Any) -> bool:
    """Validator for non-negative numbers (int or float). Returns False for None."""
    if value is None: return False
    return isinstance(value, (int, float)) and value >= 0

def is_positive(value: Any) -> bool:
    """Validator for positive numbers (int or float). Returns False for None."""
    if value is None: return False
    return isinstance(value, (int, float)) and value > 0

def is_valid_hex_color(value: Optional[str]) -> bool:
    """
    Validator for hex color strings (#RGB, #RRGGBB, #RRGGBBAA) or None.
    """
    if value is None:
        return True # None is often a valid optional value for color fields
    if not isinstance(value, str):
        return False
    # Regex for #RGB, #RRGGBB, #RRGGBBAA
    pattern = r'^#(?:[0-9a-fA-F]{3}|[0-9a-fA-F]{6}|[0-9a-fA-F]{8})$'
    return bool(re.match(pattern, value))

def is_between_0_and_1(value: Any) -> bool:
    """Validator for numbers between 0.0 and 1.0 inclusive. Returns False for None."""
    if value is None: return False
    if not isinstance(value, (int, float)): return False
    return 0.0 <= float(value) <= 1.0
