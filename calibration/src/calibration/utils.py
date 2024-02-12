#%% Imports
from reference_data.utils import write_reference_data_to_file
from reference_data.visualization import plot_all_groups
from copy import deepcopy
import shutil, uuid, tempfile, os


#%% Function used to perform a single simulation.
def run_single_simulation(parameters: dict = None, 
                          testbenches = None,
                          simulator = None,
                          reference_data = None,
                          simulation_files_path: str = None,
                          use_dask: bool = False,
                          dask_env: str = 'local',
                          plot: bool = False,
                          delete_files: bool = True,
                          print_output: bool = True):
    
    # return 5
        
    # Check that input is valid
    if testbenches is None:
        print('ERROR: testbenches is none. Please provide a valid testbench object.')
        return None
    if simulator is None:
        print('ERROR: simulator is none. Please provide a valid simulator object.')
        return None
    if reference_data is None:
        print('ERROR: reference_data is none. Please provide a valid reference_data object.')
        return None
    if simulation_files_path is None:
        print('ERROR: simulation_files_path is none. Please provide a valid simulations_file_path as a string.')
        return None
    if dask_env not in ['local', 'containers']:
        print('WARNING: dask_env is should be one of the following: [local, containers]. Setting it to local.')
        dask_env = 'local'
    
    # deepcopy input parameters to avoid any problems with manipulating the original objects
    testbenches_ = deepcopy(testbenches)
    simulator_ = deepcopy(simulator)
    reference_data_ = deepcopy(reference_data)
    
    # If dask is used, create temporary directories.
    if use_dask:
        if dask_env == 'local':
            temp_dir = os.path.join(simulation_files_path, str(uuid.uuid4()))
            os.mkdir(temp_dir)
        elif dask_env == 'containers':
            temp_dir = tempfile.mkdtemp()
            
        testbenches_.update_working_directory(temp_dir)
    else:
        temp_dir = simulation_files_path
        
    # If parameters are given, then create new testbenches
    if parameters is not None:
        testbenches_.modify_model_parameters(parameters)
    
    # Simulate
    results = simulator_.simulate_testbenches(testbenches = testbenches_,
                                              extract_results = True,
                                              compact = True,
                                              reference_data = reference_data_,
                                              delete_files = delete_files,
                                              print_output = print_output)
    
    if delete_files:
        if use_dask:
            remove_dir(dir_path = temp_dir, only_contents = False)
        else:
            remove_dir(dir_path = temp_dir, only_contents = True)
    
    # Write the simulation values in a file
    # write_reference_data_to_file(data = results,
    #                               file_path = 'test.json',
    #                               x_values = 'x_values_simulation',
    #                               y_values = 'y_values_simulation',
    #                               operating_conditions = ['temp', 'vbs', 'vds', 'vgs', 'frequency'],
    #                               instance_parameters = ['w', 'l', 'm', 'area'],
    #                               title = "nmos example",
    #                               description = "this dataset serves as an example of the json data format for an nmos transistor",
    #                               device_type = "mosfet")

    # Plot the data
    if plot:
        plot_all_groups(results, extra_legend = ['w', 'l', 'vds', 'vgs', 'vbs', 'm', 'area', 'temp'])
        
    return results


#%% Function to calculate the error metrics
def calculate_error_metrics(cost_function = None, data = None, parameters = None):
    
    # return {'data': 'kot', 'error_metric': {'total': 2}}
    
    # Check input validity
    if cost_function is None:
        print('ERROR: cost_function is none. Please provide a valid cost_function object.')
        return None
    if data is None:
        print('ERROR: data is none. Please provide a valid data object.')
        return None

    # Deepcopy object in order to avoid modification of the original object.    
    cost_function_ = deepcopy(cost_function)
    
    return cost_function_.run(data, parameters)


#%% Function to delete a directory and/or its contents
def remove_dir(dir_path: str = None, only_contents: bool = False):
    if dir_path is not None:
        if only_contents:
            for item in os.listdir(dir_path):
                item_path = os.path.join(dir_path, item)
            
                if os.path.isfile(item_path) or os.path.islink(item_path):
                    os.unlink(item_path)
            
                elif os.path.isdir(item_path):
                    shutil.rmtree(item_path)
        else:
            shutil.rmtree(dir_path)
    
    
    
    
    
    
