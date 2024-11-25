import numpy as np
import pyqtgraph as pg
import pandas as pd

def create_histogram_heatmaps(df, num_bins=30, title="Parameter Distributions"):
    """
    Create horizontal arrangement of histogram heatmaps using PyQtGraph.
    
    Parameters:
    -----------
    df : pandas.DataFrame
        DataFrame where each column is a parameter
    num_bins : int
        Number of bins for the histograms
    title : str
        Title for the plot
        
    Returns:
    --------
    window : GraphicsLayoutWidget
        The created plot widget containing all histograms
    """
    # Create the window
    window = pg.GraphicsLayoutWidget(title=title)
    window.resize(200 * len(df.columns), 300)
    
    # Normalize each column to [0,1] range
    df_normalized = pd.DataFrame()
    for column in df.columns:
        min_val = df[column].min()
        max_val = df[column].max()
        if max_val != min_val:
            df_normalized[column] = (df[column] - min_val) / (max_val - min_val)
        else:
            df_normalized[column] = 0.5
    
    # Calculate histograms
    total_max = 0
    histograms = []
    
    for column in df_normalized.columns:
        hist, bin_edges = np.histogram(df_normalized[column], 
                                     bins=num_bins, 
                                     range=(0, 1), 
                                     density=True)
        histograms.append((hist, bin_edges))
        total_max = max(total_max, np.max(hist))
    
    # Create color map
    colormap = pg.colormap.get('viridis')
    
    # Create plots
    first_plot = None
    for i, (column, (hist, bin_edges)) in enumerate(zip(df.columns, histograms)):
        # Create plot
        plot = window.addPlot()
        
        # Link y-axis to first plot
        if first_plot is None:
            first_plot = plot
        else:
            plot.setYLink(first_plot)
        
        # Hide all axes
        plot.hideAxis('left')
        plot.hideAxis('bottom')
        
        # Create image item
        img = pg.ImageItem()
        plot.addItem(img)
        
        # Reshape histogram for image display
        hist_2d = hist.reshape(-1, 1).T
        
        # Set image data
        img.setImage(hist_2d)
        img.setLookupTable(colormap.getLookupTable(0.0, 1.0, 256))
        img.setLevels([0, total_max])
        
        # Position the image correctly
        rect = pg.QtCore.QRectF(0, 0, 1, 1)
        img.setRect(rect)
        
        # Set plot range
        plot.setXRange(-0.1, 1.1)  # Slightly wider range to accommodate labels
        plot.setYRange(-0.1, 1.1)
        
        # Set only the parameter name as title
        plot.setTitle(column)
        
        # Add min/max value labels
        min_val = df[column].min()
        max_val = df[column].max()
        
        # Add min label at bottom
        min_label = pg.TextItem(f"{min_val:.2f}", anchor=(0.5, 0))
        min_label.setPos(0.5, 0.02)  # Position at bottom center
        plot.addItem(min_label)
        
        # Add max label at top
        max_label = pg.TextItem(f"{max_val:.2f}", anchor=(0.5, 1))
        max_label.setPos(0.5, 0.98)  # Position at top center
        plot.addItem(max_label)
        
        # Remove margins between plots
        plot.setMouseEnabled(x=False, y=False)  # Disable mouse interaction
        plot.getViewBox().setDefaultPadding(0)  # Remove padding
        plot.showAxis('top', show=False)
        plot.showAxis('right', show=False)
    
    return window

# Example usage
if __name__ == "__main__":
    # Create sample data with different distributions
    np.random.seed(42)
    n_samples = 1000
    data = {
        'Normal': np.random.normal(0, 1, n_samples),
        'Uniform': np.random.uniform(-2, 2, n_samples),
        'Exponential': np.random.exponential(1, n_samples),
        'Bimodal': np.concatenate([
            np.random.normal(-1, 0.3, n_samples//2),
            np.random.normal(1, 0.3, n_samples//2)
        ])
    }
    df = pd.DataFrame(data)
    
    # Create and show the visualization
    window = create_histogram_heatmaps(df, num_bins=50, title="Parameter Distributions")
    window.show()
    
    # Keep the window open
    if __name__ == '__main__':
        pg.exec()