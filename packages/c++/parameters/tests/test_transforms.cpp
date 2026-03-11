#include <gtest/gtest.h>
#include <parameters/transforms.hpp>
#include <cmath>

using namespace de::parameters;

TEST(NoTransformTest, RoundTrip) {
    NoTransform t;
    EXPECT_DOUBLE_EQ(t.scale(42.0), 42.0);
    EXPECT_DOUBLE_EQ(t.unscale(42.0), 42.0);
    EXPECT_DOUBLE_EQ(t.scale(-3.14), -3.14);
    EXPECT_DOUBLE_EQ(t.unscale(-3.14), -3.14);
    EXPECT_EQ(t.name(), "none");
}

TEST(LogTransformTest, ScaleUnscale) {
    LogTransform t;
    EXPECT_NEAR(t.scale(100.0), 2.0, 1e-12);
    EXPECT_NEAR(t.scale(1.0), 0.0, 1e-12);
    EXPECT_NEAR(t.unscale(2.0), 100.0, 1e-10);
    EXPECT_NEAR(t.unscale(0.0), 1.0, 1e-12);
    EXPECT_EQ(t.name(), "log");
}

TEST(LogTransformTest, RoundTrip) {
    LogTransform t;
    for (double v : {0.001, 0.1, 1.0, 10.0, 1000.0}) {
        EXPECT_NEAR(t.unscale(t.scale(v)), v, v * 1e-12);
    }
}

TEST(LogTransformTest, ThrowsOnNonPositive) {
    LogTransform t;
    EXPECT_THROW(t.scale(0.0), std::invalid_argument);
    EXPECT_THROW(t.scale(-1.0), std::invalid_argument);
}

TEST(NegLogTransformTest, ScaleUnscale) {
    NegLogTransform t;
    // -log10(-(-100)) = -log10(100) = -2
    EXPECT_NEAR(t.scale(-100.0), -2.0, 1e-12);
    EXPECT_NEAR(t.scale(-1.0), 0.0, 1e-12);
    EXPECT_NEAR(t.unscale(-2.0), -100.0, 1e-10);
    EXPECT_EQ(t.name(), "neglog");
}

TEST(NegLogTransformTest, RoundTrip) {
    NegLogTransform t;
    for (double v : {-0.001, -0.1, -1.0, -10.0, -1000.0}) {
        EXPECT_NEAR(t.unscale(t.scale(v)), v, std::abs(v) * 1e-12);
    }
}

TEST(NegLogTransformTest, ThrowsOnNonNegative) {
    NegLogTransform t;
    EXPECT_THROW(t.scale(0.0), std::invalid_argument);
    EXPECT_THROW(t.scale(1.0), std::invalid_argument);
}

TEST(AutoDetectScale, PositiveRange) {
    EXPECT_EQ(auto_detect_scale(1.0, 50.0), Scale::Linear);
    EXPECT_EQ(auto_detect_scale(1.0, 100.0), Scale::Logarithmic);
    EXPECT_EQ(auto_detect_scale(0.01, 10.0), Scale::Logarithmic);
}

TEST(AutoDetectScale, NegativeRange) {
    EXPECT_EQ(auto_detect_scale(-50.0, -1.0), Scale::Linear);
    EXPECT_EQ(auto_detect_scale(-1000.0, -1.0), Scale::Logarithmic);
}

TEST(MakeTransform, CorrectType) {
    auto t1 = make_transform(Scale::Linear, 0.0, 1.0);
    EXPECT_EQ(t1->name(), "none");

    auto t2 = make_transform(Scale::Logarithmic, 1.0, 100.0);
    EXPECT_EQ(t2->name(), "log");

    auto t3 = make_transform(Scale::Logarithmic, -100.0, -1.0);
    EXPECT_EQ(t3->name(), "neglog");

    // Spans zero — falls back to linear
    auto t4 = make_transform(Scale::Logarithmic, -10.0, 10.0);
    EXPECT_EQ(t4->name(), "none");
}
