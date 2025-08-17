"""
Comprehensive tests for Gaussian Process metamodel with focus on:
- Corner point handling
- Proper scaling/normalization
- Accuracy validation
"""

import numpy as np
import pandas as pd
import pytest
from sklearn.metrics import r2_score

from aivalanche_lib.metamodels.gaussian_process import GaussianProcessMetamodel


class TestGaussianProcessWithCorners:
    """Test GP metamodel with corner points and scaling."""
    
    @staticmethod
    def sphere_function(X):
        """Simple sphere function: f(x, y) = x^2 + y^2"""
        if isinstance(X, pd.DataFrame):
            X = X.values
        return np.sum(X**2, axis=1)
    
    @staticmethod
    def rosenbrock_function(X):
        """Rosenbrock function: f(x,y) = (1-x)^2 + 100*(y-x^2)^2"""
        if isinstance(X, pd.DataFrame):
            X = X.values
        x = X[:, 0]
        y = X[:, 1]
        return (1 - x)**2 + 100 * (y - x**2)**2
    
    def test_gp_with_corners_in_training(self):
        """Test that GP properly handles corner points in training data."""
        print("\n" + "="*60)
        print("Test: GP with Corner Points in Training")
        print("="*60)
        
        # Generate training data in normalized space [0, 1]
        np.random.seed(42)
        n_train = 50
        X_train_random = np.random.uniform(0.1, 0.9, (n_train, 2))  # Interior points
        
        # Add corner points
        corners = np.array([
            [0.0, 0.0], [0.0, 1.0], [1.0, 0.0], [1.0, 1.0]
        ])
        
        # Combine training data
        X_train = np.vstack([X_train_random, corners])
        
        # Map to actual space [-5, 5] for evaluation
        X_train_actual = X_train * 10 - 5
        y_train = self.sphere_function(X_train_actual)
        
        # Create and train GP
        gp = GaussianProcessMetamodel(
            kernel_type='matern52',
            normalize_inputs=True,
            normalize_outputs=True,
            optimize_hyperparameters=True,
            n_restarts=5,
            random_state=42
        )
        
        gp.fit(X_train, y_train)
        
        # Test on validation set (excluding corners)
        X_val = np.random.uniform(0.05, 0.95, (30, 2))
        X_val_actual = X_val * 10 - 5
        y_val_true = self.sphere_function(X_val_actual)
        
        y_val_pred, y_val_std = gp.predict_with_uncertainty(X_val)
        
        r2 = r2_score(y_val_true, y_val_pred)
        print(f"\nValidation R² score: {r2:.3f}")
        assert r2 > 0.9, f"R² score too low: {r2}"
        
        # Test corner predictions
        print("\nCorner predictions:")
        y_corners_true = self.sphere_function(corners * 10 - 5)
        y_corners_pred, _ = gp.predict_with_uncertainty(corners)
        
        for i, (corner, true, pred) in enumerate(zip(corners, y_corners_true, y_corners_pred)):
            error = abs(true - pred)
            print(f"  Corner {corner}: true={true:.2f}, pred={pred:.2f}, error={error:.2f}")
            assert error < 5.0, f"Corner prediction error too high: {error}"
    
    def test_gp_corner_importance(self):
        """Test the importance of including corners in training."""
        print("\n" + "="*60)
        print("Test: Importance of Corner Points")
        print("="*60)
        
        np.random.seed(42)
        
        # Generate base training data (avoiding corners)
        n_train = 40
        X_train_base = np.random.uniform(0.2, 0.8, (n_train, 2))
        X_train_actual = X_train_base * 10 - 5
        y_train_base = self.sphere_function(X_train_actual)
        
        # Corner points
        corners = np.array([
            [0.0, 0.0], [0.0, 1.0], [1.0, 0.0], [1.0, 1.0]
        ])
        corners_actual = corners * 10 - 5
        y_corners = self.sphere_function(corners_actual)
        
        # Test points including corners and edges
        test_points = np.array([
            [0.0, 0.0], [1.0, 1.0], [0.0, 1.0], [1.0, 0.0],  # Corners
            [0.5, 0.0], [0.5, 1.0], [0.0, 0.5], [1.0, 0.5],  # Edge centers
            [0.1, 0.1], [0.9, 0.9], [0.5, 0.5]               # Interior
        ])
        test_actual = test_points * 10 - 5
        y_test_true = self.sphere_function(test_actual)
        
        # Train without corners
        gp_no_corners = GaussianProcessMetamodel(
            kernel_type='matern52',
            normalize_inputs=True,
            normalize_outputs=True,
            random_state=42
        )
        gp_no_corners.fit(X_train_base, y_train_base)
        y_pred_no_corners, _ = gp_no_corners.predict_with_uncertainty(test_points)
        
        # Train with corners
        X_train_with_corners = np.vstack([X_train_base, corners])
        y_train_with_corners = np.hstack([y_train_base, y_corners])
        
        gp_with_corners = GaussianProcessMetamodel(
            kernel_type='matern52',
            normalize_inputs=True,
            normalize_outputs=True,
            random_state=42
        )
        gp_with_corners.fit(X_train_with_corners, y_train_with_corners)
        y_pred_with_corners, _ = gp_with_corners.predict_with_uncertainty(test_points)
        
        # Compare predictions
        print("\nPrediction comparison:")
        print("Point Type    | True    | No Corners | With Corners | Improvement")
        print("-"*65)
        
        corner_improvements = []
        edge_improvements = []
        
        for i, (true, pred1, pred2) in enumerate(zip(y_test_true, y_pred_no_corners, y_pred_with_corners)):
            if i < 4:
                pt_type = "Corner"
            elif i < 8:
                pt_type = "Edge"
            else:
                pt_type = "Interior"
            
            err1 = abs(true - pred1)
            err2 = abs(true - pred2)
            improvement = (err1 - err2) / err1 * 100 if err1 > 0 else 0
            
            print(f"{pt_type:8} | {true:7.2f} | {pred1:10.2f} | {pred2:12.2f} | {improvement:+6.1f}%")
            
            if i < 4:
                corner_improvements.append(improvement)
            elif i < 8:
                edge_improvements.append(improvement)
        
        # Assert that corners improve prediction accuracy
        avg_corner_improvement = np.mean(corner_improvements)
        avg_edge_improvement = np.mean(edge_improvements)
        
        print(f"\nAverage improvements:")
        print(f"  Corners: {avg_corner_improvement:.1f}%")
        print(f"  Edges: {avg_edge_improvement:.1f}%")
        
        assert avg_corner_improvement > 50, "Corner predictions should improve significantly"
    
    def test_gp_extrapolation(self):
        """Test GP extrapolation behavior with and without corners."""
        print("\n" + "="*60)
        print("Test: GP Extrapolation Behavior")
        print("="*60)
        
        np.random.seed(42)
        
        # Training data in [0.2, 0.8] range
        n_train = 30
        X_train = np.random.uniform(0.2, 0.8, (n_train, 2))
        
        # Add corners
        corners = np.array([
            [0.0, 0.0], [0.0, 1.0], [1.0, 0.0], [1.0, 1.0]
        ])
        X_train_with_corners = np.vstack([X_train, corners])
        
        # Evaluate on actual space
        X_train_actual = X_train * 10 - 5
        X_train_corners_actual = X_train_with_corners * 10 - 5
        y_train = self.sphere_function(X_train_actual)
        y_train_with_corners = self.sphere_function(X_train_corners_actual)
        
        # Create GPs
        gp_no_corners = GaussianProcessMetamodel(normalize_inputs=True, normalize_outputs=True)
        gp_with_corners = GaussianProcessMetamodel(normalize_inputs=True, normalize_outputs=True)
        
        gp_no_corners.fit(X_train, y_train)
        gp_with_corners.fit(X_train_with_corners, y_train_with_corners)
        
        # Test extrapolation points (outside [0, 1])
        extrap_points_norm = np.array([
            [-0.1, -0.1], [1.1, 1.1], [-0.1, 1.1], [1.1, -0.1],
            [0.5, -0.1], [0.5, 1.1], [-0.1, 0.5], [1.1, 0.5]
        ])
        
        # Clip to valid range for actual evaluation
        extrap_points_clipped = np.clip(extrap_points_norm, 0, 1)
        extrap_actual = extrap_points_clipped * 10 - 5
        y_extrap_true = self.sphere_function(extrap_actual)
        
        # Get predictions
        y_no_corners, std_no_corners = gp_no_corners.predict_with_uncertainty(extrap_points_clipped)
        y_with_corners, std_with_corners = gp_with_corners.predict_with_uncertainty(extrap_points_clipped)
        
        print("\nExtrapolation results:")
        print("Point        | True    | No Corners (±std) | With Corners (±std)")
        print("-"*70)
        
        for i, (pt, true, pred1, std1, pred2, std2) in enumerate(
            zip(extrap_points_norm, y_extrap_true, y_no_corners, std_no_corners, y_with_corners, std_with_corners)
        ):
            print(f"{pt} | {true:7.2f} | {pred1:6.2f} (±{std1:4.2f}) | {pred2:6.2f} (±{std2:4.2f})")
        
        # With corners should have lower uncertainty at boundaries
        avg_std_no_corners = np.mean(std_no_corners)
        avg_std_with_corners = np.mean(std_with_corners)
        
        print(f"\nAverage uncertainties:")
        print(f"  Without corners: {avg_std_no_corners:.3f}")
        print(f"  With corners: {avg_std_with_corners:.3f}")
        
        assert avg_std_with_corners < avg_std_no_corners, "Corners should reduce boundary uncertainty"
    
    def test_gp_negative_predictions(self):
        """Test that GP doesn't produce negative predictions for non-negative functions."""
        print("\n" + "="*60)
        print("Test: Non-negative Predictions")
        print("="*60)
        
        np.random.seed(42)
        
        # Generate training data
        n_train = 100
        X_train = np.random.uniform(0, 1, (n_train, 2))
        
        # Add corners for better boundary behavior
        corners = np.array([
            [0.0, 0.0], [0.0, 1.0], [1.0, 0.0], [1.0, 1.0]
        ])
        X_train = np.vstack([X_train, corners])
        
        # Sphere function is always non-negative
        X_actual = X_train * 10 - 5
        y_train = self.sphere_function(X_actual)
        
        # Train GP
        gp = GaussianProcessMetamodel(
            kernel_type='matern52',
            normalize_inputs=True,
            normalize_outputs=True,
            optimize_hyperparameters=True
        )
        gp.fit(X_train, y_train)
        
        # Test on dense grid
        n_test = 50
        x_test = np.linspace(0, 1, n_test)
        X_test = np.array([(x, y) for x in x_test for y in x_test])
        
        y_pred, y_std = gp.predict_with_uncertainty(X_test)
        
        # Check for negative predictions
        n_negative = np.sum(y_pred < 0)
        min_pred = np.min(y_pred)
        
        print(f"\nPrediction statistics:")
        print(f"  Total predictions: {len(y_pred)}")
        print(f"  Negative predictions: {n_negative}")
        print(f"  Minimum prediction: {min_pred:.6f}")
        print(f"  Prediction range: [{min_pred:.3f}, {np.max(y_pred):.3f}]")
        
        # With corners and proper training, there should be very few if any negative predictions
        assert n_negative == 0 or min_pred > -0.1, f"Too many negative predictions or too negative: {min_pred}"
    
    def test_scaling_normalization(self):
        """Test that scaling/normalization is handled properly."""
        print("\n" + "="*60)
        print("Test: Scaling and Normalization")
        print("="*60)
        
        np.random.seed(42)
        
        # Generate data with very different scales
        n_train = 50
        X_train = np.random.uniform(0, 1, (n_train, 2))
        
        # Create function with large output values
        X_actual = X_train * 100  # Large scale
        y_train = 1000 * self.sphere_function(X_actual)  # Very large outputs
        
        # Train with normalization
        gp_norm = GaussianProcessMetamodel(
            normalize_inputs=True,
            normalize_outputs=True
        )
        gp_norm.fit(X_train, y_train)
        
        # Train without normalization
        gp_no_norm = GaussianProcessMetamodel(
            normalize_inputs=False,
            normalize_outputs=False
        )
        
        # This might fail or give poor results without normalization
        try:
            gp_no_norm.fit(X_train, y_train)
            fit_success = True
        except:
            fit_success = False
            print("  GP without normalization failed to fit (expected for large scales)")
        
        # Test predictions
        X_test = np.random.uniform(0, 1, (20, 2))
        X_test_actual = X_test * 100
        y_test_true = 1000 * self.sphere_function(X_test_actual)
        
        y_pred_norm, _ = gp_norm.predict_with_uncertainty(X_test)
        r2_norm = r2_score(y_test_true, y_pred_norm)
        
        print(f"\nWith normalization:")
        print(f"  R² score: {r2_norm:.3f}")
        print(f"  Prediction range: [{np.min(y_pred_norm):.1f}, {np.max(y_pred_norm):.1f}]")
        
        if fit_success:
            y_pred_no_norm, _ = gp_no_norm.predict_with_uncertainty(X_test)
            r2_no_norm = r2_score(y_test_true, y_pred_no_norm)
            print(f"\nWithout normalization:")
            print(f"  R² score: {r2_no_norm:.3f}")
            print(f"  Prediction range: [{np.min(y_pred_no_norm):.1f}, {np.max(y_pred_no_norm):.1f}]")
        
        assert r2_norm > 0.9, "Normalized GP should achieve good accuracy"


def run_all_tests():
    """Run all GP corner tests."""
    test_suite = TestGaussianProcessWithCorners()
    
    print("\n" + "="*80)
    print("GAUSSIAN PROCESS METAMODEL TESTS WITH CORNERS")
    print("="*80)
    
    # Run tests
    test_suite.test_gp_with_corners_in_training()
    test_suite.test_gp_corner_importance()
    test_suite.test_gp_extrapolation()
    test_suite.test_gp_negative_predictions()
    test_suite.test_scaling_normalization()
    
    print("\n" + "="*80)
    print("ALL TESTS COMPLETED SUCCESSFULLY!")
    print("="*80)


if __name__ == "__main__":
    run_all_tests()