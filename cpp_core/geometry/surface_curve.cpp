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
