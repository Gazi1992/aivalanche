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

def griewank_2d(x: np.ndarray) -> float:
    """Griewank function in 2D: multimodal with product coupling term."""
    sum_term = (x[0]**2 + x[1]**2) / 4000
    prod_term = np.cos(x[0]) * np.cos(x[1] / np.sqrt(2))
    return sum_term - prod_term + 1

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

# --- Discrete Functions ---

def discrete_rastrigin_2d(x: np.ndarray, step_size: float = 1.0) -> float:
    """Discrete version of Rastrigin function - values discretized to multiples of step_size."""
    x_discrete = np.round(x / step_size) * step_size
    return 10 * 2 + np.sum(x_discrete**2 - 10 * np.cos(2 * np.pi * x_discrete))

def step_function_2d(x: np.ndarray, n_steps: int = 5) -> float:
    """Step function with discrete plateaus - creates n_steps x n_steps discrete regions."""
    # Create step boundaries
    bounds = 5.0  # Assuming [-5, 5] range
    step_edges = np.linspace(-bounds, bounds, n_steps + 1)
    
    # Find which step region each coordinate belongs to
    x_idx = np.digitize(x[0], step_edges) - 1
    y_idx = np.digitize(x[1], step_edges) - 1
    
    # Clamp to valid range
    x_idx = np.clip(x_idx, 0, n_steps - 1)
    y_idx = np.clip(y_idx, 0, n_steps - 1)
    
    # Calculate step value based on Manhattan distance from center
    center_idx = n_steps // 2
    distance = abs(x_idx - center_idx) + abs(y_idx - center_idx)
    
    return distance * 10.0

def integer_quadratic_2d(x: np.ndarray) -> float:
    """Quadratic function with integer constraints - rounds inputs to nearest integers."""
    x_int = np.round(x)
    return (x_int[0] - 3)**2 + 2*(x_int[1] + 2)**2 + 0.5*np.abs(x_int[0]*x_int[1])

def discrete_sphere_nd(x: np.ndarray, resolution: float = 0.5) -> float:
    """Sphere function with discrete values - rounds to nearest multiple of resolution."""
    x_discrete = np.round(x / resolution) * resolution
    return np.sum(x_discrete**2)

# --- Categorical/Mixed Functions ---

def string_categorical_mixed_2d(x: np.ndarray) -> float:
    """
    Mixed function with continuous x and categorical y.
    x: continuous variable
    y: categorical variable that should be one of ['a', 'b', 'c']
    
    The function expects y to be passed as a string or convertible to string.
    """
    # Extract values - handle both numeric and object arrays
    x_val = float(x[0])
    # Handle y as categorical
    y_cat = str(x[1]) if not isinstance(x[1], str) else x[1]
    
    # Define values for each category
    category_values = {
        'a': 1.0,
        'b': 0.5,
        'c': 2.0
    }
    
    # Get category multiplier, default to 10 if unknown category
    cat_mult = category_values.get(y_cat, 10.0)
    
    # Continuous function on x with category-dependent scaling
    return (x_val - 2.5)**2 * cat_mult

def integer_categorical_2d(x: np.ndarray) -> float:
    """
    Function with integer x and categorical y.
    x: integer from allowed values
    y: categorical from ['low', 'medium', 'high']
    """
    # Round x to nearest integer - handle both numeric and object arrays
    x_val = float(x[0]) if not isinstance(x[0], str) else float(x[0])
    x_int = int(np.round(x_val))
    
    # Handle y as categorical
    y_cat = str(x[1]) if not isinstance(x[1], str) else x[1]
    
    # Category impact matrix
    category_impact = {
        'low': [1, 2, 3, 4, 5],
        'medium': [5, 1, 2, 3, 4], 
        'high': [4, 5, 1, 2, 3]
    }
    
    # Get impact based on x_int position (mod 5 to handle any integer)
    impact_list = category_impact.get(y_cat, [10, 10, 10, 10, 10])
    impact = impact_list[abs(x_int) % 5]
    
    return float(x_int**2 + impact)

def discrete_categorical_2d(x: np.ndarray) -> float:
    """
    Function with discrete x (from list) and categorical y.
    x: discrete value that should be from allowed list
    y: categorical from ['red', 'green', 'blue']
    """
    # x should be from the allowed discrete values - handle both numeric and object arrays
    x_val = float(x[0]) if not isinstance(x[0], str) else float(x[0])
    
    # Handle y as categorical
    y_cat = str(x[1]) if not isinstance(x[1], str) else x[1]
    
    # Color-based function behavior
    color_functions = {
        'red': lambda v: (v - 2.5)**2,
        'green': lambda v: abs(v - 1.0) * 3,
        'blue': lambda v: np.sin(v * np.pi) * 5 + 5
    }
    
    func = color_functions.get(y_cat, lambda v: v**2 + 10)
    return func(x_val)

def mixed_discrete_continuous_2d(x: np.ndarray, discrete_dim: int = 0) -> float:
    """Mixed function where one dimension is discrete and the other is continuous."""
    if discrete_dim == 0:
        x_discrete = np.round(x[0])
        return (x_discrete**2 + (x[1] - x_discrete)**2) * (1 + 0.1 * np.abs(x_discrete))
    else:
        y_discrete = np.round(x[1])
        return ((x[0] - y_discrete)**2 + y_discrete**2) * (1 + 0.1 * np.abs(y_discrete))

def categorical_interaction_2d(x: np.ndarray) -> float:
    """
    Function with two categorical variables that interact.
    x: categorical from ['type1', 'type2', 'type3']
    y: categorical from ['mode_a', 'mode_b', 'mode_c', 'mode_d']
    """
    # Handle both as categorical
    x_cat = str(x[0]) if not isinstance(x[0], str) else x[0]
    y_cat = str(x[1]) if not isinstance(x[1], str) else x[1]
    
    # Interaction matrix
    interaction_matrix = {
        ('type1', 'mode_a'): 5.0,
        ('type1', 'mode_b'): 3.0,
        ('type1', 'mode_c'): 8.0,
        ('type1', 'mode_d'): 2.0,
        ('type2', 'mode_a'): 1.0,
        ('type2', 'mode_b'): 7.0,
        ('type2', 'mode_c'): 0.0,  # Global optimum
        ('type2', 'mode_d'): 4.0,
        ('type3', 'mode_a'): 6.0,
        ('type3', 'mode_b'): 2.0,
        ('type3', 'mode_c'): 9.0,
        ('type3', 'mode_d'): 3.0,
    }
    
    return interaction_matrix.get((x_cat, y_cat), 100.0)  # High penalty for invalid combinations

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
    "griewank_2d": {
        "func": griewank_2d,
        "dim": 2,
        "bounds": [(-100.0, 100.0), (-100.0, 100.0)],
        "optimum_loc": np.array([0.0, 0.0]),
        "optimum_val": 0.0,
        "plot_bounds": [(-10.0, 10.0), (-10.0, 10.0)],  # Tighter bounds for visualization
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
    # --- Discrete Functions ---
    "discrete_rastrigin_2d": {
        "func": discrete_rastrigin_2d,
        "dim": 2,
        "bounds": [(-5.0, 5.0, 1.0), (-5.0, 5.0, 1.0)],  # (min, max, step)
        "param_types": ["discrete", "discrete"],
        "optimum_loc": np.array([0.0, 0.0]),
        "optimum_val": 0.0,
    },
    "step_function_2d": {
        "func": step_function_2d,
        "dim": 2,
        "bounds": [(-5.0, 5.0), (-5.0, 5.0)],  # Continuous bounds, discretized internally
        "param_types": ["continuous", "continuous"],
        "optimum_loc": np.array([0.0, 0.0]),
        "optimum_val": 0.0,
    },
    "integer_quadratic_2d": {
        "func": integer_quadratic_2d,
        "dim": 2,
        "bounds": [list(range(-10, 11)), list(range(-10, 11))],  # List of allowed integer values
        "param_types": ["discrete", "discrete"],
        "optimum_loc": np.array([3, -2]),
        "optimum_val": 3.0,  # Corrected: actual minimum value is 3.0, not 0.0
    },
    "discrete_sphere_nd": {
        "func": discrete_sphere_nd,
        "dim": 'nD',
        "bounds": (-5.0, 5.0, 0.5),  # (min, max, step) for each dimension
        "param_types": "discrete",  # All dimensions are discrete
        "optimum_val": 0.0,
    },
    # --- Categorical/Mixed Functions ---
    "string_categorical_mixed_2d": {
        "func": string_categorical_mixed_2d,
        "dim": 2,
        "bounds": [(-5.0, 5.0), ['a', 'b', 'c']],  # Continuous x, categorical y
        "param_types": ["continuous", "categorical"],
        "optimum_loc": np.array([2.5, 'b']),  # x=2.5, y='b' gives minimum
        "optimum_val": 0.0,
    },
    "integer_categorical_2d": {
        "func": integer_categorical_2d,
        "dim": 2,
        "bounds": [[-5, -3, -1, 0, 1, 3, 5], ['low', 'medium', 'high']],  # Discrete integers and categories
        "param_types": ["discrete", "categorical"],
        "optimum_loc": np.array([0, 'medium']),  # Depends on the impact matrix
        "optimum_val": 1.0,
    },
    "discrete_categorical_2d": {
        "func": discrete_categorical_2d,
        "dim": 2,
        "bounds": [[0.5, 1.0, 1.5, 2.0, 2.5, 3.0], ['red', 'green', 'blue']],  # Discrete values and colors
        "param_types": ["discrete", "categorical"],
        "optimum_loc": np.array([2.5, 'red']),  # Minimum at x=2.5 with red
        "optimum_val": 0.0,
    },
    "mixed_discrete_continuous_2d": {
        "func": mixed_discrete_continuous_2d,
        "dim": 2,
        "bounds": [(-5.0, 5.0, 1.0), (-5.0, 5.0)],  # First dim discrete (min, max, step), second continuous
        "param_types": ["discrete", "continuous"],
        "optimum_loc": np.array([0.0, 0.0]),
        "optimum_val": 0.0,
    },
    "categorical_interaction_2d": {
        "func": categorical_interaction_2d,
        "dim": 2,
        "bounds": [['type1', 'type2', 'type3'], ['mode_a', 'mode_b', 'mode_c', 'mode_d']],
        "param_types": ["categorical", "categorical"],
        "optimum_loc": np.array(['type2', 'mode_c']),
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
