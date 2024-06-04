import pandas as pd

# Function to convert semicolumn to list of items when reading a csv
def convert_to_list_if_semi_colon(value):
    if isinstance(value, str) and ';' in value:
        return value.split(';')
    return value

# Filter a dataframe by col_name and value
def filter_df_by_col_name_and_val(df: pd.DataFrame, col_name: str, val: object, single: bool = True):
    filtered = df[df[col_name] == val]
    if len(filtered.index) > 0 and single:
        filtered = filtered.iloc[0, :]
    return filtered