# utils/sample_data.py
import numpy as np

def get_line_data(n_points=100):
    """Generates simple x, y data for a line plot."""
    x = np.linspace(0, 10, n_points)
    y = np.sin(x) + np.random.normal(0, 0.2, n_points)
    return x, y

def get_scatter_data(n_points=100):
    """Generates simple x, y data for a scatter plot."""
    x = np.random.rand(n_points) * 10
    y = x + np.random.normal(0, 1, n_points)
    categories = np.random.randint(0, 3, n_points) # Example categorical data
    return x, y, categories

def get_histogram_data(n_points=1000):
    """Generates data suitable for a histogram."""
    data = np.random.normal(5, 2, n_points) # Mean 5, std dev 2
    return data
