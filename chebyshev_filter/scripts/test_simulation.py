from simulation.ngspice import Ngspice_simulator
from simulation.ngspice.visualization import plot_mosfet_output_characteristic, plot_mosfet_transfer_characteristic, plot_diode_characteristic
import os, shutil
from filter import parse_results_file, plot_magnitude, plot_phase

#%% Variables
results_path = os.path.abspath('../results')
inputs_path = os.path.abspath('../inputs')
test_file = os.path.join(inputs_path, 'test.cir')


#%% Test simulation
working_dir = os.path.join(results_path, 'temp')
results_file_name = os.path.join(working_dir, 'filter_response.txt')

sim = Ngspice_simulator()
sim.simulate_single_file(file_path = test_file, results_dir = working_dir)
results = parse_results_file(results_file_name)

# if os.path.exists(working_dir):
#     shutil.rmtree(working_dir, ignore_errors=True)
    
plot_magnitude(results)
plot_phase(results)