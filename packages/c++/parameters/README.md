# Parameters

A C++ library for defining, managing, and normalizing optimization parameters. Supports continuous, discrete, and categorical parameter types with automatic scale detection and batch operations via Eigen.

## Parameter Types

### ContinuousParameter

Real-valued parameters within a range.

```cpp
#include <parameters/parameter_types.hpp>

using namespace de::parameters;

// Basic: auto-detects scale, default at midpoint
ContinuousParameter p("temperature", 0.0, 100.0);

// Full control
ContinuousParameter p("learning_rate", 1e-5, 1.0, 1e-3,
                       Scale::Logarithmic, false,
                       Mode::Variable, "Step size for optimizer");
```

**Constructor:**
```cpp
ContinuousParameter(
    const std::string& name,
    double min_val,
    double max_val,
    double default_val = NaN,         // defaults to midpoint
    Scale scale = Scale::Linear,
    bool auto_scale = true,           // auto-detect log scale
    Mode mode = Mode::Variable,
    const std::string& description = ""
);
```

**Key methods:**
- `norm(value)` — normalize to [0, 1]
- `unnorm(norm_value)` — denormalize to original domain
- `sample_random(rng)` — uniform random sample within bounds
- `min_val()`, `max_val()`, `get_default()`, `get_scale()`

### DiscreteParameter

Parameters restricted to specific values.

```cpp
// From a range with step size
DiscreteParameter layers("num_layers", 1.0, 10.0, 1.0);  // {1, 2, ..., 10}

// From an explicit list
DiscreteParameter batch("batch_size", std::vector<double>{16, 32, 64, 128, 256});
```

**Constructors:**
```cpp
// Range-based
DiscreteParameter(name, min_val, max_val, step = 1.0, default_val = NaN,
                  scale = Scale::Linear, auto_scale = true,
                  mode = Mode::Variable, description = "");

// Values-list
DiscreteParameter(name, std::vector<double> values, default_val = NaN,
                  scale = Scale::Linear, auto_scale = true,
                  mode = Mode::Variable, description = "");
```

**Key methods:**
- `values()` — all valid values (sorted, deduplicated)
- `snap_to_nearest(value)` — snap to closest valid value
- `norm(value)` / `unnorm(norm_value)` — normalization with snapping

### CategoricalParameter

Named categories mapped to indices internally.

```cpp
CategoricalParameter optimizer("optimizer", {"sgd", "adam", "rmsprop"}, "adam");
```

**Constructor:**
```cpp
CategoricalParameter(
    const std::string& name,
    std::vector<std::string> categories,
    const std::string& default_val = "",  // defaults to first category
    Mode mode = Mode::Variable,
    const std::string& description = ""
);
```

**Key methods:**
- `categories()` — all category strings
- `num_categories()` — count
- `norm_category("adam")` — normalize by name to [0, 1]
- `unnorm_category(0.5)` — denormalize to category string
- `index_of("adam")` — get index (-1 if not found)
- `category_at(1)` — get category by index

## Enums

```cpp
enum class Scale { Linear, Logarithmic };
enum class Mode  { Variable, Fixed };
```

- **Scale::Logarithmic** is auto-detected when the range ratio exceeds 100x.
- **Mode::Fixed** locks a parameter to its default value and excludes it from optimization vectors.

## ParametersCollection

Manages a set of mixed parameters with batch normalization.

```cpp
#include <parameters/parameter_types.hpp>
#include <parameters/parameters_collection.hpp>

using namespace de::parameters;

ParametersCollection params;
params.add(std::make_unique<ContinuousParameter>("x", -5.0, 5.0));
params.add(std::make_unique<ContinuousParameter>("y", -5.0, 5.0));
params.add(std::make_unique<ContinuousParameter>("fixed_z", 0.0, 1.0, 0.5,
               Scale::Linear, false, Mode::Fixed));
params.sort_by_name();  // must be called after adding all parameters
```

**Key methods:**

| Method | Description |
|--------|-------------|
| `add(unique_ptr)` | Add a parameter (throws on duplicate name) |
| `sort_by_name()` | Sort alphabetically (call once, after adding all params) |
| `size()` | Total parameter count |
| `variable_count()` | Count of variable (non-fixed) parameters |
| `names()` | All parameter names |
| `variable_names()` | Names of variable parameters only |
| `at(i)` / `by_name(name)` | Access parameter by index or name |
| `norm_all(values)` | Normalize an `Eigen::VectorXd` of variable values to [0, 1] |
| `unnorm_all(normed)` | Denormalize from [0, 1] to original domain |
| `unnorm_matrix(normed)` | Batch denormalize a population matrix |
| `normalized_defaults()` | Normalized defaults for all variable parameters |
| `to_param_map(variable_values)` | Convert to `unordered_map<string, double>` including fixed params |

### Example: Normalization Round-Trip

```cpp
ParametersCollection params;
params.add(std::make_unique<ContinuousParameter>("a", 0.0, 10.0));
params.add(std::make_unique<ContinuousParameter>("b", 0.0, 100.0));
params.sort_by_name();

Eigen::VectorXd vals(2);
vals << 5.0, 50.0;

auto normed   = params.norm_all(vals);    // [0.5, 0.5]
auto restored = params.unnorm_all(normed); // [5.0, 50.0]
```

### Example: Variable vs Fixed Parameters

```cpp
ParametersCollection params;
params.add(std::make_unique<ContinuousParameter>("var", 0.0, 10.0, 5.0,
               Scale::Linear, false, Mode::Variable));
params.add(std::make_unique<ContinuousParameter>("fix", 0.0, 1.0, 0.42,
               Scale::Linear, false, Mode::Fixed));
params.sort_by_name();

// Only variable parameters are in the vector
Eigen::VectorXd var_vals(1);
var_vals << 7.0;

// to_param_map includes fixed parameters at their default
auto map = params.to_param_map(var_vals);
// map["var"] == 7.0
// map["fix"] == 0.42
```

## Transforms

The transforms module handles value scaling between original and normalized domains.

```cpp
#include <parameters/transforms.hpp>

using namespace de::parameters;

LogTransform t;
t.scale(100.0);    // 2.0  (log10)
t.unscale(2.0);    // 100.0

// Auto-detect which scale to use
Scale s = auto_detect_scale(0.01, 100.0);  // Scale::Logarithmic

// Factory function
auto transform = make_transform(Scale::Logarithmic, 1.0, 1000.0);  // LogTransform
```

**Available transforms:**
- `NoTransform` — identity (linear scale)
- `LogTransform` — log10 for positive ranges
- `NegLogTransform` — -log10(-x) for negative ranges

## Building

This is a CMake library. From the parent `c++/` directory:

```bash
cmake -B build -G Ninja
cmake --build build
ctest --test-dir build --output-on-failure
```
