"""
Test suite for metamodel implementations.
"""

import numpy as np
import pytest
from aivalanche_lib.metamodels import BaseMetamodel
from aivalanche_lib.metamodels.utils import (
    expected_improvement, probability_of_improvement, 
    upper_confidence_bound, latin_hypercube_sampling
)


class DummyMetamodel(BaseMetamodel):
    """Dummy implementation for testing base class functionality."""
    
    def fit(self, X, y):
        X = self._to_numpy(X)
        y = self._to_numpy(y)
        
        # Store normalized data
        self.X_train = self._normalize_inputs(X, fit=True)
        self.y_train = self._normalize_outputs(y, fit=True)
        self.n_samples = X.shape[0]
        self.is_fitted = True
        return self
    
    def predict(self, X):
        X = self._to_numpy(X)
        X_norm = self._normalize_inputs(X)
        # Simple prediction: just return mean of training data
        y_pred_norm = np.full(X.shape[0], self.y_train.mean())
        return self._denormalize_outputs(y_pred_norm)
    
    def predict_with_uncertainty(self, X):
        X = self._to_numpy(X)
        predictions = self.predict(X)
        # Dummy uncertainty
        uncertainties = np.ones(X.shape[0]) * 0.1
        return predictions, uncertainties


def test_base_metamodel_interface():
    """Test the base metamodel interface."""
    model = DummyMetamodel(input_dim=2, output_dim=1)
    
    # Generate test data
    X = np.random.rand(10, 2)
    y = np.sum(X, axis=1)
    
    # Test fitting
    model.fit(X, y)
    assert model.is_fitted
    assert model.n_samples == 10
    
    # Test prediction
    X_test = np.random.rand(5, 2)
    predictions = model.predict(X_test)
    assert predictions.shape == (5,)
    
    # Test prediction with uncertainty
    pred, unc = model.predict_with_uncertainty(X_test)
    assert pred.shape == (5,)
    assert unc.shape == (5,)
    
    # Test update
    X_new = np.random.rand(3, 2)
    y_new = np.sum(X_new, axis=1)
    model.update(X_new, y_new)
    assert model.n_samples == 13


def test_acquisition_functions():
    """Test acquisition function calculations."""
    mean = np.array([1.0, 2.0, 3.0])
    std = np.array([0.1, 0.2, 0.3])
    best_value = 1.5
    
    # Test EI
    ei = expected_improvement(mean, std, best_value, minimize=True)
    assert ei.shape == mean.shape
    assert np.all(ei >= 0)
    
    # Test PI
    pi = probability_of_improvement(mean, std, best_value, minimize=True)
    assert pi.shape == mean.shape
    assert np.all((pi >= 0) & (pi <= 1))
    
    # Test UCB
    ucb = upper_confidence_bound(mean, std, kappa=2.0, minimize=True)
    assert ucb.shape == mean.shape


def test_latin_hypercube_sampling():
    """Test Latin Hypercube Sampling."""
    n_samples = 20
    n_dims = 3
    
    # Test unit hypercube
    samples = latin_hypercube_sampling(n_samples, n_dims, random_state=42)
    assert samples.shape == (n_samples, n_dims)
    assert np.all((samples >= 0) & (samples <= 1))
    
    # Test with bounds
    bounds = np.array([[-1, 1], [0, 10], [-5, 5]])
    samples = latin_hypercube_sampling(n_samples, n_dims, bounds=bounds, random_state=42)
    assert samples.shape == (n_samples, n_dims)
    for i in range(n_dims):
        assert np.all((samples[:, i] >= bounds[i, 0]) & (samples[:, i] <= bounds[i, 1]))


if __name__ == "__main__":
    test_base_metamodel_interface()
    test_acquisition_functions()
    test_latin_hypercube_sampling()
    print("All tests passed!")