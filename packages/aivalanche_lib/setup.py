from setuptools import setup, find_packages

setup(
    name="aivalanche_lib",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "numpy",
        "pandas",
        "scikit-learn",
        "matplotlib",
        "GPy",
        "scipy",
        "pyDOE"
    ],
    author="Gazmend Alia",
    author_email="gazmendalia@aivalanche.de",
    description="A Python library for AI and optimization algorithms",
    keywords="optimization, differential evolution, gaussian process",
    url="https://github.com/yourusername/aivalanche_lib",
)
