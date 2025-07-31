"""
Perturbation modes and configurations for Differential Evolution.

This module provides predefined perturbation configurations for different scenarios,
making it easier to enable and configure the perturbation system for escaping local minima.
"""

from typing import Dict, Any, Optional, List

# Predefined perturbation configurations
PERTURBATION_MODES = {
    'off': None,  # No perturbation
    
    'very_light': {
        'trigger_ratio': 0.9,  # Trigger very late (90% of max_iter_without_improvement)
        'param_selection': 'smart',
        'param_ratio': (0.05, 0.15),  # Very few parameters (5-15%)
        'population_ratio': (0.05, 0.1),  # Very small population fraction
        'scale': 'adaptive_weak',  # Gentle perturbations
        'memory_enabled': True,
        'cooldown_ratio': 0.4,  # Long cooldown
        'sigma_threshold': 0.001  # Very tight convergence required
    },
    
    'light': {
        'trigger_ratio': 0.8,  # Trigger late (80% of max_iter_without_improvement)
        'param_selection': 'smart',
        'param_ratio': (0.1, 0.2),  # Few parameters (10-20%)
        'population_ratio': (0.1, 0.2),  # Small population fraction
        'scale': 'adaptive_weak',
        'memory_enabled': True,
        'cooldown_ratio': 0.3,
        'sigma_threshold': 0.005
    },
    
    'conservative': {
        'trigger_ratio': 0.7,  # Trigger at 70% of stagnation limit
        'param_selection': 'smart',
        'param_ratio': (0.15, 0.25),  # Moderate parameters
        'population_ratio': (0.15, 0.25),
        'scale': (0.5, 1.0),  # Conservative scale range
        'memory_enabled': True,
        'cooldown_ratio': 0.25,
        'sigma_threshold': 0.01
    },
    
    'auto': {
        'trigger_ratio': 0.5,  # Balanced trigger (50% of max_iter_without_improvement)
        'param_selection': 'smart',
        'param_ratio': (0.2, 0.4),  # Balanced parameter selection
        'population_ratio': (0.2, 0.4),
        'scale': 'adaptive',  # Standard adaptive scaling
        'memory_enabled': True,
        'cooldown_ratio': 0.2,
        'sigma_threshold': 0.02
    },
    
    'moderate': {
        'trigger_ratio': 0.4,  # Trigger earlier
        'param_selection': 'smart',
        'param_ratio': (0.25, 0.45),  # More parameters
        'population_ratio': (0.25, 0.45),
        'scale': 'adaptive',
        'memory_enabled': True,
        'cooldown_ratio': 0.15,
        'sigma_threshold': 0.03
    },
    
    'strong': {
        'trigger_ratio': 0.3,  # Trigger early (30% of stagnation)
        'param_selection': 'smart',
        'param_ratio': (0.3, 0.5),  # Many parameters
        'population_ratio': (0.3, 0.5),  # Large population fraction
        'scale': 'adaptive_strong',
        'memory_enabled': True,
        'cooldown_ratio': 0.1,
        'sigma_threshold': 0.05
    },
    
    'aggressive': {
        'trigger_ratio': 0.2,  # Trigger very early
        'param_selection': 'variance',  # Focus on high variance params
        'param_ratio': (0.4, 0.6),  # Very many parameters
        'population_ratio': (0.4, 0.6),
        'scale': 'adaptive_strong',
        'memory_enabled': True,
        'cooldown_ratio': 0.05,  # Very short cooldown
        'sigma_threshold': 0.1  # Loose convergence threshold
    },
    
    'very_aggressive': {
        'trigger_ratio': 0.1,  # Trigger almost immediately
        'param_selection': 'variance',
        'param_ratio': (0.5, 0.8),  # Most parameters
        'population_ratio': (0.5, 0.8),  # Most of population
        'scale': (2.0, 5.0),  # Large fixed scale
        'memory_enabled': True,
        'cooldown_ratio': 0.02,  # Almost no cooldown
        'sigma_threshold': 0.2  # Very loose convergence
    },
    
    'random_walk': {
        'trigger_ratio': 0.5,
        'param_selection': 'random',  # Random parameter selection
        'param_ratio': 0.3,  # Fixed ratio
        'population_ratio': 0.3,
        'scale': (0.1, 2.0),  # Wide scale range
        'memory_enabled': False,  # No memory
        'cooldown_ratio': 0.1,
        'sigma_threshold': 0.05
    },
    
    'smart_escape': {
        'trigger_ratio': 0.4,
        'param_selection': 'smart',  # Smart selection with memory
        'param_ratio': (0.2, 0.5),  # Adaptive range
        'population_ratio': (0.1, 0.3),  # Focus on few individuals
        'scale': 'adaptive',
        'memory_enabled': True,
        'cooldown_ratio': 0.2,
        'sigma_threshold': 0.01,
        # Additional smart escape features
        'memory_decay': 0.1,  # Forget old perturbation history
        'success_amplification': 2.0  # Amplify successful perturbations
    },
    
    'periodic': {
        'trigger_ratio': 0.0,  # Always ready to trigger
        'param_selection': 'variance',
        'param_ratio': (0.2, 0.4),
        'population_ratio': (0.2, 0.4),
        'scale': 'adaptive',
        'memory_enabled': False,
        'cooldown_ratio': 0.5,  # Long cooldown for periodic behavior
        'sigma_threshold': 1.0,  # Effectively disabled
        'periodic_interval': 50  # Trigger every N iterations regardless
    },
    
    'emergency': {
        'trigger_ratio': 0.9,  # Only in extreme stagnation
        'param_selection': 'all',  # Perturb all parameters
        'param_ratio': 1.0,  # All parameters
        'population_ratio': (0.8, 1.0),  # Almost entire population
        'scale': (5.0, 10.0),  # Extreme perturbation
        'memory_enabled': False,
        'cooldown_ratio': 0.5,  # Long recovery period
        'sigma_threshold': 0.0001  # Only when extremely converged
    },
    
    'custom': {
        # Placeholder for user-defined configuration
        # User must provide complete configuration
    }
}


def get_perturbation_config(mode: str, custom_config: Optional[Dict[str, Any]] = None) -> Optional[Dict[str, Any]]:
    """
    Get perturbation configuration for a given mode.
    
    Args:
        mode: Perturbation mode name
        custom_config: Custom configuration (required for 'custom' mode)
        
    Returns:
        Perturbation configuration dictionary or None for 'off' mode
    """
    if mode not in PERTURBATION_MODES:
        raise ValueError(f"Unknown perturbation mode: {mode}. Available modes: {list(PERTURBATION_MODES.keys())}")
    
    if mode == 'off':
        return None
    
    if mode == 'custom':
        if not custom_config:
            raise ValueError("Custom mode requires a custom_config dictionary")
        return custom_config
    
    # Return copy of predefined configuration
    config = PERTURBATION_MODES[mode].copy()
    
    # Override with any custom settings
    if custom_config:
        config.update(custom_config)
    
    return config


def get_mode_description(mode: str) -> str:
    """Get a description of what a perturbation mode does."""
    descriptions = {
        'off': "No perturbation. Population evolves naturally without forced diversity.",
        'very_light': "Minimal perturbation only in extreme stagnation. Barely noticeable impact.",
        'light': "Gentle perturbations late in stagnation. Good for smooth landscapes.",
        'conservative': "Careful perturbations with moderate strength. Safe choice for sensitive problems.",
        'auto': "Balanced perturbation strategy. Good general purpose choice.",
        'moderate': "More frequent perturbations with moderate strength. Good for multimodal problems.",
        'strong': "Strong perturbations triggered early. Good for highly multimodal landscapes.",
        'aggressive': "Very strong and frequent perturbations. For difficult optimization landscapes.",
        'very_aggressive': "Extreme perturbations. Use when other modes fail to escape local minima.",
        'random_walk': "Random perturbations without memory. Adds stochastic exploration.",
        'smart_escape': "Intelligent escape strategy using memory and success amplification.",
        'periodic': "Regular perturbations at fixed intervals. Good for preventing premature convergence.",
        'emergency': "Last resort massive perturbation. Only triggers in extreme stagnation.",
        'custom': "User-defined configuration. Full control over all perturbation parameters."
    }
    return descriptions.get(mode, f"No description available for mode: {mode}")


def suggest_perturbation_mode(problem_type: Optional[str] = None,
                             landscape: Optional[str] = None,
                             n_dim: Optional[int] = None,
                             convergence_speed: Optional[str] = None,
                             noise_level: Optional[str] = None) -> str:
    """
    Suggest a perturbation mode based on problem characteristics.
    
    Args:
        problem_type: Type of problem ('smooth', 'multimodal', 'highly_multimodal', 'rugged')
        landscape: Landscape characteristic ('convex', 'many_local_minima', 'deceptive')
        n_dim: Number of dimensions
        convergence_speed: Desired convergence speed ('fast', 'balanced', 'thorough')
        noise_level: Function noise level ('none', 'low', 'medium', 'high')
        
    Returns:
        Suggested perturbation mode
    """
    # High noise problems
    if noise_level in ['medium', 'high']:
        return 'conservative'
    
    # Problem type based suggestions
    if problem_type == 'smooth':
        return 'light'
    elif problem_type == 'highly_multimodal':
        return 'strong'
    elif problem_type == 'rugged':
        return 'aggressive'
    
    # Landscape based suggestions
    if landscape == 'convex':
        return 'very_light'
    elif landscape == 'many_local_minima':
        return 'moderate'
    elif landscape == 'deceptive':
        return 'smart_escape'
    
    # Convergence speed preferences
    if convergence_speed == 'fast':
        return 'light'
    elif convergence_speed == 'thorough':
        return 'strong'
    
    # High dimensional problems
    if n_dim and n_dim > 30:
        return 'moderate'
    
    # Default recommendation
    return 'auto'


def list_modes() -> List[str]:
    """Get list of available perturbation modes."""
    return list(PERTURBATION_MODES.keys())


def validate_perturbation_config(config: Dict[str, Any]) -> bool:
    """
    Validate a perturbation configuration dictionary.
    
    Args:
        config: Configuration to validate
        
    Returns:
        True if valid
        
    Raises:
        ValueError: If configuration is invalid
    """
    if not config:
        return True  # None/empty config is valid (means no perturbation)
    
    required_keys = ['trigger_ratio', 'param_selection', 'param_ratio', 
                     'population_ratio', 'scale', 'memory_enabled', 
                     'cooldown_ratio', 'sigma_threshold']
    
    for key in required_keys:
        if key not in config:
            raise ValueError(f"Missing required key: {key}")
    
    # Validate param_selection
    valid_selections = ['random', 'variance', 'smart', 'all']
    if config['param_selection'] not in valid_selections:
        raise ValueError(f"Invalid param_selection: {config['param_selection']}")
    
    # Validate trigger_ratio
    if not 0 <= config['trigger_ratio'] <= 1:
        raise ValueError(f"trigger_ratio must be between 0 and 1, got {config['trigger_ratio']}")
    
    # Validate cooldown_ratio
    if not 0 <= config['cooldown_ratio'] <= 1:
        raise ValueError(f"cooldown_ratio must be between 0 and 1, got {config['cooldown_ratio']}")
    
    return True


def get_mode_comparison():
    """
    Get a DataFrame comparing all perturbation modes.
    
    Returns:
        DataFrame with mode characteristics
    """
    import pandas as pd
    
    data = []
    for mode, config in PERTURBATION_MODES.items():
        if mode in ['off', 'custom'] or config is None:
            continue
        
        row = {
            'Mode': mode,
            'Trigger': f"{config['trigger_ratio']*100:.0f}%",
            'Params': str(config['param_ratio']),
            'Population': str(config['population_ratio']),
            'Scale': str(config['scale']),
            'Memory': '✓' if config['memory_enabled'] else '✗',
            'Cooldown': f"{config['cooldown_ratio']*100:.0f}%",
            'Sigma': config['sigma_threshold']
        }
        data.append(row)
    
    return pd.DataFrame(data)