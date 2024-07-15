from pathlib import Path
import re

def find_max_suffix(directory, file):
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
