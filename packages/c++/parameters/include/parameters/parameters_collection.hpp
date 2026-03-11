#pragma once

#include <algorithm>
#include <memory>
#include <stdexcept>
#include <string>
#include <unordered_map>
#include <vector>

#include <Eigen/Dense>
#include "parameter_types.hpp"

namespace de {
namespace parameters {

class ParametersCollection {
public:
    ParametersCollection() = default;

    void add(std::unique_ptr<BaseParameterType> param) {
        const std::string& name = param->get_name();
        if (name_to_index_.count(name)) {
            throw std::invalid_argument("Duplicate parameter name: " + name);
        }
        name_to_index_[name] = params_.size();
        names_.push_back(name);
        params_.push_back(std::move(param));
        variable_cache_dirty_ = true;
    }

    // Sort parameters alphabetically (matching Python behavior).
    // Must be called after all params are added and before using index-based operations.
    void sort_by_name() {
        std::sort(params_.begin(), params_.end(),
            [](const std::unique_ptr<BaseParameterType>& a, const std::unique_ptr<BaseParameterType>& b) {
                return a->get_name() < b->get_name();
            });
        // Rebuild indices
        names_.clear();
        name_to_index_.clear();
        for (size_t i = 0; i < params_.size(); ++i) {
            names_.push_back(params_[i]->get_name());
            name_to_index_[params_[i]->get_name()] = i;
        }
        variable_cache_dirty_ = true;
    }

    size_t size() const { return params_.size(); }

    size_t variable_count() const {
        rebuild_variable_cache();
        return variable_indices_.size();
    }

    const std::vector<std::string>& names() const { return names_; }

    std::vector<std::string> variable_names() const {
        rebuild_variable_cache();
        std::vector<std::string> result;
        result.reserve(variable_indices_.size());
        for (size_t i : variable_indices_) {
            result.push_back(params_[i]->get_name());
        }
        return result;
    }

    const BaseParameterType& at(size_t i) const { return *params_.at(i); }

    const BaseParameterType& by_name(const std::string& name) const {
        auto it = name_to_index_.find(name);
        if (it == name_to_index_.end()) {
            throw std::out_of_range("Parameter not found: " + name);
        }
        return *params_[it->second];
    }

    // Get all variable parameters (const references)
    std::vector<const BaseParameterType*> variable_params() const {
        rebuild_variable_cache();
        std::vector<const BaseParameterType*> result;
        result.reserve(variable_indices_.size());
        for (size_t i : variable_indices_) {
            result.push_back(params_[i].get());
        }
        return result;
    }

    // Normalize a vector of variable parameter values (size = variable_count)
    Eigen::VectorXd norm_all(const Eigen::VectorXd& values) const {
        rebuild_variable_cache();
        if (static_cast<size_t>(values.size()) != variable_indices_.size()) {
            throw std::invalid_argument(
                "Expected " + std::to_string(variable_indices_.size()) +
                " values, got " + std::to_string(values.size()));
        }
        Eigen::VectorXd result(values.size());
        for (size_t i = 0; i < variable_indices_.size(); ++i) {
            result(i) = params_[variable_indices_[i]]->norm(values(i));
        }
        return result;
    }

    // Denormalize a vector from [0,1] to original domain (size = variable_count)
    Eigen::VectorXd unnorm_all(const Eigen::VectorXd& normed) const {
        rebuild_variable_cache();
        if (static_cast<size_t>(normed.size()) != variable_indices_.size()) {
            throw std::invalid_argument(
                "Expected " + std::to_string(variable_indices_.size()) +
                " values, got " + std::to_string(normed.size()));
        }
        Eigen::VectorXd result(normed.size());
        for (size_t i = 0; i < variable_indices_.size(); ++i) {
            result(i) = params_[variable_indices_[i]]->unnorm(normed(i));
        }
        return result;
    }

    // Denormalize a full matrix (rows = population members, cols = variable params)
    Eigen::MatrixXd unnorm_matrix(const Eigen::MatrixXd& normed) const {
        rebuild_variable_cache();
        Eigen::MatrixXd result(normed.rows(), normed.cols());
        for (Eigen::Index r = 0; r < normed.rows(); ++r) {
            for (size_t c = 0; c < variable_indices_.size(); ++c) {
                result(r, c) = params_[variable_indices_[c]]->unnorm(normed(r, c));
            }
        }
        return result;
    }

    // Convert a row of unnormalized values to a name->value map
    // (includes both variable and fixed parameters)
    std::unordered_map<std::string, double> to_param_map(const Eigen::VectorXd& variable_values) const {
        rebuild_variable_cache();
        std::unordered_map<std::string, double> result;
        // Variable params from the vector
        for (size_t i = 0; i < variable_indices_.size(); ++i) {
            result[params_[variable_indices_[i]]->get_name()] = variable_values(i);
        }
        // Fixed params use their default
        for (size_t i = 0; i < params_.size(); ++i) {
            if (params_[i]->is_fixed()) {
                result[params_[i]->get_name()] = params_[i]->get_default();
            }
        }
        return result;
    }

    // Get normalized default values for variable parameters
    Eigen::VectorXd normalized_defaults() const {
        rebuild_variable_cache();
        Eigen::VectorXd result(variable_indices_.size());
        for (size_t i = 0; i < variable_indices_.size(); ++i) {
            const auto& p = *params_[variable_indices_[i]];
            result(i) = p.norm(p.get_default());
        }
        return result;
    }

private:
    void rebuild_variable_cache() const {
        if (!variable_cache_dirty_) return;
        variable_indices_.clear();
        for (size_t i = 0; i < params_.size(); ++i) {
            if (params_[i]->is_variable()) {
                variable_indices_.push_back(i);
            }
        }
        variable_cache_dirty_ = false;
    }

    std::vector<std::unique_ptr<BaseParameterType>> params_;
    std::vector<std::string> names_;
    std::unordered_map<std::string, size_t> name_to_index_;

    mutable std::vector<size_t> variable_indices_;
    mutable bool variable_cache_dirty_ = true;
};

} // namespace parameters
} // namespace de
