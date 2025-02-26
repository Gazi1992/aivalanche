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

        self.parameters_node = self.app.subnodes[1].subnodes[3]
        self.device_node = self.app.subnodes[1].subnodes[1]

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

    def extract_results(self, parameters, plot = False):
        sim_results = {}

        # Add parameters to results
        sim_results['parameters'] = parameters

        # Get power
        sim_results['power'] = abs(self.device_node.cdev.smat.lr[1][1])**2

        # Get the zfield
        z_field_path = os.path.abspath('zfield_data.txt')
        view = self.device_node.findorcreateview()
        view.viewzfield(1,0,1,20,255,0,6,0,2,0)
        view.exportdata(z_field_path, "%10.6f")
        self.exec_cmd()
        z_field = self.parse_matrix_file(z_field_path)
        os.remove(z_field_path)
        sim_results['z_field'] = z_field

        # Get profile
        profile = self.get_taper_profile(parameters)
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

    def get_taper_profile(self, parameters):
        # Define the points
        x = np.array([0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0])
        x = x * 7 + 2
        y = np.array([7, parameters['w1'], parameters['w2'], parameters['w3'],
                      parameters['w4'], parameters['w5'], parameters['w6'],
                      parameters['w7'], parameters['w8'], parameters['w9'], 0.5]) / 2

        # Create cubic spline
        cs = CubicSpline(x, y)

        # Create points for smooth curve
        x_smooth = np.linspace(min(x), max(x), 200)
        y_smooth = cs(x_smooth)

        # Add first point
        x_smooth = np.insert(x_smooth, 0, 0)
        y_smooth = np.insert(y_smooth, 0, y_smooth[0])

        # Add last point
        x_smooth = np.append(x_smooth, 11)
        y_smooth = np.append(y_smooth, y_smooth[-1])

        # Add the bottom path
        x_smooth = np.append(x_smooth, np.flip(x_smooth))
        y_smooth = np.append(y_smooth, -np.flip(y_smooth))

        # Build 2d array
        profile = np.hstack((x_smooth.reshape(-1, 1), y_smooth.reshape(-1, 1)))

        return profile

    def simulate_parameters(self, parameters: dict = None, overwrite_results = False):
        if parameters is not None:
            self.update_parameters(parameters)
            self.simulate()
            sim_results = self.extract_results(parameters)
            if overwrite_results:
                self.sim_results = sim_results
            return sim_results

    def simulate_multiple_parameters(self, parameters: list[dict] = None, overwrite_results = False):
        if parameters is not None:
            sim_results = []
            for p in tqdm(parameters, desc = "Simulating"):
                result = self.simulate_parameters(p)
                sim_results.append(result)
            if overwrite_results:
                self.sim_results = sim_results
            return sim_results
