from pathlib import Path
import re, json, pandas as pd
from PySide6.QtGui import QValidator

# Function to convert semicolumn to list of items when reading a csv
def convert_to_list_if_semi_colon(value):
    if isinstance(value, str) and ';' in value:
        return value.split(';')
    return value

# Function to replace the whitespaces with underlines
def replace_space_with_underline(string: str = ''):
    return string.replace(' ', '_')

# Filter a dataframe by col_name and value
def filter_df_by_col_name_and_val(df: pd.DataFrame, col_name: str, val: object, single: bool = True):
    filtered = df[df[col_name] == val]
    if len(filtered.index) > 0 and single:
        filtered = filtered.iloc[0, :]
    return filtered

def find_max_suffix(directory: str = None, file: str = None):
    # Convert to a Path object
    dir_path = Path(directory)
    
    prefix = Path(file).stem
    extension = Path(file).suffix
    
    # Filter files that start with the given prefix and have the specified file extension
    matching_files = [
        f for f in dir_path.iterdir() 
        if f.is_file() and f.name.startswith(prefix) and f.suffix == extension
    ]
    
    # Extract suffixes using regex
    suffixes = []
    for f in matching_files:
        match = re.search(rf'{prefix}(_\d+){re.escape(extension)}', f.name)
        if match:
            suffix = match.group(1)  # Extract the suffix (e.g., _1, _2, _4)
            suffixes.append(suffix)
    
    if not suffixes:
        return Path.joinpath(directory, f"{prefix}_1{extension}")
    
    # Convert suffixes to integers and find the maximum
    max_suffix = max(int(suffix[1:]) for suffix in suffixes)  # Remove the underscore and convert to int
    
    # Create the new suffix by adding 1 to the maximum suffix
    new_suffix = max_suffix + 1
    return Path.joinpath(directory, f"{prefix}_{new_suffix}{extension}")

def dict_to_json(data: dict = None, file_path: str = None):
    if data is None or file_path is None:
        print('Error at dict_to_json. Data and path should not be None!')
        return
    
    with open(file_path, 'w') as json_file:
        json.dump(data, json_file, indent = 4)

class positive_number_validator(QValidator):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.last_valid_value = ''  # To store the last valid value

    def validate(self, input_str, pos):
        if input_str == '':
            return QValidator.Intermediate, input_str, pos
        
        try:
            value = float(input_str)
            if value > 0:
                self.last_valid_value = input_str  # Update the last valid value
                return QValidator.Acceptable, input_str, pos
            else:
                return QValidator.Invalid, input_str, pos
        except ValueError:
            return QValidator.Invalid, input_str, pos

    def fixup(self, input_str):
        # Reset to the last valid value
        return self.last_valid_value
    
class positive_integer_validator(QValidator):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.last_valid_value = ''  # To store the last valid value

    def validate(self, input_str, pos):
        if input_str == '':
            return QValidator.Intermediate, input_str, pos
        
        try:
            value = int(input_str)
            if value > 0:
                self.last_valid_value = input_str  # Update the last valid value
                return QValidator.Acceptable, input_str, pos
            else:
                return QValidator.Invalid, input_str, pos
        except ValueError:
            return QValidator.Invalid, input_str, pos

    def fixup(self, input_str):
        # Reset to the last valid value
        return self.last_valid_value
    
class number_validator(QValidator):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.last_valid_value = ''  # To store the last valid value

    def validate(self, input_str, pos):
        if input_str == '':
            return QValidator.Intermediate, input_str, pos
        
        try:
            value = float(input_str)
            self.last_valid_value = input_str  # Update the last valid value
            return QValidator.Acceptable, input_str, pos
        except ValueError:
            return QValidator.Invalid, input_str, pos

    def fixup(self, input_str):
        # Reset to the last valid value
        return self.last_valid_value