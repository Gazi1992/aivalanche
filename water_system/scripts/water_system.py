import wntr, matplotlib.pyplot as plt, noise, warnings, numpy as np
from screeninfo import get_monitors

def get_elevation(coordinates,
                  x_min = -500, x_max = 3500,
                  y_min = -1000, y_max = 1500,
                  amplitude = 400,
                  octaves = 6, persistence = 0.5, lacunarity = 0.2, seed = 42):
        
    x_range = x_max - x_min
    y_range = y_max - y_min
    
    x = coordinates[:,0]
    y = coordinates[:,1]
    
    x = (x - x_min) / x_range
    y = (y - y_min) / y_range
    
    # Generate Perlin noise
    np.random.seed(seed)
    
    elevation = []
    for i, j in zip(x,y):
        elevation.append(noise.pnoise2(i * lacunarity, j * lacunarity, octaves=octaves, persistence=persistence))
    elevation = np.array(elevation) * amplitude + 30
    
    return elevation
    
def generate_terrain(x_size = 1000, y_size = 1000, x_min = 0, x_max = 1, y_min = 0, y_max = 1, plot = False,
                     amplitude = 900, octaves = 6, persistence = 0.5, lacunarity = 0.2, seed = 42):
    
    # Generate Perlin noise
    x = np.linspace(x_min, x_max, x_size)
    y = np.linspace(y_min, y_max, y_size)
    xx, yy = np.meshgrid(x,y)
    xx = xx.reshape(-1, 1)
    yy = yy.reshape(-1, 1)
    coordinates = np.hstack((xx,yy))

    terrain = get_elevation(coordinates, x_min = x_min, x_max = x_max, y_min = y_min, y_max = y_max, amplitude = amplitude,
                            octaves = octaves, persistence = persistence, lacunarity = lacunarity, seed = seed)
    terrain = terrain.reshape(x_size, y_size)
    
    if plot:
        plt.figure(figsize=(12, 12))
        plt.imshow(terrain, cmap='terrain')
        plt.colorbar(label='Elevation (m)')
        plt.title('Realistic Terrain')
        plt.show()
    
    return terrain, xx, yy

class water_distribution_network:
    def __init__(self, x_min = -100, x_max = 3100, y_min = -1600, y_max = 1100, lacunarity = 0.92):
        self.x_min = x_min
        self.x_max = x_max
        self.y_min = y_min
        self.y_max = y_max
        self.lacunarity = lacunarity
        
        # Energy parameters
        self.pump_efficiency = 0.75  # pump efficiency
        self.specific_gravity = 9.81  # kN/m³
        self.electricity_cost = 0.15 * 1e-6  # milion $/kWh
        
        # Pipe cost parameters (simplified cost model)
        self.pipe_cost_params = {
            # Cost = a * diameter^b + c
            'a': 1.2,  # cost coefficient
            'b': 1.1,  # diameter exponent
            'c': 100    # base cost per meter
        }
        
        # Constraints
        self.min_pressure = 5  # meters
        self.max_pressure = 120  # meters
        self.max_velocity = 3.5  # m/s
        
        # Network layout parameters
        self.simulation_duration = 24 * 3600  # 24 hours in seconds
        self.time_step = 3600  # 1 hour in seconds
        
        self.initilize_variables()

    def calculate_pipe_cost(self, diameter, length):
        """Calculate pipe cost based on diameter (mm) and length (m)"""
        p = self.pipe_cost_params
        cost = (p['a'] * (diameter ** p['b']) + p['c']) * length * 1e-6
        return cost

    def initilize_variables(self):
        self.wn = None
        self.total_pipe_cost = None
        self.energy_metrics = None
        self.energy_cost = None
        self.total_cost = None
        self.constraint_results = None
        self.performance_metrics = None
        self.sim_results = None
        self.sim_warnings = []

    def update_network(self, params):
        self.initilize_variables()
        self.create_network(params)

    def create_network_(self, params):
        wn = wntr.network.WaterNetworkModel()
        
        # Add reservoir at coordinates (500, -750)
        reservoir_coords = (500, -750)
        reservoir_elev = get_elevation(np.array(reservoir_coords).reshape(1, -1),
                                        x_min = self.x_min, x_max = self.x_max, y_min = self.y_min, y_max = self.y_max,
                                        lacunarity = self.lacunarity)
        wn.add_reservoir('R1', base_head=reservoir_elev[0], coordinates=reservoir_coords)
        
        # Add junctions
        junctions_data = [
            # Main transmission junctions
            ('J1', 0, 0, (500, 0)),    
            ('J2', 0, 0, (1000, 0)),   
            ('J3', 0, 0, (1500, 0)),   
            ('J4', 0, 0, (2000, 0)),   
    
            # Northern branch (residential area 1)
            ('J5', 0, 0, (2000, 500)),
            ('D1', 0, 30, (2000, 1000)),  
    
            # Eastern branch (commercial area)
            ('J6', 0, 0, (2500, 0)),
            ('D2', 0, 50, (3000, 0)),   
    
            # Southern branch (industrial area)
            ('J7', 0, 0, (2000, -500)),
            ('J8', 0, 0, (2000, -1000)),
            ('D3', 0, 70, (2000, -1500)), 
    
            # Western branch (residential areas 2 & 3)
            ('J9', 0, 0, (1000, -500)),
            ('D4', 0, 25, (0, -1000)),    
            ('D5', 0, 35, (1000, -1000)),
            ('D6', 0, 15, (0, 0)),  # New demand node at (0, 0)
            
            # Add new junctions for pump connections - same coordinates for in/out
            ('J10', 0, 0, (1250, 0)),    # Between J2 and J3
            ('J11', 0, 0, (1250, 0)),   # Same coordinates as PUMP1_IN
            ('J12', 0, 0, (2000, -750)), # Between J7 and J8
            ('J13', 0, 0, (2000, -750)) # Same coordinates as PUMP2_IN
        ]
    
        # Get all node coordinates
        node_coords = np.array([coords[-1] for coords in junctions_data])
    
        # Get elevations for all nodes
        elevations = get_elevation(node_coords, x_min = self.x_min, x_max = self.x_max,
                                    y_min = self.y_min, y_max = self.y_max, lacunarity = self.lacunarity)
    
        for (name, _, demand, coords), elev in zip(junctions_data, elevations):
            wn.add_junction(name, elevation=elev, base_demand=demand, coordinates=coords)
    
        # Add pumps with their curves
        pump_curves = {
            'PUMP1': [
                (0, params['pump1_head_max']),
                (params['pump1_flow_max']*0.5, params['pump1_head_max']*0.64),
                (params['pump1_flow_max'], params['pump1_head_max']*0.25)
            ],
            'PUMP2': [
                (0, params['pump2_head_max']),
                (params['pump2_flow_max']*0.5, params['pump2_head_max']*0.64),
                (params['pump2_flow_max'], params['pump2_head_max']*0.25)
            ]
        }
        
        for pump_name, curve in pump_curves.items():
            wn.add_curve(f'{pump_name}_CURVE', 'HEAD', curve)
        
        # Add pumps between their respective inlet and outlet junctions
        wn.add_pump('PUMP1', 'J10', 'J11', pump_type='HEAD', pump_parameter='PUMP1_CURVE')
        wn.add_pump('PUMP2', 'J12', 'J13', pump_type='HEAD', pump_parameter='PUMP2_CURVE')
    
        # Add pipes
        pipes_data = [
            # Original pipes
            ('P1', 'J1', 'R1', 500),   
            ('P2', 'J1', 'J2', 500),   
            ('P3', 'J3', 'J4', 500),   
            ('P4', 'J4', 'J5', 500),
            ('P5', 'J5', 'D1', 500),
            ('P6', 'J4', 'J6', 500),
            ('P7', 'J6', 'D2', 500),
            ('P8', 'J4', 'J7', 500),
            ('P9', 'J8', 'D3', 500),
            ('P10', 'J2', 'J9', 500),
            ('P11', 'J9', 'D4', 800),
            ('P12', 'J1', 'D6', 500),
            ('P13', 'J8', 'D5', 1200),
            
            # New connecting pipes for Pump 1
            ('P14', 'J2', 'J10', 100),    # Short pipe before Pump 1
            ('P15', 'J11', 'J3', 100),   # Short pipe after Pump 1
            
            # New connecting pipes for Pump 2
            ('P16', 'J7', 'J12', 100),    # Short pipe before Pump 2
            ('P17', 'J13', 'J8', 100)    # Short pipe after Pump 2
        ]
        
        total_pipe_cost = 0
        for name, start, end, length in pipes_data:
            # Use smaller diameter for pump connecting pipes
            if name in ['P14', 'P15', 'P16', 'P17']:
                diameter = params.get(name, 400)  # default 400mm for pump connections
            else:
                diameter = params.get(name, 300)  # default 300mm for other pipes
                
            wn.add_pipe(name, start, end, length, diameter=diameter, roughness=100)
            total_pipe_cost += self.calculate_pipe_cost(diameter, length)
    
        # Add demand patterns
        patterns = {
            'residential': [0.3, 0.3, 0.3, 0.3, 0.4, 0.5, 0.6, 0.8, 1.0, 1.1, 1.2, 1.3,
                          1.2, 1.1, 1.0, 1.0, 1.1, 1.2, 1.4, 1.6, 1.4, 1.2, 0.8, 0.5],
            'commercial': [0.1, 0.1, 0.1, 0.1, 0.2, 0.3, 0.4, 1.0, 1.5, 1.5, 1.4, 1.3,
                          1.3, 1.4, 1.4, 1.5, 1.5, 1.3, 1.1, 0.8, 0.5, 0.3, 0.2, 0.1],
            'industrial': [0.8, 0.8, 0.8, 0.8, 0.8, 0.8, 1.0, 1.2, 1.2, 1.2, 1.2, 1.2,
                          1.2, 1.2, 1.2, 1.2, 1.2, 1.0, 1.0, 1.0, 1.0, 0.8, 0.8, 0.8]
        }
    
        for pattern_name, pattern_values in patterns.items():
            wn.add_pattern(pattern_name, pattern_values)
    
        # Assign patterns
        pattern_assignments = {
            'D1': 'residential',
            'D4': 'residential',
            'D5': 'residential',
            'D2': 'commercial',
            'D3': 'industrial',
            'D6': 'residential'
        }
        
        for node, pattern in pattern_assignments.items():
            wn.get_node(node).demand_pattern_name = pattern
    
        # Set simulation options
        wn.options.time.duration = self.simulation_duration
        wn.options.time.hydraulic_timestep = self.time_step
        wn.options.time.pattern_timestep = self.time_step
        wn.options.time.report_timestep = self.time_step
    
        self.wn = wn
        self.total_pipe_cost = total_pipe_cost
    
    def create_network_1(self, params):
        wn = wntr.network.WaterNetworkModel()
        
        # Add reservoir at elevation 100m
        wn.add_reservoir('R1', base_head=100, coordinates=(0, 0))
        
        # Add junctions with demand nodes at different elevations
        junctions_data = [
            ('J1', 80, 0,  (500, 0)),    # After reservoir
            ('J2', 75, 0,  (1000, 0)),   # Before first pump
            ('J3', 70, 0,  (1500, 0)),   # After first pump
            ('J4', 65, 0,  (2000, 0)),   # Junction for demands
            ('J5', 75, 0,  (2000, -300)),  # Before second pump
            ('J6', 70, 0,  (2000, -600)),  # After second pump
            ('D1', 60, 20, (2500, 200)),   # Residential
            ('D2', 58, 25, (2500, 0)),     # Commercial
            ('D3', 55, 30, (2500, -200)),  # Commercial
            ('D4', 53, 35, (2500, -400)),  # Industrial
            ('D5', 50, 40, (2500, -600)),  # Industrial
            ('D6', 48, 30, (2500, -800))   # Industrial
        ]
        
        for name, elev, demand, coords in junctions_data:
            wn.add_junction(name, elevation=elev, base_demand=demand, coordinates=coords)
        
        # Add pumps with curves
        pump_curves = {
            'PUMP1': [
                (0, params['pump1_head_max']),
                (params['pump1_flow_max']*0.5, params['pump1_head_max']*0.7),
                (params['pump1_flow_max'], params['pump1_head_max']*0.4)
            ],
            'PUMP2': [
                (0, params['pump2_head_max']),
                (params['pump2_flow_max']*0.5, params['pump2_head_max']*0.7),
                (params['pump2_flow_max'], params['pump2_head_max']*0.4)
            ]
        }
        
        for pump_name, curve in pump_curves.items():
            wn.add_curve(f'{pump_name}_CURVE', 'HEAD', curve)
        
        wn.add_pump('PUMP1', 'J2', 'J3', pump_type='HEAD', pump_parameter='PUMP1_CURVE')
        wn.add_pump('PUMP2', 'J5', 'J6', pump_type='HEAD', pump_parameter='PUMP2_CURVE')
        
        # Add pipes
        pipes_data = [
            ('P1', 'R1', 'J1', 500),    # From reservoir
            ('P2', 'J1', 'J2', 500),    # To first pump
            ('P3', 'J3', 'J4', 500),    # From first pump to junction
            ('P4', 'J4', 'D1', 500),    # To residential demand
            ('P5', 'J4', 'D2', 500),    # To commercial demand
            ('P6', 'J4', 'D3', 500),    # To commercial demand
            ('P7', 'J4', 'J5', 500),    # To second pump
            ('P8', 'J6', 'D4', 500),    # To industrial demands
            ('P9', 'J6', 'D5', 500),
            ('P10', 'J6', 'D6', 500)
        ]
        
        total_pipe_cost = 0
        for name, start, end, length in pipes_data:
            diameter = params.get(name, 400)
            wn.add_pipe(name, start, end, length, diameter=diameter, roughness=100)
            total_pipe_cost += self.calculate_pipe_cost(diameter, length)
        
        # Add patterns
        patterns = {
            'residential': [0.3, 0.3, 0.3, 0.3, 0.4, 0.5, 0.6, 0.8, 1.0, 1.1, 1.2, 1.3,
                          1.2, 1.1, 1.0, 1.0, 1.1, 1.2, 1.4, 1.6, 1.4, 1.2, 0.8, 0.5],
            'commercial': [0.1, 0.1, 0.1, 0.1, 0.2, 0.3, 0.4, 1.0, 1.5, 1.5, 1.4, 1.3,
                         1.3, 1.4, 1.4, 1.5, 1.5, 1.3, 1.1, 0.8, 0.5, 0.3, 0.2, 0.1],
            'industrial': [0.8, 0.8, 0.8, 0.8, 0.8, 0.8, 1.0, 1.2, 1.2, 1.2, 1.2, 1.2,
                         1.2, 1.2, 1.2, 1.2, 1.2, 1.0, 1.0, 1.0, 1.0, 0.8, 0.8, 0.8]
        }
        
        for pattern_name, pattern_values in patterns.items():
            wn.add_pattern(pattern_name, pattern_values)
        
        pattern_assignments = {
            'D1': 'residential',
            'D2': 'commercial',
            'D3': 'commercial',
            'D4': 'industrial',
            'D5': 'industrial',
            'D6': 'industrial'
        }
        
        for node, pattern in pattern_assignments.items():
            wn.get_node(node).demand_pattern_name = pattern
        
        wn.options.time.duration = self.simulation_duration
        wn.options.time.hydraulic_timestep = self.time_step
        wn.options.time.pattern_timestep = self.time_step
        wn.options.time.report_timestep = self.time_step
        
        self.wn = wn
        self.total_pipe_cost = total_pipe_cost
    
    def create_network(self, params):
        def get_pipe_length(start_coords, start_elev, end_coords, end_elev, correction_factor=1.2):
            """Calculate pipe length as 3D Euclidean distance times correction factor"""
            dx = end_coords[0] - start_coords[0]
            dy = end_coords[1] - start_coords[1]
            dz = end_elev - start_elev
            return correction_factor * np.sqrt(dx**2 + dy**2 + dz**2)
    
        wn = wntr.network.WaterNetworkModel()
        
        # Add reservoir at coordinates (500, -750)
        reservoir_coords = (500, -750)
        reservoir_elev = get_elevation(np.array(reservoir_coords).reshape(1, -1),
                                        x_min = self.x_min, x_max = self.x_max, y_min = self.y_min, y_max = self.y_max,
                                        lacunarity = self.lacunarity)
        wn.add_reservoir('R1', base_head=reservoir_elev[0], coordinates=reservoir_coords)
        
        # wn.add_reservoir('R1', base_head=100, coordinates=(100, -300))
        
        junctions_data = [
            # Main transmission line
            ('J1', 95, 0, (500, 0)),     # After reservoir
            ('J2', 90, 0, (1000, 0)),    # After pump 1
            ('J3', 85, 0, (1500, 0)),    # Distribution point
            ('J4', 80, 0, (2000, 0)),    # Main distribution hub
            
            # Northern residential zone
            ('J5', 82, 0, (2000, 500)),   # Before pump 2
            ('J6', 78, 0, (2000, 1000)),  # After pump 2
            ('D1', 75, 30, (2500, 1000)), # High-rise residential
            ('D2', 73, 25, (1500, 750)),  # Residential area
            ('D3', 88, 20, (1000, 250)),  # Apartments
            
            # Commercial zone
            ('J7', 77, 0, (2500, 0)),
            ('D4', 75, 45, (3000, 250)),  # Shopping mall
            ('D5', 93, 40, (250, 250)),   # Office complex
            ('D6', 83, 35, (1200, -500)), # Business district
            
            # Southern industrial zone
            ('J8', 76, 0, (2000, -500)),  # Before pump 3
            ('J9', 73, 0, (2000, -1000)), # After pump 3
            ('D7', 70, 60, (2500, -1000)),# Factory
            ('D8', 69, 55, (1350, -1200)), # Manufacturing
            ('D9', 68, 50, (2000, -1500)) # Industrial park
        ]
        # Convert to list to allow modification
        junctions_data = list(list(item) for item in junctions_data)
        
        # Get all node coordinates
        node_coords = np.array([coords[-1] for coords in junctions_data])
    
        # Get elevations for all nodes
        elevations = get_elevation(node_coords, x_min = self.x_min, x_max = self.x_max,
                                    y_min = self.y_min, y_max = self.y_max, lacunarity = self.lacunarity)
    
        for i, (name, elev, demand, coords) in enumerate(junctions_data):
            junctions_data[i][1] = elevations[i]
        
        # Convert to tuple
        junctions_data = list(tuple(item) for item in junctions_data)
        
        # Create dictionaries for quick lookups
        coords = {name: coord for name, _, _, coord in junctions_data}
        coords['R1'] = reservoir_coords
        
        elevs = {name: elev for name, elev, _, _ in junctions_data}
        elevs['R1'] = reservoir_elev[0]
        
        # Add junctions
        for name, elev, demand, coord in junctions_data:
            wn.add_junction(name, elevation=elev, base_demand=demand, coordinates=coord)
        
        # Add pump curves
        pump_curves = {
            'PUMP1': [
                (0, params['pump1_h']),
                (params['pump1_f']*0.5, params['pump1_h']*0.7),
                (params['pump1_f'], params['pump1_h']*0.4)
            ],
            'PUMP2': [
                (0, params['pump2_h']),
                (params['pump2_f']*0.5, params['pump2_h']*0.7),
                (params['pump2_f'], params['pump2_h']*0.4)
            ],
            'PUMP3': [
                (0, params['pump3_h']),
                (params['pump3_f']*0.5, params['pump3_h']*0.7),
                (params['pump3_f'], params['pump3_h']*0.4)
            ]
        }
        
        for pump_name, curve in pump_curves.items():
            wn.add_curve(f'{pump_name}_CURVE', 'HEAD', curve)
        
        # Add pumps
        wn.add_pump('PUMP1', 'J1', 'J2', pump_type='HEAD', pump_parameter='PUMP1_CURVE')
        wn.add_pump('PUMP2', 'J5', 'J6', pump_type='HEAD', pump_parameter='PUMP2_CURVE')
        wn.add_pump('PUMP3', 'J8', 'J9', pump_type='HEAD', pump_parameter='PUMP3_CURVE')
        
        # Add pipes
        pipes_data = [
            # Main transmission
            ('P1', 'R1', 'J1'),
            ('P2', 'J2', 'J3'),
            ('P3', 'J3', 'J4'),
            
            # Northern residential
            ('P4', 'J4', 'J5'),
            ('P5', 'J6', 'D1'),
            ('P6', 'J6', 'D2'),
            ('P7', 'J2', 'D3'),
            
            # Commercial
            ('P8', 'J4', 'J7'),
            ('P9', 'J7', 'D4'),
            ('P10', 'J1', 'D5'),
            ('P11', 'J3', 'D6'),
            
            # Southern industrial
            ('P12', 'J4', 'J8'),
            ('P13', 'J9', 'D7'),
            ('P14', 'J9', 'D8'),
            ('P15', 'J9', 'D9')
        ]
        
        total_pipe_cost = 0
        for name, start, end in pipes_data:
            length = get_pipe_length(coords[start], elevs[start], 
                                   coords[end], elevs[end])
            diameter = params.get(name, 400)
            wn.add_pipe(name, start, end, length, diameter=diameter, roughness=100)
            total_pipe_cost += self.calculate_pipe_cost(diameter, length)
        
        # Add patterns
        patterns = {
            'residential': [0.3, 0.3, 0.3, 0.3, 0.4, 0.5, 0.6, 0.8, 1.0, 1.1, 1.2, 1.3,
                          1.2, 1.1, 1.0, 1.0, 1.1, 1.2, 1.4, 1.6, 1.4, 1.2, 0.8, 0.5],
            'commercial': [0.1, 0.1, 0.1, 0.1, 0.2, 0.3, 0.4, 1.0, 1.5, 1.5, 1.4, 1.3,
                         1.3, 1.4, 1.4, 1.5, 1.5, 1.3, 1.1, 0.8, 0.5, 0.3, 0.2, 0.1],
            'industrial': [0.8, 0.8, 0.8, 0.8, 0.8, 0.8, 1.0, 1.2, 1.2, 1.2, 1.2, 1.2,
                         1.2, 1.2, 1.2, 1.2, 1.2, 1.0, 1.0, 1.0, 1.0, 0.8, 0.8, 0.8]
        }
        
        for pattern_name, pattern_values in patterns.items():
            wn.add_pattern(pattern_name, pattern_values)
        
        pattern_assignments = {
            'D1': 'residential', 'D2': 'residential', 'D3': 'residential',
            'D4': 'commercial', 'D5': 'commercial', 'D6': 'commercial',
            'D7': 'industrial', 'D8': 'industrial', 'D9': 'industrial'
        }
        
        for node, pattern in pattern_assignments.items():
            wn.get_node(node).demand_pattern_name = pattern
        
        wn.options.time.duration = self.simulation_duration
        wn.options.time.hydraulic_timestep = self.time_step
        wn.options.time.pattern_timestep = self.time_step
        wn.options.time.report_timestep = self.time_step
        
        self.wn = wn
        self.total_pipe_cost = total_pipe_cost
    
    def get_network_elements(self):
        elements = {
            'reservoirs': {},
            'junctions': {},
            'demand_nodes': {},
            'pipes': {},
            'pumps': {}
        }
        
        for name, node in self.wn.nodes():
            if isinstance(node, wntr.network.Reservoir):
                elements['reservoirs'][name] = {
                    'base_head': float(node.base_head),
                    'coordinates': tuple(float(x) for x in node.coordinates)
                }
            elif isinstance(node, wntr.network.Junction):
                node_data = {
                    'elevation': float(node.elevation),
                    'coordinates': tuple(float(x) for x in node.coordinates),
                    'base_demand': float(node.base_demand),
                }
                
                if node.base_demand > 0:
                    elements['demand_nodes'][name] = node_data
                else:
                    elements['junctions'][name] = node_data
        
        for name, pipe in self.wn.pipes():
            start_node = pipe.start_node_name
            end_node = pipe.end_node_name
            start_elevation = self.wn.get_node(start_node).base_head if isinstance(self.wn.get_node(start_node), wntr.network.Reservoir) else self.wn.get_node(start_node).elevation
            end_elevation = self.wn.get_node(end_node).base_head if isinstance(self.wn.get_node(end_node), wntr.network.Reservoir) else self.wn.get_node(end_node).elevation
            
            elements['pipes'][name] = {
                'start_node': str(start_node),
                'end_node': str(end_node),
                'length': float(pipe.length),
                'diameter': float(pipe.diameter),
                'roughness': float(pipe.roughness),
                'start_node_elevation': float(start_elevation),
                'end_node_elevation': float(end_elevation)
            }
        
        for name, pump in self.wn.pumps():
            pump_curve = pump.get_pump_curve()
            start_node = self.wn.get_node(pump.start_node_name)
            end_node = self.wn.get_node(pump.end_node_name)
            
            # Handle both reservoir and junction cases for elevations
            start_elevation = start_node.base_head if isinstance(start_node, wntr.network.Reservoir) else start_node.elevation
            end_elevation = end_node.base_head if isinstance(end_node, wntr.network.Reservoir) else end_node.elevation
            
            elements['pumps'][name] = {
                'start_node': str(pump.start_node_name),
                'end_node': str(pump.end_node_name),
                'pump_curve_name': str(pump.pump_curve_name),
                'pump_curve_points': [(float(x), float(y)) for x, y in pump_curve.points],
                'start_node_elevation': float(start_elevation),
                'end_node_elevation': float(end_elevation)
            }
        
        return elements
    
    def save_network_elements(self, filepath, format='json'):
        """Save network elements to a file in specified format"""
        elements = self.get_network_elements()
        
        if format.lower() == 'json':
            import json
            with open(filepath, 'w') as f:
                json.dump(elements, f, indent=4)
        elif format.lower() == 'yaml':
            import yaml
            with open(filepath, 'w') as f:
                yaml.dump(elements, f, default_flow_style=False)
        else:
            raise ValueError("Supported formats are 'json' and 'yaml'")

    def calculate_energy_cost(self, years = 100):
        energy_metrics = {}
        total_cost = 0
        
        # Calculate days per year (assuming 365 days)
        days_per_year = 365
        total_days = days_per_year * years
        
        for pump_name, pump in self.wn.pumps():
            flow = self.sim_results.link['flowrate'][pump_name]
            head_diff = self.sim_results.node['head'][pump.end_node_name] - self.sim_results.node['head'][pump.start_node_name]
            
            # Calculate power (kW)
            power = self.specific_gravity * (flow/1000) * head_diff / self.pump_efficiency
            
            # Calculate energy (kWh) and cost for one day
            daily_energy = power * (self.time_step/3600)
            daily_cost = daily_energy * self.electricity_cost
            
            # Calculate total energy and cost for all years
            total_energy = daily_energy.sum() * total_days
            total_cost_pump = daily_cost.sum() * total_days
            yearly_cost = total_cost_pump / years
            
            energy_metrics[pump_name] = {
                'total_energy': total_energy,
                'average_power': power.mean(),
                'total_cost': total_cost_pump,
                'yearly_cost': yearly_cost,
                'daily_cost': daily_cost.sum(),
                'average_flow': flow.mean(),
                'average_head': head_diff.mean()
            }
            total_cost += total_cost_pump
        
        self.energy_metrics = energy_metrics
        self.energy_cost = total_cost
        
    def check_network_constraints(self):
        constraint_results = {
            'pressure_violations': [],
            'velocity_violations': [],
            'demand_violations': [],
            'pump_violations': [],
            'all_constraints_met': True,
            'pressure_satisfied': True,
            'velocity_satisfied': True,
            'demand_satisfied': True,
            'pump_satisfied': True
        }
        
        # Check pump violations from captured warnings
        for warning in self.sim_warnings:
            if 'Pump' in warning and ('maximum flow' in warning or 'minimum flow' in warning):
                pump_name = warning.split()[1]
                # Get actual flow from simulation results
                actual_flow = self.sim_results.link['flowrate'][pump_name].max() if 'maximum' in warning else self.sim_results.link['flowrate'][pump_name].min()
                # Get flow limits from pump curve
                pump_curve = self.wn.get_link(pump_name).get_pump_curve()
                limit_flow = pump_curve.points[-1][0] if 'maximum' in warning else pump_curve.points[0][0]  # Last/first point's x-value is max/min flow
                
                constraint_results['pump_violations'].append({
                    'pump': pump_name,
                    'type': 'max_flow' if 'maximum' in warning else 'min_flow',
                    'message': warning,
                    'actual_flow': actual_flow,
                    'limit_flow': limit_flow,
                    'metric': np.abs(actual_flow - limit_flow) if 'maximum' in warning else np.abs(limit_flow - actual_flow)
                })
                constraint_results['pump_satisfied'] = False
        
        # Check pressure constraints
        for node_name, node in self.wn.nodes():
            if isinstance(node, wntr.network.Junction):
                pressures = self.sim_results.node['pressure'][node_name]
                
                # Check minimum pressure
                if any(pressures < self.min_pressure):
                    min_pressure = pressures.min()
                    violation_time = pressures.idxmin() / 3600  # Convert to hours
                    constraint_results['pressure_violations'].append({
                        'node': node_name,
                        'type': 'min_pressure',
                        'value': min_pressure,
                        'limit': self.min_pressure,
                        'time': violation_time,
                        'metric': np.abs(min_pressure - self.min_pressure)
                    })
                    constraint_results['pressure_satisfied'] = False
                
                # Check maximum pressure
                if any(pressures > self.max_pressure):
                    max_pressure = pressures.max()
                    violation_time = pressures.idxmax() / 3600
                    constraint_results['pressure_violations'].append({
                        'node': node_name,
                        'type': 'max_pressure',
                        'value': max_pressure,
                        'limit': self.max_pressure,
                        'time': violation_time,
                        'metric': np.abs(max_pressure - self.max_pressure)
                    })
                    constraint_results['pressure_satisfied'] = False
        
        # Check velocity constraints
        for link_name, link in self.wn.links():
            if isinstance(link, wntr.network.Pipe):
                flow = abs(self.sim_results.link['flowrate'][link_name])
                area = np.pi * (link.diameter/1000/2)**2
                velocity = (flow/1000) / area
                
                if any(velocity > self.max_velocity):
                    max_vel = velocity.max()
                    violation_time = velocity.idxmax() / 3600
                    constraint_results['velocity_violations'].append({
                        'pipe': link_name,
                        'value': max_vel,
                        'limit': self.max_velocity,
                        'time': violation_time,
                        'metric': np.abs(max_vel - self.max_velocity)
                    })
                    constraint_results['velocity_satisfied'] = False
        
        # Check demand satisfaction
        demand_nodes = [name for name, node in self.wn.nodes() 
                       if isinstance(node, wntr.network.Junction) and node.base_demand > 0]
        
        for node in demand_nodes:
            base_demand = self.wn.get_node(node).base_demand
            actual_demand = abs(self.sim_results.node['demand'][node])
            
            # Calculate demand satisfaction ratio
            demand_ratio = actual_demand / base_demand
            
            # Check if demand is met (allowing for 5% tolerance)
            if any(demand_ratio < 0.95):
                min_ratio = demand_ratio.min()
                violation_time = demand_ratio.idxmin() / 3600
                constraint_results['demand_violations'].append({
                    'node': node,
                    'required_demand': base_demand,
                    'minimum_actual': actual_demand.min(),
                    'satisfaction_ratio': min_ratio,
                    'time': violation_time,
                    'metric': 1/demand_ratio
                })
                constraint_results['demand_satisfied'] = False
        
        # Update overall constraint satisfaction
        constraint_results['all_constraints_met'] = bool(
            constraint_results['pressure_satisfied'] and 
            constraint_results['velocity_satisfied'] and 
            constraint_results['demand_satisfied'] and
            constraint_results['pump_satisfied']
        )
        
        self.constraint_results = constraint_results

    def calculate_performance_metrics(self):
        
        self.check_network_constraints()
        
        """Calculate performance metrics"""
        metrics = {'pump_violation': 0,  'pressure_violation': 0, 'velocity_violation': 0, 'demand_violation': 0, 'total_metric': 0}
        for item in self.constraint_results['pump_violations']:
            metrics['pump_violation'] += item['metric']
            metrics['total_metric'] += item['metric']
        for item in self.constraint_results['pressure_violations']:
            metrics['pressure_violation'] += item['metric']
            metrics['total_metric'] += item['metric']
        for item in self.constraint_results['velocity_violations']:
            metrics['velocity_violation'] += item['metric']
            metrics['total_metric'] += item['metric']
        for item in self.constraint_results['demand_violations']:
            metrics['demand_violation'] += item['metric']
            metrics['total_metric'] += item['metric']  

        self.performance_metrics = metrics

    def run_simulation(self, params = None):
        """Run simulation with given parameters and return results"""
        try:
            if params is not None:
                self.update_network(params)
            
            self.sim_warnings = []
            with warnings.catch_warnings(record=True) as w:
                warnings.simplefilter("always")
                
                sim = wntr.sim.WNTRSimulator(self.wn)
                self.sim_results = sim.run_sim()
                
                for warning in w:
                    self.sim_warnings.append(str(warning.message))
            
            # Calculate costs and metrics
            self.calculate_energy_cost()
            self.calculate_performance_metrics()

            if self.performance_metrics['total_metric'] > 0:
                self.total_metric = 1000 + self.performance_metrics['total_metric']
            else:
                self.total_metric = self.total_pipe_cost + self.energy_cost
                
            self.total_cost = self.energy_cost + self.total_pipe_cost
            
            return {
                'network': self,
                'success': True,
                'results': self.sim_results,
                'energy_metrics': self.energy_metrics,
                'energy_cost': self.energy_cost,
                'pipe_cost': self.total_pipe_cost,
                'total_cost': self.energy_cost + self.total_pipe_cost,
                'performance_metrics': self.performance_metrics,
                'total_metric': self.total_metric,
                'all_constraints_met': self.constraint_results['all_constraints_met']
            }
            
        except Exception as e:
            print(f"Simulation failed: {str(e)}")
            return {
                'network': self,
                'success': False,
                'error': str(e),
                'total_metric': 1e30,
                'energy_cost': 0,
                'pipe_cost': 0,
                'total_cost': 0,
                'all_constraints_met': False
            }
        
    def plot_network(self, ax = None):
        if ax is not None:
            plt.sca(ax)
        else:
            plt.figure(figsize=(15, 10))
        
        # Build terrain
        terrain, xx, yy = generate_terrain(x_min=self.x_min, x_max=self.x_max,
                                         y_min=self.y_min, y_max=self.y_max, lacunarity=self.lacunarity)
        plt.imshow(terrain, alpha=0.8, cmap='terrain', aspect='auto',
                   extent=(np.min(xx), np.max(xx), np.min(yy), np.max(yy)))
    
        # Get violation data
        pressure_violated_nodes = {v['node'] for v in self.constraint_results['pressure_violations']}
        velocity_violated_pipes = {v['pipe'] for v in self.constraint_results['velocity_violations']}
        demand_violated_nodes = {v['node'] for v in self.constraint_results['demand_violations']}
    
        # Calculate pump powers
        pump_powers = {}
        max_power = 1
        for pump_name, metrics in self.energy_metrics.items():
            pump_powers[pump_name] = metrics['average_power']
            max_power = max(max_power, metrics['average_power'])
    
        # Draw pipes and pumps
        for link_name, link in self.wn.links():
            start_node = self.wn.get_node(link.start_node_name)
            end_node = self.wn.get_node(link.end_node_name)
            start_pos = start_node.coordinates
            end_pos = end_node.coordinates
            
            if isinstance(link, wntr.network.Pipe):
                color = 'red' if link_name in velocity_violated_pipes else 'gray'
                linewidth = link.diameter/100
                plt.plot([start_pos[0], end_pos[0]], [start_pos[1], end_pos[1]],
                        color=color, linewidth=linewidth)
            elif isinstance(link, wntr.network.Pump):
                # Draw pump line
                plt.plot([start_pos[0], end_pos[0]], [start_pos[1], end_pos[1]],
                        color='purple', linewidth=3, zorder=2)
                
                # Calculate pump marker position (middle of the line)
                pump_x = (start_pos[0] + end_pos[0]) / 2
                pump_y = (start_pos[1] + end_pos[1]) / 2
                
                # Draw pump marker
                size = 150 + (np.abs(pump_powers[link_name]) / max_power) * 200
                plt.scatter(pump_x, pump_y, c='purple', marker='o', s=size, zorder=3)
                
                # Add pump label
                plt.annotate(link_name, (pump_x, pump_y),
                            xytext=(0, -20),
                            textcoords='offset points',
                            bbox=dict(facecolor='white', edgecolor='none', alpha=0.7),
                            fontsize=9)
    
        # Draw nodes
        max_demand = max(node.base_demand for _, node in self.wn.nodes() 
                        if isinstance(node, wntr.network.Junction) and node.base_demand > 0)
    
        # Prepare node data
        reservoirs_x, reservoirs_y = [], []
        junction_x, junction_y = [], []
        junction_colors, junction_sizes = [], []
        demand_x, demand_y = [], []
        demand_colors, demand_sizes = [], []
        
        # Collect and plot node data
        for node_name, node in self.wn.nodes():
            x, y = node.coordinates
    
            if isinstance(node, wntr.network.Reservoir):
                reservoirs_x.append(x)
                reservoirs_y.append(y)
                plt.annotate(f"{node_name} ({node.base_head:.0f} m)", (x, y),
                            xytext=(0, 20),
                            textcoords='offset points',
                            bbox=dict(facecolor='white', edgecolor='none', alpha=0.7),
                            fontsize=9)
                
            elif isinstance(node, wntr.network.Junction):                    
                if node.base_demand > 0:  # Demand node
                    demand_x.append(x)
                    demand_y.append(y)
                    size = 150 + (node.base_demand / max_demand) * 150
                    demand_sizes.append(size)
                    demand_colors.append('red' if node_name in demand_violated_nodes else 'blue')
                    plt.annotate(f"{node_name} ({node.elevation:.0f} m)", (x, y),
                                xytext=(0, 20),
                                textcoords='offset points',
                                bbox=dict(facecolor='white', edgecolor='none', alpha=0.7),
                                fontsize=9)
                else:  # Junction node
                    junction_x.append(x)
                    junction_y.append(y)
                    junction_sizes.append(100)
                    junction_colors.append('red' if node_name in pressure_violated_nodes else 'black')
                    plt.annotate(f"{node_name} ({node.elevation:.0f} m)", (x, y),
                                xytext=(0, 20),
                                textcoords='offset points',
                                bbox=dict(facecolor='white', edgecolor='none', alpha=0.7),
                                fontsize=9)
    
        # Draw all nodes
        plt.scatter(reservoirs_x, reservoirs_y, c='orange', marker='s', s=900, label='Reservoir', zorder=2)
        plt.scatter(junction_x, junction_y, c=junction_colors, marker='o', s=junction_sizes, label='Junction', zorder=2)
        plt.scatter(demand_x, demand_y, c=demand_colors, marker='D', s=demand_sizes, label='Demand Node', zorder=2)
    
        # Create legend
        legend_elements = [
            plt.scatter([], [], c='orange', marker='s', s=100, label='Reservoir'),
            plt.scatter([], [], c='black', marker='o', s=100, label='Junction'),
            plt.scatter([], [], c='blue', marker='D', s=100, label='Demand Node'),
            plt.scatter([], [], c='purple', marker='o', s=100, label='Pump'),
            plt.Line2D([0], [0], color='gray', linewidth=2, label='Pipe')
        ]
    
        plt.legend(handles=legend_elements, loc='upper left', fontsize=11, scatterpoints=1)
        plt.title('Water Distribution Network', fontsize=16)
        plt.grid(False)
        plt.xlabel('X Coordinate (m)', fontsize=16)
        plt.ylabel('Y Coordinate (m)', fontsize=16)
        
        if ax is None:
            plt.show()
            
    def plot_junction_violations(self, ax=None):
        if ax is not None:
            plt.sca(ax)
        else:
            # Create figure
            fig, ax = plt.subplots(nrows=1, ncols=1, figsize=(8, 8))
                
        def create_circle_patch(x, y, radius, color, label):
            """Helper function to create a circle with text"""
            circle = plt.Circle((x, y), radius, color=color, alpha=0.8)
            return circle, label
                    
        # Define colors
        success_color = '#006400'  # dark green
        violation_color = '#8B0000'  # dark red
            
        junction_nodes = [(name, node) for name, node in self.wn.nodes() 
                         if isinstance(node, wntr.network.Junction) 
                         and node.base_demand == 0
                         and not name.startswith('PUMP')]
        
        pressure_violated_nodes = {v['node'] for v in self.constraint_results['pressure_violations']}
        
        # Calculate grid dimensions
        cols = 3
        rows = int(np.ceil(len(junction_nodes) / cols))
        
        # Define spacing parameters
        radius = 0.5
        horizontal_spacing = radius * 0.5  # Space between circles horizontally
        vertical_spacing = radius * 0.5    # Space between circles vertically
        
        # Plot circles
        for i, (name, _) in enumerate(junction_nodes):
            col = i % cols
            row = rows - 1 - (i // cols)  # Reverse row order to plot from top to bottom
            
            # Calculate center positions with proper spacing
            x = col * (2 * radius + horizontal_spacing) + radius
            y = row * (2 * radius + vertical_spacing) + radius
            
            color = violation_color if name in pressure_violated_nodes else success_color
            circle, _ = create_circle_patch(x, y, radius, color, name)
            ax.add_patch(circle)
            ax.text(x, y, name, 
                    horizontalalignment='center', 
                    verticalalignment='center', 
                    color='white', 
                    fontweight='bold', 
                    fontsize=13)
        
        # Set proper axis limits with some padding
        ax.set_xlim(0, cols * 2 * radius + (cols - 1) * horizontal_spacing)
        ax.set_ylim(0, rows * 2 * radius + (rows - 1) * vertical_spacing)
                
        # ax.set_aspect('equal')  # Make circles circular instead of elliptical
        ax.axis('off')
        plt.title('Junction constraints', fontsize = 16)
        
        if ax is None:
            plt.show()
    
    def plot_demand_violations(self, ax=None):
        if ax is not None:
            plt.sca(ax)
        else:
            # Create figure
            fig, ax = plt.subplots(nrows=1, ncols=1, figsize=(8, 8))
                
        def create_rhombus_patch(x, y, h_size, v_size, color, label):
            """Helper function to create a rhombus with text"""
            points = [
                (x, y + v_size/2),  # top
                (x + h_size/2, y),  # right
                (x, y - v_size/2),  # bottom
                (x - h_size/2, y)   # left
            ]
            rhombus = plt.Polygon(points, color=color, alpha=0.8)
            return rhombus, label
                    
        # Define colors
        success_color = '#006400'  # dark green
        violation_color = '#8B0000'  # dark red
            
        demand_nodes = [(name, node) for name, node in self.wn.nodes() 
                        if isinstance(node, wntr.network.Junction) 
                        and node.base_demand > 0]
        
        demand_violated_nodes = {v['node'] for v in self.constraint_results['demand_violations']}        
        pressure_violated_nodes = {v['node'] for v in self.constraint_results['pressure_violations']}
        
        # Calculate grid dimensions
        cols = 3
        rows = int(np.ceil(len(demand_nodes) / cols))
        
        # Define spacing parameters
        h_size = 1
        v_size = 1
        horizontal_spacing = h_size * 0.1  # Space between circles horizontally
        vertical_spacing = v_size * 0.1   # Space between circles vertically
        
        # Plot circles
        for i, (name, _) in enumerate(demand_nodes):
            col = i % cols
            row = rows - 1 - (i // cols)  # Reverse row order to plot from top to bottom
            
            # Calculate center positions with proper spacing
            x = col * (h_size + horizontal_spacing) + h_size / 2
            y = row * (v_size + vertical_spacing) + v_size / 2
            
            color = violation_color if name in demand_violated_nodes | pressure_violated_nodes  else success_color
            rhombus, _ = create_rhombus_patch(x, y, h_size, v_size, color, name)
            ax.add_patch(rhombus)
            ax.text(x, y, name, 
                    horizontalalignment='center', 
                    verticalalignment='center', 
                    color='white', 
                    fontweight='bold', 
                    fontsize=13)
        
        # Set proper axis limits with some padding
        ax.set_xlim(0, cols * h_size + (cols - 1) * horizontal_spacing)
        ax.set_ylim(0, rows * v_size + (rows - 1) * vertical_spacing)
                
        # ax.set_aspect('equal')  # Make circles circular instead of elliptical
        ax.axis('off')
        plt.title('Demand node constraints', fontsize = 16)
        
        if ax is None:
            plt.show()
        
    def plot_pipe_pump_violations(self, ax=None):
        if ax is not None:
            plt.sca(ax)
        else:
            # Create figure
            fig, ax = plt.subplots(nrows=1, ncols=1, figsize=(8, 8))
                
        def create_rect_patch(x, y, h_size, v_size, color, label):
            """Helper function to create a square with text"""
            square = plt.Rectangle((x - h_size/2, y - v_size/2), h_size, v_size, 
                                 color=color, alpha=0.8)
            return square, label
                    
        # Define colors
        success_color = '#006400'  # dark green
        violation_color = '#8B0000'  # dark red
            
        pipes = [(name, pipe) for name, pipe in self.wn.links() 
                 if isinstance(pipe, wntr.network.Pipe)]
        
        pumps = [(name, node) for name, node in self.wn.pumps() 
                         if isinstance(node, wntr.network.Pump)]
        
        velocity_violated_pipes = {v['pipe'] for v in self.constraint_results['velocity_violations']}
        violated_pumps = {v['pump'] for v in self.constraint_results['pump_violations']}     
        
        pipes_pumps = pipes + pumps
        
        # Calculate grid dimensions
        cols = 6
        rows = int(np.ceil(len(pipes_pumps) / cols))
        
        # Define spacing parameters
        h_size = 1
        v_size = 1
        horizontal_spacing = h_size * 0.1  # Space between circles horizontally
        vertical_spacing = v_size * 0.1   # Space between circles vertically
                
        for i, (name, _) in enumerate(pipes_pumps):
            col = i % cols
            row = rows - 1 - (i // cols)  # Reverse row order to plot from top to bottom
            
            # Calculate center positions with proper spacing
            x = col * (h_size + horizontal_spacing) + h_size / 2
            y = row * (v_size + vertical_spacing) + v_size / 2
            
            if 'PUMP' in name:
                color = violation_color if name in violated_pumps else success_color
            else:
                color = violation_color if name in velocity_violated_pipes else success_color
            rect, _ = create_rect_patch(x, y, h_size, v_size, color, name)
            ax.add_patch(rect)
            ax.text(x, y, name, 
                    horizontalalignment='center', 
                    verticalalignment='center', 
                    color='white', 
                    fontweight='bold', 
                    fontsize=13)
        
        # Set proper axis limits with some padding
        ax.set_xlim(0, cols * h_size + (cols - 1) * horizontal_spacing)
        ax.set_ylim(0, rows * v_size + (rows - 1) * vertical_spacing)
                
        # ax.set_aspect('equal')  # Make circles circular instead of elliptical
        ax.axis('off')
        plt.title('Pipe and pump constraints', fontsize = 16)
        
        if ax is None:
            plt.show()
        
def plot_result(network, optimization_data = None, path = None):
    
    # Get primary monitor size
    monitor = get_monitors()[0]
    width = monitor.width / 100  # Convert pixels to inches (approximate)
    height = monitor.height / 100
    
    figure = plt.figure(figsize=(width, height), dpi=300)
    
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
    title_ax.text(0.5, 0.7, 'Water distribution network optimization', 
                 horizontalalignment='center',
                 verticalalignment='center',
                 fontsize=16,
                 fontweight='bold')
    
    # Available space after margins
    available_width = 1 - left_margin - right_margin
    available_height = 1 - top_margin - bottom_margin
    
    # Vertical spacing
    ver_space_1 = 0.07
    ver_space_2 = 0.04
    
    # Horizontal spacing
    hor_space_1 = 0.035
    hor_space_2 = 0.01
    hor_space_3 = 0.03
    
    # Define heights relative to available height
    network_height = available_height * 0.6
    junctions_height = 0.45 * network_height
    demands_height = junctions_height
    pipes_height = network_height - junctions_height - ver_space_2
    cost_height = network_height
    param_height = available_height - network_height - ver_space_1
    
    # Define widths
    network_width = 0.33 * available_width
    junctions_width = 0.13 * available_width
    demands_width = 0.14 * available_width
    pipes_width = junctions_width + demands_width + hor_space_2
    cost_width = available_width - network_width - pipes_width - hor_space_1 - hor_space_3
    
    # Calculate positions
    network_x = left_margin
    network_y = 1 - top_margin - network_height
    
    junctions_x = left_margin + network_width + hor_space_1
    junctions_y = 1 - top_margin - junctions_height
    
    demands_x = junctions_x + junctions_width + hor_space_2
    demands_y = junctions_y
    
    pipes_x = junctions_x
    pipes_y = network_y
    
    cost_x = 1 - right_margin - cost_width
    cost_y = network_y
    
    # Add the network plot
    ax = figure.add_axes([network_x, network_y, network_width, network_height])
    network.plot_network(ax=ax)
    
    # Add the junction violations
    ax = figure.add_axes([junctions_x, junctions_y, junctions_width, junctions_height])
    network.plot_junction_violations(ax=ax)
    
    # Add the demand violations
    ax = figure.add_axes([demands_x, demands_y, demands_width, demands_height])
    network.plot_demand_violations(ax=ax)
    
    # Add the pipe violations
    ax = figure.add_axes([pipes_x, pipes_y, pipes_width, pipes_height])
    network.plot_pipe_pump_violations(ax=ax)
    
    # Add the cost
    ax = figure.add_axes([cost_x, cost_y, cost_width, cost_height])
    if optimization_data is None:
        ax.bar(['energy', 'pipes', 'total'], [network.energy_cost, network.total_pipe_cost, network.total_cost])
    else:
        costs = optimization_data['costs']
        costs = costs[costs['all_constraints_met']]
        if len(costs) > 0:
            ax.plot(costs['iter'], costs['energy_cost'], '-o', label = 'Energy cost')
            ax.plot(costs['iter'], costs['pipe_cost'], '-o', label = 'Pipe cost')
            ax.plot(costs['iter'], costs['total_cost'], '-o', label = 'Total cost')
            ax.legend(loc = 'upper right')
            ax.set_xlabel('iteration')
            plt.title('Cost of the network [milion €]', fontsize = 16)
        else:
            metrics = optimization_data['metrics']
            ax.plot(metrics['iter'], metrics['metric'])
            ax.set_xlabel('iteration')
            plt.title('Constraints metric', fontsize = 16)

    # Add the parameters evolution
    if optimization_data is None:
        n_params = 20
        param_width = available_width / n_params
        for i in range(n_params):
            values = np.random.rand(1000)
            hist, edges = np.histogram(values, bins = 50, range = (0,1))
            ax = figure.add_axes([left_margin + i * param_width, bottom_margin, param_width, param_height])
            plt.sca(ax)
            plt.imshow(np.atleast_2d(hist).T, extent = [0,1,0,1],
                       aspect = "auto", origin = 'lower',
                       cmap = 'YlGn')   
            ax.set_xticks([])
            ax.set_yticks([])
            ax.set_xlabel(f'param_{i}')
    else:
        params = optimization_data['parameters']
        # params = params[params['iter'] >= params['iter'].max() - 5]
        params = params.drop(['iter', 'metric'], axis = 1)
        param_names = list(params.columns)
        n_params = len(param_names)
        param_width = available_width / n_params
        for i, p in enumerate(param_names):
            values = params[p]
            hist, edges = np.histogram(values, bins = 100, range = (0,1))
            ax = figure.add_axes([left_margin + i * param_width, bottom_margin, param_width, param_height])
            plt.sca(ax)
            plt.imshow(np.atleast_2d(hist).T, extent = [0,1,0,1],
                       aspect = "auto", origin = 'lower',
                       cmap = 'YlGn')   
            ax.set_xticks([])
            ax.set_yticks([])
            ax.set_xlabel(p)        
            
    update_fontsize(figure, 11)

    if path is not None:
        plt.savefig(path, dpi=300)

    plt.show()
        
# Update all text elements in a figure
def update_fontsize(fig, fontsize):
    # Update title and axis labels for all axes
    for ax in fig.get_axes():
        # Title
        if ax.get_title():
            ax.set_title(ax.get_title(), fontsize=fontsize)
        
        # Axis labels
        ax.set_xlabel(ax.get_xlabel(), fontsize=fontsize)
        ax.set_ylabel(ax.get_ylabel(), fontsize=fontsize)
        
        # Tick labels
        ax.tick_params(axis='both', labelsize=fontsize)
        
        # # Legend
        # if ax.get_legend():
        #     ax.legend(fontsize=fontsize)
            
        # # Colorbar if it exists
        # if hasattr(ax, 'collections'):
        #     for collection in ax.collections:
        #         if collection.colorbar:
        #             collection.colorbar.ax.tick_params(labelsize=fontsize)
        
        # # Text annotations
        # for artist in ax.get_children():
        #     if isinstance(artist, plt.Text):
        #         artist.set_fontsize(fontsize*0.8)
    
def create_realistic_network(x_min = -100, x_max = 3100, y_min = -1600, y_max = 1100, lacunarity = 0.2):
    # Create network model
    wn = wntr.network.WaterNetworkModel()
    
    # Add reservoir at coordinates (500, -750)
    reservoir_coords = (500, -750)
    reservoir_elev = get_elevation(np.array(reservoir_coords).reshape(1, -1),
                                   x_min = x_min, x_max = x_max, y_min = y_min, y_max = y_max,
                                   lacunarity = lacunarity)
    wn.add_reservoir('R1', base_head=reservoir_elev[0], coordinates=reservoir_coords)
    
    # Add junctions
    junctions_data = [
        # Main transmission junctions
        ('J1', 0, 0, (500, 0)),    
        ('J2', 0, 0, (1000, 0)),   
        ('J3', 0, 0, (1500, 0)),   
        ('J4', 0, 0, (2000, 0)),   

        # Northern branch (residential area 1)
        ('J5', 0, 0, (2000, 500)),
        ('D1', 0, 30, (2000, 1000)),  

        # Eastern branch (commercial area)
        ('J6', 0, 0, (2500, 0)),
        ('D2', 0, 50, (3000, 0)),   

        # Southern branch (industrial area)
        ('J7', 0, 0, (2000, -500)),
        ('J8', 0, 0, (2000, -1000)),
        ('D3', 0, 70, (2000, -1500)), 

        # Western branch (residential areas 2 & 3)
        ('J9', 0, 0, (1000, -500)),
        ('D4', 0, 25, (0, -1000)),    
        ('D5', 0, 35, (1000, -1000)),
        ('D6', 0, 15, (0, 0))  # New demand node at (0, 0)
    ]

    # Get all node coordinates
    node_coords = np.array([coords[-1] for coords in junctions_data])

    # Get elevations for all nodes
    elevations = get_elevation(node_coords, x_min = x_min, x_max = x_max, y_min = y_min, y_max = y_max, lacunarity = lacunarity)

    for (name, _, demand, coords), elev in zip(junctions_data, elevations):
        wn.add_junction(name, elevation=elev, base_demand=demand, coordinates=coords)

    # Add pump curves first
    pump_curve_1 = [(0, 50), (100, 40), (200, 25)]  # Q in L/s, H in m
    pump_curve_2 = [(0, 30), (50, 25), (100, 15), (150, 10)]
    wn.add_curve('PUMP1_CURVE', 'HEAD', pump_curve_1)
    wn.add_curve('PUMP2_CURVE', 'HEAD', pump_curve_2)

    # Add pumps with correct specification
    wn.add_pump('PUMP1', 'J2', 'J3', pump_type='HEAD', pump_parameter='PUMP1_CURVE')
    wn.add_pump('PUMP2', 'J7', 'J8', pump_type='HEAD', pump_parameter='PUMP2_CURVE')

    # Add pipes
    pipes_data = [
        # Main transmission
        ('P1', 'J1', 'R1', 500, 600, 100),   
        ('P2', 'J1', 'J2', 500, 600, 100),   
        ('P3', 'J3', 'J4', 500, 500, 100),   

        # Northern branch
        ('P4', 'J4', 'J5', 500, 300, 100),
        ('P5', 'J5', 'D1', 500, 200, 100),

        # Eastern branch
        ('P6', 'J4', 'J6', 500, 400, 100),
        ('P7', 'J6', 'D2', 500, 300, 100),

        # Southern branch
        ('P8', 'J4', 'J7', 500, 400, 100),
        ('P9', 'J8', 'D3', 500, 300, 100),

        # Western branch
        ('P10', 'J2', 'J9', 500, 300, 100),
        ('P11', 'J9', 'D4', 800, 200, 100),
        ('P12', 'J1', 'D6', 500, 300, 100), # New pipe from J1 to D6

        # Cross connections
        ('P13', 'J3', 'J9', 800, 300, 100),
        ('P14', 'J5', 'J6', 1000, 250, 100),
        ('P15', 'J6', 'J7', 800, 250, 100),
        ('P16', 'J8', 'D5', 1200, 200, 100),
        ('P17', 'J5', 'J8', 1500, 250, 100),
        ('P18', 'D1', 'D2', 1000, 200, 100)
    ]

    for name, start, end, length, diam, rough in pipes_data:
        wn.add_pipe(name, start, end, length, diameter=diam, roughness=rough)

    # Add demand patterns
    residential_pattern = [0.3, 0.3, 0.3, 0.3, 0.4, 0.5, 0.6, 0.8, 1.0, 1.1, 1.2, 1.3,
                        1.2, 1.1, 1.0, 1.0, 1.1, 1.2, 1.4, 1.6, 1.4, 1.2, 0.8, 0.5]
    commercial_pattern = [0.1, 0.1, 0.1, 0.1, 0.2, 0.3, 0.4, 1.0, 1.5, 1.5, 1.4, 1.3,
                        1.3, 1.4, 1.4, 1.5, 1.5, 1.3, 1.1, 0.8, 0.5, 0.3, 0.2, 0.1]
    industrial_pattern = [0.8, 0.8, 0.8, 0.8, 0.8, 0.8, 1.0, 1.2, 1.2, 1.2, 1.2, 1.2,
                        1.2, 1.2, 1.2, 1.2, 1.2, 1.0, 1.0, 1.0, 1.0, 0.8, 0.8, 0.8]

    wn.add_pattern('residential', residential_pattern)
    wn.add_pattern('commercial', commercial_pattern)
    wn.add_pattern('industrial', industrial_pattern)

    wn.get_node('D1').demand_pattern_name = 'residential'  # Residential area 1
    wn.get_node('D4').demand_pattern_name = 'residential'  # Residential area 2
    wn.get_node('D5').demand_pattern_name = 'residential'  # Residential area 3
    wn.get_node('D2').demand_pattern_name = 'commercial'   # Commercial area
    wn.get_node('D3').demand_pattern_name = 'industrial'   # Industrial area
    wn.get_node('D6').demand_pattern_name = 'residential'  # New demand node

    # Set simulation duration and time step
    wn.options.time.duration = 24 * 3600  # 24 hours
    wn.options.time.hydraulic_timestep = 3600  # 1 hour
    wn.options.time.pattern_timestep = 3600  # 1 hour

    return wn

def create_water_system():
    # Create a new network model
    wn = wntr.network.WaterNetworkModel()

    # Add reservoir
    wn.add_reservoir('R', base_head=100)

    # Add junctions
    wn.add_junction('J1', elevation=85, base_demand=0)
    wn.add_junction('J2', elevation=80, base_demand=0)
    wn.add_junction('D1', elevation=75, base_demand=80)  # Residential
    wn.add_junction('D2', elevation=70, base_demand=50)  # Commercial
    wn.add_junction('D3', elevation=72, base_demand=70)  # Industrial
    wn.add_junction('SUCT1', elevation=95, base_demand=0)  # Pump suction
    wn.add_junction('DISC1', elevation=95, base_demand=0)  # Pump discharge

    # Add tank
    wn.add_tank('T1', elevation=120, init_level=10, min_level=4, 
                max_level=15, diameter=20)

    # Add pipes
    wn.add_pipe('P1', 'R', 'SUCT1', length=500, diameter=600, roughness=120)
    wn.add_pipe('P2', 'DISC1', 'T1', length=800, diameter=500, roughness=130)
    wn.add_pipe('P3', 'T1', 'J1', length=400, diameter=400, roughness=130)
    wn.add_pipe('P4', 'J1', 'D1', length=600, diameter=250, roughness=140)
    wn.add_pipe('P5', 'J1', 'J2', length=700, diameter=350, roughness=130)
    wn.add_pipe('P6', 'J2', 'D2', length=400, diameter=200, roughness=140)
    wn.add_pipe('P7', 'J2', 'D3', length=500, diameter=300, roughness=130)

    # Add pump with pump curve
    pump_curve = [(0, 80), (50, 78.75), (100, 75), (150, 68.75), (200, 60)]
    wn.add_curve('PUMP1', 'HEAD', pump_curve)
    wn.add_pump('PMP1', 'SUCT1', 'DISC1', 'HEAD', 'PUMP1')

    # Add patterns
    res_pattern = [0.3, 0.3, 0.3, 0.3, 1.2, 1.2, 1.2, 1.2, 
                   1.0, 1.0, 1.0, 1.0, 0.8, 0.8, 0.8, 0.8,
                   1.4, 1.4, 1.4, 1.4, 0.7, 0.7, 0.7, 0.7]
    wn.add_pattern('RES_PAT', res_pattern)

    com_pattern = [0.1, 0.1, 0.1, 0.1, 0.5, 0.5, 0.5, 0.5,
                   1.5, 1.5, 1.5, 1.5, 1.4, 1.4, 1.4, 1.4,
                   0.8, 0.8, 0.8, 0.8, 0.2, 0.2, 0.2, 0.2]
    wn.add_pattern('COM_PAT', com_pattern)

    ind_pattern = [0.8, 0.8, 0.8, 0.8, 1.0, 1.0, 1.0, 1.0,
                   1.2, 1.2, 1.2, 1.2, 1.2, 1.2, 1.2, 1.2,
                   1.0, 1.0, 1.0, 1.0, 0.8, 0.8, 0.8, 0.8]
    wn.add_pattern('IND_PAT', ind_pattern)

    # Assign patterns to demand nodes
    wn.get_node('D1').demand_pattern_name = 'RES_PAT'
    wn.get_node('D2').demand_pattern_name = 'COM_PAT'
    wn.get_node('D3').demand_pattern_name = 'IND_PAT'

    # Set simulation options
    wn.options.time.duration = 24 * 3600  # 24 hours
    wn.options.time.hydraulic_timestep = 3600  # 1 hour
    wn.options.time.pattern_timestep = 3600  # 1 hour
    wn.options.hydraulic.demand_model = 'DD'

    return wn

def create_apulian_network():
    # Create an empty network
    wn = wntr.network.WaterNetworkModel()
    
    # Add reservoir (R)
    wn.add_reservoir('R', base_head=100)
    
    # Add nodes with updated elevations
    # Calculated elevations based on pressure measurements where available
    # Note: J4 with pressure 17.92m implies elevation around 82m (100-17.92)
    # Similar calculations for J13, J16, J23
    nodes_data = [
        ('J1', 82, 0),  # Example elevation
        ('J2', 82, 0),
        ('J3', 82, 0),
        ('J4', 82.08, 0),  # From measured pressure 17.92m
        ('J5', 82, 0),
        ('J6', 82, 0),
        ('J7', 82, 0),
        ('J8', 82, 0),
        ('J9', 82, 0),
        ('J10', 82, 0),
        ('J11', 82, 0),
        ('J12', 82, 0),
        ('J13', 86.63, 0),  # From measured pressure 13.37m
        ('J14', 82, 0),
        ('J15', 82, 0),
        ('J16', 83.45, 0),  # From measured pressure 16.55m
        ('J17', 82, 0),
        ('J18', 82, 0),
        ('J19', 82, 0),
        ('J20', 82, 0),
        ('J21', 82, 0),
        ('J22', 82, 0),
        ('J23', 86.43, 0)   # From measured pressure 13.57m
    ]
    
    for node, elev, demand in nodes_data:
        wn.add_junction(node, elevation=elev, base_demand=demand)
    
    # Add pipes - complete connections based on Figure 2(a)
    # Format: pipe_name, from_node, to_node, length, diameter, roughness
    pipes_data = [
        # Main transmission pipes
        ('P1', 'R', 'J1', 500, 400, 100),
        ('P2', 'J1', 'J2', 500, 400, 100),
        ('P3', 'J2', 'J3', 500, 400, 100),
        ('P4', 'J3', 'J4', 500, 400, 100),
        ('P5', 'J4', 'J5', 500, 400, 100),
        ('P6', 'J5', 'J6', 500, 400, 100),
        
        # Upper branch
        ('P7', 'J1', 'J7', 500, 400, 100),
        ('P8', 'J7', 'J8', 500, 400, 100),
        ('P9', 'J8', 'J9', 500, 400, 100),
        ('P10', 'J9', 'J10', 500, 400, 100),
        ('P11', 'J10', 'J11', 500, 400, 100),
        ('P12', 'J11', 'J12', 500, 400, 100),
        ('P13', 'J12', 'J13', 500, 400, 100),
        
        # Middle section
        ('P14', 'J8', 'J14', 500, 400, 100),
        ('P15', 'J14', 'J15', 500, 400, 100),
        ('P16', 'J15', 'J16', 500, 400, 100),
        ('P17', 'J16', 'J17', 500, 400, 100),
        ('P18', 'J17', 'J18', 500, 400, 100),
        
        # Lower section
        ('P19', 'J15', 'J19', 500, 400, 100),
        ('P20', 'J19', 'J20', 500, 400, 100),
        ('P21', 'J20', 'J21', 500, 400, 100),
        
        # Bottom branch
        ('P22', 'J21', 'J22', 500, 400, 100),
        ('P23', 'J22', 'J23', 500, 400, 100),
        
        # Cross connections
        ('P24', 'J17', 'J20', 500, 400, 100),
        ('P25', 'J18', 'J21', 500, 400, 100),
        
        # Additional connections per Figure 2(a)
        ('P26', 'J22', 'J23', 500, 400, 100),
        ('P27', 'J21', 'J23', 500, 400, 100),
        ('P28', 'J6', 'J16', 500, 400, 100),
        ('P29', 'J6', 'J17', 500, 400, 100),
        ('P30', 'J5', 'J16', 500, 400, 100),
        ('P31', 'J4', 'J15', 500, 400, 100),
        ('P32', 'J3', 'J14', 500, 400, 100),
        ('P33', 'J2', 'J8', 500, 400, 100),
        ('P34', 'J1', 'J7', 500, 400, 100)
    ]
    
    for pipe, start, end, length, diam, rough in pipes_data:
        wn.add_pipe(pipe, start, end, length, diameter=diam, roughness=rough)
    
    # Set simulation options
    wn.options.time.duration = 24*3600  # 24 hours
    wn.options.time.hydraulic_timestep = 3600  # 1 hour
    wn.options.time.pattern_timestep = 3600  # 1 hour
    
    return wn

def run_simulation(wn):
    sim = None
    try:
        sim = wntr.sim.WNTRSimulator(wn)
        results = sim.run_sim()
        return results
    finally:
        if sim is not None:
            # Clean up any references
            del sim

if __name__ == "__main__":
    # wn = create_water_system()
    wn = create_apulian_network()
    results = run_simulation(wn)