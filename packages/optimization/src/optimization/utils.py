# Imports
import pandas as pd, numpy as np
from scipy.optimize import curve_fit
from scipy.signal import savgol_filter
from sklearn.gaussian_process import GaussianProcessRegressor
from sklearn.gaussian_process.kernels import RBF, ConstantKernel

# Set transfor to 'None' for the lin parameter, to 'log' for positive parameter in log scale and to 'neglog' for negative parameter in log scale.
def set_transform(parameter):
    if parameter['scale'].lower() == 'log' or parameter['scale'].lower() == 'logarithmic':
        if parameter['min'] > 0 and parameter['max'] > 0:
            return 'log'
        elif parameter['min'] < 0 and parameter['max'] < 0:
            return 'neglog'
    return None

# Calculate the scaled value for the parameter
def scale_parameter(parameter, field = 'value'):
    if parameter['transform'] == 'log':
        return np.log10(parameter[field])
    elif parameter['transform'] == 'neglog':
        return np.log10(-parameter[field])
    else:
        return parameter[field]

# Calculate the unscaled values from the scaled parameter
def unscale_parameter(parameter, field):
    if parameter['transform'] == 'log':
        return np.longdouble(10.0**parameter[field])
    elif parameter['transform'] == 'neglog':
        return -np.longdouble(10.0**parameter[field])
    else:
        return parameter[field]

# Unnorm member
def unnorm_member(member, minimum, maximum):
    return minimum + member * (maximum - minimum)

# Norm member
def norm_member(member, minimum, maximum):
    return (member - minimum) / (maximum - minimum)

# Preprocess parameters, by checking their validity, calculating the corresponding transformation functions and scaling them respectively.
def preprocess_parameters(parameters: pd.DataFrame = None):
    if parameters is None or not isinstance(parameters, pd.DataFrame):
        raise SystemExit('ERROR! parameters have to be given as a pandas dataframe, with columns [name, min, max]')

    if 'name' not in parameters.columns or 'min' not in parameters.columns or 'max' not in parameters.columns:
        raise SystemExit('ERROR! parameters have to be given as a pandas dataframe, with columns [name, min, max]')

    if len(parameters['name'].tolist()) != len(set(parameters['name'].tolist())):
        raise SystemExit('ERROR! parameters cannot have duplicate names')

    # reset index
    parameters.reset_index(inplace = True, drop = True)

    # order parameters by name
    parameters = parameters.sort_values(by ='name')

    # set default to the middle value if it is not given
    if 'default' not in parameters.columns:
        parameters[['min', 'max']] = parameters[['min', 'max']].astype(float)
        parameters['default'] = (parameters['max'] + parameters['min']) / 2
    else:
        parameters[['min', 'max', 'default']] = parameters[['min', 'max', 'default']].astype(float)

    # set scale to linear if it is missing
    if 'scale' not in parameters.columns:
        parameters['scale'] = 'lin'

    parameters['transform'] = parameters.apply(lambda row: set_transform(row), axis = 1)                # set transform for each parameter
    parameters['value'] = parameters['default']                                                         # set the value to default
    parameters['value_scaled'] = parameters.apply(lambda row: scale_parameter(row, 'value'), axis = 1)  # set the value scaled
    parameters['min_scaled'] = parameters.apply(lambda row: scale_parameter(row, 'min'), axis = 1)      # set the min scaled
    parameters['max_scaled'] = parameters.apply(lambda row: scale_parameter(row, 'max'), axis = 1)      # set the max scaled

    return parameters

def rmse(x, y):
    return np.sqrt(np.mean((x - y)**2))

def exponential_func(x, a, b, c):
    return a * np.exp(-b * x) + c

def linear_func(x, a, b):
    return a * x + b

def fit_linear(x, y):
    best_popt = None
    lowest_rmse = np.inf
    p0_list = [[0.5, 0.5], [-0.5, -0.5], [-0.5, 0.5], [0.5, -0.5]]
    for p0 in p0_list:
        try:
            popt, pcov = curve_fit(linear_func, x, y, p0 = p0)
            fit_rmse = rmse(y, linear_func(x, *popt))
            if fit_rmse < lowest_rmse:
                best_popt = popt
                lowest_rmse = fit_rmse
        except RuntimeError:
            continue
    return best_popt, lowest_rmse

def fit_exponential(x, y):
    best_popt = None
    lowest_rmse = np.inf
    p0_list = [[0.5, 0.5, 0.5], [-0.5, -0.5, -0.5], [-0.5, 0.5, 0.5], [0.5, -0.5, 0.5], [-0.5, -0.5, 0.5], [0.5, -0.5, -0.5],]
    for p0 in p0_list:
        try:
            popt, pcov = curve_fit(exponential_func, x, y, p0 = p0)
            fit_rmse = rmse(y, exponential_func(x, *popt))
            if fit_rmse < lowest_rmse:
                best_popt = popt
                lowest_rmse = fit_rmse
        except RuntimeError:
            continue
    return best_popt, lowest_rmse

def get_exponential_or_linear_fit(x, y):
    # try the exponential fit first
    exp_popt, exp_fit_error = fit_exponential(x, y)
    lin_popt, lin_fit_error = fit_linear(x, y)
    if exp_popt is not None and lin_popt is not None:
        if exp_fit_error < lin_fit_error:
            return exp_popt, 'exponential'
        else:
            return lin_popt, 'linear'
    elif exp_popt is not None and lin_popt is None:
        return exp_popt, 'exponential'
    elif exp_popt is None and lin_popt is not None:
        return lin_popt, 'linear'
    else:
        return None, None

def get_gaussian_process_fit(x, y):
    x = x.reshape(-1, 1)
    y = y.reshape(-1, 1)

    kernel = ConstantKernel(1.0, (1e-10, 1e10)) * RBF(1.0, (1e-10, 1e10))
    gp = GaussianProcessRegressor(kernel = kernel, n_restarts_optimizer = 10, alpha = 5e-2)

    # Fit the model
    gp.fit(x, y)

    return gp

def smooth_data(data):
    window = int(np.min([99, len(data) / 2]))
    if(np.remainder(window, 2) == 0):
        window = window - 1
    return savgol_filter(data, window, min(3, window - 1))

def generate_spendley_points(n, r = 1, initial_point = None, initial_point_mode = 'corner'):
    """
    Generate Spendley's simplex points in n dimensions with a specified origin.

    Args:
        n (int): Number of dimensions
        r (float): Desired length of simplex edges
        origin (np.array or list): Coordinates of the origin point, defaults to None for origin at zero

    Returns:
        np.array: Array of shape (n+1, n) containing the simplex vertices
    """
    # Calculate p and q
    p = (r / (n * np.sqrt(2))) * (np.sqrt(n + 1) + n - 1)
    q = (r / (n * np.sqrt(2))) * (np.sqrt(n + 1) - 1)

    # Initialize points array
    points = np.full((n + 1, n), q)

    # Set diagonal elements to p
    for i in range(n):
        points[i, i] = p
    points[-1,:] = 0

    if initial_point is None:
        initial_point = np.zeros(n)

    if initial_point_mode not in ['corner', 'centroid']:
        initial_point_mode = 'corner'

    if initial_point_mode == 'corner':
        points += initial_point
    else:
        centroid = np.mean(points)
        offset = initial_point - centroid
        points += offset

    return points
