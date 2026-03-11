#pragma once

#include <atomic>
#include <functional>
#include <limits>
#include <optional>
#include <random>
#include <string>
#include <unordered_map>
#include <vector>

#include <Eigen/Dense>

#include <parameters/parameters_collection.hpp>
#include "de_config.hpp"
#include "de_history.hpp"

namespace de {
namespace optimization {

// Evaluation function signature:
// Takes a vector of parameter maps (one per population member)
// Returns a vector of metric values (one per member)
using EvalFunction = std::function<std::vector<double>(
    const std::vector<std::unordered_map<std::string, double>>& parameters
)>;

// Optional callback after each iteration
using IterCallback = std::function<void(
    int iteration,
    double best_metric,
    const std::unordered_map<std::string, double>& best_params
)>;

struct DEResult {
    std::unordered_map<std::string, double> best_parameters;
    double best_metric;
    int iterations_run;
    int nr_evaluations;
    std::string stop_reason;
    DEHistory history;
};

class DifferentialEvolution {
public:
    DifferentialEvolution(parameters::ParametersCollection params,
                          EvalFunction eval_func,
                          DEConfig config = DEConfig{});

    // Optionally set initial population (rows = members, cols = variable params, in original domain)
    void set_initial_population(const Eigen::MatrixXd& init_pop);

    // Optionally set a callback invoked after each iteration
    void set_iteration_callback(IterCallback cb);

    // Run the full optimization. Returns when stopping criteria are met.
    DEResult run();

    // Request abort (thread-safe)
    void abort();

private:
    // ---- Core algorithm steps ----
    void initialize();
    void generate_initial_population();
    void generate_donors();
    void generate_trials();
    void evaluate_trials();
    void determine_survivors();
    bool determine_best();
    bool check_stopping_criteria();
    void record_history();

    // ---- Mutation / crossover ----
    void mutate();
    void crossover();
    void handle_boundary_violations();

    // ---- Utilities ----
    Eigen::VectorXd sample_factor(const Factor& f, int n);
    std::vector<std::unordered_map<std::string, double>> matrix_to_param_maps(
        const Eigen::MatrixXd& unscaled) const;

    // ---- State ----
    parameters::ParametersCollection params_;
    EvalFunction eval_func_;
    DEConfig config_;
    IterCallback iter_callback_;

    std::mt19937 rng_;
    int n_var_params_ = 0;

    int iter_ = 0;
    int iter_no_improvement_ = 0;
    int nr_evaluations_ = 0;
    std::atomic<bool> abort_flag_{false};
    std::string stop_reason_;

    // Boundaries in normalized space [0, 1]
    Eigen::VectorXd boundaries_min_;
    Eigen::VectorXd boundaries_max_;

    // Population matrices (pop_size x n_var_params)
    Eigen::MatrixXd targets_normed_;
    Eigen::VectorXd targets_metric_;

    Eigen::MatrixXd donors_normed_;

    Eigen::MatrixXd trials_normed_;
    Eigen::VectorXd trials_metric_;

    Eigen::MatrixXd survivors_normed_;
    Eigen::VectorXd survivors_metric_;

    // Best tracking
    Eigen::VectorXd best_normed_;
    double best_metric_;

    // Optional initial population (in original domain)
    std::optional<Eigen::MatrixXd> init_pop_;

    // History
    DEHistory history_;
};

} // namespace optimization
} // namespace de
