import os, tempfile, dask
from dask import delayed
from dask.distributed import LocalCluster, Client

class SimulationManager:
    def __init__(self):
        # Initialize Dask cluster and client
        self.cluster = LocalCluster(n_workers=4)  # Adjust the number of workers as needed
        self.client = Client(self.cluster)

    def run_single_simulation(self, parameters):
        # Create a temporary directory for each worker
        with tempfile.TemporaryDirectory() as temp_dir:
            # Simulate some computation (replace this with your actual simulation)
            result = parameters ** 2

            # Create a temporary file in the worker's directory and write the result
            temp_file_path = os.path.join(temp_dir, 'result.txt')
            with open(temp_file_path, 'w') as temp_file:
                temp_file.write(f'Result: {result}')

            return temp_file_path

    def run_simulations(self, parameter_list):
        # Create delayed objects for each simulation with pure=True
        simulation_futures = [
            delayed(self.run_single_simulation)(param) for param in parameter_list
        ]

        # Compute the results using Dask
        results = dask.compute(simulation_futures, scheduler="threads", num_workers=len(parameter_list))

        # Close the Dask client and cluster
        self.client.close()
        self.cluster.close()

        return results

# Example usage
if __name__ == '__main__':
    sim_manager = SimulationManager()

    # Define a list of parameters for simulations
    parameters_list = [1, 2, 3, 4, 5]

    # Run simulations in parallel
    simulation_results = sim_manager.run_simulations(parameters_list)

    # Print the paths of the result files
    print("Simulation Result Files:", simulation_results)
