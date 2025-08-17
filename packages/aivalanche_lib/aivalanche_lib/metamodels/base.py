"""
Base classes for metamodel implementations.

This module provides the abstract base class that all metamodel implementations
should inherit from, ensuring a consistent interface across different surrogate
modeling techniques.
"""

from abc import ABC, abstractmethod
from typing import Optional, Dict, Any, Tuple, Union, List
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
import matplotlib.pyplot as plt
from sklearn.metrics import r2_score, mean_squared_error, mean_absolute_error


class BaseMetamodel(ABC):
    """
    Abstract base class for metamodel implementations.
    
    This class handles:
    1. Data normalization to [0,1]
    2. Corner/edge detection
    3. Train/test split ensuring corners are in training
    4. Common interface for all metamodel types
    """
    
    def __init__(self, 
                 random_state: Optional[int] = None,
                 test_size: float = 0.2,
                 **kwargs):
        """
        Initialize the base metamodel.
        
        Args:
            random_state: Random seed for reproducibility
            test_size: Fraction of data to use for validation
            **kwargs: Additional model-specific parameters
        """
        self.random_state = random_state
        self.test_size = test_size
        
        # Data storage
        self.X_train = None
        self.y_train = None
        self.X_test = None
        self.y_test = None
        
        # Normalization parameters
        self.X_min = None
        self.X_max = None
        self.y_mean = None
        self.y_std = None
        
        # Corner/edge detection
        self.corner_indices = None
        self.edge_indices = None
        
        # Model state
        self.is_fitted = False
        
    def fit(self, X: Union[np.ndarray, pd.DataFrame], 
            y: Union[np.ndarray, pd.Series]) -> 'BaseMetamodel':
        """
        Fit the metamodel to data.
        
        Steps:
        1. Normalize data to [0,1]
        2. Detect corners and edges
        3. Split into train/test ensuring corners are in training
        4. Fit the model
        
        Args:
            X: Input features of shape (n_samples, n_features)
            y: Target values of shape (n_samples,)
            
        Returns:
            self: The fitted metamodel instance
        """
        # Convert to numpy
        X = self._to_numpy(X)
        y = self._to_numpy(y)
        
        # Normalize X to [0,1]
        self.X_min = X.min(axis=0)
        self.X_max = X.max(axis=0)
        X_range = self.X_max - self.X_min
        X_range[X_range == 0] = 1.0  # Avoid division by zero
        X_norm = (X - self.X_min) / X_range
        
        # Standardize y
        self.y_mean = y.mean()
        self.y_std = y.std()
        if self.y_std == 0:
            self.y_std = 1.0
        y_norm = (y - self.y_mean) / self.y_std
        
        # Detect corners and edges
        self.corner_indices, self.edge_indices = self._detect_corners_edges(X_norm)
        
        # Split data ensuring corners/edges are in training
        train_idx, test_idx = self._split_data(X_norm.shape[0])
        
        # Ensure indices are integers
        train_idx = train_idx.astype(int)
        test_idx = test_idx.astype(int) if len(test_idx) > 0 else test_idx
        
        self.X_train = X_norm[train_idx]
        self.y_train = y_norm[train_idx]
        if len(test_idx) > 0:
            self.X_test = X_norm[test_idx]
            self.y_test = y_norm[test_idx]
        else:
            self.X_test = np.array([])
            self.y_test = np.array([])
        
        # Fit the actual model
        self._fit_model(self.X_train, self.y_train)
        
        self.is_fitted = True
        return self
        
    def predict(self, X: Union[np.ndarray, pd.DataFrame]) -> np.ndarray:
        """
        Make predictions.
        
        Args:
            X: Input features
            
        Returns:
            Predictions
        """
        if not self.is_fitted:
            raise ValueError("Model must be fitted before making predictions")
            
        # Convert and normalize
        X = self._to_numpy(X)
        X_norm = (X - self.X_min) / (self.X_max - self.X_min)
        
        # Predict
        y_norm = self._predict_model(X_norm)
        
        # Denormalize
        y = y_norm * self.y_std + self.y_mean
        
        return y
        
    def score(self) -> float:
        """
        Get the validation score (R²) on the test set.
        
        Returns:
            R² score
        """
        if not self.is_fitted or len(self.X_test) == 0:
            return 0.0
            
        y_pred = self._predict_model(self.X_test)
        
        # Calculate R²
        ss_res = np.sum((self.y_test - y_pred) ** 2)
        ss_tot = np.sum((self.y_test - np.mean(self.y_test)) ** 2)
        
        if ss_tot == 0:
            return 1.0 if ss_res == 0 else 0.0
            
        return 1 - (ss_res / ss_tot)
        
    def _to_numpy(self, data: Union[np.ndarray, pd.DataFrame, pd.Series]) -> np.ndarray:
        """Convert input data to numpy array."""
        if isinstance(data, (pd.DataFrame, pd.Series)):
            return data.values
        return np.asarray(data)
        
    def _detect_corners_edges(self, X_norm: np.ndarray, tol: float = 1e-6) -> Tuple[np.ndarray, np.ndarray]:
        """
        Detect corner and edge points in normalized data.
        
        Args:
            X_norm: Normalized features [0,1]
            tol: Tolerance for boundary detection
            
        Returns:
            (corner_indices, edge_indices)
        """
        corners = []
        edges = []
        
        for i in range(X_norm.shape[0]):
            point = X_norm[i]
            
            # Check how many dimensions are at boundaries
            at_boundary = np.logical_or(
                np.abs(point - 0.0) <= tol,
                np.abs(point - 1.0) <= tol
            )
            
            n_at_boundary = np.sum(at_boundary)
            
            if n_at_boundary == X_norm.shape[1]:
                corners.append(i)
            elif n_at_boundary > 0:
                edges.append(i)
                
        return np.array(corners), np.array(edges)
        
    def _split_data(self, n_samples: int) -> Tuple[np.ndarray, np.ndarray]:
        """
        Split indices into train/test, ensuring corners/edges are in training.
        
        Args:
            n_samples: Total number of samples
            
        Returns:
            (train_indices, test_indices)
        """
        all_indices = np.arange(n_samples)
        
        # Corners and edges must be in training
        if len(self.corner_indices) > 0 and len(self.edge_indices) > 0:
            priority_indices = np.concatenate([self.corner_indices, self.edge_indices])
        elif len(self.corner_indices) > 0:
            priority_indices = self.corner_indices
        elif len(self.edge_indices) > 0:
            priority_indices = self.edge_indices
        else:
            priority_indices = np.array([], dtype=int)
        
        # Other indices can be split
        other_indices = np.setdiff1d(all_indices, priority_indices)
        
        if len(other_indices) == 0:
            # All points are corners/edges
            return all_indices, np.array([])
            
        # Split the other indices
        n_test = int(len(other_indices) * self.test_size)
        if n_test == 0:
            # Not enough points for test set
            return all_indices, np.array([])
            
        np.random.seed(self.random_state)
        np.random.shuffle(other_indices)
        
        test_indices = other_indices[:n_test]
        train_other = other_indices[n_test:]
        
        # Combine priority indices with remaining training indices
        train_indices = np.concatenate([priority_indices, train_other])
        
        return train_indices, test_indices
        
    @abstractmethod
    def _fit_model(self, X_train: np.ndarray, y_train: np.ndarray) -> None:
        """
        Fit the actual model. Implemented by subclasses.
        
        Args:
            X_train: Normalized training features
            y_train: Normalized training targets
        """
        pass
        
    @abstractmethod
    def _predict_model(self, X: np.ndarray) -> np.ndarray:
        """
        Make predictions with the model. Implemented by subclasses.
        
        Args:
            X: Normalized features
            
        Returns:
            Normalized predictions
        """
        pass
        
    def get_info(self) -> Dict[str, Any]:
        """Get model information."""
        info = {
            'model_type': self.__class__.__name__,
            'is_fitted': self.is_fitted,
        }
        
        if self.is_fitted:
            info.update({
                'n_train': len(self.X_train),
                'n_test': len(self.X_test),
                'n_corners': len(self.corner_indices),
                'n_edges': len(self.edge_indices),
                'validation_score': self.score()
            })
            
        return info
    
    def plot_accuracy(self, figsize: Tuple[float, float] = (10, 6), 
                     save_path: Optional[str] = None, 
                     show: bool = True) -> Tuple[plt.Figure, plt.Axes]:
        """
        Plot predicted vs true values for train and test sets.
        
        Args:
            figsize: Figure size (width, height)
            save_path: If provided, save the figure to this path
            show: Whether to show the plot
            
        Returns:
            (fig, ax): Matplotlib figure and axes objects
        """
        if not self.is_fitted:
            raise ValueError("Model must be fitted before plotting accuracy")
            
        # Get predictions for train and test sets
        y_train_pred = self._predict_model(self.X_train)
        
        # Denormalize for plotting
        y_train_true_denorm = self.y_train * self.y_std + self.y_mean
        y_train_pred_denorm = y_train_pred * self.y_std + self.y_mean
        
        # Calculate metrics for training set
        train_r2 = r2_score(y_train_true_denorm, y_train_pred_denorm)
        train_rmse = np.sqrt(mean_squared_error(y_train_true_denorm, y_train_pred_denorm))
        train_mae = mean_absolute_error(y_train_true_denorm, y_train_pred_denorm)
        
        # Create figure
        fig, ax = plt.subplots(figsize=figsize)
        
        # Plot training points
        ax.scatter(y_train_true_denorm, y_train_pred_denorm, 
                  alpha=0.6, s=30, c='blue', edgecolors='darkblue', 
                  linewidth=0.5, label=f'Train (n={len(self.X_train)})')
        
        # Plot test points if available
        if len(self.X_test) > 0:
            y_test_pred = self._predict_model(self.X_test)
            y_test_true_denorm = self.y_test * self.y_std + self.y_mean
            y_test_pred_denorm = y_test_pred * self.y_std + self.y_mean
            
            # Calculate metrics for test set
            test_r2 = r2_score(y_test_true_denorm, y_test_pred_denorm)
            test_rmse = np.sqrt(mean_squared_error(y_test_true_denorm, y_test_pred_denorm))
            test_mae = mean_absolute_error(y_test_true_denorm, y_test_pred_denorm)
            
            ax.scatter(y_test_true_denorm, y_test_pred_denorm, 
                      alpha=0.6, s=30, c='red', edgecolors='darkred',
                      linewidth=0.5, label=f'Test (n={len(self.X_test)})')
        else:
            test_r2 = test_rmse = test_mae = None
            
        # Plot perfect prediction line
        all_true = y_train_true_denorm
        if len(self.X_test) > 0:
            all_true = np.concatenate([y_train_true_denorm, y_test_true_denorm])
        
        lims = [np.min(all_true), np.max(all_true)]
        ax.plot(lims, lims, 'k--', alpha=0.5, linewidth=1, label='Perfect prediction')
        
        # Labels and title
        ax.set_xlabel('True Values', fontsize=11)
        ax.set_ylabel('Predicted Values', fontsize=11)
        ax.set_title(f'{self.__class__.__name__} - Predicted vs True Values', fontsize=12, fontweight='bold')
        
        # Add grid
        ax.grid(True, alpha=0.3, linestyle='--')
        
        # Make the plot square
        ax.set_aspect('equal', adjustable='box')
        
        # Add legend
        ax.legend(loc='lower right', framealpha=0.9)
        
        # Create metrics text box
        metrics_text = f'Training Metrics:\n'
        metrics_text += f'  R² = {train_r2:.4f}\n'
        metrics_text += f'  RMSE = {train_rmse:.4e}\n'
        metrics_text += f'  MAE = {train_mae:.4e}\n'
        
        if test_r2 is not None:
            metrics_text += f'\nTest Metrics:\n'
            metrics_text += f'  R² = {test_r2:.4f}\n'
            metrics_text += f'  RMSE = {test_rmse:.4e}\n'
            metrics_text += f'  MAE = {test_mae:.4e}\n'
            
        # Add special points info
        if len(self.corner_indices) > 0 or len(self.edge_indices) > 0:
            metrics_text += f'\nSpecial Points:\n'
            if len(self.corner_indices) > 0:
                metrics_text += f'  Corners: {len(self.corner_indices)}\n'
            if len(self.edge_indices) > 0:
                metrics_text += f'  Edges: {len(self.edge_indices)}\n'
        
        # Add text box with metrics
        props = dict(boxstyle='round', facecolor='wheat', alpha=0.9)
        ax.text(0.05, 0.95, metrics_text, transform=ax.transAxes, fontsize=9,
                verticalalignment='top', bbox=props, family='monospace')
        
        # Adjust layout
        plt.tight_layout()
        
        # Save if requested
        if save_path:
            plt.savefig(save_path, dpi=150, bbox_inches='tight')
            
        # Show if requested
        if show:
            plt.show()
            
        return fig, ax