"""
Tests for parameter type implementations.
"""

import pytest
import numpy as np
from aivalanche_lib.parameters.types import (
    ContinuousParameter,
    DiscreteParameter,
    CategoricalParameter
)


class TestContinuousParameter:
    """Test ContinuousParameter class."""
    
    def test_init_valid(self):
        """Test valid initialization."""
        param = ContinuousParameter("test", 0.0, 10.0, 5.0)
        assert param.name == "test"
        assert param.min_val == 0.0
        assert param.max_val == 10.0
        assert param.default == 5.0
        assert param.scale == 'lin'  # Default scale
    
    def test_init_default_none(self):
        """Test initialization with None default."""
        param = ContinuousParameter("test", 0.0, 10.0)
        assert param.default == 5.0  # Should be midpoint
    
    def test_init_invalid_range(self):
        """Test initialization with invalid range - should flip with warning."""
        with pytest.warns(UserWarning, match="min_val.*is greater than max_val.*will be flipped"):
            param = ContinuousParameter("test", 10.0, 5.0)
        assert param.min_val == 5.0
        assert param.max_val == 10.0
    
    def test_init_invalid_default(self):
        """Test initialization with out-of-range default - should clip with warning."""
        with pytest.warns(UserWarning, match="Default value.*is outside range.*will be clipped"):
            param = ContinuousParameter("test", 0.0, 10.0, 15.0)
        assert param.default == 10.0  # Clipped to max
            
        with pytest.warns(UserWarning, match="Default value.*is outside range.*will be clipped"):
            param = ContinuousParameter("test2", 0.0, 10.0, -5.0)
        assert param.default == 0.0  # Clipped to min
    
    def test_init_equal_min_max(self):
        """Test initialization with equal min and max - should warn."""
        with pytest.warns(UserWarning, match="min_val and max_val are equal"):
            param = ContinuousParameter("test", 5.0, 5.0)
        assert param.min_val == 5.0
        assert param.max_val == 5.0
        assert param.default == 5.0
    
    def test_validate(self):
        """Test value validation."""
        param = ContinuousParameter("test", 0.0, 10.0)
        assert param.validate(5.0) is True
        assert param.validate(0.0) is True
        assert param.validate(10.0) is True
        # Out of range values now accepted with warning
        with pytest.warns(UserWarning, match="outside range"):
            assert param.validate(-1.0) is True
        with pytest.warns(UserWarning, match="outside range"):
            assert param.validate(11.0) is True
        assert param.validate("not a number") is False
    
    def test_norm(self):
        """Test normalization."""
        param = ContinuousParameter("test", 0.0, 10.0)
        assert param.norm_value(0.0) == 0.0
        assert param.norm_value(10.0) == 1.0
        assert param.norm_value(5.0) == 0.5
        assert param.norm_value(2.5) == 0.25
        
        # Test with negative range
        param2 = ContinuousParameter("test2", -10.0, -5.0)
        assert param2.norm_value(-10.0) == 0.0
        assert param2.norm_value(-5.0) == 1.0
        assert param2.norm_value(-7.5) == 0.5
    
    def test_norm_invalid(self):
        """Test normalization with invalid value."""
        param = ContinuousParameter("test", 0.0, 10.0)
        # Out of range values now accepted with warning
        with pytest.warns(UserWarning, match="outside range"):
            assert param.norm_value(15.0) == 1.5  # Extrapolated
        # Non-numeric values still raise error
        with pytest.raises(ValueError, match="cannot be converted to float"):
            param.norm_value("not a number")
    
    def test_unnorm(self):
        """Test denormalization."""
        param = ContinuousParameter("test", 0.0, 10.0)
        assert param.unnorm_value(0.0) == 0.0
        assert param.unnorm_value(1.0) == 10.0
        assert param.unnorm_value(0.5) == 5.0
        assert param.unnorm_value(0.25) == 2.5
    
    def test_unnorm_extrapolation(self):
        """Test denormalization with values outside [0, 1] (extrapolation)."""
        param = ContinuousParameter("test", 0.0, 10.0)
        # Values outside [0, 1] should extrapolate
        assert param.unnorm_value(1.5) == 15.0  # Extrapolate beyond max
        assert param.unnorm_value(-0.1) == -1.0  # Extrapolate below min
        assert param.unnorm_value(2.0) == 20.0   # Double the range
    
    def test_sample_random(self):
        """Test random sampling."""
        param = ContinuousParameter("test", 0.0, 10.0)
        for _ in range(10):
            value = param.sample_random()
            assert 0.0 <= value <= 10.0
        
        # Test with seed
        value1 = param.sample_random(random_state=42)
        value2 = param.sample_random(random_state=42)
        assert value1 == value2


class TestDiscreteParameter:
    """Test DiscreteParameter class."""
    
    def test_init_valid(self):
        """Test valid initialization."""
        param = DiscreteParameter("test", min_val=0, max_val=10, default=5)
        assert param.min_val == 0.0
        assert param.max_val == 10.0
        assert param.default == 5.0
        assert param.values == list(range(11))
    
    def test_init_with_step(self):
        """Test initialization with custom step."""
        param = DiscreteParameter("test", min_val=0, max_val=10, default=4, step=2)
        assert param.values == [0.0, 2.0, 4.0, 6.0, 8.0, 10.0]
        assert param.default == 4.0
    
    def test_init_adjust_max(self):
        """Test that max is adjusted to fit step grid."""
        param = DiscreteParameter("test", min_val=0, max_val=11, step=3)
        assert param.max_val == 9.0  # Adjusted from 11
        assert param.values == [0.0, 3.0, 6.0, 9.0]
    
    def test_init_default_none(self):
        """Test initialization with None default."""
        param = DiscreteParameter("test", min_val=0, max_val=10, step=2)
        # Valid values are [0, 2, 4, 6, 8, 10] - 6 values
        # Middle index is 6//2 = 3, so default is values[3] = 6
        assert param.default == 6.0
    
    def test_init_invalid_step(self):
        """Test initialization with invalid step."""
        with pytest.raises(ValueError, match="step.*must be positive"):
            DiscreteParameter("test", min_val=0, max_val=10, step=0)
    
    def test_init_invalid_range(self):
        """Test initialization with invalid range - should flip with warning."""
        with pytest.warns(UserWarning, match="min_val.*is greater than max_val.*will be flipped"):
            param = DiscreteParameter("test", min_val=10, max_val=5, step=1)
        assert param.min_val == 5.0
        assert param.max_val == 10.0
    
    def test_init_equal_min_max(self):
        """Test initialization with equal min and max - should warn."""
        with pytest.warns(UserWarning, match="min_val and max_val are equal"):
            param = DiscreteParameter("test", min_val=5, max_val=5)
        assert param.min_val == 5.0
        assert param.max_val == 5.0
        assert param.values == [5.0]
    
    def test_init_with_values_list(self):
        """Test initialization with explicit values list."""
        param = DiscreteParameter("test", values=[1, 2, 5, 10, 20])
        assert param.values == [1.0, 2.0, 5.0, 10.0, 20.0]
        assert param.min_val == 1.0
        assert param.max_val == 20.0
        assert param.default == 5.0  # Middle value
    
    def test_init_with_values_tuple(self):
        """Test initialization with values tuple."""
        param = DiscreteParameter("test", values=(3, 7, 11, 15))
        assert param.values == [3.0, 7.0, 11.0, 15.0]
        assert param.default == 11.0  # Middle value
    
    def test_init_values_with_duplicates(self):
        """Test that duplicate values are removed."""
        param = DiscreteParameter("test", values=[1, 2, 2, 3, 3, 3])
        assert param.values == [1.0, 2.0, 3.0]
    
    def test_init_values_unsorted(self):
        """Test that values are sorted."""
        param = DiscreteParameter("test", values=[5, 1, 3, 2])
        assert param.values == [1.0, 2.0, 3.0, 5.0]
    
    def test_validate(self):
        """Test value validation."""
        param = DiscreteParameter("test", min_val=0, max_val=10, step=2)
        assert param.validate(0) is True
        assert param.validate(2) is True
        assert param.validate(10) is True
        # Values not on step grid now accepted with warning
        with pytest.warns(UserWarning, match="not in allowed values.*Will snap to nearest"):
            assert param.validate(1) is True
        with pytest.warns(UserWarning, match="not in allowed values.*Will snap to nearest"):
            assert param.validate(11) is True
        with pytest.warns(UserWarning, match="not in allowed values.*Will snap to nearest"):
            assert param.validate(2.5) is True
        assert param.validate("not a number") is False
    
    def test_norm(self):
        """Test normalization."""
        param = DiscreteParameter("test", min_val=0, max_val=10, step=2)
        # Range-based normalization
        assert param.norm_value(0) == 0.0    # min_val
        assert param.norm_value(10) == 1.0   # max_val
        assert param.norm_value(4) == 0.4    # 4/10
        assert param.norm_value(6) == 0.6    # 6/10
        
        # Test value snapping
        # First validate to trigger warning
        with pytest.warns(UserWarning, match="not in allowed values.*Will snap to nearest"):
            param.validate(3)
        assert param.norm_value(3) == 0.2  # Snaps to 2, then 2/10
        
        with pytest.warns(UserWarning, match="not in allowed values.*Will snap to nearest"):
            param.validate(5)
        assert param.norm_value(5) == 0.4  # Snaps to 4 (closer), then 4/10
        
        # Test with non-uniform values
        param2 = DiscreteParameter("test2", values=[1, 2, 5, 10])
        assert param2.norm_value(1) == 0.0    # (1-1)/(10-1) = 0
        assert param2.norm_value(10) == 1.0   # (10-1)/(10-1) = 1
        assert abs(param2.norm_value(5) - 4/9) < 1e-10  # (5-1)/(10-1) = 4/9
    
    def test_unnorm(self):
        """Test denormalization."""
        param = DiscreteParameter("test", min_val=0, max_val=10, step=2)
        assert param.unnorm_value(0.0) == 0.0
        assert param.unnorm_value(1.0) == 10.0
        # 0.5 maps to 5.0 in continuous space, nearest valid is 4 or 6
        assert param.unnorm_value(0.5) in [4.0, 6.0]  # Could be either
        assert param.unnorm_value(0.39) == 4.0   # 3.9 -> nearest is 4
        assert param.unnorm_value(0.41) == 4.0   # 4.1 -> nearest is 4
        assert param.unnorm_value(0.59) == 6.0   # 5.9 -> nearest is 6
        
        # Test with non-uniform values
        param2 = DiscreteParameter("test2", values=[1, 2, 5, 10])
        assert param2.unnorm_value(0.0) == 1.0
        assert param2.unnorm_value(1.0) == 10.0
        # 0.5 maps to 5.5 in continuous space, nearest valid is 5
        assert param2.unnorm_value(0.5) == 5.0
    
    def test_sample_random(self):
        """Test random sampling."""
        param = DiscreteParameter("test", min_val=0, max_val=10, step=2)
        for _ in range(10):
            value = param.sample_random()
            assert value in param.values
    
    def test_discrete_float_range_init(self):
        """Test creating discrete parameter with float range."""
        param = DiscreteParameter("test", min_val=0.0, max_val=1.0, step=0.1)
        
        assert param.min_val == 0.0
        assert abs(param.max_val - 1.0) < 0.01  # Tolerance for float precision
        expected_values = [0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]
        assert len(param.values) == len(expected_values)
        for actual, expected in zip(param.values, expected_values):
            assert abs(actual - expected) < 1e-10
    
    def test_discrete_float_list_init(self):
        """Test creating discrete parameter with float list."""
        values = [0.5, 1.5, 2.5, 5.0, 10.0]
        param = DiscreteParameter("test", values=values)
        
        assert param.values == values
        assert param.min_val == 0.5
        assert param.max_val == 10.0
        assert param.default == 2.5  # Middle value
    
    def test_discrete_float_validation(self):
        """Test validation with float values."""
        param = DiscreteParameter("test", min_val=0.0, max_val=1.0, step=0.25)
        
        # Valid values
        assert param.validate(0.0)
        assert param.validate(0.25)
        assert param.validate(0.5)
        assert param.validate(0.75)
        assert param.validate(1.0)
        
        # Invalid values - now return True with warnings (lenient validation)
        import warnings
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            assert param.validate(0.1)  # Returns True but snaps to nearest
            assert param.validate(0.3)  # Returns True but snaps to nearest
            assert param.validate(1.5)  # Returns True but snaps to nearest
            assert param.validate(-0.5)  # Returns True but snaps to nearest
    
    def test_discrete_float_norm_unnorm(self):
        """Test normalization and denormalization with float values."""
        param = DiscreteParameter("test", min_val=0.0, max_val=10.0, step=2.5)
        # Values: [0.0, 2.5, 5.0, 7.5, 10.0]
        
        # Test normalization
        assert param.norm_value(0.0) == 0.0
        assert param.norm_value(5.0) == 0.5
        assert param.norm_value(10.0) == 1.0
        
        # Test denormalization - should snap to nearest valid value
        assert param.unnorm_value(0.0) == 0.0
        assert param.unnorm_value(0.25) == 2.5
        assert param.unnorm_value(0.5) == 5.0
        assert param.unnorm_value(0.75) == 7.5
        assert param.unnorm_value(1.0) == 10.0
    
    def test_discrete_float_small_step(self):
        """Test with very small float steps."""
        param = DiscreteParameter("test", min_val=0.0, max_val=0.1, step=0.01)
        
        assert len(param.values) == 11  # 0.00 to 0.10 in steps of 0.01
        assert param.validate(0.05)
        assert param.validate(0.07)
        # Invalid values now return True with warnings (lenient validation)
        import warnings
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            assert param.validate(0.055)  # Returns True but snaps to nearest
    
    def test_discrete_float_irregular_list(self):
        """Test with irregular float values."""
        values = [0.1, 0.3, 0.7, 1.5, 3.0]
        param = DiscreteParameter("test", values=values)
        
        # Test normalization - should be range-based
        assert param.norm_value(0.1) == 0.0  # min value
        assert param.norm_value(3.0) == 1.0  # max value
        # Middle value: (1.5 - 0.1) / (3.0 - 0.1) ≈ 0.483
        assert abs(param.norm_value(1.5) - 0.483) < 0.01
    
    def test_discrete_float_mixed_init(self):
        """Test initialization with mixed int/float values."""
        values = [1, 2.5, 5, 7.5, 10]
        param = DiscreteParameter("test", values=values)
        
        # Should convert all to floats
        assert all(isinstance(v, float) for v in param.values)
        assert param.values == [1.0, 2.5, 5.0, 7.5, 10.0]
    
    def test_discrete_float_default_handling(self):
        """Test default value handling with floats."""
        # Test with explicit default
        param1 = DiscreteParameter("test1", min_val=0.0, max_val=1.0, step=0.2, default=0.4)
        assert param1.default == 0.4
        
        # Test with default that needs snapping - should warn
        with pytest.warns(UserWarning, match="Default value.*is not in the list of valid values"):
            param2 = DiscreteParameter("test2", min_val=0.0, max_val=1.0, step=0.3, default=0.5)
            # Values: [0.0, 0.3, 0.6, 0.9]
            # 0.5 should snap to 0.6 (nearest)
            assert param2.default == 0.6
        
        # Test automatic default (middle value)
        param3 = DiscreteParameter("test3", values=[0.1, 0.5, 0.9, 1.3, 1.7])
        assert param3.default == 0.9  # Middle value
    
    def test_discrete_float_sample_random(self):
        """Test random sampling with float values."""
        param = DiscreteParameter("test", min_val=0.0, max_val=1.0, step=0.1)
        
        # Sample with seed for reproducibility
        np.random.seed(42)
        samples = [param.sample_random() for _ in range(10)]
        
        # All samples should be valid values
        assert all(s in param.values for s in samples)
        
        # Should get some variety
        assert len(set(samples)) > 1


class TestCategoricalParameter:
    """Test CategoricalParameter class."""
    
    def test_init_valid(self):
        """Test valid initialization."""
        param = CategoricalParameter("test", ['a', 'b', 'c'], 'b')
        assert param.categories == ['a', 'b', 'c']
        assert param.default == 'b'
    
    def test_init_default_none(self):
        """Test initialization with None default."""
        param = CategoricalParameter("test", ['a', 'b', 'c'])
        assert param.default == 'a'  # First category
    
    def test_init_duplicates(self):
        """Test initialization with duplicate categories."""
        param = CategoricalParameter("test", ['a', 'b', 'a', 'c'])
        assert param.categories == ['a', 'b', 'c']  # Duplicates removed
    
    def test_init_empty(self):
        """Test initialization with empty categories."""
        with pytest.raises(ValueError, match="Categories list cannot be empty"):
            CategoricalParameter("test", [])
    
    def test_init_invalid_default(self):
        """Test initialization with invalid default."""
        with pytest.raises(ValueError, match="Default value.*is not in categories"):
            CategoricalParameter("test", ['a', 'b', 'c'], 'd')
    
    def test_validate(self):
        """Test value validation."""
        param = CategoricalParameter("test", ['a', 'b', 'c'])
        assert param.validate('a') is True
        assert param.validate('b') is True
        assert param.validate('c') is True
        # Invalid values now accepted with warning
        with pytest.warns(UserWarning, match="not in categories.*Will use first category"):
            assert param.validate('d') is True
        with pytest.warns(UserWarning, match="not in categories.*Will use first category"):
            assert param.validate(123) is True
    
    def test_norm(self):
        """Test normalization."""
        param = CategoricalParameter("test", ['a', 'b', 'c'])
        assert param.norm_value('a') == 0.0
        assert param.norm_value('c') == 1.0
        assert param.norm_value('b') == 0.5
        
        # Test with single category
        param2 = CategoricalParameter("test2", ['only'])
        assert param2.norm_value('only') == 0.5
    
    def test_norm_invalid(self):
        """Test normalization with invalid value."""
        param = CategoricalParameter("test", ['a', 'b', 'c'])
        # Invalid values now use first category with warning
        # First validate to trigger warning
        with pytest.warns(UserWarning, match="not in categories.*Will use first category"):
            param.validate('d')
        assert param.norm_value('d') == 0.0  # Uses 'a' which maps to 0.0
    
    def test_unnorm(self):
        """Test denormalization."""
        param = CategoricalParameter("test", ['a', 'b', 'c'])
        assert param.unnorm_value(0.0) == 'a'
        assert param.unnorm_value(1.0) == 'c'
        assert param.unnorm_value(0.5) == 'b'
        assert param.unnorm_value(0.4) == 'b'  # Rounds to nearest
        assert param.unnorm_value(0.6) == 'b'  # Rounds to nearest
        
        # Test clipping of out-of-range values
        assert param.unnorm_value(-0.5) == 'a'  # Clips to 0.0
        assert param.unnorm_value(1.5) == 'c'   # Clips to 1.0
    
    def test_get_category_index(self):
        """Test getting category index."""
        param = CategoricalParameter("test", ['a', 'b', 'c'])
        assert param.get_category_index('a') == 0
        assert param.get_category_index('b') == 1
        assert param.get_category_index('c') == 2
        
        with pytest.raises(ValueError):
            param.get_category_index('d')
    
    def test_get_category_by_index(self):
        """Test getting category by index."""
        param = CategoricalParameter("test", ['a', 'b', 'c'])
        assert param.get_category_by_index(0) == 'a'
        assert param.get_category_by_index(1) == 'b'
        assert param.get_category_by_index(2) == 'c'
        
        with pytest.raises(IndexError):
            param.get_category_by_index(3)
    
    def test_sample_random(self):
        """Test random sampling."""
        param = CategoricalParameter("test", ['a', 'b', 'c'])
        for _ in range(10):
            value = param.sample_random()
            assert value in param.categories
        
        # Test with seed
        value1 = param.sample_random(random_state=42)
        value2 = param.sample_random(random_state=42)
        assert value1 == value2
    
    def test_numeric_categories(self):
        """Test with numeric categories."""
        param = CategoricalParameter("test", [1, 2, 3], 2)
        assert param.categories == [1, 2, 3]
        assert param.default == 2
        assert param.norm_value(1) == 0.0
        assert param.norm_value(3) == 1.0
        assert param.unnorm_value(0.5) == 2


if __name__ == "__main__":
    pytest.main([__file__, "-v"])