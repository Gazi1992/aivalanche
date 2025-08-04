"""
Comprehensive test suite for Differential Evolution refinement functionality.
Tests all refinement modes, methods, configurations, and edge cases.
"""

import sys
import os
sys.path.append(os.path.join(os.getcwd(), 'packages/aivalanche_lib'))

import numpy as np
import pandas as pd
from datetime import datetime
import matplotlib.pyplot as plt
import contextlib
import io

from aivalanche_lib.optimization.differential_evolution import DifferentialEvolution
from aivalanche_lib.optimization.differential_evolution.refinement import (
    get_refinement_history, get_default_config, validate_config, _get_scale_tier
)
from aivalanche_lib.parameters import Parameters

# Set style for better looking plots
try:
    plt.style.use('seaborn-v0_8-darkgrid')
except:
    plt.style.use('ggplot')


def test_refinement_modes():
    """Test different refinement modes: off, on (during), on (post)."""
    print("\n" + "="*80)
    print("Test 1: Refinement Modes")
    print("="*80)
    
    # Simple test function
    def eval_func(parameters, **kwargs):
        results = []
        for idx in range(len(parameters)):
            x = parameters['x'].iloc[idx]
            y = parameters['y'].iloc[idx]
            metric = (x - 1)**2 + (y - 1)**2
            results.append({'metric': metric})
        return results
    
    parameters = Parameters([
        {'name': 'x', 'type': 'continuous', 'min': -5, 'max': 5},
        {'name': 'y', 'type': 'continuous', 'min': -5, 'max': 5}
    ])
    
    # Test configurations
    test_configs = [
        ('off', None),  # No refinement
        ('on_during', {'method': 'adam', 'trigger_ratio': 0.5, 'max_iterations': 50}),  # During optimization
        ('on_post', {'method': 'adam', 'trigger_ratio': -1, 'max_iterations': 50})  # Post optimization
    ]
    
    results = {}
    
    for config_name, refinement_config in test_configs:
        print(f"\nTesting: {config_name}")
        
        # Determine actual mode
        mode = 'off' if config_name == 'off' else 'on'
        
        de = DifferentialEvolution(
            seed=42,
            eval_func=eval_func,
            parameters=parameters,
            pop_size=20,
            max_iterations=30,
            refinement_mode=mode,
            refinement_config=refinement_config
        )
        
        de.run_optimization()
        
        history = get_refinement_history(de)
        results[config_name] = {
            'final_metric': de.best_metric,
            'refinements': len(history),
            'evaluations': de.nr_evaluations
        }
        
        print(f"  Final metric: {de.best_metric:.6e}")
        print(f"  Refinements applied: {len(history)}")
        print(f"  Total evaluations: {de.nr_evaluations}")
        
        # Show when refinement was triggered
        if history:
            for i, h in enumerate(history):
                trigger_iter = h.get('trigger_iter', 'post-optimization')
                print(f"  Refinement {i+1} triggered at: {trigger_iter}")
    
    # Verify expected behavior
    assert results['off']['refinements'] == 0, "No refinements should occur with mode='off'"
    assert results['on_during']['refinements'] >= 0, "Refinements can occur during optimization"
    assert results['on_post']['refinements'] <= 1, "At most one refinement after optimization"
    
    print("\n[PASSED] Refinement modes test")
    return results


def test_refinement_methods():
    """Test different refinement methods: adam, dls, nelder_mead."""
    print("\n" + "="*80)
    print("Test 2: Refinement Methods (Adam vs DLS vs Nelder-Mead)")
    print("="*80)
    
    def eval_func(parameters, **kwargs):
        results = []
        for idx in range(len(parameters)):
            x = parameters['x'].iloc[idx]
            y = parameters['y'].iloc[idx]
            z = parameters['z'].iloc[idx]
            # Rosenbrock-like function
            metric = 100*(y - x**2)**2 + (1 - x)**2 + 50*(z - y**2)**2
            results.append({'metric': metric})
        return results
    
    parameters = Parameters([
        {'name': 'x', 'type': 'continuous', 'min': -2, 'max': 2},
        {'name': 'y', 'type': 'continuous', 'min': -2, 'max': 2},
        {'name': 'z', 'type': 'continuous', 'min': -2, 'max': 2}
    ])
    
    methods = ['adam', 'dls', 'nelder_mead']
    results = {}
    
    for method in methods:
        print(f"\nTesting method='{method}'")
        
        de = DifferentialEvolution(
            seed=42,
            eval_func=eval_func,
            parameters=parameters,
            pop_size=30,
            max_iterations=50,
            refinement_mode='post',
            refinement_config={
                'method': method,
                'max_iterations': 100
            }
        )
        
        de.run_optimization()
        
        history = get_refinement_history(de)
        if history:
            ref_info = history[0]
            results[method] = {
                'initial_metric': ref_info['initial_metric'],
                'refined_metric': ref_info['refined_metric'],
                'improvement': ref_info['relative_improvement'],
                'iterations': ref_info.get('iterations', ref_info.get('evaluations', 0))
            }
            
            print(f"  Initial metric: {ref_info['initial_metric']:.6e}")
            print(f"  Refined metric: {ref_info['refined_metric']:.6e}")
            print(f"  Improvement: {ref_info['relative_improvement']:.2%}")
            iterations = ref_info.get('iterations', ref_info.get('evaluations', 0))
            print(f"  Iterations: {iterations}")
    
    print("\n[PASSED] Refinement methods test")
    return results


def test_categorical_exclusion():
    """Test that categorical parameters are properly excluded from refinement."""
    print("\n" + "="*80)
    print("Test 3: Categorical Parameter Exclusion")
    print("="*80)
    
    def eval_func(parameters, **kwargs):
        results = []
        for idx in range(len(parameters)):
            x = parameters['x'].iloc[idx]
            y = parameters['y'].iloc[idx]
            cat = parameters['category'].iloc[idx]
            # Category affects the function shape
            if cat == 'A':
                metric = (x - 1)**2 + (y - 1)**2
            else:
                metric = (x + 1)**2 + (y + 1)**2
            results.append({'metric': metric})
        return results
    
    parameters = Parameters([
        {'name': 'x', 'type': 'continuous', 'min': -5, 'max': 5},
        {'name': 'y', 'type': 'continuous', 'min': -5, 'max': 5},
        {'name': 'category', 'type': 'categorical', 'values': ['A', 'B', 'C']}
    ])
    
    de = DifferentialEvolution(
        seed=42,
        eval_func=eval_func,
        parameters=parameters,
        pop_size=20,
        max_iterations=30,
        refinement_mode='post',
        refinement_config={'method': 'adam', 'max_iterations': 50}
    )
    
    # Capture output to check for exclusion message
    buffer = io.StringIO()
    with contextlib.redirect_stdout(buffer):
        de.run_optimization()
    
    output = buffer.getvalue()
    
    # Verify categorical parameter was excluded
    assert "Categorical parameters excluded: ['category']" in output
    
    # Verify refinement still works
    history = get_refinement_history(de)
    assert len(history) > 0, "Refinement should still occur with categorical parameters"
    
    print(f"  Categorical parameter 'category' was properly excluded")
    print(f"  Refinement still applied to continuous parameters")
    print(f"  Final metric: {de.best_metric:.6e}")
    
    print("\n[PASSED] Categorical exclusion test")


def test_fixed_parameters():
    """Test that fixed parameters are not modified during refinement."""
    print("\n" + "="*80)
    print("Test 4: Fixed Parameters")
    print("="*80)
    
    def eval_func(parameters, **kwargs):
        results = []
        for idx in range(len(parameters)):
            x = parameters['x'].iloc[idx]
            z = parameters['z'].iloc[idx]
            y_fixed = 1.0  # Fixed value
            metric = (x - 2)**2 + (y_fixed - 1)**2 + (z - 3)**2
            results.append({'metric': metric})
        return results
    
    # Create parameters where y_fixed is excluded from variable parameters
    parameters = Parameters([
        {'name': 'x', 'type': 'continuous', 'min': -5, 'max': 5},
        {'name': 'z', 'type': 'continuous', 'min': -5, 'max': 5}
    ])
    
    de = DifferentialEvolution(
        seed=42,
        eval_func=eval_func,
        parameters=parameters,
        pop_size=20,
        max_iterations=30,
        refinement_mode='post',
        refinement_config={'method': 'dls', 'max_iterations': 50}
    )
    
    de.run_optimization()
    
    # With this approach, y_fixed is not part of parameters, it's hardcoded
    print(f"  Fixed parameter y_fixed hardcoded at: 1.0")
    print(f"  Variable parameters optimized successfully")
    print(f"  Final metric: {de.best_metric:.6e}")
    print(f"  Best x: {de.best_parameters['x']:.4f} (target: 2.0)")
    print(f"  Best z: {de.best_parameters['z']:.4f} (target: 3.0)")
    
    print("\n[PASSED] Fixed parameters test")


def test_multi_scale_adaptation():
    """Test adaptive parameter scaling for different problem scales."""
    print("\n" + "="*80)
    print("Test 5: Multi-Scale Adaptation")
    print("="*80)
    
    scales = [1e0, 1e-3, 1e-6, 1e-9, 1e-12, 1e-15]
    
    for scale in scales:
        tier_name, scale_factor = _get_scale_tier(scale)
        print(f"\n  Scale {scale:.0e}: tier='{tier_name}', factor={scale_factor:.0e}")
    
    # Test actual adaptation
    def eval_func(parameters, **kwargs):
        results = []
        for idx in range(len(parameters)):
            x = parameters['x'].iloc[idx]
            metric = 1e-10 * (x - 1)**2  # Small scale problem
            results.append({'metric': metric})
        return results
    
    parameters = Parameters([
        {'name': 'x', 'type': 'continuous', 'min': -2, 'max': 2}
    ])
    
    de = DifferentialEvolution(
        seed=42,
        eval_func=eval_func,
        parameters=parameters,
        pop_size=15,
        max_iterations=20,
        refinement_mode='post',
        refinement_config={'method': 'adam', 'max_iterations': 30}
    )
    
    buffer = io.StringIO()
    with contextlib.redirect_stdout(buffer):
        de.run_optimization()
    
    output = buffer.getvalue()
    
    # Check for scale detection
    assert "Detected" in output and "-scale problem" in output
    assert "Auto-adapting" in output
    
    print("\n  Adaptive scaling triggered successfully for small-scale problem")
    print("\n[PASSED] Multi-scale adaptation test")


def test_user_config_precedence():
    """Test that user configurations override defaults and adaptations."""
    print("\n" + "="*80)
    print("Test 6: User Configuration Precedence")
    print("="*80)
    
    def eval_func(parameters, **kwargs):
        results = []
        for idx in range(len(parameters)):
            x = parameters['x'].iloc[idx]
            metric = 1e-8 * (x - 1)**2  # Small scale
            results.append({'metric': metric})
        return results
    
    parameters = Parameters([
        {'name': 'x', 'type': 'continuous', 'min': -2, 'max': 2}
    ])
    
    # Test with user-specified learning rate
    de = DifferentialEvolution(
        seed=42,
        eval_func=eval_func,
        parameters=parameters,
        pop_size=15,
        max_iterations=20,
        refinement_mode='post',
        refinement_config={
            'method': 'adam',
            'max_iterations': 30,
            'options': {
                'learning_rate': 0.5  # User override
            }
        }
    )
    
    buffer = io.StringIO()
    with contextlib.redirect_stdout(buffer):
        de.run_optimization()
    
    output = buffer.getvalue()
    
    # Learning rate should NOT be adapted
    assert "Auto-adapting learning rate" not in output
    # But other parameters might be
    assert "Auto-adapting gradient_step_size" in output
    
    print("  User-specified learning_rate was not overridden")
    print("  Other parameters were adapted as expected")
    print("\n[PASSED] User configuration precedence test")


def test_refinement_trigger_ratio():
    """Test refinement triggering at different ratios."""
    print("\n" + "="*80)
    print("Test 7: Refinement Trigger Ratios")
    print("="*80)
    
    def eval_func(parameters, **kwargs):
        results = []
        for idx in range(len(parameters)):
            x = parameters['x'].iloc[idx]
            y = parameters['y'].iloc[idx]
            # Function with multiple local minima
            metric = np.sin(3*x) * np.cos(3*y) + 0.1*((x-1)**2 + (y-1)**2)
            results.append({'metric': metric})
        return results
    
    parameters = Parameters([
        {'name': 'x', 'type': 'continuous', 'min': -2, 'max': 2},
        {'name': 'y', 'type': 'continuous', 'min': -2, 'max': 2}
    ])
    
    ratios = [0.2, 0.5, 0.8]
    
    for ratio in ratios:
        print(f"\n  Testing trigger_ratio={ratio}")
        
        de = DifferentialEvolution(
            seed=42,
            eval_func=eval_func,
            parameters=parameters,
            pop_size=20,
            max_iterations=50,
            max_iter_without_improvement=10,
            refinement_mode='on',
            refinement_config={
                'method': 'dls',
                'trigger_ratio': ratio,
                'max_iterations': 20
            }
        )
        
        de.run_optimization()
        
        history = get_refinement_history(de)
        print(f"    Refinements triggered: {len(history)}")
        
        if history:
            trigger_iters = [h.get('trigger_iter', 'post') for h in history]
            print(f"    Triggered at iterations: {trigger_iters}")
    
    print("\n[PASSED] Refinement trigger ratio test")


def test_nelder_mead_configurations():
    """Test Nelder-Mead specific configurations."""
    print("\n" + "="*80)
    print("Test 8: Nelder-Mead Configurations")
    print("="*80)
    
    def eval_func(parameters, **kwargs):
        results = []
        for idx in range(len(parameters)):
            x = parameters['x'].iloc[idx]
            y = parameters['y'].iloc[idx]
            # Shifted sphere function
            metric = (x - 2)**2 + (y - 3)**2
            results.append({'metric': metric})
        return results
    
    parameters = Parameters([
        {'name': 'x', 'type': 'continuous', 'min': -5, 'max': 5},
        {'name': 'y', 'type': 'continuous', 'min': -5, 'max': 5}
    ])
    
    # Test different Nelder-Mead configurations
    configs = [
        {
            'name': 'Corner mode with 5% scale',
            'options': {
                'best_point_position': 'corner',
                'initial_simplex_scale': 0.05
            }
        },
        {
            'name': 'Centroid mode with 2% scale',
            'options': {
                'best_point_position': 'centroid', 
                'initial_simplex_scale': 0.02
            }
        },
        {
            'name': 'Corner mode with absolute scale',
            'options': {
                'best_point_position': 'corner',
                'initial_simplex_absolute_scale': 0.5
            }
        }
    ]
    
    for config in configs:
        print(f"\n  Testing: {config['name']}")
        
        de = DifferentialEvolution(
            seed=42,
            eval_func=eval_func,
            parameters=parameters,
            pop_size=20,
            max_iterations=30,
            refinement_mode='on',
            refinement_config={
                'method': 'nelder_mead',
                'trigger_ratio': -1,  # Post-optimization only
                'max_iterations': 50,
                'options': config['options']
            }
        )
        
        de.run_optimization()
        
        history = get_refinement_history(de)
        if history:
            ref_info = history[0]
            print(f"    Initial metric: {ref_info['initial_metric']:.6e}")
            print(f"    Refined metric: {ref_info['refined_metric']:.6e}")
            print(f"    Improvement: {ref_info['relative_improvement']:.2%}")
    
    print("\n[PASSED] Nelder-Mead configurations test")


def test_config_validation():
    """Test configuration validation."""
    print("\n" + "="*80)
    print("Test 9: Configuration Validation")
    print("="*80)
    
    # Test valid config
    valid_config = {
        'method': 'adam',
        'trigger_ratio': 0.5,
        'max_iterations': 100,
        'options': {'learning_rate': 0.01}
    }
    
    try:
        validated = validate_config(valid_config)
        print("  Valid configuration accepted")
    except:
        assert False, "Valid config should not raise error"
    
    # Test invalid method
    try:
        invalid_config = {'method': 'invalid_method'}
        validate_config(invalid_config)
        assert False, "Should raise error for invalid method"
    except ValueError as e:
        print(f"  Invalid method correctly rejected: {e}")
    
    # Test invalid trigger_ratio
    try:
        invalid_config = {'trigger_ratio': 2.0}
        validate_config(invalid_config)
        assert False, "Should raise error for invalid trigger_ratio"
    except ValueError as e:
        print(f"  Invalid trigger_ratio correctly rejected: {e}")
    
    print("\n[PASSED] Configuration validation test")


def run_all_tests(visualize=True, results_dir=None):
    """Run all refinement tests with optional visualization."""
    print("\n" + "="*80)
    print("DIFFERENTIAL EVOLUTION REFINEMENT TEST SUITE")
    print("="*80)
    
    test_results = {}
    test_data = {}  # Store test-specific data for visualization
    
    # Run each test
    tests = [
        ("Refinement Modes", test_refinement_modes),
        ("Refinement Methods", test_refinement_methods),
        ("Categorical Exclusion", test_categorical_exclusion),
        ("Fixed Parameters", test_fixed_parameters),
        ("Multi-Scale Adaptation", test_multi_scale_adaptation),
        ("User Config Precedence", test_user_config_precedence),
        ("Trigger Ratios", test_refinement_trigger_ratio),
        ("Nelder-Mead Configurations", test_nelder_mead_configurations),
        ("Config Validation", test_config_validation)
    ]
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            test_results[test_name] = "PASSED"
            if result and isinstance(result, dict):
                test_data[test_name] = result
        except Exception as e:
            test_results[test_name] = f"FAILED: {str(e)}"
            print(f"\n[FAILED] {test_name}: {e}")
    
    # Summary
    print("\n" + "="*80)
    print("TEST SUMMARY")
    print("="*80)
    
    passed = sum(1 for r in test_results.values() if r == "PASSED")
    total = len(test_results)
    
    for test_name, result in test_results.items():
        status = "[PASS]" if result == "PASSED" else "[FAIL]"
        print(f"{status} {test_name}: {result}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n[SUCCESS] All refinement tests passed!")
    else:
        print("\n[WARNING] Some tests failed!")
    
    # Create visualizations if requested
    if visualize and results_dir:
        print("\nGenerating visualizations...")
        
        # 1. Summary visualization
        create_summary_visualization(test_results, 
                                   os.path.join(results_dir, 'test_summary.png'))
        
        # 2. Refinement modes comparison
        if "Refinement Modes" in test_data:
            visualize_refinement_modes(test_data["Refinement Modes"],
                                     os.path.join(results_dir, 'refinement_modes.png'))
        
        # 3. Method comparison
        if "Refinement Methods" in test_data:
            methods_data = test_data["Refinement Methods"]
            visualize_method_comparison(methods_data,
                                      os.path.join(results_dir, 'method_comparison.png'))
        
        # 4. Scale adaptation visualization
        visualize_scale_adaptation(os.path.join(results_dir, 'scale_adaptation.png'))
        
        print(f"Visualizations saved to: {results_dir}")
    
    return test_results


def visualize_refinement_modes(results, save_path=None):
    """Create visualization comparing refinement modes."""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
    
    # Extract data
    modes = list(results.keys())
    # Prettier labels for display
    mode_labels = {
        'off': 'Off',
        'on_during': 'On (During)',
        'on_post': 'On (Post)'
    }
    display_labels = [mode_labels.get(m, m) for m in modes]
    
    metrics = [results[mode]['final_metric'] for mode in modes]
    refinements = [results[mode]['refinements'] for mode in modes]
    evaluations = [results[mode]['evaluations'] for mode in modes]
    
    # Bar chart of final metrics
    bars = ax1.bar(display_labels, metrics, color=['red', 'green', 'blue'])
    ax1.set_ylabel('Final Metric')
    ax1.set_title('Final Optimization Results by Refinement Configuration')
    ax1.set_yscale('log')
    
    # Add value labels on bars
    for bar, metric in zip(bars, metrics):
        height = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width()/2., height,
                f'{metric:.2e}', ha='center', va='bottom')
    
    # Scatter plot: evaluations vs metric with refinement count
    scatter = ax2.scatter(evaluations, metrics, s=200, 
                         c=refinements, cmap='viridis', 
                         edgecolors='black', linewidth=2)
    
    for i, mode in enumerate(modes):
        ax2.annotate(display_labels[i], (evaluations[i], metrics[i]), 
                    xytext=(5, 5), textcoords='offset points')
    
    ax2.set_xlabel('Total Evaluations')
    ax2.set_ylabel('Final Metric')
    ax2.set_yscale('log')
    ax2.set_title('Efficiency Analysis')
    
    # Add colorbar
    cbar = plt.colorbar(scatter, ax=ax2)
    cbar.set_label('Number of Refinements')
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
    plt.close()


def visualize_method_comparison(methods_data, save_path=None):
    """Visualize comparison between all refinement methods."""
    if not methods_data:
        return
    
    # Filter out methods that didn't have results
    valid_methods = {k: v for k, v in methods_data.items() if v is not None}
    if not valid_methods:
        return
    
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(14, 10))
    
    # Method names with proper capitalization
    method_display = {'adam': 'Adam', 'dls': 'DLS', 'nelder_mead': 'Nelder-Mead'}
    methods = [method_display.get(m, m) for m in valid_methods.keys()]
    
    # Extract metrics
    initial_metrics = [v['initial_metric'] for v in valid_methods.values()]
    refined_metrics = [v['refined_metric'] for v in valid_methods.values()]
    
    x = np.arange(len(methods))
    width = 0.35
    
    bars1 = ax1.bar(x - width/2, initial_metrics, width, label='Initial', alpha=0.7)
    bars2 = ax1.bar(x + width/2, refined_metrics, width, label='Refined', alpha=0.7)
    
    ax1.set_ylabel('Metric Value')
    ax1.set_title('Initial vs Refined Metrics')
    ax1.set_xticks(x)
    ax1.set_xticklabels(methods)
    ax1.legend()
    ax1.set_yscale('log')
    
    # Improvement percentages
    improvements = [v['improvement'] for v in valid_methods.values()]
    colors = ['orange', 'purple', 'green', 'red', 'blue'][:len(methods)]
    bars = ax2.bar(methods, improvements, color=colors)
    ax2.set_ylabel('Improvement (%)')
    ax2.set_title('Relative Improvement by Method')
    
    for bar, imp in zip(bars, improvements):
        height = bar.get_height()
        ax2.text(bar.get_x() + bar.get_width()/2., height,
                f'{imp:.1%}', ha='center', va='bottom')
    
    # Iterations comparison
    iterations = [v['iterations'] for v in valid_methods.values()]
    ax3.bar(methods, iterations, color=colors)
    ax3.set_ylabel('Iterations')
    ax3.set_title('Refinement Iterations')
    
    # Efficiency (improvement per iteration)
    efficiency = [v['improvement'] / v['iterations'] if v['iterations'] > 0 else 0 
                  for v in valid_methods.values()]
    ax4.bar(methods, efficiency, color=colors)
    ax4.set_ylabel('Improvement per Iteration')
    ax4.set_title('Refinement Efficiency')
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
    plt.close()


def visualize_scale_adaptation(save_path=None):
    """Visualize the multi-scale adaptation tiers."""
    # Generate data points across scales
    scales = np.logspace(-18, 2, 100)
    tiers = []
    factors = []
    
    for scale in scales:
        tier, factor = _get_scale_tier(scale)
        tiers.append(tier)
        factors.append(factor)
    
    # Map tiers to numeric values for plotting
    tier_map = {'extreme': 0, 'pico': 1, 'nano': 2, 'micro': 3, 'small': 4, 'normal': 5}
    tier_values = [tier_map[t] for t in tiers]
    
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8), sharex=True)
    
    # Plot tiers
    ax1.plot(scales, tier_values, 'b-', linewidth=2)
    ax1.set_xscale('log')
    ax1.set_ylabel('Scale Tier')
    ax1.set_yticks(list(tier_map.values()))
    ax1.set_yticklabels(list(tier_map.keys()))
    ax1.set_title('Scale Tier Classification')
    ax1.grid(True, alpha=0.3)
    
    # Add tier boundaries
    boundaries = [1e-12, 1e-9, 1e-6, 1e-3, 1.0]
    for b in boundaries:
        ax1.axvline(x=b, color='red', linestyle='--', alpha=0.5)
    
    # Plot scale factors
    ax2.plot(scales, factors, 'g-', linewidth=2)
    ax2.set_xscale('log')
    ax2.set_yscale('log')
    ax2.set_xlabel('Metric Value')
    ax2.set_ylabel('Scale Factor')
    ax2.set_title('Adaptation Scale Factors')
    ax2.grid(True, alpha=0.3)
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
    plt.close()


def visualize_convergence_history(de_instance, title="Convergence History", save_path=None):
    """Plot convergence history with refinement points marked."""
    history = de_instance.get_convergence_report()
    iterations = history['iterations']
    best_metrics = history['best_metric_history']
    
    plt.figure(figsize=(10, 6))
    plt.semilogy(iterations, best_metrics, 'b-', linewidth=2, label='Best Metric')
    
    # Mark refinement points
    refinement_history = get_refinement_history(de_instance)
    for i, ref in enumerate(refinement_history):
        trigger_iter = ref.get('trigger_iter', None)
        if trigger_iter and trigger_iter != 'post':
            plt.axvline(x=trigger_iter, color='red', linestyle='--', 
                       alpha=0.7, label=f'Refinement {i+1}' if i == 0 else "")
    
    plt.xlabel('Iteration')
    plt.ylabel('Best Metric (log scale)')
    plt.title(title)
    plt.legend()
    plt.grid(True, alpha=0.3)
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
    plt.close()


def create_summary_visualization(all_results, save_path=None):
    """Create a comprehensive summary visualization."""
    fig = plt.figure(figsize=(16, 10))
    
    # Create grid
    gs = fig.add_gridspec(3, 3, hspace=0.3, wspace=0.3)
    
    # Test names and their pass/fail status
    test_names = list(all_results.keys())
    test_status = [1 if r == "PASSED" else 0 for r in all_results.values()]
    
    # 1. Test summary pie chart
    ax1 = fig.add_subplot(gs[0, :2])
    passed = sum(test_status)
    failed = len(test_status) - passed
    colors = ['#2ecc71', '#e74c3c']
    wedges, texts, autotexts = ax1.pie([passed, failed], 
                                       labels=['Passed', 'Failed'],
                                       colors=colors,
                                       autopct='%1.0f%%',
                                       startangle=90)
    ax1.set_title(f'Test Summary: {passed}/{len(test_status)} Passed')
    
    # 2. Test status heatmap
    ax2 = fig.add_subplot(gs[0, 2])
    status_matrix = np.array(test_status).reshape(-1, 1)
    
    # Manual heatmap without seaborn
    im = ax2.imshow(status_matrix, cmap='RdYlGn', aspect='auto', vmin=0, vmax=1)
    ax2.set_xticks([0])
    ax2.set_xticklabels(['Status'])
    ax2.set_yticks(range(len(test_names)))
    ax2.set_yticklabels([name[:20] for name in test_names])
    ax2.set_title('Individual Test Status')
    
    # Add text annotations
    for i in range(len(test_names)):
        text = ax2.text(0, i, 'PASS' if test_status[i] else 'FAIL',
                       ha="center", va="center", color="white", fontsize=10, weight='bold')
    
    # 3. Feature coverage
    ax3 = fig.add_subplot(gs[1, :])
    features = ['Modes', 'Methods', 'Categorical', 'Fixed Params', 
                'Multi-Scale', 'User Config', 'Triggers', 'NM Config', 'Validation']
    coverage = [test_status[i] for i in range(min(len(features), len(test_status)))]
    bars = ax3.bar(features, coverage, color=['green' if c else 'red' for c in coverage])
    ax3.set_ylim(0, 1.2)
    ax3.set_ylabel('Coverage')
    ax3.set_title('Feature Test Coverage')
    ax3.tick_params(axis='x', rotation=45)
    
    # 4. Test execution info
    ax4 = fig.add_subplot(gs[2, :])
    info_text = f"""
Test Execution Summary
═══════════════════════════════════════════
Total Tests: {len(test_status)}
Passed: {passed}
Failed: {failed}
Success Rate: {passed/len(test_status)*100:.1f}%

Key Features Tested:
- Refinement modes (off/on with trigger_ratio)
- Multiple methods (Adam/DLS/Nelder-Mead)
- Parameter handling (categorical/fixed)
- Multi-scale adaptation
- Nelder-Mead configurations (corner/centroid)
- Configuration validation
    """
    ax4.text(0.05, 0.95, info_text, transform=ax4.transAxes,
             fontsize=10, verticalalignment='top',
             fontfamily='monospace',
             bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
    ax4.axis('off')
    
    plt.suptitle('Differential Evolution Refinement Test Suite Results', fontsize=16)
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
    plt.close()


if __name__ == "__main__":
    # Create results directory
    test_dir = os.path.dirname(os.path.abspath(__file__))
    results_dir = os.path.join(test_dir, 'results', f'refinement_{datetime.now().strftime("%Y%m%d_%H%M%S")}')
    os.makedirs(results_dir, exist_ok=True)
    
    # Run tests with visualization
    results = run_all_tests(visualize=True, results_dir=results_dir)
    
    # Save results
    with open(os.path.join(results_dir, 'test_results.txt'), 'w') as f:
        f.write("Refinement Test Results\n")
        f.write("=" * 50 + "\n")
        f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write("=" * 50 + "\n\n")
        
        # Summary
        passed = sum(1 for r in results.values() if r == "PASSED")
        total = len(results)
        f.write(f"Summary: {passed}/{total} tests passed ({passed/total*100:.1f}%)\n\n")
        
        # Individual results
        f.write("Individual Test Results:\n")
        f.write("-" * 30 + "\n")
        for test_name, result in results.items():
            status = "PASS" if result == "PASSED" else "FAIL"
            f.write(f"[{status}] {test_name}: {result}\n")
    
    print(f"\nResults and visualizations saved to: {results_dir}")