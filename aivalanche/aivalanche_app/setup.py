from setuptools import setup, find_packages

setup(
    name = 'aivalanche_app',
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
        'PyQt6',
        ],
    python_requires='>=3.6',
)
