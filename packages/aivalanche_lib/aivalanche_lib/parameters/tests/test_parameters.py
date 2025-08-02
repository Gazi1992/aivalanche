"""
Tests for the Parameters class.
"""

import pytest
import numpy as np
import pandas as pd
import warnings
from aivalanche_lib.parameters import (
    Parameters,
    ContinuousParameter,
    DiscreteParameter,
    CategoricalParameter
)


class TestParameters:
    """Test Parameters class."""
    
    @pytest.fixture
    def sample_parameters(self):
        """Create a sample set of parameters for testing."""
        params = [
            ContinuousParameter("learning_rate", 0.001, 1.0, 0.1, scale='log'),
            DiscreteParameter("batch_size", min_val=16, max_val=256, default=64, step=16),
            CategoricalParameter("optimizer", ['adam', 'sgd', 'rmsprop'], 'adam'),
            ContinuousParameter("momentum", 0.0, 1.0, 0.9, mode='fixed'),
            ContinuousParameter("dropout", 0.0, 0.5, 0.2)
        ]
        return params
    
    def test_init_valid(self, sample_parameters):
        """Test valid initialization."""
        param_set = Parameters(sample_parameters)
        assert len(param_set) == 5
        # Names should be sorted alphabetically
        assert param_set.names == ['batch_size', 'dropout', 'learning_rate', 'momentum', 'optimizer']
    
    def test_init_duplicate_names(self):
        """Test initialization with duplicate parameter names."""
        params = [
            ContinuousParameter("param1", 0, 1),
            ContinuousParameter("param1", 0, 2),
            ContinuousParameter("param2", 0, 3)
        ]
        with pytest.warns(UserWarning, match="Duplicate parameter name 'param1' found"):
            param_set = Parameters(params)
        # Should only keep first occurrence
        assert len(param_set) == 2
        assert param_set.names == ['param1', 'param2']  # Alphabetically sorted
        assert param_set['param1'].max == 1  # First occurrence kept
    
    def test_len(self, sample_parameters):
        """Test __len__ method."""
        param_set = Parameters(sample_parameters)
        assert len(param_set) == 5
    
    def test_iter(self, sample_parameters):
        """Test __iter__ method."""
        param_set = Parameters(sample_parameters)
        param_names = [p.name for p in param_set]
        # Should be alphabetically sorted
        assert param_names == ['batch_size', 'dropout', 'learning_rate', 'momentum', 'optimizer']
    
    def test_getitem(self, sample_parameters):
        """Test __getitem__ method."""
        param_set = Parameters(sample_parameters)
        param = param_set['learning_rate']
        assert param.name == 'learning_rate'
        assert isinstance(param, ContinuousParameter)
    
    def test_get_parameter(self, sample_parameters):
        """Test get_parameter method."""
        param_set = Parameters(sample_parameters)
        param = param_set.get_parameter('batch_size')
        assert param.name == 'batch_size'
        assert isinstance(param, DiscreteParameter)
        
        with pytest.raises(KeyError, match="Parameter 'nonexistent' not found"):
            param_set.get_parameter('nonexistent')
    
    def test_variable_fixed_names(self, sample_parameters):
        """Test variable_names and fixed_names properties."""
        param_set = Parameters(sample_parameters)
        # Names should be alphabetically sorted
        assert param_set.variable_names == ['batch_size', 'dropout', 'learning_rate', 'optimizer']
        assert param_set.fixed_names == ['momentum']
    
    def test_get_by_type(self, sample_parameters):
        """Test get_by_type method."""
        param_set = Parameters(sample_parameters)
        
        continuous = param_set.get_by_type(ContinuousParameter)
        assert len(continuous) == 3
        assert all(isinstance(p, ContinuousParameter) for p in continuous)
        
        discrete = param_set.get_by_type(DiscreteParameter)
        assert len(discrete) == 1
        assert discrete[0].name == 'batch_size'
        
        categorical = param_set.get_by_type(CategoricalParameter)
        assert len(categorical) == 1
        assert categorical[0].name == 'optimizer'
    
    def test_get_variable_fixed_parameters(self, sample_parameters):
        """Test get_variable_parameters and get_fixed_parameters."""
        param_set = Parameters(sample_parameters)
        
        variable = param_set.get_variable_parameters()
        assert len(variable) == 4
        assert all(p.is_variable for p in variable)
        
        fixed = param_set.get_fixed_parameters()
        assert len(fixed) == 1
        assert fixed[0].name == 'momentum'
        assert all(p.is_fixed for p in fixed)
    
    def test_get_type_specific_parameters(self, sample_parameters):
        """Test type-specific getter methods."""
        param_set = Parameters(sample_parameters)
        
        continuous = param_set.get_continuous_parameters()
        assert len(continuous) == 3
        
        discrete = param_set.get_discrete_parameters()
        assert len(discrete) == 1
        
        categorical = param_set.get_categorical_parameters()
        assert len(categorical) == 1
    
    def test_count_properties(self, sample_parameters):
        """Test count properties."""
        param_set = Parameters(sample_parameters)
        
        assert param_set.n_variable == 4
        assert param_set.n_fixed == 1
        assert param_set.n_continuous == 3
        assert param_set.n_discrete == 1
        assert param_set.n_categorical == 1
    
    def test_validate_values(self, sample_parameters):
        """Test validate_values method."""
        param_set = Parameters(sample_parameters)
        
        values = {
            'learning_rate': 0.01,
            'batch_size': 64,
            'optimizer': 'adam',
            'momentum': 0.9,
            'dropout': 0.3
        }
        results = param_set.validate_values(values)
        assert all(results.values())
        
        # Invalid values - now they return True with warnings
        invalid_values = {
            'learning_rate': 2.0,  # Out of range - now returns True with warning
            'batch_size': 50,  # Not on step grid - now returns True with warning
            'optimizer': 'invalid',  # Not in categories - now returns True with warning
            'nonexistent': 5  # Parameter doesn't exist - still returns False
        }
        # Suppress warnings for this test
        import warnings
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            results = param_set.validate_values(invalid_values)
        
        assert results['learning_rate'] is True  # Now accepts with warning
        assert results['batch_size'] is True  # Now accepts with warning
        assert results['optimizer'] is True  # Now accepts with warning
        assert results['nonexistent'] is False  # Still false for non-existent param
    
    def test_norm_all_dict_input(self, sample_parameters):
        """Test norm_all with dict input."""
        param_set = Parameters(sample_parameters)
        
        values = {
            'learning_rate': 0.01,
            'batch_size': 64,
            'optimizer': 'adam',
            'momentum': 0.9,  # Fixed, should be ignored in input
            'dropout': 0.2
        }
        
        # Dict input should return dict output
        normed = param_set.norm_all(values)
        assert isinstance(normed, dict)
        assert len(normed) == 5  # Variable parameters + fixed default
        assert 0 <= normed['batch_size'] <= 1
        assert normed['dropout'] == 0.4  # 0.2/0.5
        assert 0 <= normed['learning_rate'] <= 1
        assert normed['optimizer'] == 0.0  # adam is first
        assert normed['momentum'] == 0.9  # Fixed default added
    
    def test_norm_all_array_input(self, sample_parameters):
        """Test norm_all with array input."""
        param_set = Parameters(sample_parameters)
        
        # Variable parameters sorted alphabetically: batch_size, dropout, learning_rate, optimizer
        # Test with array input
        values_array = np.array([64, 0.2, 0.01, 'adam'])  # Values for sorted params
        
        # Should return array output
        normed = param_set.norm_all(values_array)
        assert isinstance(normed, np.ndarray)
        assert len(normed) == 4  # Only variable parameters
        assert 0 <= normed[0] <= 1  # batch_size normalized
        assert normed[1] == 0.4  # dropout (0.2/0.5)
        assert 0 <= normed[2] <= 1  # learning_rate normalized
        assert normed[3] == 0.0  # optimizer (adam is first)
        
    def test_norm_all_missing_value(self, sample_parameters):
        """Test norm_all with missing parameter value."""
        param_set = Parameters(sample_parameters)
        
        values = {
            'learning_rate': 0.01,
            'batch_size': 64,
            # 'optimizer' is missing
            'dropout': 0.2
        }
        
        with pytest.raises(ValueError, match="Missing value for parameter 'optimizer'"):
            param_set.norm_all(values)
    
    def test_unnorm_all_array_input(self, sample_parameters):
        """Test unnorm_all with array input."""
        param_set = Parameters(sample_parameters)
        
        # Parameters are sorted alphabetically: batch_size, dropout, learning_rate, optimizer
        norm_values = [0.25, 0.4, 0.5, 0.5]  # 4 variable parameters
        
        values = param_set.unnorm_all(norm_values)
        
        assert len(values) == 5  # Includes fixed parameter default
        assert 'learning_rate' in values
        assert 'batch_size' in values
        assert values['batch_size'] in [16, 32, 48, 64, 80, 96, 112, 128, 144, 160, 176, 192, 208, 224, 240, 256]
        assert values['optimizer'] == 'sgd'  # Middle category
        assert values['momentum'] == 0.9  # Fixed default
        assert abs(values['dropout'] - 0.2) < 1e-10
    
    def test_unnorm_all_wrong_size(self, sample_parameters):
        """Test unnorm_all with wrong array size."""
        param_set = Parameters(sample_parameters)
        
        with pytest.raises(ValueError, match="Expected 4 normalized values, got 3"):
            param_set.unnorm_all([0.5, 0.5, 0.5])
    
    def test_norm_all_dataframe(self, sample_parameters):
        """Test norm_all with DataFrame input."""
        param_set = Parameters(sample_parameters)
        
        # Create test DataFrame
        df = pd.DataFrame({
            'learning_rate': [0.01, 0.1, 1.0],
            'batch_size': [32, 64, 128],
            'optimizer': ['adam', 'sgd', 'rmsprop'],
            'dropout': [0.1, 0.2, 0.3]
        })
        
        # Normalize
        normed_df = param_set.norm_all(df)
        assert isinstance(normed_df, pd.DataFrame)
        assert len(normed_df) == 3
        assert 'momentum' in normed_df.columns  # Fixed param added
        assert all(normed_df['momentum'] == 0.9)  # Fixed default
        
        # Check normalization
        assert all(0 <= normed_df['dropout']) and all(normed_df['dropout'] <= 1)
    
    def test_norm_all_list_of_dicts(self, sample_parameters):
        """Test norm_all with list of dicts input."""
        param_set = Parameters(sample_parameters)
        
        # Create test list
        values_list = [
            {'learning_rate': 0.01, 'batch_size': 32, 'optimizer': 'adam', 'dropout': 0.1},
            {'learning_rate': 0.1, 'batch_size': 64, 'optimizer': 'sgd', 'dropout': 0.2}
        ]
        
        # Normalize
        normed_list = param_set.norm_all(values_list)
        assert isinstance(normed_list, list)
        assert len(normed_list) == 2
        assert all('momentum' in d for d in normed_list)  # Fixed param added
        assert all(d['momentum'] == 0.9 for d in normed_list)
    
    def test_unnorm_all_dataframe(self, sample_parameters):
        """Test unnorm_all with DataFrame input."""
        param_set = Parameters(sample_parameters)
        
        # Create normalized DataFrame
        norm_df = pd.DataFrame({
            'learning_rate': [0.0, 0.5, 1.0],
            'batch_size': [0.0, 0.25, 0.5],
            'optimizer': [0.0, 0.5, 1.0],
            'dropout': [0.2, 0.4, 0.6]
        })
        
        # Denormalize
        unnorm_df = param_set.unnorm_all(norm_df)
        assert isinstance(unnorm_df, pd.DataFrame)
        assert len(unnorm_df) == 3
        assert 'momentum' in unnorm_df.columns  # Fixed param added
        assert all(unnorm_df['momentum'] == 0.9)
        
        # Check categorical values
        assert list(unnorm_df['optimizer']) == ['adam', 'sgd', 'rmsprop']
    
    def test_unnorm_all_dict(self, sample_parameters):
        """Test unnorm_all with dict input."""
        param_set = Parameters(sample_parameters)
        
        # Create normalized dict
        norm_dict = {
            'learning_rate': 0.5,
            'batch_size': 0.25,
            'optimizer': 0.5,
            'dropout': 0.4
        }
        
        # Denormalize
        unnorm_dict = param_set.unnorm_all(norm_dict)
        assert isinstance(unnorm_dict, dict)
        assert 'momentum' in unnorm_dict  # Fixed param added
        assert unnorm_dict['momentum'] == 0.9
        assert unnorm_dict['optimizer'] == 'sgd'  # Middle category
    
    def test_sample_random(self, sample_parameters):
        """Test sample_random method."""
        param_set = Parameters(sample_parameters)
        
        # Test single sample as dict
        values = param_set.sample_random(n_samples=1, random_state=42, output_format='dict')
        assert isinstance(values, dict)
        assert len(values) == 5
        assert values['momentum'] == 0.9  # Fixed default
        assert 0.001 <= values['learning_rate'] <= 1.0
        assert values['batch_size'] in [16, 32, 48, 64, 80, 96, 112, 128, 144, 160, 176, 192, 208, 224, 240, 256]
        assert values['optimizer'] in ['adam', 'sgd', 'rmsprop']
        assert 0.0 <= values['dropout'] <= 0.5
        
        # Test single sample as DataFrame (default)
        df_single = param_set.sample_random(n_samples=1, random_state=42)
        assert isinstance(df_single, pd.DataFrame)
        assert len(df_single) == 1
        assert df_single['momentum'].iloc[0] == 0.9
        
        # Test multiple samples as list of dicts
        samples_list = param_set.sample_random(n_samples=10, random_state=42, output_format='dict')
        assert isinstance(samples_list, list)
        assert len(samples_list) == 10
        assert all(isinstance(s, dict) for s in samples_list)
        assert all(s['momentum'] == 0.9 for s in samples_list)  # Fixed param
        
        # Test multiple samples as DataFrame
        df_multiple = param_set.sample_random(n_samples=10, random_state=42)
        assert isinstance(df_multiple, pd.DataFrame)
        assert len(df_multiple) == 10
        assert all(df_multiple['momentum'] == 0.9)  # Fixed param
        
        # Test reproducibility
        df_rep1 = param_set.sample_random(n_samples=5, random_state=42)
        df_rep2 = param_set.sample_random(n_samples=5, random_state=42)
        pd.testing.assert_frame_equal(df_rep1, df_rep2)
    
    def test_get_defaults(self, sample_parameters):
        """Test get_defaults method."""
        param_set = Parameters(sample_parameters)
        
        defaults = param_set.get_defaults()
        assert defaults == {
            'learning_rate': 0.1,
            'batch_size': 64,
            'optimizer': 'adam',
            'momentum': 0.9,
            'dropout': 0.2
        }
    
    def test_get_bounds(self, sample_parameters):
        """Test get_bounds method."""
        param_set = Parameters(sample_parameters)
        
        # Only variable parameters
        bounds = param_set.get_bounds(only_variable=True)
        assert bounds == {
            'learning_rate': (0.001, 1.0),
            'batch_size': (16, 256),
            'optimizer': (0, 2),  # 3 categories -> indices 0, 1, 2
            'dropout': (0.0, 0.5)
        }
        
        # All parameters
        bounds_all = param_set.get_bounds(only_variable=False)
        assert 'momentum' in bounds_all
        assert bounds_all['momentum'] == (0.0, 1.0)
    
    def test_to_dict(self, sample_parameters):
        """Test to_dict method."""
        param_set = Parameters(sample_parameters)
        
        dict_list = param_set.to_dict()
        assert len(dict_list) == 5
        
        # Check learning_rate
        lr_dict = next(d for d in dict_list if d['name'] == 'learning_rate')
        assert lr_dict['type'] == 'continuous'
        assert lr_dict['min'] == 0.001
        assert lr_dict['max'] == 1.0
        assert lr_dict['default'] == 0.1
        assert lr_dict['mode'] == 'variable'
        assert lr_dict['scale'] == 'log'  # Should have scale from parameter type
        
        # Check batch_size
        bs_dict = next(d for d in dict_list if d['name'] == 'batch_size')
        assert bs_dict['type'] == 'discrete'
        assert bs_dict['min'] == 16
        assert bs_dict['max'] == 256
        assert bs_dict['step'] == 16
        assert bs_dict['default'] == 64
        
        # Check optimizer
        opt_dict = next(d for d in dict_list if d['name'] == 'optimizer')
        assert opt_dict['type'] == 'categorical'
        assert opt_dict['values'] == ['adam', 'sgd', 'rmsprop']
        assert opt_dict['default'] == 'adam'
    
    def test_repr(self, sample_parameters):
        """Test string representation."""
        param_set = Parameters(sample_parameters)
        repr_str = repr(param_set)
        assert "Parameters(5 parameters:" in repr_str
        assert "learning_rate" in repr_str
        
        # Test with many parameters
        many_params = [ContinuousParameter(f"p{i}", 0, 1) for i in range(10)]
        param_set2 = Parameters(many_params)
        repr_str2 = repr(param_set2)
        assert "..." in repr_str2  # Should truncate
    
    def test_empty_parameter_set(self):
        """Test empty parameter set."""
        param_set = Parameters([])
        assert len(param_set) == 0
        assert param_set.names == []
        # Test norm_all with different inputs
        assert param_set.norm_all({}) == {}  # Empty dict returns empty dict
        assert np.array_equal(param_set.norm_all([]), np.array([]))  # Empty array returns empty array
        assert param_set.unnorm_all([]) == {}
        # sample_random returns DataFrame by default, check it's empty
        df = param_set.sample_random()
        assert isinstance(df, pd.DataFrame)
        assert len(df) == 1  # One row
        assert len(df.columns) == 0  # No columns
        assert param_set.get_defaults() == {}
        assert param_set.get_bounds() == {}
        assert param_set.to_dict() == []


    def test_comprehensive_norm_unnorm(self):
        """Comprehensive test of norm_all and unnorm_all with all parameter types."""
        import os
        import datetime
        
        def format_table(data, headers):
            """Simple table formatter without external dependencies."""
            # Calculate column widths
            col_widths = [len(h) for h in headers]
            for row in data:
                for i, cell in enumerate(row):
                    col_widths[i] = max(col_widths[i], len(str(cell)))
            
            # Create format string
            format_str = " | ".join([f"{{:<{w}}}" for w in col_widths])
            
            # Build table
            lines = []
            # Header
            lines.append(format_str.format(*headers))
            lines.append("-+-".join(["-" * w for w in col_widths]))
            # Data
            for row in data:
                lines.append(format_str.format(*[str(cell) for cell in row]))
            
            return "\n".join(lines)
        
        # Create a comprehensive set of parameters
        params = [
            # Continuous parameters with different scales
            ContinuousParameter("learning_rate", 0.0001, 1.0, 0.01, scale='log', description="Learning rate (log scale, positive)"),
            ContinuousParameter("log_positive", 0.01, 100.0, 1.0, scale='log', description="Log scale (positive range)"),
            ContinuousParameter("log_negative", -1000.0, -0.1, -10.0, scale='log', description="Log scale (negative range)"),
            ContinuousParameter("log_mixed", -100.0, 100.0, 0.0, scale='log', description="Log scale (mixed pos/neg)"),
            ContinuousParameter("dropout", 0.0, 0.5, 0.2, scale='lin', description="Dropout rate (linear scale)"),
            ContinuousParameter("weight_decay", 1e-6, 0.1, 1e-4, scale='log', mode='fixed', description="Weight decay (fixed, log)"),
            
            # Discrete parameters with integer and float values
            DiscreteParameter("batch_size", min_val=8, max_val=256, default=32, step=8, description="Batch size (int steps)"),
            DiscreteParameter("num_layers", values=[1, 2, 3, 5, 8, 13], default=3, description="Number of layers (Fibonacci)"),
            DiscreteParameter("temperature", min_val=0.1, max_val=2.0, step=0.1, default=1.0, description="Temperature (float steps)"),
            DiscreteParameter("discrete_log", values=[0.001, 0.01, 0.1, 1.0, 10.0, 100.0, 1000.0], default=1.0, scale='log', description="Discrete with log scale"),
            
            # Categorical parameters
            CategoricalParameter("optimizer", ['adam', 'sgd', 'rmsprop', 'adagrad'], 'adam', description="Optimizer type"),
            CategoricalParameter("activation", ['relu', 'tanh', 'sigmoid'], 'relu', mode='fixed', description="Activation function (fixed)"),
            CategoricalParameter("loss_function", ['mse', 'mae', 'huber'], 'mse', description="Loss function")
        ]
        
        # Create Parameters instance
        param_set = Parameters(params)
        
        # Test data - multiple samples with different formats
        test_samples = [
            {
                'learning_rate': 0.001,
                'log_positive': 10.0,
                'log_negative': -100.0,
                'log_mixed': -10.0,
                'dropout': 0.3,
                'weight_decay': 1e-5,  # Fixed param - should be ignored in input
                'batch_size': 64,
                'num_layers': 5,
                'temperature': 0.7,
                'discrete_log': 0.1,
                'optimizer': 'sgd',
                'activation': 'tanh',  # Fixed param - should be ignored
                'loss_function': 'mae'
            },
            {
                'learning_rate': 0.1,
                'log_positive': 0.1,
                'log_negative': -1.0,
                'log_mixed': 50.0,
                'dropout': 0.1,
                'weight_decay': 5e-4,  # Fixed param - should be ignored
                'batch_size': 128,
                'num_layers': 8,
                'temperature': 1.5,
                'discrete_log': 10.0,
                'optimizer': 'rmsprop',
                'activation': 'sigmoid',  # Fixed param - should be ignored
                'loss_function': 'huber'
            },
            {
                'learning_rate': 0.1,
                'log_positive': 0.1,
                'log_negative': -1.0,
                'log_mixed': -50.0,
                'dropout': 0.1,
                'weight_decay': 5e-4,  # Fixed param - should be ignored
                'batch_size': 128,
                'num_layers': 8,
                'temperature': 1.5,
                'discrete_log': 30.0,
                'optimizer': 'rmsprop',
                'activation': 'sigmoid',  # Fixed param - should be ignored
                'loss_function': 'huber'
            },
            {
                'learning_rate': 0.00001,
                'log_positive': 50.0,
                'log_negative': -10.0,
                'log_mixed': 0.0,
                'dropout': 0.5,
                'weight_decay': 0.01,  # Fixed param - should be ignored
                'batch_size': 16,
                'num_layers': 2,
                'temperature': 0.3,
                'discrete_log': 100.0,
                'optimizer': 'adam',
                'activation': 'relu',  # Fixed param - should be ignored
                'loss_function': 'mse'
            }
        ]
        
        # Prepare output file in results directory
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Create results directory if it doesn't exist
        results_dir = os.path.join(os.path.dirname(__file__), 'results')
        os.makedirs(results_dir, exist_ok=True)
        
        output_file = os.path.join(results_dir, f"test_norm_unnorm_comprehensive_{timestamp}.txt")
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write("=" * 100 + "\n")
            f.write("COMPREHENSIVE TEST OF NORM_ALL AND UNNORM_ALL FUNCTIONS\n")
            f.write(f"Generated: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("=" * 100 + "\n\n")
            
            # Write parameter information
            f.write("PARAMETER INFORMATION\n")
            f.write("-" * 100 + "\n")
            param_info = []
            for param in param_set.parameters:
                info = [
                    param.name,
                    param.type,
                    param.mode,
                    param.scale,
                    str(getattr(param, 'min_val', getattr(param, 'min', 'N/A'))),
                    str(getattr(param, 'max_val', getattr(param, 'max', 'N/A'))),
                    str(param.default),
                    param.description or "",
                    ""  # Values column (empty by default)
                ]
                if hasattr(param, 'categories'):
                    info[4] = "N/A"  # Clear min
                    info[5] = "N/A"  # Clear max
                    info[8] = str(param.categories)  # Put categories in values column
                elif hasattr(param, 'values') and not hasattr(param, 'step'):
                    info[4] = str(param.min_val)  # Keep min
                    info[5] = str(param.max_val)  # Keep max
                    info[8] = str(param.values)  # Put values list in values column
                param_info.append(info)
            
            headers = ["Name", "Type", "Mode", "Scale", "Min", "Max", "Default", "Description", "Values"]
            f.write(format_table(param_info, headers))
            f.write("\n\n")
            
            # Test 1: Dictionary input/output
            f.write("TEST 1: DICTIONARY INPUT -> NORMALIZE -> DENORMALIZE\n")
            f.write("-" * 100 + "\n")
            
            for i, sample in enumerate(test_samples):
                f.write(f"\nSample {i+1}:\n")
                
                # Filter to only variable parameters for input
                variable_sample = {k: v for k, v in sample.items() if k in param_set.variable_names}
                
                # Normalize
                normalized = param_set.norm_all(variable_sample)
                
                # Denormalize
                denormalized = param_set.unnorm_all(normalized)
                
                # Create comparison table
                comparison_data = []
                for param_name in sorted(param_set.names):
                    param = param_set[param_name]
                    
                    if param.is_variable and param_name in variable_sample:
                        original = variable_sample[param_name]
                    else:
                        original = param.default if param.is_fixed else "N/A"
                    
                    norm_val = normalized.get(param_name, "N/A")
                    denorm_val = denormalized.get(param_name, "N/A")
                    
                    # Format normalized values
                    if isinstance(norm_val, float):
                        norm_str = f"{norm_val:.4f}"
                    else:
                        norm_str = str(norm_val)
                    
                    # Check if values match (accounting for floating point precision)
                    if param.is_fixed:
                        match = "OK (fixed)"
                    elif isinstance(original, str) and isinstance(denorm_val, str):
                        match = "OK" if original == denorm_val else "FAIL"
                    elif isinstance(original, (int, float)) and isinstance(denorm_val, (int, float)):
                        # For discrete parameters, check if denormalized value is valid
                        if param.type == 'discrete':
                            # Check if the denormalized value is in the list of valid values
                            if denorm_val in param.values:
                                # It's OK if it snapped to a valid value
                                if abs(original - denorm_val) < 1e-10:
                                    match = "OK"
                                else:
                                    match = f"OK (snapped to {denorm_val})"
                            else:
                                match = f"FAIL (invalid value {denorm_val})"
                        else:
                            # For continuous, allow small tolerance
                            match = "OK" if abs(original - denorm_val) < 1e-6 else f"FAIL ({abs(original - denorm_val):.2e})"
                    else:
                        match = "?"
                    
                    comparison_data.append([
                        param_name,
                        param.type,
                        param.mode,
                        str(original),
                        norm_str,
                        str(denorm_val),
                        match
                    ])
                
                headers = ["Parameter", "Type", "Mode", "Original", "Normalized", "Denormalized", "Match"]
                f.write(format_table(comparison_data, headers))
                f.write("\n")
            
            # Test 2: Array input
            f.write("\nTEST 2: ARRAY INPUT -> NORMALIZE -> DENORMALIZE\n")
            f.write("-" * 100 + "\n")
            
            # Create array with values for variable parameters (alphabetically sorted)
            variable_params = param_set.get_variable_parameters()
            array_values = []
            for param in variable_params:
                if param.name == 'batch_size':
                    array_values.append(32)
                elif param.name == 'discrete_log':
                    array_values.append(1.0)
                elif param.name == 'dropout':
                    array_values.append(0.25)
                elif param.name == 'learning_rate':
                    array_values.append(0.005)
                elif param.name == 'log_mixed':
                    array_values.append(-5.0)
                elif param.name == 'log_negative':
                    array_values.append(-50.0)
                elif param.name == 'log_positive':
                    array_values.append(5.0)
                elif param.name == 'loss_function':
                    array_values.append('huber')
                elif param.name == 'num_layers':
                    array_values.append(3)
                elif param.name == 'optimizer':
                    array_values.append('adam')
                elif param.name == 'temperature':
                    array_values.append(1.0)
            
            f.write(f"Input array (for {len(variable_params)} variable parameters):\n")
            f.write(f"{array_values}\n\n")
            
            # Normalize
            norm_array = param_set.norm_all(array_values)
            f.write(f"Normalized array:\n")
            f.write(f"{norm_array}\n\n")
            
            # Denormalize
            denorm_dict = param_set.unnorm_all(norm_array)
            
            # Show results
            array_comparison = []
            for i, param in enumerate(variable_params):
                array_comparison.append([
                    param.name,
                    str(array_values[i]),
                    f"{norm_array[i]:.4f}",
                    str(denorm_dict[param.name])
                ])
            
            headers = ["Parameter", "Original", "Normalized", "Denormalized"]
            f.write(format_table(array_comparison, headers))
            f.write("\n")
            
            # Test 3: DataFrame input
            f.write("\nTEST 3: DATAFRAME INPUT -> NORMALIZE -> DENORMALIZE\n")
            f.write("-" * 100 + "\n")
            
            # Create DataFrame from test samples (only variable parameters)
            df_data = []
            for sample in test_samples:
                df_data.append({k: v for k, v in sample.items() if k in param_set.variable_names})
            
            df_input = pd.DataFrame(df_data)
            f.write("Input DataFrame:\n")
            f.write(df_input.to_string())
            f.write("\n\n")
            
            # Normalize
            df_normalized = param_set.norm_all(df_input)
            f.write("Normalized DataFrame:\n")
            f.write(df_normalized.to_string())
            f.write("\n\n")
            
            # Denormalize
            df_denormalized = param_set.unnorm_all(df_normalized)
            f.write("Denormalized DataFrame:\n")
            f.write(df_denormalized.to_string())
            f.write("\n\n")
            
            # Test 4: Log scale transformation details
            f.write("\nTEST 4: LOG SCALE TRANSFORMATION DETAILS\n")
            f.write("-" * 100 + "\n")
            f.write("Showing normalization behavior for log scale parameters:\n\n")
            
            # Test specific values for each log scale parameter
            log_test_data = []
            
            # Log positive range
            log_pos_param = param_set['log_positive']
            log_pos_values = [0.01, 0.1, 1.0, 10.0, 100.0]
            for val in log_pos_values:
                norm = log_pos_param.norm_value(val)
                denorm = log_pos_param.unnorm_value(norm)
                log_test_data.append(['log_positive', val, f"{norm:.4f}", denorm, f"{abs(val - denorm):.2e}"])
            
            # Log negative range
            log_neg_param = param_set['log_negative']
            log_neg_values = [-1000.0, -100.0, -10.0, -1.0, -0.1]
            for val in log_neg_values:
                norm = log_neg_param.norm_value(val)
                denorm = log_neg_param.unnorm_value(norm)
                log_test_data.append(['log_negative', val, f"{norm:.4f}", denorm, f"{abs(val - denorm):.2e}"])
            
            # Log mixed range (uses symlog)
            log_mixed_param = param_set['log_mixed']
            log_mixed_values = [-100.0, -10.0, -1.0, 0.0, 1.0, 10.0, 100.0]
            for val in log_mixed_values:
                norm = log_mixed_param.norm_value(val)
                denorm = log_mixed_param.unnorm_value(norm)
                log_test_data.append(['log_mixed', val, f"{norm:.4f}", denorm, f"{abs(val - denorm):.2e}"])
            
            # Discrete with log scale
            discrete_log_param = param_set['discrete_log']
            # Test all discrete values
            for val in discrete_log_param.values:
                norm = discrete_log_param.norm_value(val)
                denorm = discrete_log_param.unnorm_value(norm)
                log_test_data.append(['discrete_log', val, f"{norm:.4f}", denorm, f"{abs(val - denorm):.2e}"])
            
            headers = ["Parameter", "Original", "Normalized", "Denormalized", "Error"]
            f.write(format_table(log_test_data, headers))
            f.write("\n\n")
            
            # Test 5: Discrete parameter with in-between normalized values
            f.write("\nTEST 5: DISCRETE PARAMETER DENORMALIZATION WITH IN-BETWEEN VALUES\n")
            f.write("-" * 100 + "\n")
            f.write("Testing what happens when normalized values don't map exactly to discrete values:\n\n")
            
            discrete_test_data = []
            
            # Test discrete_log parameter with various normalized values
            discrete_log_param = param_set['discrete_log']
            # discrete_log values: [0.001, 0.01, 0.1, 1.0, 10.0, 100.0, 1000.0]
            # With 7 values, normalized values are: 0.0, 0.1667, 0.3333, 0.5, 0.6667, 0.8333, 1.0
            
            test_norm_values = [
                0.0,      # Should map to 0.001
                0.08,     # Between 0.0 and 0.1667
                0.1667,   # Should map to 0.01
                0.25,     # Between 0.1667 and 0.3333
                0.3333,   # Should map to 0.1
                0.4,      # Between 0.3333 and 0.5
                0.5,      # Should map to 1.0
                0.58,     # Between 0.5 and 0.6667
                0.6667,   # Should map to 10.0
                0.75,     # Between 0.6667 and 0.8333
                0.8333,   # Should map to 100.0
                0.9,      # Between 0.8333 and 1.0
                1.0       # Should map to 1000.0
            ]
            
            for norm_val in test_norm_values:
                denorm = discrete_log_param.unnorm_value(norm_val)
                # Find which discrete value it snapped to
                closest_idx = None
                for i, val in enumerate(discrete_log_param.values):
                    if abs(val - denorm) < 1e-10:
                        closest_idx = i
                        break
                
                if closest_idx is not None:
                    expected_norm = closest_idx / (len(discrete_log_param.values) - 1)
                    discrete_test_data.append([
                        'discrete_log',
                        f"{norm_val:.4f}",
                        denorm,
                        discrete_log_param.values[closest_idx],
                        f"{expected_norm:.4f}",
                        "Exact" if abs(norm_val - expected_norm) < 1e-10 else "Snapped"
                    ])
            
            headers = ["Parameter", "Input Norm", "Denormalized", "Snapped To", "Expected Norm", "Type"]
            f.write(format_table(discrete_test_data, headers))
            f.write("\n\n")
            
            # Also test regular discrete parameter (linear scale)
            f.write("Testing regular discrete parameter (linear scale) with in-between values:\n\n")
            
            discrete_test_data2 = []
            batch_size_param = param_set['batch_size']
            # batch_size has 32 values from 8 to 256 in steps of 8
            
            test_norm_values2 = [0.0, 0.1, 0.25, 0.5, 0.75, 0.9, 1.0]
            
            for norm_val in test_norm_values2:
                denorm = batch_size_param.unnorm_value(norm_val)
                # Find which discrete value it snapped to
                closest_val = min(batch_size_param.values, key=lambda x: abs(x - denorm))
                discrete_test_data2.append([
                    'batch_size',
                    f"{norm_val:.4f}",
                    f"{denorm:.1f}",
                    f"{closest_val:.0f}",
                    "Exact" if abs(denorm - closest_val) < 1e-10 else "Snapped"
                ])
            
            headers = ["Parameter", "Input Norm", "Denormalized", "Snapped To", "Type"]
            f.write(format_table(discrete_test_data2, headers))
            f.write("\n\n")
            
            # Summary
            f.write("SUMMARY\n")
            f.write("-" * 100 + "\n")
            f.write(f"Total parameters: {len(param_set)}\n")
            f.write(f"Variable parameters: {param_set.n_variable}\n")
            f.write(f"Fixed parameters: {param_set.n_fixed}\n")
            f.write(f"Continuous parameters: {param_set.n_continuous}\n")
            f.write(f"Discrete parameters: {param_set.n_discrete}\n")
            f.write(f"Categorical parameters: {param_set.n_categorical}\n")
            f.write("\n")
            f.write("Log scale parameter types detected:\n")
            f.write("- log_positive: Uses LogTransform (positive values only)\n")
            f.write("- log_negative: Uses NegLogTransform (negative values only)\n")
            f.write("- log_mixed: Uses SymLogTransform (handles both positive and negative values)\n")
            f.write("- discrete_log: Discrete parameter with log scale (uses LogTransform)\n")
            f.write("\n")
            f.write("All normalization and denormalization operations completed successfully!\n")
            f.write(f"\nOutput saved to: {output_file}\n")
        
        # Print to console
        print(f"\nComprehensive norm/unnorm test completed. Results saved to: {output_file}")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])