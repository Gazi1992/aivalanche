from multiprocessing import Process, Queue
from calibration.Calibration import Calibration
import queue, numpy as np

class model_calibration:
    def __init__(self, simulation_input = None):
        self.simulation_input = simulation_input
        self.process = None
        self.result_queue = Queue()

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
        # responses['results'][np.argmin(responses['metrics'])]
        better_solution_found = kwargs['better_solution_found']
        results_dir = self.simulation_input['results_dir']
        trials = kwargs['trials']
        res = {'status': 'progress',
               'model_id': model_id,
               'iteration': iteration,
               'best_loss': best_loss,
               'best_results': best_results,
               'max_iterations': max_iterations,
               'better_solution_found': better_solution_found,
               'trials': trials,
               'results_dir': results_dir}
        self.result_queue.put(res)
        
    def callback_after_last_iter(self, **kwargs):
        iteration = kwargs['iteration']
        model_id = self.simulation_input['model_id']
        results_dir = self.simulation_input['results_dir']
        results = kwargs['responses']['results']
        metrics = kwargs['responses']['metrics']
        best_loss = kwargs['best_metric']
        best_results = results[np.argmin(metrics)]
        res = {'status': 'finish',
               'model_id': model_id,
               'iteration': iteration,
               'best_loss': best_loss,
               'best_results': best_results,
               'results_dir': results_dir}
        self.result_queue.put(res)
            
    def on_calibration_error(self, **kwargs):
        res = {'status': 'error',
               'model_id': self.simulation_input['model_id'],
               'error': kwargs['error']}
        self.result_queue.put(res)

    def run(self):
        if self.simulation_input is None:
            self.result_queue.put(('error', "No simulation input provided"))
            return
        
        if not self.simulation_input['running_environment'] == 'local':
            self.result_queue.put(('error', "running_environment has to be 'local'"))
            return
        
        try:
            self.simulation_input['optimizer_config'].update({'callback_after_each_iter': self.callback_after_each_iter,
                                                              'callback_after_last_iter': self.callback_after_last_iter})
            calibration = Calibration(
                reference_data = self.simulation_input['reference_data'],
                parameters = self.simulation_input['parameters'],
                testbenches = self.simulation_input['testbenches'],
                dut_file = self.simulation_input['dut_file'],
                dut_name = self.simulation_input['dut_name'],
                results_dir = self.simulation_input['results_dir'],
                optimizer_config = self.simulation_input['optimizer_config'],
                simulator_config = self.simulation_input['simulator_config'],
                cost_function_config = self.simulation_input['cost_function_config'],
                running_environment = self.simulation_input['running_environment']
            )
            calibration.calibrate(create_new_dir = False,
                                  simulation_files_path = self.simulation_input['simulation_files_dir'],
                                  write_input_to_files = False)
        except Exception as e:
            self.on_calibration_error(error = str(e))

    def start(self):
        if self.process is None or not self.process.is_alive():
            self.process = Process(target = self.run)
            self.process.start()

    def is_running(self):
        return self.process is not None and self.process.is_alive()

    def get_result(self):
        item = None
        try:
            item = self.result_queue.get_nowait()
        except queue.Empty:
            pass
        return item
        
        # last_item = None
        # while not self.result_queue.empty():
        #     try:
        #         last_item = self.result_queue.get_nowait()
        #     except queue.Empty:
        #         break  # This shouldn't happen, but just in case
        # return last_item

    def terminate(self):
        if self.process and self.process.is_alive():
            self.process.terminate()
            self.process.join()