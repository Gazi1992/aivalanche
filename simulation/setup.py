from setuptools import setup, find_packages
import os, pathlib

current_directory = os.path.dirname(__file__)                                   # __file__ is the current script's path
parent_directory = os.path.abspath(os.path.join(current_directory, os.pardir))  # Get the parent directory

setup(
    name = 'simulation',
    version = '1.0.0',
    author = 'Gazmend Alia',
    description = 'A short description of my package',
    long_description = 'A longer description of my package',
    long_description_content_type = 'text/markdown',
    url = 'https://github.com/yourusername/my_package',
    packages = find_packages('src'),
    package_dir = {'': 'src'},
    classifiers = [
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.10',
    ],
    install_requires = [
        'numpy',
        'pandas',
        f'testbench @ {pathlib.Path(os.path.join(parent_directory, "testbench")).as_uri()}',
        ],
    dependency_links=[
        'file://./testbench',
    ],
    python_requires='>=3.6',
)
