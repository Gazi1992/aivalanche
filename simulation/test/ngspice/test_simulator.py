#%% Imports
from simulation.ngspice import simulator
import os

file = 'nmos_bsim4_example.cir'

file_path = os.path.abspath(file)

sim = simulator()

sim.simulate_single_file(file_path = file_path)

