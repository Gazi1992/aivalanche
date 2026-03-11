#pragma once

#include <algorithm>
#include <cmath>
#include <memory>
#include <random>
#include <stdexcept>
#include <string>
#include <unordered_map>
#include <vector>

#include "transforms.hpp"

namespace de {
namespace parameters {

enum class Mode { Variable, Fixed };

class BaseParameterType {
public:
    virtual ~BaseParameterType() = default;

    const std::string& get_name() const { return name_; }
    double get_default() const { return default_; }
    Scale get_scale() const { return scale_; }
    Mode get_mode() const { return mode_; }
    const std::string& get_description() const { return description_; }

    bool is_variable() const { return mode_ == Mode::Variable; }
    bool is_fixed() const { return mode_ == Mode::Fixed; }

    double scaled_min() const { return scaled_min_; }
    double scaled_max() const { return scaled_max_; }
    double scaled_range() const { return scaled_range_; }
    double scaled_default() const { return scaled_default_; }

    virtual std::string type_name() const = 0;

    // Normalize value to [0, 1]
    virtual double norm(double value) const = 0;

    // Denormalize from [0, 1] to original domain
    virtual double unnorm(double norm_value) const = 0;

    // Sample a random value using the given RNG
    virtual double sample_random(std::mt19937& rng) const = 0;

protected:
    BaseParameterType(const std::string& name, double default_val, Scale scale,
                      Mode mode, const std::string& description)
        : name_(name), default_(default_val), scale_(scale),
          mode_(mode), description_(description) {}

    // Determine scale: fixed params always linear, otherwise use provided or auto-detect
    static Scale determine_scale(Scale scale, Mode mode, double min_val, double max_val) {
        if (mode == Mode::Fixed) return Scale::Linear;
        return scale;
    }

    std::string name_;
    double default_;
    Scale scale_;
    Mode mode_;
    std::string description_;
    std::unique_ptr<BaseTransform> transform_;
    double scaled_min_ = 0.0;
    double scaled_max_ = 1.0;
    double scaled_default_ = 0.5;
    double scaled_range_ = 1.0;
    double range_ = 0.0;
};

// ============================================================================
// ContinuousParameter
// ============================================================================

class ContinuousParameter : public BaseParameterType {
public:
    ContinuousParameter(const std::string& name, double min_val, double max_val,
                        double default_val = std::numeric_limits<double>::quiet_NaN(),
                        Scale scale = Scale::Linear, bool auto_scale = true,
                        Mode mode = Mode::Variable,
                        const std::string& description = "")
        : BaseParameterType(name, 0.0, Scale::Linear, mode, description),
          min_val_(min_val), max_val_(max_val)
    {
        // Flip if needed
        if (min_val_ > max_val_) std::swap(min_val_, max_val_);

        // Default to midpoint if NaN
        if (std::isnan(default_val)) {
            default_ = (min_val_ + max_val_) / 2.0;
        } else {
            default_ = std::clamp(default_val, min_val_, max_val_);
        }

        // Determine scale
        if (auto_scale && mode != Mode::Fixed) {
            scale_ = auto_detect_scale(min_val_, max_val_);
        } else {
            scale_ = determine_scale(scale, mode, min_val_, max_val_);
        }

        transform_ = make_transform(scale_, min_val_, max_val_);

        range_ = max_val_ - min_val_;
        scaled_min_ = transform_->scale(min_val_);
        scaled_max_ = transform_->scale(max_val_);
        scaled_default_ = transform_->scale(default_);
        scaled_range_ = scaled_max_ - scaled_min_;
    }

    double min_val() const { return min_val_; }
    double max_val() const { return max_val_; }

    std::string type_name() const override { return "continuous"; }

    double norm(double value) const override {
        if (scaled_range_ == 0.0) return 0.5;
        double scaled = transform_->scale(value);
        return (scaled - scaled_min_) / scaled_range_;
    }

    double unnorm(double norm_value) const override {
        double scaled = scaled_min_ + norm_value * scaled_range_;
        return transform_->unscale(scaled);
    }

    double sample_random(std::mt19937& rng) const override {
        std::uniform_real_distribution<double> dist(min_val_, max_val_);
        return dist(rng);
    }

private:
    double min_val_;
    double max_val_;
};

// ============================================================================
// DiscreteParameter
// ============================================================================

class DiscreteParameter : public BaseParameterType {
public:
    // Range-based constructor
    DiscreteParameter(const std::string& name, double min_val, double max_val,
                      double step = 1.0,
                      double default_val = std::numeric_limits<double>::quiet_NaN(),
                      Scale scale = Scale::Linear, bool auto_scale = true,
                      Mode mode = Mode::Variable,
                      const std::string& description = "")
        : BaseParameterType(name, 0.0, Scale::Linear, mode, description)
    {
        if (min_val > max_val) std::swap(min_val, max_val);
        if (step <= 0.0) throw std::invalid_argument("step must be positive");

        int n_steps = static_cast<int>(std::round((max_val - min_val) / step));
        for (int i = 0; i <= n_steps; ++i) {
            double v = min_val + i * step;
            if (v <= max_val + step * 0.01) {
                values_.push_back(v);
            }
        }
        if (values_.empty()) values_.push_back(min_val);

        // Snap last value to max if close
        if (!values_.empty() && std::abs(values_.back() - max_val) < step * 0.1) {
            values_.back() = max_val;
        }

        init_common(default_val, scale, auto_scale, mode);
    }

    // Values-list constructor
    DiscreteParameter(const std::string& name, std::vector<double> values,
                      double default_val = std::numeric_limits<double>::quiet_NaN(),
                      Scale scale = Scale::Linear, bool auto_scale = true,
                      Mode mode = Mode::Variable,
                      const std::string& description = "")
        : BaseParameterType(name, 0.0, Scale::Linear, mode, description)
    {
        if (values.empty()) throw std::invalid_argument("values list cannot be empty");

        // Sort and deduplicate
        std::sort(values.begin(), values.end());
        values.erase(std::unique(values.begin(), values.end()), values.end());
        values_ = std::move(values);

        init_common(default_val, scale, auto_scale, mode);
    }

    const std::vector<double>& values() const { return values_; }
    double min_val() const { return values_.front(); }
    double max_val() const { return values_.back(); }

    std::string type_name() const override { return "discrete"; }

    double snap_to_nearest(double value) const {
        auto it = std::min_element(values_.begin(), values_.end(),
            [value](double a, double b) { return std::abs(a - value) < std::abs(b - value); });
        return *it;
    }

    double norm(double value) const override {
        if (scaled_range_ == 0.0) return 0.5;
        // Snap to nearest valid value first
        value = snap_to_nearest(value);
        double scaled = transform_->scale(value);
        return (scaled - scaled_min_) / scaled_range_;
    }

    double unnorm(double norm_value) const override {
        if (values_.size() == 1) return values_[0];
        double scaled = scaled_min_ + norm_value * scaled_range_;
        double continuous = transform_->unscale(scaled);
        return snap_to_nearest(continuous);
    }

    double sample_random(std::mt19937& rng) const override {
        std::uniform_int_distribution<size_t> dist(0, values_.size() - 1);
        return values_[dist(rng)];
    }

private:
    void init_common(double default_val, Scale scale, bool auto_scale, Mode mode) {
        double min_v = values_.front();
        double max_v = values_.back();

        // Default to middle value
        if (std::isnan(default_val)) {
            default_ = values_[values_.size() / 2];
        } else {
            default_ = snap_to_nearest(default_val);
        }

        if (auto_scale && mode != Mode::Fixed) {
            scale_ = auto_detect_scale(min_v, max_v);
        } else {
            scale_ = determine_scale(scale, mode, min_v, max_v);
        }

        transform_ = make_transform(scale_, min_v, max_v);

        range_ = max_v - min_v;
        scaled_min_ = transform_->scale(min_v);
        scaled_max_ = transform_->scale(max_v);
        scaled_default_ = transform_->scale(default_);
        scaled_range_ = scaled_max_ - scaled_min_;
    }

    std::vector<double> values_;
};

// ============================================================================
// CategoricalParameter
// ============================================================================

class CategoricalParameter : public BaseParameterType {
public:
    CategoricalParameter(const std::string& name, std::vector<std::string> categories,
                         const std::string& default_val = "",
                         Mode mode = Mode::Variable,
                         const std::string& description = "")
        : BaseParameterType(name, 0.0, Scale::Linear, mode, description),
          categories_(std::move(categories))
    {
        if (categories_.empty()) throw std::invalid_argument("categories list cannot be empty");

        // Remove duplicates preserving order
        {
            std::vector<std::string> unique;
            std::unordered_map<std::string, bool> seen;
            for (auto& c : categories_) {
                if (!seen.count(c)) {
                    seen[c] = true;
                    unique.push_back(std::move(c));
                }
            }
            categories_ = std::move(unique);
        }

        // Build index map
        for (size_t i = 0; i < categories_.size(); ++i) {
            category_to_index_[categories_[i]] = i;
        }

        // Set default
        if (default_val.empty()) {
            default_index_ = 0;
        } else {
            auto it = category_to_index_.find(default_val);
            if (it == category_to_index_.end()) {
                throw std::invalid_argument("Default value '" + default_val + "' is not in categories");
            }
            default_index_ = it->second;
        }
        default_ = static_cast<double>(default_index_);

        // Categorical always uses NoTransform
        transform_ = std::make_unique<NoTransform>();
        scale_ = Scale::Linear;

        range_ = categories_.size() > 1 ? static_cast<double>(categories_.size() - 1) : 0.0;
        scaled_min_ = 0.0;
        scaled_max_ = range_;
        scaled_default_ = default_;
        scaled_range_ = range_;
    }

    const std::vector<std::string>& categories() const { return categories_; }
    size_t num_categories() const { return categories_.size(); }

    std::string type_name() const override { return "categorical"; }

    int index_of(const std::string& cat) const {
        auto it = category_to_index_.find(cat);
        if (it == category_to_index_.end()) return -1;
        return static_cast<int>(it->second);
    }

    const std::string& category_at(size_t index) const {
        return categories_.at(index);
    }

    double norm(double value) const override {
        // value is the category index
        if (categories_.size() == 1) return 0.5;
        size_t idx = static_cast<size_t>(std::clamp(value, 0.0, static_cast<double>(categories_.size() - 1)));
        return static_cast<double>(idx) / static_cast<double>(categories_.size() - 1);
    }

    // Normalize from category name — convenience
    double norm_category(const std::string& cat) const {
        int idx = index_of(cat);
        if (idx < 0) idx = 0;
        return norm(static_cast<double>(idx));
    }

    double unnorm(double norm_value) const override {
        if (categories_.size() == 1) return 0.0;
        norm_value = std::clamp(norm_value, 0.0, 1.0);
        int idx = static_cast<int>(std::round(norm_value * static_cast<double>(categories_.size() - 1)));
        idx = std::clamp(idx, 0, static_cast<int>(categories_.size() - 1));
        return static_cast<double>(idx);
    }

    // Get the category string from a denormalized value (index)
    const std::string& unnorm_category(double norm_value) const {
        return categories_.at(static_cast<size_t>(unnorm(norm_value)));
    }

    double sample_random(std::mt19937& rng) const override {
        std::uniform_int_distribution<size_t> dist(0, categories_.size() - 1);
        return static_cast<double>(dist(rng));
    }

private:
    std::vector<std::string> categories_;
    std::unordered_map<std::string, size_t> category_to_index_;
    size_t default_index_ = 0;
};

} // namespace parameters
} // namespace de
