"""
Test suite for Gaussian Process metamodel implementation.
"""

import numpy as np
import pytest

try:
    import GPy
    GPY_AVAILABLE = True
except ImportError:
    GPY_AVAILABLE = False

from aivalanche_lib.metamodels import GaussianProcessMetamodel
from aivalanche_lib.metamodels.utils import calculate_r2_score


# Skip tests if GPy is not available
pytestmark = pytest.mark.skipif(not GPY_AVAILABLE, reason="GPy not installed")


def simple_1d_function(x):
    """Simple 1D test function: f(x) = sin(2*pi*x) + 0.1*x"""
    return np.sin(2 * np.pi * x) + 0.1 * x


def rosenbrock_2d(x):
    """2D Rosenbrock function for testing."""
    return (1 - x[:, 0])**2 + 100 * (x[:, 1] - x[:, 0]**2)**2


class TestGaussianProcessMetamodel:
    """Test cases for Gaussian Process metamodel."""
    
    def test_initialization(self):
        """Test GP initialization with different parameters."""
        # Default initialization
        gp = GaussianProcessMetamodel()
        assert gp.kernel_type == 'rbf'
        assert gp.optimize_hyperparameters == True
        
        # Custom initialization
        gp = GaussianProcessMetamodel(
            kernel_type='matern52',
            length_scale=0.5,
            variance=1.0,
            noise_variance=0.01,
            optimize_hyperparameters=False
        )
        assert gp.kernel_type == 'matern52'
        assert gp.length_scale == 0.5
        assert gp.variance == 1.0
        assert gp.noise_variance == 0.01
    
    def test_1d_fitting_and_prediction(self):
        """Test fitting and prediction on 1D function."""
        # Generate training data
        np.random.seed(42)
        X_train = np.random.uniform(0, 1, 20).reshape(-1, 1)
        y_train = simple_1d_function(X_train).ravel()
        
        # Fit GP
        gp = GaussianProcessMetamodel(random_state=42)
        gp.fit(X_train, y_train)
        
        assert gp.is_fitted
        assert gp.n_samples == 20
        assert gp.input_dim == 1
        
        # Test predictions
        X_test = np.linspace(0, 1, 50).reshape(-1, 1)
        y_pred = gp.predict(X_test)
        
        assert y_pred.shape == (50,)
        assert not np.any(np.isnan(y_pred))
        
        # Test R2 score on training data (should be high)
        y_train_pred = gp.predict(X_train)
        r2 = calculate_r2_score(y_train, y_train_pred)
        assert r2 > 0.95  # Should fit training data very well
    
    def test_prediction_with_uncertainty(self):
        """Test predictions with uncertainty estimates."""
        # Generate training data
        np.random.seed(42)
        X_train = np.random.uniform(0, 1, 15).reshape(-1, 1)
        y_train = simple_1d_function(X_train).ravel()
        
        # Fit GP
        gp = GaussianProcessMetamodel(random_state=42)
        gp.fit(X_train, y_train)
        
        # Test predictions with uncertainty
        X_test = np.array([[0.25], [0.5], [0.75], [1.5]])  # Include extrapolation
        y_pred, y_std = gp.predict_with_uncertainty(X_test)
        
        assert y_pred.shape == (4,)
        assert y_std.shape == (4,)
        assert np.all(y_std > 0)  # Uncertainties should be positive
        
        # Uncertainty should be higher for extrapolation
        assert y_std[3] > y_std[1]  # Point at 1.5 vs point at 0.5
    
    def test_2d_fitting(self):
        """Test fitting on 2D function."""
        # Generate training data
        np.random.seed(42)
        n_samples = 50
        X_train = np.random.uniform(-2, 2, (n_samples, 2))
        y_train = rosenbrock_2d(X_train)
        
        # Fit GP
        gp = GaussianProcessMetamodel(
            kernel_type='matern52',
            random_state=42
        )
        gp.fit(X_train, y_train)
        
        assert gp.is_fitted
        assert gp.input_dim == 2
        
        # Test predictions
        X_test = np.array([[1.0, 1.0], [0.0, 0.0], [-1.0, 1.0]])
        y_pred = gp.predict(X_test)
        
        assert y_pred.shape == (3,)
        # At optimum [1, 1], Rosenbrock should be close to 0
        assert abs(y_pred[0]) < 1.0
    
    def test_kernel_types(self):
        """Test different kernel types."""
        # Generate simple data
        X_train = np.linspace(0, 1, 10).reshape(-1, 1)
        y_train = X_train.ravel() ** 2
        
        kernel_types = ['rbf', 'matern32', 'matern52', 'exponential']
        
        for kernel_type in kernel_types:
            gp = GaussianProcessMetamodel(
                kernel_type=kernel_type,
                random_state=42
            )
            gp.fit(X_train, y_train)
            
            # Should be able to predict
            y_pred = gp.predict(X_train)
            assert not np.any(np.isnan(y_pred))
    
    def test_update_method(self):
        """Test incremental update with new data."""
        # Initial training data
        X_train = np.array([[0.2], [0.4], [0.6], [0.8]])
        y_train = simple_1d_function(X_train).ravel()
        
        # Fit GP
        gp = GaussianProcessMetamodel(random_state=42)
        gp.fit(X_train, y_train)
        
        initial_samples = gp.n_samples
        
        # Add new data
        X_new = np.array([[0.1], [0.9]])
        y_new = simple_1d_function(X_new).ravel()
        
        gp.update(X_new, y_new)
        
        assert gp.n_samples == initial_samples + 2
        assert gp.is_fitted
    
    def test_kernel_parameters(self):
        """Test getting and setting kernel parameters."""
        # Fit a simple model
        X_train = np.random.uniform(0, 1, (10, 2))
        y_train = np.sum(X_train, axis=1)
        
        gp = GaussianProcessMetamodel(
            optimize_hyperparameters=False,
            random_state=42
        )
        gp.fit(X_train, y_train)
        
        # Get parameters
        params = gp.get_kernel_parameters()
        assert 'variance' in params
        assert 'length_scale' in params
        assert 'noise_variance' in params
        
        # Set new parameters
        gp.set_kernel_parameters(
            variance=2.0,
            length_scale=[0.3, 0.3],
            noise_variance=0.1
        )
        
        # Verify they were set
        new_params = gp.get_kernel_parameters()
        assert abs(new_params['variance'] - 2.0) < 1e-6
        assert abs(new_params['noise_variance'] - 0.1) < 1e-6
    
    def test_normalization(self):
        """Test input/output normalization."""
        # Data with different scales
        X_train = np.random.uniform(100, 200, (20, 2))
        y_train = np.random.uniform(1000, 2000, 20)
        
        # With normalization (default)
        gp_norm = GaussianProcessMetamodel(random_state=42)
        gp_norm.fit(X_train, y_train)
        
        # Without normalization
        gp_no_norm = GaussianProcessMetamodel(
            normalize_inputs=False,
            normalize_outputs=False,
            random_state=42
        )
        gp_no_norm.fit(X_train, y_train)
        
        # Both should make predictions
        X_test = np.array([[150, 150]])
        y_pred_norm = gp_norm.predict(X_test)
        y_pred_no_norm = gp_no_norm.predict(X_test)
        
        assert not np.isnan(y_pred_norm[0])
        assert not np.isnan(y_pred_no_norm[0])
    
    def test_invalid_kernel_type(self):
        """Test error handling for invalid kernel type."""
        with pytest.raises(ValueError, match="Unknown kernel type"):
            gp = GaussianProcessMetamodel(kernel_type='invalid')
            X = np.random.rand(10, 2)
            y = np.random.rand(10)
            gp.fit(X, y)
    
    def test_predict_before_fit(self):
        """Test error when predicting before fitting."""
        gp = GaussianProcessMetamodel()
        X_test = np.random.rand(5, 2)
        
        with pytest.raises(ValueError, match="Model must be fitted"):
            gp.predict(X_test)
        
        with pytest.raises(ValueError, match="Model must be fitted"):
            gp.predict_with_uncertainty(X_test)


def test_gp_on_noisy_data():
    """Test GP performance on noisy data."""
    # Generate noisy training data
    np.random.seed(42)
    X_train = np.linspace(0, 1, 30).reshape(-1, 1)
    y_true = simple_1d_function(X_train).ravel()
    noise = 0.1 * np.random.normal(0, 1, len(y_true))
    y_train = y_true + noise
    
    # Fit GP with noise handling
    gp = GaussianProcessMetamodel(
        noise_variance=0.01,  # Estimate of noise level
        random_state=42
    )
    gp.fit(X_train, y_train)
    
    # Predictions should smooth out the noise
    y_pred = gp.predict(X_train)
    
    # Check that predictions are smoother than noisy data
    pred_variance = np.var(np.diff(y_pred))
    data_variance = np.var(np.diff(y_train))
    assert pred_variance < data_variance


if __name__ == "__main__":
    # Run basic tests
    test_module = TestGaussianProcessMetamodel()
    
    print("Testing initialization...")
    test_module.test_initialization()
    
    print("Testing 1D fitting and prediction...")
    test_module.test_1d_fitting_and_prediction()
    
    print("Testing prediction with uncertainty...")
    test_module.test_prediction_with_uncertainty()
    
    print("Testing 2D fitting...")
    test_module.test_2d_fitting()
    
    print("Testing kernel types...")
    test_module.test_kernel_types()
    
    print("Testing GP on noisy data...")
    test_gp_on_noisy_data()
    
    print("\nAll tests passed!")