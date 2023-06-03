#%% Imports
from reference_data import Reference_data
from reference_data.visualization import plot_all_groups
from testbench.ngspice import Ngspice_testbench_compiler


#%% get a reference data dataframe
ref_data_file = 'nmos_output_transfer.json'

# initialize the parser
ref_data = Reference_data(ref_data_file)

# get the groups, curves and all the data together
groups = ref_data.groups
curves = ref_data.curves
data = ref_data.data

# plot all groups
# plot_all_groups(data)


#%% build testbenches for all the rows of the dataframe
testbenches_file = 'testbenches_example.json'

testbench_compiler = Ngspice_testbench_compiler(testbenches_file = testbenches_file,
                                                reference_data = data,
                                                dut_file = 'dut.cir',
                                                dut_name = 'dut',
                                                model_parameters={'vth0': 0.1, 'ua': 10})

testbench_compiler.create_testbenches()

