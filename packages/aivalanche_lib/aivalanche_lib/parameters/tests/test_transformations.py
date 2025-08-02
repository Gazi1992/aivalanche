"""
Tests for parameter transformation implementations.
"""

import pytest
import numpy as np
from aivalanche_lib.parameters.transformations import (
    NoTransform,
    LogTransform,
    NegLogTransform,
    SymLogTransform
)


class TestNoTransform:
    """Test NoTransform class."""
    
    def test_scale(self):
        """Test scaling (identity)."""
        transform = NoTransform()
        assert transform.scale(5.0) == 5.0
        assert transform.scale(-10.0) == -10.0
        assert transform.scale(0) == 0.0
        assert transform.scale(1e6) == 1e6
    
    def test_unscale(self):
        """Test unscaling (identity)."""
        transform = NoTransform()
        assert transform.unscale(5.0) == 5.0
        assert transform.unscale(-10.0) == -10.0
        assert transform.unscale(0.0) == 0.0
    
    def test_validate_value(self):
        """Test value validation."""
        transform = NoTransform()
        assert transform.validate_value(5.0) is True
        assert transform.validate_value(-10.0) is True
        assert transform.validate_value(0) is True
        assert transform.validate_value("not a number") is False
        assert transform.validate_value(None) is False
    
    def test_name(self):
        """Test transform name."""
        transform = NoTransform()
        assert transform.name == "none"
    
    def test_repr(self):
        """Test string representation."""
        transform = NoTransform()
        assert repr(transform) == "NoTransform()"


class TestLogTransform:
    """Test LogTransform class."""
    
    def test_scale_valid(self):
        """Test scaling with valid positive values."""
        transform = LogTransform()
        assert transform.scale(1.0) == 0.0  # log10(1) = 0
        assert transform.scale(10.0) == 1.0  # log10(10) = 1
        assert transform.scale(100.0) == 2.0  # log10(100) = 2
        assert abs(transform.scale(0.1) - (-1.0)) < 1e-10  # log10(0.1) = -1
    
    def test_scale_invalid(self):
        """Test scaling with invalid values."""
        transform = LogTransform()
        with pytest.raises(ValueError, match="requires positive values"):
            transform.scale(0.0)
        with pytest.raises(ValueError, match="requires positive values"):
            transform.scale(-5.0)
    
    def test_unscale(self):
        """Test unscaling."""
        transform = LogTransform()
        assert transform.unscale(0.0) == 1.0  # 10^0 = 1
        assert transform.unscale(1.0) == 10.0  # 10^1 = 10
        assert transform.unscale(2.0) == 100.0  # 10^2 = 100
        assert abs(transform.unscale(-1.0) - 0.1) < 1e-10  # 10^-1 = 0.1
    
    def test_validate_value(self):
        """Test value validation."""
        transform = LogTransform()
        assert transform.validate_value(1.0) is True
        assert transform.validate_value(0.1) is True
        assert transform.validate_value(1000.0) is True
        assert transform.validate_value(0.0) is False
        assert transform.validate_value(-1.0) is False
        assert transform.validate_value("not a number") is False
    
    def test_round_trip(self):
        """Test scale/unscale round trip."""
        transform = LogTransform()
        values = [0.001, 0.1, 1.0, 10.0, 100.0, 1000.0]
        for val in values:
            scaled = transform.scale(val)
            unscaled = transform.unscale(scaled)
            assert abs(unscaled - val) < 1e-10
    
    def test_name(self):
        """Test transform name."""
        transform = LogTransform()
        assert transform.name == "log"


class TestNegLogTransform:
    """Test NegLogTransform class."""
    
    def test_scale_valid(self):
        """Test scaling with valid negative values."""
        transform = NegLogTransform()
        assert transform.scale(-1.0) == 0.0  # -log10(-(-1)) = -log10(1) = 0
        assert transform.scale(-10.0) == -1.0  # -log10(-(-10)) = -log10(10) = -1
        assert transform.scale(-100.0) == -2.0  # -log10(-(-100)) = -log10(100) = -2
        assert abs(transform.scale(-0.1) - 1.0) < 1e-10  # -log10(-(-0.1)) = -log10(0.1) = 1
    
    def test_scale_invalid(self):
        """Test scaling with invalid values."""
        transform = NegLogTransform()
        with pytest.raises(ValueError, match="requires negative values"):
            transform.scale(0.0)
        with pytest.raises(ValueError, match="requires negative values"):
            transform.scale(5.0)
    
    def test_unscale(self):
        """Test unscaling."""
        transform = NegLogTransform()
        assert transform.unscale(0.0) == -1.0  # -(10^(-0)) = -1
        assert transform.unscale(-1.0) == -10.0  # -(10^(-(-1))) = -10
        assert transform.unscale(-2.0) == -100.0  # -(10^(-(-2))) = -100
        assert abs(transform.unscale(1.0) - (-0.1)) < 1e-10  # -(10^(-1)) = -0.1
    
    def test_validate_value(self):
        """Test value validation."""
        transform = NegLogTransform()
        assert transform.validate_value(-1.0) is True
        assert transform.validate_value(-0.1) is True
        assert transform.validate_value(-1000.0) is True
        assert transform.validate_value(0.0) is False
        assert transform.validate_value(1.0) is False
        assert transform.validate_value("not a number") is False
    
    def test_round_trip(self):
        """Test scale/unscale round trip."""
        transform = NegLogTransform()
        values = [-0.001, -0.1, -1.0, -10.0, -100.0, -1000.0]
        for val in values:
            scaled = transform.scale(val)
            unscaled = transform.unscale(scaled)
            assert abs(unscaled - val) < 1e-10
    
    def test_name(self):
        """Test transform name."""
        transform = NegLogTransform()
        assert transform.name == "neglog"


class TestSymLogTransform:
    """Test SymLogTransform class."""
    
    def test_init(self):
        """Test initialization."""
        transform = SymLogTransform()
        assert transform.threshold == 1e-6
        
        transform2 = SymLogTransform(threshold=0.01)
        assert transform2.threshold == 0.01
        
        with pytest.raises(ValueError, match="Threshold must be positive"):
            SymLogTransform(threshold=0)
    
    def test_scale_positive(self):
        """Test scaling with positive values."""
        transform = SymLogTransform(threshold=1.0)
        
        # Test some key values
        assert transform.scale(0.0) == 0.0
        assert abs(transform.scale(1.0) - np.log10(2)) < 1e-10  # log10(1 + 1/1)
        
        # Large positive values should behave like log
        large_val = 1000.0
        expected = np.log10(1 + large_val)
        assert abs(transform.scale(large_val) - expected) < 1e-10
    
    def test_scale_negative(self):
        """Test scaling with negative values."""
        transform = SymLogTransform(threshold=1.0)
        
        # Should be symmetric
        assert transform.scale(-1.0) == -transform.scale(1.0)
        assert transform.scale(-100.0) == -transform.scale(100.0)
    
    def test_scale_near_zero(self):
        """Test scaling near zero."""
        transform = SymLogTransform(threshold=1e-6)
        
        # Very small values
        small_val = 1e-8
        scaled = transform.scale(small_val)
        assert abs(scaled) < 1  # Should be small
        
        # Should be continuous at zero
        assert transform.scale(0.0) == 0.0
    
    def test_unscale(self):
        """Test unscaling."""
        transform = SymLogTransform(threshold=1.0)
        
        # Key values
        assert transform.unscale(0.0) == 0.0
        
        # Round trip for positive
        val = 5.0
        scaled = transform.scale(val)
        unscaled = transform.unscale(scaled)
        assert abs(unscaled - val) < 1e-10
        
        # Round trip for negative
        val = -5.0
        scaled = transform.scale(val)
        unscaled = transform.unscale(scaled)
        assert abs(unscaled - val) < 1e-10
    
    def test_validate_value(self):
        """Test value validation."""
        transform = SymLogTransform()
        assert transform.validate_value(0.0) is True
        assert transform.validate_value(1.0) is True
        assert transform.validate_value(-1.0) is True
        assert transform.validate_value(1e10) is True
        assert transform.validate_value(-1e10) is True
        assert transform.validate_value(np.inf) is False
        assert transform.validate_value(-np.inf) is False
        assert transform.validate_value(np.nan) is False
        assert transform.validate_value("not a number") is False
    
    def test_round_trip_comprehensive(self):
        """Test scale/unscale round trip with various values."""
        transform = SymLogTransform()
        values = [-1000, -10, -1, -0.1, -0.001, 0, 0.001, 0.1, 1, 10, 1000]
        for val in values:
            scaled = transform.scale(val)
            unscaled = transform.unscale(scaled)
            assert abs(unscaled - val) < 1e-10 * max(1, abs(val))
    
    def test_name(self):
        """Test transform name."""
        transform = SymLogTransform()
        assert transform.name == "symlog"
    
    def test_repr(self):
        """Test string representation."""
        transform = SymLogTransform()
        assert repr(transform) == "SymLogTransform(threshold=1e-06)"
        
        transform2 = SymLogTransform(threshold=0.01)
        assert repr(transform2) == "SymLogTransform(threshold=0.01)"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])