import numpy as np
from pyDOE import lhs
import matplotlib.pyplot as plt
from scipy.stats.qmc import Sobol, Halton
from scipy.spatial.distance import pdist

def evaluate_sampling(samples):
    """Calculate uniformity metrics for samples"""
    distances = pdist(samples)
    return {
        'samples': samples,
        'min_dist': np.min(distances),
        'mean_dist': np.mean(distances),
        'std_dist': np.std(distances)
    }

def generate_samples(n_samples, n_dims, method='sobol'):
    if method == 'sobol':
        sampler = Sobol(d=n_dims, scramble=True)
        samples = sampler.random_base2(m=int(np.ceil(np.log2(n_samples))))[:n_samples]
    elif method == 'halton':
        sampler = Halton(d=n_dims)
        samples = sampler.random(n=n_samples)
    elif method == 'lhs':
        samples = lhs(n_dims, samples=n_samples)
    elif method == 'random':
        samples = np.random.random((n_samples, n_dims))
    return samples

def plot_sampling_comparison(n_samples=50, n_dims=2, save_path=None):
    methods = ['sobol', 'halton', 'lhs', 'random']
    fig, axes = plt.subplots(2, 2, figsize=(12, 12))
    axes = axes.ravel()
    
    for idx, method in enumerate(methods):
        samples = generate_samples(n_samples, n_dims, method)
        result = evaluate_sampling(samples)
        
        ax = axes[idx]
        ax.scatter(result['samples'][:, 0], result['samples'][:, 1], alpha=0.6)
        ax.set_title(f'Method: {method}\nMin dist: {result["min_dist"]:.3f}\n'
                    f'Mean dist: {result["mean_dist"]:.3f}\nStd dist: {result["std_dist"]:.3f}')
        ax.grid(True)
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
    
    plt.tight_layout()
    if save_path:
        plt.savefig(save_path)
    
    return fig, axes

sample_sizes = [10, 50, 100]
for n in sample_sizes:
    fig, axes = plot_sampling_comparison(n_samples=n, save_path=f'sampling_comparison_n{n}.png')