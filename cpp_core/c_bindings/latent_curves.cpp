// cpp_core/c_bindings/latent_curves.cpp
#include "latent_curves.h"
#include "../geometry/subd_evaluator.h"
#include "../geometry/surface_curve.h"

using namespace latent;

//=============================================================================
// Curve Lifecycle
//=============================================================================

LATENT_API LatentCurveHandle latent_curve_create(
    const int* face_ids,
    const float* us,
    const float* vs,
    int point_count,
    LatentCurveType curve_type,
    int degree)
{
    if (!face_ids || !us || !vs || point_count <= 0) {
        return nullptr;
    }

    try {
        std::vector<ParametricPoint> points;
        points.reserve(point_count);

        for (int i = 0; i < point_count; ++i) {
            points.emplace_back(face_ids[i], us[i], vs[i]);
        }

        CurveType type;
        switch (curve_type) {
            case LATENT_CURVE_LINEAR:  type = CurveType::LINEAR; break;
            case LATENT_CURVE_BEZIER:  type = CurveType::BEZIER; break;
            case LATENT_CURVE_BSPLINE: type = CurveType::BSPLINE; break;
            default: type = CurveType::BEZIER;
        }

        return static_cast<LatentCurveHandle>(
            new SurfaceCurve(points, type, degree)
        );

    } catch (...) {
        return nullptr;
    }
}

LATENT_API void latent_curve_destroy(LatentCurveHandle handle) {
    if (handle) {
        delete static_cast<SurfaceCurve*>(handle);
    }
}

//=============================================================================
// Curve Evaluation
//=============================================================================

LATENT_API bool latent_curve_evaluate(
    LatentCurveHandle handle,
    LatentEvaluatorHandle evaluator,
    float t,
    float* out_x, float* out_y, float* out_z)
{
    if (!handle || !evaluator || !out_x || !out_y || !out_z) {
        return false;
    }

    try {
        auto* curve = static_cast<SurfaceCurve*>(handle);
        auto* eval = static_cast<SubDEvaluator*>(evaluator);

        Point3D point = curve->evaluate(t, *eval);
        *out_x = point.x;
        *out_y = point.y;
        *out_z = point.z;
        return true;

    } catch (...) {
        return false;
    }
}

LATENT_API bool latent_curve_evaluate_parametric(
    LatentCurveHandle handle,
    float t,
    int* out_face_id, float* out_u, float* out_v)
{
    if (!handle || !out_face_id || !out_u || !out_v) {
        return false;
    }

    try {
        auto* curve = static_cast<SurfaceCurve*>(handle);
        ParametricPoint p = curve->evaluate_parametric(t);

        *out_face_id = p.face_id;
        *out_u = p.u;
        *out_v = p.v;
        return p.is_valid();

    } catch (...) {
        return false;
    }
}

LATENT_API bool latent_curve_sample(
    LatentCurveHandle handle,
    LatentEvaluatorHandle evaluator,
    int num_samples,
    float* out_points)
{
    if (!handle || !evaluator || !out_points || num_samples <= 0) {
        return false;
    }

    try {
        auto* curve = static_cast<SurfaceCurve*>(handle);
        auto* eval = static_cast<SubDEvaluator*>(evaluator);

        std::vector<Point3D> samples = curve->sample(num_samples, *eval);

        for (size_t i = 0; i < samples.size(); ++i) {
            out_points[i * 3 + 0] = samples[i].x;
            out_points[i * 3 + 1] = samples[i].y;
            out_points[i * 3 + 2] = samples[i].z;
        }

        return true;

    } catch (...) {
        return false;
    }
}

LATENT_API bool latent_curve_arc_length(
    LatentCurveHandle handle,
    LatentEvaluatorHandle evaluator,
    float* out_length)
{
    if (!handle || !evaluator || !out_length) {
        return false;
    }

    try {
        auto* curve = static_cast<SurfaceCurve*>(handle);
        auto* eval = static_cast<SubDEvaluator*>(evaluator);

        *out_length = curve->arc_length(*eval, 100);
        return true;

    } catch (...) {
        return false;
    }
}

//=============================================================================
// Curve Properties
//=============================================================================

LATENT_API int latent_curve_get_point_count(LatentCurveHandle handle) {
    if (!handle) return 0;
    auto* curve = static_cast<SurfaceCurve*>(handle);
    return static_cast<int>(curve->get_control_points().size());
}

LATENT_API LatentCurveType latent_curve_get_type(LatentCurveHandle handle) {
    if (!handle) return LATENT_CURVE_BEZIER;
    auto* curve = static_cast<SurfaceCurve*>(handle);

    switch (curve->get_type()) {
        case CurveType::LINEAR:  return LATENT_CURVE_LINEAR;
        case CurveType::BEZIER:  return LATENT_CURVE_BEZIER;
        case CurveType::BSPLINE: return LATENT_CURVE_BSPLINE;
        default: return LATENT_CURVE_BEZIER;
    }
}

LATENT_API int latent_curve_get_degree(LatentCurveHandle handle) {
    if (!handle) return 0;
    auto* curve = static_cast<SurfaceCurve*>(handle);
    return curve->get_degree();
}
