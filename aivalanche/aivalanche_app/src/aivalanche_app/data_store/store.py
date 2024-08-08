import json, pandas as pd, uuid, shutil, numpy as np, zmq, pickle
from copy import copy
from pathlib import Path
from datetime import datetime
from aivalanche_app.paths import dummy_data_path, projects_path
from aivalanche_app.resources.themes.style import style
from aivalanche_app.data_store.db import db
from aivalanche_app.simulations.single_simulation import single_simulation
from aivalanche_app.helper_functions import convert_to_list_if_semi_colon, filter_df_by_col_name_and_val, replace_space_with_underline, dict_to_json, get_current_timestamp
from reference_data.Reference_data import Reference_data
from reference_data.utils import write_reference_data_to_file
from PySide6.QtCore import QObject, Signal, QThread, QTimer

# Data management thread
class dm_thread(QThread):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.tasks = []

    def run(self):
        while True:
            if self.tasks:
                task, args = self.tasks.pop(0)
                try:
                    task(*args)
                except Exception as e:
                    print(e)
                    pass
            else:
                self.msleep(100)  # Sleep for 100ms when no tasks are available

    def add_task(self, task, *args):
        self.tasks.append((task, args))

# All the calculations and data manipulations happen here.
class store(QObject):
    show_snackbar = Signal(str)
    stop_calibration_timer = Signal()
    
    # Single simulation
    single_simulation_start = Signal(object)
    single_simulation_progress = Signal(object)
    single_simulation_end = Signal(object)
    single_simulation_error = Signal(object)
    
    # Calibration
    calibration_start = Signal(object)
    calibration_progress = Signal(object)
    calibration_end = Signal(object)
    calibration_error = Signal(object)
    calibration_abort = Signal(object)
    
    fetch_available_optimizers_start = Signal()
    fetch_available_optimizers_end = Signal(object)
    
    fetch_available_simulators_start = Signal()
    fetch_available_simulators_end = Signal(object)
    
    # User
    validate_user_start = Signal(object)
    validate_user_end = Signal(object)

    # Project
    active_project_change_start = Signal(object)
    active_project_change_end = Signal(object)
    fetch_projects_start = Signal(object)
    fetch_projects_end = Signal(object)
    create_project_start = Signal(object)
    create_project_end = Signal(object)
    create_project_directories_start = Signal(object)
    create_project_directories_end = Signal(object)
    
    # Model
    active_model_change_start = Signal(object)
    active_model_change_end = Signal(object)
    fetch_models_start = Signal(object)
    fetch_models_end = Signal(object)
    create_model_start = Signal(object)
    create_model_end = Signal(object)
    fetch_model_templates_start = Signal()
    fetch_model_templates_end = Signal(object)
    create_model_directories_start = Signal(object)
    create_model_directories_end = Signal(object)
    update_model_status_start = Signal(object)
    update_model_status_end = Signal(object)
    update_model_max_iteration_start = Signal(object)
    update_model_max_iteration_end = Signal(object)
    update_model_iteration_and_loss_start = Signal(object)
    update_model_iteration_and_loss_end = Signal(object)
    fetch_model_results_start = Signal()
    fetch_model_results_end = Signal()
    overwrite_calibration_results_start = Signal(object)
    overwrite_calibration_results_end = Signal(object)
    
    # Reference data
    fetch_available_reference_data_start = Signal(object)
    fetch_available_reference_data_end = Signal(object)
    add_available_reference_data_start = Signal(object)
    add_available_reference_data_end = Signal(object)
    update_reference_data_id_start = Signal(object)
    update_reference_data_id_end = Signal(object)
    
    # Parameters
    fetch_available_parameters_start = Signal(object)
    fetch_available_parameters_end = Signal(object)
    add_available_parameters_start = Signal(object)
    add_available_parameters_end = Signal(object)
    update_parameters_id_start = Signal(object)
    update_parameters_id_end = Signal(object)
    
    # Model files
    fetch_available_model_files_start = Signal(object)
    fetch_available_model_files_end = Signal(object)
    add_available_model_file_start = Signal(object)
    add_available_model_file_end = Signal(object)
    update_model_file_id_start = Signal(object)
    update_model_file_id_end = Signal(object)
    update_model_template_start = Signal(object)
    update_model_template_end = Signal(object)
    
    # Testbenches
    fetch_available_testbenches_start = Signal(object)
    fetch_available_testbenches_end = Signal(object)
    add_available_testbenches_start = Signal(object)
    add_available_testbenches_end = Signal(object)
    update_testbenches_id_start = Signal(object)
    update_testbenches_id_end = Signal(object)
    
    # Optimization settings
    create_optimization_settings_file_start = Signal(object)
    create_optimization_settings_file_end = Signal(object)
    update_optimization_settings_id_start = Signal(object)
    update_optimization_settings_id_end = Signal(object)
    fetch_optimization_settings_start = Signal(object)
    fetch_optimization_settings_end = Signal(object)
    
    # Single simulation results
    create_single_simulation_results_file_start = Signal()
    create_single_simulation_results_file_end = Signal(object)
    update_single_simulation_results_start = Signal()
    update_single_simulation_results_end = Signal()
    update_single_simulation_results_id_start = Signal(object)
    update_single_simulation_results_id_end = Signal(object)
    fetch_single_simulation_results_files_start = Signal(object)
    fetch_single_simulation_results_files_end = Signal(object)
    
    # Calibration results
    create_calibration_results_file_start = Signal()
    create_calibration_results_file_end = Signal(object)
    update_calibration_results_file_start = Signal()
    update_calibration_results_file_end = Signal(object)
    update_calibration_results_start = Signal()
    update_calibration_results_end = Signal()
    update_calibration_results_id_start = Signal(object)
    update_calibration_results_id_end = Signal(object)
    fetch_calibration_results_files_start = Signal(object)
    fetch_calibration_results_files_end = Signal(object)
    
    def __init__(self, db_type: str = 'local_files', style: style = None,
                 on_query_success: callable = None, on_query_error: callable = None):
        super().__init__()
        
        self.db_type = db_type
        self.style = style

        if self.db_type == 'local_files':
            self.set_local_paths()
        elif self.db_type == 'local_mysql_db':
            self.db = db()
            self.db.connect_to_db()
            self.projects_directory_path = projects_path

        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.REQ)
        self.socket.connect("tcp://localhost:5555")
        
        self.reset_user()
        
        self.projects = pd.DataFrame()
        self.reset_active_project()
        
        self.models = pd.DataFrame()
        self.reset_active_model()
    
        self.reset_available_model_data()        
        self.reset_model_data()
                
        self.start_dm_thread()
        
    #%% Properties
    @property
    def reference_data(self):
        return self._reference_data

    @reference_data.setter
    def reference_data(self, value):
        if value is None:
            self._reference_data = None
            self.loss_function_groups = []
        elif self._reference_data != value:
            self._reference_data = value
            self.loss_function_groups = self._reference_data.group_types
            
    @property
    def model_template(self):
        return self._model_template

    @model_template.setter
    def model_template(self, value):
        if value is None:
            self._model_template = None
            self.update_model_template(self._model_template, self.active_model['id'])
        elif self._model_template != value:
            self._model_template = value
            self.update_model_template(self._model_template, self.active_model['id'])
    
    #%% Data management thread
    def start_dm_thread(self):
        self.dm_thread = dm_thread()
        self.dm_thread.start()
        
    def cleanup_dm_thread(self):
        self.dm_thread.quit()
        # self.dm_thread.wait()
                
    def _run_task(self, task, *args):
        self.dm_thread.add_task(task, *args)
    
    #%% Reset functions
    def set_local_paths(self):
        self.users_path = Path.joinpath(dummy_data_path, 'users.csv')
        self.projects_path = Path.joinpath(dummy_data_path, 'projects.csv')
        self.models_path = Path.joinpath(dummy_data_path, 'models.csv')
        self.available_reference_data_path = Path.joinpath(dummy_data_path, 'reference_data_files.csv')
        self.available_parameters_path = Path.joinpath(dummy_data_path, 'parameters_files.csv')
        self.available_model_files_path = Path.joinpath(dummy_data_path, 'model_files.csv')
        self.available_testbenches_path = Path.joinpath(dummy_data_path, 'testbenches_files.csv')
        self.available_loss_function_path = Path.joinpath(dummy_data_path, 'loss_function_files.csv')
        self.available_optimizers_path = Path.joinpath(dummy_data_path, 'optimizers.csv')
        self.available_simulators_path = Path.joinpath(dummy_data_path, 'simulators.csv')
        self.single_simulation_results_files_path = Path.joinpath(dummy_data_path, 'single_simulation_results_files.csv')
        self.calibration_results_files_path = Path.joinpath(dummy_data_path, 'calibration_results_files.csv')
        self.optimization_settings_files_path = Path.joinpath(dummy_data_path, 'optimization_settings_files.csv')
        self.projects_directory_path = projects_path
    
    def reset_user(self):
        self.user = None
        
    def reset_active_project(self):
        self.active_project = None
        self.active_project_directory = None
        self.active_project_common_reference_data_directory = None
        self.active_project_common_parameters_directory = None
        self.active_project_common_model_files_directory = None
        self.active_project_common_testbenches_directory = None
        self.active_project_common_loss_functions_directory = None
        
    def reset_active_model(self):
        self.active_model = None
        self.active_model_directory = None
        self.active_model_inputs_directory = None
        
    def reset_model_data(self):
        self.model_file_path = None
        self._model_template = None
        self.testbenches_path = None
        self.reference_data_path = None
        self._reference_data = None
        self.parameters_path = None
        self.parameters = None
        self.optimization_settings_path = None
        self.optimizers = None
        self.simulators = None
        self.loss_function = None
        self.loss_function_groups = []
        self.reset_simulation_variables()
        
    def reset_simulation_variables(self):
        self.simulation_input = None
        self.calibration_status = None
        self.optimizer_config = None
        self.simulator_config = None
        self.cost_function_config = None
        self.reset_calibration_results()
        self.reset_single_simulation_results()
        
    def reset_calibration_results(self):
        self.calibration_results = None
        self.calibration_results_survivors = None
        self.calibration_results_trials = None
        self.calibration_new_results = None
        
    def reset_model_calibration(self):             
        self.model_calibration_id = None
        self.model_calibration_running = False
        self.status_check_timer = None
        self.model_calibration_abort = False
        
    def reset_single_simulation_results(self):
        self.single_simulation_results = None
                
    def reset_available_model_data(self):
        self.model_templates = pd.DataFrame()        
        self.available_reference_data = pd.DataFrame()
        self.available_parameters = pd.DataFrame()
        self.available_loss_functions = pd.DataFrame()
        self.available_model_files = pd.DataFrame()
        self.available_testbenches = pd.DataFrame()
        self.single_simulation_results_files = pd.DataFrame()
        self.calibration_results_files = pd.DataFrame()
        self.available_optimizers = {}
        self.available_simulators = {}

    #%% Single simulation
    def init_single_simulation(self):
        self.single_simulation = single_simulation()
        self.single_simulation_timer = QTimer(self)
        self.single_simulation_timer.timeout.connect(self.check_single_simulation_status)
        self.single_simulation_timer.start(2000)
        
    def start_single_simulation(self, sync: bool = False):
        try:
            self.init_single_simulation()
            if self.single_simulation is not None:
                single_simulation_path = self.create_single_simulation_directory()
                shutil.copy(self.optimization_settings_path, Path.joinpath(single_simulation_path, 'inputs', Path(self.optimization_settings_path).name))
                self.compile_simulation_input(files_path = single_simulation_path)
                self.single_simulation.update_simulation_input(self.simulation_input)
                if sync:
                    self.single_simulation.run()
                else:
                    self.single_simulation.start()
                self.on_single_simulation_start({'model_id': self.active_model['id']})
        except Exception as e:
            print('ERROR at start_single_simulation!')
            print(e)
            
    def check_single_simulation_status(self):
        if not self.single_simulation.is_running():
            self.single_simulation_timer.stop()
        data = self.single_simulation.get_result()
        if data is not None:
            status = data['status']
            if status == 'error':
                self.on_single_simulation_error(data)
            elif status == 'finish':
                self.on_single_simulation_finish(data)
    
    def on_single_simulation_error(self, data):
        self.update_model_status('single simulation error', data['model_id'])
        self.single_simulation_error.emit(data)
        
    def on_single_simulation_start(self, data):
        self.update_model_status('single simulation in progress', data['model_id'])
        self.single_simulation_start.emit(data)

    def on_single_simulation_finish(self, data):
        model_id = data['model_id']
        results_dir = data['results_dir']
        results = data['results']
        loss = data['loss']
        self.update_model_status('single simulation finished', model_id)
        self.create_single_simulation_results_file(results = results,
                                                   path = Path.joinpath(results_dir, 'results.json'),
                                                   model_id = model_id)
        if model_id == self.active_model['id']:
            try:
                results['plot'] = self.single_simulation_results['plot'] # keep the plots if there were any before
            except:
                pass
            self.single_simulation_results = results
            # Keep only the columns that are important to show
            columns = list(self.reference_data.data.columns) + ['x_values_simulation', 'y_values_simulation']
            columns.remove('calibrate')
            columns.remove('include')
            self.single_simulation_results = self.single_simulation_results[columns]
        
        if self.single_simulation.is_running():
            self.single_simulation.terminate()
            
        self.single_simulation_end.emit({'model_id': model_id})
    
    def create_single_simulation_directory(self):
        timestamp = get_current_timestamp()
        model_path = Path(self.active_model['path'])
        
        single_simulation_path = Path.joinpath(model_path, f'single_simulation_{timestamp}')
        if not Path.exists(single_simulation_path):
            Path.mkdir(single_simulation_path)
            
        simulation_files_path = Path.joinpath(single_simulation_path, 'simulation_files')
        if not Path.exists(simulation_files_path):
            Path.mkdir(simulation_files_path)
            
        results_path = Path.joinpath(single_simulation_path, 'results')
        if not Path.exists(results_path):
            Path.mkdir(results_path)
        
        inputs_path = Path.joinpath(single_simulation_path, 'inputs')
        if not Path.exists(inputs_path):
            Path.mkdir(inputs_path)
        
        return single_simulation_path

    #%% Calibration
    def check_calibration_status(self, sync: bool = False):
        if sync:
            self._check_calibration_status()
        else:
            self._run_task(self._check_calibration_status)
    
    def _check_calibration_status(self):
        print('_check_calibration_status')
        if hasattr(self, 'model_calibration_id'):
            message = {
                'command': 'check_calibration_status',
                'calibration_id': self.model_calibration_id
            }
            self.socket.send(pickle.dumps(message))
            response = pickle.loads(self.socket.recv())
            if response is not None:
                status = response['status']
                if status == 'error':
                    self.on_calibration_error(response)
                elif status == 'progress' and not self.model_calibration_abort:
                    self.on_calibration_progress(response)
                elif status == 'finish':
                    self.on_calibration_finish(response)
    
    def start_calibration(self, emit_signals: bool = True, sync: bool = True):
        if sync:
            self._start_calibration(emit_signals)
        else:
            self._run_task(self._start_calibration, emit_signals)
    
    def _start_calibration(self, emit_signals: bool = True):
        self.reset_model_calibration()
        calibration_path = self.create_calibration_directory()
        shutil.copy(self.optimization_settings_path, Path.joinpath(calibration_path, 'inputs', Path(self.optimization_settings_path).name))
        self.compile_simulation_input(files_path = calibration_path)        
        calibration_id = copy(self.active_model['id'])
        message = {
            'command': 'start_calibration',
            'calibration_id': calibration_id,
            'simulation_input': self.simulation_input
        }
        self.socket.send(pickle.dumps(message))
        response = pickle.loads(self.socket.recv())
        if response['status'] == 'calibration_started':
            self.model_calibration_id = calibration_id
            self.on_calibration_start(self.simulation_input)
            self.start_status_check_timer()
            
    def on_calibration_start(self, data, emit_signals: bool = True):
        self._run_task(self._on_calibration_start, data)
    
    def _on_calibration_start(self, data, emit_signals: bool = True):
        self.reset_calibration_results()
        self.model_calibration_running = True
        self.update_model_status('starting calibration', data['model_id'])
        if emit_signals:
            self.calibration_start.emit(data)
            
    def start_status_check_timer(self):
        if self.status_check_timer is None:
            self.status_check_timer = QTimer(self)
            self.status_check_timer.timeout.connect(self.check_calibration_status)
            self.stop_calibration_timer.connect(self.status_check_timer.stop)
        self.status_check_timer.start(2000)

    def stop_status_check_timer(self):
        if self.status_check_timer is not None:
            self.stop_calibration_timer.emit()
            self.status_check_timer = None
        
    def abort_calibration(self, emit_signals: bool = True, sync: bool = False):
        if sync:
            self._abort_calibration(emit_signals)
        else:
            self._run_task(self._abort_calibration, emit_signals)
    
    def _abort_calibration(self, emit_signals: bool = True):
        if hasattr(self, 'model_calibration_id'):
            message = {
                'command': 'abort_calibration',
                'calibration_id': self.model_calibration_id
            }
            self.socket.send(pickle.dumps(message))
            response = pickle.loads(self.socket.recv())
            if response['status'] == 'calibration_abort_sent':
                self.model_calibration_abort = True
                self.on_calibration_abort({'model_id': self.active_model['id']})
                    
    def on_calibration_abort(self, data, emit_signals: bool = True):
        self._run_task(self._on_calibration_abort, data)
    
    def _on_calibration_abort(self, data, emit_signals: bool = True):
        self.update_model_status('aborting calibration', data['model_id'])
        if emit_signals:
            self.calibration_abort.emit(data)
    
    def on_calibration_progress(self, data, emit_signals: bool = True):
        self._run_task(self._on_calibration_progress, data, emit_signals)
    
    def _on_calibration_progress(self, data, emit_signals: bool = True):
        model_id = data['model_id']
        iteration = data['iteration']
        max_iterations = data['max_iterations']
        best_loss = data['best_loss']
        best_results = data['best_results']
        better_solution_found = data['better_solution_found']
        results_dir = data['results_dir']
        self.calibration_results_survivors = data['survivors']
        self.calibration_results_trials = data['trials']
    
        self.update_model_status('calibration in progress', model_id)
        self.update_model_iteration_and_loss(iteration, best_loss, model_id)
        
        if iteration == 1 or self.calibration_results is None:
            self.create_calibration_results_file(results = best_results,
                                                 path = Path.joinpath(results_dir, 'results.json'),
                                                 model_id = model_id)
            if model_id == self.active_model['id']:
                try:
                    best_results['plot'] = self.calibration_results['plot']
                except:
                    pass
                self.calibration_results = best_results
                # Keep only the columns that are important to show
                columns = list(self.reference_data.data.columns) + ['x_values_simulation', 'y_values_simulation']
                columns.remove('calibrate')
                columns.remove('include')
                self.calibration_results = self.calibration_results[columns]
        elif better_solution_found and iteration > 1:
            self.update_calibration_results_file(results = best_results,
                                                 path = Path.joinpath(results_dir, 'results.json'),
                                                 model_id = model_id)  
            if model_id == self.active_model['id']:
                self.calibration_new_results = best_results            
                # Keep only the columns that are important to show
                columns = list(self.reference_data.data.columns) + ['x_values_simulation', 'y_values_simulation']
                columns.remove('calibrate')
                columns.remove('include')
                self.calibration_new_results = self.calibration_new_results[columns]
        
        if emit_signals:
            self.calibration_progress.emit({'model_id': model_id, 'iteration': iteration, 'max_iterations': max_iterations,
                                            'best_loss': best_loss, 'better_solution_found': better_solution_found})

    def on_calibration_finish(self, data, emit_signals: bool = True, sync: bool = False):
        if sync:
            self._on_calibration_finish(data, emit_signals)
        else:
            self._run_task(self._on_calibration_finish, data, emit_signals)

    def _on_calibration_finish(self, data, emit_signals: bool = True):
        self.stop_calibration_timer.emit()
        model_id = data['model_id']
        # iteration = data['iteration']
        # max_iterations = data['max_iterations']
        # best_loss = data['best_loss']
        # best_results = data['best_results']
        # better_solution_found = data['better_solution_found']
        # results_dir = data['results_dir']
        stop_reason = data['stop_reason']
        status = 'calibration aborted' if stop_reason == 'optimization aborted' else 'calibration finished'
        self.calibration_results_survivors = data['survivors']
        self.calibration_results_trials = data['trials']
        self.update_model_status(status, model_id)
        if emit_signals:
            self.calibration_end.emit(data)
    
    def on_calibration_error(self, data, emit_signals: bool = True):
        self._run_task(self._on_calibration_error, data, emit_signals)
    
    def _on_calibration_error(self, data, emit_signals: bool = True):
        print(data)
        self.update_model_status('calibration error', data['model_id'])
        self.stop_calibration_timer.emit()
        if emit_signals:
            self.calibration_error.emit(data)

    def create_calibration_directory(self):
        timestamp = get_current_timestamp()
        model_path = Path(self.active_model['path'])
        
        calibration_path = Path.joinpath(model_path, f'calibration_{timestamp}')
        if not Path.exists(calibration_path):
            Path.mkdir(calibration_path)
            
        simulation_files_path = Path.joinpath(calibration_path, 'simulation_files')
        if not Path.exists(simulation_files_path):
            Path.mkdir(simulation_files_path)
            
        results_path = Path.joinpath(calibration_path, 'results')
        if not Path.exists(results_path):
            Path.mkdir(results_path)
        
        inputs_path = Path.joinpath(calibration_path, 'inputs')
        if not Path.exists(inputs_path):
            Path.mkdir(inputs_path)
        
        return calibration_path

    #%% Optimizers
    def fetch_available_optimizers(self, emit_signals: bool = True):
        self._run_task(self._fetch_available_optimizers, emit_signals)
        
    def _fetch_available_optimizers(self, emit_signals: bool = True):
        if emit_signals:
            self.fetch_available_optimizers_start.emit()
        
        success = True
        error = None
        available_optimizers = None
        
        if self.db_type == 'local_files':
            available_optimizers = pd.read_csv(filepath_or_buffer = self.available_optimizers_path,
                                               converters = {'file_type': convert_to_list_if_semi_colon},
                                               na_values = ['null', 'Null', 'None', 'none'])
        elif self.db_type == 'local_mysql_db':
            db_response = self.db.fetch_optimizers()
            if db_response['success']:
                available_optimizers = db_response['data']
                if 'file_type' in available_optimizers.columns:
                    available_optimizers['file_type'] = available_optimizers['file_type'].apply(convert_to_list_if_semi_colon)
            else:
                success = False
                error = db_response['error']
                
        if success:
            self.available_optimizers = available_optimizers
                
        if emit_signals:
            self.fetch_available_optimizers_end.emit({'success': success, 'error': error, 'data': available_optimizers})
    
    def parse_available_optimizers_to_dict(self):
        optimizers_dict = {}
        optimizers_grouped = self.available_optimizers.groupby('optimizer')
        for optimizer, group in optimizers_grouped:
            optimizers_dict[optimizer] = group.set_index('name')['default'].to_dict()
        return optimizers_dict
            
    
    #%% Simulators
    def fetch_available_simulators(self, emit_signals: bool = True):
        self._run_task(self._fetch_available_simulators, emit_signals)
        
    def _fetch_available_simulators(self, emit_signals: bool = True):
        if emit_signals:
            self.fetch_available_simulators_start.emit()
        
        success = True
        error = None
        available_simulators = None
        
        if self.db_type == 'local_files':
            available_simulators = pd.read_csv(filepath_or_buffer = self.available_simulators_path,
                                               converters = {'file_type': convert_to_list_if_semi_colon},
                                               na_values = ['null', 'Null', 'None', 'none'])
        elif self.db_type == 'local_mysql_db':
            db_response = self.db.fetch_simulators()
            if db_response['success']:
                available_simulators = db_response['data']
            else:
                success = False
                error = db_response['error']
                
        if success:
            self.available_simulators = available_simulators
                
        if emit_signals:
            self.fetch_available_simulators_end.emit({'success': success, 'error': error, 'data': available_simulators})
    
    def parse_available_simulators_to_dict(self):
        simulators_dict = {}
        simulators_grouped = self.available_simulators.groupby('simulator')
        for simulator, group in simulators_grouped:
            simulators_dict[simulator] = group.set_index('name')['default'].to_dict()
        return simulators_dict
    
    #%% Users
    def validate_user(self, username: str = None, password: str = None, emit_signals: bool = True):
        self._run_task(self._validate_user, username, password, emit_signals)
        
    def _validate_user(self, username: str = None, password: str = None, emit_signals: bool = True):
        if emit_signals:
            self.validate_user_start.emit({'username': username, 'password': password})
        
        success = True
        error = None
        user = None
        
        if username is None:
            success = False
            error = 'username is None!'
        elif password is None:
            success = False
            error = 'password is None!'
        elif self.db_type == 'local_files':
            all_users = pd.read_csv(self.users_path)
            user = all_users[(all_users['username'] == username) & (all_users['password'] == password)]
        elif self.db_type == 'local_mysql_db':
            db_response = self.db.fetch_user_by_username_and_password(username, password)
            if db_response['success']:
                user = db_response['data']
            else:
                success = False
                error = db_response['error']
                
        if success:
            if user.empty:
                success = False
                error = 'No user matches the username and password given! Please contact aivalanche support for further information!'
            elif len(user.index) > 1:
                success = False
                error = 'More than 1 user matches the username and password given! Please contact aivalanche support for further information!'
            else:
                user = user.squeeze()
                self.user = user
                
        if emit_signals:
            self.validate_user_end.emit({'success': success, 'error': error, 'data': user})

    #%% Projects
    def set_active_project(self, p: pd.Series = None, emit_signals: bool = True):
        if p is None and self.active_project is None:
            return
        
        if self.active_project is not None and self.active_project['id'] == p['id']:
            return
        
        if emit_signals:
            self.active_project_change_start.emit({'active_project': self.active_project})
            
        if p is None:
            self.reset_active_project()
        else:
            self.active_project = p
            self.active_project_directory = Path(p['path'])
            self.active_project_common_reference_data_directory = Path.joinpath(self.active_project_directory, 'common', 'reference_data')
            self.active_project_common_parameters_directory = Path.joinpath(self.active_project_directory, 'common', 'parameters')
            self.active_project_common_model_files_directory = Path.joinpath(self.active_project_directory, 'common', 'model_files')
            self.active_project_common_testbenches_directory = Path.joinpath(self.active_project_directory, 'common', 'testbenches')
            self.active_project_common_loss_functions_directory = Path.joinpath(self.active_project_directory, 'common', 'loss_functions')
        
        if emit_signals:
            self.active_project_change_end.emit({'active_project': self.active_project})

    def fetch_projects(self, emit_signals: bool = True):
        self._run_task(self._fetch_projects, emit_signals)

    def _fetch_projects(self, emit_signals: bool = True):
        if emit_signals:
            self.fetch_projects_start.emit({'user': self.user})

        success = True
        error = None
        projects = None
        
        if self.user is None:
            success = False
            error = 'User is None!'
        else:
            user_id = self.user['id']
            if self.db_type == 'local_files':
                all_projects = pd.read_csv(self.projects_path)
                projects = all_projects[(all_projects['user_id'] == user_id)]
                projects.loc[:,'created_at'] = pd.to_datetime(projects['created_at'])
                projects.loc[:,'last_modified_at'] = pd.to_datetime(projects['last_modified_at'])
                projects.sort_values(by = 'created_at', ascending = False, inplace = True, ignore_index = True)
            elif self.db_type == 'local_mysql_db':
                db_response = self.db.fetch_projects_by_user_id(user_id)
                if db_response['success']:
                    projects = db_response['data']
                else:
                    success = False
                    error = db_response['error']
        
        if success:
            self.projects = projects
        
        if emit_signals:
            self.fetch_projects_end.emit({'success': success, 'error': error, 'data': projects})
    
    def create_project(self, title: str = None, emit_signals: bool = True):
        self._run_task(self._create_project, title, emit_signals)

    def _create_project(self, title: str = None, emit_signals: bool = True):
        if emit_signals:
            self.create_project_start.emit({'title': title})
            
        success = True
        error = None
        data = None
        
        if title is None:
            success = False
            error = 'Title is None!'
        else:
            if not self.projects.empty and title in self.projects['title'].tolist():
                success = False
                error = f'You already have a project called {title}. Please specify a different title.'
            else:
                user_id = self.user['id']
                if self.db_type == 'local_files':
                    current_time = datetime.now()
                    formatted_time = current_time.strftime('%Y-%m-%d %H:%M:%S')
                    all_projects = pd.read_csv(self.projects_path)
                    new_project = pd.DataFrame.from_dict([{'id': str(uuid.uuid4()),
                                                           'user_id': user_id,
                                                           'created_at': formatted_time,
                                                           'last_modified_at': formatted_time,
                                                           'title': title,
                                                           'labels': ''}])
                    all_projects = pd.concat((all_projects, new_project))
                    all_projects.to_csv(path_or_buf = self.projects_path, index = False)
                    data = {'user_id': user_id, 'title': title}
                elif self.db_type == 'local_mysql_db':
                    db_response = self.db.create_project_by_user_id(user_id, title)
                    if db_response['success']:
                        data = db_response['data']
                    else:
                        success = False
                        error = db_response['error']
                    
            if success:
                self._fetch_projects(emit_signals = False)
                self._create_project_directories(title)
                self._fetch_projects(emit_signals = False)
        
        if emit_signals:
            self.create_project_end.emit({'success': success, 'error': error, 'data': data})
        
    def create_project_directories(self, title: str = None, emit_signals: bool = True):
        self._run_task(self._create_project_directories, title, emit_signals)
        
    def _create_project_directories(self, title: str = None, emit_signals: bool = True):
        if emit_signals:
            self.create_project_directories_start.emit({'title': title})
        
        success = True
        error = None
        data = None
        
        if title is None:
            success = False
            error = 'Title is None!'
        else:
            if self.db_type in ['local_files', 'local_mysql_db']:
                project = filter_df_by_col_name_and_val(df = self.projects, col_name = 'title', val = title)
                if len(project.index) == 0:
                    success = False
                    error = f'No project titled {title} exists!'
                else:
                    username = self.user['username']
                    project_id = project['id']
                    project_path = Path.joinpath(self.projects_directory_path, f'{replace_space_with_underline(title)}.{username}.{project_id}')
                    project_models_path = Path.joinpath(project_path, 'models')
                    project_common_path = Path.joinpath(project_path, 'common')
                    project_common_models_path = Path.joinpath(project_common_path, 'model_files')
                    project_common_parameters_path = Path.joinpath(project_common_path, 'parameters')
                    project_common_reference_data_path = Path.joinpath(project_common_path, 'reference_data')
                    project_common_testbenches_path = Path.joinpath(project_common_path, 'testbenches')
                    project_common_loss_functions_path = Path.joinpath(project_common_path, 'loss_functions')
                    try:
                        Path.mkdir(project_path)
                        Path.mkdir(project_models_path)
                        Path.mkdir(project_common_path)
                        Path.mkdir(project_common_models_path)
                        Path.mkdir(project_common_parameters_path)
                        Path.mkdir(project_common_reference_data_path)
                        Path.mkdir(project_common_testbenches_path)
                        Path.mkdir(project_common_loss_functions_path)
                        if self.db_type == 'local_files':
                            all_projects = pd.read_csv(self.projects_path)
                            all_projects.loc[all_projects['id'] == project_id, 'path'] = project_path
                            all_projects.to_csv(path_or_buf = self.projects_path, index = False)
                        elif self.db_type == 'local_mysql_db':
                            db_response = self.db.update_project_path_by_id(project_id = project_id, path = project_path)
                            if db_response['success']:
                                data = db_response['data']
                            else:
                                success = False
                                error = db_response['error']                        
                    except FileExistsError:
                        success = False
                        error = f'{project_path} already exists!'
                    except FileNotFoundError:
                        success = False
                        error = f'{project_path} cannot be created because one of the parent directories does not exist!'
                        
        if emit_signals:
            self.create_project_directories_end.emit({'success': success, 'error': error, 'data': data})
        
    #%% Models
    def set_active_model(self, m: pd.Series = None, override: bool = False, emit_signals: bool = True, sync = True):
        if sync:
            self._set_active_model(m, override, emit_signals)
        else:
            self._run_task(self._set_active_model, m, override, emit_signals)
    
    def _set_active_model(self, m: pd.Series = None, override: bool = False, emit_signals: bool = True):        
        if m is None and self.active_model is None:
            return
                
        if self.active_model is not None and m is not None and self.active_model['id'] == m['id'] and not override:
            return
        
        if emit_signals:
            self.active_model_change_start.emit({'active_model': self.active_model})
            
        if m is None:
            self.reset_active_model()
            self.reset_model_data()
        else:
            self.active_model = m
            self.active_model_directory = Path(m['path'])
            self.active_model_inputs_directory = Path.joinpath(self.active_model_directory, 'inputs')
            if pd.isnull(self.active_model['optimization_settings_id']):
                self.create_optimization_settings_file()
            else:
                if not override:
                    self.fetch_optimization_settings(sync = False)
                    self.fetch_model_results(model_id = self.active_model['id'])
        if emit_signals:
            self.active_model_change_end.emit({'active_model': self.active_model})
    
    def fetch_model_templates(self, emit_signals: bool = True):
        self._run_task(self._fetch_model_templates, emit_signals)
        
    def _fetch_model_templates(self, emit_signals: bool = True):
        if emit_signals:
            self.fetch_model_templates_start.emit()
        
        success = True
        error = None
        if self.db_type == 'local_files':
            self.model_templates = pd.read_csv(Path.joinpath(dummy_data_path, 'model_templates.csv'))
        elif self.db_type == 'local_mysql_db':
            db_response = self.db.fetch_model_templates()
            if db_response['success']:
                self.model_templates = db_response['data']
            else:
                success = False
                error = db_response['error']
                
        if emit_signals:
            self.fetch_model_templates_end.emit({'success': success, 'error': error, 'data': self.model_templates})
    
    def fetch_models(self, emit_signals: bool = True, sync: bool = False):
        if sync:
            self._fetch_models(emit_signals)
        else:
            self._run_task(self._fetch_models, emit_signals)
 
    def _fetch_models(self, emit_signals: bool = True):
        if emit_signals:
            self.fetch_models_start.emit({'project': self.active_project})
            
        success = True
        error = None
        models = None
        
        if self.active_project is None:
            success = False
            error = 'active_project is None!'
        else:
            project_id = self.active_project['id']
            if self.db_type == 'local_files':
                all_models = pd.read_csv(self.models_path)
                models = all_models[(all_models['project_id'] == project_id)]
                models.loc[:,'created_at'] = pd.to_datetime(models['created_at'])
                models.loc[:,'last_modified_at'] = pd.to_datetime(models['last_modified_at'])
                models_sorted = models.sort_values(by = 'created_at', ascending = False, ignore_index = True)
                models = models_sorted
            elif self.db_type == 'local_mysql_db':
                db_response = self.db.fetch_models_by_project_id(project_id)
                if db_response['success']:
                    models = db_response['data']
                else:
                    success = False
                    error = db_response['error']
        
        if success:
            self.models = models
        
        if emit_signals:
            self.fetch_models_end.emit({'success': success, 'error': error, 'data': models})
    
    def create_model(self, title: str = None, emit_signals: bool = True):
        self._run_task(self._create_model, title, emit_signals)    

    def _create_model(self, title: str = None, emit_signals: bool = True):
        if emit_signals:
            self.create_model_start.emit({'title': title})
            
        success = True
        error = None
        data = None
        
        if title is None:
            success = False
            error = 'Title is None!'
        else:
            if not self.models.empty and title in self.models['title'].tolist():
                success = False
                error = f'You already have a model called {title}. Please specify a different title.'
            else:
                project_id = self.active_project['id']
                if self.db_type == 'local_files':
                    current_time = datetime.now()
                    formatted_time = current_time.strftime('%Y-%m-%d %H:%M:%S')
                    all_models = pd.read_csv(self.models_path)
                    new_model = pd.DataFrame.from_dict([{'id': str(uuid.uuid4()),
                                                         'project_id': project_id,
                                                         'created_at': formatted_time,
                                                         'last_modified_at': formatted_time,
                                                         'title': title,
                                                         'status': 'setup',
                                                         'max_iterations': 1000,
                                                         'iter': 0,
                                                         'labels': ''}])
                    all_models = pd.concat((all_models, new_model))
                    all_models.to_csv(path_or_buf = self.models_path, index = False)
                elif self.db_type == 'local_mysql_db':
                    db_response = self.db.create_model_by_project_id(project_id, title)
                    if db_response['success']:
                        data = db_response['data']
                    else:
                        success = False
                        error = db_response['error']
            
            if success:
                self._fetch_models(emit_signals = False)
                self._create_model_directories(title)
                self._fetch_models(emit_signals = False)

        if emit_signals:
            self.create_model_end.emit({'success': success, 'error': error, 'data': data})

    def create_model_directories(self, title: str = None, emit_signals: bool = True):
        self._run_task(self._create_model_directories, title, emit_signals)
        
    def _create_model_directories(self, title: str = None, emit_signals: bool = True):
        if emit_signals:
            self.create_model_directories_start.emit({'title': title})
        
        success = True
        error = None
        data = None
        
        if title is None:
            success = False
            error = 'Title is None!'
        else:
            if self.db_type in ['local_files', 'local_mysql_db']:
                model = filter_df_by_col_name_and_val(df = self.models, col_name = 'title', val = title)
                if len(model.index) == 0:
                    success = False
                    error = f'No model titled {title} exists!'
                else:
                    model_id = model['id']
                    project_path = Path(self.active_project['path'])
                    model_path = Path.joinpath(project_path, 'models', f'{replace_space_with_underline(title)}.{model_id}')
                    inputs_path = Path.joinpath(model_path, 'inputs')
                    try:
                        Path.mkdir(model_path)
                        Path.mkdir(inputs_path)
                        if self.db_type == 'local_files':
                            all_models = pd.read_csv(self.models_path)
                            all_models.loc[all_models['id'] == model_id, 'path'] = model_path
                            all_models.to_csv(path_or_buf = self.models_path, index = False)
                        elif self.db_type == 'local_mysql_db':
                            db_response = self.db.update_model_path_by_id(model_id = model_id, path = model_path)
                            if db_response['success']:
                                data = db_response['data']
                            else:
                                success = False
                                error = db_response['error']
                                
                    except FileExistsError:
                        success = False
                        error = f'{model_path} already exists!'
                    except FileNotFoundError:
                        success = False
                        error = f'{model_path} cannot be created because one of the parent directories does not exist!'
                
        if emit_signals:
            self.create_model_directories_end.emit({'success': success, 'error': error, 'data': data})
    
    def update_model_status(self, status: str = None, model_id: str = None, emit_signals: bool = True):
        self._run_task(self._update_model_status, status, model_id, emit_signals)
        
    def _update_model_status(self, status: str = None, model_id: str = None, emit_signals: bool = True):
        if emit_signals:
            self.update_model_status_start.emit({'status': status, 'model_id': model_id})
        
        success = True
        error = None
        data = None
        
        if model_id is None:
            success = False
            error = 'model_id is None!'
        else:
            if self.db_type == 'local_files':
                all_models = pd.read_csv(self.models_path)
                all_models.loc[all_models['id'] == model_id, 'status'] = status
                all_models.to_csv(path_or_buf = self.models_path, index = False)
                self.models.loc[self.models['id'] == model_id, 'status'] = status
                if self.active_model is not None and self.active_model['id'] == model_id:
                    self.set_active_model(self.models[self.models['id'] == model_id].squeeze(), override = True, emit_signals = False)
            elif self.db_type == 'local_mysql_db':
                db_response = self.db.update_model_status_by_id(model_id, status)
                if db_response['success']:
                    data = db_response['data']
                    self.models.loc[self.models['id'] == model_id, 'status'] = status
                    if self.active_model is not None and self.active_model['id'] == model_id:
                        self.set_active_model(self.models[self.models['id'] == model_id].squeeze(), override = True, emit_signals = False)
                else:
                    success = False
                    error = db_response['error']
        
        if emit_signals:
            self.update_model_status_end.emit({'success': success, 'error': error, 'model_id': model_id, 'data': data})
            
    def update_model_max_iteration(self, max_iteration: str = None, model_id: str = None, emit_signals: bool = True):
        self._run_task(self._update_model_max_iteration, max_iteration, model_id, emit_signals)
        
    def _update_model_max_iteration(self, max_iteration: str = None, model_id: str = None, emit_signals: bool = True):
        if emit_signals:
            self.update_model_max_iteration_start.emit({'max_iteration': max_iteration, 'model_id': model_id})
        
        success = True
        error = None
        data = None
        
        if model_id is None:
            success = False
            error = 'model_id is None!'
        else:
            if self.db_type == 'local_files':
                all_models = pd.read_csv(self.models_path)
                all_models.loc[all_models['id'] == model_id, 'max_iteration'] = max_iteration
                all_models.to_csv(path_or_buf = self.models_path, index = False)
                self.models.loc[self.models['id'] == model_id, 'max_iteration'] = max_iteration
                if self.active_model is not None and self.active_model['id'] == model_id:
                    self.set_active_model(self.models[self.models['id'] == model_id].squeeze(), override = True, emit_signals = False)
            elif self.db_type == 'local_mysql_db':
                db_response = self.db.update_model_max_iteration_by_id(model_id, max_iteration)
                if db_response['success']:
                    data = db_response['data']
                    self.models.loc[self.models['id'] == model_id, 'max_iteration'] = max_iteration
                    if self.active_model is not None and self.active_model['id'] == model_id:
                        self.set_active_model(self.models[self.models['id'] == model_id].squeeze(), override = True, emit_signals = False)
                else:
                    success = False
                    error = db_response['error']
        
        if emit_signals:
            self.update_model_max_iteration_end.emit({'success': success, 'error': error, 'model_id': model_id, 'data': data})
            
    def update_model_iteration_and_loss(self, iteration: int = None, loss: float = None, model_id: str = None, emit_signals: bool = True):
        self._run_task(self._update_model_iteration_and_loss, iteration, loss, model_id, emit_signals)
        
    def _update_model_iteration_and_loss(self, iteration: int = None, loss: float = None, model_id: str = None, emit_signals: bool = True):
        if emit_signals:
            self.update_model_iteration_and_loss_start.emit({'iteration': iteration, 'loss': loss, 'model_id': model_id})
        
        success = True
        error = None
        data = None
        
        if model_id is None:
            success = False
            error = 'model_id is None!'
        else:
            if self.db_type == 'local_files':
                all_models = pd.read_csv(self.models_path)
                all_models.loc[all_models['id'] == model_id, 'iteration'] = iteration
                all_models.loc[all_models['id'] == model_id, 'loss'] = loss
                all_models.to_csv(path_or_buf = self.models_path, index = False)
                self.models.loc[self.models['id'] == model_id, 'iteration'] = iteration
                self.models.loc[self.models['id'] == model_id, 'loss'] = loss
                if self.active_model is not None and self.active_model['id'] == model_id:
                    self.set_active_model(self.models[self.models['id'] == model_id].squeeze(), override = True, emit_signals = False)
            elif self.db_type == 'local_mysql_db':
                db_response = self.db.update_model_iteration_and_loss_by_id(model_id, iteration, loss)
                if db_response['success']:
                    data = db_response['data']
                    self.models.loc[self.models['id'] == model_id, 'iteration'] = iteration
                    self.models.loc[self.models['id'] == model_id, 'loss'] = loss
                    if self.active_model is not None and self.active_model['id'] == model_id:
                        self.set_active_model(self.models[self.models['id'] == model_id].squeeze(), override = True, emit_signals = False)
                else:
                    success = False
                    error = db_response['error']
        
        if emit_signals:
            self.update_model_iteration_and_loss_end.emit({'success': success, 'error': error, 'model_id': model_id, 'data': data})

    def fetch_model_results(self, model_id: str = None, emit_signals: bool = True, sync: bool = False):
        if sync:
            self._fetch_model_results(model_id, emit_signals)
        else:
            self._run_task(self._fetch_model_results, emit_signals)
        
    def _fetch_model_results(self, model_id: str = None, emit_signals: bool = True):
        if emit_signals:
            self.fetch_model_results_start.emit()
            
        self._fetch_calibration_results_files(model_id = model_id, emit_signals = False)
        self._fetch_single_simulation_results_files(model_id = model_id, emit_signals = False)
        
        if emit_signals:
            self.fetch_model_results_end.emit()
        
    #%% Reference data files
    def fetch_available_reference_data(self, project_id: str = None, emit_signals: bool = True):
        self._run_task(self._fetch_available_reference_data, project_id, emit_signals)
        
    def _fetch_available_reference_data(self, project_id: str = None, emit_signals: bool = True):
        if emit_signals:
            self.fetch_available_reference_data_start.emit({'project_id': project_id})
        
        success = True
        error = None
        available_reference_data = None
        
        if project_id is None:
            success = False
            error = 'project_id is None!'
        else:
            if self.db_type == 'local_files':
                all_reference_data = pd.read_csv(self.available_reference_data_path)
                available_reference_data = all_reference_data[(all_reference_data['project_id'] == project_id)]
                available_reference_data_sorted = available_reference_data.sort_values(by = 'name', ascending = False, ignore_index = True)
                available_reference_data = available_reference_data_sorted
            elif self.db_type == 'local_mysql_db':
                db_response = self.db.fetch_reference_data_by_project_id(project_id)
                if db_response['success']:
                    available_reference_data = db_response['data']
                else:
                    success = False
                    error = db_response['error']
        
        if success:
            self.available_reference_data = available_reference_data
        
        if emit_signals:
            self.fetch_available_reference_data_end.emit({'success': success, 'error': error, 'data': available_reference_data})
    
    def add_available_reference_data(self, path: str = None, name: str = None, original_path: str = None, project_id: str = None, emit_signals: bool = True):
        self._run_task(self._add_available_reference_data, path, name, original_path, project_id, emit_signals)
        
    def _add_available_reference_data(self, path: str = None, name: str = None, original_path: str = None, project_id: str = None, emit_signals: bool = True):
        if emit_signals:
            self.add_available_reference_data_start.emit({'path': path, 'project_id': project_id})
            
        success = True
        error = None
        data = None
        
        if original_path is None:
            original_path = path
        
        if path is None:
            success = False
            error = 'path is None!'
        elif name is None:
            success = False
            error = 'name is None!'
        elif project_id is None:
            success = False
            error = 'project_id is None!'
        else:
            if self.db_type == 'local_files':
                all_reference_data = pd.read_csv(self.available_reference_data_path)
                if name in all_reference_data[all_reference_data['project_id'] == project_id]['name'].tolist():
                    success = False
                    error = f'You already have a reference data file with the name {name} for the project {project_id}. Please specify a different file name.'
                else:
                    new_reference_data_file = pd.DataFrame.from_dict([{'id': str(uuid.uuid4()),
                                                                       'path': path,
                                                                       'project_id': project_id,
                                                                       'name': name,
                                                                       'original_path': original_path}])
                    all_reference_data = pd.concat((all_reference_data, new_reference_data_file))
                    all_reference_data.to_csv(path_or_buf = self.available_reference_data_path, index = False)
                    data = new_reference_data_file.squeeze()
            elif self.db_type == 'local_mysql_db':
                db_response = self.db.fetch_reference_data_by_path_and_project_id(path, project_id)
                if len(db_response['data'].index) == 0:
                    db_response = self.db.add_reference_data_by_project_id(path, name, original_path, project_id)
                    if db_response['success']:
                        data = db_response['data']
                    else:
                        success = False
                        error = db_response['error']
                else:
                    success = False
                    error = f'You already have a reference data file with the name {name} for the project {project_id}. Please specify a different file name.'
        
        if emit_signals:
            self.add_available_reference_data_end.emit({'success': success, 'error': error, 'data': data})
        
    def update_reference_data_id(self, reference_data_id: str = None, model_id: str = None, emit_signals: bool = True):
        self._run_task(self._update_reference_data_id, reference_data_id, model_id, emit_signals)
    
    def _update_reference_data_id(self, reference_data_id: str = None, model_id: str = None, emit_signals: bool = True):
        if emit_signals:
            self.update_reference_data_id_start.emit({'reference_data_id': reference_data_id, 'model_id': model_id})
        
        success = True
        error = None
        data = None
        
        if model_id is None:
            success = False
            error = 'model_id is None!'
        elif reference_data_id == self.models.loc[self.models['id'] == model_id, 'reference_data_id'].iloc[0]:
            success = False
            error = 'reference_data_id is the same as the one you are trying to set!'
        else:
            if self.db_type == 'local_files':
                all_models = pd.read_csv(self.models_path)
                all_models.loc[all_models['id'] == model_id, 'reference_data_id'] = reference_data_id
                all_models.to_csv(path_or_buf = self.models_path, index = False)
                self.models.loc[self.models['id'] == model_id, 'reference_data_id'] = reference_data_id
                if self.active_model is not None and self.active_model['id'] == model_id:
                    self.set_active_model(self.models[self.models['id'] == model_id].squeeze(), override = True, emit_signals = False)
            elif self.db_type == 'local_mysql_db':
                db_response = self.db.update_reference_data_id_by_model_id(reference_data_id, model_id)
                if db_response['success']:
                    data = db_response['data']
                    self.models.loc[self.models['id'] == model_id, 'reference_data_id'] = reference_data_id
                    if self.active_model is not None and self.active_model['id'] == model_id:
                        self.set_active_model(self.models[self.models['id'] == model_id].squeeze(), override = True, emit_signals = False)
                else:
                    success = False
                    error = db_response['error']
        
        if emit_signals:
            self.update_reference_data_id_end.emit({'success': success, 'error': error, 'data': data})
        
    #%% Parameters files
    def fetch_available_parameters(self, project_id: str = None, emit_signals: bool = True):
        self._run_task(self._fetch_available_parameters, project_id, emit_signals)
        
    def _fetch_available_parameters(self, project_id: str = None, emit_signals: bool = True):
        if emit_signals:
            self.fetch_available_parameters_start.emit({'project_id': project_id})

        success = True
        error = None
        available_parameters = None
        
        if project_id is None:
            success = False
            error = 'project_id is None!'
        else:
            if self.db_type == 'local_files':
                all_parameters = pd.read_csv(self.available_parameters_path)
                available_parameters = all_parameters[(all_parameters['project_id'] == project_id)]
                available_parameters_sorted = available_parameters.sort_values(by = 'name', ascending = False, ignore_index = True)
                available_parameters = available_parameters_sorted
            elif self.db_type == 'local_mysql_db':
                db_response = self.db.fetch_parameters_by_project_id(project_id)
                if db_response['success']:
                    available_parameters = db_response['data']
                else:
                    success = False
                    error = db_response['error']
        
        if success:
            self.available_parameters = available_parameters
        
        if emit_signals:
            self.fetch_available_parameters_end.emit({'success': success, 'error': error, 'data': available_parameters})
    
    def add_available_parameters(self, path: str = None, name: str = None, original_path: str = None, project_id: str = None, emit_signals: bool = True):
        self._run_task(self._add_available_parameters, path, name, original_path, project_id, emit_signals)
        
    def _add_available_parameters(self, path: str = None, name: str = None, original_path: str = None, project_id: str = None, emit_signals: bool = True):
        if emit_signals:
            self.add_available_parameters_start.emit({'path': path, 'project_id': project_id})
        
        success = True
        error = None
        data = None
        
        if original_path is None:
            original_path = path
        
        if path is None:
            success = False
            error = 'path is None!'
        elif name is None:
            success = False
            error = 'name is None!'
        elif project_id is None:
            success = False
            error = 'project_id is None!'
        else:
            if self.db_type == 'local_files':
                all_parameters = pd.read_csv(self.available_parameters_path)
                if name in all_parameters[all_parameters['project_id'] == project_id]['name'].tolist():
                    success = False
                    error = f'You already have a parameters file with the name {name} for the project {project_id}. Please specify a different file.'
                else:
                    new_parameters_file = pd.DataFrame.from_dict([{'id': str(uuid.uuid4()),
                                                                   'path': path,
                                                                   'project_id': project_id,
                                                                   'name': name,
                                                                   'original_path': original_path}])
                    all_parameters = pd.concat((all_parameters, new_parameters_file))
                    all_parameters.to_csv(path_or_buf = self.available_parameters_path, index = False)
                    data = new_parameters_file.squeeze()
            elif self.db_type == 'local_mysql_db':
                db_response = self.db.fetch_parameters_by_path_and_project_id(path, project_id)
                if len(db_response['data'].index) == 0:
                    db_response = self.db.add_parameters_by_project_id(path, name, original_path, project_id)
                    if db_response['success']:
                        data = db_response['data']
                    else:
                        success = False
                        error = db_response['error']
                else:
                    success = False
                    error = f'You already have a parameters file with the name {name} for the project {project_id}. Please specify a different file.'
        
        if emit_signals:
            self.add_available_parameters_end.emit({'success': success, 'error': error, 'data': data})
        
    def update_parameters_id(self, parameters_id: str = None, model_id: str = None, emit_signals: bool = True):
        self._run_task(self._update_parameters_id, parameters_id, model_id, emit_signals)
    
    def _update_parameters_id(self, parameters_id: str = None, model_id: str = None, emit_signals: bool = True):
        if emit_signals:
            self.update_parameters_id_start.emit({'parameters_id': parameters_id, 'model_id': model_id})
        
        success = True
        error = None
        data = None
        
        if model_id is None:
            success = False
            error = 'model_id is None!'
        elif parameters_id == self.models.loc[self.models['id'] == model_id, 'parameters_id'].iloc[0]:
            success = False
            error = 'parameters_id is the same as the one you are trying to set!'
        else:
            if self.db_type == 'local_files':
                all_models = pd.read_csv(self.models_path)
                all_models.loc[all_models['id'] == model_id, 'parameters_id'] = parameters_id
                all_models.to_csv(path_or_buf = self.models_path, index = False)
                self.models.loc[self.models['id'] == model_id, 'parameters_id'] = parameters_id
                if self.active_model is not None and self.active_model['id'] == model_id:
                    self.set_active_model(self.models[self.models['id'] == model_id].squeeze(), override = True, emit_signals = False)
            elif self.db_type == 'local_mysql_db':
                db_response = self.db.update_parameters_id_by_model_id(parameters_id, model_id)
                if db_response['success']:
                    data = db_response['data']
                    self.models.loc[self.models['id'] == model_id, 'parameters_id'] = parameters_id
                    if self.active_model is not None and self.active_model['id'] == model_id:
                        self.set_active_model(self.models[self.models['id'] == model_id].squeeze(), override = True, emit_signals = False)
                else:
                    success = False
                    error = db_response['error']
        
        if emit_signals:
            self.update_parameters_id_end.emit({'success': success, 'error': error, 'data': data})

    #%% Model files
    def fetch_available_model_files(self, project_id: str = None, emit_signals: bool = True):
        self._run_task(self._fetch_available_model_files, project_id, emit_signals)
        
    def _fetch_available_model_files(self, project_id: str = None, emit_signals: bool = True):
        if emit_signals:
            self.fetch_available_model_files_start.emit({'project_id': project_id})
    
        success = True
        error = None
        available_model_files = None
        
        if project_id is None:
            success = False
            error = 'project_id is None!'
        else:
            if self.db_type == 'local_files':
                all_model_files = pd.read_csv(self.available_model_files_path)
                available_model_files = all_model_files[(all_model_files['project_id'] == project_id)]
                available_model_files_sorted = available_model_files.sort_values(by = 'name', ascending = False, ignore_index = True)
                available_model_files = available_model_files_sorted
            elif self.db_type == 'local_mysql_db':
                db_response = self.db.fetch_model_files_by_project_id(project_id)
                if db_response['success']:
                    available_model_files = db_response['data']
                else:
                    success = False
                    error = db_response['error']
        
        if success:
            self.available_model_files = available_model_files
        
        if emit_signals:
            self.fetch_available_model_files_end.emit({'success': success, 'error': error, 'data': available_model_files})
    
    def add_available_model_file(self, path: str = None, name: str = None, original_path: str = None, project_id: str = None, emit_signals: bool = True):
        self._run_task(self._add_available_model_file, path, name, original_path, project_id, emit_signals)
        
    def _add_available_model_file(self, path: str = None, name: str = None, original_path: str = None, project_id: str = None, emit_signals: bool = True):
        if emit_signals:
            self.add_available_model_file_start.emit({'path': path, 'project_id': project_id})
        
        success = True
        error = None
        data = None
        
        if original_path is None:
            original_path = path
        
        if path is None:
            success = False
            error = 'path is None!'
        elif name is None:
            success = False
            error = 'name is None!'
        elif project_id is None:
            success = False
            error = 'project_id is None!'
        else:
            if self.db_type == 'local_files':
                all_model_files = pd.read_csv(self.available_model_files_path)
                if name in all_model_files[all_model_files['project_id'] == project_id]['name'].tolist():
                    success = False
                    error = f'You already have a model file with the name {name} for the project {project_id}. Please specify a different file.'
                else:
                    new_model_file = pd.DataFrame.from_dict([{'id': str(uuid.uuid4()),
                                                              'path': path,
                                                              'project_id': project_id,
                                                              'name': name,
                                                              'original_path': original_path}])
                    all_model_files = pd.concat((all_model_files, new_model_file))
                    all_model_files.to_csv(path_or_buf = self.available_model_files_path, index = False)
                    data = new_model_file.squeeze()
            elif self.db_type == 'local_mysql_db':
                db_response = self.db.fetch_model_file_by_path_and_project_id(path, project_id)
                if len(db_response['data'].index) == 0:
                    db_response = self.db.add_model_file_by_project_id(path, name, original_path, project_id)
                    if db_response['success']:
                        data = db_response['data']
                    else:
                        success = False
                        error = db_response['error']
                else:
                    success = False
                    error = f'You already have a model file with the name {name} for the project {project_id}. Please specify a different file.'
        
        if emit_signals:
            self.add_available_model_file_end.emit({'success': success, 'error': error, 'data': data})
        
    def update_model_file_id(self, model_file_id: str = None, model_id: str = None, emit_signals: bool = True):
        self._run_task(self._update_model_file_id, model_file_id, model_id, emit_signals)
    
    def _update_model_file_id(self, model_file_id: str = None, model_id: str = None, emit_signals: bool = True):
        if emit_signals:
            self.update_model_file_id_start.emit({'model_file_id': model_file_id, 'model_id': model_id})
        
        success = True
        error = None
        data = None
        
        if model_id is None:
            success = False
            error = 'model_id is None!'
        elif model_file_id == self.models.loc[self.models['id'] == model_id, 'model_file_id'].iloc[0]:
            success = False
            error = 'model_file_id is the same as the one you are trying to set!'
        else:
            if self.db_type == 'local_files':
                all_models = pd.read_csv(self.models_path)
                all_models.loc[all_models['id'] == model_id, 'model_file_id'] = model_file_id
                all_models.to_csv(path_or_buf = self.models_path, index = False)
                self.models.loc[self.models['id'] == model_id, 'model_file_id'] = model_file_id
                if self.active_model is not None and self.active_model['id'] == model_id:
                    self.set_active_model(self.models[self.models['id'] == model_id].squeeze(), override = True, emit_signals = False)
            elif self.db_type == 'local_mysql_db':
                db_response = self.db.update_model_file_id_by_model_id(model_file_id, model_id)
                if db_response['success']:
                    data = db_response['data']
                    self.models.loc[self.models['id'] == model_id, 'model_file_id'] = model_file_id
                    if self.active_model is not None and self.active_model['id'] == model_id:
                        self.set_active_model(self.models[self.models['id'] == model_id].squeeze(), override = True, emit_signals = False)
                else:
                    success = False
                    error = db_response['error']
        
        if emit_signals:
            self.update_model_file_id_end.emit({'success': success, 'error': error, 'data': data})
    
    def update_model_template(self, model_template: str = None, model_id: str = None, emit_signals: bool = True):
        self._run_task(self._update_model_template, model_template, model_id, emit_signals)
    
    def _update_model_template(self, model_template: str = None, model_id: str = None, emit_signals: bool = True):
        if emit_signals:
            self.update_model_template_start.emit({'model_template': model_template, 'model_id': model_id})
        
        success = True
        error = None
        data = None
        
        if model_id is None:
            success = False
            error = 'model_id is None!'
        else:
            if self.db_type == 'local_files':
                all_models = pd.read_csv(self.models_path)
                all_models.loc[all_models['id'] == model_id, 'model_template'] = model_template
                all_models.to_csv(path_or_buf = self.models_path, index = False)
                self.models.loc[self.models['id'] == model_id, 'model_template'] = model_template
                if self.active_model is not None and self.active_model['id'] == model_id:
                    self.set_active_model(self.models[self.models['id'] == model_id].squeeze(), override = True, emit_signals = False)
            elif self.db_type == 'local_mysql_db':
                db_response = self.db.update_model_template_by_model_id(model_template, model_id)
                if db_response['success']:
                    data = db_response['data']
                    self.models.loc[self.models['id'] == model_id, 'model_template'] = model_template
                    if self.active_model is not None and self.active_model['id'] == model_id:
                        self.set_active_model(self.models[self.models['id'] == model_id].squeeze(), override = True, emit_signals = False)
                else:
                    success = False
                    error = db_response['error']
        
        if emit_signals:
            self.update_model_template_end.emit({'success': success, 'error': error, 'data': data})
    
    def get_model_file_path(self):
        if self.model_template is None:
            return self.model_file_path
        else:
            return None
    
    #%% Tesbenches files
    def fetch_available_testbenches(self, project_id: str = None, emit_signals: bool = True):
        self._run_task(self._fetch_available_testbenches, project_id, emit_signals)
        
    def _fetch_available_testbenches(self, project_id: str = None, emit_signals: bool = True):
        if emit_signals:
            self.fetch_available_testbenches_start.emit({'project_id': project_id})
    
        success = True
        error = None
        available_testbenches = None
        
        if project_id is None:
            success = False
            error = 'project_id is None!'
        else:
            if self.db_type == 'local_files':
                all_testbenches = pd.read_csv(self.available_testbenches_path)
                available_testbenches = all_testbenches[(all_testbenches['project_id'] == project_id)]
                available_testbenches_sorted = available_testbenches.sort_values(by = 'name', ascending = False, ignore_index = True)
                available_testbenches = available_testbenches_sorted
            elif self.db_type == 'local_mysql_db':
                db_response = self.db.fetch_testbenches_by_project_id(project_id)
                if db_response['success']:
                    available_testbenches = db_response['data']
                else:
                    success = False
                    error = db_response['error']
        
        if success:
            self.available_testbenches = available_testbenches
        
        if emit_signals:
            self.fetch_available_testbenches_end.emit({'success': success, 'error': error, 'data': available_testbenches})
    
    def add_available_testbenches(self, path: str = None, name: str = None, original_path: str = None, project_id: str = None, emit_signals: bool = True):
        self._run_task(self._add_available_testbenches, path, name, original_path, project_id, emit_signals)
        
    def _add_available_testbenches(self, path: str = None, name: str = None, original_path: str = None, project_id: str = None, emit_signals: bool = True):
        if emit_signals:
            self.add_available_testbenches_start.emit({'path': path, 'project_id': project_id})
        
        success = True
        error = None
        data = None
        
        if original_path is None:
            original_path = path
        
        if path is None:
            success = False
            error = 'path is None!'
        elif name is None:
            success = False
            error = 'name is None!'
        elif project_id is None:
            success = False
            error = 'project_id is None!'
        else:
            if self.db_type == 'local_files':
                all_testbenches = pd.read_csv(self.available_testbenches_path)
                if name in all_testbenches[all_testbenches['project_id'] == project_id]['name'].tolist():
                    success = False
                    error = f'You already have a model file with the name {name} for the project {project_id}. Please specify a different file.'
                else:
                    new_testbenches = pd.DataFrame.from_dict([{'id': str(uuid.uuid4()),
                                                              'path': path,
                                                              'project_id': project_id,
                                                              'name': name,
                                                              'original_path': original_path}])
                    all_testbenches = pd.concat((all_testbenches, new_testbenches))
                    all_testbenches.to_csv(path_or_buf = self.available_testbenches_path, index = False)
                    data = new_testbenches.squeeze()
            elif self.db_type == 'local_mysql_db':
                db_response = self.db.fetch_testbenches_by_path_and_project_id(path, project_id)
                if len(db_response['data'].index) == 0:
                    db_response = self.db.add_testbenches_by_project_id(path, name, original_path, project_id)
                    if db_response['success']:
                        data = db_response['data']
                    else:
                        success = False
                        error = db_response['error']
                else:
                    success = False
                    error = f'You already have a model file with the name {name} for the project {project_id}. Please specify a different file.'
        
        if emit_signals:
            self.add_available_testbenches_end.emit({'success': success, 'error': error, 'data': data})
        
    def update_testbenches_id(self, testbenches_id: str = None, model_id: str = None, emit_signals: bool = True):
        self._run_task(self._update_testbenches_id, testbenches_id, model_id, emit_signals)
    
    def _update_testbenches_id(self, testbenches_id: str = None, model_id: str = None, emit_signals: bool = True):
        if emit_signals:
            self.update_testbenches_id_start.emit({'testbenches_id': testbenches_id, 'model_id': model_id})
        
        success = True
        error = None
        data = None
        
        if model_id is None:
            success = False
            error = 'model_id is None!'
        elif testbenches_id == self.models.loc[self.models['id'] == model_id, 'testbenches_id'].iloc[0]:
            success = False
            error = 'testbenches_id is the same as the one you are trying to set!'
        else:
            if self.db_type == 'local_files':
                all_models = pd.read_csv(self.models_path)
                all_models.loc[all_models['id'] == model_id, 'testbenches_id'] = testbenches_id
                all_models.to_csv(path_or_buf = self.models_path, index = False)
                self.models.loc[self.models['id'] == model_id, 'testbenches_id'] = testbenches_id
                if self.active_model is not None and self.active_model['id'] == model_id:
                    self.set_active_model(self.models[self.models['id'] == model_id].squeeze(), override = True, emit_signals = False)
            elif self.db_type == 'local_mysql_db':
                db_response = self.db.update_testbenches_id_by_model_id(testbenches_id, model_id)
                if db_response['success']:
                    data = db_response['data']
                    self.models.loc[self.models['id'] == model_id, 'testbenches_id'] = testbenches_id
                    if self.active_model is not None and self.active_model['id'] == model_id:
                        self.set_active_model(self.models[self.models['id'] == model_id].squeeze(), override = True, emit_signals = False)
                else:
                    success = False
                    error = db_response['error']
        
        if emit_signals:
            self.update_testbenches_id_end.emit({'success': success, 'error': error, 'data': data})
    
    #%% Optimization settings   
    def create_optimization_settings_file(self, emit_signals: bool = True):
        self._run_task(self._create_optimization_settings_file, emit_signals)
                
    def _create_optimization_settings_file(self, emit_signals: bool = True):
        if emit_signals:
            self.create_optimization_settings_file_start.emit({'model_id': self.active_model['id']})

        success = True
        error = None
        data = None

        if self.db_type in ['local_files', 'local_mysql_db']:
            model_path = Path(self.active_model['path'])
            inputs_path = Path.joinpath(model_path, 'inputs')
            optimization_settings_file_path = Path.joinpath(inputs_path, 'optimization_settings.json')
            if not Path.exists(optimization_settings_file_path):
                with open(optimization_settings_file_path, 'w') as file:
                    json.dump({}, file, indent = 4)
                
        if self.db_type == 'local_files':
            all_optimization_settings = pd.read_csv(self.optimization_settings_files_path)
            optimization_settings_id = str(uuid.uuid4())
            new_optimization_settings_file = pd.DataFrame.from_dict([{'id': optimization_settings_id,
                                                                      'path': optimization_settings_file_path}])
            all_optimization_settings = pd.concat((all_optimization_settings, new_optimization_settings_file))
            all_optimization_settings.to_csv(path_or_buf = self.optimization_settings_files_path, index = False)
        elif self.db_type == 'local_mysql_db':
            db_response = self.db.add_optimization_settings(optimization_settings_file_path)
            if db_response['success']:
                data = db_response['data']
                optimization_settings_id = data['id']
            else:
                success = False
                error = db_response['error']
        
        if success:
            self.optimization_settings_path = optimization_settings_file_path
            self._update_optimization_settings_id(optimization_settings_id = optimization_settings_id, emit_signals = False)
            self._fetch_optimization_settings()

        if emit_signals:
            self.create_optimization_settings_file_end.emit({'success': success, 'error': error, 'data': data})
            
    def update_optimization_settings_id(self, optimization_settings_id: str = None, emit_signals: bool = True):
        self._run_task(self._update_optimization_settings_id, optimization_settings_id, emit_signals)
        
    def _update_optimization_settings_id(self, optimization_settings_id: str = None, emit_signals: bool = True):
        if emit_signals:
            self.update_optimization_settings_id_start.emit({'model_id': self.active_model['id']})

        success = True
        error = None
        data = None
        
        if optimization_settings_id is None:
            success = False
            error = 'optimization_settings_id is None!'
        else:
            model_id = self.active_model['id']
            if self.db_type == 'local_files':
                all_models = pd.read_csv(self.models_path)
                all_models.loc[all_models['id'] == model_id, 'optimization_settings_id'] = optimization_settings_id
                all_models.to_csv(path_or_buf = self.models_path, index = False)
                self.models.loc[self.models['id'] == model_id, 'optimization_settings_id'] = optimization_settings_id
                self.set_active_model(self.models[self.models['id'] == model_id].squeeze(), override = True, emit_signals = False)
            elif self.db_type == 'local_mysql_db':
                db_response = self.db.update_optimization_settings_id_by_model_id(optimization_settings_id, model_id)
                if db_response['success']:
                    data = db_response['data']
                    self.models.loc[self.models['id'] == self.models['id'], 'optimization_settings_id'] = optimization_settings_id
                    self.set_active_model(self.models[self.models['id'] == self.active_model['id']].squeeze(), override = True, emit_signals = False)
                else:
                    success = False
                    error = db_response['error']

        if emit_signals:
            self.update_optimization_settings_id_end.emit({'success': success, 'error': error, 'data': data})
            
    def fetch_optimization_settings(self, emit_signals: bool = True, sync: bool = False):
        if sync:
            self._fetch_optimization_settings(emit_signals)
        else:
            self._run_task(self._fetch_optimization_settings, emit_signals)
            
    def _fetch_optimization_settings(self, emit_signals: bool = True):
        if emit_signals:
            self.fetch_optimization_settings_start.emit({'model_id': self.active_model['id']})

        success = True
        error = None
        data = None

        optimization_settings_id = self.active_model['optimization_settings_id']        
        if self.db_type == 'local_files':
            all_optimization_settings = pd.read_csv(self.optimization_settings_files_path)
            optimization_settings_path = all_optimization_settings.loc[all_optimization_settings['id'] == optimization_settings_id, 'path'].values[0]                     
        elif self.db_type == 'local_mysql_db':
            db_response = self.db.fetch_optimization_settings_by_id(optimization_settings_id)
            if db_response['success']:
                optimization_settings_path = db_response['data'].iloc[0]['path']
            else:
                success = False
                error = db_response['error']
                
        if success:
            self.optimization_settings_path = optimization_settings_path
            with open(optimization_settings_path, 'r') as file:
                optimization_settings = json.load(file)
                self.optimizers = self.available_optimizers.copy()
                self.optimizers['value'] = self.optimizers['default']
                self.simulators = self.available_simulators.copy()
                self.simulators['value'] = self.simulators['default']
                self.active_optimizer = 'differential_evolution'
                self.active_simulator = 'ngspice'
                self.loss_function = {'file': None, 'parts': {}}
                if len(optimization_settings.keys()) > 0:
                    # optimizer
                    if 'optimizer' in optimization_settings.keys():
                        optimizer = optimization_settings['optimizer']
                        if 'active_optimizer' in optimizer.keys():
                            self.active_optimizer = optimizer['active_optimizer']
                            del optimizer['active_optimizer']
                        for key, value in optimizer.items():
                            self.optimizers.loc[(self.optimizers['optimizer'] == self.active_optimizer) & (self.optimizers['name'] == key), 'value'] = value
                    
                    # simulator
                    if 'simulator' in optimization_settings.keys():
                        simulator = optimization_settings['simulator']
                        if 'active_simulator' in optimizer.keys():
                            self.active_optimizer = simulator['active_simulator']
                            del simulator['active_simulator']
                        for key, value in optimizer.items():
                            self.simulators.loc[(self.simulators['simulator'] == self.active_simulator) & (self.simulators['name'] == key), 'value'] = value
                    
                    # loss function
                    if 'loss_function' in optimization_settings.keys():
                        loss_function = optimization_settings['loss_function']
                        if 'file' in loss_function.keys():
                            self.loss_function['file'] = loss_function['file']
                        if 'parts' in loss_function.keys():
                            for p in loss_function['parts']:
                                self.loss_function['parts'][p['id']] = p

        if emit_signals:
            self.fetch_optimization_settings_end.emit({'success': success, 'error': error, 'data': data})
            
    def get_optimization_settings_path_by_id(self, optimization_settings_id: str = None):
        optimization_settings_path = None
        if self.db_type == 'local_files':
            all_optimization_settings = pd.read_csv(self.optimization_settings_files_path)
            optimization_settings_path = all_optimization_settings.loc[all_optimization_settings['id'] == optimization_settings_id, 'path'].values[0]
        elif self.db_type == 'local_mysql_db':
            db_response = self.db.fetch_optimization_settings_by_id(optimization_settings_id)
            if db_response['success']:
                optimization_settings_path = db_response['data'].iloc[0]['path']
        return optimization_settings_path
    
    def write_optimization_settings_to_file(self):
        optimization_settings = {}
        # optimizer
        if self.optimizers is not None:
            optimization_settings['optimizer'] = {'active_optimizer': self.active_optimizer}
            temp = self.optimizers[self.optimizers['optimizer'] == self.active_optimizer].set_index('name')
            optimization_settings['optimizer'].update(temp['value'].to_dict())
        
        # simulator
        if self.simulators is not None:
            optimization_settings['simulator'] = {'active_simulator': self.active_simulator}
            temp = self.simulators[self.simulators['simulator'] == self.active_simulator].set_index('name')
            optimization_settings['simulator'].update(temp['value'].to_dict())
            
        # loss function    
        if self.loss_function is not None:
            optimization_settings['loss_function'] = {'file': None, 'parts': []}
            
            if self.loss_function['file'] is not None:
                optimization_settings['loss_function']['file'] = self.loss_function['file']
                
            for key, part in self.loss_function['parts'].items():
                if len(part['group_types']) > 0:
                    optimization_settings['loss_function']['parts'].append(part)
                    
            if len(optimization_settings['loss_function']['parts']) == 0 and optimization_settings['loss_function']['file'] is None:
                del optimization_settings['loss_function']
                    
        # write to json file
        if len(optimization_settings.keys()) > 0:
            dict_to_json(optimization_settings, self.optimization_settings_path)
            if 'maximum_number_of_iterations' in optimization_settings.keys():
                self.update_model_max_iteration(optimization_settings['maximum_number_of_iterations'], self.active_model['id'])

    #%% Simulation input
    def compile_simulation_input(self, files_path = None):
        if files_path is None:
            files_path = self.active_model_results_directory
        results_path = Path.joinpath(files_path, 'results') 
        simulation_files_path = Path.joinpath(files_path, 'simulation_files')
        inputs_path = Path.joinpath(files_path, 'inputs')
        
        self.compile_simulator_config()
        self.compile_optimizer_config()
        self.compile_cost_function_config()
        dut_file = self.get_model_file_path()
        dut_name = 'dut'
        if self.db_type in ['local_files', 'local_mysql_db']:
            running_environment = 'local' 
        else:
            running_environment = None
        self.simulation_input = {'model_id': self.active_model['id'],
                                 'max_iterations': self.optimizer_config['max_iterations'],
                                 'reference_data': self.reference_data,
                                 'parameters': self.parameters,
                                 'testbenches': self.testbenches_path,
                                 'dut_file': dut_file,
                                 'dut_name': dut_name,
                                 'results_dir': results_path,
                                 'inputs_dir': inputs_path,
                                 'simulation_files_dir': simulation_files_path,
                                 'simulator_config': self.simulator_config,
                                 'optimizer_config': self.optimizer_config,
                                 'cost_function_config': self.cost_function_config,
                                 'running_environment': running_environment}
        self.write_optimization_settings_to_file()
    
    def compile_simulator_config(self):
        self.simulator_config = {'type': self.active_simulator}
        temp = self.simulators.copy()
        temp.set_index('name', inplace = True)
        temp = temp.loc[temp['simulator'] == self.active_simulator, 'value'].to_dict()
        self.simulator_config.update(temp)
        
    def compile_optimizer_config(self):
        self.optimizer_config = {'type': self.active_optimizer,
                                 'results_dir': self.active_model_directory}
        temp = self.optimizers.copy()
        temp.set_index('name', inplace = True)
        temp = temp.loc[temp['optimizer'] == self.active_optimizer, 'value'].to_dict()
        key_mapping = {'population_size': 'pop_size',
                       'maximum_number_of_iterations': 'max_iterations',
                       'maximum_number_of_iterations_without_improvement': 'max_iter_without_improvement',
                       'initial_population': 'init_pop',
                       'loss_threshold': 'metric_threshold'}
        new_dict = {key_mapping.get(k, k): v for k, v in temp.items()}
        self.optimizer_config.update(new_dict)
        
    def compile_cost_function_config(self):
        self.cost_function_config = {'type': 'default',
                                     'parts': list(self.loss_function['parts'].values())}
    
    #%% Single simulation results
    def update_single_simulation_results(self, emit_signals: bool = True):
        if emit_signals:
            self.update_single_simulation_results_start.emit()
        
        self.single_simulation_results = None
        
        single_simulation_results_id = self.active_model['single_simulation_results_id']
        if not pd.isnull(single_simulation_results_id):
            single_simulation_results_path = self.single_simulation_results_files.loc[self.single_simulation_results_files['id'] == single_simulation_results_id, 'path'].values
            if len(single_simulation_results_path) >= 1:                
                single_simulation_results_path = single_simulation_results_path[0]            
                if Path.exists(Path(single_simulation_results_path)):
                    temp = Reference_data(file = single_simulation_results_path)
                    self.single_simulation_results = temp.data
        
        if emit_signals:
            self.update_single_simulation_results_end.emit()
    
    def fetch_single_simulation_results_files(self, model_id: str = None, emit_signals: bool = True, sync: bool = False):
        if sync:
            self._fetch_single_simulation_results_files(model_id, emit_signals)
        else:
            self._run_task(self._fetch_single_simulation_results_files, model_id, emit_signals)
        
    def _fetch_single_simulation_results_files(self, model_id: str = None, emit_signals: bool = True):
        if emit_signals:
            self.fetch_single_simulation_results_files_start.emit({'model_id': model_id})
        
        success = True
        error = None
        single_simulation_results_files = None
        
        if model_id is None:
            success = False
            error = 'project_id is None!'
        else:
            if self.db_type == 'local_files':
                single_simulation_results_files = pd.read_csv(self.single_simulation_results_files_path)
            elif self.db_type == 'local_mysql_db':
                db_response = self.db.fetch_single_simulation_results()
                if db_response['success']:
                    single_simulation_results_files = db_response['data']
                else:
                    success = False
                    error = db_response['error']
        
        if success:
            self.single_simulation_results_files = single_simulation_results_files
            self.update_single_simulation_results()
        
        if emit_signals:
            self.fetch_single_simulation_results_files_end.emit({'success': success, 'error': error, 'data': single_simulation_results_files})
    
    def create_single_simulation_results_file(self, results: pd.DataFrame = None, path: str = None, model_id: str = None, emit_signals: bool = True, sync: bool = False):
        if sync:
            self._create_single_simulation_results_file(results, path, model_id, emit_signals)
        else:
            self._run_task(self._create_single_simulation_results_file, results, path, model_id, emit_signals)
    
    def _create_single_simulation_results_file(self, results: pd.DataFrame = None, path: str = None, model_id: str = None, emit_signals: bool = True):
        if emit_signals:
            self.create_single_simulation_results_file_start.emit()
        
        success = True
        error = None
        data = None
        
        if model_id is None:
            success = False
            error = 'model_id is None!'
        elif results is None:
            success = False
            error = 'results is None!'
        elif path is None:
            success = False
            error = 'path is None!'
        else:
            # Create the file
            write_reference_data_to_file(data = results,
                                         file_path = path,
                                         include_simulation = 'True',
                                         operating_conditions = ['temp', 'vbs', 'vds', 'vgs', 'frequency'],
                                         instance_parameters = ['w', 'l', 'm', 'area'])
            
            # Add it to the single_simulation_results_files and update the model
            if self.db_type == 'local_files':
                    id = str(uuid.uuid4())
                    new_single_simulation_results_file = pd.DataFrame.from_dict([{'id': id,
                                                                                  'path': path,
                                                                                  'model_id': model_id}])
                    self.single_simulation_results_files = pd.concat((self.single_simulation_results_files, new_single_simulation_results_file))
                    self.single_simulation_results_files.to_csv(path_or_buf = self.single_simulation_results_files_path, index = False)
                    data = new_single_simulation_results_file.squeeze()   
            elif self.db_type == 'local_mysql_db':
                db_response = self.db.add_single_simulation_results(path, model_id)
                if db_response['success']:
                    data = db_response['data']
                    id = data['id']
                else:
                    success = False
                    error = db_response['error']
                    
            if success:
                self.update_single_simulation_results_id(id, model_id)
                    
        if emit_signals:
            self.create_single_simulation_results_file_end.emit({'success': success, 'error': error, 'data': data})
    
    def update_single_simulation_results_id(self, single_simulation_results_id: str = None, model_id: str = None, emit_signals: bool = True):
        self._run_task(self._update_single_simulation_results_id, single_simulation_results_id, model_id, emit_signals)
        
    def _update_single_simulation_results_id(self, single_simulation_results_id: str = None, model_id: str = None, emit_signals: bool = True):
        if emit_signals:
            self.update_single_simulation_results_id_start.emit({'single_simulation_results_id': single_simulation_results_id, 'model_id': model_id})
        
        success = True
        error = None
        data = None
        
        if model_id is None:
            success = False
            error = 'model_id is None!'
        else:
            if self.db_type == 'local_files':
                all_models = pd.read_csv(self.models_path)
                all_models.loc[all_models['id'] == model_id, 'single_simulation_results_id'] = single_simulation_results_id
                all_models.to_csv(path_or_buf = self.models_path, index = False)
                self.models.loc[self.models['id'] == model_id, 'single_simulation_results_id'] = single_simulation_results_id
                if self.active_model is not None and self.active_model['id'] == model_id:
                    self.set_active_model(self.models[self.models['id'] == model_id].squeeze(), override = True, emit_signals = False)
            elif self.db_type == 'local_mysql_db':
                db_response = self.db.update_single_simulation_results_id_by_model_id(single_simulation_results_id, model_id)
                if db_response['success']:
                    data = db_response['data']
                    self.models.loc[self.models['id'] == model_id, 'single_simulation_results_id'] = single_simulation_results_id
                    if self.active_model is not None and self.active_model['id'] == model_id:
                        self.set_active_model(self.models[self.models['id'] == model_id].squeeze(), override = True, emit_signals = False)
                else:
                    success = False
                    error = db_response['error']
        
        if emit_signals:
            self.update_single_simulation_results_id_end.emit({'success': success, 'error': error, 'data': data})
            
    #%% Calibration results
    def update_calibration_results(self, emit_signals: bool = True):
        if emit_signals:
            self.update_calibration_results_start.emit()
        
        self.calibration_results = None
        
        calibration_results_id = self.active_model['calibration_results_id']
        if not pd.isnull(calibration_results_id):
            calibration_results_path = self.calibration_results_files.loc[self.calibration_results_files['id'] == calibration_results_id, 'path'].values
            if len(calibration_results_path) >= 1:                
                calibration_results_path = calibration_results_path[0]            
                if Path.exists(Path(calibration_results_path)):
                    temp = Reference_data(file = calibration_results_path)
                    self.calibration_results = temp.data
        
        if emit_signals:
            self.update_calibration_results_end.emit()
    
    def fetch_calibration_results_files(self, model_id: str = None, emit_signals: bool = True):
        self._run_task(self._fetch_calibration_results_files, model_id, emit_signals)
        
    def _fetch_calibration_results_files(self, model_id: str = None, emit_signals: bool = True):
        if emit_signals:
            self.fetch_calibration_results_files_start.emit({'model_id': model_id})
        
        success = True
        error = None
        calibration_results_files = None
        
        if model_id is None:
            success = False
            error = 'project_id is None!'
        else:
            if self.db_type == 'local_files':
                calibration_results_files = pd.read_csv(self.calibration_results_files_path)
            elif self.db_type == 'local_mysql_db':
                db_response = self.db.fetch_calibration_results()
                if db_response['success']:
                    calibration_results_files = db_response['data']
                else:
                    success = False
                    error = db_response['error']
        
        if success:
            self.calibration_results_files = calibration_results_files
            self.update_calibration_results()
        
        if emit_signals:
            self.fetch_calibration_results_files_end.emit({'success': success, 'error': error, 'data': calibration_results_files})
    
    def create_calibration_results_file(self, results: pd.DataFrame = None, path: str = None, model_id: str = None, emit_signals: bool = True):
        self._run_task(self._create_calibration_results_file, results, path, model_id, emit_signals)
    
    def _create_calibration_results_file(self, results: pd.DataFrame = None, path: str = None, model_id: str = None, emit_signals: bool = True):
        if emit_signals:
            self.create_calibration_results_file_start.emit()
        
        success = True
        error = None
        data = None
        
        if model_id is None:
            success = False
            error = 'model_id is None!'
        elif results is None:
            success = False
            error = 'results is None!'
        elif path is None:
            success = False
            error = 'path is None!'
        else:
            # Create the file
            write_reference_data_to_file(data = results,
                                         file_path = path,
                                         include_simulation = 'True',
                                         operating_conditions = ['temp', 'vbs', 'vds', 'vgs', 'frequency'],
                                         instance_parameters = ['w', 'l', 'm', 'area'])
            
            # Add it to the calibration_results_files and update the model
            if self.db_type == 'local_files':
                    id = str(uuid.uuid4())
                    new_calibration_results_file = pd.DataFrame.from_dict([{'id': id,
                                                                                  'path': path,
                                                                                  'model_id': model_id}])
                    self.calibration_results_files = pd.concat((self.calibration_results_files, new_calibration_results_file))
                    self.calibration_results_files.to_csv(path_or_buf = self.calibration_results_files_path, index = False)
                    data = new_calibration_results_file.squeeze()   
            elif self.db_type == 'local_mysql_db':
                db_response = self.db.add_calibration_results(path, model_id)
                if db_response['success']:
                    data = db_response['data']
                    id = data['id']
                else:
                    success = False
                    error = db_response['error']
                    
            if success:
                self.update_calibration_results_id(id, model_id)
                    
        if emit_signals:
            self.create_calibration_results_file_end.emit({'success': success, 'error': error, 'data': data})
            
    def update_calibration_results_file(self, results: pd.DataFrame = None, path: str = None, model_id: str = None, emit_signals: bool = True):
        self._run_task(self._update_calibration_results_file, results, path, model_id, emit_signals)
    
    def _update_calibration_results_file(self, results: pd.DataFrame = None, path: str = None, model_id: str = None, emit_signals: bool = True):
        if emit_signals:
            self.update_calibration_results_file_start.emit()
        
        success = True
        error = None
        data = None
        
        if model_id is None:
            success = False
            error = 'model_id is None!'
        elif results is None:
            success = False
            error = 'results is None!'
        elif path is None:
            success = False
            error = 'path is None!'
        else:
            # Create the file
            write_reference_data_to_file(data = results,
                                         file_path = path,
                                         include_simulation = 'True',
                                         operating_conditions = ['temp', 'vbs', 'vds', 'vgs', 'frequency'],
                                         instance_parameters = ['w', 'l', 'm', 'area'])
                    
        if emit_signals:
            self.update_calibration_results_file_end.emit({'success': success, 'error': error, 'data': data})
    
    def update_calibration_results_id(self, calibration_results_id: str = None, model_id: str = None, emit_signals: bool = True):
        self._run_task(self._update_calibration_results_id, calibration_results_id, model_id, emit_signals)
        
    def _update_calibration_results_id(self, calibration_results_id: str = None, model_id: str = None, emit_signals: bool = True):
        if emit_signals:
            self.update_calibration_results_id_start.emit({'calibration_results_id': calibration_results_id, 'model_id': model_id})
        
        success = True
        error = None
        data = None
        
        if model_id is None:
            success = False
            error = 'model_id is None!'
        else:
            if self.db_type == 'local_files':
                all_models = pd.read_csv(self.models_path)
                all_models.loc[all_models['id'] == model_id, 'calibration_results_id'] = calibration_results_id
                all_models.to_csv(path_or_buf = self.models_path, index = False)
                self.models.loc[self.models['id'] == model_id, 'calibration_results_id'] = calibration_results_id
                if self.active_model is not None and self.active_model['id'] == model_id:
                    self.set_active_model(self.models[self.models['id'] == model_id].squeeze(), override = True, emit_signals = False)
            elif self.db_type == 'local_mysql_db':
                db_response = self.db.update_calibration_results_id_by_model_id(calibration_results_id, model_id)
                if db_response['success']:
                    data = db_response['data']
                    self.models.loc[self.models['id'] == model_id, 'calibration_results_id'] = calibration_results_id
                    if self.active_model is not None and self.active_model['id'] == model_id:
                        self.set_active_model(self.models[self.models['id'] == model_id].squeeze(), override = True, emit_signals = False)
                else:
                    success = False
                    error = db_response['error']
        
        if emit_signals:
            self.update_calibration_results_id_end.emit({'success': success, 'error': error, 'data': data})  
    
    def overwrite_calibration_results(self, model_id: str = None, emit_signals: bool = True, sync: bool = True):
        if sync:
            self._overwrite_calibration_results(model_id, emit_signals)
        else:
            self._run_task(self._overwrite_calibration_results, model_id, emit_signals)
    
    def _overwrite_calibration_results(self, model_id: str = None, emit_signals: bool = True):
        if emit_signals:
            self.overwrite_calibration_results_start.emit({'model_id': model_id})
        
        if model_id == self.active_model['id']:
            if self.calibration_new_results is not None:
                plot = np.array(self.calibration_results['plot'])
                self.calibration_results = self.calibration_new_results.copy()
                self.calibration_results['plot'] = plot
                self.calibration_new_results = None
                
        if emit_signals:
            self.overwrite_calibration_results_end.emit({'model_id': model_id})

    #%% Extra functions
    def on_app_exit(self):
        print('Exiting the application...')
        self.write_optimization_settings_to_file()
        self.cleanup_dm_thread()
        self.abort_calibration()
        
    def emit_show_snackbar(self, message = 'snackbar message'):
        self.show_snackbar.emit(message)
    
    