#%% Imports
import pandas as pd
from cost_function.utils import norm_groups, filter_groups, scale_groups
from cost_function.exceptions import no_data_exception



#%% Calculate the error metric for the output characteristic of a mosfet transistor
def mosfet_output_characteristic(data: pd.DataFrame = None, parameters: pd.DataFrame = None, metric_type: str = 'rmse',
                                 weight = 1, norm: bool = True, scale: str = 'lin', **kwargs):
    
    # Get only the output characteristics
    groups = filter_groups(all_groups = data, relevant_groups = ['ids_vds_vgs', 'id_vd_vg'])
    
    # If no output characteristic present, then raise an error
    if len(groups.index) <= 0:
        raise(no_data_exception())
    
    # Scale to logarithmic if required
    if scale == 'log':
        groups = scale_groups(groups)
        
    # Norm if required
    if norm:
        groups = norm_groups(groups)
        
    

    
    
#%% Calculate the error metric for the output characteristic of a mosfet transistor
def mosfet_transfer_characteristic(data: pd.DataFrame = None, parameters: pd.DataFrame = None,
                                   weight = 1, norm: bool = True, scale: str = 'lin', **kwargs):
    print('kot')
    return 0
    
    
    
    
    
    
    
    
    
    
    
    