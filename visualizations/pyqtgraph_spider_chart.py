import numpy as np
import pyqtgraph as pg
import pandas as pd

def create_spider_plot(df, title="Spider Plot"):
    """
    Create a standalone spider/radar plot using PyQtGraph.
    
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
    plot_widget.hideAxis('left')
    plot_widget.hideAxis('bottom')
    plot_widget.setAspectLocked()
    
    # Calculate angles for parameters
    num_params = len(df.columns)
    angles = np.linspace(0, 2*np.pi, num_params, endpoint=False)
    
    # Draw grid lines
    levels = 5
    for level in range(1, levels + 1):
        radius = level / levels
        points = 100
        theta = np.linspace(0, 2*np.pi, points)
        x = radius * np.cos(theta)
        y = radius * np.sin(theta)
        plot_widget.plot(x, y, pen=pg.mkPen(color=(100, 100, 100), width=0.5))
    
    # Draw parameter axes
    for angle in angles:
        x = [0, np.cos(angle)]
        y = [0, np.sin(angle)]
        plot_widget.plot(x, y, pen=pg.mkPen(color=(100, 100, 100), width=0.5))
    
    # Add parameter labels
    for i, param in enumerate(df.columns):
        angle = angles[i]
        x = 1.2 * np.cos(angle)
        y = 1.2 * np.sin(angle)
        text = pg.TextItem(param, anchor=(0.5, 0.5))
        text.setPos(x, y)
        plot_widget.addItem(text)
    
    # Plot data for each sample
    colors = [(255, 0, 0), (0, 255, 0), (0, 0, 255), 
              (255, 255, 0), (255, 0, 255), (0, 255, 255)]
    
    for idx, (_, row) in enumerate(df.iterrows()):
        # Normalize data if needed
        data = row.values
        if np.max(data) > 1 or np.min(data) < 0:
            data = (data - np.min(data)) / (np.max(data) - np.min(data))
        
        # Calculate points
        x = data * np.cos(angles)
        y = data * np.sin(angles)
        
        # Close the polygon
        x = np.append(x, x[0])
        y = np.append(y, y[0])
        
        # Create plot with fill
        color = colors[idx % len(colors)]
        plot_widget.plot(x, y, 
                        pen=pg.mkPen(color=color, width=2),
                        fillLevel=0,
                        fillBrush=pg.mkBrush(color=color + (50,)),
                        name=f'Sample {idx+1}')
    
    return plot_widget

# Example usage
if __name__ == "__main__":
    # Create sample data
    data = {
        'Speed': [0.8, 0.3, 0.5],
        'Power': [0.2, 0.9, 0.3],
        'Accuracy': [0.5, 0.2, 0.8],
        'Durability': [0.3, 0.6, 0.4],
        'Cost': [0.7, 0.4, 0.6]
    }
    df = pd.DataFrame(data)
    
    # Create and show the plot
    plot = create_spider_plot(df, "Performance Metrics")
    
    # This line keeps the plot window open
    pg.exec()