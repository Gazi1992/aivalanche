#include <optimization/differential_evolution.hpp>
#include <optimization/halton.hpp>

#include <algorithm>
#include <cmath>
#include <numeric>

namespace de {
namespace optimization {

// ============================================================================
// Constructor
// ============================================================================

DifferentialEvolution::DifferentialEvolution(
    parameters::ParametersCollection params,
    EvalFunction eval_func,
    DEConfig config)
    : params_(std::move(params)),
      eval_func_(std::move(eval_func)),
      config_(std::move(config))
{
    // Sort parameters alphabetically (matches Python)
    params_.sort_by_name();
    n_var_params_ = static_cast<int>(params_.variable_count());

    // Initialize RNG
    if (config_.seed < 0) {
        std::random_device rd;
        rng_.seed(rd());
    } else {
        rng_.seed(static_cast<unsigned int>(config_.seed));
    }

    // Initialize best metric
    if (config_.direction == OptDirection::Minimize) {
        best_metric_ = std::numeric_limits<double>::infinity();
    } else {
        best_metric_ = -std::numeric_limits<double>::infinity();
    }
}

void DifferentialEvolution::set_initial_population(const Eigen::MatrixXd& init_pop) {
    init_pop_ = init_pop;
}

void DifferentialEvolution::set_iteration_callback(IterCallback cb) {
    iter_callback_ = std::move(cb);
}

void DifferentialEvolution::abort() {
    abort_flag_.store(true);
}

// ============================================================================
// Main loop
// ============================================================================

DEResult DifferentialEvolution::run() {
    initialize();

    // First iteration: generate initial population as donors, use them as trials directly
    iter_ = 1;
    generate_initial_population();
    trials_normed_ = donors_normed_;

    // Main loop
    while (true) {
        evaluate_trials();
        determine_survivors();
        determine_best();
        record_history();

        // Callback
        if (iter_callback_) {
            auto best_unscaled = params_.unnorm_all(best_normed_);
            auto best_map = params_.to_param_map(best_unscaled);
            iter_callback_(iter_, best_metric_, best_map);
        }

        // Check stopping
        if (check_stopping_criteria()) break;

        // Prepare next iteration
        iter_++;
        targets_normed_ = survivors_normed_;
        targets_metric_ = survivors_metric_;

        generate_donors();
        generate_trials();
    }

    // Build result
    DEResult result;
    auto best_unscaled = params_.unnorm_all(best_normed_);
    result.best_parameters = params_.to_param_map(best_unscaled);
    result.best_metric = best_metric_;
    result.iterations_run = iter_;
    result.nr_evaluations = nr_evaluations_;
    result.stop_reason = stop_reason_;
    result.history = std::move(history_);

    return result;
}

// ============================================================================
// Initialize
// ============================================================================

void DifferentialEvolution::initialize() {
    int ps = config_.pop_size;

    boundaries_min_ = Eigen::VectorXd::Zero(n_var_params_);
    boundaries_max_ = Eigen::VectorXd::Ones(n_var_params_);

    targets_normed_ = Eigen::MatrixXd::Zero(ps, n_var_params_);
    targets_metric_ = Eigen::VectorXd::Constant(ps, std::numeric_limits<double>::quiet_NaN());

    donors_normed_ = Eigen::MatrixXd::Zero(ps, n_var_params_);
    trials_normed_ = Eigen::MatrixXd::Zero(ps, n_var_params_);
    trials_metric_ = Eigen::VectorXd::Constant(ps, std::numeric_limits<double>::quiet_NaN());

    survivors_normed_ = Eigen::MatrixXd::Zero(ps, n_var_params_);
    survivors_metric_ = Eigen::VectorXd::Constant(ps, std::numeric_limits<double>::quiet_NaN());

    best_normed_ = Eigen::VectorXd::Zero(n_var_params_);
}

// ============================================================================
// Population initialization
// ============================================================================

void DifferentialEvolution::generate_initial_population() {
    int ps = config_.pop_size;

    // Generate Halton sequence in [0, 1]^n_var_params
    int seed_skip = (config_.seed >= 0) ? config_.seed : 0;
    HaltonSequence halton(n_var_params_, seed_skip);
    donors_normed_ = halton.generate(ps);

    // Incorporate user-provided initial population if available
    if (init_pop_.has_value()) {
        const auto& ip = init_pop_.value();
        int n_to_inject = std::min(static_cast<int>(ip.rows()), ps);

        // Normalize the initial population
        for (int i = 0; i < n_to_inject; ++i) {
            donors_normed_.row(i) = params_.norm_all(ip.row(i).transpose()).transpose();
        }
    }

    // Incorporate default values if configured
    if (config_.defaults_in_init_pop) {
        int replace_count = static_cast<int>(ps * config_.defaults_in_init_pop_ratio);
        replace_count = std::max(1, std::min(replace_count, ps));

        Eigen::VectorXd norm_defaults = params_.normalized_defaults();

        // Determine starting index for defaults (after any init_pop)
        int start_idx = 0;
        if (init_pop_.has_value()) {
            start_idx = std::min(static_cast<int>(init_pop_.value().rows()), ps);
        }

        for (int i = 0; i < replace_count && (start_idx + i) < ps; ++i) {
            donors_normed_.row(start_idx + i) = norm_defaults.transpose();
        }
    }
}

// ============================================================================
// Mutation
// ============================================================================

void DifferentialEvolution::generate_donors() {
    mutate();
    handle_boundary_violations();
}

void DifferentialEvolution::mutate() {
    int ps = config_.pop_size;

    // Sample mutation factors
    Eigen::VectorXd f1 = sample_factor(config_.mutation_factor_1, ps);
    Eigen::VectorXd f2 = sample_factor(config_.mutation_factor_2, ps);
    Eigen::VectorXd f3 = sample_factor(config_.mutation_factor_3, ps);

    for (int i = 0; i < ps; ++i) {
        // Fisher-Yates partial shuffle to pick 3 distinct indices != i
        std::vector<int> pool;
        pool.reserve(ps - 1);
        for (int j = 0; j < ps; ++j) {
            if (j != i) pool.push_back(j);
        }

        auto pick = [&](int exclude_end) {
            int idx = std::uniform_int_distribution<int>(0, exclude_end)(rng_);
            std::swap(pool[idx], pool[exclude_end]);
            return pool[exclude_end];
        };

        int r1 = pick(static_cast<int>(pool.size()) - 1);
        int r2 = pick(static_cast<int>(pool.size()) - 2);
        int r3 = pick(static_cast<int>(pool.size()) - 3);

        // donor = r1 + F1*(r2-r3) + F2*(best-r1) + F3*(best-target)
        Eigen::VectorXd rand1 = targets_normed_.row(r1).transpose();
        Eigen::VectorXd rand2 = targets_normed_.row(r2).transpose();
        Eigen::VectorXd rand3 = targets_normed_.row(r3).transpose();
        Eigen::VectorXd target = targets_normed_.row(i).transpose();

        donors_normed_.row(i) = (
            rand1.transpose()
            + f1(i) * (rand2 - rand3).transpose()
            + f2(i) * (best_normed_ - rand1).transpose()
            + f3(i) * (best_normed_ - target).transpose()
        );
    }
}

void DifferentialEvolution::handle_boundary_violations() {
    int ps = config_.pop_size;

    for (int i = 0; i < ps; ++i) {
        for (int j = 0; j < n_var_params_; ++j) {
            double val = donors_normed_(i, j);
            double lo = boundaries_min_(j);
            double hi = boundaries_max_(j);

            if (val > hi) {
                switch (config_.boundary_handling) {
                    case BoundaryHandling::RandomFromTarget: {
                        double target_val = targets_normed_(i, j);
                        std::uniform_real_distribution<double> dist(target_val, hi);
                        donors_normed_(i, j) = dist(rng_);
                        break;
                    }
                    case BoundaryHandling::Clamp:
                        donors_normed_(i, j) = hi;
                        break;
                    case BoundaryHandling::Random: {
                        std::uniform_real_distribution<double> dist(lo, hi);
                        donors_normed_(i, j) = dist(rng_);
                        break;
                    }
                }
            } else if (val < lo) {
                switch (config_.boundary_handling) {
                    case BoundaryHandling::RandomFromTarget: {
                        double target_val = targets_normed_(i, j);
                        std::uniform_real_distribution<double> dist(lo, target_val);
                        donors_normed_(i, j) = dist(rng_);
                        break;
                    }
                    case BoundaryHandling::Clamp:
                        donors_normed_(i, j) = lo;
                        break;
                    case BoundaryHandling::Random: {
                        std::uniform_real_distribution<double> dist(lo, hi);
                        donors_normed_(i, j) = dist(rng_);
                        break;
                    }
                }
            }
        }
    }
}

// ============================================================================
// Crossover
// ============================================================================

void DifferentialEvolution::generate_trials() {
    crossover();
}

void DifferentialEvolution::crossover() {
    int ps = config_.pop_size;

    // Sample recombination factor
    Eigen::VectorXd cr = sample_factor(config_.recombination_factor, ps);

    std::uniform_real_distribution<double> uniform01(0.0, 1.0);

    for (int i = 0; i < ps; ++i) {
        // Ensure at least one parameter comes from donor
        std::uniform_int_distribution<int> j_dist(0, n_var_params_ - 1);
        int j_rand = j_dist(rng_);

        for (int j = 0; j < n_var_params_; ++j) {
            if (uniform01(rng_) < cr(i) || j == j_rand) {
                trials_normed_(i, j) = donors_normed_(i, j);
            } else {
                trials_normed_(i, j) = targets_normed_(i, j);
            }
        }
    }
}

// ============================================================================
// Evaluation
// ============================================================================

void DifferentialEvolution::evaluate_trials() {
    // Denormalize trials to original domain
    Eigen::MatrixXd trials_unscaled = params_.unnorm_matrix(trials_normed_);

    // Convert to parameter maps
    auto param_maps = matrix_to_param_maps(trials_unscaled);

    // Call eval function
    std::vector<double> metrics = eval_func_(param_maps);

    // Store metrics
    trials_metric_ = Eigen::Map<Eigen::VectorXd>(metrics.data(), metrics.size());
    nr_evaluations_ += config_.pop_size;
}

// ============================================================================
// Selection
// ============================================================================

void DifferentialEvolution::determine_survivors() {
    int ps = config_.pop_size;

    if (iter_ == 1) {
        // First iteration: all trials become survivors
        survivors_normed_ = trials_normed_;
        survivors_metric_ = trials_metric_;
    } else {
        for (int i = 0; i < ps; ++i) {
            bool trial_is_better;
            if (config_.direction == OptDirection::Minimize) {
                trial_is_better = trials_metric_(i) < targets_metric_(i);
            } else {
                trial_is_better = trials_metric_(i) > targets_metric_(i);
            }

            if (trial_is_better) {
                survivors_normed_.row(i) = trials_normed_.row(i);
                survivors_metric_(i) = trials_metric_(i);
            } else {
                survivors_normed_.row(i) = targets_normed_.row(i);
                survivors_metric_(i) = targets_metric_(i);
            }
        }
    }
}

// ============================================================================
// Best tracking
// ============================================================================

bool DifferentialEvolution::determine_best() {
    Eigen::Index best_idx = 0;
    if (config_.direction == OptDirection::Minimize) {
        survivors_metric_.minCoeff(&best_idx);
    } else {
        survivors_metric_.maxCoeff(&best_idx);
    }

    double current_best = survivors_metric_(best_idx);
    double previous_best = best_metric_;

    bool better_found = false;
    if (config_.direction == OptDirection::Minimize && current_best < previous_best) {
        better_found = true;
    } else if (config_.direction == OptDirection::Maximize && current_best > previous_best) {
        better_found = true;
    }

    if (better_found) {
        // Check if improvement is significant
        bool significant = false;
        double abs_prev = std::abs(previous_best);
        if (abs_prev > std::numeric_limits<double>::epsilon()) {
            double relative_improvement = std::abs(current_best - previous_best) / abs_prev;
            if (std::isfinite(relative_improvement) &&
                relative_improvement >= config_.improvement_threshold) {
                significant = true;
            } else if (std::isinf(relative_improvement) &&
                       std::isfinite(config_.improvement_threshold)) {
                significant = true;
            }
        } else {
            // Previous best was ~0, any improvement is significant
            significant = true;
        }

        if (significant) {
            iter_no_improvement_ = 0;
        } else {
            iter_no_improvement_++;
        }

        best_normed_ = survivors_normed_.row(best_idx).transpose();
        best_metric_ = current_best;
    } else {
        iter_no_improvement_++;
    }

    return better_found;
}

// ============================================================================
// Stopping criteria
// ============================================================================

bool DifferentialEvolution::check_stopping_criteria() {
    if (abort_flag_.load()) {
        stop_reason_ = "optimization aborted";
        return true;
    }

    if (config_.direction == OptDirection::Minimize &&
        best_metric_ < config_.metric_threshold) {
        stop_reason_ = "metric threshold reached";
        return true;
    }

    if (config_.direction == OptDirection::Maximize &&
        best_metric_ > config_.metric_threshold) {
        stop_reason_ = "metric threshold reached";
        return true;
    }

    if (iter_no_improvement_ > config_.max_iter_without_improvement) {
        stop_reason_ = "maximum iterations without improvement reached";
        return true;
    }

    if (iter_ >= config_.max_iterations) {
        stop_reason_ = "maximum iterations reached";
        return true;
    }

    return false;
}

// ============================================================================
// History
// ============================================================================

void DifferentialEvolution::record_history() {
    IterationRecord rec;
    rec.iteration = iter_;
    rec.trials_normed = trials_normed_;
    rec.trials_unscaled = params_.unnorm_matrix(trials_normed_);
    rec.trials_metric = trials_metric_;
    rec.survivors_normed = survivors_normed_;
    rec.survivors_unscaled = params_.unnorm_matrix(survivors_normed_);
    rec.survivors_metric = survivors_metric_;
    history_.add_iteration(std::move(rec));

    BestRecord best_rec;
    best_rec.iteration = iter_;
    best_rec.params_normed = best_normed_;
    best_rec.params_unscaled = params_.unnorm_all(best_normed_);
    best_rec.metric = best_metric_;
    history_.add_best(std::move(best_rec));
}

// ============================================================================
// Utilities
// ============================================================================

Eigen::VectorXd DifferentialEvolution::sample_factor(const Factor& f, int n) {
    if (auto* fixed = std::get_if<double>(&f)) {
        return Eigen::VectorXd::Constant(n, *fixed);
    }
    auto& range = std::get<std::pair<double, double>>(f);
    std::uniform_real_distribution<double> dist(range.first, range.second);
    Eigen::VectorXd result(n);
    for (int i = 0; i < n; ++i) {
        result(i) = dist(rng_);
    }
    return result;
}

std::vector<std::unordered_map<std::string, double>>
DifferentialEvolution::matrix_to_param_maps(const Eigen::MatrixXd& unscaled) const {
    std::vector<std::unordered_map<std::string, double>> result;
    result.reserve(unscaled.rows());
    for (Eigen::Index i = 0; i < unscaled.rows(); ++i) {
        result.push_back(params_.to_param_map(unscaled.row(i).transpose()));
    }
    return result;
}

} // namespace optimization
} // namespace de
