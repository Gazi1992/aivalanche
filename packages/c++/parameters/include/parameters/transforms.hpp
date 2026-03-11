#pragma once

#include <cmath>
#include <memory>
#include <stdexcept>
#include <string>

namespace de {
namespace parameters {

class BaseTransform {
public:
    virtual ~BaseTransform() = default;
    virtual double scale(double value) const = 0;
    virtual double unscale(double scaled_value) const = 0;
    virtual std::string name() const = 0;
};

class NoTransform : public BaseTransform {
public:
    double scale(double value) const override { return value; }
    double unscale(double scaled_value) const override { return scaled_value; }
    std::string name() const override { return "none"; }
};

class LogTransform : public BaseTransform {
public:
    double scale(double value) const override {
        if (value <= 0.0) {
            throw std::invalid_argument("LogTransform requires positive values, got " + std::to_string(value));
        }
        return std::log10(value);
    }

    double unscale(double scaled_value) const override {
        return std::pow(10.0, scaled_value);
    }

    std::string name() const override { return "log"; }
};

class NegLogTransform : public BaseTransform {
public:
    double scale(double value) const override {
        if (value >= 0.0) {
            throw std::invalid_argument("NegLogTransform requires negative values, got " + std::to_string(value));
        }
        return -std::log10(-value);
    }

    double unscale(double scaled_value) const override {
        return -(std::pow(10.0, -scaled_value));
    }

    std::string name() const override { return "neglog"; }
};

enum class Scale { Linear, Logarithmic };

// Auto-detect scale based on value range (matching Python logic)
inline Scale auto_detect_scale(double min_val, double max_val) {
    if (min_val * max_val > 0.0) {
        double ratio;
        if (min_val > 0.0) {
            ratio = max_val / min_val;
        } else {
            ratio = std::abs(min_val / max_val);
        }
        if (ratio >= 100.0) return Scale::Logarithmic;
    } else if (min_val < 0.0 && max_val > 0.0) {
        if ((max_val - min_val) > 100.0) return Scale::Logarithmic;
    }
    return Scale::Linear;
}

// Factory function to create the appropriate transform
inline std::unique_ptr<BaseTransform> make_transform(Scale scale, double min_val, double max_val) {
    if (scale == Scale::Linear) {
        return std::make_unique<NoTransform>();
    }
    // Logarithmic scale
    if (min_val > 0.0) {
        return std::make_unique<LogTransform>();
    } else if (max_val < 0.0) {
        return std::make_unique<NegLogTransform>();
    }
    // Range spans zero — fall back to linear (SymLog not ported)
    return std::make_unique<NoTransform>();
}

} // namespace parameters
} // namespace de
