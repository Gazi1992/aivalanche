import numpy as np
import pyqtgraph as pg
import pandas as pd

def create_parallel_coordinates(df, title="Parallel Coordinates Plot"):
    """
    Create a parallel coordinates plot using PyQtGraph.
    
    Parameters:
    -----------
    df : pandas.DataFrame
        DataFrame where each column is a parameter and each row is a sample
    title : str
        Title for the plot
        
    Returns:
    --------
    plot_widget : pyqtgraph.PlotWidget
        The created plot widget
    """
    # Create the plot widget
    plot_widget = pg.plot(title=title)
    
    # Get number of parameters and samples
    num_params = len(df.columns)
    num_samples = len(df)
    
    # Normalize the data
    df_normalized = df.copy()
    for column in df.columns:
        min_val = df[column].min()
        max_val = df[column].max()
        if max_val != min_val:
            df_normalized[column] = (df[column] - min_val) / (max_val - min_val)
        else:
            df_normalized[column] = 0.5  # Set to middle if all values are the same
    
    # Create x coordinates for parameters (evenly spaced)
    x_coords = np.arange(num_params)
    
    # Plot vertical lines for parameters
    for i in range(num_params):
        # Draw vertical line
        line = pg.PlotDataItem([i, i], [0, 1], pen=pg.mkPen(color=(100, 100, 100), width=1))
        plot_widget.addItem(line)
        
        # Add parameter label
        label = pg.TextItem(df.columns[i], anchor=(0.5, 0))
        label.setPos(i, -0.1)
        plot_widget.addItem(label)
        
        # Add tick marks
        num_ticks = 5
        for tick in range(num_ticks + 1):
            y = tick / num_ticks
            tick_line = pg.PlotDataItem(
                [i-0.1, i+0.1], [y, y],
                pen=pg.mkPen(color=(100, 100, 100), width=1)
            )
            plot_widget.addItem(tick_line)
            
            # Add original value label (non-normalized)
            orig_val = df[df.columns[i]].min() + y * (df[df.columns[i]].max() - df[df.columns[i]].min())
            value_label = pg.TextItem(f'{orig_val:.2f}', anchor=(1, 0.5))
            value_label.setPos(i-0.15, y)
            plot_widget.addItem(value_label)
    
    # Plot the data lines
    colors = [(255, 0, 0), (0, 255, 0), (0, 0, 255),
              (255, 255, 0), (255, 0, 255), (0, 255, 255)]
    
    for idx, (_, row) in enumerate(df_normalized.iterrows()):
        # Get x and y coordinates for this sample
        x = x_coords
        y = row.values
        
        # Create line with custom color
        color = colors[idx % len(colors)]
        line = pg.PlotDataItem(
            x, y,
            pen=pg.mkPen(color=color, width=2),
            name=f'Sample {idx+1}'
        )
        plot_widget.addItem(line)
    
    # Set up the view
    plot_widget.setXRange(-0.5, num_params - 0.5)
    plot_widget.setYRange(-0.2, 1.2)
    plot_widget.hideAxis('left')
    plot_widget.hideAxis('bottom')
    
    # Add legend
    legend = plot_widget.addLegend()
    
    return plot_widget

# Example usage
if __name__ == "__main__":
    # Create sample data
    data = {
        'Speed': [120, 90, 150, 80],
        'Weight': [1500, 2000, 1800, 1600],
        'Power': [200, 150, 250, 180],
        'Efficiency': [25, 30, 20, 28],
        'Cost': [35000, 25000, 45000, 30000]
    }
    df = pd.DataFrame(data)
    
    # Create and show the plot
    plot = create_parallel_coordinates(df, "Car Specifications Comparison")
    pg.exec()