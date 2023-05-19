#%% Imports
from simulation.ngspice import simulator
from simulation.ngspice.visualization import plot_mosfet_output_characteristic, plot_mosfet_transfer_characteristic, plot_diode_characteristic
import os

#%% Select the tests
test_bsim4_nmos_output_characteristic = True
test_bsim4_nmos_transfer_characteristic = True
test_diode_characteristic = True

#%% Test nmos bsim 4 output characteristic
if test_bsim4_nmos_output_characteristic:
    sim_file = './bsim4/nmos/output_characteristic.cir'
    sim_file_path = os.path.abspath(sim_file)
    
    results_file_name = 'output_characteristic_results.txt'
    
    sim = simulator()
    res = sim.simulate_single_file(file_path = sim_file_path,
                                    extract_results = True,
                                    results_file_name = results_file_name,
                                    characteristic_type = 'output_characteristic')
    
    for idx, row in res.iterrows():
        plot_mosfet_output_characteristic(row)


#%% Test nmos bsim 4 transfer characteristic
if test_bsim4_nmos_transfer_characteristic:
    sim_file = './bsim4/nmos/transfer_characteristic.cir'
    sim_file_path = os.path.abspath(sim_file)
    
    results_file_name = 'transfer_characteristic_results.txt'
    
    sim = simulator()
    res = sim.simulate_single_file(file_path = sim_file_path,
                                    extract_results = True,
                                    results_file_name = results_file_name,
                                    characteristic_type = 'transfer_characteristic')
    
    for idx, row in res.iterrows():
        plot_mosfet_transfer_characteristic(row)


#%% Test diode characteristic
if test_diode_characteristic:
    sim_file = './diode/diode_characteristic.cir'
    sim_file_path = os.path.abspath(sim_file)
    
    results_file_name = 'diode_characteristic_results.txt'
    
    sim = simulator()
    res = sim.simulate_single_file(file_path = sim_file_path,
                                    extract_results = True,
                                    results_file_name = results_file_name,
                                    device = 'diode',
                                    characteristic_type = 'dc_characteristic')
    
    for idx, row in res.iterrows():
        plot_diode_characteristic(row)

