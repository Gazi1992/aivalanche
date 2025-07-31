"""
Test that custom configurations properly override predefined mode settings.
"""

from aivalanche_lib.optimization.differential_evolution import (
    get_perturbation_config,
    get_refinement_config,
    get_metamodel_config
)


def test_perturbation_override():
    """Test perturbation mode override functionality."""
    print("\n" + "="*60)
    print("TESTING PERTURBATION MODE OVERRIDES")
    print("="*60)
    
    # Get base configuration
    base_config = get_perturbation_config('auto')
    print("\nBase 'auto' configuration:")
    for key, value in base_config.items():
        print(f"  {key}: {value}")
    
    # Override some settings
    custom_overrides = {
        'trigger_ratio': 0.7,  # Changed from 0.5
        'scale': 'adaptive_strong',  # Changed from 'adaptive'
        'new_parameter': 'test_value'  # Added new parameter
    }
    
    overridden_config = get_perturbation_config('auto', custom_overrides)
    print("\nOverridden configuration:")
    for key, value in overridden_config.items():
        print(f"  {key}: {value}")
    
    # Verify overrides
    assert overridden_config['trigger_ratio'] == 0.7, "trigger_ratio not overridden"
    assert overridden_config['scale'] == 'adaptive_strong', "scale not overridden"
    assert overridden_config['new_parameter'] == 'test_value', "new parameter not added"
    assert overridden_config['memory_enabled'] == True, "unchanged parameter modified"
    
    print("\n✓ Perturbation overrides work correctly!")


def test_refinement_override():
    """Test refinement mode override functionality."""
    print("\n" + "="*60)
    print("TESTING REFINEMENT MODE OVERRIDES")
    print("="*60)
    
    # Get base configuration
    base_config = get_refinement_config('moderate')
    print("\nBase 'moderate' configuration:")
    for key, value in base_config.items():
        print(f"  {key}: {value}")
    
    # Override some settings
    custom_overrides = {
        'max_iterations': 200,  # Changed from 100
        'trigger': 'both',  # Changed from 'on_stagnation'
        'options': {
            'gradient_tolerance': 1e-12,  # More strict
            'residual_type': 'vector'  # Changed from scalar
        }
    }
    
    overridden_config = get_refinement_config('moderate', custom_overrides)
    print("\nOverridden configuration:")
    for key, value in overridden_config.items():
        print(f"  {key}: {value}")
    
    # Note: Simple update() will replace the entire 'options' dict, not merge it
    assert overridden_config['max_iterations'] == 200, "max_iterations not overridden"
    assert overridden_config['trigger'] == 'both', "trigger not overridden"
    assert overridden_config['options']['gradient_tolerance'] == 1e-12, "gradient_tolerance not overridden"
    assert overridden_config['options']['residual_type'] == 'vector', "residual_type not overridden"
    
    print("\n✓ Refinement overrides work correctly!")


def test_metamodel_override():
    """Test metamodel mode override functionality."""
    print("\n" + "="*60)
    print("TESTING METAMODEL MODE OVERRIDES")
    print("="*60)
    
    # Get base configuration
    base_config = get_metamodel_config('auto')
    print("\nBase 'auto' configuration:")
    for key, value in base_config.items():
        print(f"  {key}: {value}")
    
    # Override some settings
    custom_overrides = {
        'update_frequency': 10,  # Changed from 5
        'exploration_ratio': 0.3,  # Changed from 0.2
        'verbose': True,  # Changed from False
        'model_config': {
            'kernel': 'rbf',  # Changed from 'matern'
            'alpha': 1e-8  # Changed from 1e-6
        }
    }
    
    overridden_config = get_metamodel_config('auto', custom_overrides)
    print("\nOverridden configuration:")
    for key, value in overridden_config.items():
        print(f"  {key}: {value}")
    
    # Verify overrides
    assert overridden_config['update_frequency'] == 10, "update_frequency not overridden"
    assert overridden_config['exploration_ratio'] == 0.3, "exploration_ratio not overridden"
    assert overridden_config['verbose'] == True, "verbose not overridden"
    assert overridden_config['acquisition_strategy'] == 'mixed', "unchanged parameter modified"
    
    print("\n✓ Metamodel overrides work correctly!")


def test_nested_override_limitation():
    """Demonstrate limitation with nested dictionary overrides."""
    print("\n" + "="*60)
    print("TESTING NESTED DICTIONARY OVERRIDE LIMITATION")
    print("="*60)
    
    # Get base configuration
    base_config = get_metamodel_config('auto')
    print("\nOriginal model_config:")
    print(f"  {base_config['model_config']}")
    
    # Try to override just one field in nested dict
    custom_overrides = {
        'model_config': {
            'alpha': 1e-10  # Only want to change this
        }
    }
    
    overridden_config = get_metamodel_config('auto', custom_overrides)
    print("\nAfter override - model_config:")
    print(f"  {overridden_config['model_config']}")
    
    print("\n⚠ WARNING: Simple update() replaces entire nested dictionaries!")
    print("  The 'kernel' and 'n_restarts_optimizer' fields were lost.")
    print("  For deep merging of nested configs, consider using a custom merge function.")


def demonstrate_proper_nested_override():
    """Show how to properly override nested configurations."""
    print("\n" + "="*60)
    print("PROPER WAY TO OVERRIDE NESTED CONFIGURATIONS")
    print("="*60)
    
    # Get base configuration
    base_config = get_metamodel_config('auto')
    
    # Method 1: Override the entire nested dict with all fields
    custom_overrides = {
        'model_config': {
            'kernel': base_config['model_config']['kernel'],  # Keep original
            'alpha': 1e-10,  # Change this
            'n_restarts_optimizer': base_config['model_config']['n_restarts_optimizer']  # Keep original
        }
    }
    
    overridden_config = get_metamodel_config('auto', custom_overrides)
    print("\nMethod 1 - Override entire nested dict:")
    print(f"  {overridden_config['model_config']}")
    
    # Method 2: Get config first, then modify nested fields
    config = get_metamodel_config('auto')
    config['model_config']['alpha'] = 1e-10  # Modify just what we need
    
    print("\nMethod 2 - Modify after getting config:")
    print(f"  {config['model_config']}")
    
    print("\n✓ Both methods preserve all nested fields!")


if __name__ == "__main__":
    # Test all three mode types
    test_perturbation_override()
    test_refinement_override()
    test_metamodel_override()
    
    # Demonstrate nested dict limitation
    test_nested_override_limitation()
    
    # Show proper way to handle nested overrides
    demonstrate_proper_nested_override()
    
    print("\n" + "="*60)
    print("ALL TESTS COMPLETED")
    print("="*60)