NO_DATA_ERROR = 9e10
NO_GROUP_ERROR = 8e10
PART_FAILED_ERROR = 7e10
HUGE_ERROR = 1e10


#%% Wrapper of exceptions
def raise_exception(exception_type: str = None, *args):
    if exception_type is not None:
        try:
            raise globals()[exception_type](*args)
        except Exception as e:
            return e.error_metric


#%% custom exception class for missing data
class no_data_exception(Exception):
    def __init__(self, message: str = None):
        
        if message is not None:
            print(message)
        else:
            print('ERROR: No data available.')
            print(f'returning NO_DATA_ERROR: {NO_DATA_ERROR}')
        
        self.error_metric = NO_DATA_ERROR


#%% custom exception class for missing group
class no_group_exception(Exception):
    def __init__(self, message: str = None, group_types: list[str] = None):
        
        if message is not None:
            print(message)
        else:
            print('ERROR: No group found for the following types:')
            print(group_types)
            print(f'returning NO_GROUP_ERROR: {NO_GROUP_ERROR}')
        
        self.error_metric = NO_GROUP_ERROR


#%% custom exception class for failing error metric calculation
class failed_error_metric_exception(Exception):
    def __init__(self, message: str = None, group_types: list[str] = None):
        
        if message is not None:
            print(message)
        else:
            print('ERROR: No group found for the following types:')
            print(group_types)
            print(f'returning PART_FAILED_ERROR: {PART_FAILED_ERROR}')
        
        self.error_metric = PART_FAILED_ERROR
    
    
    
    
    
    
    
    