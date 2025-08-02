"""
Tests for IO functions.
"""

import pytest
import json
import pandas as pd
from pathlib import Path
import tempfile
from aivalanche_lib.parameters.io import read_json, read_csv, read_dict_list
from aivalanche_lib.parameters import (
    Parameters,
    ContinuousParameter,
    DiscreteParameter,
    CategoricalParameter
)


class TestIO:
    """Test IO functions."""
    
    @pytest.fixture
    def sample_json_data(self):
        """Sample parameter data in JSON format."""
        return [
            {
                "name": "learning_rate",
                "type": "continuous",
                "min": 0.001,
                "max": 1.0,
                "default": 0.1,
                "mode": "variable"
            },
            {
                "name": "batch_size",
                "type": "discrete",
                "min": 16,
                "max": 256,
                "step": 16,
                "default": 64,
                "mode": "variable"
            },
            {
                "name": "optimizer",
                "type": "categorical",
                "values": ["adam", "sgd", "rmsprop"],
                "default": "adam",
                "mode": "variable"
            },
            {
                "name": "momentum",
                "type": "continuous",
                "min": 0.0,
                "max": 1.0,
                "default": 0.9,
                "mode": "fixed"
            }
        ]
    
    @pytest.fixture
    def sample_csv_data(self):
        """Sample parameter data as CSV DataFrame."""
        return pd.DataFrame([
            {
                "name": "learning_rate",
                "type": "continuous",
                "min": 0.001,
                "max": 1.0,
                "default": 0.1,
                "mode": "variable"
            },
            {
                "name": "batch_size",
                "type": "discrete",
                "min": 16,
                "max": 256,
                "step": 16,
                "default": 64,
                "mode": "variable"
            },
            {
                "name": "optimizer",
                "type": "categorical",
                "values": "adam,sgd,rmsprop",  # CSV format: comma-separated
                "default": "adam",
                "mode": "variable"
            }
        ])
    
    def test_read_json_valid(self, sample_json_data):
        """Test reading valid JSON file."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(sample_json_data, f)
            temp_path = f.name
        
        try:
            param_set = read_json(temp_path)
            
            assert isinstance(param_set, Parameters)
            assert len(param_set) == 4
            
            # Check learning_rate
            lr = param_set['learning_rate']
            assert lr.name == 'learning_rate'
            assert isinstance(lr, ContinuousParameter)
            assert lr.min_val == 0.001
            assert lr.max_val == 1.0
            
            # Check batch_size
            bs = param_set['batch_size']
            assert isinstance(bs, DiscreteParameter)
            assert bs.min_val == 16
            assert bs.max_val == 256
            assert bs.values == [float(x) for x in range(16, 257, 16)]
            
            # Check optimizer
            opt = param_set['optimizer']
            assert isinstance(opt, CategoricalParameter)
            assert opt.categories == ['adam', 'sgd', 'rmsprop']
            
            # Check momentum
            mom = param_set['momentum']
            assert mom.mode == 'fixed'
            
        finally:
            Path(temp_path).unlink()
    
    def test_read_json_file_not_found(self):
        """Test reading non-existent JSON file."""
        with pytest.raises(FileNotFoundError):
            read_json('nonexistent.json')
    
    def test_read_json_invalid_format(self):
        """Test reading invalid JSON format."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            f.write('{"not": "a list"}')  # Should be a list
            temp_path = f.name
        
        try:
            with pytest.raises(ValueError, match="must contain a list"):
                read_json(temp_path)
        finally:
            Path(temp_path).unlink()
    
    def test_read_csv_valid(self, sample_csv_data):
        """Test reading valid CSV file."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            sample_csv_data.to_csv(f, index=False)
            temp_path = f.name
        
        try:
            param_set = read_csv(temp_path)
            
            assert isinstance(param_set, Parameters)
            assert len(param_set) == 3
            
            # Check categorical values were split correctly
            opt = param_set['optimizer']
            assert opt.categories == ['adam', 'sgd', 'rmsprop']
            
        finally:
            Path(temp_path).unlink()
    
    def test_read_csv_file_not_found(self):
        """Test reading non-existent CSV file."""
        with pytest.raises(FileNotFoundError):
            read_csv('nonexistent.csv')
    
    def test_read_dict_list_valid(self, sample_json_data):
        """Test creating Parameters from dict list."""
        param_set = read_dict_list(sample_json_data)
        
        assert isinstance(param_set, Parameters)
        assert len(param_set) == 4
        # Names should be sorted alphabetically
        assert param_set.names == ['batch_size', 'learning_rate', 'momentum', 'optimizer']
    
    def test_read_dict_list_missing_name(self):
        """Test dict list with missing name field."""
        data = [{"type": "continuous", "min": 0, "max": 1}]
        with pytest.raises(ValueError, match="missing 'name' field"):
            read_dict_list(data)
    
    def test_read_dict_list_missing_type(self):
        """Test dict list with missing type field - should default to continuous."""
        data = [{"name": "param1", "min": 0, "max": 1}]
        param_set = read_dict_list(data)
        
        # Should create a continuous parameter by default
        assert len(param_set) == 1
        param = param_set['param1']
        assert isinstance(param, ContinuousParameter)
        assert param.type == 'continuous'
    
    def test_read_dict_list_invalid_type(self):
        """Test dict list with invalid parameter type."""
        data = [{"name": "param1", "type": "invalid", "min": 0, "max": 1}]
        with pytest.raises(ValueError, match="Unknown parameter type"):
            read_dict_list(data)
    
    def test_read_dict_list_continuous_missing_bounds(self):
        """Test continuous parameter missing min/max."""
        data = [{"name": "param1", "type": "continuous", "default": 0.5}]
        with pytest.raises(ValueError, match="missing 'min' or 'max'"):
            read_dict_list(data)
    
    def test_read_dict_list_discrete_missing_bounds(self):
        """Test discrete parameter missing min/max."""
        data = [{"name": "param1", "type": "discrete", "step": 2}]
        with pytest.raises(ValueError, match="missing 'min' or 'max'"):
            read_dict_list(data)
    
    def test_read_dict_list_categorical_missing_values(self):
        """Test categorical parameter missing values."""
        data = [{"name": "param1", "type": "categorical", "default": "a"}]
        with pytest.raises(ValueError, match="missing 'values'"):
            read_dict_list(data)
    
    def test_read_dict_list_categorical_invalid_values(self):
        """Test categorical parameter with non-list values."""
        data = [{"name": "param1", "type": "categorical", "values": "not a list"}]
        with pytest.raises(ValueError, match="'values' must be a list"):
            read_dict_list(data)
    
    def test_read_dict_list_with_scale(self):
        """Test reading parameters with scale property."""
        data = [{
            "name": "param1",
            "type": "continuous",
            "min": 0.001,
            "max": 1000,
            "scale": "log"
        }]
        param_set = read_dict_list(data)
        
        param = param_set['param1']
        assert param.scale == 'log'
    
    def test_round_trip_json(self, sample_json_data):
        """Test reading and recreating parameters via JSON."""
        # Create parameter set from dict
        param_set1 = read_dict_list(sample_json_data)
        
        # Convert back to dict
        dict_data = param_set1.to_dict()
        
        # Create new parameter set from that dict
        param_set2 = read_dict_list(dict_data)
        
        # Should be equivalent
        assert len(param_set1) == len(param_set2)
        assert param_set1.names == param_set2.names
        
        for name in param_set1.names:
            p1 = param_set1[name]
            p2 = param_set2[name]
            assert p1.name == p2.name
            assert p1.mode == p2.mode
            assert type(p1) == type(p2)
    
    def test_defaults_and_modes(self):
        """Test default values for optional fields."""
        data = [{
            "name": "param1",
            "type": "continuous",
            "min": 0,
            "max": 1
            # No default, mode, or scale specified
        }]
        param_set = read_dict_list(data)
        
        param = param_set['param1']
        assert param.default == 0.5  # Midpoint
        assert param.mode == 'variable'  # Default mode
        # Scale will be auto-detected as 'lin' (ratio = 0, can't divide by zero)
        assert param.scale == 'lin'
    
    def test_missing_type_defaults_to_continuous(self):
        """Test that missing type field defaults to continuous."""
        data = [{
            "name": "param1",
            # No type specified
            "min": 0,
            "max": 10,
            "default": 5
        }]
        param_set = read_dict_list(data)
        
        param = param_set['param1']
        assert isinstance(param, ContinuousParameter)
        assert param.type == 'continuous'
        assert param.min_val == 0
        assert param.max_val == 10
        assert param.default == 5
    
    def test_discrete_float_from_json(self):
        """Test reading discrete parameters with float values."""
        data = [
            {
                "name": "learning_rate",
                "type": "discrete",
                "min": 0.001,
                "max": 0.1,
                "step": 0.01,
                "default": 0.01,
                "mode": "variable"
            },
            {
                "name": "dropout_rate",
                "type": "discrete",
                "values": [0.0, 0.1, 0.2, 0.3, 0.5],
                "default": 0.2,
                "mode": "variable"
            }
        ]
        
        param_set = read_dict_list(data)
        
        # Check learning_rate (range-based float discrete)
        lr = param_set['learning_rate']
        assert isinstance(lr, DiscreteParameter)
        assert lr.min_val == 0.001
        # max_val might be adjusted due to step size
        assert abs(lr.max_val - 0.1) < 0.01  # Within tolerance
        # Default might be adjusted to nearest valid value
        assert lr.default in lr.values
        assert abs(lr.default - 0.01) < 0.005  # Close to requested default
        assert all(isinstance(v, float) for v in lr.values)
        
        # Check dropout_rate (list-based float discrete)
        dr = param_set['dropout_rate']
        assert isinstance(dr, DiscreteParameter)
        assert dr.values == [0.0, 0.1, 0.2, 0.3, 0.5]
        assert dr.default == 0.2


if __name__ == "__main__":
    pytest.main([__file__, "-v"])