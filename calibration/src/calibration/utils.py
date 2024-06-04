#%% Imports
from reference_data.utils import write_reference_data_to_file
from reference_data.visualization import plot_all_groups
from copy import deepcopy
import shutil, uuid, tempfile, os, pickle

#%% Function used to perform a single simulation.
def run_single_simulation(parameters: dict = None, 
                          testbenches = None,
                          simulator = None,
                          reference_data = None,
                          simulation_files_path: str = None,
                          running_environment: str = 'local',
                          plot: bool = False,
                          delete_files: bool = True,
                          print_output: bool = True):
        
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
    if running_environment not in ('local', 'dask_local', 'kafka_local'):
        print('WARNING: dask_env is should be one of the following: [local, dask_local, kafka]. Setting it to local.')
        running_environment = 'local'
    
    # deepcopy input parameters to avoid any problems with manipulating the original objects
    _testbenches = deepcopy(testbenches)
    _simulator = deepcopy(simulator)
    _reference_data = deepcopy(reference_data)
    
    # If dask is used, create temporary directories.
    if running_environment == 'dask_local':
        temp_dir = os.path.join(simulation_files_path, str(uuid.uuid4()))
        os.mkdir(temp_dir)
        _testbenches.update_working_directory(temp_dir)
    else:
        temp_dir = simulation_files_path
        
    # If parameters are given, then create new testbenches
    if parameters is not None:
        _testbenches.modify_model_parameters(parameters)
    
    # Simulate
    results = _simulator.simulate_testbenches(testbenches = _testbenches,
                                              extract_results = True,
                                              compact = True,
                                              reference_data = _reference_data,
                                              delete_files = delete_files,
                                              print_output = print_output)
    
    if delete_files:
        if running_environment == 'dask_local':
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

def run_single_simulation_kafka_local(input_file: str = None):
    
    if input_file is None:
        print('ERROR: input_file is none. Please provide a valid input_file.')
        return None
    
    # Load the pickle file
    with open(input_file, 'rb') as file:
        input_dict = pickle.load(file)
    
    # Assign the variables
    if 'parameters' not in input_dict.keys():
        print('ERROR: testbenches is none. Please provide a valid testbench object.')
        return None
    else:
        parameters = input_dict['parameters']

    if 'testbenches' not in input_dict.keys():
        print('ERROR: testbenches is none. Please provide a valid testbench object.')
        return None
    else:
        testbenches = input_dict['testbenches']
        
    if 'simulator' not in input_dict.keys():
        print('ERROR: simulator is none. Please provide a valid simulator object.')
        return None
    else:
        simulator = input_dict['simulator'
                               ]
    if 'reference_data' not in input_dict.keys():
        print('ERROR: reference_data is none. Please provide a valid reference_data object.')
        return None
    else:
        reference_data = input_dict['reference_data']
        
    if 'cost_function' not in input_dict.keys():
        print('ERROR: reference_data is none. Please provide a valid reference_data object.')
        return None
    else:
        cost_function = input_dict['cost_function']
    
    if 'simulation_files_path' not in input_dict.keys():
        print('ERROR: simulation_files_path is none. Please provide a valid simulations_file_path as a string.')
        return None
    else:
        simulation_files_path = input_dict['simulation_files_path']
        
    if 'delete_files' not in input_dict.keys():
        delete_files = True
    else:
        delete_files = input_dict['delete_files']
        
    if 'print_output' not in input_dict.keys():
        print_output = False
    else:
        print_output = input_dict['print_output']
        
    if 'plot' not in input_dict.keys():
        plot = False
    else:
        plot = input_dict['plot']
    
    
    # deepcopy input parameters to avoid any problems with manipulating the original objects
    _testbenches = deepcopy(testbenches)
    _simulator = deepcopy(simulator)
    _reference_data = deepcopy(reference_data)
    
    # update simulation directory
    if _testbenches.working_directory != simulation_files_path:
        _testbenches.update_working_directory(simulation_files_path)
        
    # Update parameters
    _testbenches.modify_model_parameters(parameters)
    
    # Simulate
    simulation_results = _simulator.simulate_testbenches(testbenches = _testbenches,
                                                         extract_results = True,
                                                         compact = True,
                                                         reference_data = _reference_data,
                                                         delete_files = delete_files,
                                                         print_output = print_output)
    if delete_files: # Delete simulation files
            remove_dir(dir_path = simulation_files_path)
    if plot: # Plot the data
        plot_all_groups(simulation_results, extra_legend = ['w', 'l', 'vds', 'vgs', 'vbs', 'm', 'area', 'temp'])
        
    # Calculate metric
    metric = calculate_error_metrics(cost_function = cost_function, data = simulation_results, parameters = parameters)

    return metric

def run_single_simulation_kafka_aws(input_dict: dict = None):
    
    if input_dict is None:
        print('ERROR: input_dict is none. Please provide a valid input_dict.')
        return None
    
    # Assign the variables
    if 'parameters' not in input_dict.keys():
        print('ERROR: testbenches is none. Please provide a valid testbench object.')
        return None
    else:
        parameters = input_dict['parameters']

    if 'testbenches' not in input_dict.keys():
        print('ERROR: testbenches is none. Please provide a valid testbench object.')
        return None
    else:
        testbenches = input_dict['testbenches']
        
    if 'simulator' not in input_dict.keys():
        print('ERROR: simulator is none. Please provide a valid simulator object.')
        return None
    else:
        simulator = input_dict['simulator'
                               ]
    if 'reference_data' not in input_dict.keys():
        print('ERROR: reference_data is none. Please provide a valid reference_data object.')
        return None
    else:
        reference_data = input_dict['reference_data']
        
    if 'cost_function' not in input_dict.keys():
        print('ERROR: reference_data is none. Please provide a valid reference_data object.')
        return None
    else:
        cost_function = input_dict['cost_function']
    
    if 'simulation_files_path' not in input_dict.keys():
        print('ERROR: simulation_files_path is none. Please provide a valid simulations_file_path as a string.')
        return None
    else:
        simulation_files_path = input_dict['simulation_files_path']
        
    if 'delete_files' not in input_dict.keys():
        delete_files = True
    else:
        delete_files = input_dict['delete_files']
        
    if 'print_output' not in input_dict.keys():
        print_output = False
    else:
        print_output = input_dict['print_output']
        
    if 'plot' not in input_dict.keys():
        plot = False
    else:
        plot = input_dict['plot']
    
    
    # # deepcopy input parameters to avoid any problems with manipulating the original objects
    # _testbenches = deepcopy(testbenches)
    # _simulator = deepcopy(simulator)
    # _reference_data = deepcopy(reference_data)
    
    # # update simulation directory
    # if _testbenches.working_directory != simulation_files_path:
    #     _testbenches.update_working_directory(simulation_files_path)
        
    # Update parameters
    testbenches.modify_model_parameters(parameters)
    
    # Simulate
    simulation_results = simulator.simulate_testbenches(testbenches = testbenches,
                                                         extract_results = True,
                                                         compact = True,
                                                         reference_data = reference_data,
                                                         delete_files = delete_files,
                                                         print_output = print_output)
    if delete_files: # Delete simulation files
            remove_dir(dir_path = simulation_files_path)
    if plot: # Plot the data
        plot_all_groups(simulation_results, extra_legend = ['w', 'l', 'vds', 'vgs', 'vbs', 'm', 'area', 'temp'])
        
    # Calculate metric
    metric = calculate_error_metrics(cost_function = cost_function, data = simulation_results, parameters = parameters)

    return metric

#%% Function to calculate the error metrics
def calculate_error_metrics(cost_function = None, data = None, parameters = None):
    # Check input validity
    if cost_function is None:
        print('ERROR: cost_function is none. Please provide a valid cost_function object.')
        return None
    if data is None:
        print('ERROR: data is none. Please provide a valid data object.')
        return None

    # Deepcopy object in order to avoid modification of the original object.    
    _cost_function = deepcopy(cost_function)
    
    return _cost_function.run(data, parameters)

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
            
#%% Function to test ngspice
def test_ngspice(testbenches = None, simulator = None, reference_data = None):
    
    temp_dir = tempfile.mkdtemp()
    
    testbenches.update_working_directory(temp_dir)
    
    results = simulator.simulate_testbenches(testbenches = testbenches,
                                              extract_results = True,
                                              compact = True,
                                              reference_data = reference_data,
                                              delete_files = False,
                                              print_output = True)
    
    return results
    
    
    
    
    
    
