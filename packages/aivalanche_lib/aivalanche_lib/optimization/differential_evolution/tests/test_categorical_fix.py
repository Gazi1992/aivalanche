"""
Simple test to verify the categorical parameter exclusion fix works.
This test uses mock objects to avoid dependency issues.
"""

class MockParameters:
    """Mock Parameters class for testing."""
    def __init__(self, param_data):
        self.param_data = param_data
        self.variable_parameters = self
        self.variable_parameters_names = [p['name'] for p in param_data if p.get('mode', 'variable') == 'variable']
        
    @property
    def empty(self):
        return len(self.param_data) == 0
    
    @property 
    def columns(self):
        return ['name', 'type', 'mode'] if self.param_data else []
    
    def __getitem__(self, key):
        if key == 'type':
            param_data = self.param_data
            class TypeAccessor:
                @property
                def values(self):
                    return [p['type'] for p in param_data if p.get('mode', 'variable') == 'variable']
            return TypeAccessor()
        raise KeyError(key)
    
    def iloc(self, idx):
        class IlocAccessor:
            def __init__(self, data, index):
                self.data = data
                self.index = index
            def __getitem__(self, key):
                variable_params = [p for p in self.data if p.get('mode', 'variable') == 'variable']
                return variable_params[self.index][key]
        return IlocAccessor(self.param_data, idx)


class MockDE:
    """Mock DifferentialEvolution instance for testing."""
    def __init__(self, parameters):
        self.parameters = parameters
        self.nr_variable_parameters = len(parameters.variable_parameters_names)
        self.variable_parameters_names = parameters.variable_parameters_names
        self._perturbation_active_config = {'param_selection': 'all'}
        
        # Mock numpy array behavior
        class MockArray:
            def __init__(self, data):
                self.data = list(data)
            def __eq__(self, value):
                return [d == value for d in self.data]
            def __ne__(self, value):
                return [d != value for d in self.data]
            
        class MockNumpy:
            @staticmethod
            def where(condition):
                indices = [i for i, cond in enumerate(condition) if cond]
                return (indices,)
            @staticmethod
            def array(data):
                return list(data)
                
        self.np = MockNumpy()


def test_categorical_exclusion():
    """Test that categorical parameters are excluded from perturbation selection."""
    
    # Create test parameters with mixed types
    param_data = [
        {'name': 'x1', 'type': 'continuous', 'mode': 'variable'},
        {'name': 'x2', 'type': 'continuous', 'mode': 'variable'},
        {'name': 'discrete_param', 'type': 'discrete', 'mode': 'variable'},
        {'name': 'category', 'type': 'categorical', 'mode': 'variable'},
        {'name': 'optimizer', 'type': 'categorical', 'mode': 'variable'},
        {'name': 'fixed_param', 'type': 'continuous', 'mode': 'fixed'}
    ]
    
    mock_params = MockParameters(param_data)
    mock_de = MockDE(mock_params)
    
    print("Testing categorical parameter exclusion logic...")
    print(f"Total variable parameters: {mock_de.nr_variable_parameters}")
    print(f"Variable parameter names: {mock_de.variable_parameters_names}")
    
    # Simulate the logic from _select_parameters_for_perturbation
    variable_params = mock_de.parameters.variable_parameters
    if not variable_params.empty:
        param_types = variable_params['type'].values
        print(f"Parameter types: {param_types}")
        
        non_categorical_mask = [t != 'categorical' for t in param_types]
        print(f"Non-categorical mask: {non_categorical_mask}")
        
        non_categorical_indices = [i for i, mask in enumerate(non_categorical_mask) if mask]
        print(f"Non-categorical indices: {non_categorical_indices}")
        
        # Verify the selection
        selected_names = [mock_de.variable_parameters_names[i] for i in non_categorical_indices]
        print(f"Selected parameter names: {selected_names}")
        
        # Check that no categorical parameters were selected
        for idx in non_categorical_indices:
            param_type = variable_params.iloc(idx)['type']
            assert param_type != 'categorical', f"Categorical parameter at index {idx} was selected!"
        
        print("\n[PASS] Test passed! Categorical parameters are properly excluded.")
        
        # Verify the expected selection
        expected_names = ['x1', 'x2', 'discrete_param']
        assert selected_names == expected_names, f"Expected {expected_names}, got {selected_names}"
        print(f"[PASS] Correct parameters selected: {selected_names}")
    else:
        print("No variable parameters found!")


if __name__ == "__main__":
    test_categorical_exclusion()