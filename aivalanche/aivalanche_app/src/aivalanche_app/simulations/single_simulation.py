from PySide6.QtCore import QThread, Signal
from calibration.Calibration import Calibration
import time

class single_simulation(QThread):   
    simulation_start = Signal(object)
    simulation_progress = Signal(object)
    simulation_finish = Signal(object)

    def __init__(self, on_start: callable = None, on_progress: callable = None, on_finish: callable = None, db_type: str = 'local_files', simulation_input: dict = None):
        super().__init__()
        if on_start is not None:
            self.simulation_start.connect(on_start)
        if on_progress is not None:
            self.simulation_progress.connect(on_progress)
        if on_finish is not None:
            self.simulation_finish.connect(on_finish)
        self.db_type = db_type
        self.simulation_input = simulation_input
    
    def update_simulation_input(self, new_simulation_input: dict = None):
        self.simulation_input = new_simulation_input
    
    def run(self):
        if self.simulation_input is not None:
            if self.db_type in ['local_files', 'local_mysql_db']: 
                self.simulation_start.emit(self.simulation_input)
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
                except Exception as e:
                    print('Error at single simulation!')
                    print(e)
                    results = None
                
                self.simulation_finish.emit(results)

