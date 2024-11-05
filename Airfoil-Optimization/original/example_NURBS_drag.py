"""
An example to show how to combine NURBS airfoil_generator and XFOIL.
This script performs a parameter study by:
1. Generating different airfoils using NURBS with varying parameters
2. Analyzing each airfoil using XFOIL to get drag coefficients
3. Visualizing the results in a color-coded plot
"""

# Import required libraries
from airfoil_generators.nurbs import NURBS     # For generating airfoil shapes
from xfoil.xfoil import oper_visc_cl, oper_visc_alpha# For XFOIL analysis at specified lift coefficient
import matplotlib.pyplot as plt                # For plotting results
import numpy as np                            # For numerical operations
import os                                     # For file operations
import tempfile                               # For temporary file handling

# Set flow conditions for XFOIL analysis
Re = 100000                                   # Reynolds number
Cl = 0.2                                      # Target lift coefficient
drags = np.zeros((5,3))                       # Initialize array to store drag coefficients

def plot_airfoil(airfoil, title=None):
    """
    Function to plot airfoil shape
    
    Args:
        airfoil: List containing [x_lower, y_lower, x_upper, y_upper] coordinates
        title: Optional title for the plot
    """
    plt.figure(figsize=(10, 5))
    
    # Plot lower and upper surfaces
    plt.plot(airfoil[1], airfoil[0], 'b-', label='Lower surface')  # Lower surface
    plt.plot(airfoil[3], airfoil[2], 'r-', label='Upper surface')  # Upper surface
    
    # Add plot details
    plt.axis('equal')  # Equal aspect ratio
    plt.grid(True)
    plt.xlabel('x/c')
    plt.ylabel('y/c')
    if title:
        plt.title(title)
    plt.legend()
    plt.show()

def get_coords_plain(argv):
    """
    Convert airfoil coordinates to XFOIL format.
    
    Args:
        argv: List containing [x_lower, y_lower, x_upper, y_upper] coordinates
    
    Returns:
        String with formatted coordinates suitable for XFOIL input
    """
    x_l = argv[0]    # x-coordinates of lower surface
    y_l = argv[1]    # y-coordinates of lower surface
    x_u = argv[2]    # x-coordinates of upper surface
    y_u = argv[3]    # y-coordinates of upper surface
    
    # Combine upper and lower surface coordinates
    # [::-1] reverses the arrays to maintain proper airfoil coordinate ordering
    ycoords = np.append(y_l[::-1], y_u[1:])
    xcoords = np.append(x_l[::-1], x_u[1:])
    
    # Create coordinate pairs and format them
    coordslist = np.array((xcoords, ycoords)).T
    coordstrlist = ["{:.6f} {:.6f}".format(coord[1], coord[0])
                   for coord in coordslist]
    return '\n'.join(coordstrlist)

# Define NURBS airfoil parameters
# These parameters control the shape of the airfoil
ta_u = 0.1584                        # Upper surface thickness parameter
ta_l = 0.1565                        # Lower surface thickness parameter
tb_u = np.linspace(1,10,6)           # Array of upper surface thickness distribution parameters
tb_l = 1.8255                        # Lower surface thickness distribution
alpha_c = 3.8270                     # Curvature parameter
alpha_b = np.linspace(10,20,4)       # Array of trailing edge angles

# Create temporary directory for airfoil files
temp_dir = tempfile.mkdtemp()

try:
    # Nested loops for parameter study
    for i in range(1,6):             # Loop over tb_u values
        for j in range(1,4):         # Loop over alpha_b values
            # Create dictionary of NURBS parameters for current airfoil
            k = {}
            k['ta_u'] = ta_u
            k['ta_l'] = ta_l
            k['tb_u'] = tb_u[i]      # Vary upper surface thickness distribution
            k['tb_l'] = tb_l
            k['alpha_b'] = alpha_b[j] # Vary trailing edge angle
            k['alpha_c'] = alpha_c
            
            # k = {'ta_u': 0.1584,
            # 'ta_l': 0.1565,
            # 'tb_u': 2.1241,
            # 'tb_l': 1.8255,
            # 'alpha_b': 11.6983,
            # 'alpha_c': 3.8270}
            
            # Generate airfoil using NURBS
            af = NURBS(k)
            airfoil = af._spline()
            plot_airfoil(airfoil)
            
            
            # Create unique filename for this airfoil
            temp_af_filename = os.path.join(temp_dir, f"temp_airfoil_{i}{j}.dat")
            
            # Save airfoil coordinates to file
            with open(temp_af_filename, 'w') as af:
                af.write(get_coords_plain(airfoil))
            
            # Analyze airfoil with XFOIL
            try:
                print(f'{i}, {j}')    # Print progress
                # Run XFOIL analysis at specified Cl
                # polar = oper_visc_cl(temp_af_filename, Cl, Re, iterlim=1000, show_seconds=1)
                polar = oper_visc_alpha(temp_af_filename, -5, Re, iterlim=1000, show_seconds=1)
                # Store drag coefficient (index 2 in polar results)
                drags[i-1][j-1] = polar[0][0][2]
            except Exception as e:
                print(f"Warning: XFOIL didn't converge for airfoil_{i}{j}: {str(e)}")
                drags[i-1][j-1] = np.nan
     
            # Extract airfoil coordinates for plotting
            xl = airfoil[0]    # lower surface x-coordinates
            yl = airfoil[1]    # lower surface y-coordinates
            xu = airfoil[2]    # upper surface x-coordinates
            yu = airfoil[3]    # upper surface y-coordinates
            
            # Define function to plot translated airfoil shapes
            def translated_plt(x, y, *args):
                # Plot airfoil scaled and translated based on i,j indices
                plt.plot(x*0.8 + (j-.9), y*0.8 + (i-0.5), *args)
            
            # Plot current airfoil shape
            translated_plt(yl, xl, 'w')    # lower surface
            translated_plt(yu, xu, 'w')    # upper surface
            
            # Clean up temporary file
            os.remove(temp_af_filename)

finally:
    # Clean up temporary directory when done
    try:
        os.rmdir(temp_dir)
    except OSError:
        pass

# Print final drag coefficient matrix
print(drags)

# Create color plot of drag coefficients
plt.pcolor(drags, cmap=plt.cm.RdBu)
plt.pcolor(drags, cmap=plt.cm.coolwarm)
cbar = plt.colorbar()
cbar.ax.set_ylabel("Drag coefficient $C_d$")

# Set custom tick labels
plt.yticks((.5,1.5,2.5,3.5,4.5), ("1", "2", "3", "4", "5"))
plt.xticks((.5,1.5,2.5), ("1", "2", "3"))

# Adjust plot layout and display
plt.tight_layout()
plt.show()