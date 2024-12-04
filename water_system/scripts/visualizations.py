# visualizations.py
import wntr
import matplotlib.pyplot as plt
import networkx as nx
import numpy as np
from matplotlib.colors import Normalize
import matplotlib.cm as cm
import wntr.graphics.network as graphics
from water_system import generate_terrain

def plot_network(wn, x_min = -100, x_max = 3100, y_min = -1600, y_max = 1100, lacunarity = 0.2):
    # Create figure
    plt.figure(figsize=(15, 10))
    
    # Build terrain
    terrain, xx, yy = generate_terrain(x_min = x_min, x_max = x_max, y_min = y_min, y_max = y_max, lacunarity = lacunarity)
    plt.imshow(terrain, cmap='terrain', extent=(np.min(xx), np.max(xx), np.min(yy), np.max(yy))) 
    
    # Draw pipes (links)
    for link_name, link in wn.links():
        start_node = wn.get_node(link.start_node_name)
        end_node = wn.get_node(link.end_node_name)

        start_pos = start_node.coordinates
        end_pos = end_node.coordinates

        # Scale line width based on pipe diameter
        if isinstance(link, wntr.network.Pipe):
            linewidth = link.diameter/100
            plt.plot([start_pos[0], end_pos[0]],
                    [start_pos[1], end_pos[1]],
                    'gray',
                    linewidth=linewidth,
                    label=f'Pipe (D={link.diameter}mm)' if link.diameter not in [p.get_label() for p in plt.gca().get_lines()] else "")
        elif isinstance(link, wntr.network.Pump):
            plt.plot([start_pos[0], end_pos[0]],
                    [start_pos[1], end_pos[1]],
                    'blue',
                    linewidth=2,
                    label='Pump')
            # Add pump symbol
            pump_x = (start_pos[0] + end_pos[0]) / 2
            pump_y = (start_pos[1] + end_pos[1]) / 2
            plt.plot(pump_x, pump_y, 'bo', markersize=10)

    # Draw nodes
    for node_name, node in wn.nodes():
        x, y = node.coordinates

        # Create label based on node type
        if isinstance(node, wntr.network.Reservoir):
            plt.plot(x, y, 'bs', markersize=15, label='Reservoir')
            label_text = f"{node_name} ({node.base_head:.0f} m)"
        elif isinstance(node, wntr.network.Tank):
            plt.plot(x, y, 'gs', markersize=15, label='Tank')
            label_text = f"{node_name} ({node.elevation:.0f} m)"
        elif isinstance(node, wntr.network.Junction):
            if node.base_demand > 0:  # Demand node
                plt.plot(x, y, 'ro', markersize=12, label='Demand Node')
                label_text = f"{node_name} ({node.elevation:.0f} m)"
            else:  # Junction node
                plt.plot(x, y, 'ko', markersize=8, label='Junction')
                label_text = f"{node_name} ({node.elevation:.0f} m)"

        # Add node label
        plt.annotate(label_text,
                    (x, y),
                    xytext=(10, 10),
                    textcoords='offset points',
                    bbox=dict(facecolor='white',
                            edgecolor='none',
                            alpha=0.7),
                    fontsize=12)

    plt.title('Water Distribution Network', fontsize=14)
    plt.grid(False)

    # Add legend without duplicates
    handles, labels = plt.gca().get_legend_handles_labels()
    by_label = dict(zip(labels, handles))
    plt.legend(by_label.values(),
              by_label.keys(),
              loc='upper left',
              fontsize=12)

    # Add axis labels
    plt.xlabel('X Coordinate (m)', fontsize=12)
    plt.ylabel('Y Coordinate (m)', fontsize=12)
    plt.tight_layout()
    plt.show()
    
def plot_pressure_heatmap(wn, results, time_step=None):
    """Plot pressure distribution across all nodes at a given time."""
    # Get all junction names
    junction_names = [name for name, node in wn.nodes() 
                     if isinstance(node, wntr.network.Junction)]
    
    # Handle time steps
    if time_step is None:
        # Use average pressure across all time steps
        pressures = [results.node['pressure'][j].mean() for j in junction_names]
    else:
        # Get the available time steps
        time_steps = results.node['pressure'].index
        if time_step not in time_steps:
            print(f"Warning: Time step {time_step} not found. Using last time step.")
            time_step = time_steps[-1]
        pressures = [results.node['pressure'][j][time_step] for j in junction_names]
    
    # Get node coordinates
    x_coords = [wn.get_node(j).coordinates[0] for j in junction_names]
    y_coords = [wn.get_node(j).coordinates[1] for j in junction_names]
    
    plt.figure(figsize=(12, 8))
    scatter = plt.scatter(x_coords, y_coords, c=pressures, cmap='RdYlBu', s=100)
    plt.colorbar(scatter, label='Pressure (m)')
    
    # Add node labels
    for i, j in enumerate(junction_names):
        plt.annotate(f"{j}\n{pressures[i]:.1f}m", 
                    (x_coords[i], y_coords[i]), 
                    xytext=(5, 5), 
                    textcoords='offset points')
    
    title = 'Average Pressure Distribution' if time_step is None else f'Pressure Distribution at {time_step/3600:.1f} hours'
    plt.title(title)
    plt.xlabel('X Coordinate (m)')
    plt.ylabel('Y Coordinate (m)')
    plt.grid(True)
    plt.show()

def plot_flow_distribution(results, time_step=None):
    """Plot flow rate distribution in pipes."""
    pipe_names = results.link['flowrate'].columns
    
    # Handle time steps
    if time_step is None:
        # Use average flow rates
        flow_rates = results.link['flowrate'].mean()
    else:
        # Get the available time steps
        time_steps = results.link['flowrate'].index
        if time_step not in time_steps:
            print(f"Warning: Time step {time_step} not found. Using last time step.")
            time_step = time_steps[-1]
        flow_rates = results.link['flowrate'].loc[time_step]
    
    plt.figure(figsize=(12, 6))
    flow_rates.plot(kind='bar')
    plt.title('Flow Rate Distribution in Pipes')
    plt.xlabel('Pipe Name')
    plt.ylabel('Flow Rate (L/s)')
    plt.xticks(rotation=45)
    plt.grid(True)
    plt.tight_layout()
    plt.show()

def plot_demand_satisfaction(wn, results):
    """Plot actual vs required demand for all demand nodes."""
    demand_nodes = [name for name, node in wn.nodes() 
                   if isinstance(node, wntr.network.Junction) and node.base_demand > 0]
    
    actual_demands = []
    required_demands = []
    
    for node in demand_nodes:
        actual = abs(results.node['demand'][node].mean())  # Take absolute value for comparison
        required = wn.get_node(node).base_demand
        actual_demands.append(actual)
        required_demands.append(required)
    
    plt.figure(figsize=(10, 6))
    x = range(len(demand_nodes))
    width = 0.35
    
    plt.bar(x, required_demands, width, label='Required', color='blue', alpha=0.6)
    plt.bar([i + width for i in x], actual_demands, width, label='Actual', color='red', alpha=0.6)
    
    plt.xlabel('Demand Nodes')
    plt.ylabel('Demand (L/s)')
    plt.title('Demand Satisfaction Analysis')
    plt.xticks([i + width/2 for i in x], demand_nodes, rotation=45)
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.show()

def plot_pump_efficiency(wn, results):
    """Plot pump operating points over time."""
    plt.figure(figsize=(12, 6))
    
    for pump_name, pump in wn.pumps():
        # Get flow and head data
        flow = results.link['flowrate'][pump_name]
        head = results.node['head'][pump.end_node_name] - results.node['head'][pump.start_node_name]
        
        # Plot operating points
        plt.scatter(flow, head, alpha=0.5, label=f'{pump_name} Operating Points')
        
        # Plot pump curve for reference
        if hasattr(pump, 'pump_curve_name'):
            curve = wn.get_curve(pump.pump_curve_name)
            curve_flow = np.array([pt[0] for pt in curve.points])
            curve_head = np.array([pt[1] for pt in curve.points])
            plt.plot(curve_flow, curve_head, '--', label=f'{pump_name} Curve')
    
    plt.title('Pump Operating Points vs Pump Curves')
    plt.xlabel('Flow Rate (L/s)')
    plt.ylabel('Head (m)')
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.show()

def plot_pump_operation_over_time(wn, results):
    """Plot pump flow and head over time."""
    time_hours = np.array(results.time) / 3600.0
    
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8))
    
    for pump_name, pump in wn.pumps():
        # Plot flow over time
        flow = results.link['flowrate'][pump_name]
        ax1.plot(time_hours, flow, label=f'{pump_name} Flow')
        ax1.set_ylabel('Flow Rate (L/s)')
        ax1.set_xlabel('Time (hours)')
        ax1.grid(True)
        ax1.legend()
        
        # Calculate head difference
        head = results.node['head'][pump.end_node_name] - results.node['head'][pump.start_node_name]
        ax2.plot(time_hours, head, label=f'{pump_name} Head')
        ax2.set_ylabel('Head (m)')
        ax2.set_xlabel('Time (hours)')
        ax2.grid(True)
        ax2.legend()
    
    plt.suptitle('Pump Operation Over Time')
    plt.tight_layout()
    plt.show()

def analyze_network(wn, results):
    """Run all analysis plots."""
    # Get actual time steps from results
    time_steps = results.node['pressure'].index
    
    # Use middle time step for snapshot analysis
    mid_time = time_steps[len(time_steps)//2]
    
    print("Analyzing network performance...")
    
    print("\nPressure Distribution at Mid-Simulation:")
    plot_pressure_heatmap(wn, results, mid_time)
    
    print("\nFlow Distribution in Pipes:")
    plot_flow_distribution(results, mid_time)
    
    print("\nDemand Satisfaction Analysis:")
    plot_demand_satisfaction(wn, results)
    
    print("\nPump Performance Analysis:")
    plot_pump_efficiency(wn, results)
    plot_pump_operation_over_time(wn, results)
    
    # Print summary statistics
    print("\nNetwork Performance Summary:")
    print("-" * 40)
    
    # Calculate minimum pressures at demand nodes
    demand_nodes = [name for name, node in wn.nodes() 
                   if isinstance(node, wntr.network.Junction) and node.base_demand > 0]
    
    min_pressures = {node: results.node['pressure'][node].min() for node in demand_nodes}
    print("\nMinimum Pressures at Demand Nodes:")
    for node, pressure in min_pressures.items():
        print(f"{node}: {pressure:.2f} m")
    
    # Calculate maximum flow rates in pipes
    max_flows = results.link['flowrate'].max()
    print("\nMaximum Flow Rates in Pipes:")
    print(f"Maximum flow rate: {max_flows.max():.2f} L/s in pipe {max_flows.idxmax()}")