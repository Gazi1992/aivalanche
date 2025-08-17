"""
Test the base metamodel functionality:
- Normalization
- Corner/edge detection
- Train/test split with corners in training
"""

import numpy as np
from aivalanche_lib.metamodels.gaussian_process import GaussianProcessMetamodel


def test_normalization():
    """Test that data is properly normalized to [0,1]."""
    print("\n" + "="*60)
    print("Test: Data Normalization")
    print("="*60)
    
    # Create data with different scales
    X = np.array([
        [10, 100],
        [20, 200],
        [30, 300],
        [40, 400]
    ])
    y = np.array([1, 2, 3, 4])
    
    gp = GaussianProcessMetamodel()
    gp.fit(X, y)
    
    # Check that training data is normalized
    print(f"Original X range: [{X.min()}, {X.max()}]")
    print(f"Normalized X_train range: [{gp.X_train.min():.3f}, {gp.X_train.max():.3f}]")
    
    assert np.allclose(gp.X_train.min(), 0.0), "Min should be 0"
    assert np.allclose(gp.X_train.max(), 1.0), "Max should be 1"
    
    print("[PASSED] Data normalization working!")


def test_corner_detection():
    """Test automatic corner and edge detection."""
    print("\n" + "="*60)
    print("Test: Corner and Edge Detection")
    print("="*60)
    
    # Create data with corners, edges, and interior points
    X = np.array([
        [0, 0],      # corner
        [0, 10],     # corner
        [10, 0],     # corner
        [10, 10],    # corner
        [5, 0],      # edge
        [5, 10],     # edge
        [0, 5],      # edge
        [10, 5],     # edge
        [3, 4],      # interior
        [7, 6],      # interior
    ])
    y = np.sum(X**2, axis=1)
    
    gp = GaussianProcessMetamodel(test_size=0.3)
    gp.fit(X, y)
    
    print(f"Detected {len(gp.corner_indices)} corners: {gp.corner_indices}")
    print(f"Detected {len(gp.edge_indices)} edges: {gp.edge_indices}")
    
    # After normalization, corners should be at indices 0,1,2,3
    assert len(gp.corner_indices) == 4, f"Expected 4 corners, got {len(gp.corner_indices)}"
    assert len(gp.edge_indices) == 4, f"Expected 4 edges, got {len(gp.edge_indices)}"
    
    print("[PASSED] Corner detection working!")


def test_train_test_split():
    """Test that corners/edges are kept in training set."""
    print("\n" + "="*60)
    print("Test: Train/Test Split")
    print("="*60)
    
    # Create data
    np.random.seed(42)
    X = np.random.rand(50, 2) * 10
    
    # Add explicit corners
    corners = np.array([[0, 0], [0, 10], [10, 0], [10, 10]])
    X = np.vstack([X, corners])
    y = np.sum(X**2, axis=1)
    
    gp = GaussianProcessMetamodel(test_size=0.2, random_state=42)
    gp.fit(X, y)
    
    print(f"Total samples: {len(X)}")
    print(f"Training samples: {len(gp.X_train)}")
    print(f"Test samples: {len(gp.X_test)}")
    print(f"Corners in data: {len(gp.corner_indices)}")
    print(f"Edges in data: {len(gp.edge_indices)}")
    
    # Check that all corners are in training
    # After normalization, the corners will be at different indices
    # but we can check that the normalized corners (0,0), (0,1), (1,0), (1,1) are in training
    corners_norm = np.array([[0, 0], [0, 1], [1, 0], [1, 1]])
    
    # Count how many normalized corners are in training
    corners_in_train = 0
    for corner in corners_norm:
        # Check if this corner exists in training data
        dists = np.sum((gp.X_train - corner)**2, axis=1)
        if np.min(dists) < 1e-6:
            corners_in_train += 1
            
    print(f"Corners in training: {corners_in_train}")
    assert corners_in_train >= len(gp.corner_indices), "All corners should be in training"
    
    print("[PASSED] Train/test split preserves corners!")


def test_score():
    """Test model scoring on test set."""
    print("\n" + "="*60)
    print("Test: Model Scoring")
    print("="*60)
    
    # Create simple quadratic data
    np.random.seed(42)
    X = np.random.rand(100, 2) * 10
    y = 2 * X[:, 0]**2 + 3 * X[:, 1]**2 + np.random.randn(100) * 0.1
    
    gp = GaussianProcessMetamodel(test_size=0.2, random_state=42)
    gp.fit(X, y)
    
    score = gp.score()
    print(f"Model R² score on test set: {score:.3f}")
    
    # Should get reasonable score
    assert score > 0.5, f"Score too low: {score}"
    
    print("[PASSED] Model scoring working!")


def test_info():
    """Test model info reporting."""
    print("\n" + "="*60)
    print("Test: Model Info")
    print("="*60)
    
    # Create data
    X = np.random.rand(30, 2)
    y = np.sum(X**2, axis=1)
    
    gp = GaussianProcessMetamodel()
    
    # Before fitting
    info = gp.get_info()
    print("Info before fitting:")
    for k, v in info.items():
        print(f"  {k}: {v}")
    
    # After fitting
    gp.fit(X, y)
    info = gp.get_info()
    print("\nInfo after fitting:")
    for k, v in info.items():
        print(f"  {k}: {v}")
    
    assert info['is_fitted'] == True
    assert 'validation_score' in info
    
    print("[PASSED] Model info working!")


def run_all_tests():
    """Run all base metamodel tests."""
    print("\n" + "="*80)
    print("BASE METAMODEL TESTS")
    print("="*80)
    
    test_normalization()
    test_corner_detection()
    test_train_test_split()
    test_score()
    test_info()
    
    print("\n" + "="*80)
    print("ALL TESTS PASSED!")
    print("="*80)


if __name__ == "__main__":
    run_all_tests()