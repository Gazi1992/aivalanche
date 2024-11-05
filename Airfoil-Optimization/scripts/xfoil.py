"""
Enhanced XFOIL interface with direct subprocess control and NURBS airfoil generation.
"""

from __future__ import division
import subprocess as subp
import numpy as np
import os
import warnings
from nurbs import Nurbs
from visualizations import plot_airfoil, plot_polar, plot_pressure_distribution, plot_boundary_layer

class XFoilSettings:
    """Settings container for XFOIL analysis"""
    def __init__(self, timeout = 5, n_iter = 1000, n_crit = 9, init_bl_loc = 0.05, working_dir = ".", parameters = None):
        self.timeout = timeout       # seconds
        self.n_iter = n_iter      # maximum iterations
        self.n_crit = n_crit        # critical amplification ratio
        self.init_bl_loc = init_bl_loc
        self.working_dir = working_dir  # working directory for temp files
        self.parameters = parameters or {
            'ta_u': 0.1584,   # Upper surface leading edge tangent
            'ta_l': 0.1565,   # Lower surface leading edge tangent
            'tb_u': 2.1241,   # Upper surface trailing edge tangent
            'tb_l': 1.8255,   # Lower surface trailing edge tangent
            'alpha_b': 11.6983,  # Trailing edge angle
            'alpha_c': 3.8270    # Camber angle
        }

class XFoilAnalyzer:
    def __init__(self, settings = None):
        """
        Initialize XFOIL analyzer
        
        Args:
            settings: XFoilSettings object or None for defaults
        """
        self.settings = settings or XFoilSettings()
        self.airfoil = None
        self.airfoil_path = None
        self.nurbs_airfoil = None  # Store NURBS object for geometric analysis
    
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
        input_file = os.path.join(self.settings.working_dir, "xfoil_input.in")
        
        # Create working directory if it doesn't exist
        os.makedirs(self.settings.working_dir, exist_ok=True)
        
        # Change to working directory
        original_dir = os.getcwd()
        os.chdir(self.settings.working_dir)
        
        try:
            # Write commands using relative paths
            with open("xfoil_input.in", 'w') as f:
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
                    process = subp.Popen("xfoil.exe < xfoil_input.in", 
                                       shell=True, stdout=subp.PIPE, 
                                       stderr=subp.PIPE)
                else:  # Linux/Mac
                    process = subp.Popen("xfoil < xfoil_input.in", 
                                       shell=True, stdout=subp.PIPE, 
                                       stderr=subp.PIPE)
                
                output, error = process.communicate(timeout=self.settings.timeout)
                return True
                
            except subp.TimeoutExpired:
                process.kill()
                print("XFOIL process timed out")
                return False
                
        finally:
            # Clean up input file
            if os.path.exists("xfoil_input.in"):
                os.remove("xfoil_input.in")
            
            # Change back to original directory
            os.chdir(original_dir)

    def _run_single_alpha(self, alpha, Re, Mach=0.0):
       """Run analysis for single angle of attack"""
       output_basename = "polar.txt"
       output_file = os.path.join(self.settings.working_dir, output_basename)
       
       if os.path.exists(output_file):
           os.remove(output_file)
           
       commands = [
           # "PLOP",              # Enter plot options menu
           # "G",                 # Turn off all graphics
           # "",                  # Exit plot options menu
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
                data = np.loadtxt(output_file, skiprows=12)
                if len(data) == 0:
                    return {'convergence': False}
                
            except Exception as e:
                print(f"Error in single alpha analysis: {str(e)}")
                return {'convergence': False}
                
            finally:
                if os.path.exists(output_file):
                    os.remove(output_file)
       else:
           return {'convergence': False}
       
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
       
       return results
    
    def _run_alpha_range(self, alpha_range, Re, Mach=0.0):
        """Run analysis for range of angles of attack"""
        output_basename = "polar.txt"
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
                    return {'convergence': False}
                    
                valid_mask = ~np.isnan(data).any(axis=1) & (data[:, 2] > 0)
                if not np.any(valid_mask):
                    return {'convergence': False}
                    
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
                
                return results
                
            except Exception as e:
                print(f"Error in alpha range analysis: {str(e)}")
                return {'convergence': False}
                
            finally:
                if os.path.exists(output_file):
                    os.remove(output_file)
                    
        return {'convergence': False}
    
    def _run_alpha_list(self, alpha_list, Re, Mach=0.0):
        """Run analysis for a list of specific angles of attack"""
        output_basename = "polar.txt"
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
            return {'convergence': False}
            
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
        
        return results
    
    def _run_pressure_distribution(self, alpha, Re, Mach=0.0):
        """Get pressure coefficient distribution"""
        output_basename = "polar.txt"
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
        output_basename = "polar.txt"
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
        geometric_properties = self.nurbs_airfoil.get_geometric_properties()
        
        if not self.airfoil_path:
            return {'convergence': False}
            
        if isinstance(alpha, (list, np.ndarray)):
            results = self._run_alpha_list(alpha, Re, Mach)
        elif isinstance(alpha, tuple):
            results = self._run_alpha_range(alpha, Re, Mach)
        else:
            results = self._run_single_alpha(alpha, Re, Mach)
        
        # Add geometric properties and input parameters to results
        results.update({
            'geometry': geometric_properties,
            'parameters': parameters
        })    
        
        if not results['convergence']:
            return results
            
        if isinstance(alpha, (list, tuple, np.ndarray)):
            analysis_alpha = results['alpha'][0]
        else:
            analysis_alpha = alpha
        
        if get_pressure:
            pressure_results = self._run_pressure_distribution(analysis_alpha, Re, Mach)
            results['pressure'] = pressure_results
            
        if get_boundary_layer:
            bl_results = self._run_boundary_layer(analysis_alpha, Re, Mach)
            results['boundary_layer'] = bl_results
        
        return results

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