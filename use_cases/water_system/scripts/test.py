import wntr
import numpy as np
import matplotlib.pyplot as plt

class WaterNetworkOptimizer:
    def __init__(self):
        # Energy parameters
        self.pump_efficiency = 0.75  # pump efficiency
        self.specific_gravity = 9.81  # kN/m³
        self.electricity_cost = 0.15  # $/kWh
        
        # Pipe cost parameters (simplified cost model)
        self.pipe_cost_params = {
            # Cost = a * diameter^b + c
            'a': 1.1,  # cost coefficient
            'b': 1.5,  # diameter exponent
            'c': 100   # base cost per meter
        }
        
        # Constraints
        self.min_pressure = 20  # meters
        self.max_pressure = 80  # meters
        self.max_velocity = 2.0  # m/s
        
        # Network layout parameters
        self.simulation_duration = 24 * 3600  # 24 hours in seconds
        self.time_step = 3600  # 1 hour in seconds

    def calculate_pipe_cost(self, diameter, length):
        """Calculate pipe cost based on diameter (mm) and length (m)"""
        p = self.pipe_cost_params
        cost = (p['a'] * (diameter ** p['b']) + p['c']) * length
        return cost

    def create_network(self, pump_params, pipe_params):
        """
        Create network with given pump and pipe parameters
        
        Parameters:
        -----------
        pump_params : dict
            'pump1_head_max': Maximum head for pump 1 (m)
            'pump1_flow_max': Maximum flow for pump 1 (L/s)
            'pump2_head_max': Maximum head for pump 2 (m)
            'pump2_flow_max': Maximum flow for pump 2 (L/s)
        
        pipe_params : dict
            Dictionary of pipe diameters (mm) with pipe names as keys
        """
        wn = wntr.network.WaterNetworkModel()
        
        # Add reservoir
        wn.add_reservoir('R1', base_head=311, coordinates=(500, -750))
        
        # Add junctions with their elevations and demands
        junctions_data = [
            ('J1', 256, 0, (500, 0)),    
            ('J2', 267, 0, (1000, 0)),   
            ('J3', 153, 0, (1500, 0)),   
            ('J4', 60, 0, (2000, 0)),   
            ('J5', 225, 0, (2000, 500)),
            ('D1', 177, 30, (2000, 1000)),  # Residential
            ('J6', 139, 0, (2500, 0)),
            ('D2', 127, 50, (3000, 0)),    # Commercial
            ('J7', 90, 0, (2000, -500)),
            ('J8', 99, 0, (2000, -1000)),
            ('D3', 142, 70, (2000, -1500)), # Industrial
            ('J9', 247, 0, (1000, -500)),
            ('D4', 249, 25, (0, -1000)),    # Residential
            ('D5', 190, 35, (1000, -1000)), # Residential
            ('D6', 210, 15, (0, 0))         # Residential
        ]
        
        for name, elev, demand, coords in junctions_data:
            wn.add_junction(name, elevation=elev, base_demand=demand, coordinates=coords)

        # Add pumps with their curves
        pump_curves = {
            'PUMP1': [
                (0, pump_params['pump1_head_max']),
                (pump_params['pump1_flow_max']*0.5, pump_params['pump1_head_max']*0.64),
                (pump_params['pump1_flow_max'], pump_params['pump1_head_max']*0.25)
            ],
            'PUMP2': [
                (0, pump_params['pump2_head_max']),
                (pump_params['pump2_flow_max']*0.5, pump_params['pump2_head_max']*0.64),
                (pump_params['pump2_flow_max'], pump_params['pump2_head_max']*0.25)
            ]
        }
        
        for pump_name, curve in pump_curves.items():
            wn.add_curve(f'{pump_name}_CURVE', 'HEAD', curve)
        
        wn.add_pump('PUMP1', 'J2', 'J3', pump_type='HEAD', pump_parameter='PUMP1_CURVE')
        wn.add_pump('PUMP2', 'J7', 'J8', pump_type='HEAD', pump_parameter='PUMP2_CURVE')

        # Add pipes
        pipes_data = [
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
            ('P13', 'J8', 'D5', 1200)
        ]
        
        total_pipe_cost = 0
        for name, start, end, length in pipes_data:
            diameter = pipe_params.get(name, 300)  # default 300mm if not specified
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

        return wn, total_pipe_cost

    def calculate_energy_cost(self, wn, results):
        """Calculate energy consumption and cost for all pumps"""
        energy_metrics = {}
        total_cost = 0
        
        for pump_name, pump in wn.pumps():
            flow = results.link['flowrate'][pump_name]
            head_diff = results.node['head'][pump.end_node_name] - results.node['head'][pump.start_node_name]
            
            # Calculate power (kW)
            power = self.specific_gravity * (flow/1000) * head_diff / self.pump_efficiency
            
            # Calculate energy (kWh) and cost
            energy = power * (self.time_step/3600)
            cost = energy * self.electricity_cost
            
            energy_metrics[pump_name] = {
                'total_energy': energy.sum(),
                'average_power': power.mean(),
                'total_cost': cost.sum(),
                'average_flow': flow.mean(),
                'average_head': head_diff.mean()
            }
            total_cost += cost.sum()
        
        return energy_metrics, total_cost

    def calculate_metrics(self, results, wn):
        """Calculate performance metrics"""
        metrics = {}
        
        # Pressure metrics
        pressures = []
        for node_name, node in wn.nodes():
            if isinstance(node, wntr.network.Junction):
                node_pressures = results.node['pressure'][node_name]
                pressures.extend(node_pressures)
                
        metrics['min_pressure'] = min(pressures)
        metrics['max_pressure'] = max(pressures)
        
        # Velocity metrics
        velocities = {}
        for link_name, link in wn.links():
            if isinstance(link, wntr.network.Pipe):
                flow = abs(results.link['flowrate'][link_name])
                area = np.pi * (link.diameter/1000/2)**2
                velocity = (flow/1000) / area
                velocities[link_name] = velocity.max()
        
        metrics['max_velocity'] = max(velocities.values())
        metrics['velocities'] = velocities
        
        return metrics

    def run_simulation(self, pump_params, pipe_params):
        """Run simulation with given parameters and return results"""
        try:
            # Create network
            wn, pipe_cost = self.create_network(pump_params, pipe_params)
            
            # Run simulation
            sim = wntr.sim.WNTRSimulator(wn)
            results = sim.run_sim()
            
            # Calculate costs and metrics
            energy_metrics, energy_cost = self.calculate_energy_cost(wn, results)
            performance_metrics = self.calculate_metrics(results, wn)
            
            return {
                'success': True,
                'results': results,
                'energy_metrics': energy_metrics,
                'energy_cost': energy_cost,
                'pipe_cost': pipe_cost,
                'total_cost': energy_cost + pipe_cost,
                'performance_metrics': performance_metrics
            }
            
        except Exception as e:
            print(f"Simulation failed: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }

    def plot_results(self, simulation_data):
        """Plot comprehensive results"""
        if not simulation_data['success']:
            print("No results to plot - simulation failed")
            return
        
        results = simulation_data['results']
        metrics = simulation_data['performance_metrics']
        
        fig = plt.figure(figsize=(15, 10))
        gs = plt.GridSpec(3, 2)
        
        # 1. Pressure at demand nodes
        ax1 = fig.add_subplot(gs[0, :])
        time_hours = results.node['pressure'].index / 3600
        demand_nodes = ['D1', 'D2', 'D3', 'D4', 'D5', 'D6']
        
        for node in demand_nodes:
            ax1.plot(time_hours, results.node['pressure'][node], label=node)
        ax1.set_xlabel('Time (hours)')
        ax1.set_ylabel('Pressure (m)')
        ax1.set_title('Pressure at Demand Nodes')
        ax1.grid(True)
        ax1.legend()
        
        # 2. Pump flow rates
        ax2 = fig.add_subplot(gs[1, 0])
        for pump in ['PUMP1', 'PUMP2']:
            ax2.plot(time_hours, results.link['flowrate'][pump], label=pump)
        ax2.set_xlabel('Time (hours)')
        ax2.set_ylabel('Flow Rate (L/s)')
        ax2.set_title('Pump Flow Rates')
        ax2.grid(True)
        ax2.legend()
        
        # 3. Energy costs
        ax3 = fig.add_subplot(gs[1, 1])
        energy_costs = [m['total_cost'] for m in simulation_data['energy_metrics'].values()]
        pump_names = list(simulation_data['energy_metrics'].keys())
        ax3.bar(pump_names, energy_costs)
        ax3.set_ylabel('Energy Cost ($)')
        ax3.set_title('Daily Energy Cost by Pump')
        
        # 4. Cost summary
        ax4 = fig.add_subplot(gs[2, 0])
        costs = [
            simulation_data['energy_cost'],
            simulation_data['pipe_cost'],
            simulation_data['total_cost']
        ]
        ax4.bar(['Energy', 'Pipes', 'Total'], costs)
        ax4.set_ylabel('Cost ($)')
        ax4.set_title('Cost Breakdown')
        
        # 5. Performance metrics
        ax5 = fig.add_subplot(gs[2, 1])
        metrics_text = (
            f"Min Pressure: {metrics['min_pressure']:.1f}m\n"
            f"Max Pressure: {metrics['max_pressure']:.1f}m\n"
            f"Max Velocity: {metrics['max_velocity']:.1f}m/s\n"
            f"Total Cost: ${simulation_data['total_cost']:.2f}\n"
            f"Energy Cost: ${simulation_data['energy_cost']:.2f}\n"
            f"Pipe Cost: ${simulation_data['pipe_cost']:.2f}"
        )
        ax5.text(0.1, 0.5, metrics_text, transform=ax5.transAxes, fontsize=10)
        ax5.axis('off')
        
        plt.tight_layout()
        plt.show()

def main():
    # Create optimizer
    optimizer = WaterNetworkOptimizer()
    
    # Define parameters
    pump_params = {
        'pump1_head_max': 40,
        'pump1_flow_max': 150,
        'pump2_head_max': 30,
        'pump2_flow_max': 120
    }
    
    # Define pipe diameters (mm)
    pipe_params = {
        'P1': 600,   # Main transmission
        'P2': 600,
        'P3': 500,
        'P4': 300,
        'P5': 200,   # To demand nodes
        'P6': 400,
        'P7': 300,
        'P8': 400,
        'P9': 300,
        'P10': 300,
        'P11': 200,
        'P12': 300,
        'P13': 200
    }
    
    # Run simulation with these parameters
    results = optimizer.run_simulation(pump_params, pipe_params)
    
    if results['success']:
        # Print summary
        print("\nSimulation Results Summary:")
        print("-" * 40)
        print(f"Total Cost: ${results['total_cost']:.2f}")
        print(f"  Energy Cost: ${results['energy_cost']:.2f}")
        print(f"  Pipe Cost: ${results['pipe_cost']:.2f}")
        
        print("\nPerformance Metrics:")
        metrics = results['performance_metrics']
        print(f"  Minimum Pressure: {metrics['min_pressure']:.1f} m")
        print(f"  Maximum Pressure: {metrics['max_pressure']:.1f} m")
        print(f"  Maximum Velocity: {metrics['max_velocity']:.1f} m/s")
        
        print("\nPump Performance:")
        for pump, metrics in results['energy_metrics'].items():
            print(f"\n{pump}:")
            print(f"  Average Flow: {metrics['average_flow']:.1f} L/s")
            print(f"  Average Power: {metrics['average_power']:.1f} kW")
            print(f"  Daily Energy Cost: ${metrics['total_cost']:.2f}")
        
        # Plot results
        optimizer.plot_results(results)
        
    else:
        print(f"Simulation failed: {results['error']}")

if __name__ == "__main__":
    main()