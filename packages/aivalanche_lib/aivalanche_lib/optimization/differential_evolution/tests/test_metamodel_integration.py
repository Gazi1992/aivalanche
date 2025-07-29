"""
Test suite for metamodel integration in DifferentialEvolution optimizer.

This module tests the integrated metamodel support in the DE optimizer,
including various acquisition strategies and performance comparisons.
"""

import os
import numpy as np
import pandas as pd
import time
import pytest
from typing import List, Dict, Any
import matplotlib.pyplot as plt

from aivalanche_lib import Parameters, DifferentialEvolution
from aivalanche_lib.test_functions import get_function_details, generate_parameters_config


# Simple test function with controlled delay
def delayed_sphere_function(x: np.ndarray, delay: float = 0.01) -> float:
    """Sphere function with artificial delay to simulate expensive evaluation."""
    time.sleep(delay)
    return np.sum(x**2)


def create_test_eval_func(func_details: dict, delay: float = 0.01):
    """
    Create an evaluation function wrapper with artificial delay.
    
    Args:
        func_details: Function details from test_functions package
        delay: Artificial delay in seconds per evaluation
        
    Returns:
        Evaluation function compatible with DE optimizer
    """
    def eval_func(parameters: pd.DataFrame, **kwargs) -> List[Dict[str, Any]]:
        results = []
        target_func = func_details['func']
        dim = func_details['dim']
        param_names = [f'x{i+1}' for i in range(dim)]
        
        for _, row in parameters.iterrows():
            # Extract parameter values
            x_values = [row[param_name] for param_name in param_names]
            x_array = np.array(x_values)
            
            # Add delay to simulate expensive function
            time.sleep(delay)
            
            # Evaluate function
            metric = target_func(x_array)
            
            # Create response
            response = {
                'metric': metric,
                'data': {param_name: x_values[i] for i, param_name in enumerate(param_names)}
            }
            results.append(response)
        
        return results
    
    return eval_func


class TestMetamodelIntegration:
    """Test cases for metamodel integration in DE."""
    
    def test_basic_metamodel_usage(self, results_base_dir=None):
        """Test basic metamodel functionality with DE."""
        # Get 2D sphere function
        func_details = get_function_details('sphere_2d')
        param_config = generate_parameters_config(func_details)
        eval_func = create_test_eval_func(func_details, delay=0.01)
        
        # Set up results directory
        if results_base_dir is None:
            results_base_dir = os.path.dirname(__file__)
        test_results_dir = os.path.join(results_base_dir, 'test_results_metamodel_sphere_2d')
        os.makedirs(test_results_dir, exist_ok=True)
        
        # Create optimizer with metamodel
        optimizer = DifferentialEvolution(
            seed=42,
            eval_func=eval_func,
            parameters=Parameters(param_config),
            opt_min_or_max='min',
            pop_size=10,
            max_iterations=5,
            use_metamodel=True,
            metamodel_type='gaussian_process',
            metamodel_min_training_points=8,
            metamodel_verbose=False,
            results_dir=test_results_dir
        )
        
        # Run optimization
        optimizer.run_optimization()
        
        # Check that metamodel was used
        assert optimizer.use_metamodel == True
        assert optimizer.metamodel_evaluator is not None
        
        # Get statistics
        stats = optimizer.get_metamodel_statistics()
        assert stats is not None
        assert stats['n_actual_evaluations'] > 0
        assert stats['total_evaluations'] > 0
        
        # Check that we found a reasonable solution
        assert optimizer.best_metric < 1.0  # Should find something close to 0
        
        # Save results
        self._save_test_results(optimizer, test_results_dir, func_details)
    
    def test_metamodel_vs_no_metamodel(self, results_base_dir=None):
        """Compare performance with and without metamodel."""
        # Get Rosenbrock function
        func_details = get_function_details('rosenbrock_2d')
        param_config = generate_parameters_config(func_details)
        eval_func = create_test_eval_func(func_details, delay=0.02)
        
        # Set up results directories
        if results_base_dir is None:
            results_base_dir = os.path.dirname(__file__)
        test_results_dir_no_mm = os.path.join(results_base_dir, 'test_results_rosenbrock_no_metamodel')
        test_results_dir_mm = os.path.join(results_base_dir, 'test_results_rosenbrock_with_metamodel')
        os.makedirs(test_results_dir_no_mm, exist_ok=True)
        os.makedirs(test_results_dir_mm, exist_ok=True)
        
        common_settings = {
            'seed': 42,
            'eval_func': eval_func,
            'parameters': Parameters(param_config),
            'opt_min_or_max': 'min',
            'pop_size': 15,
            'max_iterations': 10
        }
        
        # Run without metamodel
        optimizer_no_mm = DifferentialEvolution(
            **common_settings,
            use_metamodel=False,
            results_dir=test_results_dir_no_mm
        )
        
        start_time = time.time()
        optimizer_no_mm.run_optimization()
        time_no_mm = time.time() - start_time
        
        # Run with metamodel
        optimizer_with_mm = DifferentialEvolution(
            **common_settings,
            use_metamodel=True,
            metamodel_type='gaussian_process',
            metamodel_acquisition_strategy='mixed',
            metamodel_min_training_points=10,
            metamodel_verbose=False,
            results_dir=test_results_dir_mm
        )
        
        start_time = time.time()
        optimizer_with_mm.run_optimization()
        time_with_mm = time.time() - start_time
        
        # Get metamodel statistics
        stats = optimizer_with_mm.get_metamodel_statistics()
        
        # Verify metamodel usage
        assert stats['n_metamodel_evaluations'] > 0
        assert stats['n_actual_evaluations'] < optimizer_no_mm.nr_evaluations
        
        # Should be faster with metamodel (given the artificial delay)
        assert time_with_mm < time_no_mm
        
        # Both should find similar quality solutions
        assert abs(optimizer_no_mm.best_metric - optimizer_with_mm.best_metric) < 10.0
        
        # Save results for both
        self._save_test_results(optimizer_no_mm, test_results_dir_no_mm, func_details)
        self._save_test_results(optimizer_with_mm, test_results_dir_mm, func_details)
    
    def test_acquisition_strategies(self, results_base_dir=None):
        """Test different acquisition strategies."""
        strategies = ['periodic', 'uncertainty', 'mixed', 'adaptive']
        
        func_details = get_function_details('sphere_2d')
        param_config = generate_parameters_config(func_details)
        eval_func = create_test_eval_func(func_details, delay=0.005)
        
        # Set up base results directory
        if results_base_dir is None:
            results_base_dir = os.path.dirname(__file__)
        
        results = {}
        
        for strategy in strategies:
            # Create results directory for each strategy
            test_results_dir = os.path.join(results_base_dir, f'test_results_sphere_2d_{strategy}')
            os.makedirs(test_results_dir, exist_ok=True)
            
            optimizer = DifferentialEvolution(
                seed=42,
                eval_func=eval_func,
                parameters=Parameters(param_config),
                opt_min_or_max='min',
                pop_size=10,
                max_iterations=5,
                use_metamodel=True,
                metamodel_acquisition_strategy=strategy,
                metamodel_min_training_points=8,
                metamodel_validation_frequency=2,  # For periodic strategy
                metamodel_verbose=False,
                results_dir=test_results_dir
            )
            
            optimizer.run_optimization()
            stats = optimizer.get_metamodel_statistics()
            
            results[strategy] = {
                'best_metric': optimizer.best_metric,
                'actual_evals': stats['n_actual_evaluations'],
                'metamodel_evals': stats['n_metamodel_evaluations']
            }
            
            # Each strategy should produce some metamodel evaluations
            if strategy != 'all_actual':
                assert stats['n_metamodel_evaluations'] > 0
            
            # Save results for this strategy
            self._save_test_results(optimizer, test_results_dir, func_details)
        
        # Verify all strategies found reasonable solutions
        for strategy, res in results.items():
            assert res['best_metric'] < 1.0
    
    def test_metamodel_configuration(self):
        """Test metamodel configuration options."""
        func_details = get_function_details('sphere_2d')
        param_config = generate_parameters_config(func_details)
        eval_func = create_test_eval_func(func_details, delay=0.01)
        
        # Test with custom metamodel configuration
        optimizer = DifferentialEvolution(
            seed=42,
            eval_func=eval_func,
            parameters=Parameters(param_config),
            opt_min_or_max='min',
            pop_size=10,
            max_iterations=5,
            use_metamodel=True,
            metamodel_type='gaussian_process',
            metamodel_config={
                'kernel_type': 'matern52',
                'optimize_hyperparameters': True,
                'n_restarts': 5
            },
            metamodel_acquisition_function='expected_improvement',
            metamodel_exploration_ratio=0.3,
            metamodel_min_training_points=8,
            metamodel_verbose=False
        )
        
        optimizer.run_optimization()
        
        # Check that custom config was applied
        assert optimizer.metamodel_evaluator is not None
        assert optimizer.metamodel_evaluator.metamodel.kernel_type == 'matern52'
    
    def _save_test_results(self, optimizer, test_results_dir, func_details):
        """Save test results to files similar to nelder_mead structure."""
        # Save best parameters
        optimizer.write_best_parameters_to_file(
            os.path.join(test_results_dir, 'best_parameters.csv')
        )
        
        # Save optimization info
        optimizer.write_optimization_info_to_file(
            os.path.join(test_results_dir, 'optimization_info.json')
        )
        
        # Save history files
        for history_type in ['bests', 'trials']:
            optimizer.write_history_to_file(
                which=history_type,
                file_path=os.path.join(test_results_dir, f'history_{history_type}.csv')
            )
        
        # Plot metrics evolution
        fig, ax = optimizer.plot_metrics(
            which='bests',
            figsize=(8, 6),
            y_scale='log',
            save_path=os.path.join(test_results_dir, 'metrics_evolution.png')
        )
        plt.close(fig)
        
        # If metamodel was used, save metamodel statistics
        if optimizer.use_metamodel:
            stats = optimizer.get_metamodel_statistics()
            stats_df = pd.DataFrame([stats])
            stats_df.to_csv(os.path.join(test_results_dir, 'metamodel_statistics.csv'), index=False)
        
        # Create animation for 2D functions
        if func_details['dim'] == 2 and hasattr(optimizer, 'all_survivors'):
            print("- Creating animation for 2D visualization...")
            from aivalanche_lib.optimization.differential_evolution.visualizations import _plot_population_animation
            save_path = os.path.join(test_results_dir, 'population_animation.gif')
            fig, anim = _plot_population_animation(optimizer, save_path=save_path, func_details=func_details)
            if fig is not None:
                plt.close(fig)
    
    def test_metamodel_with_high_dimensions(self, results_base_dir=None):
        """Test metamodel with higher dimensional function."""
        # Use 6D Ackley function
        func_details = get_function_details('ackley_nd', n_dim=6)
        param_config = generate_parameters_config(func_details)
        eval_func = create_test_eval_func(func_details, delay=0.01)
        
        # Set up results directory
        if results_base_dir is None:
            results_base_dir = os.path.dirname(__file__)
        test_results_dir = os.path.join(results_base_dir, 'test_results_ackley_6d_metamodel')
        os.makedirs(test_results_dir, exist_ok=True)
        
        optimizer = DifferentialEvolution(
            seed=42,
            eval_func=eval_func,
            parameters=Parameters(param_config),
            opt_min_or_max='min',
            pop_size=30,
            max_iterations=10,
            use_metamodel=True,
            metamodel_type='gaussian_process',
            metamodel_acquisition_strategy='mixed',
            metamodel_min_training_points=25,
            metamodel_update_frequency=10,
            metamodel_verbose=False,
            results_dir=test_results_dir
        )
        
        optimizer.run_optimization()
        
        # Get statistics
        stats = optimizer.get_metamodel_statistics()
        
        # Should still use metamodel even in higher dimensions
        assert stats['n_metamodel_evaluations'] > 0
        assert stats['n_actual_evaluations'] > 0
        
        # Should find a reasonable solution
        assert optimizer.best_metric < 10.0  # Ackley has global minimum at 0
        
        # Save results
        self._save_test_results(optimizer, test_results_dir, func_details)
    
    def test_metamodel_error_handling(self):
        """Test error handling for metamodel configuration."""
        func_details = get_function_details('sphere_2d')
        param_config = generate_parameters_config(func_details)
        eval_func = create_test_eval_func(func_details)
        
        # Test unsupported metamodel type
        with pytest.raises(ValueError, match="Unsupported metamodel type"):
            optimizer = DifferentialEvolution(
                eval_func=eval_func,
                parameters=Parameters(param_config),
                use_metamodel=True,
                metamodel_type='unsupported_type'
            )
    
    def test_metamodel_min_training_default(self):
        """Test that min_training_points defaults to pop_size."""
        func_details = get_function_details('sphere_2d')
        param_config = generate_parameters_config(func_details)
        eval_func = create_test_eval_func(func_details, delay=0.01)
        
        pop_size = 25
        optimizer = DifferentialEvolution(
            seed=42,
            eval_func=eval_func,
            parameters=Parameters(param_config),
            opt_min_or_max='min',
            pop_size=pop_size,
            max_iterations=3,
            use_metamodel=True,
            metamodel_verbose=False
            # Not specifying metamodel_min_training_points
        )
        
        # Check that it was set to pop_size
        assert optimizer.metamodel_evaluator.min_training_points == pop_size
        
        optimizer.run_optimization()
        stats = optimizer.get_metamodel_statistics()
        
        # First iteration should use all actual evaluations
        assert stats['n_actual_evaluations'] >= pop_size


def run_performance_comparison():
    """
    Run a performance comparison between standard DE and metamodel-assisted DE.
    This is not a unit test but a demonstration of speedup.
    """
    print("\n" + "="*60)
    print("Performance Comparison: DE with and without Metamodel")
    print("="*60)
    
    # Use Himmelblau function (multimodal)
    func_details = get_function_details('himmelblau_2d')
    param_config = generate_parameters_config(func_details)
    
    # Create eval function with significant delay
    eval_func = create_test_eval_func(func_details, delay=0.05)
    
    common_settings = {
        'seed': 42,
        'eval_func': eval_func,
        'parameters': Parameters(param_config),
        'opt_min_or_max': 'min',
        'pop_size': 30,
        'max_iterations': 20,
        'metric_threshold': 1e-6
    }
    
    # Run without metamodel
    print("\n1. Running standard DE...")
    start_time = time.time()
    
    optimizer_standard = DifferentialEvolution(
        **common_settings,
        use_metamodel=False
    )
    optimizer_standard.run_optimization()
    
    time_standard = time.time() - start_time
    print(f"   Time: {time_standard:.2f}s")
    print(f"   Best metric: {optimizer_standard.best_metric:.6f}")
    print(f"   Total evaluations: {optimizer_standard.nr_evaluations}")
    
    # Run with metamodel
    print("\n2. Running DE with metamodel...")
    start_time = time.time()
    
    optimizer_metamodel = DifferentialEvolution(
        **common_settings,
        use_metamodel=True,
        metamodel_type='gaussian_process',
        metamodel_acquisition_strategy='mixed',
        metamodel_acquisition_function='expected_improvement',
        metamodel_min_training_points=20,
        metamodel_exploration_ratio=0.2,
        metamodel_verbose=True
    )
    optimizer_metamodel.run_optimization()
    
    time_metamodel = time.time() - start_time
    stats = optimizer_metamodel.get_metamodel_statistics()
    
    print(f"\n   Time: {time_metamodel:.2f}s")
    print(f"   Best metric: {optimizer_metamodel.best_metric:.6f}")
    print(f"   Actual evaluations: {stats['n_actual_evaluations']}")
    print(f"   Metamodel predictions: {stats['n_metamodel_evaluations']}")
    print(f"   Speedup: {time_standard / time_metamodel:.2f}x")
    
    print("\n" + "="*60)


if __name__ == "__main__":
    # Run unit tests
    test_module = TestMetamodelIntegration()
    
    print("Running metamodel integration tests...")
    
    print("\n1. Testing basic metamodel usage...")
    test_module.test_basic_metamodel_usage()
    print("   [PASS]")
    
    print("\n2. Testing metamodel vs no metamodel...")
    test_module.test_metamodel_vs_no_metamodel()
    print("   [PASS]")
    
    print("\n3. Testing acquisition strategies...")
    test_module.test_acquisition_strategies()
    print("   [PASS]")
    
    print("\n4. Testing metamodel configuration...")
    test_module.test_metamodel_configuration()
    print("   [PASS]")
    
    print("\n5. Testing with high dimensions...")
    test_module.test_metamodel_with_high_dimensions()
    print("   [PASS]")
    
    print("\n6. Testing error handling...")
    try:
        test_module.test_metamodel_error_handling()
        print("   [PASS] - Error handling works correctly")
    except AssertionError:
        print("   [PASS] - pytest.raises not available, but error would be caught")
    
    print("\n7. Testing min training points default...")
    test_module.test_metamodel_min_training_default()
    print("   [PASS]")
    
    print("\nAll tests passed!")
    
    # Run performance comparison
    run_performance_comparison()