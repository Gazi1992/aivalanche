"""
Metamodel functionality for Differential Evolution.

This module implements metamodel-based optimization using a nested DE approach,
where a fast metamodel is used to run a separate DE optimization to generate
promising trial candidates.

Author: Gazmend Alia
"""

import numpy as np
import pandas as pd
from typing import Dict, Any, Optional, List, Tuple, Callable
from sklearn.metrics import r2_score, mean_squared_error
import warnings
warnings.filterwarnings('ignore', category=UserWarning)

# Import our metamodel
from ...metamodels.gaussian_process import GaussianProcessMetamodel


def _setup_metamodel_config(de_instance, user_config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Setup metamodel configuration with defaults and user overrides.
    
    Args:
        de_instance: DifferentialEvolution instance
        user_config: User-provided configuration
        
    Returns:
        Complete metamodel configuration
    """
    # Default configuration
    default_config = {
        'type': 'gaussian_process',
        'min_training_points': de_instance.pop_size if de_instance else 20,  # Use pop_size as default
        'min_accuracy': 0.9,  # Minimum R² score to use metamodel
        
        # Gaussian Process specific settings
        'gp_config': {
            'kernel': 'matern',
            'alpha': 1e-6,
            'n_restarts_optimizer': 5,
            'normalize_y': True
        },
        
        # Nested DE settings
        'nested_de_config': {
            'max_iterations': 100,
            'mutation_factor_1': (0.8, 1.2),  # More aggressive
            'mutation_factor_2': (0.3, 0.7),
            'mutation_factor_3': (0.0, 0.3),
            'recombination_factor': (0.9, 0.99),
            'adaptive_iterations': True,  # Scale iterations based on accuracy
            'max_iterations_multiplier': 10.0,  # Max multiplier when accuracy=1.0
        },
        
        
        # Validation settings
        'validation_ratio': 0.2,  # Hold out ratio for validation
        'min_validation_points': 10,
        
        # Debug/verbose
        'verbose': False,
        'show_plots': True,  # Show accuracy plots when verbose
        'save_plots': False,  # Save plots to files
        'plot_dir': None  # Directory for saving plots
    }
    
    # Merge user config
    if user_config:
        _deep_update(default_config, user_config)
    
    return default_config


def _deep_update(base_dict: Dict, update_dict: Dict) -> None:
    """Deep update dictionary in place."""
    for key, value in update_dict.items():
        if isinstance(value, dict) and key in base_dict and isinstance(base_dict[key], dict):
            _deep_update(base_dict[key], value)
        else:
            base_dict[key] = value


class MetamodelManager:
    """Manages metamodel training, evaluation, and accuracy tracking."""
    
    def __init__(self, de_instance, config: Dict[str, Any]):
        self.de = de_instance
        self.config = config
        self.model = None
        
        # Tracking
        self.is_trained = False
        self.current_accuracy = 0.0
        self.training_history = []
        self.last_train_iter = -1
        
        # Training data (will be handled by metamodel)
        self.X_all = None
        self.y_all = None
        
    def should_use_metamodel(self) -> bool:
        """Check if metamodel should be used based on training status and accuracy."""
        # Need minimum training points
        # Count available evaluated points from trials (not survivors)
        available_points = 0
        if hasattr(self.de, 'all_trials_metrics') and self.de.all_trials_metrics is not None:
            # Count non-NaN metrics from all trials
            if self.de.all_trials_metrics.shape[0] > 0:
                available_points = np.sum(~np.isnan(self.de.all_trials_metrics))
                
        if available_points < self.config['min_training_points']:
            return False
            
        # Always train/retrain when we have enough points
        # This ensures we use the most up-to-date data
        self._train_metamodel()
            
        # Use metamodel only if accuracy is sufficient
        return self.is_trained and self.current_accuracy >= self.config['min_accuracy']
    
    def _train_metamodel(self):
        """Train the metamodel on recent optimization history."""
        if self.config['verbose']:
            print(f"\n[Metamodel] Training at iteration {self.de.iter}")
            
        # Prepare training data
        self._prepare_training_data()
        
        if self.X_all is None or len(self.X_all) < self.config['min_training_points']:
            if self.config['verbose']:
                print(f"[Metamodel] Not enough training points: {0 if self.X_all is None else len(self.X_all)}")
            return
            
        # Create and train model
        self._create_model()
        
        try:
            # Train model - it handles normalization, corner detection, and train/test split internally
            self.model.fit(self.X_all, self.y_all)
            self.is_trained = True
            
            # Get accuracy from the model's internal validation
            self.current_accuracy = self.model.score()
            self.last_train_iter = self.de.iter
            
            if self.config['verbose']:
                info = self.model.get_info()
                print(f"[Metamodel] Training complete. Accuracy: {self.current_accuracy:.3f}")
                print(f"[Metamodel] Corners: {info['n_corners']}, Edges: {info['n_edges']}, Train: {info['n_train']}, Test: {info['n_test']}")
                
                # Show or save accuracy plot if verbose
                if self.config.get('show_plots', True) or self.config.get('save_plots', False):
                    save_path = None
                    if self.config.get('save_plots', False):
                        import os
                        plot_dir = self.config.get('plot_dir', '.')
                        # Create subfolder for accuracy plots
                        accuracy_plot_dir = os.path.join(plot_dir, 'metamodel_accuracy_plots')
                        os.makedirs(accuracy_plot_dir, exist_ok=True)
                        save_path = os.path.join(accuracy_plot_dir, f'accuracy_iter_{self.de.iter:03d}.png')
                        print(f"[Metamodel] Saving accuracy plot to: {save_path}")
                    
                    if self.config.get('show_plots', True):
                        print(f"[Metamodel] Displaying accuracy plot...")
                    
                    self.model.plot_accuracy(
                        figsize=(8, 6), 
                        save_path=save_path,
                        show=self.config.get('show_plots', True)
                    )
                
        except Exception as e:
            if self.config['verbose']:
                print(f"[Metamodel] Training failed: {str(e)}")
                import traceback
                traceback.print_exc()
            self.is_trained = False
            self.current_accuracy = 0.0
            
    def _prepare_training_data(self):
        """Prepare training data from optimization history."""
        # Get all evaluated points from history
        all_params = []
        all_metrics = []
        
        # Use trials (not survivors) since survivors are just a subset of trials
        if hasattr(self.de, 'all_trials') and self.de.all_trials is not None:
            # Get all trials and their metrics
            for i in range(self.de.all_trials.shape[0]):
                # Each row contains pop_size individuals
                for j in range(self.de.pop_size):
                    params = self.de.all_trials[i, j, :]
                    metric = self.de.all_trials_metrics[i, j]
                    if not np.isnan(metric):
                        all_params.append(params)
                        all_metrics.append(metric)
        
        # Debug: Print data collection info
        if self.config.get('verbose', False):
            print(f"[Metamodel] Collected {len(all_params)} training points from {self.de.all_trials.shape[0] if hasattr(self.de, 'all_trials') and self.de.all_trials is not None else 0} iterations")
                    
        # Convert to arrays
        # Note: all_trials contain normalized values (0-1)
        # We need to denormalize them because the metamodel expects original scale
        # and will do its own normalization internally
        if len(all_params) > 0:
            # Denormalize parameters to original space
            self.X_all = self.de.parameters.unnorm_all(pd.DataFrame(np.array(all_params), columns=self.de.parameters.variable_names)).values
            self.y_all = np.array(all_metrics)

        else:
            self.X_all = None
            self.y_all = None
                    
    def _create_model(self):
        """Create the metamodel based on configuration."""
        if self.config['type'] == 'gaussian_process':
            gp_config = self.config['gp_config']
            
            # Map kernel names
            kernel_map = {
                'matern': 'matern52',  # Default to Matern 5/2
                'rbf': 'rbf'
            }
            kernel_type = kernel_map.get(gp_config['kernel'], 'rbf')
            
            # Create our GaussianProcessMetamodel
            self.model = GaussianProcessMetamodel(
                kernel_type=kernel_type,
                optimize_hyperparameters=True,
                n_restarts=gp_config['n_restarts_optimizer'],
                random_state=self.de.seed if hasattr(self.de, 'seed') else None,
                test_size=self.config.get('validation_ratio', 0.2)
            )
        else:
            raise ValueError(f"Unknown metamodel type: {self.config['type']}")
            
        
    def predict(self, X: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """
        Predict using the metamodel.
        
        Args:
            X: Parameter values in original scale
            
        Returns:
            Tuple of (predictions, uncertainties)
        """
        if not self.is_trained:
            raise RuntimeError("Metamodel not trained")
            
        # Pass data directly - metamodel handles normalization internally
        if self.config['type'] == 'gaussian_process':
            # Use predict_with_uncertainty for GP
            y_pred, y_std = self.model.predict_with_uncertainty(X)
            return y_pred, y_std
        else:
            # For other models, just predict without uncertainty
            y_pred = self.model.predict(X)
            return y_pred, np.zeros_like(y_pred)
            
    def get_statistics(self) -> Dict[str, Any]:
        """Get metamodel statistics."""
        stats = {
            'is_trained': self.is_trained,
            'current_accuracy': self.current_accuracy,
            'last_train_iter': self.last_train_iter,
            'training_history': self.training_history
        }
        
        if self.is_trained and self.model is not None:
            # Add model-specific info
            model_info = self.model.get_info()
            stats.update({
                'n_training_points': model_info.get('n_train', 0),
                'n_test_points': model_info.get('n_test', 0),
                'n_corners': model_info.get('n_corners', 0),
                'n_edges': model_info.get('n_edges', 0)
            })
        else:
            stats['n_training_points'] = 0
            
        return stats


def _should_use_metamodel_de(de_instance) -> bool:
    """
    Check if metamodel-based DE should be used for trial generation.
    
    Args:
        de_instance: DifferentialEvolution instance
        
    Returns:
        bool: Whether to use metamodel DE
    """
    if not hasattr(de_instance, 'metamodel_manager') or de_instance.metamodel_manager is None:
        return False
        
    return de_instance.metamodel_manager.should_use_metamodel()


def _run_metamodel_de_optimization(de_instance) -> pd.DataFrame:
    """
    Run a nested DE optimization using the metamodel as objective function.
    
    Args:
        de_instance: DifferentialEvolution instance
        
    Returns:
        DataFrame with optimized trial candidates
    """
    manager = de_instance.metamodel_manager
    config = manager.config['nested_de_config']
    
    if config.get('verbose', manager.config['verbose']):
        print(f"\n[Metamodel DE] Starting nested optimization at iter {de_instance.iter}")
    
    # Create evaluation function wrapper for metamodel
    def metamodel_eval_func(parameters, **kwargs):
        # Parameters are in DataFrame format in original scale
        # Pass directly to metamodel which handles normalization internally
        predictions, uncertainties = manager.predict(parameters.values)
        
        # For debugging metamodel issues
        if config.get('debug_predictions', False):
            print(f"[Metamodel Debug] Input shape: {parameters.shape}")
            print(f"[Metamodel Debug] First point: {parameters.iloc[0].values}")
            print(f"[Metamodel Debug] Predictions: min={np.min(predictions):.6f}, max={np.max(predictions):.6f}, mean={np.mean(predictions):.6f}")
        
        # Return in format expected by DE
        return [{'metric': pred} for pred in predictions]
    
    # Import here to avoid circular dependency
    from . import DifferentialEvolution
    
    # Adaptive iteration scaling based on accuracy
    base_iterations = config['max_iterations']
    
    if config.get('adaptive_iterations', True):
        # Scale iterations based on metamodel accuracy
        # If accuracy is at minimum threshold, use base iterations
        # If accuracy is perfect (1.0), use more iterations
        accuracy = manager.current_accuracy
        min_accuracy = manager.config['min_accuracy']
        max_multiplier = config.get('max_iterations_multiplier', 3.0)
        
        if accuracy >= min_accuracy:
            # Linear scaling: at min_accuracy use base_iterations,
            # at accuracy=1.0 use max_multiplier * base_iterations
            accuracy_factor = (accuracy - min_accuracy) / (1.0 - min_accuracy)
            iterations_multiplier = 1.0 + (max_multiplier - 1.0) * accuracy_factor
            adaptive_iterations = int(base_iterations * iterations_multiplier)
            
            if config.get('verbose', manager.config['verbose']):
                print(f"[Metamodel DE] Accuracy: {accuracy:.3f}, using {adaptive_iterations} iterations (base: {base_iterations}, multiplier: {iterations_multiplier:.2f})")
        else:
            # Shouldn't happen as we check accuracy before calling this
            adaptive_iterations = base_iterations
    else:
        # No adaptive scaling
        adaptive_iterations = base_iterations
    
    # Use current survivors as initial population
    current_pop_df = pd.DataFrame(
        de_instance.survivors, 
        columns=de_instance.parameters.variable_names
    )
    
    # Create nested DE instance
    nested_de = DifferentialEvolution(
        seed=de_instance.seed + de_instance.iter,  # Different seed each time
        eval_func=metamodel_eval_func,
        parameters=de_instance.parameters,
        opt_min_or_max=de_instance.opt_min_or_max,
        
        # Population settings
        pop_size=de_instance.pop_size,
        max_iterations=adaptive_iterations,
        
        # Disable metric threshold to prevent early stopping due to metamodel inaccuracies
        # Metamodel can predict values outside the true function's range
        metric_threshold=float('-inf') if de_instance.opt_min_or_max == 'min' else float('inf'),
        
        # Use current population as initial population
        init_pop=current_pop_df,
        
        # No metamodel recursion!
        metamodel_mode='off',
        
        # No refinement or perturbation
        refinement_mode='off',
        perturbation_mode='off',
        adaptive_boundaries_mode='off',
        
        # No file output
        results_dir=None
    )
    
    # Run nested optimization
    nested_de.run_optimization()
    
    if config.get('verbose', manager.config['verbose']):
        print(f"[Metamodel DE] Completed. Best metric: {nested_de.best_metric:.6f}")
    
    # Extract the final survivors as trial candidates
    # Since the nested DE runs for full iterations with accurate metamodel,
    # the entire survivor population should be high quality
    final_population = nested_de.survivors
    
    # Debug: Check quality of what we're returning
    if config.get('verbose', manager.config['verbose']):
        # Evaluate the quality of the returned population
        df_survivors = pd.DataFrame(final_population, columns=de_instance.parameters.variable_names)
        df_survivors_orig = de_instance.parameters.unnorm_all(df_survivors)
        predictions, _ = manager.predict(df_survivors_orig.values)
        
        print(f"[Metamodel DE] Returning full survivor population:")
        print(f"  Population size: {len(final_population)}")
        print(f"  Predicted metrics: min={np.min(predictions):.6f}, max={np.max(predictions):.6f}, mean={np.mean(predictions):.6f}")
        
        # Show diversity in parameter space
        print(f"[Metamodel DE] Population diversity (original space):")
        for param in de_instance.parameters.variable_names:
            print(f"    {param}: [{df_survivors_orig[param].min():.6f}, {df_survivors_orig[param].max():.6f}]")
    
    return final_population


def _initialize_metamodel_manager(de_instance):
    """
    Initialize the metamodel manager for a DE instance.
    
    Args:
        de_instance: DifferentialEvolution instance
    """
    if de_instance.metamodel_mode == 'off':
        de_instance.metamodel_manager = None
        return
        
    # Setup configuration with defaults
    config = _setup_metamodel_config(de_instance, de_instance.metamodel_config)
    
    # Create manager
    de_instance.metamodel_manager = MetamodelManager(de_instance, config)
    
    if config['verbose']:
        print(f"\n[Metamodel] Initialized")
        print(f"[Metamodel] Min training points: {config['min_training_points']}")
        print(f"[Metamodel] Min accuracy required: {config['min_accuracy']}")


