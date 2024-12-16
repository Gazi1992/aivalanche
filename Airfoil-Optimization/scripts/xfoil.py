#%% Imports
from __future__ import division
import subprocess as subp
import numpy as np, pandas as pd, os, warnings, matplotlib.pyplot as plt, uuid, re
from nurbs import Nurbs
from visualizations import plot_airfoil, plot_polar, plot_pressure_distribution, plot_boundary_layer
from screeninfo import get_monitors
from copy import copy
from subprocess import DEVNULL

#%% xfoil settings
class XFoilSettings:
    """Settings container for XFOIL analysis"""
    def __init__(self, timeout = 5, n_iter = 1000, n_crit = 9, init_bl_loc = 0.05, working_dir = ".", parameters = None):
        self.timeout = timeout       # seconds
        self.n_iter = n_iter      # maximum iterations
        self.n_crit = n_crit        # critical amplification ratio
        self.init_bl_loc = init_bl_loc
        self.working_dir = working_dir  # working directory for temp files
        if not os.path.exists(working_dir):
            os.mkdir(working_dir)
        self.parameters = parameters or {
            'ta_u': 0.1584,   # Upper surface leading edge tangent
            'ta_l': 0.1565,   # Lower surface leading edge tangent
            'tb_u': 2.1241,   # Upper surface trailing edge tangent
            'tb_l': 1.8255,   # Lower surface trailing edge tangent
            'alpha_b': 11.6983,  # Trailing edge angle
            'alpha_c': 3.8270    # Camber angle
        }

#%% xfoil analyzer
class XFoilAnalyzer:
    def __init__(self, settings = None):
        self.initialize_variables(settings)
    
    def initialize_variables(self, settings = None):
        self.settings = settings or XFoilSettings()
        self.airfoil = None
        self.airfoil_path = None
        self.nurbs_airfoil = None  # Store NURBS object for geometric analysis
        self.geometric_properties = None
        self.results = None
        self.sim_output = None
        self.sim_error = None
        
        self.max_thickness_upper_limit = 0.18
        self.max_thickness_lower_limit = 0.08
        self.max_thickness_metric = 0
        
        self.max_thickness_location_upper_limit = 0.4
        self.max_thickness_location_lower_limit = 0.2
        self.max_thickness_location_metric = 0
        
        self.leading_edge_radius_upper_limit = 0.04
        self.leading_edge_radius_lower_limit = 0.01
        self.leading_edge_radius_metric = 0
        
        self.max_curvature_upper_limit = 60
        self.max_curvature_lower_limit = 0
        self.max_curvature_metric = 0
        
        self.trailing_edge_angle_upper_limit = 15
        self.trailing_edge_angle_lower_limit = 5
        self.trailing_edge_angle_metric = 0
        
        self.geometry_metric = 0
        self.convergence_metric = 0
        self.ld_metric = 0
        self.total_metric = 0
        
        self.constraints_met = False
        
    def format_coordinates(self, airfoil):
        """
        Convert airfoil coordinates to XFOIL format
        
        Args:
            airfoil: Array containing [x_lower, y_lower, x_upper, y_upper]
        
        Returns:
            String with coordinates in XFOIL format (x y pairs, one per line)
        """
        x_l = airfoil[0]    # x-coordinates of lower surface
        y_l = airfoil[1]    # y-coordinates of lower surface
        x_u = airfoil[2]    # x-coordinates of upper surface
        y_u = airfoil[3]    # y-coordinates of upper surface
        
        # Combine coordinates, going from trailing edge up to leading edge
        # and then back to trailing edge along upper surface
        xcoords = np.append(x_l[::-1], x_u[1:])
        ycoords = np.append(y_l[::-1], y_u[1:])
        
        # Create array of (x,y) pairs
        coordslist = np.array((xcoords, ycoords)).T
        
        # Format as strings with x y pairs (note: switched order of coord[0], coord[1])
        coordstrlist = ["{:.6f} {:.6f}".format(coord[0], coord[1])
                       for coord in coordslist]
        
        return '\n'.join(coordstrlist)
    
    def generate_airfoil(self, parameters: dict = None, plot: bool = False, plot_alpha: float = None):
        """Generate airfoil using NURBS"""
        parameters = parameters or self.settings.parameters
        airfoil = Nurbs(parameters)
        self.nurbs_airfoil = airfoil
        self.airfoil = airfoil._spline()
        
        if plot:
            plot_airfoil(self.airfoil, show_panels=True, alpha=plot_alpha)
        
    def write_airfoil_file(self, coords, filename="airfoil.dat"):
        """
        Write airfoil coordinates to file
        
        Args:
            coords: Airfoil coordinates
            filename: Name of the file to write (can be absolute or relative path)
        """
        # Ensure working directory exists
        os.makedirs(self.settings.working_dir, exist_ok=True)
        
        # Get absolute paths
        if os.path.isabs(filename):
            filepath = filename
            self.airfoil_path = "./airfoil.dat"  # Use relative path for XFOIL
        else:
            filepath = os.path.join(self.settings.working_dir, filename)
            self.airfoil_path = "./airfoil.dat"  # Use relative path for XFOIL
        
        # Write coordinates
        with open(filepath, 'w') as f:
            f.write("Generated Airfoil\n")
            f.write(self.format_coordinates(coords))
        
        # If file is not in working directory, copy it there with relative name
        if os.path.dirname(filepath) != self.settings.working_dir:
            import shutil
            shutil.copy2(filepath, os.path.join(self.settings.working_dir, "airfoil.dat"))
        
        return filepath

    def run_xfoil_command(self, commands):
        """
        Run XFOIL with given commands
        
        Args:
            commands: List of XFOIL commands to execute
        """
        
        # Create working directory if it doesn't exist
        os.makedirs(self.settings.working_dir, exist_ok=True)
        
        # Change to working directory
        original_dir = os.getcwd()
        os.chdir(self.settings.working_dir)
        
        try:
            in_path = f'xfoil_input_{str(uuid.uuid4())[-8:]}.in'
            # Write commands using relative paths
            with open(in_path, 'w') as f:
                for cmd in commands:
                    # Convert absolute paths to relative for output files
                    if 'DUMP' in cmd or 'CPWR' in cmd or 'PACC' in cmd:
                        # Get just the filename from the path
                        cmd = cmd.split()
                        filename = os.path.basename(cmd[-1])
                        cmd[-1] = filename
                        cmd = ' '.join(cmd)
                    f.write(cmd + "\n")
            
            # Run XFOIL
            try:
                if os.name == 'nt':  # Windows
                    process = subp.Popen(f"xfoil.exe < {in_path}", 
                                        shell=True, stdout=subp.PIPE, 
                                        stderr=DEVNULL)
                else:  # Linux/Mac
                    process = subp.Popen(f"xfoil < {in_path}", 
                                        shell=True, stdout=subp.PIPE, 
                                        stderr=DEVNULL)
                
                output, error = process.communicate(timeout=self.settings.timeout)
                self.sim_output = output
                self.sim_error = error
                return True
                
            except subp.TimeoutExpired:
                process.kill()
                print("XFOIL process timed out")
                return False
                
        finally:
            # Clean up input file
            if os.path.exists(in_path):
                os.remove(in_path)
            
            # Change back to original directory
            os.chdir(original_dir)

    def parse_output(self):
        try:
            # Parse results from stdout
            output_str = self.sim_output.decode('utf-8')
            self.parse_stdout_polar(output_str)
            lines = output_str.split('\n')
            for i, line in enumerate(lines):
                if 'alpha    CL        CD       CDp       CM     Top_Xtr  Bot_Xtr' in line:
                    data_line = lines[i + 1].split()
                    if len(data_line) >= 7:
                        return {
                            'convergence': True,
                            'alpha': float(data_line[0]),
                            'cl': float(data_line[1]),
                            'cd': float(data_line[2]),
                            'cdp': float(data_line[3]),
                            'cm': float(data_line[4]),
                            'Top_xtr': float(data_line[5]),
                            'Bot_xtr': float(data_line[6]),
                            'ld_ratio': float(data_line[1])/float(data_line[2])
                        }
        except:
            return None        

    def parse_stdout_polar(self, lines):
        """Converts polar 'PLIS' data to array"""    
        def clean_split(s): return re.split('\s+', s.replace(os.linesep,''))[1:]

        # Find location of data from ---- divider
        for i, line in enumerate(lines):
            if re.match('\s*---', line):
                dividerIndex = i
        
        # What columns mean
        data_header = clean_split(lines[dividerIndex-1])

        # Clean info lines
        info = ''.join(lines[dividerIndex-4:dividerIndex-2])
        info = re.sub("[\r\n\s]","", info)
        # Parse info with regular expressions
        def p(s): return float(re.search(s, info).group(1))
        infodict = {
         'xtrf_top': p("xtrf=(\d+\.\d+)"),
         'xtrf_bottom': p("\(top\)(\d+\.\d+)\(bottom\)"),
         'Mach': p("Mach=(\d+\.\d+)"),
         'Ncrit': p("Ncrit=(\d+\.\d+)"),
         'Re': p("Re=(\d+\.\d+e\d+)")
        }

        # Extract, clean, convert to array
        datalines = lines[dividerIndex+1:-2]
        data_array = np.array(
        [clean_split(dataline) for dataline in datalines], dtype='float')

        return data_array, data_header, infodict

    def _run_single_alpha(self, alpha, Re, Mach=0.0):
       """Run analysis for single angle of attack"""
       
       output_basename = f"polar{str(uuid.uuid4())[-8:]}.txt"
       output_file = os.path.join(self.settings.working_dir, output_basename)
       
       if os.path.exists(output_file):
           os.remove(output_file)
           
       commands = [
           f"LOAD {self.airfoil_path}",
            # "PLOP",
            # "G", 
            # "",
           "PANE",
           "OPER",
           f"Visc {Re}",
           f"MACH {Mach}",
           f"ITER {self.settings.n_iter}",
           "PACC",
           f"{output_basename}",
           "",
           f"ALFA {alpha}",
           "",
           "quit"
       ]
       
       success = self.run_xfoil_command(commands)
       # self.parse_output()
       
       if success and os.path.exists(output_file):
            try:
                data = np.loadtxt(output_file, skiprows=12)
                if len(data) == 0:
                    self.results = {'convergence': False}
                    return
                
            except Exception as e:
                print(f"Error in single alpha analysis: {str(e)}")
                self.results = {'convergence': False}
                return
                
            finally:
                if os.path.exists(output_file):
                    os.remove(output_file)
       else:
           self.results = {'convergence': False}
           return
       
       results = {
            'convergence': True,
            'alpha': data[0],
            'cl': data[1],
            'cd': data[2],
            'cdp': data[3],
            'cm': data[4],
            'Top_xtr': data[5],
            'Bot_xtr': data[6],
            'ld_ratio': data[1]/data[2]
        }
       
       self.results = results
    
    def _run_alpha_range(self, alpha_range, Re, Mach=0.0):
        """Run analysis for range of angles of attack"""
        output_basename = f"polar{str(uuid.uuid4())[-8:]}.txt"
        output_file = os.path.join(self.settings.working_dir, output_basename)
        
        if os.path.exists(output_file):
            os.remove(output_file)
            
        commands = [
            "PLOP",              # Enter plot options menu
            "G F",                 # Turn off all graphics
            "",                  # Exit plot options menu
            f"LOAD {self.airfoil_path}",
            "PANE",
            "OPER",
            f"Visc {Re}",
            f"MACH {Mach}",
            f"ITER {self.settings.n_iter}",
            "PACC",
            f"{output_basename}",
            "",
            f"ASEQ {alpha_range[0]} {alpha_range[1]} {alpha_range[2]}",
            "",
            "quit"
        ]
        
        success = self.run_xfoil_command(commands)
        
        if success and os.path.exists(output_file):
            try:
                data = np.loadtxt(output_file, skiprows=12)
                if len(data) == 0:
                    self.results = {'convergence': False}
                    return
                    
                valid_mask = ~np.isnan(data).any(axis=1) & (data[:, 2] > 0)
                if not np.any(valid_mask):
                    self.results = {'convergence': False}
                    return
                
                data = data[valid_mask]
                n_valid = len(data)
                n_total = int((alpha_range[1] - alpha_range[0])/alpha_range[2]) + 1
                print(f"Converged {n_valid} out of {n_total} points")
                
                results = {
                    'convergence': True,
                    'alpha': data[:, 0],
                    'cl': data[:, 1],
                    'cd': data[:, 2],
                    'cdp': data[:, 3],
                    'cm': data[:, 4],
                    'Top_xtr': data[:, 5],
                    'Bot_xtr': data[:, 6]
                }
                
                results['cl_max'] = np.max(results['cl'])
                results['cd_min'] = np.min(results['cd'])
                results['ld_ratio'] = results['cl']/results['cd']
                results['ld_max'] = np.max(results['ld_ratio'])
                results['alpha_opt'] = results['alpha'][np.argmax(results['ld_ratio'])]
                
                self.results = results
                
            except Exception as e:
                print(f"Error in alpha range analysis: {str(e)}")
                self.results = {'convergence': False}
                
            finally:
                if os.path.exists(output_file):
                    os.remove(output_file)
        else:         
            self.results = {'convergence': False}
    
    def _run_alpha_list(self, alpha_list, Re, Mach=0.0):
        """Run analysis for a list of specific angles of attack"""
        output_basename = f"polar{str(uuid.uuid4())[-8:]}.txt"
        output_file = os.path.join(self.settings.working_dir, output_basename)
        valid_results = []
        
        for alpha in alpha_list:
            if os.path.exists(output_file):
                os.remove(output_file)
                
            commands = [
                "PLOP",              # Enter plot options menu
                "G F",                 # Turn off all graphics
                "",                  # Exit plot options menu
                f"LOAD {self.airfoil_path}",
                "PANE",
                "OPER",
                f"Visc {Re}",
                f"MACH {Mach}",
                f"ITER {self.settings.n_iter}",
                "PACC",
                f"{output_basename}",
                "",
                f"ALFA {alpha}",
                "",
                "quit"
            ]
            
            success = self.run_xfoil_command(commands)
            
            if success and os.path.exists(output_file):
                try:
                    if os.path.getsize(output_file) == 0:
                        print(f"No convergence for alpha = {alpha}")
                        continue
                        
                    with warnings.catch_warnings():
                        warnings.simplefilter("ignore")
                        data = np.loadtxt(output_file, skiprows=12)
                    
                    if len(data.shape) == 1:
                        if not np.isnan(data).any() and data[2] > 0:
                            valid_results.append(data)
                    elif len(data) > 0:
                        if not np.isnan(data[0]).any() and data[0, 2] > 0:
                            valid_results.append(data[0])
                            
                except Exception as e:
                    print(f"No convergence for alpha = {alpha}")
                    continue
                    
                finally:
                    if os.path.exists(output_file):
                        os.remove(output_file)
        
        if not valid_results:
            self.results = {'convergence': False}
            return
            
        data = np.array(valid_results)
        n_valid = len(data)
        n_total = len(alpha_list)
        
        print(f"Converged {n_valid} out of {n_total} points")
        
        results = {
            'convergence': True,
            'alpha': data[:, 0],
            'cl': data[:, 1],
            'cd': data[:, 2],
            'cdp': data[:, 3],
            'cm': data[:, 4],
            'Top_xtr': data[:, 5],
            'Bot_xtr': data[:, 6]
        }
        
        results['cl_max'] = np.max(results['cl'])
        results['cd_min'] = np.min(results['cd'])
        results['ld_ratio'] = results['cl']/results['cd']
        results['ld_max'] = np.max(results['ld_ratio'])
        results['alpha_opt'] = results['alpha'][np.argmax(results['ld_ratio'])]
        
        self.results = results
    
    def _run_pressure_distribution(self, alpha, Re, Mach=0.0):
        """Get pressure coefficient distribution"""
        output_basename = f"polar{str(uuid.uuid4())[-8:]}.txt"
        output_file = os.path.join(self.settings.working_dir, output_basename)
        
        commands = [
            "PLOP",              # Enter plot options menu
            "G F",                 # Turn off all graphics
            "",                  # Exit plot options menu
            f"LOAD {self.airfoil_path}",
            "PANE",
            "OPER",
            f"Visc {Re}",
            f"MACH {Mach}",
            f"ITER {self.settings.n_iter}",
            f"ALFA {alpha}",
            "CPWR",
            output_basename,
            "",
            "quit"
        ]
        
        success = self.run_xfoil_command(commands)
        
        if success and os.path.exists(output_file):
            try:
                data = np.loadtxt(output_file, skiprows=3)
                if len(data) == 0:
                    return {'convergence': False}
                    
                return {
                    'convergence': True,
                    'x': data[:, 0],
                    'cp': data[:, 1],
                    'upper': data[:, 0] <= 1.0,
                    'lower': data[:, 0] > 1.0
                }
            except Exception as e:
                print(f"Error in pressure distribution analysis: {str(e)}")
                return {'convergence': False}
            finally:
                if os.path.exists(output_file):
                    os.remove(output_file)
                    
        return {'convergence': False}
    
    def _run_boundary_layer(self, alpha, Re, Mach=0.0):
        """Get boundary layer properties"""
        output_basename = f"polar{str(uuid.uuid4())[-8:]}.txt"
        output_file = os.path.join(self.settings.working_dir, output_basename)
        
        if os.path.exists(output_file):
            os.remove(output_file)
        
        commands = [
            f"LOAD {self.airfoil_path}",
            "PANE",
            "OPER",
            f"Visc {Re}",
            f"MACH {Mach}",
            f"ITER {self.settings.n_iter}",
            f"ALFA {alpha}",
            "BL",
            f"DUMP {output_basename}",
            "",
            "quit"
        ]
        
        success = self.run_xfoil_command(commands)
        
        if success and os.path.exists(output_file):
            try:
                with open(output_file, 'r') as f:
                    lines = f.readlines()
                
                if len(lines) <= 1:
                    return {'convergence': False}
                    
                data = []
                for line in lines[1:]:
                    try:
                        values = [float(x) for x in line.strip().split()]
                        if len(values) >= 8:
                            data.append(values[:8])
                    except ValueError:
                        continue
                        
                if len(data) == 0:
                    return {'convergence': False}
                        
                data = np.array(data)
                
                x_coords = data[:, 1]
                sep_idx = np.where(np.diff(x_coords) < -0.5)[0]
                if len(sep_idx) > 0:
                    sep_idx = sep_idx[0] + 1
                else:
                    y_coords = data[:, 2]
                    sep_idx = len(y_coords) // 2
                
                upper_data = data[:sep_idx]
                lower_data = data[sep_idx:]
                
                return {
                    'convergence': True,
                    'upper': {
                        's': upper_data[:, 0],
                        'x': upper_data[:, 1],
                        'y': upper_data[:, 2],
                        'Ue': upper_data[:, 3],
                        'Dstar': upper_data[:, 4],
                        'theta': upper_data[:, 5],
                        'Cf': upper_data[:, 6],
                        'H': upper_data[:, 7],
                    },
                    'lower': {
                        's': lower_data[:, 0],
                        'x': lower_data[:, 1],
                        'y': lower_data[:, 2],
                        'Ue': lower_data[:, 3],
                        'Dstar': lower_data[:, 4],
                        'theta': lower_data[:, 5],
                        'Cf': lower_data[:, 6],
                        'H': lower_data[:, 7],
                    }
                }
                
            except Exception as e:
                print(f"Error processing boundary layer data: {str(e)}")
                return {'convergence': False}
                
            finally:
                if os.path.exists(output_file):
                    os.remove(output_file)
        
        return {'convergence': False}
    
    def calculate_max_thickness_metric(self):
        
        max_thickness = self.geometric_properties['max_thickness']
            
        # Maximum thickness should be between 8-18% for typical subsonic airfoils
        if max_thickness < self.max_thickness_lower_limit:
            self.max_thickness_metric = self.max_thickness_lower_limit - max_thickness
        elif max_thickness > self.max_thickness_upper_limit:
            self.max_thickness_metric = max_thickness - self.max_thickness_upper_limit
        else:
            self.max_thickness_metric = 0

        return self.max_thickness_metric
    
    def calculate_max_thickness_location_metric(self):
        
        max_thickness_location = self.geometric_properties['max_thickness_location']
        
        # Maximum thickness location should be between 20-40% chord
        if max_thickness_location < self.max_thickness_location_lower_limit:
            self.max_thickness_location_metric = self.max_thickness_location_lower_limit - max_thickness_location
        elif  max_thickness_location > self.max_thickness_location_upper_limit:
            self.max_thickness_location_metric = max_thickness_location - self.max_thickness_location_upper_limit
        else:
            self.max_thickness_location_metric = 0
                    
        return self.max_thickness_location_metric

    def calculate_leading_edge_radius_metric(self):
        
        leading_edge_radius = self.geometric_properties['leading_edge_radius']
        
        if leading_edge_radius < self.leading_edge_radius_lower_limit:
            self.leading_edge_radius_metric = self.leading_edge_radius_lower_limit - leading_edge_radius
        elif leading_edge_radius > self.leading_edge_radius_upper_limit:
            self.leading_edge_radius_metric = leading_edge_radius - self.leading_edge_radius_upper_limit
        else:
            self.leading_edge_radius_metric = 0

        return self.leading_edge_radius_metric

    def calculate_max_curvature_metric(self):
        
        max_curvature = self.geometric_properties['max_curvature']
        
        if max_curvature > self.max_curvature_upper_limit:
            self.max_curvature_metric = max_curvature - self.max_curvature_upper_limit
        elif max_curvature < self.max_curvature_lower_limit:
            self.max_curvature_metric = self.max_curvature_lower_limit - max_curvature
        else:
            self.max_curvature_metric = 0
                        
        return self.max_curvature_metric

    def calculate_trailing_edge_angle_metric(self):
        
        trailing_edge_angle = self.geometric_properties['trailing_edge_angle']
        
        if trailing_edge_angle < self.trailing_edge_angle_lower_limit:
            self.trailing_edge_angle_metric = self.trailing_edge_angle_lower_limit - trailing_edge_angle
        elif trailing_edge_angle > self.trailing_edge_angle_upper_limit:
            self.trailing_edge_angle_metric = trailing_edge_angle - self.trailing_edge_angle_upper_limit
        else:
            self.trailing_edge_angle_metric = 0
            
        return self.trailing_edge_angle_metric

    def calculate_geometry_metric(self):
        self.calculate_max_thickness_metric()
        self.calculate_max_thickness_location_metric()
        self.calculate_leading_edge_radius_metric()
        self.calculate_max_curvature_metric()
        self.calculate_trailing_edge_angle_metric()
        
        self.geometry_metric = self.max_thickness_metric + \
                               self.max_thickness_location_metric + \
                               self.leading_edge_radius_metric + \
                               self.max_curvature_metric + \
                               self.trailing_edge_angle_metric
    
        if self.geometry_metric > 0:
            self.geometry_metric = 100 + self.geometry_metric                               
                               
        return self.geometry_metric

    def calculate_ld_metric(self):
        self.ld_metric = 1 / self.results['ld_ratio']
        return self.ld_metric

    def calculate_convergence_metric(self):
        if not self.results['convergence']:
            self.convergence_metric = 1e3
        elif pd.isna(self.results['ld_ratio']) or self.results['ld_ratio'] < 0:
            self.convergence_metric = 1e3
        else:
            self.convergence_metric = 0
            
        return self.convergence_metric

    def calculate_total_metric(self):
        
        self.calculate_convergence_metric()
        if self.convergence_metric > 0:
            self.total_metric = self.convergence_metric
            self.constraints_met = False
        else:        
            self.calculate_geometry_metric()
            self.calculate_ld_metric()
            if self.geometry_metric > 0:
                self.total_metric = self.geometry_metric
                self.constraints_met = False
            else:
                self.total_metric = self.ld_metric
                self.constraints_met = True
            
        return self.total_metric
    
    def analyze_airfoil(self, parameters, alpha, Re, Mach=0.0, 
                       get_pressure=False, get_boundary_layer=False, 
                       plot_airfoil=False, plot_at_alpha=None):
        """
        Main entry point for airfoil analysis
        
        Args:
            parameters: Dictionary of NURBS parameters
            alpha: Single value, tuple (start, end, step), or list of angles
            Re: Reynolds number
            Mach: Mach number
            get_pressure: Flag to calculate pressure distribution
            get_boundary_layer: Flag to calculate boundary layer properties
            plot_airfoil: Flag to plot the airfoil shape
            plot_at_alpha: Specific angle of attack for airfoil plot
        """
        self.generate_airfoil(parameters, plot=plot_airfoil, plot_alpha=plot_at_alpha)
        self.write_airfoil_file(self.airfoil)
        
        # Get geometric properties
        self.geometric_properties = self.nurbs_airfoil.get_geometric_properties()
        
        if not self.airfoil_path:
            return {'convergence': False}
            
        if isinstance(alpha, (list, np.ndarray)):
            self._run_alpha_list(alpha, Re, Mach)
        elif isinstance(alpha, tuple):
            self._run_alpha_range(alpha, Re, Mach)
        else:
            self._run_single_alpha(alpha, Re, Mach)
        
        # Add geometric properties and input parameters to results
        self.results.update({
            'geometry': self.geometric_properties,
            'parameters': parameters
        })    
        
        # if not self.results['convergence']:
        #     return results
            
        # if isinstance(alpha, (list, tuple, np.ndarray)):
        #     analysis_alpha = results['alpha'][0]
        # else:
        #     analysis_alpha = alpha
        
        # if get_pressure:
        #     pressure_results = self._run_pressure_distribution(analysis_alpha, Re, Mach)
        #     results['pressure'] = pressure_results
            
        # if get_boundary_layer:
        #     bl_results = self._run_boundary_layer(analysis_alpha, Re, Mach)
        #     results['boundary_layer'] = bl_results
            
        self.calculate_total_metric()
        
        
        self.results['metrics'] = {
                'max_thickness_metric': self.max_thickness_metric,
                'max_thickness_location_metric': self.max_thickness_location_metric,
                'leading_edge_radius_metric': self.leading_edge_radius_metric,
                'max_curvature_metric': self.max_curvature_metric,
                'trailing_edge_angle_metric': self.trailing_edge_angle_metric,
                'geometry_metric': self.geometry_metric,
                'convergence_metric': self.convergence_metric,
                'ld_metric': self.ld_metric,
                'total_metric': self.total_metric
            }
        
        self.results['constraints_met'] = self.constraints_met
        
        self.results['airfoil'] = self
        
        return self.results

    def plot_airfoil(self, ax = None, extra_airfoils=None, min_alpha=0.1, max_alpha=0.4):
        if ax is not None:
            plt.sca(ax)
        else:
            # Create figure
            fig, ax = plt.subplots(nrows=1, ncols=1, figsize=(10, 5))

        # Plot database entries if provided
        if extra_airfoils is not None:        
            n_entries = len(extra_airfoils)
            if n_entries > 0:
                alphas = np.linspace(min_alpha, max_alpha, n_entries)
                for i, item in enumerate(extra_airfoils):
                    x_l = item[0]
                    y_l = item[1]
                    x_u = item[2]
                    y_u = item[3]
                    ax.plot(x_u, y_u, 'black', alpha=alphas[i])
                    ax.plot(x_l, y_l, 'black', alpha=alphas[i])
    
        airfoil = self.airfoil
        
        x_l = airfoil[0]
        y_l = airfoil[1]
        x_u = airfoil[2]
        y_u = airfoil[3]
        
        ax.plot(x_u, y_u, 'purple', label='Upper surface')
        ax.plot(x_l, y_l, 'orange', label='Lower surface')

        xlim = (-0.1, 1.1)
        ylim = (-0.5, 0.5)
        ax.set_xlim(xlim)
        ax.set_ylim(ylim)
        
        plt.grid(True, linestyle='--', alpha=0.5)
        plt.xlabel('x/c')
        plt.ylabel('y/c')
        plt.title('Airfoil Shape')
        plt.legend(loc = 'upper right')
        
        if ax is None:
            plt.show()
            
    def plot_geometry(self, ax=None, extra_airfoils=None, min_alpha=0.1, max_alpha=0.5):
                
        normalized_lower_pass = 0.4
        normalized_upper_pass = 0.6
        
        properties = {
            'max_thickness': (self.max_thickness_lower_limit, self.max_thickness_upper_limit),
            'max_thickness_location': (self.max_thickness_location_lower_limit, self.max_thickness_location_upper_limit),
            'leading_edge_radius': (self.leading_edge_radius_lower_limit, self.leading_edge_radius_upper_limit),
            'trailing_edge_angle': (self.trailing_edge_angle_lower_limit, self.trailing_edge_angle_upper_limit),
            'max_curvature': (0, self.max_curvature_upper_limit),
        }
    
        def normalize(value, min_val, max_val):
            normed_value = normalized_lower_pass + (normalized_upper_pass - normalized_lower_pass) * (value - min_val) / (max_val - min_val)
            return normed_value
    
        normalized_values = []
        for prop, (min_val, max_val) in properties.items():
            current_val = self.geometric_properties[prop]
            norm_val = normalize(current_val, min_val, max_val)
            normalized_values.append(norm_val)
    
        num_vars = len(properties)
        angles = [n / float(num_vars) * 2 * np.pi for n in range(num_vars)]
        angles += angles[:1]
        normalized_values += normalized_values[:1]
    
        if ax is not None:
            plt.sca(ax)
        else:
            fig, ax = plt.subplots(figsize=(10, 10), subplot_kw=dict(projection='polar'))
    
        # Plot database entries if provided
        if extra_airfoils is not None:
            n_entries = len(extra_airfoils)
            if n_entries > 0:
                alphas = np.linspace(min_alpha, max_alpha, n_entries)
                for idx, row in extra_airfoils.iterrows():
                    db_normalized_values = []
                    for prop, (min_val, max_val) in properties.items():
                        norm_val = normalize(row[prop], min_val, max_val)
                        db_normalized_values.append(norm_val)
                    db_normalized_values.append(db_normalized_values[0])  # Complete the circle
                    
                    line_color = 'darkgreen' if row['constraints_met'] else 'darkred'
                    ax.plot(angles, db_normalized_values, '-', linewidth=1, color=line_color, alpha=alphas[idx])
    
        ax.fill_between(angles, [normalized_lower_pass]*(num_vars+1), [normalized_upper_pass]*(num_vars+1), 
                        color='lightgreen', alpha=0.2, label='Acceptable Range')
    
        line_color = 'darkgreen' if self.results['constraints_met'] else 'darkred'
        ax.plot(angles, normalized_values, 'o-', linewidth=2, color=line_color)
    
        ax.set_xticks(angles[:-1])
        labels = [prop.replace('_', ' ').title() for prop in properties.keys()]
        ax.set_xticklabels(labels, fontsize=12)
    
        ax.set_ylim(0, 1)
        ax.set_yticklabels([])
        ax.grid(True)
        # plt.title("Airfoil Geometric Properties", pad=20, fontsize=14)
        # plt.legend(fontsize=12, loc='upper right', bbox_to_anchor=(0.85, 0.8))
        if ax is None:
            plt.show()


def plot_results(airfoil, optimization_data = None, path = None):
    # Get primary monitor size
    monitor = get_monitors()[0]
    width = monitor.width / 100  # Convert pixels to inches (approximate)
    height = monitor.height / 100
    
    # size = min(width, height)
    
    figure = plt.figure(figsize=(width * 0.9, height), dpi=300)
    
    # Margins
    left_margin = 0.05
    right_margin = 0.01
    top_margin = 0.07
    bottom_margin = 0.03
    
    # Create a base subplot to hold the margin rectangles
    ax = figure.add_axes([0, 0, 1, 1])
    ax.axis('off')
    
    # Add title in the top margin
    title_ax = figure.add_axes([0, 1-top_margin, 1, top_margin])
    title_ax.axis('off')
    title_ax.text(0.5, 0.7, 'Airfoil optimization', 
                 horizontalalignment='center',
                 verticalalignment='center',
                 fontsize=16,
                 fontweight='bold')
    
    # Available space after margins
    available_width = 1 - left_margin - right_margin
    available_height = 1 - top_margin - bottom_margin
    
    # Vertical spacing
    ver_space = 0.1
    
    # Horizontal spacing
    hor_space = 0.05
    
    # Define widths
    geometry_width = (available_width - hor_space) * 0.5    
    ld_width = geometry_width
    airfoil_width = 0.5 * (available_width - hor_space)
    all_param_width = available_width - hor_space - airfoil_width
    
    # Define heights relative to available height
    geometry_height = geometry_width
    ld_height = ld_width
    airfoil_height = available_height - ver_space - geometry_height
    param_height = airfoil_height
    
    # Calculate positions
    airfoil_x = left_margin
    airfoil_y = 1 - top_margin - airfoil_height
    
    geometry_x = airfoil_x
    geometry_y = bottom_margin
    
    param_x = 1 - right_margin - all_param_width
    param_y = airfoil_y
        
    ld_x = 1 - right_margin - ld_width
    ld_y = geometry_y
    
    # Add the airfoil plot
    ax = figure.add_axes([airfoil_x, airfoil_y, airfoil_width, airfoil_height])
    extra_airfoils = None
    if optimization_data is not None:
        extra_airfoils = copy(optimization_data['all_airfoils'])
        extra_airfoils = extra_airfoils[len(extra_airfoils) - 10 : len(extra_airfoils) - 2]   
    airfoil.plot_airfoil(ax=ax, extra_airfoils = extra_airfoils)
    
    # Add the geometry
    ax = figure.add_axes([geometry_x, geometry_y, geometry_width, geometry_height], projection='polar')
    if optimization_data is None:
        data = {
            'max_thickness': [0.12, 0.15, 0.10, 0.18, 0.09],
            'max_thickness_location': [0.25, 0.30, 0.35, 0.22, 0.38],
            'leading_edge_radius': [0.02, 0.015, 0.025, 0.01, 0.03],
            'trailing_edge_angle': [10, 8, 12, 14, 7],
            'max_curvature': [25, 35, 45, 30, 40],
            'constraints_met': [True, True, False, False, True]
        }
        df = pd.DataFrame(data)
    else:
        df = copy(optimization_data['all_constraints'])
        df = df[(df['iter'] < df['iter'].max()) & (df['iter'] > df['iter'].max() - 10)]
    airfoil.plot_geometry(ax=ax, extra_airfoils = df)
    
    # Add the parameters evolution
    if optimization_data is None:
        n_params = 6
        param_width = all_param_width / n_params
        for i in range(n_params):
            values = np.random.rand(1000)
            hist, edges = np.histogram(values, bins = 50, range = (0,1))
            ax = figure.add_axes([param_x + i * param_width, param_y, param_width, param_height])
            plt.sca(ax)
            plt.imshow(np.atleast_2d(hist).T, extent = [0,1,0,1],
                       aspect = "auto", origin = 'lower',
                       cmap = 'binary')   
            ax.set_xticks([])
            ax.set_yticks([])
            ax.set_xlabel(f'param_{i}')
    else:
        params = optimization_data['parameters']
        # params = params[params['iter'] >= params['iter'].max() - 5]
        params = params.drop(['iter', 'metric'], axis = 1)
        param_names = list(params.columns)
        n_params = len(param_names)
        param_width = all_param_width / n_params
        for i, p in enumerate(param_names):
            values = params[p]
            hist, edges = np.histogram(values, bins = 100, range = (0,1))
            ax = figure.add_axes([param_x + i * param_width, param_y, param_width, param_height])
            plt.sca(ax)
            plt.imshow(np.atleast_2d(hist).T, extent = [0,1,0,1],
                        aspect = "auto", origin = 'lower',
                        cmap = 'YlGn')   
            ax.set_xlabel(p)
            ax.set_xticks([])
            ax.set_yticks([])
    
    # Add the ld
    ax = figure.add_axes([ld_x, ld_y, ld_width, ld_height])
    if optimization_data is not None:
        ld = optimization_data['ld']
        ld = ld[ld['constraints_met']]
        metrics = optimization_data['metrics']
        if len(ld) > 0:
            ax.plot(ld['iter'], ld['ld_ratio'], '-o', color = 'darkgreen', label = 'lift over drag ratio')
            ax.plot(ld['iter'], ld['lift'], '-o', color = 'darkblue', label = 'lift')
            ax.plot(ld['iter'], ld['drag'], '-o', color = 'darkorange', label = 'drag')
            ax.set_xlabel('iteration')
            ax.set_yscale('log')
            plt.grid(which='major', linestyle='--', alpha=0.5)
            plt.grid(which='minor', axis = 'y', linestyle='--', alpha=0.3)
            plt.title('Lift and drag', fontsize = 16)
            ax.legend(loc='upper right', bbox_to_anchor=(0.98, 0.9))
        else:
            ax.plot(metrics['iter'], metrics['metric'], '-o', color = 'darkblue')
            ax.set_xlabel('iteration')
            # ax.set_yscale('log')
            plt.grid(which='major', linestyle='--', alpha=0.5)
            plt.title('Constraints metric', fontsize = 16)
    
    update_fontsize(figure, 14)
    
    if path is not None:
        plt.savefig(path, bbox_inches='tight', dpi=300)
        
    plt.show()

# Kill all xfoil processes
def kill_xfoil_processes():
    """Kill all running XFOIL processes"""
    import psutil
    import signal
    
    killed = 0
    for proc in psutil.process_iter(['name', 'pid']):
        try:
            if 'xfoil' in proc.info['name'].lower():
                psutil.Process(proc.info['pid']).send_signal(signal.SIGTERM)
                killed += 1
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    
    return killed

# Update all text elements in a figure
def update_fontsize(fig, fontsize):
    # Update title and axis labels for all axes
    for ax in fig.get_axes():
        # Title
        if ax.get_title():
            ax.set_title(ax.get_title(), fontsize=fontsize*1.2)
        
        # Axis labels
        ax.set_xlabel(ax.get_xlabel(), fontsize=fontsize)
        ax.set_ylabel(ax.get_ylabel(), fontsize=fontsize)
        
        # Tick labels
        ax.tick_params(axis='both', labelsize=fontsize)
        
        # Legend - modify existing legend instead of creating new one
        if ax.get_legend():
            for text in ax.get_legend().get_texts():
                text.set_fontsize(fontsize)
            
        # Colorbar if it exists
        if hasattr(ax, 'collections'):
            for collection in ax.collections:
                if collection.colorbar:
                    collection.colorbar.ax.tick_params(labelsize=fontsize)
        
        # Text annotations
        for artist in ax.get_children():
            if isinstance(artist, plt.Text):
                artist.set_fontsize(fontsize*1.2)
    

class XFoilBatch:
    def __init__(self, analyzer):
        """
        Initialize batch simulation handler
        
        Args:
            analyzer: Instance of XFoilAnalyzer
        """
        self.analyzer = analyzer
        
    def run_batch(self, param_list, alpha, Re, Mach=0.0, 
                  get_pressure=False, get_boundary_layer=False,
                  show_progress=True):
        """
        Run batch simulations for multiple parameter sets
        """
        import pandas as pd
        from tqdm import tqdm
        
        results_list = []
        iterator = tqdm(param_list, desc="Running simulations") if show_progress else param_list
        
        for params in iterator:
            result = self.analyzer.analyze_airfoil(
                parameters=params,
                alpha=alpha,
                Re=Re,
                Mach=Mach,
                get_pressure=get_pressure,
                get_boundary_layer=get_boundary_layer,
                plot_airfoil=False
            )
            
            # Create base result dictionary with input parameters and geometric properties
            result_dict = {
                'Re': Re,
                'Mach': Mach,
                **params,  # Input parameters
                'max_thickness': result['geometry']['max_thickness'],
                'max_thickness_location': result['geometry']['max_thickness_location'],
                'leading_edge_radius': result['geometry']['leading_edge_radius'],
                'trailing_edge_angle': result['geometry']['trailing_edge_angle'],
                'max_curvature': result['geometry']['max_curvature']
            }
            
            if result['convergence']:
                if isinstance(alpha, (list, tuple, np.ndarray)):
                    for a, cl, cd, cm in zip(result['alpha'], result['cl'], 
                                           result['cd'], result['cm']):
                        alpha_dict = result_dict.copy()
                        alpha_dict.update({
                            'alpha': a,
                            'cl': cl,
                            'cd': cd,
                            'cm': cm,
                            'ld': cl/cd,
                            'cl_max': result['cl_max'],
                            'cd_min': result['cd_min'],
                            'ld_max': result['ld_max'],
                            'alpha_opt': result['alpha_opt']
                        })
                        results_list.append(alpha_dict)
                else:
                    result_dict.update({
                        'alpha': alpha,
                        'cl': result['cl'],
                        'cd': result['cd'],
                        'cm': result['cm'],
                        'ld': result['ld_ratio']
                    })
                    results_list.append(result_dict)
            else:
                if isinstance(alpha, (list, tuple, np.ndarray)):
                    if isinstance(alpha, tuple):
                        alpha_vals = np.arange(alpha[0], alpha[1] + alpha[2], alpha[2])
                    else:
                        alpha_vals = alpha
                        
                    for a in alpha_vals:
                        result_dict_nan = result_dict.copy()
                        result_dict_nan.update({
                            'alpha': a,
                            'cl': np.nan,
                            'cd': np.nan,
                            'cm': np.nan,
                            'ld': np.nan,
                            'cl_max': np.nan,
                            'cd_min': np.nan,
                            'ld_max': np.nan,
                            'alpha_opt': np.nan
                        })
                        results_list.append(result_dict_nan)
                else:
                    result_dict.update({
                        'alpha': alpha,
                        'cl': np.nan,
                        'cd': np.nan,
                        'cm': np.nan,
                        'ld': np.nan
                    })
                    results_list.append(result_dict)
        
        # Convert results to DataFrame
        df = pd.DataFrame(results_list)
        
        # Organize columns
        param_cols = list(param_list[0].keys())
        geom_cols = ['max_thickness', 'max_thickness_location', 'leading_edge_radius', 
                    'trailing_edge_angle', 'max_curvature']
        input_cols = ['Re', 'Mach', *param_cols]
        result_cols = ['alpha', 'cl', 'cd', 'cm', 'ld']
        
        if isinstance(alpha, (list, tuple, np.ndarray)):
            result_cols.extend(['cl_max', 'cd_min', 'ld_max', 'alpha_opt'])
            
        # Reorder columns
        all_cols = input_cols + geom_cols + result_cols
        df = df[all_cols]
        
        return df

def _example():
    """Run example case"""
    params = {
        'ta_u': 0.1584,
        'ta_l': 0.1565,
        'tb_u': 2.1241,
        'tb_l': 1.8255,
        'alpha_b': 11.6983,
        'alpha_c': 3.8270
    }
    
    alpha = (-5, 15, 0.5)
    # alpha = 5
    Re = 1e6
    Mach = 0.2
    
    analyzer = XFoilAnalyzer()
    
    results = analyzer.analyze_airfoil(
        parameters=params,
        alpha=alpha,
        Re=Re,
        Mach=Mach,
        get_pressure=True,
        get_boundary_layer=True,
        plot_airfoil=True
    )
    
    if results['convergence']:
        plot_polar(results)
        if results.get('boundary_layer'):
            plot_boundary_layer(results['boundary_layer'])
        if results.get('pressure'):
            plot_pressure_distribution(results['pressure'])
        
        print("\nPerformance Metrics:")
        print(f"Maximum Lift Coefficient: {results['cl_max']:.3f}")
        print(f"Minimum Drag Coefficient: {results['cd_min']:.4f}")
        print(f"Maximum L/D Ratio: {results['ld_max']:.2f}")
        print(f"Optimal Angle of Attack: {results['alpha_opt']:.1f}°")
    else:
        print("Simulation failed to converge")

if __name__ == "__main__":
    _example()