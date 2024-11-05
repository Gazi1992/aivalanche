"""
NURBS-based airfoil generator implementation based on:
'Airfoil geometry parameterization for optimization studies using NURBS'
http://eprints.soton.ac.uk/50031/1/Sobe07.pdf
# """

from __future__ import division
import numpy as np
from math import pi, cos, sin

class Nurbs:
    def __init__(self, k):
        """
        Initialize NURBS airfoil generator with shape parameters
        
        Args:
            k: Dictionary containing shape parameters:
               ta_u: Upper surface leading edge tangent magnitude
               ta_l: Lower surface leading edge tangent magnitude
               tb_u: Upper surface trailing edge tangent magnitude
               tb_l: Lower surface trailing edge tangent magnitude
               alpha_b: Trailing edge angle (degrees)
               alpha_c: Camber angle (degrees)
        """
        self.ta_u = k['ta_u']
        self.ta_l = k['ta_l']
        self.tb_u = k['tb_u']
        self.tb_l = k['tb_l']
        self.alpha_b = k['alpha_b']
        self.alpha_c = k['alpha_c']
        
        # Calculate coordinates immediately
        self._coordinates = self._spline()
    
    @property
    def x_lower(self):
        """Get x-coordinates of lower surface"""
        return np.array([x[0] for x in self._coordinates[0]])
    
    @property
    def y_lower(self):
        """Get y-coordinates of lower surface"""
        return np.array([y[0] for y in self._coordinates[1]])
    
    @property
    def x_upper(self):
        """Get x-coordinates of upper surface"""
        return np.array([x[0] for x in self._coordinates[2]])
    
    @property
    def y_upper(self):
        """Get y-coordinates of upper surface"""
        return np.array([y[0] for y in self._coordinates[3]])
    
    @property
    def thickness_distribution(self):
        """
        Calculate thickness distribution along the chord
        
        Returns:
            tuple: (x positions, thickness values)
        """
        # Create common x-coordinates for interpolation
        x_common = np.linspace(0, 1, 100)
        
        # Ensure coordinates are 1D arrays
        x_u = self.x_upper
        y_u = self.y_upper
        x_l = self.x_lower
        y_l = self.y_lower
        
        # Interpolate upper and lower surfaces
        y_upper_interp = np.interp(x_common, x_u, y_u)
        y_lower_interp = np.interp(x_common, x_l, y_l)
        
        # Calculate thickness normal to chord line
        thickness = y_upper_interp - y_lower_interp
        
        return x_common, thickness
    
    @property
    def max_thickness(self):
        """
        Get maximum thickness as fraction of chord
        
        Returns:
            float: Maximum thickness ratio (t/c)
        """
        _, thickness = self.thickness_distribution
        return float(np.max(thickness))
    
    @property
    def max_thickness_location(self):
        """
        Get chordwise location of maximum thickness
        
        Returns:
            float: x/c location of maximum thickness
        """
        x, thickness = self.thickness_distribution
        return float(x[np.argmax(thickness)])
    
    @property
    def leading_edge_radius(self):
        """
        Calculate leading edge radius using circle fitting
        
        Returns:
            float: Leading edge radius as fraction of chord
        """
        # Take points near leading edge (first 5% of chord)
        le_region = 0.05
        
        x_u = self.x_upper
        y_u = self.y_upper
        x_l = self.x_lower
        y_l = self.y_lower
        
        upper_mask = x_u <= le_region
        lower_mask = x_l <= le_region
        
        # Combine points for circle fitting
        x_points = np.concatenate([x_u[upper_mask], x_l[lower_mask]])
        y_points = np.concatenate([y_u[upper_mask], y_l[lower_mask]])
        
        if len(x_points) < 3:  # Need at least 3 points for circle fit
            return 0.0
        
        # Convert to matrix form for least squares circle fit
        A = np.column_stack([2*x_points, 2*y_points, np.ones_like(x_points)])
        b = x_points**2 + y_points**2
        
        try:
            # Solve for circle parameters
            solution = np.linalg.lstsq(A, b, rcond=None)[0]
            
            # Extract circle center and radius
            x_center = solution[0]
            y_center = solution[1]
            radius = np.sqrt(solution[2] + x_center**2 + y_center**2)
            
            return float(radius)
        except np.linalg.LinAlgError:
            return 0.0
    
    @property
    def surface_smoothness(self):
        """
        Calculate surface curvature distribution for upper and lower surfaces
        
        Returns:
            tuple: (upper surface curvature, lower surface curvature)
        """
        def calculate_curvature(x, y):
            # Calculate first derivatives
            dx_dt = np.gradient(x)
            dy_dt = np.gradient(y)
            
            # Calculate second derivatives
            d2x_dt2 = np.gradient(dx_dt)
            d2y_dt2 = np.gradient(dy_dt)
            
            # Calculate curvature
            curvature = np.abs(dx_dt * d2y_dt2 - dy_dt * d2x_dt2) / (dx_dt**2 + dy_dt**2)**(3/2)
            return curvature
        
        upper_curvature = calculate_curvature(self.x_upper, self.y_upper)
        lower_curvature = calculate_curvature(self.x_lower, self.y_lower)
        
        return upper_curvature, lower_curvature
    
    @property
    def max_curvature(self):
        """
        Get maximum curvature value from both surfaces
        
        Returns:
            float: Maximum absolute curvature
        """
        upper_curvature, lower_curvature = self.surface_smoothness
        return float(max(np.max(upper_curvature), np.max(lower_curvature)))
    
    def _spline(self):
        """
        Calculate NURBS spline for airfoil surface
        
        Returns:
            numpy array with [x_lower, y_lower, x_upper, y_upper] coordinates
        """
        # Parameter space discretization
        u = np.linspace(0, 1, 100)
        
        # Initialize coordinate arrays
        x_u, y_u, x_l, y_l = [], [], [], []
        
        # Hermite basis matrix
        basis_matrix = np.array([
            [1, 0, 0, 0],
            [0, 0, 1, 0],
            [-3, 3, -2, -1],
            [2, -2, 1, 1]
        ])
        
        # End points
        A = [0, 0]  # Leading edge
        B = [1, 0]  # Trailing edge
        
        # Calculate tangent vectors
        TA_u = [
            self.ta_u * cos(-pi/2),
            self.ta_u * abs(sin(-pi/2))
        ]  # Upper leading edge
        
        TB_u = [
            self.tb_u * cos(-((self.alpha_c + self.alpha_b)*pi/180)),
            self.tb_u * sin(-((self.alpha_b + self.alpha_c)*pi/180))
        ]  # Upper trailing edge
        
        TA_l = [
            self.ta_l * cos(-pi/2),
            self.ta_l * sin(-pi/2)
        ]  # Lower leading edge
        
        TB_l = [
            self.tb_l * cos(-(self.alpha_c*pi/180)),
            self.tb_l * sin(-(self.alpha_c*pi/180))
        ]  # Lower trailing edge
    
        # Generate upper surface
        for j in range(2):  # Loop for x and y coordinates
            control_points = np.array([[A[j]], [B[j]], [TA_u[j]], [TB_u[j]]])
            coefficients = np.dot(basis_matrix, control_points)
            
            for t in u:
                parameter = [1, t, t**2, t**3]
                if j == 0:  # j=0 is for x coordinates
                    x_u.append(np.dot(parameter, coefficients))
                else:       # j=1 is for y coordinates
                    y_u.append(np.dot(parameter, coefficients))
    
        # Generate lower surface
        for j in range(2):  # Loop for x and y coordinates
            control_points = np.array([[A[j]], [B[j]], [TA_l[j]], [TB_l[j]]])
            coefficients = np.dot(basis_matrix, control_points)
            
            for t in u:
                parameter = [1, t, t**2, t**3]
                if j == 0:  # j=0 is for x coordinates
                    x_l.append(np.dot(parameter, coefficients))
                else:       # j=1 is for y coordinates
                    y_l.append(np.dot(parameter, coefficients))
    
        return np.array([x_l, y_l, x_u, y_u])
    
    def get_geometric_properties(self):
        """
        Get all geometric properties in a dictionary
        
        Returns:
            dict: Dictionary containing all geometric properties
        """
        return {
            'max_thickness': self.max_thickness,
            'max_thickness_location': self.max_thickness_location,
            'leading_edge_radius': self.leading_edge_radius,
            'trailing_edge_angle': self.alpha_b,
            'max_curvature': self.max_curvature
        }