"""
Predefined refinement mode configurations for Differential Evolution.

This module provides various refinement strategies optimized for different
problem types and convergence scenarios.
"""

# Predefined refinement configurations
REFINEMENT_MODES = {
    'off': None,
    
    'auto': {
        'method': 'dls',
        'max_iterations': 50,
        'trigger': 'on_completion',  # When to apply refinement
        'options': {
            'initial_damping': 0.01,
            'damping_increase_factor': 10.0,
            'damping_decrease_factor': 0.1,
            'gradient_tolerance': 1e-8,
            'parameter_tolerance': 1e-8,
            'improvement_threshold': 1e-6,
            'jacobian_step_size': 1e-6,
            'residual_type': 'scalar',
            'boundary_handling': 'reflect'
        }
    },
    
    'light': {
        'method': 'dls',
        'max_iterations': 20,  # Quick polish
        'trigger': 'on_completion',
        'options': {
            'initial_damping': 0.001,  # Start aggressive
            'damping_increase_factor': 5.0,
            'damping_decrease_factor': 0.2,
            'gradient_tolerance': 1e-6,  # Looser tolerances
            'parameter_tolerance': 1e-6,
            'improvement_threshold': 1e-4,
            'jacobian_step_size': 1e-5,
            'residual_type': 'scalar',
            'trust_region_radius': 0.1,  # Limit step size
            'boundary_handling': 'clip'
        }
    },
    
    'moderate': {
        'method': 'dls',
        'max_iterations': 100,
        'trigger': 'on_stagnation',  # Apply when DE stagnates
        'stagnation_threshold': 50,  # Iterations without improvement
        'options': {
            'initial_damping': 0.01,
            'damping_increase_factor': 10.0,
            'damping_decrease_factor': 0.1,
            'gradient_tolerance': 1e-8,
            'parameter_tolerance': 1e-8,
            'improvement_threshold': 1e-6,
            'jacobian_step_size': 1e-6,
            'residual_type': 'scalar',
            'boundary_handling': 'reflect'
        }
    },
    
    'aggressive': {
        'method': 'dls',
        'max_iterations': 200,  # Thorough refinement
        'trigger': 'adaptive',  # Apply periodically
        'adaptive_interval': 100,  # Every N iterations
        'options': {
            'initial_damping': 0.1,  # Start conservative
            'damping_increase_factor': 20.0,
            'damping_decrease_factor': 0.05,
            'gradient_tolerance': 1e-10,  # Very tight tolerances
            'parameter_tolerance': 1e-10,
            'improvement_threshold': 1e-8,
            'max_iter_without_improvement': 50,
            'jacobian_step_size': 1e-8,
            'jacobian_step_size_relative': True,
            'residual_type': 'scalar',
            'use_qr_decomposition': True,
            'boundary_handling': 'penalty'  # Smooth boundaries
        }
    },
    
    'high_precision': {
        'method': 'dls',
        'max_iterations': 500,
        'trigger': 'both',  # On stagnation AND completion
        'stagnation_threshold': 30,
        'options': {
            'initial_damping': 1.0,  # Very conservative start
            'damping_increase_factor': 50.0,
            'damping_decrease_factor': 0.02,
            'min_damping': 0.01,  # Don't get too aggressive
            'gradient_tolerance': 1e-12,  # Ultra-tight tolerances
            'parameter_tolerance': 1e-12,
            'improvement_threshold': 1e-10,
            'max_iter_without_improvement': 100,
            'jacobian_step_size': 1e-10,
            'jacobian_step_size_relative': True,
            'residual_type': 'scalar',
            'use_qr_decomposition': True,
            'trust_region_radius': 0.01,  # Very small steps
            'boundary_handling': 'penalty'
        }
    },
    
    'curve_fitting': {
        'method': 'dls',
        'max_iterations': 100,
        'trigger': 'on_completion',
        'options': {
            'initial_damping': 0.01,
            'damping_increase_factor': 10.0,
            'damping_decrease_factor': 0.1,
            'gradient_tolerance': 1e-8,
            'parameter_tolerance': 1e-8,
            'improvement_threshold': 1e-6,
            'jacobian_step_size': 1e-6,
            'residual_type': 'vector',  # Important for fitting!
            'use_qr_decomposition': True,  # Better for overdetermined systems
            'boundary_handling': 'reflect'
        }
    },
    
    'multi_objective': {
        'method': 'dls',
        'max_iterations': 150,
        'trigger': 'on_stagnation',
        'stagnation_threshold': 40,
        'options': {
            'initial_damping': 0.1,
            'damping_increase_factor': 15.0,
            'damping_decrease_factor': 0.067,
            'gradient_tolerance': 1e-9,
            'parameter_tolerance': 1e-9,
            'improvement_threshold': 1e-7,
            'jacobian_step_size': 1e-7,
            'residual_type': 'vector',  # For multiple objectives
            'use_qr_decomposition': True,
            'boundary_handling': 'reflect'
        }
    },
    
    'sensitive': {
        'method': 'dls',
        'max_iterations': 100,
        'trigger': 'on_completion',
        'options': {
            'initial_damping': 10.0,  # Very conservative
            'damping_increase_factor': 100.0,  # Extreme caution
            'damping_decrease_factor': 0.01,
            'min_damping': 1.0,  # Stay conservative
            'max_damping': 1e6,
            'gradient_tolerance': 1e-8,
            'parameter_tolerance': 1e-10,
            'improvement_threshold': 1e-8,
            'jacobian_step_size': 1e-10,  # Tiny steps for derivatives
            'jacobian_step_size_relative': True,
            'residual_type': 'scalar',
            'trust_region_radius': 0.001,  # Very small trust region
            'boundary_handling': 'penalty'  # Smooth behavior near bounds
        }
    },
    
    'custom': {
        # Placeholder for user-defined configuration
        # User must provide all settings
    }
}


def get_refinement_config(mode: str, custom_config: dict = None) -> dict:
    """
    Get refinement configuration for a given mode.
    
    Args:
        mode: Refinement mode name
        custom_config: Custom configuration (only used for 'custom' mode)
        
    Returns:
        Dictionary with refinement configuration
    """
    if mode not in REFINEMENT_MODES:
        raise ValueError(f"Unknown refinement mode: '{mode}'. "
                        f"Available modes: {list(REFINEMENT_MODES.keys())}")
    
    if mode == 'off':
        return None
    
    if mode == 'custom':
        if custom_config is None:
            raise ValueError("custom_config must be provided for 'custom' mode")
        return custom_config
    
    return REFINEMENT_MODES[mode].copy()


def get_mode_description(mode: str) -> str:
    """
    Get a description of what each refinement mode does.
    
    Args:
        mode: Refinement mode name
        
    Returns:
        String description of the mode
    """
    descriptions = {
        'off': "No refinement applied",
        'auto': "Balanced refinement after DE converges. Good general purpose choice.",
        'light': "Quick polish with loose tolerances. Fast but less precise.",
        'moderate': "Applies refinement when DE stagnates. Good balance of speed and precision.",
        'aggressive': "Thorough refinement with tight tolerances. Slow but precise.",
        'high_precision': "Ultra-precise refinement for problems requiring extreme accuracy.",
        'curve_fitting': "Optimized for least squares fitting problems with vector residuals.",
        'multi_objective': "For problems with multiple objectives using vector residuals.",
        'sensitive': "Very conservative refinement for highly sensitive problems.",
        'custom': "User-defined refinement configuration."
    }
    
    return descriptions.get(mode, "Unknown mode")


def suggest_refinement_mode(problem_type: str = None, 
                           n_parameters: int = None,
                           precision_required: str = 'medium') -> str:
    """
    Suggest a refinement mode based on problem characteristics.
    
    Args:
        problem_type: Type of problem ('fitting', 'optimization', 'sensitive', etc.)
        n_parameters: Number of parameters
        precision_required: 'low', 'medium', 'high', 'ultra'
        
    Returns:
        Suggested refinement mode name
    """
    # Problem type suggestions
    if problem_type == 'fitting':
        return 'curve_fitting'
    elif problem_type == 'multi_objective':
        return 'multi_objective'
    elif problem_type == 'sensitive':
        return 'sensitive'
    
    # Precision-based suggestions
    if precision_required == 'low':
        return 'light'
    elif precision_required == 'medium':
        return 'auto'
    elif precision_required == 'high':
        return 'aggressive'
    elif precision_required == 'ultra':
        return 'high_precision'
    
    # Parameter count suggestions
    if n_parameters and n_parameters > 50:
        return 'moderate'  # More conservative for high dimensions
    
    # Default
    return 'auto'