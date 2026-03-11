#pragma once

#include <utility>
#include <variant>

namespace de {
namespace optimization {

// A factor can be a fixed value or an adaptive range (uniform sampling)
using Factor = std::variant<double, std::pair<double, double>>;

enum class OptDirection { Minimize, Maximize };

enum class BoundaryHandling { RandomFromTarget, Clamp, Random };

struct DEConfig {
    int seed = -1;                           // -1 = random seed
    int pop_size = 100;
    int max_iterations = 1000;
    double metric_threshold = 0.0;
    int max_iter_without_improvement = 50;
    double improvement_threshold = 0.01;

    Factor mutation_factor_1 = std::make_pair(0.7, 1.1);
    Factor mutation_factor_2 = std::make_pair(0.2, 0.6);
    Factor mutation_factor_3 = std::make_pair(0.0, 0.3);
    Factor recombination_factor = std::make_pair(0.8, 0.97);

    OptDirection direction = OptDirection::Minimize;
    BoundaryHandling boundary_handling = BoundaryHandling::RandomFromTarget;

    bool defaults_in_init_pop = false;
    double defaults_in_init_pop_ratio = 0.2;
};

} // namespace optimization
} // namespace de
