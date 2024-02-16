from dask.distributed import LocalCluster, Client


# Initialize dask client
def init_dask(scale:int  = 2, dask_env: str = 'local', uplaod_files: list = []):
    cluster = None
    if dask_env == 'local':
        cluster = LocalCluster()
        print('dashboard_link: ', cluster.dashboard_link)
    elif dask_env == 'containers':
        cluster = Client("scheduler:8786")
        if len(uplaod_files) > 0:
            for file in uplaod_files:
                cluster.upload_file(file)
                print('uploading file: ', file)
        print('dashboard_link: ', cluster.dashboard_link)
    else:
        print('Error: dask_env has to be one of the following: ["local", "containers"].')
        print('Dask not initialized. Returning none.')
    return cluster


# Close the dask client: not working properly, needs to be fixed
def close_dask(cluster):
    try:
        cluster.close()
    except Exception as e:
        print(f"Error closing cluster: ${e}")
        pass

