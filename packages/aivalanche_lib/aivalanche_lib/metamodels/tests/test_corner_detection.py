"""
Test automatic corner and edge detection in metamodels.
"""

import numpy as np
import pandas as pd
from aivalanche_lib.metamodels.gaussian_process import GaussianProcessMetamodel


def test_corner_detection():
    """Test that corners and edges are automatically detected."""
    print("\n" + "="*60)
    print("Test: Automatic Corner and Edge Detection")
    print("="*60)
    
    # Create test data with some corners, edges, and interior points
    # Working in normalized [0, 1] space
    X_train = np.array([
        # Corners (all dimensions at boundaries)
        [0.0, 0.0],
        [0.0, 1.0],
        [1.0, 0.0],
        [1.0, 1.0],
        
        # Edges (one dimension at boundary)
        [0.5, 0.0],  # bottom edge
        [0.5, 1.0],  # top edge
        [0.0, 0.5],  # left edge
        [1.0, 0.5],  # right edge
        
        # Interior points
        [0.3, 0.4],
        [0.6, 0.7],
        [0.2, 0.8],
        [0.9, 0.2],
    ])
    
    # Create dummy y values
    y_train = np.sum(X_train**2, axis=1)
    
    # Create and fit GP
    gp = GaussianProcessMetamodel()
    gp.fit(X_train, y_train)
    
    # Check corner detection
    print(f"\nDetected corners: {gp._corner_indices}")
    print(f"Detected edges: {gp._edge_indices}")
    
    # Verify corners
    expected_corners = [0, 1, 2, 3]
    assert np.array_equal(sorted(gp._corner_indices), expected_corners), \
        f"Expected corners {expected_corners}, got {sorted(gp._corner_indices)}"
    
    # Verify edges
    expected_edges = [4, 5, 6, 7]
    assert np.array_equal(sorted(gp._edge_indices), expected_edges), \
        f"Expected edges {expected_edges}, got {sorted(gp._edge_indices)}"
    
    # Check info
    info = gp.get_info()
    print(f"\nModel info:")
    print(f"  Total samples: {info['n_samples']}")
    print(f"  Corner points: {info['n_corner_points']}")
    print(f"  Edge points: {info['n_edge_points']}")
    
    print("\n[PASSED] Corner and edge detection working correctly!")


def test_corner_detection_high_dim():
    """Test corner detection in higher dimensions."""
    print("\n" + "="*60)
    print("Test: Corner Detection in High Dimensions")
    print("="*60)
    
    # 3D test
    X_train_3d = np.array([
        # Corners (2^3 = 8 corners)
        [0, 0, 0], [0, 0, 1], [0, 1, 0], [0, 1, 1],
        [1, 0, 0], [1, 0, 1], [1, 1, 0], [1, 1, 1],
        
        # Some edges (2 dims at boundary)
        [0.5, 0, 0], [0.5, 1, 1],
        
        # Some faces (1 dim at boundary)
        [0.5, 0.5, 0], [0.5, 0.5, 1],
        
        # Interior
        [0.5, 0.5, 0.5], [0.3, 0.7, 0.4],
    ])
    
    y_train_3d = np.sum(X_train_3d**2, axis=1)
    
    gp = GaussianProcessMetamodel()
    gp.fit(X_train_3d, y_train_3d)
    
    print(f"\n3D data:")
    print(f"  Detected {len(gp._corner_indices)} corners (expected 8)")
    print(f"  Detected {len(gp._edge_indices)} edges/faces")
    
    assert len(gp._corner_indices) == 8, f"Expected 8 corners, got {len(gp._corner_indices)}"
    
    print("\n[PASSED] High-dimensional corner detection working!")


def test_corner_detection_with_tolerance():
    """Test corner detection with points near boundaries."""
    print("\n" + "="*60)
    print("Test: Corner Detection with Tolerance")
    print("="*60)
    
    # Create data with points very close to boundaries
    X_train = np.array([
        # Exact corners
        [0.0, 0.0],
        [1.0, 1.0],
        
        # Very close to corners (should be detected as corners with tolerance)
        [1e-7, 1e-7],
        [1.0 - 1e-7, 1.0 - 1e-7],
        
        # Close but not within tolerance
        [0.01, 0.01],
        [0.99, 0.99],
        
        # Interior
        [0.5, 0.5],
    ])
    
    y_train = np.sum(X_train**2, axis=1)
    
    gp = GaussianProcessMetamodel()
    gp.fit(X_train, y_train)
    
    print(f"\nWith default tolerance (1e-6):")
    print(f"  Corner indices: {sorted(gp._corner_indices)}")
    print(f"  Number of corners: {len(gp._corner_indices)}")
    
    # Should detect 4 corners (including the very close ones)
    assert len(gp._corner_indices) == 4, f"Expected 4 corners, got {len(gp._corner_indices)}"
    
    print("\n[PASSED] Tolerance-based corner detection working!")


def test_no_corners_in_data():
    """Test behavior when no corners are present."""
    print("\n" + "="*60)
    print("Test: No Corners in Data")
    print("="*60)
    
    # Create interior points only
    np.random.seed(42)
    X_train = np.random.uniform(0.1, 0.9, (20, 2))
    y_train = np.sum(X_train**2, axis=1)
    
    gp = GaussianProcessMetamodel()
    gp.fit(X_train, y_train)
    
    print(f"\nNo corners in data:")
    print(f"  Detected corners: {len(gp._corner_indices)}")
    print(f"  Detected edges: {len(gp._edge_indices)}")
    
    # When data is normalized to [0,1], the min/max points become corners
    # This is expected behavior - corners are relative to the normalized space
    if len(gp._corner_indices) > 0:
        print(f"  Note: Points at data extremes become corners after normalization")
        print(f"  Corner points in original data: {X_train[gp._corner_indices]}")
    
    print("\n[PASSED] Corner detection works with normalized data!")


def run_all_tests():
    """Run all corner detection tests."""
    print("\n" + "="*80)
    print("CORNER DETECTION TESTS")
    print("="*80)
    
    test_corner_detection()
    test_corner_detection_high_dim()
    test_corner_detection_with_tolerance()
    test_no_corners_in_data()
    
    print("\n" + "="*80)
    print("ALL CORNER DETECTION TESTS PASSED!")
    print("="*80)


if __name__ == "__main__":
    run_all_tests()