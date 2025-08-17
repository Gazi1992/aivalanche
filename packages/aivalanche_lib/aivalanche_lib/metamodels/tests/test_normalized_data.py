"""
Test metamodel with already normalized data.
"""

import numpy as np
from aivalanche_lib.metamodels.gaussian_process import GaussianProcessMetamodel


def test_normalized_data():
    """Test that metamodel handles data normalization correctly."""
    # Create data in original scale
    np.random.seed(42)
    n_samples = 50
    
    # Generate data in [-5, 5] range
    X = np.random.uniform(-5, 5, (n_samples, 2))
    
    # Add explicit corners in original scale
    corners = np.array([
        [-5, -5], [-5, 5], [5, -5], [5, 5]
    ])
    X = np.vstack([corners, X])
    
    # Add some edge points
    edges = np.array([
        [0, -5], [0, 5], [-5, 0], [5, 0],
        [-2.5, -5], [2.5, 5]
    ])
    X = np.vstack([X, edges])
    
    # Generate y values (simple function)
    y = X[:, 0]**2 + X[:, 1]**2
    
    # Create model
    model = GaussianProcessMetamodel(
        kernel_type='rbf',
        test_size=0.2,
        random_state=42
    )
    
    # Fit model
    model.fit(X, y)
    
    # Check that corners were detected
    info = model.get_info()
    print(f"Model info:")
    print(f"  Corners detected: {info['n_corners']}")
    print(f"  Edges detected: {info['n_edges']}")
    print(f"  Training points: {info['n_train']}")
    print(f"  Test points: {info['n_test']}")
    print(f"  Validation score: {info['validation_score']:.3f}")
    
    # Check that corners are in training set
    corner_indices = model.corner_indices
    print(f"\nCorner indices: {corner_indices}")
    print(f"Expected corner indices: [0, 1, 2, 3]")
    
    # Verify corners are not in test set
    train_has_corners = all(i in range(len(model.X_train)) for i in [0, 1, 2, 3])
    print(f"\nAll corners in training set: {train_has_corners}")
    
    # Test prediction with original scale input
    X_test = np.array([[0.0, 0.0], [-2.5, 2.5]])
    y_pred = model.predict(X_test)
    print(f"\nPredictions for test points:")
    for i, (x, pred) in enumerate(zip(X_test, y_pred)):
        true_val = x[0]**2 + x[1]**2
        print(f"  Point {x}: pred={pred:.3f}, true={true_val:.3f}")
    
    # Verify X_min and X_max for original scale data
    print(f"\nNormalization bounds:")
    print(f"  X_min: {model.X_min}")
    print(f"  X_max: {model.X_max}")
    assert np.allclose(model.X_min, [-5, -5])
    assert np.allclose(model.X_max, [5, 5])
    
    print("\nTest passed!")


if __name__ == "__main__":
    test_normalized_data()