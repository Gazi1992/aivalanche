#pragma once

#include <vector>
#include <Eigen/Dense>

namespace de {
namespace optimization {

struct IterationRecord {
    int iteration;
    Eigen::MatrixXd trials_normed;      // pop_size x n_params
    Eigen::MatrixXd trials_unscaled;    // pop_size x n_params (denormalized)
    Eigen::VectorXd trials_metric;      // pop_size

    Eigen::MatrixXd survivors_normed;   // pop_size x n_params
    Eigen::MatrixXd survivors_unscaled; // pop_size x n_params (denormalized)
    Eigen::VectorXd survivors_metric;   // pop_size
};

struct BestRecord {
    int iteration;
    Eigen::VectorXd params_normed;
    Eigen::VectorXd params_unscaled;
    double metric;
};

class DEHistory {
public:
    void add_iteration(IterationRecord record) {
        iterations_.push_back(std::move(record));
    }

    void add_best(BestRecord record) {
        bests_.push_back(std::move(record));
    }

    const std::vector<IterationRecord>& iterations() const { return iterations_; }
    const std::vector<BestRecord>& bests() const { return bests_; }
    size_t size() const { return iterations_.size(); }

private:
    std::vector<IterationRecord> iterations_;
    std::vector<BestRecord> bests_;
};

} // namespace optimization
} // namespace de
