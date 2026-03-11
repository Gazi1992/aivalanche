# Optimization — Differential Evolution

A C++ implementation of the Differential Evolution (DE) algorithm for global optimization. Works with the [parameters](../parameters/) package for parameter management and normalization.

## Quick Start

```cpp
#include <optimization/differential_evolution.hpp>
#include <parameters/parameter_types.hpp>
#include <parameters/parameters_collection.hpp>

using namespace de::parameters;
using namespace de::optimization;

// 1. Define parameters
ParametersCollection params;
params.add(std::make_unique<ContinuousParameter>("x", -5.0, 5.0));
params.add(std::make_unique<ContinuousParameter>("y", -5.0, 5.0));

// 2. Define evaluation function
auto eval = [](const std::vector<std::unordered_map<std::string, double>>& pop)
    -> std::vector<double> {
    std::vector<double> metrics;
    for (const auto& p : pop) {
        double x = p.at("x"), y = p.at("y");
        // Rosenbrock function — minimum at (1, 1)
        metrics.push_back((1-x)*(1-x) + 100*(y-x*x)*(y-x*x));
    }
    return metrics;
};

// 3. Configure and run
DEConfig config;
config.seed = 42;
config.pop_size = 80;
config.max_iterations = 500;
config.direction = OptDirection::Minimize;

DifferentialEvolution de(std::move(params), eval, config);
DEResult result = de.run();

// 4. Use results
std::cout << "Best metric: " << result.best_metric << "\n";
std::cout << "x = " << result.best_parameters.at("x") << "\n";
std::cout << "y = " << result.best_parameters.at("y") << "\n";
std::cout << "Stopped: " << result.stop_reason << "\n";
```

## API

### DifferentialEvolution

**Constructor:**
```cpp
DifferentialEvolution(
    parameters::ParametersCollection params,
    EvalFunction eval_func,
    DEConfig config = DEConfig{}
);
```

**Methods:**

| Method | Description |
|--------|-------------|
| `run()` | Execute optimization, returns `DEResult` |
| `abort()` | Thread-safe abort signal (sets atomic flag) |
| `set_initial_population(matrix)` | Provide initial population (rows = members, cols = variable params, original domain values) |
| `set_iteration_callback(cb)` | Register per-iteration callback |

### EvalFunction

The evaluation function receives a batch of parameter sets and returns a metric for each:

```cpp
using EvalFunction = std::function<std::vector<double>(
    const std::vector<std::unordered_map<std::string, double>>& parameters
)>;
```

- **Input:** vector of parameter maps — one map per population member, keys are parameter names, values are in the original domain. Fixed parameters are included with their default values.
- **Output:** vector of metric values, one per member, same order as input.

### IterCallback

Optional callback invoked after each iteration:

```cpp
using IterCallback = std::function<void(
    int iteration,
    double best_metric,
    const std::unordered_map<std::string, double>& best_params
)>;
```

```cpp
de.set_iteration_callback([](int iter, double metric, const auto& params) {
    std::cout << "Iteration " << iter << ": " << metric << "\n";
});
```

### DEConfig

```cpp
struct DEConfig {
    int seed = -1;                    // -1 = random seed
    int pop_size = 100;               // population size
    int max_iterations = 1000;        // max iterations
    double metric_threshold = 0.0;    // stop when metric reaches this
    int max_iter_without_improvement = 50;  // early stopping patience
    double improvement_threshold = 0.01;    // min relative improvement to count

    // Mutation/crossover factors — fixed value or adaptive range
    Factor mutation_factor_1 = {0.7, 1.1};      // F1: general mutation
    Factor mutation_factor_2 = {0.2, 0.6};      // F2: best-directed mutation
    Factor mutation_factor_3 = {0.0, 0.3};      // F3: best-target mutation
    Factor recombination_factor = {0.8, 0.97};  // CR: crossover probability

    OptDirection direction = OptDirection::Minimize;
    BoundaryHandling boundary_handling = BoundaryHandling::RandomFromTarget;

    bool defaults_in_init_pop = false;        // seed defaults into initial pop
    double defaults_in_init_pop_ratio = 0.2;  // fraction of pop to fill with defaults
};
```

**Factor type:**
```cpp
using Factor = std::variant<double, std::pair<double, double>>;
```

A fixed value (e.g., `0.8`) or an adaptive range (e.g., `{0.5, 0.9}`) sampled uniformly per member per iteration.

### Enums

```cpp
enum class OptDirection { Minimize, Maximize };

enum class BoundaryHandling {
    RandomFromTarget,  // random between boundary and target value
    Clamp,             // clamp to boundary
    Random             // random within full [0, 1] range
};
```

### DEResult

```cpp
struct DEResult {
    std::unordered_map<std::string, double> best_parameters;
    double best_metric;
    int iterations_run;
    int nr_evaluations;
    std::string stop_reason;
    DEHistory history;
};
```

**Possible stop reasons:**
- `"metric threshold reached"`
- `"maximum iterations without improvement reached"`
- `"maximum iterations reached"`
- `"optimization aborted"`

### DEHistory

Full iteration-by-iteration history for analysis.

```cpp
const auto& iters = result.history.iterations();  // vector<IterationRecord>
const auto& bests = result.history.bests();        // vector<BestRecord>
```

**IterationRecord** — complete population state at each iteration:
- `iteration`, `trials_normed`, `trials_unscaled`, `trials_metric`
- `survivors_normed`, `survivors_unscaled`, `survivors_metric`

**BestRecord** — best solution at each improvement:
- `iteration`, `params_normed`, `params_unscaled`, `metric`

## Examples

### Maximization

```cpp
ParametersCollection params;
params.add(std::make_unique<ContinuousParameter>("x", 0.0, 6.0));

auto eval = [](const std::vector<std::unordered_map<std::string, double>>& pop)
    -> std::vector<double> {
    std::vector<double> metrics;
    for (const auto& p : pop) {
        double x = p.at("x");
        metrics.push_back(-(x - 3.0) * (x - 3.0) + 9.0);  // max at x=3, f=9
    }
    return metrics;
};

DEConfig config;
config.direction = OptDirection::Maximize;
config.metric_threshold = 8.99;

DifferentialEvolution de(std::move(params), eval, config);
DEResult result = de.run();
// result.best_parameters["x"] ≈ 3.0, result.best_metric ≈ 9.0
```

### Mixed Parameter Types

```cpp
ParametersCollection params;
params.add(std::make_unique<DiscreteParameter>(
    "batch_size", std::vector<double>{16, 32, 64, 128, 256}));
params.add(std::make_unique<ContinuousParameter>(
    "learning_rate", 1e-5, 1.0, 1e-3, Scale::Logarithmic, false));

auto eval = [](const std::vector<std::unordered_map<std::string, double>>& pop)
    -> std::vector<double> {
    std::vector<double> metrics;
    for (const auto& p : pop) {
        double batch = p.at("batch_size");
        double lr = p.at("learning_rate");
        // your objective function here
        metrics.push_back(some_objective(batch, lr));
    }
    return metrics;
};

DifferentialEvolution de(std::move(params), eval);
DEResult result = de.run();
```

### Abort from Callback

```cpp
DifferentialEvolution de(std::move(params), eval, config);

de.set_iteration_callback([&de](int iter, double metric, const auto& params) {
    if (some_external_condition()) {
        de.abort();
    }
});

DEResult result = de.run();
// result.stop_reason == "optimization aborted"
```

## Algorithm

The mutation strategy combines three components:

```
donor = r1 + F1*(r2 - r3) + F2*(best - r1) + F3*(best - target)
```

- **F1** — general diversity from random population members
- **F2** — guidance toward the current best solution
- **F3** — awareness of the current target vector

Crossover is binomial with probability CR, ensuring at least one dimension comes from the donor. Selection is greedy: each trial replaces its target only if it improves the metric.

Population is initialized using a **Halton sequence** for quasi-random, space-filling coverage.

## Building

From the parent `c++/` directory:

```bash
cmake -B build -G Ninja
cmake --build build
ctest --test-dir build --output-on-failure
```
