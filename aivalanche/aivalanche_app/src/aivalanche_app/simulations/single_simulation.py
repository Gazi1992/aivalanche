from multiprocessing import Process, Queue
from calibration.Calibration import Calibration
import queue

class single_simulation:
    def __init__(self, simulation_input = None):
        self.simulation_input = simulation_input
        self.process = None
        self.result_queue = Queue()

    def update_simulation_input(self, new_simulation_input):
        self.simulation_input = new_simulation_input
    
    def on_simulation_error(self, **kwargs):
        res = {'status': 'error',
               'model_id': self.simulation_input['model_id'],
               'error': kwargs['error']}
        self.result_queue.put(res)

    def on_simulation_finish(self, **kwargs):
        res = {'status': 'finish',
               'model_id': self.simulation_input['model_id'],
               'results_dir': self.simulation_input['results_dir'],
               'results': kwargs['results'],
               'loss': kwargs['loss']}
        self.result_queue.put(res)        
        
    def run(self):
        if self.simulation_input is None:
            self.result_queue.put(('error', "No simulation input provided"))
            return
        
        if not self.simulation_input['running_environment'] == 'local':
            self.result_queue.put(('error', "running_environment has to be 'local'"))
            return
        
        try:
            calibration = Calibration(reference_data = self.simulation_input['reference_data'],
                                      parameters = self.simulation_input['parameters'],
                                      testbenches = self.simulation_input['testbenches'],
                                      dut_file = self.simulation_input['dut_file'],
                                      dut_name = self.simulation_input['dut_name'],
                                      results_dir = self.simulation_input['results_dir'],
                                      simulator_config = self.simulation_input['simulator_config'],
                                      cost_function_config = self.simulation_input['cost_function_config'],
                                      running_environment = self.simulation_input['running_environment'])
            results = calibration.run_default_simulation(plot = False, delete_files = False, print_output = False)
            self.on_simulation_finish(results = results['data'], loss = results['error_metric'])
        except Exception as e:
            self.on_simulation_error(error = str(e))

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