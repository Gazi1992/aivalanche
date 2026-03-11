#pragma once

#include <Eigen/Dense>
#include <vector>

namespace de {
namespace optimization {

class HaltonSequence {
public:
    // dimensions: number of dimensions, skip: number of initial elements to skip
    explicit HaltonSequence(int dimensions, int skip = 0)
        : dimensions_(dimensions), skip_(skip) {}

    // Generate n_samples points in [0, 1]^dimensions
    Eigen::MatrixXd generate(int n_samples) const {
        Eigen::MatrixXd result(n_samples, dimensions_);
        for (int d = 0; d < dimensions_; ++d) {
            int base = primes_[d % primes_.size()];
            for (int i = 0; i < n_samples; ++i) {
                result(i, d) = halton_element(i + skip_, base);
            }
        }
        return result;
    }

private:
    static double halton_element(int index, int base) {
        double f = 1.0;
        double r = 0.0;
        int i = index + 1; // 1-based for Halton
        while (i > 0) {
            f /= base;
            r += f * (i % base);
            i /= base;
        }
        return r;
    }

    int dimensions_;
    int skip_;

    static inline const std::vector<int> primes_ = {
        2, 3, 5, 7, 11, 13, 17, 19, 23, 29,
        31, 37, 41, 43, 47, 53, 59, 61, 67, 71,
        73, 79, 83, 89, 97, 101, 103, 107, 109, 113,
        127, 131, 137, 139, 149, 151, 157, 163, 167, 173,
        179, 181, 191, 193, 197, 199, 211, 223, 227, 229,
        233, 239, 241, 251, 257, 263, 269, 271, 277, 281,
        283, 293, 307, 311, 313, 317, 331, 337, 347, 349,
        353, 359, 367, 373, 379, 383, 389, 397, 401, 409,
        419, 421, 431, 433, 439, 443, 449, 457, 461, 463,
        467, 479, 487, 491, 499, 503, 509, 521, 523, 541
    };
};

} // namespace optimization
} // namespace de
