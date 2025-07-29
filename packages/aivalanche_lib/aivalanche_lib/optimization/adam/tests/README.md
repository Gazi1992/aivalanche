# ADAM Optimizer Tests

This directory contains test scripts for the ADAM (Adaptive Moment Estimation) optimizer.

## Test Files

- `test_adam_basic.py` - Basic functionality tests including:
  - Simple optimization problems (sphere, rosenbrock)
  - Learning rate decay
  - AMSGrad variant
  - Gradient estimation methods
  - Boundary handling
  - Callbacks
  - Stopping criteria

- `test_adam_advanced.py` - Advanced features testing:
  - Animations for 2D functions
  - High-dimensional problems
  - Fixed parameters handling
  - Comparison with other optimizers
  - Restart capability
  - Noisy objective functions

- `test_adam_simple.py` - Minimal test without external dependencies

## Test Results

Test results are saved in directories following the pattern:
- `test_results_<function_name>` (e.g., `test_results_sphere_2d`)
- `test_results_animations_<function_name>` for animation outputs

Each test results directory typically contains:
- `best_parameters.csv` - Best found parameters
- `optimization_info.json` - Optimization configuration and results
- `metrics_evolution.png` - Plot of metric evolution
- `gradient_norm.png` - Plot of gradient norm evolution
- `learning_rate.png` - Plot of learning rate evolution
- `adam_<function>_animation.gif` - Animation of optimization process (for 2D functions)
- `adam_<function>_summary.png` - Comprehensive summary plot

## Running Tests

To run the tests, ensure you have the required dependencies installed:
```bash
pip install numpy pandas matplotlib
```

Then run:
```bash
python test_adam_basic.py
python test_adam_advanced.py
```

The tests will create result directories in the same location as the test scripts, following the same pattern as other optimizers in the aivalanche_lib package.