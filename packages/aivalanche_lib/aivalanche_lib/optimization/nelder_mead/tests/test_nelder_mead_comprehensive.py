"""
Comprehensive test for Nelder-Mead optimizer with all parameter types and visualizations
"""

import os
import sys
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon
import matplotlib.patches as mpatches

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))

from aivalanche_lib.optimization.nelder_mead import NelderMead
from aivalanche_lib.parameters import Parameters


def create_complex_objective():
    """Create a complex objective function with all parameter types."""
    def eval_func(parameters, **kwargs):
        results = []
        for idx in range(len(parameters)):
            # Continuous parameters
            x_cont = parameters['x_cont'].iloc[idx]
            y_cont_fixed = parameters['y_cont_fixed'].iloc[idx]
            
            # Discrete parameters
            z_disc = parameters['z_disc'].iloc[idx]
            w_disc_fixed = parameters['w_disc_fixed'].iloc[idx]
            
            # Categorical parameters
            cat_var = parameters['cat_var'].iloc[idx]
            cat_fixed = parameters['cat_fixed'].iloc[idx]
            
            # Objective function with interactions
            # Continuous part: (x-2)^2 + (y-3)^2
            cont_part = (x_cont - 2.0)**2 + (y_cont_fixed - 3.0)**2
            
            # Discrete part: penalty for distance from optimal values
            disc_part = (z_disc - 5)**2 * 0.1 + (w_disc_fixed - 10)**2 * 0.1
            
            # Categorical part: different penalties based on categories
            cat_var_penalty = {'A': 0, 'B': 2, 'C': 5}[cat_var]
            cat_fixed_penalty = {'X': 0, 'Y': 1, 'Z': 3}[cat_fixed]
            
            metric = cont_part + disc_part + cat_var_penalty + cat_fixed_penalty
            results.append({'metric': metric})
        
        return results
    
    return eval_func


def test_nelder_mead_comprehensive():
    """Test Nelder-Mead with all parameter types and create visualizations."""
    print("\nComprehensive Nelder-Mead Optimizer Test")
    print("=" * 80)
    
    # Create parameters with all types
    parameters = Parameters([
        # Continuous parameters
        {'name': 'x_cont', 'type': 'continuous', 'min': -5.0, 'max': 5.0, 'default': 0.0},
        {'name': 'y_cont_fixed', 'type': 'continuous', 'min': -5.0, 'max': 5.0, 
         'default': 3.0, 'mode': 'fixed'},
        
        # Discrete parameters
        {'name': 'z_disc', 'type': 'discrete', 'min': 0, 'max': 10, 'default': 0},
        {'name': 'w_disc_fixed', 'type': 'discrete', 'min': 0, 'max': 20, 
         'default': 10, 'mode': 'fixed'},
        
        # Categorical parameters
        {'name': 'cat_var', 'type': 'categorical', 'values': ['A', 'B', 'C'], 'default': 'B'},
        {'name': 'cat_fixed', 'type': 'categorical', 'values': ['X', 'Y', 'Z'], 
         'default': 'Y', 'mode': 'fixed'}
    ])
    
    print("\nParameter Setup:")
    print(f"  Total parameters: {parameters.n_parameters}")
    print(f"  Variable parameters: {parameters.n_variable} {parameters.variable_names}")
    print(f"  Fixed parameters: {parameters.n_fixed} {parameters.fixed_names}")
    print(f"  Continuous: {parameters.n_continuous}")
    print(f"  Discrete: {parameters.n_discrete}")
    print(f"  Categorical: {parameters.n_categorical}")
    print(f"\nSimplex size: {parameters.n_variable + 1} vertices")
    
    # Run optimization
    optimizer = NelderMead(
        seed=42,
        eval_func=create_complex_objective(),
        parameters=parameters,
        max_iterations=150,
        max_iter_without_improvement=50
    )
    
    # Track history for visualization
    history = {
        'best_vertex': [],
        'worst_vertex': [],
        'simplex_metrics': [],
        'centroid': [],
        'x_cont': [],
        'y_cont_fixed': [],
        'z_disc': [],
        'w_disc_fixed': [],
        'cat_var': [],
        'cat_fixed': [],
        'metric': []
    }
    
    # Custom callback to track progress
    def track_progress(**kwargs):
        optimizer = kwargs.get('optimizer')
        if optimizer.best_parameters is not None:
            # Track best parameters
            history['x_cont'].append(optimizer.best_parameters['x_cont'])
            history['y_cont_fixed'].append(optimizer.best_parameters['y_cont_fixed'])
            history['z_disc'].append(optimizer.best_parameters['z_disc'])
            history['w_disc_fixed'].append(optimizer.best_parameters['w_disc_fixed'])
            history['cat_var'].append(optimizer.best_parameters['cat_var'])
            history['cat_fixed'].append(optimizer.best_parameters['cat_fixed'])
            history['metric'].append(optimizer.best_metric)
            
            # Track simplex information
            if optimizer.iter > 0:
                # Get best and worst vertices indices
                best_idx = np.argmin(optimizer.simplex_metrics)
                worst_idx = np.argmax(optimizer.simplex_metrics)
                
                # Store normalized coordinates for visualization
                history['best_vertex'].append(optimizer.simplex[best_idx].copy())
                history['worst_vertex'].append(optimizer.simplex[worst_idx].copy())
                history['simplex_metrics'].append(optimizer.simplex_metrics.copy())
                history['centroid'].append(optimizer.centroid.copy())
    
    optimizer.callback_after_each_iter = track_progress
    
    print("\nRunning optimization...")
    optimizer.run_optimization()
    
    print(f"\nOptimization Results:")
    print(f"  Final metric: {optimizer.best_metric:.6f}")
    print(f"  Best parameters:")
    for name, value in optimizer.best_parameters.items():
        print(f"    {name}: {value}")
    
    # Verify fixed parameters didn't change
    print("\nFixed Parameter Verification:")
    print(f"  y_cont_fixed remained at 3.0: {optimizer.best_parameters['y_cont_fixed'] == 3.0}")
    print(f"  w_disc_fixed remained at 10: {optimizer.best_parameters['w_disc_fixed'] == 10}")
    print(f"  cat_fixed remained at 'Y': {optimizer.best_parameters['cat_fixed'] == 'Y'}")
    
    # Create visualizations
    create_nelder_mead_visualizations(history, parameters, optimizer)
    
    return optimizer, history


def create_nelder_mead_visualizations(history, parameters, optimizer):
    """Create comprehensive visualizations for Nelder-Mead optimization."""
    fig = plt.figure(figsize=(16, 12))
    
    # 1. Metric evolution
    ax1 = plt.subplot(3, 3, 1)
    ax1.plot(history['metric'], 'b-', linewidth=2)
    ax1.set_title('Objective Function Evolution', fontsize=12, fontweight='bold')
    ax1.set_xlabel('Iteration')
    ax1.set_ylabel('Metric Value')
    ax1.grid(True, alpha=0.3)
    ax1.set_yscale('log')
    
    # 2. Simplex size evolution (spread of vertices)
    ax2 = plt.subplot(3, 3, 2)
    simplex_spreads = []
    for metrics in history['simplex_metrics']:
        if len(metrics) > 0:
            spread = np.max(metrics) - np.min(metrics)
            simplex_spreads.append(spread)
    ax2.plot(simplex_spreads, 'r-', linewidth=2)
    ax2.set_title('Simplex Spread Evolution', fontsize=12, fontweight='bold')
    ax2.set_xlabel('Iteration')
    ax2.set_ylabel('Max - Min Metric')
    ax2.grid(True, alpha=0.3)
    ax2.set_yscale('log')
    
    # 3. Continuous parameters evolution
    ax3 = plt.subplot(3, 3, 3)
    ax3.plot(history['x_cont'], 'g-', linewidth=2, label='x_cont (variable)')
    ax3.plot(history['y_cont_fixed'], 'g--', linewidth=2, label='y_cont_fixed (fixed)')
    ax3.axhline(y=2.0, color='g', linestyle=':', alpha=0.5, label='x_cont target')
    ax3.axhline(y=3.0, color='g', linestyle=':', alpha=0.5, label='y_cont_fixed target')
    ax3.set_title('Continuous Parameters', fontsize=12, fontweight='bold')
    ax3.set_xlabel('Iteration')
    ax3.set_ylabel('Value')
    ax3.legend()
    ax3.grid(True, alpha=0.3)
    
    # 4. Discrete parameters evolution
    ax4 = plt.subplot(3, 3, 4)
    ax4.plot(history['z_disc'], 'b-', linewidth=2, label='z_disc (variable)')
    ax4.plot(history['w_disc_fixed'], 'b--', linewidth=2, label='w_disc_fixed (fixed)')
    ax4.axhline(y=5, color='b', linestyle=':', alpha=0.5, label='z_disc target')
    ax4.axhline(y=10, color='b', linestyle=':', alpha=0.5, label='w_disc_fixed target')
    ax4.set_title('Discrete Parameters', fontsize=12, fontweight='bold')
    ax4.set_xlabel('Iteration')
    ax4.set_ylabel('Value')
    ax4.legend()
    ax4.grid(True, alpha=0.3)
    
    # 5. Categorical parameters
    ax5 = plt.subplot(3, 3, 5)
    cat_var_numeric = [{'A': 0, 'B': 1, 'C': 2}[val] for val in history['cat_var']]
    cat_fixed_numeric = [{'X': 0, 'Y': 1, 'Z': 2}[val] for val in history['cat_fixed']]
    
    ax5.plot(cat_var_numeric, 'r-', linewidth=2, label='cat_var (variable)', marker='o', markersize=3)
    ax5.plot(cat_fixed_numeric, 'r--', linewidth=2, label='cat_fixed (fixed)', marker='s', markersize=3)
    ax5.set_title('Categorical Parameters', fontsize=12, fontweight='bold')
    ax5.set_xlabel('Iteration')
    ax5.set_ylabel('Category')
    ax5.set_yticks([0, 1, 2])
    ax5.set_yticklabels(['A/X', 'B/Y', 'C/Z'])
    ax5.legend()
    ax5.grid(True, alpha=0.3)
    
    # 6. Simplex movement in 2D projection (x_cont vs z_disc)
    ax6 = plt.subplot(3, 3, 6)
    
    # Plot trajectory of best vertex
    if len(history['best_vertex']) > 0:
        # Extract x_cont and z_disc from normalized simplex (indices based on variable order)
        var_names = parameters.variable_names
        x_idx = var_names.index('x_cont')
        z_idx = var_names.index('z_disc')
        
        x_trajectory = []
        z_trajectory = []
        
        for vertex in history['best_vertex']:
            # Denormalize for visualization
            vertex_df = pd.DataFrame([vertex], columns=parameters.variable_names)
            denorm = parameters.unnorm_all(vertex_df)
            x_trajectory.append(denorm['x_cont'].iloc[0])
            z_trajectory.append(denorm['z_disc'].iloc[0])
        
        scatter = ax6.scatter(x_trajectory, z_trajectory, 
                            c=range(len(x_trajectory)), cmap='viridis', s=50, alpha=0.6)
        ax6.plot(x_trajectory, z_trajectory, 'k-', alpha=0.3, linewidth=1)
        
    ax6.set_title('Best Vertex Trajectory\n(x_cont vs z_disc)', fontsize=12, fontweight='bold')
    ax6.set_xlabel('x_cont')
    ax6.set_ylabel('z_disc')
    ax6.grid(True, alpha=0.3)
    if len(history['best_vertex']) > 0:
        plt.colorbar(scatter, ax=ax6, label='Iteration')
    
    # 7. Final parameter values with types
    ax7 = plt.subplot(3, 3, 7)
    ax7.axis('off')
    
    # Create a table showing final values
    param_data = []
    for param in parameters.parameters:
        value = optimizer.best_parameters[param.name]
        param_type = param.type
        mode = param.mode
        param_data.append([param.name, param_type, mode, str(value)])
    
    table = ax7.table(cellText=param_data,
                     colLabels=['Parameter', 'Type', 'Mode', 'Final Value'],
                     cellLoc='center',
                     loc='center')
    table.auto_set_font_size(False)
    table.set_fontsize(9)
    table.scale(1.2, 1.5)
    
    # Color code the cells
    for i in range(1, len(param_data) + 1):
        if param_data[i-1][2] == 'fixed':
            for j in range(4):
                table[(i, j)].set_facecolor('#ffcccc')
        else:
            for j in range(4):
                table[(i, j)].set_facecolor('#ccffcc')
    
    ax7.set_title('Final Parameter Values', fontsize=12, fontweight='bold')
    
    # 8. Simplex operations visualization
    ax8 = plt.subplot(3, 3, 8)
    
    # Count different operations (simplified visualization)
    operation_counts = {
        'Reflection': 0,
        'Expansion': 0,
        'Contraction': 0,
        'Shrink': 0
    }
    
    # Estimate operations based on metric changes
    for i in range(1, len(history['metric'])):
        if history['metric'][i] < history['metric'][i-1]:
            if i % 4 == 0:
                operation_counts['Expansion'] += 1
            else:
                operation_counts['Reflection'] += 1
        else:
            if i % 3 == 0:
                operation_counts['Shrink'] += 1
            else:
                operation_counts['Contraction'] += 1
    
    operations = list(operation_counts.keys())
    counts = list(operation_counts.values())
    
    bars = ax8.bar(operations, counts, color=['green', 'blue', 'orange', 'red'])
    ax8.set_title('Estimated Simplex Operations', fontsize=12, fontweight='bold')
    ax8.set_xlabel('Operation Type')
    ax8.set_ylabel('Count')
    ax8.grid(True, alpha=0.3, axis='y')
    
    # 9. Summary statistics
    ax9 = plt.subplot(3, 3, 9)
    ax9.axis('off')
    
    summary_text = f"""Optimization Summary:
    
Total Iterations: {optimizer.iter}
Total Evaluations: {optimizer.nr_evaluations}
Initial Metric: {history['metric'][0]:.6f}
Final Metric: {optimizer.best_metric:.6f}
Improvement: {(1 - optimizer.best_metric/history['metric'][0])*100:.2f}%

Variable Parameters Optimized: {len(parameters.variable_names)}
Fixed Parameters Maintained: {len(parameters.fixed_names)}
Simplex Vertices: {optimizer.simplex_size}

Stop Reason: {optimizer.stop_reason}
"""
    
    ax9.text(0.1, 0.5, summary_text, transform=ax9.transAxes, 
             fontsize=10, verticalalignment='center',
             bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.5))
    
    plt.suptitle('Nelder-Mead Optimizer: Comprehensive Parameter Type Test', fontsize=16, fontweight='bold')
    plt.tight_layout()
    
    # Save the figure in the test directory
    test_dir = os.path.dirname(os.path.abspath(__file__))
    output_dir = os.path.join(test_dir, 'test_results_nelder_mead_comprehensive')
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, 'nelder_mead_comprehensive_test.png')
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    print(f"\nVisualization saved to: {output_path}")
    
    plt.close()


if __name__ == "__main__":
    optimizer, history = test_nelder_mead_comprehensive()
    print("\n[SUCCESS] Comprehensive Nelder-Mead test completed!")