'''
Author: Gazmend Alia
Description: parser class is used for processing the .
Inputs:
    file -> 

'''

#%% Imports
import pandas as pd
import numpy as np
import json


#%% differential_evolution class

class parser:
    def __init__(self,
                 file: str = None, # the path of the reference data file
               ):
        
        self.file = file
        self.raw_data = None
        self.dataframe = pd.DataFrame()

    # Convert json file to pandas dataframe
    def json_to_dataframe(self):
        with open(self.file) as json_file:
            self.raw_data = json.load(json_file)
            print(self.raw_data)
            
            
        
        


        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
