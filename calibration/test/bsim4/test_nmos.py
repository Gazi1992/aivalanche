from calibration import Calibration


reference_data_file = '../../src/templates/bsim4/nmos/reference_data.json'
parameters_file = '../../src/templates/bsim4/nmos/parameters.csv'
testbenches_file = '../../src/templates/bsim4/nmos/testbenches.json'
dut_file = '../../../src/templates/bsim4/nmos/dut.cir'
dut_name = 'dut'
optimizer = 'differential_evolution'
simulator = 'ngspice'
results_dir = 'results'



calibration = Calibration(reference_data_file = reference_data_file,
                          parameters_file = parameters_file,
                          testbenches_file = testbenches_file,
                          dut_file = dut_file,
                          dut_name = dut_name,
                          results_dir = results_dir,
                          simulator = simulator,
                          optimizer = optimizer)

calibration.run_default_simulation(plot = True)