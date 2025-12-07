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
