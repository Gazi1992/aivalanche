# themes.py
import pyqtgraph as pg

DEFAULT_THEME_NAME = "Classic Light" # Or "Classic Light", or whichever you prefer as default

THEMES = {
    "Classic Light": {
        "background": 'w',  # White
        "foreground": 'k',  # Black
        "description": "Standard high-contrast light theme. Good for printing.",
        "data_colors": ['blue', 'red', 'green', 'purple', 'orange'] # Suggested data colors
    },
    "Classic Dark": {
        "background": 'k',  # Black
        "foreground": 'w',  # White (or try '#dddddd' for slightly softer white)
        "description": "Default PyQtGraph theme. High contrast, good for dark UI environments.",
        "data_colors": ['cyan', 'magenta', 'yellow', 'lime', '#FFA500'] # Bright colors work well
    },
    "Gray Background": {
        "background": '#f0f0f0', # Very light gray
        "foreground": '#333333', # Dark gray
        "description": "Softer than pure white, reduces eye strain.",
        "data_colors": ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd'] # Standard Matplotlib colors
    },
    "Blueprint": {
        "background": '#070B2A', # Dark Navy Blue
        "foreground": '#AAAAFF', # Light Blue/Lavender
        "description": "Technical drawing or CAD-like appearance.",
        "data_colors": ['cyan', 'yellow', 'white', '#FF8C00', 'lime']
    },
    "Solarized Light (Approx)": {
        "background": '#fdf6e3', # Creamy off-white (Base3)
        "foreground": '#657b83', # Muted Slate Gray (Base00)
        "description": "Approximation of the popular Solarized light color scheme.",
        "data_colors": ['#268bd2', '#dc322f', '#859900', '#6c71c4', '#d33682'] # Solarized accent colors
    },
    "Solarized Dark (Approx)": {
        "background": '#002b36', # Very dark desaturated cyan (Base03)
        "foreground": '#839496', # Muted cyan-gray (Base0)
        "description": "Approximation of the popular Solarized dark color scheme.",
        "data_colors": ['#268bd2', '#dc322f', '#859900', '#6c71c4', '#d33682'] # Solarized accent colors (same as light)
    },
    "Forest": {
        "background": '#E8F5E9', # Very light green
        "foreground": '#2E7D32', # Dark Green
        "description": "A nature-inspired green theme.",
        "data_colors": ['#FF6F00', '#4E342E', '#AD1457', '#0277BD', '#558B2F']
    }
    # Add more themes here if desired
}

def apply_theme(theme_name):
    """Applies a predefined PyQtGraph theme by setting global config options."""
    if theme_name in THEMES:
        theme = THEMES[theme_name]
        try:
            pg.setConfigOption('background', theme['background'])
            pg.setConfigOption('foreground', theme['foreground'])
            print(f"Applied theme: {theme_name}")
            return True # Indicate success
        except Exception as e:
            print(f"Error applying theme '{theme_name}': {e}")
            return False # Indicate failure
    else:
        print(f"Warning: Theme '{theme_name}' not found. Using default dark theme.")
        # Apply a fallback default theme
        try:
            pg.setConfigOption('background', 'k') # Default dark
            pg.setConfigOption('foreground', 'w')
            return False # Indicate theme not found, but default applied
        except Exception as e:
            print(f"Error applying default theme: {e}")
            return False # Indicate failure
