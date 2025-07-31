"""
Metamodel modes and configurations for Differential Evolution.

This module provides predefined metamodel configurations for different use cases,
making it easier to enable and configure metamodel-assisted optimization.
"""

from typing import Dict, Any, Optional, List

# Predefined metamodel configurations
METAMODEL_MODES = {
    'off': None,  # No metamodel
    
    'auto': {
        'enabled': True,
        'type': 'gaussian_process',
        'model_config': {
            'kernel': 'matern',
            'alpha': 1e-6,
            'n_restarts_optimizer': 5
        },
        'acquisition_strategy': 'mixed',
        'acquisition_function': 'expected_improvement',
        'min_training_points': None,  # Will be set to pop_size
        'update_frequency': 5,
        'exploration_ratio': 0.2,
        'uncertainty_threshold': 0.2,
        'validation_frequency': 10,
        'verbose': False
    },
    
    'exploration': {
        'enabled': True,
        'type': 'gaussian_process',
        'model_config': {
            'kernel': 'rbf',
            'alpha': 1e-5,
            'n_restarts_optimizer': 10
        },
        'acquisition_strategy': 'adaptive',
        'acquisition_function': 'upper_confidence_bound',
        'min_training_points': None,  # Will be set to 2 * pop_size
        'update_frequency': 3,
        'exploration_ratio': 0.4,  # More exploration
        'uncertainty_threshold': 0.3,
        'validation_frequency': 5,
        'verbose': False
    },
    
    'exploitation': {
        'enabled': True,
        'type': 'gaussian_process',
        'model_config': {
            'kernel': 'matern',
            'alpha': 1e-8,  # More trust in model
            'n_restarts_optimizer': 3
        },
        'acquisition_strategy': 'mixed',
        'acquisition_function': 'expected_improvement',
        'min_training_points': None,  # Will be set to 0.5 * pop_size
        'update_frequency': 10,  # Less frequent updates
        'exploration_ratio': 0.1,  # Less exploration
        'uncertainty_threshold': 0.1,
        'validation_frequency': 20,
        'verbose': False
    },
    
    'fast': {
        'enabled': True,
        'type': 'gaussian_process',
        'model_config': {
            'kernel': 'rbf',
            'alpha': 1e-4,
            'n_restarts_optimizer': 1,  # Fast training
            'optimize_kernel': False
        },
        'acquisition_strategy': 'all_metamodel',  # Use metamodel for all evaluations
        'acquisition_function': 'expected_improvement',
        'min_training_points': None,  # Will be set to 0.3 * pop_size
        'update_frequency': 20,  # Infrequent updates
        'exploration_ratio': 0.05,
        'uncertainty_threshold': 0.5,  # Accept higher uncertainty
        'validation_frequency': 50,
        'verbose': False
    },
    
    'accurate': {
        'enabled': True,
        'type': 'gaussian_process',
        'model_config': {
            'kernel': 'matern',
            'alpha': 1e-10,  # Very low noise
            'n_restarts_optimizer': 20,  # Thorough optimization
            'normalize_y': True
        },
        'acquisition_strategy': 'uncertainty',  # Only use when certain
        'acquisition_function': 'expected_improvement',
        'min_training_points': None,  # Will be set to 3 * pop_size
        'update_frequency': 2,  # Frequent updates
        'exploration_ratio': 0.3,
        'uncertainty_threshold': 0.05,  # Very low threshold
        'validation_frequency': 5,
        'verbose': True
    },
    
    'periodic': {
        'enabled': True,
        'type': 'gaussian_process',
        'model_config': {
            'kernel': 'rbf',
            'alpha': 1e-6
        },
        'acquisition_strategy': 'periodic',  # Alternates between actual and metamodel
        'acquisition_function': 'probability_of_improvement',
        'min_training_points': None,  # Will be set to pop_size
        'update_frequency': 5,
        'exploration_ratio': 0.25,
        'uncertainty_threshold': 0.15,
        'validation_frequency': 10,  # Validation period for periodic strategy
        'verbose': False
    },
    
    'noisy': {
        'enabled': True,
        'type': 'gaussian_process',
        'model_config': {
            'kernel': 'matern',
            'alpha': 1e-3,  # Higher noise assumption
            'n_restarts_optimizer': 5,
            'normalize_y': True
        },
        'acquisition_strategy': 'mixed',
        'acquisition_function': 'expected_improvement',
        'min_training_points': None,  # Will be set to 2 * pop_size
        'update_frequency': 7,
        'exploration_ratio': 0.35,  # More exploration for noisy functions
        'uncertainty_threshold': 0.25,
        'validation_frequency': 15,
        'verbose': False
    },
    
    'high_dimensional': {
        'enabled': True,
        'type': 'gaussian_process',
        'model_config': {
            'kernel': 'rbf',  # Simpler kernel for high dimensions
            'alpha': 1e-5,
            'n_restarts_optimizer': 3,
            'optimize_kernel': True
        },
        'acquisition_strategy': 'adaptive',
        'acquisition_function': 'upper_confidence_bound',
        'min_training_points': None,  # Will be set to 5 * n_dim
        'update_frequency': 10,
        'exploration_ratio': 0.15,
        'uncertainty_threshold': 0.2,
        'validation_frequency': 20,
        'verbose': False
    },
    
    'custom': {
        # Placeholder for user-defined configuration
        # User must provide complete configuration
    }
}


def get_metamodel_config(mode: str, custom_config: Optional[Dict[str, Any]] = None) -> Optional[Dict[str, Any]]:
    """
    Get metamodel configuration for a given mode.
    
    Args:
        mode: Metamodel mode name
        custom_config: Custom configuration (required for 'custom' mode)
        
    Returns:
        Metamodel configuration dictionary or None for 'off' mode
    """
    if mode not in METAMODEL_MODES:
        raise ValueError(f"Unknown metamodel mode: {mode}. Available modes: {list(METAMODEL_MODES.keys())}")
    
    if mode == 'off':
        return None
    
    if mode == 'custom':
        if not custom_config:
            raise ValueError("Custom mode requires a custom_config dictionary")
        return custom_config
    
    # Return copy of predefined configuration
    config = METAMODEL_MODES[mode].copy()
    
    # Override with any custom settings
    if custom_config:
        config.update(custom_config)
    
    return config


def get_mode_description(mode: str) -> str:
    """Get a description of what a metamodel mode does."""
    descriptions = {
        'off': "No metamodel. All evaluations use the actual objective function.",
        'auto': "Balanced metamodel usage. Good general purpose choice for speedup.",
        'exploration': "Emphasizes exploration with uncertain predictions. Good for complex landscapes.",
        'exploitation': "Trusts the model more for exploitation. Good when function is smooth.",
        'fast': "Maximum speedup by using metamodel for most evaluations. May sacrifice accuracy.",
        'accurate': "Conservative usage only when model is very certain. Maintains high accuracy.",
        'periodic': "Periodically validates metamodel predictions. Good balance of speed and reliability.",
        'noisy': "Configured for noisy objective functions. More robust to noise.",
        'high_dimensional': "Optimized for high-dimensional problems. Careful with training data.",
        'custom': "User-defined configuration. Full control over all metamodel parameters."
    }
    return descriptions.get(mode, f"No description available for mode: {mode}")


def suggest_metamodel_mode(problem_type: Optional[str] = None,
                          n_dim: Optional[int] = None,
                          n_evaluations_budget: Optional[int] = None,
                          function_noise: Optional[str] = None,
                          accuracy_required: Optional[str] = None) -> str:
    """
    Suggest a metamodel mode based on problem characteristics.
    
    Args:
        problem_type: Type of problem ('smooth', 'multimodal', 'noisy', etc.)
        n_dim: Number of dimensions
        n_evaluations_budget: Evaluation budget
        function_noise: Noise level ('none', 'low', 'medium', 'high')
        accuracy_required: Required accuracy ('low', 'medium', 'high')
        
    Returns:
        Suggested metamodel mode
    """
    # High dimensional problems
    if n_dim and n_dim > 20:
        return 'high_dimensional'
    
    # Noisy functions
    if function_noise in ['medium', 'high']:
        return 'noisy'
    
    # Limited evaluation budget
    if n_evaluations_budget and n_evaluations_budget < 500:
        if accuracy_required == 'high':
            return 'accurate'
        else:
            return 'fast'
    
    # Smooth problems
    if problem_type == 'smooth':
        return 'exploitation'
    
    # Complex/multimodal problems
    if problem_type == 'multimodal':
        return 'exploration'
    
    # High accuracy requirement
    if accuracy_required == 'high':
        return 'accurate'
    
    # Default recommendation
    return 'auto'


def list_modes() -> List[str]:
    """Get list of available metamodel modes."""
    return list(METAMODEL_MODES.keys())


def validate_metamodel_config(config: Dict[str, Any]) -> bool:
    """
    Validate a metamodel configuration dictionary.
    
    Args:
        config: Configuration to validate
        
    Returns:
        True if valid
        
    Raises:
        ValueError: If configuration is invalid
    """
    if not config:
        return True  # None/empty config is valid (means no metamodel)
    
    required_keys = ['enabled', 'type']
    for key in required_keys:
        if key not in config:
            raise ValueError(f"Missing required key: {key}")
    
    if config['enabled']:
        # Check other required keys when enabled
        strategy_keys = ['acquisition_strategy', 'acquisition_function']
        for key in strategy_keys:
            if key not in config:
                raise ValueError(f"Missing required key for enabled metamodel: {key}")
    
    # Validate acquisition strategy
    valid_strategies = ['all_actual', 'all_metamodel', 'mixed', 'adaptive', 'uncertainty', 'periodic']
    if 'acquisition_strategy' in config and config['acquisition_strategy'] not in valid_strategies:
        raise ValueError(f"Invalid acquisition_strategy: {config['acquisition_strategy']}")
    
    # Validate acquisition function
    valid_functions = ['expected_improvement', 'probability_of_improvement', 'upper_confidence_bound']
    if 'acquisition_function' in config and config['acquisition_function'] not in valid_functions:
        raise ValueError(f"Invalid acquisition_function: {config['acquisition_function']}")
    
    return True