"""
Utilities for color manipulation.
"""
import logging
from .validators import is_valid_hex_color

logger = logging.getLogger(__name__)

def get_color_with_default_alpha(color_hex: str, alpha_hex: str = "80") -> str:
    """
    Adds a default alpha component to a hex color string if it doesn't have one.
    """
    if not is_valid_hex_color(color_hex): # Validator already checks for None implicitly if it's not allowed by its own logic
         logger.warning(f"Invalid base color format '{color_hex}' for alpha addition. Returning fallback #000000{alpha_hex}.")
         return f"#000000{alpha_hex}"

    color_hex_val = color_hex.lstrip('#')

    if len(color_hex_val) == 8: # RRGGBBAA (already has alpha)
        return f"#{color_hex_val}"
    elif len(color_hex_val) == 6: # RRGGBB
        return f"#{color_hex_val}{alpha_hex}"
    elif len(color_hex_val) == 3: # RGB -> RRGGBB
        r, g, b = color_hex_val[0], color_hex_val[1], color_hex_val[2]
        return f"#{r}{r}{g}{g}{b}{b}{alpha_hex}"
    else:
         # This case should ideally be caught by is_valid_hex_color
         logger.warning(f"Cannot add alpha to unexpected hex format: '{color_hex}'. Using fallback #000000{alpha_hex}.")
         return f"#000000{alpha_hex}"
