// cpp_core/tests/test_surface_curve.cpp
#include <gtest/gtest.h>
#include "geometry/surface_curve.h"
#include "geometry/subd_evaluator.h"

using namespace latent;

class SurfaceCurveTest : public ::testing::Test {
protected:
    SubDEvaluator evaluator;

    void SetUp() override {
        // Initialize with unit cube
        std::vector<float> vertices = {
            -1, -1, -1,  1, -1, -1,  1, 1, -1,  -1, 1, -1,
            -1, -1,  1,  1, -1,  1,  1, 1,  1,  -1, 1,  1
        };
        std::vector<int> faces = {
            0, 1, 2, 3, 4, 7, 6, 5, 0, 4, 5, 1,
            2, 6, 7, 3, 0, 3, 7, 4, 1, 5, 6, 2
        };
        std::vector<int> face_sizes = {4, 4, 4, 4, 4, 4};

        // Build control cage
        SubDControlCage cage;
        cage.vertices.reserve(8);
        for (size_t i = 0; i < 8; ++i) {
            cage.vertices.push_back(Point3D(vertices[i*3], vertices[i*3+1], vertices[i*3+2]));
        }

        // Build faces
        int face_offset = 0;
        for (int i = 0; i < 6; ++i) {
            std::vector<int> face;
            for (int j = 0; j < face_sizes[i]; ++j) {
                face.push_back(faces[face_offset + j]);
            }
            cage.faces.push_back(face);
            face_offset += face_sizes[i];
        }

        evaluator.initialize(cage);
    }
};

TEST_F(SurfaceCurveTest, LinearInterpolation) {
    // Create a linear curve across face 0
    std::vector<ParametricPoint> points = {
        ParametricPoint(0, 0.0f, 0.5f),
        ParametricPoint(0, 1.0f, 0.5f)
    };

    SurfaceCurve curve(points, CurveType::LINEAR, 1);

    // Test endpoints
    auto p0 = curve.evaluate_parametric(0.0f);
    EXPECT_FLOAT_EQ(p0.u, 0.0f);
    EXPECT_FLOAT_EQ(p0.v, 0.5f);

    auto p1 = curve.evaluate_parametric(1.0f);
    EXPECT_FLOAT_EQ(p1.u, 1.0f);
    EXPECT_FLOAT_EQ(p1.v, 0.5f);

    // Test midpoint
    auto mid = curve.evaluate_parametric(0.5f);
    EXPECT_FLOAT_EQ(mid.u, 0.5f);
    EXPECT_FLOAT_EQ(mid.v, 0.5f);
}

TEST_F(SurfaceCurveTest, BezierEndpoints) {
    // Bezier curves interpolate endpoints
    std::vector<ParametricPoint> points = {
        ParametricPoint(0, 0.0f, 0.0f),
        ParametricPoint(0, 0.5f, 0.8f),
        ParametricPoint(0, 1.0f, 1.0f)
    };

    SurfaceCurve curve(points, CurveType::BEZIER, 2);

    auto p0 = curve.evaluate_parametric(0.0f);
    EXPECT_FLOAT_EQ(p0.u, 0.0f);
    EXPECT_FLOAT_EQ(p0.v, 0.0f);

    auto p1 = curve.evaluate_parametric(1.0f);
    EXPECT_FLOAT_EQ(p1.u, 1.0f);
    EXPECT_FLOAT_EQ(p1.v, 1.0f);
}

TEST_F(SurfaceCurveTest, SampleProducesSmoothCurve) {
    std::vector<ParametricPoint> points = {
        ParametricPoint(0, 0.0f, 0.0f),
        ParametricPoint(0, 0.5f, 0.5f),
        ParametricPoint(0, 1.0f, 1.0f)
    };

    SurfaceCurve curve(points, CurveType::BEZIER, 2);

    auto samples = curve.sample(10, evaluator);

    EXPECT_EQ(samples.size(), 10);

    // Check samples are on the surface (valid points)
    for (const auto& pt : samples) {
        EXPECT_FALSE(std::isnan(pt.x));
        EXPECT_FALSE(std::isnan(pt.y));
        EXPECT_FALSE(std::isnan(pt.z));
    }
}

TEST_F(SurfaceCurveTest, TangentIsNonZero) {
    std::vector<ParametricPoint> points = {
        ParametricPoint(0, 0.0f, 0.5f),
        ParametricPoint(0, 1.0f, 0.5f)
    };

    SurfaceCurve curve(points, CurveType::LINEAR, 1);

    Vector3 tan = curve.tangent(0.5f, evaluator);

    EXPECT_GT(tan.length(), 0.0f);
}

TEST_F(SurfaceCurveTest, ArcLengthPositive) {
    std::vector<ParametricPoint> points = {
        ParametricPoint(0, 0.0f, 0.0f),
        ParametricPoint(0, 1.0f, 1.0f)
    };

    SurfaceCurve curve(points, CurveType::LINEAR, 1);

    float length = curve.arc_length(evaluator, 50);

    EXPECT_GT(length, 0.0f);
}

TEST_F(SurfaceCurveTest, BSplineApproximatesControlPolygon) {
    std::vector<ParametricPoint> points = {
        ParametricPoint(0, 0.0f, 0.0f),
        ParametricPoint(0, 0.25f, 0.5f),
        ParametricPoint(0, 0.75f, 0.5f),
        ParametricPoint(0, 1.0f, 0.0f)
    };

    SurfaceCurve curve(points, CurveType::BSPLINE, 3);

    // B-spline should be smooth and stay near control polygon
    auto mid = curve.evaluate_parametric(0.5f);

    // Midpoint should be somewhere reasonable
    EXPECT_GE(mid.u, 0.0f);
    EXPECT_LE(mid.u, 1.0f);
    EXPECT_GE(mid.v, 0.0f);
    EXPECT_LE(mid.v, 1.0f);
}

TEST_F(SurfaceCurveTest, EmptyControlPoints) {
    // Test with no control points
    std::vector<ParametricPoint> points;
    SurfaceCurve curve(points, CurveType::BEZIER, 2);

    auto p = curve.evaluate_parametric(0.5f);
    EXPECT_FALSE(p.is_valid());
}

TEST_F(SurfaceCurveTest, SingleControlPoint) {
    // Test with single control point
    std::vector<ParametricPoint> points = {
        ParametricPoint(0, 0.5f, 0.5f)
    };
    SurfaceCurve curve(points, CurveType::BEZIER, 2);

    auto p = curve.evaluate_parametric(0.5f);
    EXPECT_FLOAT_EQ(p.u, 0.5f);
    EXPECT_FLOAT_EQ(p.v, 0.5f);
}

TEST_F(SurfaceCurveTest, CurveTypeChange) {
    // Test changing curve type
    std::vector<ParametricPoint> points = {
        ParametricPoint(0, 0.0f, 0.0f),
        ParametricPoint(0, 1.0f, 1.0f)
    };

    SurfaceCurve curve(points, CurveType::LINEAR, 1);
    EXPECT_EQ(curve.get_type(), CurveType::LINEAR);

    curve.set_type(CurveType::BEZIER);
    EXPECT_EQ(curve.get_type(), CurveType::BEZIER);
}

TEST_F(SurfaceCurveTest, ParameterClamping) {
    // Test that parameters outside [0,1] are clamped
    std::vector<ParametricPoint> points = {
        ParametricPoint(0, 0.0f, 0.0f),
        ParametricPoint(0, 1.0f, 1.0f)
    };

    SurfaceCurve curve(points, CurveType::LINEAR, 1);

    // Test t < 0
    auto p_neg = curve.evaluate_parametric(-0.5f);
    EXPECT_FLOAT_EQ(p_neg.u, 0.0f);
    EXPECT_FLOAT_EQ(p_neg.v, 0.0f);

    // Test t > 1
    auto p_over = curve.evaluate_parametric(1.5f);
    EXPECT_FLOAT_EQ(p_over.u, 1.0f);
    EXPECT_FLOAT_EQ(p_over.v, 1.0f);
}

TEST_F(SurfaceCurveTest, MultiSegmentLinear) {
    // Test linear curve with multiple segments
    std::vector<ParametricPoint> points = {
        ParametricPoint(0, 0.0f, 0.0f),
        ParametricPoint(0, 0.5f, 0.5f),
        ParametricPoint(0, 1.0f, 0.0f)
    };

    SurfaceCurve curve(points, CurveType::LINEAR, 1);

    // First segment midpoint
    auto p1 = curve.evaluate_parametric(0.25f);
    EXPECT_NEAR(p1.u, 0.25f, 0.01f);
    EXPECT_NEAR(p1.v, 0.25f, 0.01f);

    // Second segment midpoint
    auto p2 = curve.evaluate_parametric(0.75f);
    EXPECT_NEAR(p2.u, 0.75f, 0.01f);
    EXPECT_NEAR(p2.v, 0.25f, 0.01f);
}
