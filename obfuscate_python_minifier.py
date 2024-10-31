#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Oct 15 12:21:07 2024

@author: gazi
"""

import os, re, shutil
from python_minifier import minify

def update_setup_py(file_path, obfuscated_name):
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Update package name
    content = re.sub(r'name="[^"]*"', f'name="{obfuscated_name}"', content)
    
    # Update version
    content = re.sub(r'version="[^"]*"', 'version="0.1.0-obf"', content)
    
    with open(file_path, 'w') as f:
        f.write(content)

def update_readme_md(file_path):
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Add note about obfuscated version
    obfuscation_note = "# Obfuscated Version\n\nThis is an obfuscated version of the original package.\n\n"
    content = obfuscation_note + content
    
    with open(file_path, 'w') as f:
        f.write(content)

def update_init_py(file_path):
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Update version string
    content = re.sub(r'__version__\s*=\s*"[^"]*"', '__version__ = "0.1.0-obf"', content)
    
    with open(file_path, 'w') as f:
        f.write(content)

def obfuscate_package(source_dir, dest_dir):
    # Get the base name of the source directory to use as the obfuscated package name
    original_name = os.path.basename(source_dir)
    obfuscated_name = f"{original_name}_obfuscated"

    # Create the destination directory if it doesn't exist
    os.makedirs(dest_dir, exist_ok=True)

    for root, dirs, files in os.walk(source_dir):
        # Create corresponding subdirectories in the destination
        for dir in dirs:
            src_path = os.path.join(root, dir)
            rel_path = os.path.relpath(src_path, source_dir)
            dest_path = os.path.join(dest_dir, rel_path)
            os.makedirs(dest_path, exist_ok=True)

        # Process files
        for file in files:
            src_path = os.path.join(root, file)
            rel_path = os.path.relpath(src_path, source_dir)
            dest_path = os.path.join(dest_dir, rel_path)

            # If it's a Python file (excluding setup.py), minify it
            if file.endswith('.py') and file != 'setup.py':
                with open(src_path, 'r') as f:
                    content = f.read()
                minified = minify(content)
                with open(dest_path, 'w') as f:
                    f.write(minified)
            else:
                # For non-Python files and setup.py, just copy them
                shutil.copy2(src_path, dest_path)

            # Perform specific updates on certain files
            if file == 'setup.py':
                update_setup_py(dest_path, obfuscated_name)
            elif file == 'README.md':
                update_readme_md(dest_path)
            elif file == '__init__.py':
                update_init_py(dest_path)

    print(f"Obfuscated package created at: {dest_dir}")

if __name__ == "__main__":
    source_package = "/home/gazi/Desktop/Work/custom_packages/optimization"
    obfuscated_package = "/home/gazi/Desktop/Work/custom_packages/optimization_obf"
    obfuscate_package(source_package, obfuscated_package)