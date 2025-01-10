from water_system import create_water_system, run_simulation, create_realistic_network, generate_terrain
from visualizations import analyze_network, plot_network

# generate_terrain(plot = True, lacunarity = 1)


# Create and run simulation
x_min = -100
x_max = 3100
y_min = -1600
y_max = 1100
lacunarity = 0.92
wn = create_realistic_network(x_min, x_max, y_min, y_max, lacunarity)
plot_network(wn, x_min, x_max, y_min, y_max, lacunarity)

results = run_simulation(wn)


# # Create all visualizations
analyze_network(wn, results)