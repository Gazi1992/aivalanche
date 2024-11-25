import numpy as np
import matplotlib.pyplot as plt

def create_spider_chart(df, title="Spider Chart", figsize=(10, 10)):
    """
    Create a spider/radar chart from a pandas DataFrame.
    
    Parameters:
    -----------
    df : pandas.DataFrame
        DataFrame where each column is a parameter and each row is a sample
    title : str
        Title of the chart
    figsize : tuple
        Figure size in inches (width, height)
        
    Returns:
    --------
    fig, ax : matplotlib figure and axis objects
    """
    # Get the parameters (column names) and number of parameters
    parameters = df.columns.tolist()
    num_params = len(parameters)
    
    # Calculate the angle for each parameter
    angles = [n / float(num_params) * 2 * np.pi for n in range(num_params)]
    # angles += angles[:1]  # Complete the circle
    
    # Create the plot
    fig, ax = plt.subplots(figsize=figsize, subplot_kw=dict(projection='polar'))
    
    # Draw parameter lines
    plt.xticks(angles, parameters)
    
    # Plot data
    for idx, row in df.iterrows():
        values = row.values.flatten().tolist()
        # values += values[:1]  # Complete the circle
        
        # Plot the values
        ax.plot(angles, values, linewidth=1, linestyle='solid', label=f"Sample {idx}")
        # ax.fill(angles, values, alpha=0.1)
    
    # Add legend
    plt.legend(loc='upper right', bbox_to_anchor=(0.1, 0.1))
    
    plt.title(title)
    
    plt.show()
    
    return fig, ax

def normalize_dataframe(df):
    """
    Normalize the DataFrame values to a 0-1 scale for each parameter.
    
    Parameters:
    -----------
    df : pandas.DataFrame
        Input DataFrame
        
    Returns:
    --------
    pandas.DataFrame
        Normalized DataFrame
    """
    return (df - df.min()) / (df.max() - df.min())