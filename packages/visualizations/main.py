import pandas as pd
from utils import normalize_dataframe, create_spider_chart


# Create sample data
data = {
    'Parameter1': [4, 3, 5],
    'Parameter2': [2, 4, 3],
    'Parameter3': [5, 2, 1],
    'Parameter4': [3, 3, 4],
    'Parameter5': [1, 5, 2]
}
df = pd.DataFrame(data)

# Normalize the data (recommended for parameters with different scales)
# df_normalized = normalize_dataframe(df)

# Create the spider chart
fig, ax = create_spider_chart(df, title="Sample Spider Chart")
