import pandas as pd, numpy as np, os, itertools, random, time, json, multiprocessing
import seaborn as sns, matplotlib.pyplot as plt, math, torch, psutil
from tqdm import tqdm
from copy import copy
from multiprocessing import Pool

# Get total number of CPU cores
total_cores = multiprocessing.cpu_count()
num_processes = max(1, int(total_cores * 0.90))  # Use 90% of cores

def get_device():
    """Get available device (GPU or CPU)"""
    if torch.cuda.is_available():
        try:
            # Test CUDA availability with a small tensor
            test_tensor = torch.zeros(1).cuda()
            device = 'cuda'
        except RuntimeError:
            print("Warning: CUDA device reported as available but failed to initialize. Falling back to CPU.")
            device = 'cpu'
    else:
        print("CUDA not available. Using CPU.")
        device = 'cpu'
    
    print(f'Using device: {device}')
    return device

# Generate all possible combinations using itertools.product
def generate_full_factorial_design(nr_factors = 5, levels = 2):    
    combinations = list(itertools.product(list(range(levels)), repeat = nr_factors))  
    combinations = np.array(combinations)
    return combinations

# Generate oa using elimination of experiments
def generate_oa_by_elimination(nr_factors = 5, levels = 2, strength = 3, nr_restarts = 5, file_path = None, overwrite = False):
    # Make sure strength is always less than the number of factors
    if strength > nr_factors:
        print('Cannot generate array where strength is greater than the number of factors.')
        return None
    
    if file_path is not None and os.path.exists(file_path) and not overwrite:
        print(f'Fetching results from the existing file {file_path}.')
        return fetch_oa_from_file(file_path)
        
    print(f'Generating orthogonal array for {nr_factors} factors, {levels} levels and strength {strength}...')
    
    all_combinations = generate_full_factorial_design(nr_factors, levels)
    
    if strength == nr_factors:
        print('Strength is equal to the number of factors, which means that the full factorial design is requested.')
        best_oa = {'oa': all_combinations, 'oa_length': all_combinations.shape[0], 'generation_time': 0}
    else:
        full_factorial_array = all_combinations
        strength_combinations = np.array(list(itertools.combinations(list(range(nr_factors)), strength)))
        nr_required_combinations = levels ** strength
        
        all_results = []
        
        for r in range(nr_restarts):
             result = single_oa_by_elimination_run(full_factorial_array, strength_combinations, nr_required_combinations, levels)
             all_results.append(result)
        
        valid_results = [item for item in all_results if item['oa'] is not None]
        
        if len(valid_results) == 0:
            print('No valid OA could be generated.')
            return None
        
        best_oa = min(valid_results, key = lambda item: item['oa_length'])
    
    results = {'factors': nr_factors,
               'levels': levels,
               'strength': strength,
               'full_factorial_length': all_combinations.shape[0],
               'oa_length': best_oa['oa_length'],
               'generation_time': best_oa['generation_time'],
               'oa': best_oa['oa'].tolist()}
    
    if file_path is not None:
        with open(file_path, 'w') as f:
            f.write(custom_format_json(results))
        fig_path = os.path.splitext(file_path)[0] + '.png'
    else:
        fig_path = None
   
    title = f'Orthogonal array with {nr_factors} factors, {levels} levels and strength {strength}'
    fig_size = (nr_factors * 2, best_oa['oa_length'] * 0.3)
    try:
        plot_sampling_array_heatmap(oa = best_oa['oa'], fig_size = fig_size, title = title, save_path = fig_path)
    except:
        pass
    
    return results

# def single_oa_by_elimination_run(array = np.empty((0,0)), strength_combinations = [], nr_required_combinations = 0, levels = 3, exclude_indices = []):
#     i = 0
#     reduction_factor = 2
#     nr_rows_to_eleminate = 1
#     trial = 1
#     retry = False
#     oa = array
#     is_last_trial = False
#     pbar = tqdm(desc = "Generating OA: Removing experiments...", unit = " iterations", position=0, leave=True)
#     start_time = time.time()
#     while not is_last_trial:
#         _exclude_indices = copy(exclude_indices)
#         while True:
#             nr_rows_to_eleminate = nr_rows_to_remove(oa.shape[0], reduction_factor)
#             if nr_rows_to_eleminate == 1:
#                 is_last_trial = True
#             else:
#                 is_last_trial = False
            
#             pbar.set_postfix({'array_length': oa.shape[0], 'trial': trial, 'reduction_factor': reduction_factor})
#             pbar.update(1) 
            
#             if oa.shape[0] - len(_exclude_indices) > nr_rows_to_eleminate:
#                 oa_test, index_removed = remove_experiment(oa, _exclude_indices, nr_rows_to_eleminate)  
#                 all_corners_included = check_if_all_corners_are_included(oa_test, strength_combinations, nr_required_combinations, levels)
#                 if all_corners_included:
#                     oa = oa_test
#                     if nr_rows_to_eleminate == 1:
#                         _exclude_indices = [i if i <= index_removed[0] else i-1 for i in _exclude_indices]                        
#                     else:
#                         _exclude_indices = copy(exclude_indices)
#                 else:
#                     _exclude_indices.extend(index_removed)
                
#                 i = i + 1
#             else:
#                 if oa.shape[0] - len(_exclude_indices) == 1 and nr_rows_to_eleminate == 1:
#                     retry = False
#                 else:
#                     retry = True
#                 break
#         if retry:
#             reduction_factor = math.ceil(reduction_factor * 2)
#             trial = trial + 1
#         else:
#             end_time = time.time()
#             break

#     if is_last_trial and retry:
#         print('OA could not be generated')
#         oa = None
    
#     print(f'Orthogonal array length: {oa.shape[0]}')
#     print(f'Time required to generate: {end_time - start_time} seconds')
    
#     results = {'oa_length': oa.shape[0],
#                'generation_time': end_time - start_time,
#                'oa': oa}

#     return results

def single_oa_by_elimination_run(array=np.empty((0,0)), strength_combinations=[], 
                               nr_required_combinations=0, levels=3, exclude_indices=[], restart_num=None):
    i = 0
    reduction_factor = 2
    nr_rows_to_eleminate = 1
    trial = 1
    retry = False
    oa = array
    is_last_trial = False
    start_time = time.time()
    
    while not is_last_trial:
        _exclude_indices = copy(exclude_indices)
        while True:
            nr_rows_to_eleminate = nr_rows_to_remove(oa.shape[0], reduction_factor)
            if nr_rows_to_eleminate == 1:
                is_last_trial = True
            else:
                is_last_trial = False
            
            # if i % 100 == 0:  # Print progress every 100 iterations
            #     print(f"Restart {restart_num} elimination: Length {oa.shape[0]}, trial {trial}, reduction {reduction_factor}")
            
            if oa.shape[0] - len(_exclude_indices) > nr_rows_to_eleminate:
                oa_test, index_removed = remove_experiment(oa, _exclude_indices, nr_rows_to_eleminate)
                all_corners_included = check_if_all_corners_are_included(
                    oa_test, 
                    strength_combinations, 
                    nr_required_combinations, 
                    levels
                )
                if all_corners_included:
                    oa = oa_test
                    _exclude_indices = copy(exclude_indices)
                else:
                    _exclude_indices.extend(index_removed)
                
                i = i + 1
            else:
                if oa.shape[0] - len(_exclude_indices) == 1 and nr_rows_to_eleminate == 1:
                    retry = False
                else:
                    retry = True
                break
                
        if retry:
            reduction_factor = math.ceil(reduction_factor * 2)
            trial = trial + 1
        else:
            end_time = time.time()
            break

    if is_last_trial and retry:
        print(f'Restart {restart_num}: OA could not be generated')
        oa = None
    else:
        print(f'Restart {restart_num}: Final array length: {oa.shape[0] if oa is not None else 0}')
        print(f'Restart {restart_num}: Time required: {end_time - start_time:.2f} seconds')
    
    results = {
        'oa_length': oa.shape[0] if oa is not None else 0,
        'generation_time': end_time - start_time,
        'oa': oa
    }

    return results

def remove_experiment(data: np.array, exclude_indices: list = [], nr_rows_to_eleminate: int = 1):
    try:
        # Get the list of possible indices to remove
        indices_list = list(range(data.shape[0]))
        for i in exclude_indices:
            indices_list.remove(i)
        
        index = random.sample(indices_list, min(nr_rows_to_eleminate, len(indices_list)))
        
        # Remove the row index
        new_data = np.delete(data, index, axis = 0)
        
        return new_data, index
    except:
        print('error')
        
def nr_rows_to_remove(array_length = 200, reduction_factor = 2):
    nr = array_length // reduction_factor    
    return max(1, nr)

def generate_oa_by_addition(nr_factors = 5, levels = 2, strength = 3, nr_restarts = 5, file_path = None, overwrite = False):    
    # Make sure strength is always less than the number of factors
    if strength > nr_factors:
        print('Cannot generate array where strength is greater than the number of factors.')
        return None
           
    if file_path is not None and os.path.exists(file_path) and not overwrite:
        print(f'Fetching results from the existing file {file_path}.')
        return fetch_oa_from_file(file_path)
    
    # device = get_device()
    device = 'cpu'
    
    print('*************************************************************************************************')
    print(f'Generating orthogonal array for {nr_factors} factors, {levels} levels and strength {strength}...')
    
    full_factorial_length = levels ** nr_factors
    
    if strength == nr_factors:
        print('Strength is equal to the number of factors, which means that the full factorial design is requested.')
        all_combinations = generate_full_factorial_design(nr_factors, levels)
        best_oa = {'oa': all_combinations, 'oa_length': all_combinations.shape[0], 'generation_time': 0}
    else:    
        strength_combinations = np.array(list(itertools.combinations(list(range(nr_factors)), strength)))
        nr_required_combinations = levels ** strength
        
        # # Create argument list for parallel processing
        # args_list = [
        #     (r, nr_factors, levels, strength, strength_combinations, nr_required_combinations, device)
        #     for r in range(nr_restarts)
        # ]
        
        # # Run restarts in parallel
        # with Pool(processes=num_processes) as pool:
        #     all_results = pool.map(single_restart_run, args_list)
        
        all_results = []
        for r in range(nr_restarts):
            if r == 0:
                exclude_indices = [0]
            else:
                exclude_indices = []
            result = single_oa_by_addition_run(nr_factors, levels, strength, strength_combinations, nr_required_combinations, device, exclude_indices)
            all_results.append(result)
        
        valid_results = [item for item in all_results if item['oa'] is not None]
        
        if len(valid_results) == 0:
            print('No valid OA could be generated.')
            return None
        
        best_oa = min(valid_results, key = lambda item: item['oa_length'])
    
    results = {'factors': nr_factors,
               'levels': levels,
               'strength': strength,
               'full_factorial_length': full_factorial_length,
               'oa_length': best_oa['oa_length'],
               'generation_time': best_oa['generation_time'],
               'oa': best_oa['oa'].tolist()}
    
    if file_path is not None:
        with open(file_path, 'w') as f:
            f.write(custom_format_json(results))
        fig_path = os.path.splitext(file_path)[0] + '.png'
    else:
        fig_path = None
   
    title = f'Orthogonal array with {nr_factors} factors, {levels} levels and strength {strength}'
    fig_size = (nr_factors * 2, best_oa['oa_length'] * 0.3)
    try:
        plot_sampling_array_heatmap(oa = best_oa['oa'], fig_size = fig_size, title = title, save_path = fig_path)
    except:
        pass
    
    return results    

def generate_oa_by_addition_parallel(nr_factors=5, levels=2, strength=3, nr_restarts=5, 
                                   file_path=None, overwrite=False, num_processes=None):
    if strength > nr_factors:
        print('Cannot generate array where strength is greater than the number of factors.')
        return None
           
    if file_path is not None and os.path.exists(file_path) and not overwrite:
        print(f'Fetching results from the existing file {file_path}.')
        return fetch_oa_from_file(file_path)
    
    device = 'cpu'
    
    print('*************************************************************************************************')
    print(f'Generating orthogonal array for {nr_factors} factors, {levels} levels and strength {strength}...')
    
    full_factorial_length = levels ** nr_factors
    
    if strength == nr_factors:
        print('Strength is equal to the number of factors, which means that the full factorial design is requested.')
        all_combinations = generate_full_factorial_design(nr_factors, levels)
        best_oa = {'oa': all_combinations, 'oa_length': all_combinations.shape[0], 'generation_time': 0}
    else:    
        strength_combinations = np.array(list(itertools.combinations(list(range(nr_factors)), strength)))
        nr_required_combinations = levels ** strength
        
        args_list = [
            (r, nr_factors, levels, strength, strength_combinations, nr_required_combinations, device)
            for r in range(nr_restarts)
        ]
        
        start_time = time.time()
        print(f"\nStarting {nr_restarts} parallel restarts with {num_processes} processes...")
        
        with Pool(processes=num_processes) as pool:
            all_results = pool.map(single_restart_run, args_list)
            
        end_time = time.time()
        
        print(f"\nTotal time for all restarts: {end_time - start_time:.2f} seconds")
        
        valid_results = [item for item in all_results if item['oa'] is not None]
        
        if len(valid_results) == 0:
            print('No valid OA could be generated.')
            return None
        
        best_oa = min(valid_results, key=lambda item: item['oa_length'])
        print(f"\nBest result found: array length = {best_oa['oa_length']}")
    
    results = {
        'factors': nr_factors,
        'levels': levels,
        'strength': strength,
        'full_factorial_length': full_factorial_length,
        'oa_length': best_oa['oa_length'],
        'generation_time': best_oa['generation_time'],
        'oa': best_oa['oa'].tolist()
    }
    
    if file_path is not None:
        with open(file_path, 'w') as f:
            f.write(custom_format_json(results))
        fig_path = os.path.splitext(file_path)[0] + '.png'
    else:
        fig_path = None
   
    title = f'Orthogonal array with {nr_factors} factors, {levels} levels and strength {strength}'
    fig_size = (nr_factors * 2, best_oa['oa_length'] * 0.3)
    try:
        plot_sampling_array_heatmap(oa = best_oa['oa'], fig_size = fig_size, title = title, save_path = fig_path)
    except:
        pass
        
    return results
    
def single_restart_run(args):
    """
    Wrapper function for a single restart run
    """
    r, nr_factors, levels, strength, strength_combinations, nr_required_combinations, device = args
    exclude_indices = [0] if r == 0 else []
    
    # Just print which restart is running instead of using a progress bar
    print(f"\nStarting restart {r + 1}")
    
    result = single_oa_by_addition_run(
        nr_factors, 
        levels, 
        strength, 
        strength_combinations, 
        nr_required_combinations, 
        device, 
        exclude_indices,
        restart_num=r + 1
    )
    
    return result

# def single_oa_by_addition_run(nr_factors = 5, levels = 2, strength = 3, strength_combinations = np.empty((0,0)), nr_required_combinations = 0, device = 'cpu', exclude_indices = []):
    
#     if len(exclude_indices) == 1:
#         oa = np.zeros((1, nr_factors), dtype = int)
#     else:
#         oa = np.empty((0, nr_factors), dtype = int)
#     pbar = tqdm(desc = "Generating OA: Adding experiments...", unit = " iterations", position=0, leave=True)
    
#     start_time = time.time()
    
#     i = 0
#     while not check_if_all_corners_are_included(oa, strength_combinations, nr_required_combinations, levels):
#         oa = add_random_sample(oa, nr_factors, levels, nr_required_combinations)
#         pbar.set_postfix({'array_length': oa.shape[0]})
#         pbar.update(1)
#         i = i + 1
#     pbar.close()
    
#     # Once the oa has been created, check if any rows can be eleminated to reduce the size
#     if device == 'cuda':
#         results = gpu_single_oa_by_elimination_run(oa, strength_combinations, nr_required_combinations, levels, device)
#     else:
#         results = single_oa_by_elimination_run(oa, strength_combinations, nr_required_combinations, levels, exclude_indices)
    
#     end_time = time.time()
    
#     results['generation_time'] = end_time - start_time
    
#     return results    

def single_oa_by_addition_run(nr_factors=5, levels=2, strength=3, strength_combinations=np.empty((0,0)), 
                            nr_required_combinations=0, device='cpu', exclude_indices=[], restart_num=None):
    if len(exclude_indices) == 1:
        oa = np.zeros((1, nr_factors), dtype=int)
    else:
        oa = np.empty((0, nr_factors), dtype=int)
    
    start_time = time.time()
    
    # Simple counter instead of progress bar
    i = 0
    while not check_if_all_corners_are_included(oa, strength_combinations, nr_required_combinations, levels):
        oa = add_random_sample(oa, nr_factors, levels, nr_required_combinations)
        i = i + 1
        # if i % 100 == 0:  # Print progress every 100 iterations
        #     print(f"Restart {restart_num}: Added {i} samples, current array length: {oa.shape[0]}")
    
    # For elimination phase
    result = single_oa_by_elimination_run(
        oa, 
        strength_combinations, 
        nr_required_combinations, 
        levels, 
        exclude_indices,
        restart_num=restart_num
    )
    
    end_time = time.time()
    result['generation_time'] = end_time - start_time
    
    return result
    
def add_random_sample(oa, nr_factors, levels, nr_required_combinations):
    full_factorial_length = levels ** nr_factors
    random_sample = np.empty(shape = (0, nr_factors))
    for i in range(nr_required_combinations):
        if oa.shape[0] == full_factorial_length:
            return oa
        while True:
            random_sample = np.random.randint(0, levels, size = (1, nr_factors))
            if not np.any(np.all(oa == random_sample, axis=1)): # Check if the row already exists
                break
        oa = np.vstack((oa, random_sample))
    return oa    

def check_if_all_corners_are_included(data: np.array, strength_combinations: np.array, nr_required_combinations: int = 0 ,levels: int = 3):
    results = np.apply_along_axis(check_if_all_corners_are_included_for_given_columns,
                                  axis = 1,
                                  arr = strength_combinations,
                                  data = data,
                                  nr_required_combinations = nr_required_combinations,
                                  levels = levels)
    
    return np.all(results)
    
def check_if_all_corners_are_included_for_given_columns(row, data: np.array, nr_required_combinations: int = 0, levels: int = 3):
    """
    Check if all required combinations exist in given columns using power encoding
    Instead of using np.unique on the full array, we encode rows as unique numbers
    """
    subarray = data[:, row]
    
    # Create powers of 'level' for each column
    powers = np.array([levels**i for i in range(subarray.shape[1])], dtype=np.int64)
    
    # Convert each row to a unique number
    combined = (subarray * powers).sum(axis=1)
    
    # Count unique combinations
    unique_count = len(np.unique(combined))
    
    return unique_count == nr_required_combinations

# def check_if_all_corners_are_included_parallel(data: np.array, strength_combinations: np.array, nr_required_combinations: int = 0, levels: int = 3, num_processes: int = None):
#     """
#     Parallel version of corner checking using multiprocessing
#     """
#     # Create list of arguments for each combination
#     args_list = [(row, data, nr_required_combinations, levels) for row in strength_combinations]
    
#     # Use multiprocessing pool to check combinations in parallel
#     with Pool(processes=num_processes) as pool:
#         results = pool.map(check_single_combination, args_list)
    
#     return np.all(results)

# def check_single_combination(args):
#     """
#     Helper function to check a single combination of corners
#     """
#     row, data, nr_required_combinations, levels = args
#     subarray = data[:, row]
#     powers = np.array([levels**i for i in range(subarray.shape[1])], dtype=np.int64)
#     combined = (subarray * powers).sum(axis=1)
#     unique_count = len(np.unique(combined))
#     return unique_count == nr_required_combinations

def fetch_oa_from_file(file_path = None):
    if file_path is None:
        print('Please provide a file path.')
        return None
    
    if not os.path.exists(file_path):
        print(f'Please provide a valid file path. {file_path} does not exist')
        return None
    
    with open(file_path, 'r') as f:
        results = json.load(f)
        results['oa'] = np.array(results['oa'])
        
    return results
    
def custom_format_json(data):
    # Format the main structure with indentation
    formatted = "{\n"
    
    # Handle all items except the last one (which will be "oa")
    items = []
    for key, value in data.items():
        if key != "oa":
            formatted_value = json.dumps(value)
            items.append(f'    "{key}": {formatted_value}')
    
    # Add the formatted items
    formatted += ",\n".join(items)
    
    # Format "oa" with each sublist on its own line
    formatted += ',\n    "oa": [\n'
    # Add each sublist with indentation
    oa_items = [f'        {json.dumps(item)}' for item in data["oa"]]
    formatted += ',\n'.join(oa_items)
    formatted += '\n    ]\n'
    
    formatted += "}"
    return formatted
    
def plot_sampling_array_heatmap(oa, factors=None, title = None, fig_size=(10, 6), save_path=None, dpi=300):
    """
    Plot sampling array as a heatmap and optionally save it.
    
    Parameters:
    -----------
    oa : array-like
        The orthogonal array to plot
    factors : list, optional
        List of factor names. If None, will use 'Factor 1', 'Factor 2', etc.
    figsize : tuple, optional
        Figure size in inches (width, height)
    save_path : str, optional
        If provided, save the figure to this path (e.g., 'plot.png', 'plot.pdf')
    dpi : int, optional
        The resolution in dots per inch for saving the figure
    """
    # Create factor names if not provided
    if factors is None:
        factors = [f'Factor {i+1}' for i in range(oa.shape[1])]
    
    # Create sample names
    samples = [f'Sample {i+1}' for i in range(oa.shape[0])]
    
    # Create DataFrame
    df = pd.DataFrame(oa, columns=factors, index=samples)
    
    # Create plot
    plt.figure(figsize=fig_size)
    sns.heatmap(df, 
                cmap='viridis',
                cbar=False,     # Remove colorbar
                xticklabels=True,
                yticklabels=True,
                annot=True,     # Show numbers in cells
                fmt='d',        # Format as integer
                linewidths=0.5, # Add thin borders
                linecolor='black') # Border color
    
    plt.tick_params(axis='both', which='both', length=0)
    plt.tight_layout()

    if title is not None:
        plt.title(title)
    
    # Save figure if path is provided
    if save_path is not None:
        plt.savefig(save_path, dpi=dpi, bbox_inches='tight')
        plt.close()
    else:
        plt.show()

#%% GPU functions
def gpu_unique_rows(tensor, levels):
    """GPU version of np.unique for rows"""
    # Combine rows into a single number for comparison
    # This is more efficient than comparing row by row
    powers = torch.tensor([levels**i for i in range(tensor.shape[1])], device=tensor.device, dtype=torch.int64)
    combined = (tensor * powers).sum(dim=1)
    unique_combinations = torch.unique(combined)
    return unique_combinations.shape[0]

def gpu_check_if_all_corners_are_included_for_given_columns(row, data, nr_required_combinations, levels):
    """GPU version of checking corners for given columns"""
    subarray = data[:, row]
    unique_count = gpu_unique_rows(subarray, levels)
    return unique_count == nr_required_combinations

def gpu_check_if_all_corners_are_included(data, strength_combinations, nr_required_combinations, levels):
    """GPU version of checking all corners"""
    results = []
    for combination in strength_combinations:
        result = gpu_check_if_all_corners_are_included_for_given_columns(combination, data, nr_required_combinations, levels)
        results.append(result)
    return torch.tensor(results, device=data.device).all()

def gpu_remove_experiment(data, exclude_indices=[], nr_rows_to_eleminate=1):
    """GPU version of removing experiments"""
    try:
        # Get the list of possible indices to remove
        indices_list = list(range(data.shape[0]))
        for i in exclude_indices:
            indices_list.remove(i)
        
        # Randomly select indices to remove
        index = random.sample(indices_list, nr_rows_to_eleminate)
        
        # Create mask for rows to keep
        mask = torch.ones(data.shape[0], dtype=torch.bool, device=data.device)
        mask[torch.tensor(index, device=data.device)] = False
        
        # Remove the rows using the mask
        new_data = data[mask]
        
        return new_data, index
    except Exception as e:
        print(f'Error in gpu_remove_experiment: {str(e)}')
        return None, None
    
def gpu_single_oa_by_elimination_run(array, strength_combinations, nr_required_combinations, levels, device='cuda'):
    """GPU version of the main OA generation function"""
    # Convert input arrays to GPU tensors
    oa = torch.tensor(array, device=device)
    strength_combinations = torch.tensor(strength_combinations, device=device)
    
    i = 0
    reduction_factor = 2
    nr_rows_to_eleminate = 1
    trial = 1
    retry = False
    is_last_trial = False
    
    pbar = tqdm(desc="Generating OA: Removing experiments...", unit=" iterations", position=0, leave=True)
    start_time = time.time()
    
    while not is_last_trial:
        exclude_indices = []
        while True:
            nr_rows_to_eleminate = nr_rows_to_remove(oa.shape[0], reduction_factor)
            if nr_rows_to_eleminate == 1:
                is_last_trial = True
            else:
                is_last_trial = False
            
            pbar.set_postfix({
                'array_length': oa.shape[0], 
                'trial': trial, 
                'reduction_factor': reduction_factor
            })
            pbar.update(1)
            
            if oa.shape[0] - len(exclude_indices) > nr_rows_to_eleminate:
                oa_test, index_removed = gpu_remove_experiment(oa, exclude_indices, nr_rows_to_eleminate)
                
                if oa_test is not None:
                    all_corners_included = gpu_check_if_all_corners_are_included(oa_test, strength_combinations, nr_required_combinations, levels)
                    
                    if all_corners_included:
                        oa = oa_test
                        exclude_indices = []
                    else:
                        exclude_indices.extend(index_removed)
                    
                    i = i + 1
                else:
                    retry = True
                    break
            else:
                if oa.shape[0] - len(exclude_indices) == 1 and nr_rows_to_eleminate == 1:
                    retry = False
                else:
                    retry = True
                break
                
        if retry:
            reduction_factor = math.ceil(reduction_factor * 1.5)
            trial = trial + 1
        else:
            end_time = time.time()
            break

    if is_last_trial and retry:
        print('OA could not be generated')
        oa = None
        results = {'oa_length': 0,
                  'generation_time': end_time - start_time,
                  'oa': None}
    else:
        # Convert result back to numpy for consistency with original function
        oa_numpy = oa.cpu().numpy()
        print(f'Orthogonal array length: {oa_numpy.shape[0]}')
        print(f'Time required to generate: {end_time - start_time} seconds')
        
        results = {'oa_length': oa_numpy.shape[0],
                  'generation_time': end_time - start_time,
                  'oa': oa_numpy}

    return results

#%%
# class batch_size_optimizer:
#     """Optimize batch size based on system resources and problem size"""
    
#     def __init__(self):
#         self.min_batch_size = 100
#         self.max_batch_size = 10000
        
#     def get_gpu_memory_info(self):
#         """Get GPU memory information"""
#         if torch.cuda.is_available():
#             device = torch.cuda.current_device()
#             total_memory = torch.cuda.get_device_properties(device).total_memory
#             reserved_memory = torch.cuda.memory_reserved(device)
#             allocated_memory = torch.cuda.memory_allocated(device)
#             free_memory = total_memory - reserved_memory - allocated_memory
#             return total_memory, free_memory
#         return 0, 0
    
#     def get_system_memory_info(self):
#         """Get system memory information"""
#         memory = psutil.virtual_memory()
#         return memory.total, memory.available
    
#     def estimate_memory_per_item(self, array_shape: tuple[int, int], strength: int) -> float:
#         """Estimate memory needed per combination"""
#         # Rough estimation of memory needed for one combination
#         row_count = array_shape[0]
#         return (row_count * strength * 8)  # 8 bytes per number (64-bit)
    
#     def optimize_batch_size(self, array_shape: tuple[int, int], strength: int, num_gpus: int):
#         """
#         Optimize batch size based on available resources and problem size
        
#         Args:
#             array_shape: Shape of the input array
#             strength: Strength parameter
#             num_gpus: Number of GPUs available
#         Returns:
#             Optimal batch size
#         """
#         if torch.cuda.is_available():
#             total_memory, free_memory = self.get_gpu_memory_info()
#             # Use 70% of free GPU memory
#             available_memory = free_memory * 0.7
#         else:
#             _, free_memory = self.get_system_memory_info()
#             # Use 50% of free system memory
#             available_memory = free_memory * 0.5
        
#         memory_per_item = self.estimate_memory_per_item(array_shape, strength)
        
#         # Calculate batch size based on available memory
#         optimal_batch_size = int(available_memory / (memory_per_item * num_gpus))
        
#         # Bound the batch size
#         optimal_batch_size = max(self.min_batch_size, min(self.max_batch_size, optimal_batch_size))
        
#         # Round to nearest 100 for cleaner numbers
#         optimal_batch_size = int(round(optimal_batch_size / 100.0) * 100)
        
#         return optimal_batch_size

# class parallel_torch_array_checker:
#     def __init__(self, strength, num_gpus=None, batch_size=None):
#         """
#         Initialize checker with given strength
        
#         Args:
#             strength: strength parameter
#             num_gpus: number of GPUs to use. If None, use all available
#             batch_size: size of batches for parallel processing. If None, optimize automatically
#         """
#         self.strength = strength
#         self.nr_required_combinations = get_required_combinations_count(strength)
        
#         # Setup GPU devices
#         if torch.cuda.is_available():
#             self.num_gpus = num_gpus or torch.cuda.device_count()
#             self.devices = [f'cuda:{i}' for i in range(self.num_gpus)]
#             print(f"Using {self.num_gpus} GPU(s)")
#         else:
#             self.num_gpus = 1
#             self.devices = ['cpu']
#             print("Using CPU")
        
#         self.batch_optimizer = batch_size_optimizer()
#         self.batch_size = batch_size  # Will be set in check_array_parallel
        
#     def optimize_batch_size(self, array_shape: tuple[int, int]) -> int:
#         """Optimize batch size for given array shape"""
#         return self.batch_optimizer.optimize_batch_size(
#             array_shape, self.strength, self.num_gpus
#         )

#     def check_array_parallel(self, array: np.ndarray) -> Tuple[bool, Optional[np.ndarray]]:
#         """
#         Check array strength using parallel GPU processing with optimized batch size
        
#         Args:
#             array: numpy array to check
#         Returns:
#             tuple: (bool, array or None) - (success status, failing combination if any)
#         """
#         # Optimize batch size if not manually set
#         if self.batch_size is None:
#             self.batch_size = self.optimize_batch_size(array.shape)
#             print(f"Optimized batch size: {self.batch_size}")
        
#         # Convert data to torch tensor
#         data = torch.tensor(array, device=self.devices[0])
        
#         # Generate all combinations
#         strength_combinations = generate_strength_combinations(array.shape[1], self.strength)
        
#         # Create batch processor
#         processor = BatchProcessor(data, self.nr_required_combinations)
        
#         if self.num_gpus > 1:
#             processor = DataParallel(processor, device_ids=range(self.num_gpus))
        
#         # Process combinations in parallel batches
#         batches = split_into_chunks(strength_combinations, self.batch_size)
#         total_batches = len(batches)
        
#         for batch_idx, batch in enumerate(batches):
#             # Progress update
#             if (batch_idx + 1) % max(1, total_batches // 10) == 0:
#                 print(f"Progress: {((batch_idx + 1) / total_batches) * 100:.1f}%")
            
#             # Convert batch to tensor
#             batch_tensor = torch.tensor(batch, device=self.devices[0])
            
#             # Process batch
#             with torch.no_grad():
#                 batch_results = processor(batch_tensor)
            
#             # Check results
#             cpu_results = batch_results.cpu().numpy()
#             if not np.all(cpu_results):
#                 # Find first failing combination
#                 fail_idx = batch_idx * self.batch_size + np.where(~cpu_results)[0][0]
#                 return False, strength_combinations[fail_idx]
        
#         return True, None

#     def __del__(self):
#         # Clean up GPU memory
#         if torch.cuda.is_available():
#             torch.cuda.empty_cache()
            
# class BatchProcessor(torch.nn.Module):
#     """Module to process batches of combinations in parallel"""
#     def __init__(self, data, nr_required_combinations):
#         super().__init__()
#         self.register_buffer('data', data)
#         self.nr_required_combinations = nr_required_combinations

#     def forward(self, combinations_batch):
#         batch_results = []
#         batch_size = combinations_batch.size(0)
        
#         # Process each combination in the batch
#         for i in range(batch_size):
#             combination = combinations_batch[i]
#             subarray = self.data[:, combination]
            
#             # Create unique representation
#             powers = torch.tensor([3**i for i in range(len(combination))], 
#                                 device=subarray.device, dtype=torch.int64)
#             combined = (subarray * powers).sum(dim=1)
            
#             # Count unique combinations
#             unique_count = torch.unique(combined).size(0)
#             batch_results.append(unique_count == self.nr_required_combinations)
            
#         return torch.tensor(batch_results, device=combinations_batch.device)

# def get_required_combinations_count(strength):
#     """Calculate the number of required unique combinations for given strength"""
#     return 3 ** strength

# def generate_strength_combinations(columns, strength):
#     """Generate all possible column combinations of given strength"""
#     return np.array(list(combinations(range(columns), strength)))

# def split_into_chunks(lst: np.ndarray, chunk_size: int) -> List[np.ndarray]:
#     """Split array into chunks of specified size"""
#     return [lst[i:i + chunk_size] for i in range(0, len(lst), chunk_size)]