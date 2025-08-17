"""
Filter Quality Analysis - Visualizing Good vs Bad Filter Responses
===================================================================
This script generates various filter responses to illustrate what makes
a filter good or bad by comparing different designs against the ideal response.
"""

import sys
import os
from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import json

# Add paths
sys.path.append(str(Path(__file__).parent))
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "packages" / "aivalanche_lib"))

from mzi_gds_simulator import MZIFilterGDSSimulator


def create_filter_examples():
    """Create different filter parameter sets representing various quality levels."""
    
    # Load configuration
    inputs_dir = Path(__file__).parent.parent / "inputs"
    simulator = MZIFilterGDSSimulator(inputs_dir / "filter_config.json")
    
    # Load default parameters as baseline
    params_df = pd.read_csv(inputs_dir / "parameters.csv")
    default_params = {row['name']: row['default'] for _, row in params_df.iterrows()}
    
    examples = {}
    
    # 1. IDEAL-LIKE (Very Good) - Sharp transitions, low loss, high extinction
    examples['ideal_like'] = default_params.copy()
    examples['ideal_like']['delta_L'] = 16.485  # Optimized path difference
    # Optimized coupling ratios for sharp transition
    kappas_ideal = [0.023, 0.235, 0.144, 0.169, 0.141, 0.486, 0.099, 
                    0.448, 0.446, 0.217, 0.333, 0.092, 0.059]
    for i, k in enumerate(kappas_ideal):
        examples['ideal_like'][f'kappa_{i}'] = k
    
    # 2. GOOD - Reasonable performance, meets most specs
    examples['good'] = default_params.copy()
    examples['good']['delta_L'] = 15.8
    # Slightly sub-optimal coupling ratios
    kappas_good = [0.05, 0.22, 0.15, 0.18, 0.16, 0.45, 0.12,
                   0.42, 0.43, 0.20, 0.31, 0.10, 0.08]
    for i, k in enumerate(kappas_good):
        examples['good'][f'kappa_{i}'] = k
    
    # 3. MEDIOCRE - Some issues but partially functional
    examples['mediocre'] = default_params.copy()
    examples['mediocre']['delta_L'] = 14.5
    # Less optimized coupling ratios
    kappas_med = [0.1, 0.2, 0.2, 0.2, 0.2, 0.35, 0.2,
                  0.35, 0.35, 0.25, 0.25, 0.15, 0.12]
    for i, k in enumerate(kappas_med):
        examples['mediocre'][f'kappa_{i}'] = k
    
    # 4. POOR - High crosstalk, slow roll-off
    examples['poor'] = default_params.copy()
    examples['poor']['delta_L'] = 13.0
    # Poor coupling ratios - too uniform
    kappas_poor = [0.15] * 13  # All same value - poor design
    for i, k in enumerate(kappas_poor):
        examples['poor'][f'kappa_{i}'] = k
    
    # 5. BAD - Very high insertion loss, poor extinction
    examples['bad'] = default_params.copy()
    examples['bad']['delta_L'] = 18.0  # Wrong path difference
    # Random coupling ratios
    np.random.seed(42)
    kappas_bad = np.random.uniform(0.05, 0.45, 13)
    for i, k in enumerate(kappas_bad):
        examples['bad'][f'kappa_{i}'] = k
    
    # 6. TERRIBLE - Completely wrong parameters
    examples['terrible'] = default_params.copy()
    examples['terrible']['delta_L'] = 10.0  # Way off
    # Very poor coupling ratios
    kappas_terrible = [0.02] * 13  # Too weak coupling
    for i, k in enumerate(kappas_terrible):
        examples['terrible'][f'kappa_{i}'] = k
    
    return examples, simulator


def plot_comparison_figure(examples, simulator):
    """Create comprehensive comparison figure."""
    
    # Calculate responses and metrics for all examples
    results = {}
    for name, params in examples.items():
        transmission = simulator.simulate_analytical(params)
        metrics = simulator.calculate_metrics(transmission)
        # Calculate objective value
        objective = simulator.objective_function(params)
        metrics['objective'] = objective
        results[name] = {
            'transmission': transmission,
            'metrics': metrics,
            'params': params
        }
    
    # Create figure with subplots
    fig = plt.figure(figsize=(20, 12))
    gs = fig.add_gridspec(3, 3, hspace=0.3, wspace=0.3)
    
    # Wavelength array
    wl_nm = simulator.wavelengths * 1000
    
    # Get ideal response
    ideal = simulator._create_ideal_response()
    
    # Color scheme for different quality levels
    colors = {
        'ideal_like': '#00AA00',  # Dark green
        'good': '#66BB66',        # Light green
        'mediocre': '#FFAA00',     # Orange
        'poor': '#FF6600',         # Dark orange
        'bad': '#FF3333',          # Light red
        'terrible': '#AA0000'      # Dark red
    }
    
    # Define plot order and titles
    plot_configs = [
        ('ideal_like', 'Near-Ideal Design', 0, 0),
        ('good', 'Good Design', 0, 1),
        ('mediocre', 'Mediocre Design', 0, 2),
        ('poor', 'Poor Design', 1, 0),
        ('bad', 'Bad Design', 1, 1),
        ('terrible', 'Terrible Design', 1, 2)
    ]
    
    # Individual response plots
    for name, title, row, col in plot_configs:
        ax = fig.add_subplot(gs[row, col])
        
        # Plot ideal reference
        ax.plot(wl_nm, ideal, 'k--', linewidth=1.5, alpha=0.4, label='Ideal')
        
        # Plot actual response
        ax.plot(wl_nm, results[name]['transmission'], 
                color=colors[name], linewidth=2, label='Actual')
        
        # Add band regions
        ax.axvspan(simulator.s_band[0]*1000, simulator.s_band[1]*1000, 
                  alpha=0.1, color='green', label='S-band' if row==0 and col==0 else '')
        ax.axvspan(simulator.c_band[0]*1000, simulator.c_band[1]*1000, 
                  alpha=0.1, color='red', label='C-band' if row==0 and col==0 else '')
        
        # Add transition band
        ax.axvspan(simulator.transition_band[0]*1000, simulator.transition_band[1]*1000, 
                  alpha=0.1, color='gray')
        
        # Formatting
        ax.set_xlabel('Wavelength (nm)', fontsize=9)
        ax.set_ylabel('Transmission', fontsize=9)
        ax.set_title(f'{title}', fontsize=11, fontweight='bold')
        ax.grid(True, alpha=0.3)
        ax.set_ylim([-0.05, 1.1])
        ax.legend(loc='upper right', fontsize=8)
        
        # Add metrics text box
        metrics = results[name]['metrics']
        metrics_text = (
            f"IL: {metrics['insertion_loss']:.2f} dB\n"
            f"XT: {metrics['crosstalk']:.1f} dB\n"
            f"ER: {metrics['extinction_ratio']:.1f} dB\n"
            f"Roll-off: {metrics['rolloff_rate']:.1f} dB/nm\n"
            f"Ripple: {metrics['passband_ripple']:.2f} dB\n"
            f"Objective: {metrics['objective']:.1f}"
        )
        
        # Color code the metrics box based on quality
        if metrics['objective'] < 10:
            box_color = '#CCFFCC'  # Light green
        elif metrics['objective'] < 50:
            box_color = '#FFFFCC'  # Light yellow
        elif metrics['objective'] < 100:
            box_color = '#FFCCCC'  # Light red
        else:
            box_color = '#FFAAAA'  # Darker red
            
        ax.text(0.02, 0.98, metrics_text, transform=ax.transAxes,
                fontsize=8, verticalalignment='top',
                bbox=dict(boxstyle='round', facecolor=box_color, alpha=0.8))
    
    # Comparison plot - All together (linear scale)
    ax_comp1 = fig.add_subplot(gs[2, 0])
    ax_comp1.plot(wl_nm, ideal, 'k--', linewidth=2, alpha=0.7, label='Ideal')
    for name in ['ideal_like', 'good', 'mediocre']:
        ax_comp1.plot(wl_nm, results[name]['transmission'], 
                     color=colors[name], linewidth=1.5, alpha=0.7, label=name.replace('_', '-').title())
    
    ax_comp1.axvspan(simulator.s_band[0]*1000, simulator.s_band[1]*1000, alpha=0.1, color='green')
    ax_comp1.axvspan(simulator.c_band[0]*1000, simulator.c_band[1]*1000, alpha=0.1, color='red')
    ax_comp1.set_xlabel('Wavelength (nm)')
    ax_comp1.set_ylabel('Transmission')
    ax_comp1.set_title('Good Designs Comparison (Linear)', fontsize=11, fontweight='bold')
    ax_comp1.grid(True, alpha=0.3)
    ax_comp1.legend(loc='upper right', fontsize=8)
    ax_comp1.set_ylim([-0.05, 1.1])
    
    # Comparison plot - All together (dB scale)
    ax_comp2 = fig.add_subplot(gs[2, 1])
    ideal_db = 10 * np.log10(np.maximum(ideal, 1e-10))
    ax_comp2.plot(wl_nm, ideal_db, 'k--', linewidth=2, alpha=0.7, label='Ideal')
    
    for name in examples.keys():
        trans_db = 10 * np.log10(np.maximum(results[name]['transmission'], 1e-10))
        ax_comp2.plot(wl_nm, trans_db, color=colors[name], 
                     linewidth=1.5, alpha=0.7, label=name.replace('_', '-').title())
    
    ax_comp2.axvspan(simulator.s_band[0]*1000, simulator.s_band[1]*1000, alpha=0.1, color='green')
    ax_comp2.axvspan(simulator.c_band[0]*1000, simulator.c_band[1]*1000, alpha=0.1, color='red')
    ax_comp2.axhline(y=-0.45, color='g', linestyle=':', alpha=0.5, label='IL target')
    ax_comp2.axhline(y=-20.7, color='r', linestyle=':', alpha=0.5, label='XT target')
    ax_comp2.set_xlabel('Wavelength (nm)')
    ax_comp2.set_ylabel('Transmission (dB)')
    ax_comp2.set_title('All Designs Comparison (dB Scale)', fontsize=11, fontweight='bold')
    ax_comp2.grid(True, alpha=0.3)
    ax_comp2.legend(loc='lower right', fontsize=7, ncol=2)
    ax_comp2.set_ylim([-60, 5])
    
    # Metrics comparison bar chart
    ax_bar = fig.add_subplot(gs[2, 2])
    
    # Prepare data for bar chart
    designs = list(examples.keys())
    design_labels = [d.replace('_', '-').title() for d in designs]
    objectives = [results[d]['metrics']['objective'] for d in designs]
    
    # Create bars with color coding
    bars = ax_bar.bar(range(len(designs)), objectives, color=[colors[d] for d in designs])
    
    # Add value labels on bars
    for bar, obj in zip(bars, objectives):
        height = bar.get_height()
        ax_bar.text(bar.get_x() + bar.get_width()/2., height,
                   f'{obj:.1f}', ha='center', va='bottom', fontsize=8)
    
    ax_bar.set_xticks(range(len(designs)))
    ax_bar.set_xticklabels(design_labels, rotation=45, ha='right', fontsize=8)
    ax_bar.set_ylabel('Objective Value (lower is better)')
    ax_bar.set_title('Objective Function Comparison', fontsize=11, fontweight='bold')
    ax_bar.grid(True, alpha=0.3, axis='y')
    ax_bar.set_yscale('log')
    
    # Add horizontal lines for quality thresholds
    ax_bar.axhline(y=10, color='green', linestyle='--', alpha=0.5, label='Excellent (<10)')
    ax_bar.axhline(y=50, color='orange', linestyle='--', alpha=0.5, label='Acceptable (<50)')
    ax_bar.axhline(y=100, color='red', linestyle='--', alpha=0.5, label='Poor (>100)')
    ax_bar.legend(loc='upper left', fontsize=8)
    
    # Overall title
    fig.suptitle('MZI Filter Quality Analysis: Understanding Good vs Bad Designs', 
                fontsize=14, fontweight='bold', y=0.98)
    
    # Add description text
    description = (
        "Key Performance Indicators:\n"
        "• Insertion Loss (IL): Signal loss in passband - lower is better (target < 0.45 dB)\n"
        "• Crosstalk (XT): Unwanted signal in stopband - more negative is better (target < -20.7 dB)\n"
        "• Extinction Ratio (ER): Passband/stopband ratio - higher is better (target > 35 dB)\n"
        "• Roll-off Rate: Transition sharpness - higher is better (target > 0.5 dB/nm)\n"
        "• Passband Ripple: Flatness in passband - lower is better"
    )
    
    fig.text(0.02, 0.02, description, fontsize=9, 
            bbox=dict(boxstyle='round', facecolor='white', alpha=0.9))
    
    return fig, results


def create_metric_breakdown_figure(examples, simulator):
    """Create detailed metric breakdown visualization."""
    
    # Calculate metrics for all examples
    results = {}
    for name, params in examples.items():
        transmission = simulator.simulate_analytical(params)
        metrics = simulator.calculate_metrics(transmission)
        # Calculate objective value
        objective = simulator.objective_function(params)
        metrics['objective'] = objective
        results[name] = metrics
    
    # Create figure
    fig, axes = plt.subplots(2, 3, figsize=(18, 10))
    fig.suptitle('Detailed Metric Breakdown: What Makes a Filter Good or Bad', 
                fontsize=14, fontweight='bold')
    
    designs = list(examples.keys())
    design_labels = [d.replace('_', '-').title() for d in designs]
    x_pos = np.arange(len(designs))
    
    # Color scheme
    colors_list = ['#00AA00', '#66BB66', '#FFAA00', '#FF6600', '#FF3333', '#AA0000']
    
    # 1. Insertion Loss
    ax = axes[0, 0]
    il_values = [results[d]['insertion_loss'] for d in designs]
    bars = ax.bar(x_pos, il_values, color=colors_list)
    ax.axhline(y=0.45, color='red', linestyle='--', label='Target < 0.45 dB')
    ax.set_title('Insertion Loss (Lower is Better)', fontweight='bold')
    ax.set_ylabel('IL (dB)')
    ax.set_xticks(x_pos)
    ax.set_xticklabels(design_labels, rotation=45, ha='right')
    ax.legend()
    ax.grid(True, alpha=0.3, axis='y')
    
    # Add value labels
    for bar, val in zip(bars, il_values):
        ax.text(bar.get_x() + bar.get_width()/2., bar.get_height() + 0.05,
               f'{val:.2f}', ha='center', va='bottom', fontsize=9)
    
    # 2. Crosstalk
    ax = axes[0, 1]
    xt_values = [results[d]['crosstalk'] for d in designs]
    bars = ax.bar(x_pos, xt_values, color=colors_list)
    ax.axhline(y=-20.7, color='red', linestyle='--', label='Target < -20.7 dB')
    ax.set_title('Crosstalk (More Negative is Better)', fontweight='bold')
    ax.set_ylabel('Crosstalk (dB)')
    ax.set_xticks(x_pos)
    ax.set_xticklabels(design_labels, rotation=45, ha='right')
    ax.legend()
    ax.grid(True, alpha=0.3, axis='y')
    
    # 3. Extinction Ratio
    ax = axes[0, 2]
    er_values = [results[d]['extinction_ratio'] for d in designs]
    bars = ax.bar(x_pos, er_values, color=colors_list)
    ax.axhline(y=35, color='red', linestyle='--', label='Target > 35 dB')
    ax.set_title('Extinction Ratio (Higher is Better)', fontweight='bold')
    ax.set_ylabel('ER (dB)')
    ax.set_xticks(x_pos)
    ax.set_xticklabels(design_labels, rotation=45, ha='right')
    ax.legend()
    ax.grid(True, alpha=0.3, axis='y')
    
    # 4. Roll-off Rate
    ax = axes[1, 0]
    ro_values = [results[d]['rolloff_rate'] for d in designs]
    bars = ax.bar(x_pos, ro_values, color=colors_list)
    ax.axhline(y=0.5, color='red', linestyle='--', label='Target > 0.5 dB/nm')
    ax.set_title('Roll-off Rate (Higher is Better)', fontweight='bold')
    ax.set_ylabel('Roll-off (dB/nm)')
    ax.set_xticks(x_pos)
    ax.set_xticklabels(design_labels, rotation=45, ha='right')
    ax.legend()
    ax.grid(True, alpha=0.3, axis='y')
    
    # 5. Passband Ripple
    ax = axes[1, 1]
    ripple_values = [results[d]['passband_ripple'] for d in designs]
    bars = ax.bar(x_pos, ripple_values, color=colors_list)
    ax.axhline(y=0.1, color='red', linestyle='--', label='Good < 0.1 dB')
    ax.set_title('Passband Ripple (Lower is Better)', fontweight='bold')
    ax.set_ylabel('Ripple (dB)')
    ax.set_xticks(x_pos)
    ax.set_xticklabels(design_labels, rotation=45, ha='right')
    ax.legend()
    ax.grid(True, alpha=0.3, axis='y')
    
    # 6. Overall Objective
    ax = axes[1, 2]
    obj_values = [results[d]['objective'] for d in designs]
    bars = ax.bar(x_pos, obj_values, color=colors_list)
    ax.set_title('Overall Objective (Lower is Better)', fontweight='bold')
    ax.set_ylabel('Objective Value')
    ax.set_xticks(x_pos)
    ax.set_xticklabels(design_labels, rotation=45, ha='right')
    ax.set_yscale('log')
    ax.grid(True, alpha=0.3, axis='y')
    
    # Add value labels
    for bar, val in zip(bars, obj_values):
        ax.text(bar.get_x() + bar.get_width()/2., bar.get_height() * 1.1,
               f'{val:.1f}', ha='center', va='bottom', fontsize=9)
    
    # Add quality zones
    ax.axhspan(0, 10, alpha=0.2, color='green', label='Excellent')
    ax.axhspan(10, 50, alpha=0.2, color='yellow', label='Good')
    ax.axhspan(50, 100, alpha=0.2, color='orange', label='Acceptable')
    ax.axhspan(100, 1000, alpha=0.2, color='red', label='Poor')
    ax.legend(loc='upper left')
    
    plt.tight_layout()
    
    return fig, results


def main():
    """Main function to generate all analysis figures."""
    
    print("="*70)
    print("MZI Filter Quality Analysis")
    print("="*70)
    print("Generating example filter designs...")
    
    # Create examples
    examples, simulator = create_filter_examples()
    
    # Create output directory
    output_dir = Path(__file__).parent.parent / "results" / "quality_analysis"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Generate comparison figure
    print("\nGenerating main comparison figure...")
    fig1, results1 = plot_comparison_figure(examples, simulator)
    fig1.savefig(output_dir / "filter_quality_comparison.png", dpi=150, bbox_inches='tight')
    plt.close(fig1)
    print(f"  Saved: filter_quality_comparison.png")
    
    # Generate metric breakdown figure
    print("\nGenerating metric breakdown figure...")
    fig2, results2 = create_metric_breakdown_figure(examples, simulator)
    fig2.savefig(output_dir / "metric_breakdown.png", dpi=150, bbox_inches='tight')
    plt.close(fig2)
    print(f"  Saved: metric_breakdown.png")
    
    # Save metrics summary
    print("\nSaving metrics summary...")
    metrics_summary = {}
    for name in examples.keys():
        metrics_summary[name] = results2[name]
    
    with open(output_dir / "metrics_summary.json", 'w') as f:
        json.dump(metrics_summary, f, indent=2)
    print(f"  Saved: metrics_summary.json")
    
    # Print summary table
    print("\n" + "="*70)
    print("QUALITY SUMMARY TABLE")
    print("="*70)
    print(f"{'Design':<15} {'IL (dB)':<10} {'XT (dB)':<10} {'ER (dB)':<10} {'Objective':<10} {'Quality':<10}")
    print("-"*70)
    
    quality_ratings = {
        'ideal_like': 'EXCELLENT',
        'good': 'GOOD',
        'mediocre': 'MEDIOCRE',
        'poor': 'POOR',
        'bad': 'BAD',
        'terrible': 'TERRIBLE'
    }
    
    for name in examples.keys():
        m = results2[name]
        print(f"{name.replace('_','-').title():<15} "
              f"{m['insertion_loss']:<10.2f} "
              f"{m['crosstalk']:<10.1f} "
              f"{m['extinction_ratio']:<10.1f} "
              f"{m['objective']:<10.1f} "
              f"{quality_ratings[name]:<10}")
    
    print("\n" + "="*70)
    print("Analysis complete! Check the results/quality_analysis folder for figures.")
    print("="*70)
    
    # Explanation of what makes filters good or bad
    print("\nKEY INSIGHTS:")
    print("-"*50)
    print("GOOD FILTERS have:")
    print("  • Low insertion loss (< 0.5 dB) in passbands")
    print("  • High extinction (> -20 dB) in stopbands")
    print("  • Sharp roll-off (> 0.5 dB/nm) at transitions")
    print("  • Flat passband response (ripple < 0.1 dB)")
    print("  • Optimized coupling ratios (varied, not uniform)")
    print("  • Correct path length difference (delta_L ~ 16.5 um)")
    
    print("\nBAD FILTERS have:")
    print("  • High insertion loss (> 1 dB) in passbands")
    print("  • Poor extinction (> -15 dB) in stopbands")
    print("  • Slow roll-off (< 0.3 dB/nm) at transitions")
    print("  • Rippled passband response (> 0.5 dB)")
    print("  • Poor coupling ratios (too uniform or random)")
    print("  • Wrong path length difference")
    
    print("\nThe OBJECTIVE FUNCTION combines all metrics:")
    print("  Objective = w1*IL + w2*|XT| + w3*(1/ER) + w4*(1/roll-off) + w5*ripple")
    print("  where weights are tuned to prioritize critical specs")
    print("-"*50)


if __name__ == "__main__":
    main()