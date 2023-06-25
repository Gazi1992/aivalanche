#%% Imports
from simulation.ngspice import Ngspice_simulator
from simulation.ngspice.visualization import plot_mosfet_output_characteristic, plot_mosfet_transfer_characteristic, plot_diode_characteristic
import os

#%% Select the tests
test_bsim4_nmos_output_characteristic = True
test_bsim4_nmos_transfer_characteristic = False
test_diode_characteristic = False
test_bsim4_nmos_transfer_characteristic_dicrete_values = False


#%% Test nmos bsim 4 output characteristic
if test_bsim4_nmos_output_characteristic:
    sim_file = './bsim4/nmos/output_characteristic.cir'
    sim_file_path = os.path.abspath(sim_file)
    
    results_file_name = 'output_characteristic_results.txt'
    
    sim = Ngspice_simulator()
    results = sim.simulate_single_file(file_path = sim_file_path,
                                       extract_results = True,
                                       compact = True,
                                       results_file_name = results_file_name,
                                       simulation_type = 'dc_sweep')
    
    for idx, row in results.iterrows():
        plot_mosfet_output_characteristic(row)


#%% Test nmos bsim 4 transfer characteristic
if test_bsim4_nmos_transfer_characteristic:
    sim_file = './bsim4/nmos/transfer_characteristic.cir'
    sim_file_path = os.path.abspath(sim_file)
    
    results_file_name = 'transfer_characteristic_results.txt'
    
    sim = Ngspice_simulator()
    results = sim.simulate_single_file(file_path = sim_file_path,
                                       extract_results = True,
                                       compact = True,
                                       results_file_name = results_file_name,
                                       simulation_type = 'dc_sweep')
    
    for idx, row in results.iterrows():
        plot_mosfet_transfer_characteristic(row)


#%% Test diode characteristic
if test_diode_characteristic:
    sim_file = './diode/diode_characteristic.cir'
    sim_file_path = os.path.abspath(sim_file)
    
    results_file_name = 'diode_characteristic_results.txt'
    
    sim = Ngspice_simulator()
    results = sim.simulate_single_file(file_path = sim_file_path,
                                       extract_results = True,
                                       compact = True,
                                       results_file_name = results_file_name,
                                       simulation_type = 'dc_sweep')
    
    for idx, row in results.iterrows():
        plot_diode_characteristic(row)


#%% Test nmos bsim 4 transfer characteristic discrete values
if test_bsim4_nmos_transfer_characteristic_dicrete_values:
    sim_file = './bsim4/nmos/transfer_characteristic_discrete_values.cir'
    sim_file_path = os.path.abspath(sim_file)
    
    results_file_name = 'transfer_characteristic_discrete_values_results.csv'
    
    sim = Ngspice_simulator()
    results = sim.simulate_single_file(file_path = sim_file_path,
                                       extract_results = True,
                                       compact = True,
                                       results_file_name = results_file_name,
                                       simulation_type = 'dc_list')
    
    for idx, row in results.iterrows():
        plot_mosfet_transfer_characteristic(row)
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        