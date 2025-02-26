import numpy as np, pandas as pd
import GPy
from typing import Optional, Tuple, Union, List, Dict
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import KFold
import matplotlib.pyplot as plt
from copy import deepcopy, copy
# from ..differential_evolution.Differential_evolution import Differential_evolution

class Gaussian_process:
    """
    A wrapper class for Gaussian Process regression using GPy.
    Provides functionality for training, prediction, and uncertainty quantification.
    """
    def __init__(
        self,
        X: Optional[np.ndarray] = None,
        y: Optional[np.ndarray] = None,
        X_test: Optional[np.ndarray] = None,
        y_test: Optional[np.ndarray] = None,
        test_size: Optional[float] = 0.1,
        kernel: Optional[GPy.kern.Kern] = None,
        standardize: bool = True,
        noise_variance: float = 1.0,
        auto_kernel_selection: bool = False
    ):
        """
        Initialize the Gaussian Process model.

        Args:
            kernel: GPy kernel object. If None, uses Matern32 kernel
            standardize: Whether to standardize the input and output data
            noise_variance: Initial noise variance for the GP
            auto_kernel_selection: Whether to automatically select the best kernel
        """
        self.available_kernels = {
            'Matern32': lambda dim: GPy.kern.Matern32(input_dim=dim),
            'Matern52': lambda dim: GPy.kern.Matern52(input_dim=dim),
            'RBF': lambda dim: GPy.kern.RBF(input_dim=dim),
            'Linear': lambda dim: GPy.kern.Linear(input_dim=dim),
            'Exponential': lambda dim: GPy.kern.Exponential(input_dim=dim),
            'Matern32+Linear': lambda dim: GPy.kern.Matern32(input_dim=dim) + GPy.kern.Linear(input_dim=dim),
            'RBF+Linear': lambda dim: GPy.kern.RBF(input_dim=dim) + GPy.kern.Linear(input_dim=dim)
        }

        self.auto_kernel_selection = auto_kernel_selection
        self.kernel = kernel if kernel is not None else GPy.kern.Matern52(input_dim=1)
        self.standardize = standardize
        self.noise_variance = noise_variance
        self.model = None
        self.X_scaler = StandardScaler() if standardize else None
        self.y_scaler = StandardScaler() if standardize else None
        self.best_kernel_name = None
        self.kernel_scores = None
        self.test_size = test_size

        if X is not None and y is not None:
            if X_test is not None and y_test is not None:
                self.set_data(X, y, X_test, y_test)
            else:
                self.set_data(X, y)

    def set_data(self,
                 X: np.ndarray,
                 y: np.ndarray,
                 X_test: Optional[np.ndarray] = None,
                 y_test: Optional[np.ndarray] = None):

        # Store full dataset
        self.X = np.array(X)
        self.y = np.array(y)

        # Ensure correct shapes
        if len(self.X.shape) == 1:
            self.X = self.X.reshape(-1, 1)
        if len(self.y.shape) == 1:
            self.y = self.y.reshape(-1, 1)

        # Split data if test set not provided
        if X_test is None or y_test is None:
            train_idx = np.random.choice(len(self.X), int((1-self.test_size)*len(self.X)), replace=False)
            test_idx = np.array(list(set(range(len(self.X))) - set(train_idx)))

            self.X_train = self.X[train_idx]
            self.y_train = self.y[train_idx]
            self.X_test = self.X[test_idx]
            self.y_test = self.y[test_idx]
        else:
            self.X_test = np.array(X_test)
            self.y_test = np.array(y_test)
            if len(self.X_test.shape) == 1:
                self.X_test = self.X_test.reshape(-1, 1)
            if len(self.y_test.shape) == 1:
                self.y_test = self.y_test.reshape(-1, 1)
            self.X_train = self.X
            self.y_train = self.y

        # Store original data before standardization
        self.X_train_original = self.X_train.copy()
        self.y_train_original = self.y_train.copy()
        self.X_test_original = self.X_test.copy()
        self.y_test_original = self.y_test.copy()

        # Standardize if requested
        if self.standardize:
            self.X_train = self.X_scaler.fit_transform(self.X_train)
            self.y_train = self.y_scaler.fit_transform(self.y_train)
            if self.X_test is not None:
                self.X_test = self.X_scaler.transform(self.X_test)
                self.y_test = self.y_scaler.transform(self.y_test)

    def _evaluate_kernel(
        self,
        kernel: GPy.kern.Kern,
        n_splits: int = 5
    ) -> float:
        model = GPy.models.GPRegression(
            X=self.X_train,
            Y=self.y_train,
            kernel=kernel.copy(),
            noise_var = self.noise_variance
        )

        model = self.optimize_with_de(model.copy())

        y_pred, _ = model.predict(self.X_test)
        mse = np.mean((self.y_test - y_pred) ** 2)
        return mse, model

    def _select_best_kernel(
        self,
       ) -> Tuple[GPy.kern.Kern, str, Dict[str, float]]:
        """
        Select the best kernel based on cross-validation performance.

        Returns:
            Tuple of (best kernel, kernel name, all kernel scores)
        """
        input_dim = self.X.shape[1]
        best_score = np.inf

        for name, kernel_func in self.available_kernels.items():
            print(f'Optimizing the kernel {name}')
            kernel = kernel_func(input_dim)
            score, model = self._evaluate_kernel(kernel)
            if score < best_score:
                self.kernel = kernel
                self.model = model

    def fit(
        self,
        X: np.ndarray,
        y: np.ndarray,
        X_test: Optional[np.ndarray] = None,
        y_test: Optional[np.ndarray] = None,
        optimize: bool = True,
        num_restarts: int = 5,
        test_size: float = 0.1
    ) -> None:
        """
        Fit the Gaussian Process model to the training data.

        Args:
            X: Training input data of shape (n_samples, n_features)
            y: Training target values of shape (n_samples, 1)
            X_test: Optional test input data. If None, splits X using test_size
            y_test: Optional test target values. If None, splits y using test_size
            optimize: Whether to optimize the kernel hyperparameters
            num_restarts: Number of random restarts for optimization
            test_size: Fraction of data to use for testing if X_test/y_test not provided
        """

        if X is not None and y is not None:
            if X_test is not None and y_test is not None:
                self.set_data(X, y, X_test, y_test)
            else:
                self.set_data(X, y)

        # Select best kernel if requested
        if self.auto_kernel_selection:
            self._select_best_kernel()
        else:
            # Create and fit the GP model
            self.model = GPy.models.GPRegression(
                X=self.X_train,
                Y=self.y_train,
                kernel=self.kernel,
                noise_var=self.noise_variance
            )

            # Optimize hyperparameters if requested
            if optimize:
                # self.model.optimize_restarts(num_restarts=num_restarts)
                self.model = self.optimize_with_de(self.model)

    def predict(
        self,
        X: np.ndarray,
        return_std: bool = True,
        full_cov: bool = False
    ) -> Union[np.ndarray, Tuple[np.ndarray, np.ndarray]]:
        """
        Make predictions with the trained GP model.

        Args:
            X: Test input data of shape (n_samples, n_features)
            return_std: Whether to return standard deviation
            full_cov: Whether to return full covariance matrix

        Returns:
            If return_std is False, returns mean predictions
            If return_std is True, returns tuple (mean, std)
        """
        if self.model is None:
            raise ValueError("Model has not been fitted yet.")

        # Ensure correct shape
        X = np.array(X)
        if len(X.shape) == 1:
            X = X.reshape(-1, 1)

        # Standardize if necessary
        X_transformed = self.X_scaler.transform(X) if self.standardize else X

        # Make predictions
        mean, var = self.model.predict(X_transformed, full_cov=full_cov)

        # Transform predictions back if standardized
        if self.standardize:
            mean = self.y_scaler.inverse_transform(mean)
            if not full_cov:
                var = var * (self.y_scaler.scale_**2)
            else:
                var = var * (self.y_scaler.scale_**2)

        if return_std:
            return mean, np.sqrt(var)
        return mean

    def get_kernel_params(self) -> dict:
        """
        Get the current kernel parameters.

        Returns:
            Dictionary of kernel parameters
        """
        if self.model is None:
            raise ValueError("Model has not been fitted yet.")
        return self.model.kern.param_array.tolist()

    def get_kernel_info(self) -> Dict:
        """
        Get information about kernel selection results.

        Returns:
            Dictionary containing kernel selection information
        """
        if not self.auto_kernel_selection:
            return {"auto_selection": False, "current_kernel": self.kernel.name}

        return {
            "auto_selection": True,
            "best_kernel": self.best_kernel_name,
            "kernel_scores": self.kernel_scores,
            "current_kernel": self.kernel.name
        }

    def update(
        self,
        X_new: np.ndarray,
        y_new: np.ndarray,
        optimize: bool = True,
        replace_values: bool = False
    ) -> None:
        """
        Update the GP model with new observations.

        Args:
            X_new: New input data
            y_new: New target values
            optimize: Whether to re-optimize hyperparameters
            replace_values: If True, replace existing data with new data.
                          If False, append new data to existing data.
        """
        if self.model is None:
            self.fit(X_new, y_new, optimize=optimize)
            return

        X_new = np.array(X_new)
        y_new = np.array(y_new)
        if len(X_new.shape) == 1:
            X_new = X_new.reshape(-1, 1)
        if len(y_new.shape) == 1:
            y_new = y_new.reshape(-1, 1)

        if self.standardize:
            X_new = self.X_scaler.transform(X_new)
            y_new = self.y_scaler.transform(y_new)

        if replace_values:
            self.model.set_XY(
                X=X_new,
                Y=y_new
            )
        else:
            self.model.set_XY(
                X=np.vstack([self.model.X, X_new]),
                Y=np.vstack([self.model.Y, y_new])
            )

        if optimize:
            # self.model.optimize()
            self.optimize_with_de()

    def optimize_with_de(
        self,
        model = None,
        **optimizer_kwargs
    ) -> None:
        """
        Optimize GP parameters using a custom optimization method.

        Args:
            optimizer_func: Custom optimization function that takes objective and gradient functions
            initial_params: Initial parameters for optimization. If None, uses current parameters
            optimizer_kwargs: Additional arguments for the optimizer function
        """
        if model is None:
            raise ValueError("Please provide a model")

        # Get parameters
        params = []
        params_names = model.parameter_names()
        params_values = model.param_array
        letters = list('abcdefghijklmnopqrstuvwxyz')

        for i, (name, value) in enumerate(zip(params_names, params_values)):
            params.append({
                'name': letters[i],
                'min': float(1e-10),
                'max': float(5e1),
                'default': float(value),
                'scale':'log'
            })
        params_df = pd.DataFrame(params)

        # Define objective function (negative log likelihood)
        def evaluate_multiple_parameters(parameters: list[dict] = None, **kwargs):
            metrics = []
            for p in parameters:
                arr = np.array(list(p.values()))
                model[:] = arr
                likelihood_metric = -model.log_likelihood()

                y_pred, _ = model.predict(self.X_test)
                mse = np.mean((self.y_test - y_pred) ** 2)
                test_metric = mse * 0

                metrics.append(likelihood_metric + test_metric)
            responses = {'metrics': metrics}
            return responses

        from ..differential_evolution.Differential_evolution import Differential_evolution
        # Initialize optimizer
        optimizer = Differential_evolution(parameters = params_df,
                                           eval_func = evaluate_multiple_parameters,
                                           pop_size = 20,
                                           metric_threshold = -1e10,
                                           max_iterations = 1000,
                                           max_iter_without_improvement = 50)

        # Run optimization
        optimizer.run_optimization()

        best_params = np.array(list(optimizer.get_best_parameters().values()))
        model[:] = best_params
        return model

    def plot_accuracy(
        self,
        title: str = "Prediction Accuracy",
        save_path: Optional[str] = None
    ) -> None:
        """
        Plot predicted vs true values to evaluate model accuracy for both training and test data.

        Args:
            title: Plot title
            save_path: If provided, save the plot to this path
        """
        if self.model is None:
            raise ValueError("Model has not been fitted yet.")

        # Get predictions for both train and test sets using original X values
        y_train_pred = self.predict(self.X_train_original, return_std=False)
        y_test_pred = self.predict(self.X_test_original, return_std=False)
        y_true_train = self.y_train_original
        y_true_test = self.y_test_original

        # Create figure
        plt.figure(figsize=(8, 8))

        # Plot predictions vs true values
        plt.scatter(y_true_train, y_train_pred, alpha=0.5, color='blue', label='Training Data')
        plt.scatter(y_true_test, y_test_pred, alpha=0.5, color='red', label='Test Data')

        # Plot perfect prediction line
        all_y_true = np.concatenate([y_true_train, y_true_test])
        all_y_pred = np.concatenate([y_train_pred, y_test_pred])
        min_val = min(all_y_true.min(), all_y_pred.min())
        max_val = max(all_y_true.max(), all_y_pred.max())
        plt.plot([min_val, max_val], [min_val, max_val], 'k--', label='Perfect Prediction')

        # Calculate and display R² scores
        r2_train = np.corrcoef(y_true_train.flatten(), y_train_pred.flatten())[0, 1]**2
        r2_test = np.corrcoef(y_true_test.flatten(), y_test_pred.flatten())[0, 1]**2
        plt.text(0.05, 0.95, f'Train R² = {r2_train:.3f}\nTest R² = {r2_test:.3f}',
                transform=plt.gca().transAxes,
                bbox=dict(facecolor='white', alpha=0.8))

        plt.xlabel('True Values')
        plt.ylabel('Predicted Values')
        plt.title(title)
        plt.grid(True)
        plt.legend()
        plt.axis('equal')

        if save_path:
            plt.savefig(save_path)
        plt.show()

    def sample_prior(
        self,
        X: np.ndarray,
        n_samples: int = 1,
        seed: Optional[int] = None
    ) -> np.ndarray:
        """
        Draw samples from the prior distribution.

        Args:
            X: Input locations to sample at
            n_samples: Number of samples to draw
            seed: Random seed for reproducibility

        Returns:
            Array of samples with shape (n_samples, n_locations)
        """
        if seed is not None:
            np.random.seed(seed)

        X = np.array(X)
        if len(X.shape) == 1:
            X = X.reshape(-1, 1)

        if self.standardize:
            X = self.X_scaler.transform(X)

        K = self.kernel.K(X)
        L = np.linalg.cholesky(K + 1e-10 * np.eye(len(X)))
        samples = np.random.standard_normal((len(X), n_samples))
        samples = L @ samples

        if self.standardize:
            samples = self.y_scaler.inverse_transform(samples)

        return samples.T

    def sample_posterior(
        self,
        X: np.ndarray,
        n_samples: int = 1,
        seed: Optional[int] = None
    ) -> np.ndarray:
        """
        Draw samples from the posterior distribution.

        Args:
            X: Input locations to sample at
            n_samples: Number of samples to draw
            seed: Random seed for reproducibility

        Returns:
            Array of samples with shape (n_samples, n_locations)
        """
        if self.model is None:
            raise ValueError("Model has not been fitted yet.")

        if seed is not None:
            np.random.seed(seed)

        X = np.array(X)
        if len(X.shape) == 1:
            X = X.reshape(-1, 1)

        X_transformed = self.X_scaler.transform(X) if self.standardize else X

        mean, var = self.model.predict(X_transformed, full_cov=True)
        L = np.linalg.cholesky(var + 1e-10 * np.eye(len(X)))
        samples = np.random.standard_normal((len(X), n_samples))
        samples = mean + L @ samples

        if self.standardize:
            samples = self.y_scaler.inverse_transform(samples)

        return samples.T


if __name__ == "__main__":
    # Generate sample data
    np.random.seed(42)

    # Generate non-linear function with noise
    X = np.linspace(0, 10, 100).reshape(-1, 1)
    y = np.sin(X) + 0.3 * np.cos(2*X) + 0.05 * np.random.randn(100, 1)

    # Create and fit GP model with automatic kernel selection
    gp = Gaussian_process(auto_kernel_selection=True, standardize=True)
    gp.fit(X, y)  # Will automatically split into train/test

    # Print kernel selection results
    kernel_info = gp.get_kernel_info()
    print("\nKernel Selection Results:")
    print(f"Best kernel: {kernel_info['best_kernel']}")
    print("\nKernel scores:")
    for kernel, score in kernel_info['kernel_scores'].items():
        print(f"{kernel}: {score:.3f}")

    # Plot predictions vs true values for both train and test sets
    gp.plot_accuracy(title="GP Regression Accuracy")

    # Plot the function and predictions
    plt.figure(figsize=(12, 6))

    # Sort points for smooth plotting
    sort_idx = np.argsort(X.flatten())
    X_sorted = X[sort_idx]
    y_sorted = y[sort_idx]

    # Get predictions with uncertainty
    y_pred, y_std = gp.predict(X_sorted)

    plt.scatter(gp.X_train_original, gp.y_train_original, color='blue', label='Training Data')
    plt.scatter(gp.X_test_original, gp.y_test_original, color='red', label='Test Data')
    plt.plot(X_sorted, y_pred, 'k', label='Predictions')
    plt.fill_between(X_sorted.flatten(),
                    (y_pred - 2*y_std).flatten(),
                    (y_pred + 2*y_std).flatten(),
                    color='black', alpha=0.2,
                    label='95% Confidence')

    plt.xlabel('X')
    plt.ylabel('y')
    plt.title('Gaussian Process Regression')
    plt.legend()
    plt.grid(True)
    plt.show()

    # Example of sampling from the prior and posterior
    X_sample = np.linspace(-2, 12, 200).reshape(-1, 1)

    # Draw samples from prior
    prior_samples = gp.sample_prior(X_sample, n_samples=3, seed=42)

    plt.figure(figsize=(12, 6))
    plt.plot(X_sample, prior_samples.T, '--', alpha=0.5, label=['Prior Sample 1', 'Prior Sample 2', 'Prior Sample 3'])
    plt.xlabel('X')
    plt.ylabel('y')
    plt.title('Samples from Prior Distribution')
    plt.legend()
    plt.grid(True)
    plt.show()

    # Draw samples from posterior
    posterior_samples = gp.sample_posterior(X_sample, n_samples=3, seed=42)

    plt.figure(figsize=(12, 6))
    plt.scatter(gp.X_train_original, gp.y_train_original, color='blue', label='Training Data')
    plt.plot(X_sample, posterior_samples.T, '--', alpha=0.5, label=['Posterior Sample 1', 'Posterior Sample 2', 'Posterior Sample 3'])
    plt.xlabel('X')
    plt.ylabel('y')
    plt.title('Samples from Posterior Distribution')
    plt.legend()
    plt.grid(True)
    plt.show()
