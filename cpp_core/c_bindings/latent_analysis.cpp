// cpp_core/c_bindings/latent_analysis.cpp
#include "latent_analysis.h"
#include "../geometry/subd_evaluator.h"
#include "../analysis/curvature_analyzer.h"

using namespace latent;

//=============================================================================
// Curvature Analysis
//=============================================================================

LATENT_API bool latent_compute_curvature(
    LatentEvaluatorHandle handle,
    int face_id, float u, float v,
    float* out_k1, float* out_k2,
    float* out_H, float* out_K)
{
    if (!handle || !out_k1 || !out_k2 || !out_H || !out_K) {
        return false;
    }

    try {
        auto* evaluator = static_cast<SubDEvaluator*>(handle);
        CurvatureAnalyzer analyzer;

        CurvatureResult result = analyzer.compute_curvature(
            *evaluator, face_id, u, v
        );

        *out_k1 = result.kappa1;
        *out_k2 = result.kappa2;
        *out_H = result.mean_curvature;
        *out_K = result.gaussian_curvature;

        return true;
    } catch (...) {
        return false;
    }
}

LATENT_API bool latent_compute_curvature_directions(
    LatentEvaluatorHandle handle,
    int face_id, float u, float v,
    float* out_dir1, float* out_dir2)
{
    if (!handle || !out_dir1 || !out_dir2) {
        return false;
    }

    try {
        auto* evaluator = static_cast<SubDEvaluator*>(handle);
        CurvatureAnalyzer analyzer;

        CurvatureResult result = analyzer.compute_curvature(
            *evaluator, face_id, u, v
        );

        out_dir1[0] = result.dir1.x;
        out_dir1[1] = result.dir1.y;
        out_dir1[2] = result.dir1.z;

        out_dir2[0] = result.dir2.x;
        out_dir2[1] = result.dir2.y;
        out_dir2[2] = result.dir2.z;

        return true;
    } catch (...) {
        return false;
    }
}

LATENT_API bool latent_sample_curvature_grid(
    LatentEvaluatorHandle handle,
    int face_id,
    int resolution,
    float* out_H,
    float* out_K)
{
    if (!handle || !out_H || !out_K || resolution <= 0) {
        return false;
    }

    try {
        auto* evaluator = static_cast<SubDEvaluator*>(handle);
        CurvatureAnalyzer analyzer;

        for (int j = 0; j < resolution; ++j) {
            for (int i = 0; i < resolution; ++i) {
                float u = static_cast<float>(i) / (resolution - 1);
                float v = static_cast<float>(j) / (resolution - 1);

                CurvatureResult result = analyzer.compute_curvature(
                    *evaluator, face_id, u, v
                );

                int idx = j * resolution + i;
                out_H[idx] = result.mean_curvature;
                out_K[idx] = result.gaussian_curvature;
            }
        }

        return true;
    } catch (...) {
        return false;
    }
}
