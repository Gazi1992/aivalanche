#%% Imports
import os, numpy as np, matplotlib.pyplot as plt, pandas as pd
from matplotlib.style import context

# Plot all columns of a df
def plot_simplex_2d(points, title = 'title', x_label = 'x', y_label = 'y'):
    figure, ax = plt.subplots(nrows = 1, ncols = 1, figsize=(8, 8))

    # Plot vertices
    plt.scatter(points[:,0], points[:,1], c = 'red', s = 100)

    # Plot edges
    for i in range(points.shape[0]):
        for j in range(i + 1, points.shape[0]):
            plt.plot([points[i,0], points[j,0]], [points[i,1], points[j,1]], 'b--')

    ax.set_title(title)
    ax.set_xlabel(x_label)
    ax.set_ylabel(y_label)
    plt.grid(which='major', linestyle='-', alpha=0.5)
    plt.grid(which='minor', axis='y', linestyle='--', alpha=0.3)

    ax.set_xlim([-10, 10])
    ax.set_ylim([-10, 10])

    plt.show()
