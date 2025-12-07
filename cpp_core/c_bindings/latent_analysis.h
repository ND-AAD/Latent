// cpp_core/c_bindings/latent_analysis.h
#ifndef LATENT_ANALYSIS_H
#define LATENT_ANALYSIS_H

#include "exports.h"
#include "latent_core.h"
#include <stdbool.h>

#ifdef __cplusplus
extern "C" {
#endif

//=============================================================================
// Curvature Analysis
//=============================================================================

/**
 * Compute principal curvatures at a surface point.
 *
 * @param handle Evaluator handle
 * @param face_id Face index
 * @param u U parameter
 * @param v V parameter
 * @param out_k1 Output maximum principal curvature
 * @param out_k2 Output minimum principal curvature
 * @param out_H Output mean curvature (k1 + k2) / 2
 * @param out_K Output Gaussian curvature (k1 * k2)
 * @return true on success
 */
LATENT_API bool latent_compute_curvature(
    LatentEvaluatorHandle handle,
    int face_id, float u, float v,
    float* out_k1, float* out_k2,
    float* out_H, float* out_K
);

/**
 * Compute principal curvature directions at a surface point.
 *
 * @param handle Evaluator handle
 * @param face_id Face index
 * @param u U parameter
 * @param v V parameter
 * @param out_dir1 Output direction of maximum curvature (3 floats)
 * @param out_dir2 Output direction of minimum curvature (3 floats)
 * @return true on success
 */
LATENT_API bool latent_compute_curvature_directions(
    LatentEvaluatorHandle handle,
    int face_id, float u, float v,
    float* out_dir1, float* out_dir2
);

/**
 * Sample curvature values across a grid on one face.
 *
 * @param handle Evaluator handle
 * @param face_id Face index
 * @param resolution Grid resolution (resolution x resolution samples)
 * @param out_H Output mean curvature values (resolution * resolution floats)
 * @param out_K Output Gaussian curvature values (resolution * resolution floats)
 * @return true on success
 */
LATENT_API bool latent_sample_curvature_grid(
    LatentEvaluatorHandle handle,
    int face_id,
    int resolution,
    float* out_H,
    float* out_K
);

#ifdef __cplusplus
}
#endif

#endif // LATENT_ANALYSIS_H
