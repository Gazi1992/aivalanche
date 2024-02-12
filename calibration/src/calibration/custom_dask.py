from dask.distributed import LocalCluster


# Initialize dask client
def init_dask(scale:int  = 2, dask_env: str = 'local'):
    cluster = None
    if dask_env == 'local':
        cluster = LocalCluster()
        print('dashboard_link: ', cluster.dashboard_link)
    else:
        print('Error: dask_env has to be one of the following: ["local"].')
        print('Dask not initialized. Returning none.')
    return cluster


# Close the dask client: not working properly, needs to be fixed
def close_dask(cluster):
    try:
        cluster.close()
    except Exception as e:
        print(f"Error closing cluster: ${e}")
        pass

