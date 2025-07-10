"""
Utility functions for interacting with schema definition dictionaries.
These are primarily for accessing schema properties like defaults or performing
basic validation checks based on a field's schema definition.
"""
from typing import Dict, Any, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from config_schema import ConfigField

def get_field_schema(schema: Dict[str, 'ConfigField'], field_name: str) -> Optional['ConfigField']:
    """Get the ConfigField object for a field name from a schema dictionary."""
    return schema.get(field_name)

def get_default_value(schema: Dict[str, 'ConfigField'], field_name: str) -> Any:
    """
    Get the default value for a field from a schema.
    Returns None if field doesn't exist, has no default, or is required.
    """
    field = get_field_schema(schema, field_name)
    return field.default if field and hasattr(field, 'default') and not field.required else None

def is_valid_value(schema: Dict[str, 'ConfigField'], field_name: str, value: Any) -> bool:
    """
    Check if a value is valid for a field according to its schema definition.
    Note: This provides a standalone way to check validity, similar to logic in ConfigLoader.
    """
    field = get_field_schema(schema, field_name)
    if not field:
        return False # Field not in schema

    # Type check
    is_correct_type = any(isinstance(value, t) for t in field.field_type if t is not type(None))
    if type(None) in field.field_type and value is None: # Explicitly allow None if in field_type
         is_correct_type = True
    if not is_correct_type:
        return False

    # Possible values check
    if field.possible_values is not None:
        is_in_possible = value in field.possible_values
        # Handle case where None is allowed by type but not explicitly in possible_values
        if not is_in_possible and value is None and type(None) in field.field_type:
             pass # This None is valid due to type allowance.
        elif not is_in_possible:
            return False

    # Custom validator check
    if field.validator:
        # Validators usually don't run on None unless designed to; assume None already passed type/possible_values check
        if value is None and type(None) in field.field_type:
             pass
        else:
             try:
                 if not field.validator(value):
                     return False
             except Exception: # Validator itself raised an error
                  return False
    return True
