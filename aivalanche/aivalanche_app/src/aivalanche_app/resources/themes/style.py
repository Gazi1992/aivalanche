import importlib.util
from aivalanche_app.paths import theme_1_path

# Define constants
ALL_THEMES = {'theme_1': theme_1_path}
DEFAULT_THEME = 'theme_1'


class style():
    def __init__(self, active_theme: str = None):
        self.read_all_themes()      
        self.set_active_theme(active_theme)    
        
    def read_all_themes(self):
        self.all_themes = {}
        for theme in ALL_THEMES:
            self.all_themes[theme] = self.read_theme(theme)
        
    def read_theme(self, theme):
        # Load the module
        module_spec = importlib.util.spec_from_file_location('THEME', ALL_THEMES[theme])
        my_dict_module = importlib.util.module_from_spec(module_spec)
        module_spec.loader.exec_module(my_dict_module)
        
        # Access the dictionary
        my_dict = my_dict_module.THEME
        
        return my_dict
    
    def set_active_theme(self, active_theme: str = None):
        self.active_theme = active_theme if active_theme is not None else DEFAULT_THEME
        self.__dict__.update(self.all_themes[self.active_theme])
