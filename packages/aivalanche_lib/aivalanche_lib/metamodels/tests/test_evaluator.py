"""
Test suite for the MetamodelEvaluator integration layer.
"""

import numpy as np
import pandas as pd
import pytest
from typing import List, Dict, Any

from aivalanche_lib.metamodels import MetamodelEvaluator, AcquisitionStrategy, GaussianProcessMetamodel
from aivalanche_lib.metamodels.base import BaseMetamodel


# Simple test function
def sphere_function(x: np.ndarray) -> float:
    """Simple sphere function for testing."""
    return np.sum(x**2)


def create_test_eval_func():
    """Create a test evaluation function in the expected format."""
    call_count = 0
    
    def eval_func(parameters: pd.DataFrame, **kwargs) -> List[Dict[str, Any]]:
        nonlocal call_count
        responses = []
        
        for _, row in parameters.iterrows():
            x = row.values
            metric = sphere_function(x)
            call_count += 1
            
            response = {
                'metric': metric,
                'data': {'x': x.tolist()},
                'call_count': call_count
            }
            responses.append(response)
        
        return responses
    
    eval_func.call_count = lambda: call_count
    return eval_func


class TestMetamodelEvaluator:
    """Test cases for MetamodelEvaluator."""
    
    def test_initialization(self):
        """Test evaluator initialization."""
        eval_func = create_test_eval_func()
        evaluator = MetamodelEvaluator(
            actual_eval_func=eval_func,
            min_training_points=10,
            verbose=False
        )
        
        assert evaluator.n_actual_evals == 0
        assert evaluator.n_metamodel_evals == 0
        assert evaluator.acquisition_strategy == AcquisitionStrategy.MIXED
    
    def test_initial_evaluations_use_actual(self):
        """Test that initial evaluations use actual function."""
        eval_func = create_test_eval_func()
        evaluator = MetamodelEvaluator(
            actual_eval_func=eval_func,
            min_training_points=5,
            verbose=False
        )
        
        # Create test parameters
        params = pd.DataFrame({
            'x1': [0.1, 0.2, 0.3],
            'x2': [0.4, 0.5, 0.6]
        })
        
        # Evaluate
        responses = evaluator(params)
        
        assert len(responses) == 3
        assert evaluator.n_actual_evals == 3
        assert evaluator.n_metamodel_evals == 0
        assert eval_func.call_count() == 3
    
    def test_metamodel_usage_after_training(self):
        """Test that metamodel is used after enough training points."""
        eval_func = create_test_eval_func()
        evaluator = MetamodelEvaluator(
            actual_eval_func=eval_func,
            acquisition_strategy=AcquisitionStrategy.ALL_METAMODEL,
            min_training_points=5,
            update_frequency=5,
            verbose=False
        )
        
        # Initial evaluations (should use actual)
        params_init = pd.DataFrame({
            'x1': np.random.uniform(-1, 1, 6),
            'x2': np.random.uniform(-1, 1, 6)
        })
        evaluator(params_init)
        
        assert evaluator.n_actual_evals == 6
        assert evaluator.metamodel_trained
        
        # Next evaluations (should use metamodel with ALL_METAMODEL strategy)
        params_next = pd.DataFrame({
            'x1': [0.7, 0.8],
            'x2': [0.1, 0.2]
        })
        responses = evaluator(params_next)
        
        assert evaluator.n_metamodel_evals == 2
        assert all('is_metamodel' in r for r in responses)
    
    def test_periodic_strategy(self):
        """Test periodic validation strategy."""
        eval_func = create_test_eval_func()
        evaluator = MetamodelEvaluator(
            actual_eval_func=eval_func,
            acquisition_strategy=AcquisitionStrategy.PERIODIC,
            min_training_points=5,
            validation_frequency=3,
            verbose=False
        )
        
        # Initial training
        params_init = pd.DataFrame({
            'x1': np.random.uniform(-1, 1, 5),
            'x2': np.random.uniform(-1, 1, 5)
        })
        evaluator(params_init)
        
        # Evaluate 10 more points
        for i in range(10):
            params = pd.DataFrame({
                'x1': [np.random.uniform(-1, 1)],
                'x2': [np.random.uniform(-1, 1)]
            })
            evaluator(params)
        
        # Should have used actual evaluation periodically
        assert evaluator.n_actual_evals > 5
        assert evaluator.n_metamodel_evals > 0
    
    def test_caching(self):
        """Test that caching prevents redundant evaluations."""
        eval_func = create_test_eval_func()
        evaluator = MetamodelEvaluator(
            actual_eval_func=eval_func,
            enable_caching=True,
            min_training_points=2,
            verbose=False
        )
        
        # Evaluate same point twice
        params = pd.DataFrame({'x1': [0.5], 'x2': [0.5]})
        
        evaluator(params)
        first_count = eval_func.call_count()
        
        evaluator(params)
        second_count = eval_func.call_count()
        
        # Should not have called actual function again
        assert first_count == second_count == 1
    
    def test_statistics(self):
        """Test statistics tracking."""
        eval_func = create_test_eval_func()
        evaluator = MetamodelEvaluator(
            actual_eval_func=eval_func,
            min_training_points=5,
            verbose=False
        )
        
        # Run some evaluations
        params = pd.DataFrame({
            'x1': np.random.uniform(-1, 1, 10),
            'x2': np.random.uniform(-1, 1, 10)
        })
        evaluator(params)
        
        stats = evaluator.get_statistics()
        
        assert 'n_actual_evaluations' in stats
        assert 'n_metamodel_evaluations' in stats
        assert 'total_evaluations' in stats
        assert stats['total_evaluations'] == 10
    
    def test_reset(self):
        """Test reset functionality."""
        eval_func = create_test_eval_func()
        evaluator = MetamodelEvaluator(
            actual_eval_func=eval_func,
            verbose=False
        )
        
        # Run some evaluations
        params = pd.DataFrame({
            'x1': np.random.uniform(-1, 1, 5),
            'x2': np.random.uniform(-1, 1, 5)
        })
        evaluator(params)
        
        # Reset
        evaluator.reset()
        
        assert evaluator.n_actual_evals == 0
        assert evaluator.n_metamodel_evals == 0
        assert len(evaluator.training_X) == 0
        assert not evaluator.metamodel_trained


class DummyMetamodel(BaseMetamodel):
    """Dummy metamodel for testing that always predicts 0."""
    
    def fit(self, X, y):
        self.is_fitted = True
        return self
    
    def predict(self, X):
        return np.zeros(X.shape[0])
    
    def predict_with_uncertainty(self, X):
        return np.zeros(X.shape[0]), np.ones(X.shape[0]) * 0.1


def test_custom_metamodel():
    """Test using a custom metamodel."""
    eval_func = create_test_eval_func()
    custom_model = DummyMetamodel()
    
    evaluator = MetamodelEvaluator(
        actual_eval_func=eval_func,
        metamodel=custom_model,
        min_training_points=3,
        verbose=False
    )
    
    # Initial training
    params = pd.DataFrame({
        'x1': np.random.uniform(-1, 1, 5),
        'x2': np.random.uniform(-1, 1, 5)
    })
    responses = evaluator(params)
    
    assert evaluator.metamodel == custom_model
    assert len(responses) == 5


def test_optimization_direction():
    """Test that optimization direction is properly handled."""
    eval_func = create_test_eval_func()
    evaluator = MetamodelEvaluator(
        actual_eval_func=eval_func,
        verbose=False
    )
    
    # Test minimization
    params = pd.DataFrame({'x1': [0.5], 'x2': [0.5]})
    evaluator(params, opt_min_or_max='min')
    assert evaluator.minimize == True
    
    # Test maximization
    evaluator.reset()
    evaluator(params, opt_min_or_max='max')
    assert evaluator.minimize == False


if __name__ == "__main__":
    # Run basic tests
    test_module = TestMetamodelEvaluator()
    
    print("Testing initialization...")
    test_module.test_initialization()
    
    print("Testing initial evaluations...")
    test_module.test_initial_evaluations_use_actual()
    
    print("Testing metamodel usage...")
    test_module.test_metamodel_usage_after_training()
    
    print("Testing periodic strategy...")
    test_module.test_periodic_strategy()
    
    print("Testing caching...")
    test_module.test_caching()
    
    print("Testing statistics...")
    test_module.test_statistics()
    
    print("Testing custom metamodel...")
    test_custom_metamodel()
    
    print("\nAll tests passed!")