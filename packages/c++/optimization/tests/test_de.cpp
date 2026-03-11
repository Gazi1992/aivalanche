#include <gtest/gtest.h>
#include <optimization/differential_evolution.hpp>
#include <parameters/parameter_types.hpp>
#include <parameters/parameters_collection.hpp>

#include <cmath>
#include <iostream>

using namespace de::parameters;
using namespace de::optimization;

// Rosenbrock function: f(x,y) = (1-x)^2 + 100*(y-x^2)^2
// Minimum at (1, 1) with f = 0
static std::vector<double> rosenbrock_eval(
    const std::vector<std::unordered_map<std::string, double>>& params)
{
    std::vector<double> metrics;
    metrics.reserve(params.size());
    for (const auto& p : params) {
        double x = p.at("x");
        double y = p.at("y");
        double val = (1.0 - x) * (1.0 - x) + 100.0 * (y - x * x) * (y - x * x);
        metrics.push_back(val);
    }
    return metrics;
}

// Sphere function: f(x1, ..., xn) = sum(xi^2)
// Minimum at origin with f = 0
static std::vector<double> sphere_eval(
    const std::vector<std::unordered_map<std::string, double>>& params)
{
    std::vector<double> metrics;
    metrics.reserve(params.size());
    for (const auto& p : params) {
        double sum = 0.0;
        for (const auto& [name, val] : p) {
            sum += val * val;
        }
        metrics.push_back(sum);
    }
    return metrics;
}

TEST(DETest, SphereFunction) {
    ParametersCollection pc;
    pc.add(std::make_unique<ContinuousParameter>("x1", -5.0, 5.0, 0.0, Scale::Linear, false));
    pc.add(std::make_unique<ContinuousParameter>("x2", -5.0, 5.0, 0.0, Scale::Linear, false));

    DEConfig config;
    config.seed = 42;
    config.pop_size = 50;
    config.max_iterations = 200;
    config.max_iter_without_improvement = 100;
    config.metric_threshold = 1e-6;
    config.direction = OptDirection::Minimize;

    DifferentialEvolution de(std::move(pc), sphere_eval, config);
    DEResult result = de.run();

    std::cout << "Sphere: best_metric = " << result.best_metric
              << ", iterations = " << result.iterations_run << std::endl;

    EXPECT_LT(result.best_metric, 0.01);
    EXPECT_NEAR(result.best_parameters.at("x1"), 0.0, 0.5);
    EXPECT_NEAR(result.best_parameters.at("x2"), 0.0, 0.5);
}

TEST(DETest, RosenbrockFunction) {
    ParametersCollection pc;
    pc.add(std::make_unique<ContinuousParameter>("x", -5.0, 5.0, 0.0, Scale::Linear, false));
    pc.add(std::make_unique<ContinuousParameter>("y", -5.0, 5.0, 0.0, Scale::Linear, false));

    DEConfig config;
    config.seed = 123;
    config.pop_size = 80;
    config.max_iterations = 500;
    config.max_iter_without_improvement = 200;
    config.metric_threshold = 1e-4;
    config.direction = OptDirection::Minimize;

    DifferentialEvolution de(std::move(pc), rosenbrock_eval, config);
    DEResult result = de.run();

    std::cout << "Rosenbrock: best_metric = " << result.best_metric
              << ", x = " << result.best_parameters.at("x")
              << ", y = " << result.best_parameters.at("y")
              << ", iterations = " << result.iterations_run << std::endl;

    EXPECT_LT(result.best_metric, 1.0);
    EXPECT_NEAR(result.best_parameters.at("x"), 1.0, 1.0);
    EXPECT_NEAR(result.best_parameters.at("y"), 1.0, 1.0);
}

TEST(DETest, Maximization) {
    // Maximize f(x) = -(x-3)^2 + 9  => max at x=3, f=9
    ParametersCollection pc;
    pc.add(std::make_unique<ContinuousParameter>("x", 0.0, 6.0, 3.0, Scale::Linear, false));

    auto eval = [](const std::vector<std::unordered_map<std::string, double>>& params)
        -> std::vector<double> {
        std::vector<double> metrics;
        for (const auto& p : params) {
            double x = p.at("x");
            metrics.push_back(-(x - 3.0) * (x - 3.0) + 9.0);
        }
        return metrics;
    };

    DEConfig config;
    config.seed = 7;
    config.pop_size = 30;
    config.max_iterations = 100;
    config.max_iter_without_improvement = 50;
    config.metric_threshold = 8.99;
    config.direction = OptDirection::Maximize;

    DifferentialEvolution de(std::move(pc), eval, config);
    DEResult result = de.run();

    EXPECT_GT(result.best_metric, 8.0);
    EXPECT_NEAR(result.best_parameters.at("x"), 3.0, 0.5);
}

TEST(DETest, DiscreteParameters) {
    ParametersCollection pc;
    pc.add(std::make_unique<DiscreteParameter>("d", std::vector<double>{1.0, 2.0, 3.0, 4.0, 5.0}));
    pc.add(std::make_unique<ContinuousParameter>("c", -5.0, 5.0, 0.0, Scale::Linear, false));

    // Minimize (d-3)^2 + c^2 => d=3, c=0
    auto eval = [](const std::vector<std::unordered_map<std::string, double>>& params)
        -> std::vector<double> {
        std::vector<double> metrics;
        for (const auto& p : params) {
            double d = p.at("d");
            double c = p.at("c");
            metrics.push_back((d - 3.0) * (d - 3.0) + c * c);
        }
        return metrics;
    };

    DEConfig config;
    config.seed = 99;
    config.pop_size = 40;
    config.max_iterations = 200;
    config.max_iter_without_improvement = 100;
    config.direction = OptDirection::Minimize;

    DifferentialEvolution de(std::move(pc), eval, config);
    DEResult result = de.run();

    EXPECT_NEAR(result.best_parameters.at("d"), 3.0, 1e-10);
    EXPECT_NEAR(result.best_parameters.at("c"), 0.0, 0.5);
}

TEST(DETest, HistoryTracking) {
    ParametersCollection pc;
    pc.add(std::make_unique<ContinuousParameter>("x", -5.0, 5.0, 0.0, Scale::Linear, false));

    auto eval = [](const std::vector<std::unordered_map<std::string, double>>& params)
        -> std::vector<double> {
        std::vector<double> m;
        for (const auto& p : params) {
            double x = p.at("x");
            m.push_back(x * x);
        }
        return m;
    };

    DEConfig config;
    config.seed = 1;
    config.pop_size = 20;
    config.max_iterations = 10;
    config.max_iter_without_improvement = 100;

    DifferentialEvolution de(std::move(pc), eval, config);
    DEResult result = de.run();

    EXPECT_EQ(result.history.size(), static_cast<size_t>(result.iterations_run));
    EXPECT_FALSE(result.history.bests().empty());
}

TEST(DETest, DiscreteOnlyParameters) {
    // All discrete: minimize (a-3)^2 + (b-7)^2
    // a in {1,2,3,4,5}, b in {5,6,7,8,9} => optimal a=3, b=7
    ParametersCollection pc;
    pc.add(std::make_unique<DiscreteParameter>("a", std::vector<double>{1.0, 2.0, 3.0, 4.0, 5.0}));
    pc.add(std::make_unique<DiscreteParameter>("b", std::vector<double>{5.0, 6.0, 7.0, 8.0, 9.0}));

    auto eval = [](const std::vector<std::unordered_map<std::string, double>>& params)
        -> std::vector<double> {
        std::vector<double> metrics;
        for (const auto& p : params) {
            double a = p.at("a");
            double b = p.at("b");
            metrics.push_back((a - 3.0) * (a - 3.0) + (b - 7.0) * (b - 7.0));
        }
        return metrics;
    };

    DEConfig config;
    config.seed = 42;
    config.pop_size = 40;
    config.max_iterations = 200;
    config.max_iter_without_improvement = 100;
    config.direction = OptDirection::Minimize;

    DifferentialEvolution de(std::move(pc), eval, config);
    DEResult result = de.run();

    EXPECT_NEAR(result.best_parameters.at("a"), 3.0, 1e-10);
    EXPECT_NEAR(result.best_parameters.at("b"), 7.0, 1e-10);
    EXPECT_NEAR(result.best_metric, 0.0, 1e-10);
}

TEST(DETest, CategoricalParameter) {
    // Categorical "mode" with 3 categories: "low"=0, "medium"=1, "high"=2
    // Combined with a continuous param. Objective: minimize (mode - 1)^2 + (x - 3)^2
    // Optimal: mode=1 ("medium"), x=3
    ParametersCollection pc;
    pc.add(std::make_unique<CategoricalParameter>("mode", std::vector<std::string>{"low", "medium", "high"}));
    pc.add(std::make_unique<ContinuousParameter>("x", 0.0, 6.0, 3.0, Scale::Linear, false));

    auto eval = [](const std::vector<std::unordered_map<std::string, double>>& params)
        -> std::vector<double> {
        std::vector<double> metrics;
        for (const auto& p : params) {
            double mode = p.at("mode");  // category index: 0, 1, or 2
            double x = p.at("x");
            metrics.push_back((mode - 1.0) * (mode - 1.0) + (x - 3.0) * (x - 3.0));
        }
        return metrics;
    };

    DEConfig config;
    config.seed = 42;
    config.pop_size = 40;
    config.max_iterations = 200;
    config.max_iter_without_improvement = 100;
    config.direction = OptDirection::Minimize;

    DifferentialEvolution de(std::move(pc), eval, config);
    DEResult result = de.run();

    EXPECT_NEAR(result.best_parameters.at("mode"), 1.0, 1e-10);  // "medium"
    EXPECT_NEAR(result.best_parameters.at("x"), 3.0, 0.5);
}

TEST(DETest, AllParameterTypesMixed) {
    // Mix all three types: continuous + discrete + categorical
    // Minimize: (x - 2)^2 + (d - 5)^2 + (cat - 2)^2
    // x continuous [-5, 5], d discrete {1,3,5,7,9}, cat {"a","b","c"} (indices 0,1,2)
    // Optimal: x=2, d=5, cat=2 ("c")
    ParametersCollection pc;
    pc.add(std::make_unique<CategoricalParameter>("cat", std::vector<std::string>{"a", "b", "c"}));
    pc.add(std::make_unique<DiscreteParameter>("d", std::vector<double>{1.0, 3.0, 5.0, 7.0, 9.0}));
    pc.add(std::make_unique<ContinuousParameter>("x", -5.0, 5.0, 0.0, Scale::Linear, false));

    auto eval = [](const std::vector<std::unordered_map<std::string, double>>& params)
        -> std::vector<double> {
        std::vector<double> metrics;
        for (const auto& p : params) {
            double x = p.at("x");
            double d = p.at("d");
            double cat = p.at("cat");
            metrics.push_back((x - 2.0) * (x - 2.0) + (d - 5.0) * (d - 5.0) + (cat - 2.0) * (cat - 2.0));
        }
        return metrics;
    };

    DEConfig config;
    config.seed = 77;
    config.pop_size = 60;
    config.max_iterations = 300;
    config.max_iter_without_improvement = 150;
    config.direction = OptDirection::Minimize;

    DifferentialEvolution de(std::move(pc), eval, config);
    DEResult result = de.run();

    EXPECT_NEAR(result.best_parameters.at("x"), 2.0, 0.5);
    EXPECT_NEAR(result.best_parameters.at("d"), 5.0, 1e-10);
    EXPECT_NEAR(result.best_parameters.at("cat"), 2.0, 1e-10);  // "c"
    EXPECT_LT(result.best_metric, 1.0);
}

TEST(DETest, AbortFlag) {
    ParametersCollection pc;
    pc.add(std::make_unique<ContinuousParameter>("x", -10.0, 10.0, 0.0, Scale::Linear, false));

    int eval_count = 0;
    DifferentialEvolution* de_ptr = nullptr;

    auto eval = [&](const std::vector<std::unordered_map<std::string, double>>& params)
        -> std::vector<double> {
        eval_count++;
        if (eval_count >= 3 && de_ptr) {
            de_ptr->abort();
        }
        std::vector<double> m;
        for (const auto& p : params) {
            m.push_back(p.at("x") * p.at("x"));
        }
        return m;
    };

    DEConfig config;
    config.seed = 1;
    config.pop_size = 10;
    config.max_iterations = 1000;
    config.max_iter_without_improvement = 1000;

    DifferentialEvolution de(std::move(pc), eval, config);
    de_ptr = &de;
    DEResult result = de.run();

    EXPECT_EQ(result.stop_reason, "optimization aborted");
    EXPECT_LT(result.iterations_run, 1000);
}
