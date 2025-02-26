import numpy as np, pandas as pd

class Adam:
    def __init__(self,
                 eval_func: callable = None,                            # function that is used for the evaluation of the fittness of the parameter sets
                 eval_func_args: dict = None,                           # extra arguments to pass to the evaluation function
                 callback_after_first_iter: callable = None,            # callback that is called after the first iteration
                 callback_after_each_iter: callable = None,             # callback that is called after each iteration
                 callback_after_last_iter: callable = None,             # callback that is called after the last iteration
                 callback_after_better_solution_found: callable = None, # callback that is called after finding a better solution
                 parameters: pd.DataFrame = None,                       # the parameters to be optimized
                 learning_rate = 0.001,
                 beta1 = 0.9,
                 beta2 = 0.999,
                 epsilon = 1e-8):
        """
        Initialize Adam optimizer.

        Args:
            learning_rate (float): The learning rate (α)
            beta1 (float): Exponential decay rate for first moment estimates
            beta2 (float): Exponential decay rate for second moment estimates
            epsilon (float): Small constant to prevent division by zero
        """
        self.learning_rate = learning_rate
        self.beta1 = beta1
        self.beta2 = beta2
        self.epsilon = epsilon
        self.m = None  # First moment estimate
        self.v = None  # Second moment estimate
        self.t = 0     # Timestep

    def step(self, params, gradients):
        """
        Perform one optimization step.

        Args:
            params (np.ndarray): Current parameter values
            gradients (np.ndarray): Gradient of the objective function

        Returns:
            np.ndarray: Updated parameter values
        """
        if self.m is None:
            self.m = np.zeros_like(params)
            self.v = np.zeros_like(params)

        self.t += 1

        # Update biased first moment estimate
        self.m = self.beta1 * self.m + (1 - self.beta1) * gradients

        # Update biased second raw moment estimate
        self.v = self.beta2 * self.v + (1 - self.beta2) * np.square(gradients)

        # Compute bias-corrected first moment estimate
        m_hat = self.m / (1 - self.beta1**self.t)

        # Compute bias-corrected second raw moment estimate
        v_hat = self.v / (1 - self.beta2**self.t)

        # Update parameters
        params = params - self.learning_rate * m_hat / (np.sqrt(v_hat) + self.epsilon)

        return params

# Example usage:
def example():
    # Create optimizer
    optimizer = Adam(learning_rate=0.01)

    # Initialize parameters
    params = np.array([1.0, 2.0, 3.0])

    # In a real scenario, you would compute these gradients
    gradients = np.array([0.1, -0.2, 0.3])

    # Perform an optimization step
    new_params = optimizer.step(params, gradients)

    print("Original parameters:", params)
    print("Gradients:", gradients)
    print("Updated parameters:", new_params)

if __name__ == "__main__":
    example()
