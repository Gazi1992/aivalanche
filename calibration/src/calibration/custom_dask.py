from dask.distributed import LocalCluster

# Initialize dask client
def init_dask(scale: int  = 2):
    cluster = LocalCluster()
    print('dashboard_link: ', cluster.dashboard_link)
    return cluster

# Close the dask client: not working properly, needs to be fixed
def close_dask(cluster):
    try:
        cluster.close()
    except Exception as e:
        print(f"Error closing cluster: ${e}")
        pass

