#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Oct 16 18:17:21 2024

@author: gazi
"""

import os
import shutil

def create_dummy_package(base_path):
    package_name = "dummy_package"
    package_path = os.path.join(base_path, package_name)
    
    # Create package directory
    os.makedirs(package_path, exist_ok=True)
    
    # Create src directory
    src_path = os.path.join(package_path, "src")
    os.makedirs(src_path, exist_ok=True)
    
    # Create package directory inside src
    package_src_path = os.path.join(src_path, package_name)
    os.makedirs(package_src_path, exist_ok=True)
    
    # Create __init__.py
    with open(os.path.join(package_src_path, "__init__.py"), "w") as f:
        f.write("from .main import hello_world\n")
    
    # Create main.py
    with open(os.path.join(package_src_path, "main.py"), "w") as f:
        f.write("def hello_world():\n    print('Hello from the dummy package!')\n")
    
    # Create setup.py
    setup_py_content = f"""
from setuptools import setup, find_packages

setup(
    name='{package_name}',
    version='0.1',
    packages=find_packages('src'),
    package_dir={{'': 'src'}},
    install_requires=[],
)
"""
    with open(os.path.join(package_path, "setup.py"), "w") as f:
        f.write(setup_py_content)
    
    print(f"Dummy package created at: {package_path}")

if __name__ == "__main__":
    base_path = os.path.expanduser("/home/gazi/Desktop/Work/custom_packages")
    create_dummy_package(base_path)