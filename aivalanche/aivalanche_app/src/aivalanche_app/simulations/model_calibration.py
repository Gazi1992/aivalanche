from calibration.Calibration import Calibration
import numpy as np, pandas as pd

class model_calibration:
    def __init__(self, result_queue, command_queue):
        self.simulation_input = None
        self.result_queue = result_queue
        self.command_queue = command_queue
        self.calibration = None

    def update_simulation_input(self, new_simulation_input):
        self.simulation_input = new_simulation_input
        
    def callback_after_each_iter(self, **kwargs):
        iteration = kwargs['iteration']
        model_id = self.simulation_input['model_id']
        max_iterations = self.simulation_input['max_iterations']
        results = kwargs['responses']['results']
        metrics = kwargs['responses']['metrics']
        best_loss = kwargs['best_metric']
        best_results = results[np.argmin(metrics)]
        better_solution_found = kwargs['better_solution_found']
        results_dir = self.simulation_input['results_dir']
        survivors = self.get_all_survivors(kwargs['trials'])
        survivors = survivors[['iter', 'survivor_metric']]
        trials = self.get_trial_parameters(kwargs['trials'])
        res = {'status': 'progress',
               'model_id': model_id,
               'iteration': iteration,
               'best_loss': best_loss,
               'best_results': best_results,
               'max_iterations': max_iterations,
               'better_solution_found': better_solution_found,
               'survivors': survivors,
               'trials': trials,
               'results_dir': results_dir}
        self.result_queue.put(res)
        
    def callback_after_last_iter(self, **kwargs):
        iteration = kwargs['iteration']
        model_id = self.simulation_input['model_id']
        max_iterations = self.simulation_input['max_iterations']
        results_dir = self.simulation_input['results_dir']
        results = kwargs['responses']['results']
        metrics = kwargs['responses']['metrics']
        best_loss = kwargs['best_metric']
        best_results = results[np.argmin(metrics)]
        better_solution_found = True
        survivors = self.get_all_survivors(kwargs['trials'])
        survivors = survivors[['iter', 'survivor_metric']]
        trials = self.get_trial_parameters(kwargs['trials'])
        stop_reason = kwargs['stop_reason']
        res = {'status': 'finish',
               'model_id': model_id,
               'iteration': iteration,
               'best_loss': best_loss,
               'best_results': best_results,
               'max_iterations': max_iterations,
               'better_solution_found': better_solution_found,
               'survivors': survivors,
               'trials': trials,
               'results_dir': results_dir,
               'stop_reason': stop_reason}
        self.result_queue.put(res)
            
    def on_calibration_error(self, **kwargs):
        res = {'status': 'error',
               'model_id': self.simulation_input['model_id'],
               'error': kwargs['error']}
        self.result_queue.put(res)

    def run(self):
        if self.simulation_input is None:
            self.result_queue.put({'status': 'error', 'error': "No simulation input provided"})
            return
        
        if not self.simulation_input['running_environment'] == 'local':
            self.result_queue.put({'status': 'error', 'error': "running_environment has to be 'local'"})
            return
        
        try:
            self.simulation_input['optimizer_config'].update({'callback_after_each_iter': self.callback_after_each_iter,
                                                              'callback_after_last_iter': self.callback_after_last_iter})
            self.calibration = Calibration(
                reference_data = self.simulation_input['reference_data'],
                parameters = self.simulation_input['parameters'],
                testbenches = self.simulation_input['testbenches'],
                dut_file = self.simulation_input['dut_file'],
                dut_name = self.simulation_input['dut_name'],
                results_dir = self.simulation_input['results_dir'],
                optimizer_config = self.simulation_input['optimizer_config'],
                simulator_config = self.simulation_input['simulator_config'],
                cost_function_config = self.simulation_input['cost_function_config'],
                running_environment = self.simulation_input['running_environment'],
                command_queue = self.command_queue
            )
            self.calibration.calibrate(create_new_dir = False,
                                       simulation_files_path = self.simulation_input['simulation_files_dir'],
                                       write_input_to_files = False)
        except Exception as e:
            self.on_calibration_error(error = str(e))
            
    def get_all_survivors(self, trials):
        data = []
        pop_size = len(trials[trials['iter'] == 1])
        for row_idx, row in trials.iterrows():
            if row_idx < pop_size:
                data.append(row.tolist())
            else:
                if row['trial_metric'] < data[row_idx - pop_size][-1]:
                    data.append(row.tolist())
                else:
                    temp = data[row_idx - pop_size].copy()
                    temp[0] = row['iter']
                    data.append(temp)
        
        all_survivors = pd.DataFrame(columns = ['iter', 'survivor_normed', 'survivor', 'survivor_unscaled', 'survivor_metric'],
                                     data = data)

        return all_survivors
    
    def get_trial_parameters(self, trials):
        parameter_names = self.simulation_input['parameters'].variable_parameters_names
        df_exploded = trials['trial_normed'].apply(pd.Series)
        df_exploded = df_exploded.astype(float)
        df_exploded.columns = parameter_names
        df_exploded.reset_index(drop = True, inplace = True)
        return df_exploded
