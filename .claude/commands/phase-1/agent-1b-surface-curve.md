# Agent 1B: Surface Curve Implementation

## Objective

Implement parametric curves on the SubD limit surface (Bezier and B-spline in parameter space).

## Working Directory

`/Users/NickDuch/.claude-worktrees/Latent/focused-robinson`

## Read First

- `cpp_core/geometry/subd_evaluator.h` - surface evaluation interface
- `CLAUDE.md` - lossless architecture (curves defined parametrically)

## Files to Create

1. `cpp_core/geometry/surface_curve.h` - curve class declarations
2. `cpp_core/geometry/surface_curve.cpp` - curve implementations
3. `cpp_core/tests/test_surface_curve.cpp` - unit tests

## Tasks

### 1. Create surface_curve.h

```cpp
// cpp_core/geometry/surface_curve.h
#ifndef SURFACE_CURVE_H
#define SURFACE_CURVE_H

#include <vector>
#include "subd_evaluator.h"

namespace latent {

/**
 * A point in the parametric space of the SubD surface.
 */
struct ParametricPoint {
    int face_id;
    float u;
    float v;

    ParametricPoint() : face_id(-1), u(0), v(0) {}
    ParametricPoint(int f, float u_, float v_) : face_id(f), u(u_), v(v_) {}

    bool is_valid() const { return face_id >= 0; }
};

/**
 * Type of curve interpolation.
 */
enum class CurveType {
    LINEAR,     // Linear interpolation between control points
    BEZIER,     // Bezier curve
    BSPLINE     // B-spline curve
};

/**
 * A curve defined by control points in the parametric space of a SubD surface.
 *
 * The curve is evaluated by:
 * 1. Interpolating control points in parameter space using the curve type
 * 2. Evaluating the SubD surface at the resulting (face_id, u, v) position
 */
class SurfaceCurve {
public:
    SurfaceCurve();
    SurfaceCurve(const std::vector<ParametricPoint>& control_points,
                 CurveType type = CurveType::BEZIER,
                 int degree = 3);

    // Accessors
    const std::vector<ParametricPoint>& get_control_points() const { return control_points_; }
    CurveType get_type() const { return type_; }
    int get_degree() const { return degree_; }

    // Mutators
    void set_control_points(const std::vector<ParametricPoint>& points);
    void set_type(CurveType type);
    void set_degree(int degree);

    /**
     * Evaluate the curve at parameter t ∈ [0, 1].
     *
     * @param t Curve parameter [0, 1]
     * @param evaluator SubD evaluator for surface lookup
     * @return 3D point on the limit surface
     */
    Point3D evaluate(float t, const SubDEvaluator& evaluator) const;

    /**
     * Get the parametric point at parameter t.
     *
     * @param t Curve parameter [0, 1]
     * @return Parametric point (face_id, u, v)
     */
    ParametricPoint evaluate_parametric(float t) const;

    /**
     * Sample the curve for display.
     *
     * @param num_samples Number of sample points
     * @param evaluator SubD evaluator for surface lookup
     * @return Vector of 3D points on the surface
     */
    std::vector<Point3D> sample(int num_samples, const SubDEvaluator& evaluator) const;

    /**
     * Get the tangent vector at parameter t.
     *
     * @param t Curve parameter [0, 1]
     * @param evaluator SubD evaluator for derivatives
     * @return 3D tangent vector
     */
    Vector3 tangent(float t, const SubDEvaluator& evaluator) const;

    /**
     * Get the arc length of the curve (approximate).
     *
     * @param evaluator SubD evaluator
     * @param num_samples Samples for approximation
     * @return Approximate arc length
     */
    float arc_length(const SubDEvaluator& evaluator, int num_samples = 100) const;

private:
    std::vector<ParametricPoint> control_points_;
    CurveType type_;
    int degree_;

    // Bezier evaluation using de Casteljau
    ParametricPoint evaluate_bezier(float t) const;

    // B-spline evaluation
    ParametricPoint evaluate_bspline(float t) const;

    // Linear interpolation
    ParametricPoint evaluate_linear(float t) const;

    // B-spline basis function
    float bspline_basis(int i, int k, float t, const std::vector<float>& knots) const;
};

} // namespace latent

#endif // SURFACE_CURVE_H
```

### 2. Create surface_curve.cpp

```cpp
// cpp_core/geometry/surface_curve.cpp
#include "surface_curve.h"
#include <cmath>
#include <algorithm>

namespace latent {

SurfaceCurve::SurfaceCurve()
    : type_(CurveType::BEZIER), degree_(3) {}

SurfaceCurve::SurfaceCurve(const std::vector<ParametricPoint>& control_points,
                           CurveType type, int degree)
    : control_points_(control_points), type_(type), degree_(degree) {}

void SurfaceCurve::set_control_points(const std::vector<ParametricPoint>& points) {
    control_points_ = points;
}

void SurfaceCurve::set_type(CurveType type) {
    type_ = type;
}

void SurfaceCurve::set_degree(int degree) {
    degree_ = degree;
}

ParametricPoint SurfaceCurve::evaluate_parametric(float t) const {
    if (control_points_.empty()) {
        return ParametricPoint();
    }

    t = std::clamp(t, 0.0f, 1.0f);

    switch (type_) {
        case CurveType::LINEAR:
            return evaluate_linear(t);
        case CurveType::BEZIER:
            return evaluate_bezier(t);
        case CurveType::BSPLINE:
            return evaluate_bspline(t);
        default:
            return evaluate_bezier(t);
    }
}

Point3D SurfaceCurve::evaluate(float t, const SubDEvaluator& evaluator) const {
    ParametricPoint p = evaluate_parametric(t);
    if (!p.is_valid()) {
        return Point3D(0, 0, 0);
    }
    return evaluator.evaluate_limit_point(p.face_id, p.u, p.v);
}

std::vector<Point3D> SurfaceCurve::sample(int num_samples, const SubDEvaluator& evaluator) const {
    std::vector<Point3D> points;
    points.reserve(num_samples);

    for (int i = 0; i < num_samples; ++i) {
        float t = static_cast<float>(i) / static_cast<float>(num_samples - 1);
        points.push_back(evaluate(t, evaluator));
    }

    return points;
}

Vector3 SurfaceCurve::tangent(float t, const SubDEvaluator& evaluator) const {
    // Approximate tangent using finite differences
    const float epsilon = 0.001f;
    float t0 = std::max(0.0f, t - epsilon);
    float t1 = std::min(1.0f, t + epsilon);

    Point3D p0 = evaluate(t0, evaluator);
    Point3D p1 = evaluate(t1, evaluator);

    Vector3 tan = p1 - p0;
    tan.normalize();
    return tan;
}

float SurfaceCurve::arc_length(const SubDEvaluator& evaluator, int num_samples) const {
    float length = 0.0f;
    Point3D prev = evaluate(0.0f, evaluator);

    for (int i = 1; i < num_samples; ++i) {
        float t = static_cast<float>(i) / static_cast<float>(num_samples - 1);
        Point3D curr = evaluate(t, evaluator);
        length += (curr - prev).length();
        prev = curr;
    }

    return length;
}

// De Casteljau's algorithm for Bezier curves
ParametricPoint SurfaceCurve::evaluate_bezier(float t) const {
    if (control_points_.size() == 1) {
        return control_points_[0];
    }

    // Copy control points for de Casteljau
    std::vector<ParametricPoint> points = control_points_;
    int n = points.size();

    for (int r = 1; r < n; ++r) {
        for (int i = 0; i < n - r; ++i) {
            // Linear interpolation in parameter space
            // Note: face_id handling for cross-face curves would need more work
            points[i].u = (1 - t) * points[i].u + t * points[i + 1].u;
            points[i].v = (1 - t) * points[i].v + t * points[i + 1].v;

            // For now, use the face_id of the first point if they differ
            // TODO: Handle face transitions properly
            if (points[i].face_id != points[i + 1].face_id) {
                // Use weighted selection based on t
                points[i].face_id = (t < 0.5f) ? points[i].face_id : points[i + 1].face_id;
            }
        }
    }

    return points[0];
}

ParametricPoint SurfaceCurve::evaluate_linear(float t) const {
    if (control_points_.size() == 1) {
        return control_points_[0];
    }

    // Find which segment we're in
    int n = control_points_.size() - 1;
    float segment_t = t * n;
    int segment = static_cast<int>(segment_t);
    segment = std::min(segment, n - 1);

    float local_t = segment_t - segment;

    const ParametricPoint& p0 = control_points_[segment];
    const ParametricPoint& p1 = control_points_[segment + 1];

    ParametricPoint result;
    result.u = (1 - local_t) * p0.u + local_t * p1.u;
    result.v = (1 - local_t) * p0.v + local_t * p1.v;
    result.face_id = (local_t < 0.5f) ? p0.face_id : p1.face_id;

    return result;
}

ParametricPoint SurfaceCurve::evaluate_bspline(float t) const {
    int n = control_points_.size();
    int k = std::min(degree_ + 1, n);  // Order = degree + 1

    // Create uniform knot vector
    std::vector<float> knots;
    int num_knots = n + k;
    for (int i = 0; i < num_knots; ++i) {
        if (i < k) {
            knots.push_back(0.0f);
        } else if (i >= n) {
            knots.push_back(1.0f);
        } else {
            knots.push_back(static_cast<float>(i - k + 1) / static_cast<float>(n - k + 1));
        }
    }

    // Evaluate B-spline
    ParametricPoint result;
    result.face_id = control_points_[0].face_id;
    result.u = 0.0f;
    result.v = 0.0f;

    float weight_sum = 0.0f;

    for (int i = 0; i < n; ++i) {
        float basis = bspline_basis(i, k, t, knots);
        result.u += basis * control_points_[i].u;
        result.v += basis * control_points_[i].v;
        weight_sum += basis;

        // Track dominant control point for face_id
        if (basis > 0.5f) {
            result.face_id = control_points_[i].face_id;
        }
    }

    if (weight_sum > 0.0f) {
        result.u /= weight_sum;
        result.v /= weight_sum;
    }

    return result;
}

float SurfaceCurve::bspline_basis(int i, int k, float t, const std::vector<float>& knots) const {
    if (k == 1) {
        if (t >= knots[i] && t < knots[i + 1]) {
            return 1.0f;
        }
        // Handle end point
        if (t == 1.0f && knots[i + 1] == 1.0f && knots[i] < 1.0f) {
            return 1.0f;
        }
        return 0.0f;
    }

    float left = 0.0f, right = 0.0f;

    float denom_left = knots[i + k - 1] - knots[i];
    if (denom_left > 0.0f) {
        left = (t - knots[i]) / denom_left * bspline_basis(i, k - 1, t, knots);
    }

    float denom_right = knots[i + k] - knots[i + 1];
    if (denom_right > 0.0f) {
        right = (knots[i + k] - t) / denom_right * bspline_basis(i + 1, k - 1, t, knots);
    }

    return left + right;
}

} // namespace latent
```

### 3. Create Unit Tests

```cpp
// cpp_core/tests/test_surface_curve.cpp
#include <gtest/gtest.h>
#include "geometry/surface_curve.h"

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

        evaluator.initialize(vertices.data(), 8,
                            faces.data(), face_sizes.data(), 6,
                            nullptr, nullptr, 0);
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
```

### 4. Update CMakeLists.txt

Add to `cpp_core/CMakeLists.txt`:

```cmake
# Add surface_curve to geometry sources
set(GEOMETRY_SOURCES
    geometry/subd_evaluator.cpp
    geometry/surface_curve.cpp  # NEW
)
```

## Success Criteria

- [ ] `SurfaceCurve` class compiles without errors
- [ ] Bezier curves interpolate endpoints exactly
- [ ] B-spline curves approximate control polygon
- [ ] Linear interpolation works segment-by-segment
- [ ] `sample()` produces smooth curves on the surface
- [ ] All unit tests pass

## Verification Commands

```bash
cd cpp_core/build
cmake .. && make -j4
./test_surface_curve
```

## Do Not Modify

- `subd_evaluator.h/cpp` (Agent 1A's domain)
- Files in `c_bindings/` (Agent 1C/1D's domain)
- Files outside `geometry/` directory

## Skills to Use

- `superpowers:test-driven-development` - write tests first
- `superpowers:verification-before-completion` - run tests before reporting

## Notes

**Cross-face curves**: The current implementation handles single-face curves well. Cross-face curves (where control points are on different faces) use a simplified approach of selecting face_id based on parameter t. A more sophisticated implementation would trace the geodesic path across faces, but this is deferred to a future enhancement.

## Report

When complete, provide:
1. Test output showing all tests pass
2. Sample output showing curve evaluation works
3. Any limitations discovered (especially with cross-face curves)
