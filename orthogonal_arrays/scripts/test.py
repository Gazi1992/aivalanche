import numpy as np
from itertools import combinations
import time
from tqdm import tqdm
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

def check_combinations_power_encoding(data, strength_combinations, nr_required_combinations):
    """Check combinations using power encoding method"""
    levels = 3
    results = []
    
    for combo in strength_combinations:
        subarray = data[:, combo]
        powers = np.array([levels**i for i in range(len(combo))], dtype=np.int64)
        combined = (subarray * powers).sum(axis=1)
        unique_count = len(np.unique(combined))
        results.append(unique_count == nr_required_combinations)
    
    return np.all(results)

def check_combinations_direct(data, strength_combinations, nr_required_combinations):
    """Check combinations using direct unique method"""
    results = []
    
    for combo in strength_combinations:
        subarray = data[:, combo]
        unique_count = len(np.unique(subarray, axis=0))
        results.append(unique_count == nr_required_combinations)
    
    return np.all(results)

def run_comparison(rows, strength, n_runs=5):
    """Run comparison for specific array size and strength"""
    # Create test array
    cols = 10  # Fixed number of columns
    array = np.random.randint(0, 3, size=(rows, cols))
    strength_combinations = np.array(list(combinations(range(cols), strength)))
    nr_required_combinations = 3 ** strength
    
    # Warm up
    for _ in range(2):
        check_combinations_power_encoding(array, strength_combinations, nr_required_combinations)
        check_combinations_direct(array, strength_combinations, nr_required_combinations)
    
    # Time power encoding method
    start_time = time.time()
    for _ in range(n_runs):
        check_combinations_power_encoding(array, strength_combinations, nr_required_combinations)
    power_time = (time.time() - start_time) / n_runs
    
    # Time direct method
    start_time = time.time()
    for _ in range(n_runs):
        check_combinations_direct(array, strength_combinations, nr_required_combinations)
    direct_time = (time.time() - start_time) / n_runs
    
    return {
        'rows': rows,
        'strength': strength,
        'power_time': power_time * 1000,  # Convert to milliseconds
        'direct_time': direct_time * 1000,
        'speedup': direct_time / power_time,
        'n_combinations': len(strength_combinations)  # Added to show complexity
    }

def plot_results(results_df):
    """Create plots from the results using pure matplotlib"""
    # Create figure with multiple subplots
    fig = plt.figure(figsize=(20, 10))
    gs = plt.GridSpec(2, 2)
    
    # Colors and markers for different strengths
    colors = ['b', 'r', 'g', 'purple']
    markers = ['o', 's', '^', 'D']
    
    # Plot 1: Times vs Rows for each Strength and Method
    ax1 = fig.add_subplot(gs[0, 0])
    
    for idx, strength in enumerate(sorted(results_df['strength'].unique())):
        mask = results_df['strength'] == strength
        # Plot power encoding times
        ax1.plot(results_df[mask]['rows'], results_df[mask]['power_time'],
                color=colors[idx], marker=markers[idx], linestyle='-',
                label=f'Power Encoding (s={strength})')
        # Plot direct method times
        ax1.plot(results_df[mask]['rows'], results_df[mask]['direct_time'],
                color=colors[idx], marker=markers[idx], linestyle='--',
                label=f'Direct Method (s={strength})')
    
    ax1.set_xlabel('Number of Rows')
    ax1.set_ylabel('Time (milliseconds)')
    ax1.set_title('Performance Comparison')
    ax1.set_xscale('log')
    ax1.set_yscale('log')
    ax1.grid(True)
    ax1.legend()
    
    # Plot 2: Speedup vs Rows for each Strength
    ax2 = fig.add_subplot(gs[0, 1])
    
    for idx, strength in enumerate(sorted(results_df['strength'].unique())):
        mask = results_df['strength'] == strength
        ax2.plot(results_df[mask]['rows'], results_df[mask]['speedup'],
                color=colors[idx], marker=markers[idx],
                label=f'Strength={strength}')
    
    ax2.set_xlabel('Number of Rows')
    ax2.set_ylabel('Speedup (Direct Time / Power Time)')
    ax2.set_title('Speedup Factor')
    ax2.set_xscale('log')
    ax2.grid(True)
    ax2.legend()
    
    # Plot 3: Times vs Number of Combinations
    ax3 = fig.add_subplot(gs[1, 0])
    
    # Group by n_combinations and calculate mean times
    combo_stats = results_df.groupby('n_combinations').agg({
        'power_time': 'mean',
        'direct_time': 'mean'
    }).reset_index()
    
    ax3.plot(combo_stats['n_combinations'], combo_stats['power_time'],
             'bo-', label='Power Encoding')
    ax3.plot(combo_stats['n_combinations'], combo_stats['direct_time'],
             'rs-', label='Direct Method')
    
    ax3.set_xlabel('Number of Combinations')
    ax3.set_ylabel('Time (milliseconds)')
    ax3.set_title('Performance vs Complexity')
    ax3.set_xscale('log')
    ax3.set_yscale('log')
    ax3.grid(True)
    ax3.legend()
    
    # Plot 4: Scatter plot of speedup
    ax4 = fig.add_subplot(gs[1, 1])
    
    for idx, strength in enumerate(sorted(results_df['strength'].unique())):
        mask = results_df['strength'] == strength
        ax4.scatter(results_df[mask]['rows'], results_df[mask]['speedup'],
                   color=colors[idx], marker=markers[idx], s=100,
                   label=f'Strength={strength}')
    
    ax4.set_xlabel('Number of Rows')
    ax4.set_ylabel('Speedup (Direct Time / Power Time)')
    ax4.set_title('Speedup Distribution')
    ax4.set_xscale('log')
    ax4.grid(True)
    ax4.legend()
    
    plt.tight_layout()
    return fig

if __name__ == "__main__":
    # Test parameters
    row_sizes = [500, 1000, 2000, 5000, 10000]
    strengths = [2, 3, 4, 5]
    n_runs = 5  # Number of runs to average over
    
    # Store results
    results = []
    
    # Run tests
    total_tests = len(row_sizes) * len(strengths)
    with tqdm(total=total_tests, desc="Running tests") as pbar:
        for rows in row_sizes:
            for strength in strengths:
                try:
                    result = run_comparison(rows, strength, n_runs)
                    results.append(result)
                    pbar.set_postfix({
                        'rows': rows, 
                        'strength': strength, 
                        'speedup': f"{result['speedup']:.2f}x"
                    })
                except Exception as e:
                    print(f"Error with rows={rows}, strength={strength}: {str(e)}")
                pbar.update(1)
    
    # Convert to DataFrame
    results_df = pd.DataFrame(results)
    
    # Print summary
    print("\nSummary of results:")
    summary = results_df.groupby('strength').agg({
        'speedup': ['mean', 'min', 'max'],
        'power_time': 'mean',
        'direct_time': 'mean',
        'n_combinations': 'first'
    }).round(3)
    print("\nSpeedup statistics by strength:")
    print(summary)
    
    print("\nDetailed timing statistics (milliseconds):")
    timing_stats = results_df.groupby(['strength', 'rows']).agg({
        'power_time': 'mean',
        'direct_time': 'mean',
        'speedup': 'mean'
    }).round(3)
    print(timing_stats)
    
    # Create and save plots
    fig = plot_results(results_df)
    # plt.savefig('cpu_performance_comparison.png', dpi=300, bbox_inches='tight')
    # print("\nPlot saved as 'cpu_performance_comparison.png'")
    
    # Save detailed results
    # results_df.to_csv('cpu_performance_results.csv', index=False)
    # print("Detailed results saved to 'cpu_performance_results.csv'")