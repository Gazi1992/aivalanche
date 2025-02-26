#%% Imports
import numpy as np, os, sys, psutil
from utils import plot_z_field_and_profile
from scipy.interpolate import CubicSpline
from tqdm import tqdm

# Add the fimmwave path to the system path
sys.path.append(r"C:\Program Files\PhotonD\Fimmwave\Scripts\Python")
import fimmwavelib as fimm

#%% The simulator class
class Fimmwave_simulator():

    def __init__(self, fimmwave_path = None, port = 5101, project_path = None, device: str = 'taper'):

        self.fimmwave_path = os.path.join("C:/", 'Program Files', 'PhotonD', 'Fimmwave', 'bin64', 'fimmwave.exe') or fimmwave_path
        self.port = port
        self.project_path = project_path
        self.app = None
        self.device = device

    def start(self):
        self.app = fimm.start_fimmwave(self.fimmwave_path, self.port)

    def connect(self):
        original_dir = os.getcwd()
        if self.is_fimmwave_running():
            self.app = fimm.connect_to_fimmwave('localhost', self.port)
        else:
            self.start()
        os.chdir(original_dir)

    def disconnect(self):
        fimm.disconnect_fimmwave()

    def is_fimmwave_running(self):
        for proc in psutil.process_iter(['name']):
            try:
                # Check if process name contains the given string
                if proc.info['name'].lower() == 'fimmwave.exe':
                    return True
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass
        return False

    def open_project(self, project_path = None):
        self.project_path = self.project_path or project_path
        self.app.openproject(self.project_path, "")

        # Add the Exec() to send the command to the simulator, because the openproject is only using AddCmd()
        self.exec_cmd()

        self.parameters_node = self.app.subnodes[1].subnodes[1]
        self.device_node = self.app.subnodes[1].subnodes[2]

    def exec_cmd(self):
        from fimmwavelib import pdAppConnector
        pdAppConnector.Exec('')

    def update_parameters(self, parameters: dict = None):
        if parameters is not None:
            for key, value in parameters.items():
                self.parameters_node.setvariable(key,f"{value}")
        self.exec_cmd()

    def simulate(self):
        self.device_node.update() # run simulation
        self.exec_cmd()

    def extract_results(self, parameters, plot = False, fetch_z_field = True):
        sim_results = {}

        # Add parameters to results
        sim_results['parameters'] = parameters

        # Get power
        sim_results['power'] = abs(self.device_node.cdev.smat.lr[1][1])**2

        if fetch_z_field:
            # Get the zfield
            z_field_path = os.path.abspath('zfield_data.txt')
            view = self.device_node.findorcreateview()
            view.viewzfield(1,0,1,20,255,0,6,0,2,0)
            view.exportdata(z_field_path, "%10.6f")
            self.exec_cmd()
            z_field = self.parse_matrix_file(z_field_path)
            os.remove(z_field_path)
        else:
            z_field = None
        sim_results['z_field'] = z_field

        # Get profile
        profile = self.get_splitter_profile(parameters)
        sim_results['profile'] = profile

        if plot:
            plot_z_field_and_profile(z_field, profile)

        return sim_results

    def parse_matrix_file(self, file_path):
        with open(file_path, 'r') as f:
            lines = f.readlines()

        sections = []
        i = 0
        while i < len(lines):
            line = lines[i].strip()

            if line.startswith('SECTION'):
                # Skip header lines
                i += 6  # Skip dimension and matrix description lines

                # Get y coordinates
                y_coords = np.array([float(x) for x in lines[i].split()[1:]])
                i += 1

                # Read section data until empty line or new section
                section_data = []
                while i < len(lines) and lines[i].strip() and not lines[i].startswith('SECTION'):
                    row = [float(x) for x in lines[i].split()]
                    section_data.append(row)
                    i += 1

                # Process section data
                section_data = np.array(section_data)
                x_coords = section_data[:, 0]
                values = section_data[:, 1:]

                # Create array of coordinates and values
                result = []
                for j, x in enumerate(x_coords):
                    for k, y in enumerate(y_coords):
                        result.append([x, y, values[j,k]])
                result = np.array(result)

                sections.append({'x': x_coords,
                                 'x_size': len(x_coords),
                                 'y': y_coords,
                                 'y_size': len(y_coords),
                                 'values': result})
            else:
                i += 1

        all_data = sections[0]
        if len(sections) > 1:
            for s in sections[1:]:
                all_data['x'] = np.append(all_data['x'], s['x'][1:])
                all_data['x_size'] = all_data['x_size'] + s['x_size'] - 1
                all_data['values'] = np.vstack((all_data['values'], s['values'][s['y_size']:, :]))
        all_data['sections'] = sections
        return all_data

    def calculate_sine_path(self, x, y_start, y_end):
        return y_start * (1 - np.sin(np.pi*x/2)**2) + y_end * np.sin(np.pi*x/2)**2

    def get_splitter_profile(self, parameters):
        w1 = 1.5
        d2 = 10

        # left section up
        x_left = [0, parameters['l1']]
        y_left = [w1/2, parameters['w2']/2]

        # middle section up
        x_middle = [parameters['l1'], parameters['l1'] + parameters['l2'] / 2, parameters['l1'] + parameters['l2']]
        y_middle = [parameters['w3']/2, parameters['w4']/2, parameters['w3']/2]

        # right section up
        x_right = np.linspace(start = 0,
                              stop = 1,
                              num = 101)
        y_right_offset = self.calculate_sine_path(x_right, parameters['d1']/2, d2/2)

        width_right = self.calculate_sine_path(x_right, parameters['w2'], w1)

        y_right_up = y_right_offset + width_right/2
        y_right_down = y_right_offset - width_right/2

        x_right = x_right * parameters['l3'] + parameters['l1'] + parameters['l2']

        x_top = np.hstack((x_left, x_middle, x_right, np.flip(x_right)))
        y_top = np.hstack((y_left, y_middle, y_right_up, np.flip(y_right_down)))

        x_down = np.flip(x_top)
        y_down = np.flip(-y_top)

        x = np.hstack((x_top, x_down, x_top[0]))
        y = np.hstack((y_top, y_down, y_top[0]))

        # import matplotlib.pyplot as plt
        # fig, ax = plt.subplots(nrows=1, ncols=1, figsize=(8, 4.5))
        # ax.plot(x, y)
        # plt.show()

        # Build 2d array
        profile = np.hstack((x.reshape(-1, 1), y.reshape(-1, 1)))

        return profile

    def is_valid_geometry(self, parameters):
        if parameters['d1'] < parameters['w2']:
            return False
        if parameters['w3'] < parameters['w2']:
            return False
        if parameters['w3'] < parameters['w2'] + parameters['d1']:
            return False
        return True

    def calculate_geometry_penalty(self, parameters):
        penalty = 0
        if parameters['d1'] < parameters['w2']:
            penalty += parameters['w2'] - parameters['d1']
        if parameters['w3'] < parameters['w2']:
            penalty += parameters['w2'] - parameters['w3']
        if parameters['w3'] < parameters['w2'] + parameters['d1']:
            penalty += parameters['w2'] + parameters['d1'] - parameters['w3']
        return penalty

    def simulate_parameters(self, parameters: dict = None, overwrite_results = False, validate_geometry = True, fetch_z_field = True, **kwargs):
        if parameters is not None:
            if validate_geometry and not self.is_valid_geometry(parameters):
                sim_results = {'parameters': parameters,
                               'power': None,
                               'penalty': self.calculate_geometry_penalty(parameters)}
            else:
                self.update_parameters(parameters)
                self.simulate()
                sim_results = self.extract_results(parameters, fetch_z_field = fetch_z_field)
            if overwrite_results:
                self.sim_results = sim_results
            return sim_results

    def simulate_multiple_parameters(self, parameters: list[dict] = None, overwrite_results = False, validate_geometry = True, fetch_z_field = True, **kwargs):
        if parameters is not None:
            sim_results = []
            for p in tqdm(parameters, desc = "Simulating"):
                result = self.simulate_parameters(p, validate_geometry = validate_geometry, fetch_z_field = fetch_z_field, **kwargs)
                sim_results.append(result)
            if overwrite_results:
                self.sim_results = sim_results
            return sim_results
