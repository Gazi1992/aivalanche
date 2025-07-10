"""
Definitions of common optimization test functions.

Each function entry includes:
- func: The callable function implementation (accepts a numpy array).
- dim: The dimensionality (int or 'nD').
- bounds: Suggested bounds for each dimension as a list of tuples [(min, max), ...]
          or a single tuple (min, max) for nD functions (applied to all dimensions).
- optimum_loc: The known location(s) of the global optimum (as a numpy array or list of arrays).
- optimum_val: The value of the function at the global optimum.
- plot_bounds: Optional tighter bounds specifically useful for informative plotting.
"""

import numpy as np

# ----------------------------------------------------------------------------
# Function Implementations
# ----------------------------------------------------------------------------

# --- 1D Functions ---

def parabola_1d(x: np.ndarray) -> float:
    """Simple quadratic function: f(x) = x^2"""
    return x[0]**2

def sine_1d(x: np.ndarray) -> float:
    """Simple sine wave: f(x) = sin(x)"""
    # Shifted slightly to have minimum != maximum within typical bounds
    return np.sin(x[0] + 0.1)

# --- 2D Functions ---

def sphere_2d(x: np.ndarray) -> float:
    """Simple sphere function: f(x, y) = x^2 + y^2"""
    return np.sum(x**2)

def rosenbrock_2d(x: np.ndarray) -> float:
    """Rosenbrock's banana function: f(x,y) = (1-x)^2 + 100*(y-x^2)^2"""
    return (1 - x[0])**2 + 100 * (x[1] - x[0]**2)**2

def himmelblau_2d(x: np.ndarray) -> float:
    """Himmelblau's function: f(x,y) = (x^2+y-11)^2 + (x+y^2-7)^2"""
    term1 = (x[0]**2 + x[1] - 11)**2
    term2 = (x[0] + x[1]**2 - 7)**2
    return term1 + term2

def beale_2d(x: np.ndarray) -> float:
    """Beale function: f(x,y) = (1.5 - x + xy)^2 + (2.25 - x + xy^2)^2 + (2.625 - x + xy^3)^2"""
    term1 = (1.5 - x[0] + x[0] * x[1])**2
    term2 = (2.25 - x[0] + x[0] * x[1]**2)**2
    term3 = (2.625 - x[0] + x[0] * x[1]**3)**2
    return term1 + term2 + term3

# --- 3D Functions ---

def sphere_3d(x: np.ndarray) -> float:
    """Simple sphere function in 3D: f(x, y, z) = x^2 + y^2 + z^2"""
    return np.sum(x**2)

# --- nD Functions ---

def sphere_nd(x: np.ndarray) -> float:
    """Simple n-dimensional sphere function."""
    return np.sum(x**2)

def ackley_nd(x: np.ndarray) -> float:
    """Ackley function - highly multimodal."""
    n = len(x)
    a = 20
    b = 0.2
    c = 2 * np.pi
    sum1 = np.sum(x**2)
    sum2 = np.sum(np.cos(c * x))
    term1 = -a * np.exp(-b * np.sqrt(sum1 / n))
    term2 = -np.exp(sum2 / n)
    return term1 + term2 + a + np.exp(1)

def rastrigin_nd(x: np.ndarray) -> float:
    """Rastrigin function - highly multimodal with regular pattern."""
    n = len(x)
    return 10 * n + np.sum(x**2 - 10 * np.cos(2 * np.pi * x))

def griewank_nd(x: np.ndarray) -> float:
    """Griewank function - multimodal, product coupling term."""
    n = len(x)
    sum_term = np.sum(x**2 / 4000)
    prod_term = np.prod(np.cos(x / np.sqrt(np.arange(1, n + 1))))
    return sum_term - prod_term + 1

# ----------------------------------------------------------------------------
# Function Metadata Dictionary
# ----------------------------------------------------------------------------

# Use lowercase names for keys for consistency
ALL_FUNCTIONS = {
    # --- 1D ---
    "parabola_1d": {
        "func": parabola_1d,
        "dim": 1,
        "bounds": [(-5.0, 5.0)],
        "optimum_loc": np.array([0.0]),
        "optimum_val": 0.0,
    },
    "sine_1d": {
        "func": sine_1d,
        "dim": 1,
        "bounds": [(-np.pi, np.pi)],
        "optimum_loc": np.array([(-np.pi/2) - 0.1]), # approx location of min
        "optimum_val": -1.0,
    },
    # --- 2D ---
    "sphere_2d": {
        "func": sphere_2d,
        "dim": 2,
        "bounds": [(-5.12, 5.12), (-5.12, 5.12)],
        "optimum_loc": np.array([0.0, 0.0]),
        "optimum_val": 0.0,
    },
    "rosenbrock_2d": {
        "func": rosenbrock_2d,
        "dim": 2,
        "bounds": [(-2.0, 2.0), (-1.0, 3.0)], # Classic bounds
        "optimum_loc": np.array([1.0, 1.0]),
        "optimum_val": 0.0,
        "plot_bounds": [(-2.0, 2.0), (-1.0, 3.0)]
    },
     "himmelblau_2d": {
        "func": himmelblau_2d,
        "dim": 2,
        "bounds": [(-5.0, 5.0), (-5.0, 5.0)],
        "optimum_loc": [ # Four distinct minima
            np.array([3.0, 2.0]),
            np.array([-2.805118, 3.131312]),
            np.array([-3.779310, -3.283186]),
            np.array([3.584428, -1.848126])
        ],
        "optimum_val": 0.0,
    },
    "beale_2d": {
        "func": beale_2d,
        "dim": 2,
        "bounds": [(-4.5, 4.5), (-4.5, 4.5)],
        "optimum_loc": np.array([3.0, 0.5]),
        "optimum_val": 0.0,
    },
    # --- 3D ---
     "sphere_3d": {
        "func": sphere_3d,
        "dim": 3,
        "bounds": [(-5.12, 5.12)] * 3, # Apply same bounds to all dims
        "optimum_loc": np.array([0.0, 0.0, 0.0]),
        "optimum_val": 0.0,
    },
    # --- nD ---
    # Note: For nD, 'bounds' usually represents the bounds for *each* dimension.
    # 'optimum_loc' is generated based on the specified dimension during use.
    "sphere_nd": {
        "func": sphere_nd,
        "dim": 'nD', # Indicates dimension needs to be specified
        "bounds": (-5.12, 5.12), # Bounds for each dimension
        # Optimum location depends on n, generated on the fly
        "optimum_val": 0.0,
    },
    "ackley_nd": {
        "func": ackley_nd,
        "dim": 'nD',
        "bounds": (-32.768, 32.768),
        "optimum_val": 0.0,
    },
    "rastrigin_nd": {
        "func": rastrigin_nd,
        "dim": 'nD',
        "bounds": (-5.12, 5.12),
        "optimum_val": 0.0,
    },
     "griewank_nd": {
        "func": griewank_nd,
        "dim": 'nD',
        "bounds": (-600.0, 600.0),
        "optimum_val": 0.0,
    },
    # Add more functions here (e.g., Schwefel, Levy, etc.)
}

# ----------------------------------------------------------------------------
# Helper Function to Get Details
# ----------------------------------------------------------------------------

def get_function_details(name: str, n_dim: int = None) -> dict:
    """
    Retrieves the details for a given test function.

    Args:
        name (str): The name (key) of the function in ALL_FUNCTIONS.
        n_dim (int, optional): The desired dimension for 'nD' functions.
                               Required if the function's dim is 'nD'.

    Returns:
        dict: A copy of the function's detail dictionary, with 'nD' specific
              fields potentially resolved (like optimum_loc and bounds list).

    Raises:
        KeyError: If the function name is not found.
        ValueError: If 'nD' function is requested without specifying n_dim,
                    or if a fixed-dimension function is called with n_dim.
    """
    name_lower = name.lower()
    if name_lower not in ALL_FUNCTIONS:
        raise KeyError(f"Test function '{name}' not found in definitions. "
                       f"Available functions: {list(ALL_FUNCTIONS.keys())}")

    details = ALL_FUNCTIONS[name_lower].copy() # Return a copy

    if details['dim'] == 'nD':
        if n_dim is None or not isinstance(n_dim, int) or n_dim <= 0:
            raise ValueError(f"Function '{name}' is n-dimensional ('nD'). "
                             f"Please provide a positive integer 'n_dim'.")
        # Resolve nD specific fields
        details['dim'] = n_dim
        # Generate bounds list
        details['bounds'] = [details['bounds']] * n_dim
        # Generate optimum location (typically all zeros for these functions)
        details['optimum_loc'] = np.zeros(n_dim)
    elif n_dim is not None:
         print(f"Warning: Function '{name}' has a fixed dimension of {details['dim']}. "
               f"Ignoring provided 'n_dim={n_dim}'.")

    return details
