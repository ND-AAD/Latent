// cpp_core/c_bindings/latent_curves.h
#ifndef LATENT_CURVES_H
#define LATENT_CURVES_H

#include "exports.h"
#include "latent_core.h"
#include <stdbool.h>

#ifdef __cplusplus
extern "C" {
#endif

//=============================================================================
// Handle Types
//=============================================================================

/** Opaque handle to surface curve */
typedef void* LatentCurveHandle;

//=============================================================================
// Curve Types
//=============================================================================

typedef enum {
    LATENT_CURVE_LINEAR = 0,
    LATENT_CURVE_BEZIER = 1,
    LATENT_CURVE_BSPLINE = 2
} LatentCurveType;

//=============================================================================
// Curve Lifecycle
//=============================================================================

/**
 * Create a surface curve from control points.
 *
 * @param face_ids Array of face indices for each control point
 * @param us Array of U parameters for each control point
 * @param vs Array of V parameters for each control point
 * @param point_count Number of control points
 * @param curve_type Type of curve interpolation
 * @param degree Curve degree (for Bezier/B-spline)
 * @return Handle to the curve, or NULL on failure
 */
LATENT_API LatentCurveHandle latent_curve_create(
    const int* face_ids,
    const float* us,
    const float* vs,
    int point_count,
    LatentCurveType curve_type,
    int degree
);

/**
 * Destroy a surface curve and free resources.
 * @param handle Curve handle (safe to call with NULL)
 */
LATENT_API void latent_curve_destroy(LatentCurveHandle handle);

//=============================================================================
// Curve Evaluation
//=============================================================================

/**
 * Evaluate a point on the curve.
 *
 * @param handle Curve handle
 * @param evaluator Evaluator handle for surface lookup
 * @param t Curve parameter [0, 1]
 * @param out_x Output X coordinate
 * @param out_y Output Y coordinate
 * @param out_z Output Z coordinate
 * @return true on success
 */
LATENT_API bool latent_curve_evaluate(
    LatentCurveHandle handle,
    LatentEvaluatorHandle evaluator,
    float t,
    float* out_x, float* out_y, float* out_z
);

/**
 * Evaluate the parametric position on the curve.
 *
 * @param handle Curve handle
 * @param t Curve parameter [0, 1]
 * @param out_face_id Output face index
 * @param out_u Output U parameter
 * @param out_v Output V parameter
 * @return true on success
 */
LATENT_API bool latent_curve_evaluate_parametric(
    LatentCurveHandle handle,
    float t,
    int* out_face_id, float* out_u, float* out_v
);

/**
 * Sample the curve for display.
 *
 * @param handle Curve handle
 * @param evaluator Evaluator handle
 * @param num_samples Number of sample points
 * @param out_points Output array (must have space for num_samples * 3 floats)
 * @return true on success
 */
LATENT_API bool latent_curve_sample(
    LatentCurveHandle handle,
    LatentEvaluatorHandle evaluator,
    int num_samples,
    float* out_points
);

/**
 * Get the arc length of the curve.
 *
 * @param handle Curve handle
 * @param evaluator Evaluator handle
 * @param out_length Output arc length
 * @return true on success
 */
LATENT_API bool latent_curve_arc_length(
    LatentCurveHandle handle,
    LatentEvaluatorHandle evaluator,
    float* out_length
);

//=============================================================================
// Curve Properties
//=============================================================================

/**
 * Get the number of control points.
 * @param handle Curve handle
 * @return Number of control points
 */
LATENT_API int latent_curve_get_point_count(LatentCurveHandle handle);

/**
 * Get the curve type.
 * @param handle Curve handle
 * @return Curve type enum value
 */
LATENT_API LatentCurveType latent_curve_get_type(LatentCurveHandle handle);

/**
 * Get the curve degree.
 * @param handle Curve handle
 * @return Curve degree
 */
LATENT_API int latent_curve_get_degree(LatentCurveHandle handle);

#ifdef __cplusplus
}
#endif

#endif // LATENT_CURVES_H
