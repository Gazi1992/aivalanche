#include <gtest/gtest.h>
#include <parameters/parameter_types.hpp>
#include <parameters/parameters_collection.hpp>
#include <cmath>
#include <random>

using namespace de::parameters;

// ============================================================================
// ContinuousParameter
// ============================================================================

TEST(ContinuousParameterTest, NormUnnormRoundTrip) {
    ContinuousParameter p("x", 0.0, 10.0, 5.0, Scale::Linear, false);

    EXPECT_NEAR(p.norm(0.0), 0.0, 1e-12);
    EXPECT_NEAR(p.norm(10.0), 1.0, 1e-12);
    EXPECT_NEAR(p.norm(5.0), 0.5, 1e-12);

    EXPECT_NEAR(p.unnorm(0.0), 0.0, 1e-12);
    EXPECT_NEAR(p.unnorm(1.0), 10.0, 1e-12);
    EXPECT_NEAR(p.unnorm(0.5), 5.0, 1e-12);
}

TEST(ContinuousParameterTest, LogScaleRoundTrip) {
    ContinuousParameter p("y", 1.0, 1000.0, 10.0, Scale::Logarithmic, false);

    // norm(1) = 0, norm(1000) = 1
    EXPECT_NEAR(p.norm(1.0), 0.0, 1e-12);
    EXPECT_NEAR(p.norm(1000.0), 1.0, 1e-12);

    // Round-trip
    for (double v : {1.0, 10.0, 100.0, 500.0, 1000.0}) {
        EXPECT_NEAR(p.unnorm(p.norm(v)), v, v * 1e-10);
    }
}

TEST(ContinuousParameterTest, AutoScale) {
    // Should auto-detect log for large ratio
    ContinuousParameter p("z", 0.01, 100.0, 1.0, Scale::Linear, true);
    EXPECT_EQ(p.get_scale(), Scale::Logarithmic);
}

TEST(ContinuousParameterTest, DefaultMidpoint) {
    ContinuousParameter p("a", 2.0, 8.0);
    EXPECT_NEAR(p.get_default(), 5.0, 1e-12);
}

TEST(ContinuousParameterTest, SampleRandom) {
    ContinuousParameter p("r", 0.0, 1.0);
    std::mt19937 rng(42);
    for (int i = 0; i < 100; ++i) {
        double v = p.sample_random(rng);
        EXPECT_GE(v, 0.0);
        EXPECT_LE(v, 1.0);
    }
}

// ============================================================================
// DiscreteParameter
// ============================================================================

TEST(DiscreteParameterTest, RangeMode) {
    DiscreteParameter p("d", 0.0, 10.0, 2.0);
    auto& vals = p.values();
    EXPECT_EQ(vals.size(), 6u); // 0, 2, 4, 6, 8, 10
    EXPECT_NEAR(vals[0], 0.0, 1e-12);
    EXPECT_NEAR(vals[5], 10.0, 1e-12);
}

TEST(DiscreteParameterTest, ValuesMode) {
    DiscreteParameter p("d", std::vector<double>{1.0, 5.0, 10.0, 20.0});
    EXPECT_EQ(p.values().size(), 4u);
    EXPECT_NEAR(p.min_val(), 1.0, 1e-12);
    EXPECT_NEAR(p.max_val(), 20.0, 1e-12);
}

TEST(DiscreteParameterTest, SnapToNearest) {
    DiscreteParameter p("d", std::vector<double>{1.0, 5.0, 10.0});
    EXPECT_NEAR(p.snap_to_nearest(3.0), 1.0, 1e-12); // closer to 1 than 5? No, 3-1=2, 5-3=2; tie goes to first
    EXPECT_NEAR(p.snap_to_nearest(4.0), 5.0, 1e-12);
    EXPECT_NEAR(p.snap_to_nearest(8.0), 10.0, 1e-12);
}

TEST(DiscreteParameterTest, NormUnnormRoundTrip) {
    DiscreteParameter p("d", std::vector<double>{0.0, 5.0, 10.0}, 5.0, Scale::Linear, false);

    EXPECT_NEAR(p.norm(0.0), 0.0, 1e-12);
    EXPECT_NEAR(p.norm(10.0), 1.0, 1e-12);

    // unnorm should snap to discrete values
    EXPECT_NEAR(p.unnorm(0.0), 0.0, 1e-12);
    EXPECT_NEAR(p.unnorm(1.0), 10.0, 1e-12);
    EXPECT_NEAR(p.unnorm(0.5), 5.0, 1e-12);
}

// ============================================================================
// CategoricalParameter
// ============================================================================

TEST(CategoricalParameterTest, NormUnnorm) {
    CategoricalParameter p("cat", {"a", "b", "c"}, "a");

    // a=0, b=1, c=2 -> norm: 0, 0.5, 1
    EXPECT_NEAR(p.norm(0.0), 0.0, 1e-12);
    EXPECT_NEAR(p.norm(1.0), 0.5, 1e-12);
    EXPECT_NEAR(p.norm(2.0), 1.0, 1e-12);

    EXPECT_NEAR(p.unnorm(0.0), 0.0, 1e-12);
    EXPECT_NEAR(p.unnorm(0.5), 1.0, 1e-12);
    EXPECT_NEAR(p.unnorm(1.0), 2.0, 1e-12);
}

TEST(CategoricalParameterTest, NormCategory) {
    CategoricalParameter p("cat", {"low", "medium", "high"});
    EXPECT_NEAR(p.norm_category("low"), 0.0, 1e-12);
    EXPECT_NEAR(p.norm_category("medium"), 0.5, 1e-12);
    EXPECT_NEAR(p.norm_category("high"), 1.0, 1e-12);
}

TEST(CategoricalParameterTest, UnnormCategory) {
    CategoricalParameter p("cat", {"low", "medium", "high"});
    EXPECT_EQ(p.unnorm_category(0.0), "low");
    EXPECT_EQ(p.unnorm_category(0.5), "medium");
    EXPECT_EQ(p.unnorm_category(1.0), "high");
}

TEST(CategoricalParameterTest, SingleCategory) {
    CategoricalParameter p("cat", {"only"});
    EXPECT_NEAR(p.norm(0.0), 0.5, 1e-12);
    EXPECT_NEAR(p.unnorm(0.5), 0.0, 1e-12);
}

// ============================================================================
// ParametersCollection
// ============================================================================

TEST(ParametersCollectionTest, SortByName) {
    ParametersCollection coll;
    coll.add(std::make_unique<ContinuousParameter>("z_param", 0.0, 1.0));
    coll.add(std::make_unique<ContinuousParameter>("a_param", 0.0, 10.0));
    coll.sort_by_name();

    EXPECT_EQ(coll.names()[0], "a_param");
    EXPECT_EQ(coll.names()[1], "z_param");
}

TEST(ParametersCollectionTest, NormUnnormAll) {
    ParametersCollection coll;
    coll.add(std::make_unique<ContinuousParameter>("a", 0.0, 10.0, 5.0, Scale::Linear, false));
    coll.add(std::make_unique<ContinuousParameter>("b", 0.0, 100.0, 50.0, Scale::Linear, false));
    coll.sort_by_name();

    Eigen::VectorXd vals(2);
    vals << 5.0, 50.0;
    auto normed = coll.norm_all(vals);

    EXPECT_NEAR(normed(0), 0.5, 1e-12);
    EXPECT_NEAR(normed(1), 0.5, 1e-12);

    auto unnormed = coll.unnorm_all(normed);
    EXPECT_NEAR(unnormed(0), 5.0, 1e-10);
    EXPECT_NEAR(unnormed(1), 50.0, 1e-10);
}

TEST(ParametersCollectionTest, VariableFixedFiltering) {
    ParametersCollection coll;
    coll.add(std::make_unique<ContinuousParameter>("var1", 0.0, 1.0, 0.5, Scale::Linear, false, Mode::Variable));
    coll.add(std::make_unique<ContinuousParameter>("fixed1", 0.0, 1.0, 0.5, Scale::Linear, false, Mode::Fixed));
    coll.add(std::make_unique<ContinuousParameter>("var2", 0.0, 1.0, 0.5, Scale::Linear, false, Mode::Variable));
    coll.sort_by_name();

    EXPECT_EQ(coll.variable_count(), 2u);
    EXPECT_EQ(coll.size(), 3u);

    auto vnames = coll.variable_names();
    EXPECT_EQ(vnames.size(), 2u);
}

TEST(ParametersCollectionTest, ToParamMap) {
    ParametersCollection coll;
    coll.add(std::make_unique<ContinuousParameter>("var", 0.0, 10.0, 5.0, Scale::Linear, false, Mode::Variable));
    coll.add(std::make_unique<ContinuousParameter>("fix", 0.0, 1.0, 0.42, Scale::Linear, false, Mode::Fixed));
    coll.sort_by_name();

    Eigen::VectorXd vals(1);
    vals << 7.0;
    auto map = coll.to_param_map(vals);

    EXPECT_NEAR(map["var"], 7.0, 1e-12);
    EXPECT_NEAR(map["fix"], 0.42, 1e-12);
}
