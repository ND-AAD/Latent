// cpp_core/geometry/nurbs_fitting.cpp

#include "nurbs_generator.h"
#include <GeomAPI_PointsToBSplineSurface.hxx>
#include <TColgp_Array2OfPnt.hxx>
#include <gp_Pnt.hxx>
#include <stdexcept>
#include <cmath>

namespace latent {

NURBSMoldGenerator::NURBSMoldGenerator(const SubDEvaluator& evaluator)
    : evaluator_(evaluator) {
}

Handle(Geom_BSplineSurface) NURBSMoldGenerator::fit_nurbs_surface(
    const std::vector<int>& face_indices,
    int sample_density) {

    if (face_indices.empty()) {
        throw std::runtime_error("Cannot fit NURBS surface with no faces");
    }

    if (sample_density < 2) {
        throw std::runtime_error("Sample density must be at least 2");
    }

    // NOTE: Current implementation handles single faces.
    // Multi-face regions require topology/connectivity information
    // to create unified parametrization. This will be added in future
    // when region boundary stitching is implemented.
    if (face_indices.size() > 1) {
        throw std::runtime_error(
            "Multi-face NURBS fitting not yet implemented. "
            "Current version handles single-face regions. "
            "Multi-face support requires topology-aware parametrization."
        );
    }

    // Sample exact limit surface (single face for now)
    std::vector<Point3D> samples = sample_limit_surface(face_indices, sample_density);

    if (samples.empty()) {
        throw std::runtime_error("No samples generated from limit surface");
    }

    // Verify we got the expected number of samples
    int expected_samples = sample_density * sample_density;
    if (static_cast<int>(samples.size()) != expected_samples) {
        throw std::runtime_error(
            "Unexpected sample count: got " + std::to_string(samples.size()) +
            ", expected " + std::to_string(expected_samples)
        );
    }

    // Convert to OpenCASCADE 2D array of points
    int n = sample_density;
    TColgp_Array2OfPnt points(1, n, 1, n);

    for (int i = 0; i < n; ++i) {
        for (int j = 0; j < n; ++j) {
            int idx = i * n + j;
            points.SetValue(i + 1, j + 1,
                gp_Pnt(samples[idx].x, samples[idx].y, samples[idx].z));
        }
    }

    // Fit B-spline surface using OpenCASCADE
    GeomAPI_PointsToBSplineSurface fitter(points);

    if (!fitter.IsDone()) {
        throw std::runtime_error("NURBS fitting failed");
    }

    return fitter.Surface();
}

std::vector<Point3D> NURBSMoldGenerator::sample_limit_surface(
    const std::vector<int>& face_indices,
    int density) {

    std::vector<Point3D> samples;
    samples.reserve(face_indices.size() * density * density);

    for (int face_id : face_indices) {
        // Sample face at regular grid
        for (int i = 0; i < density; ++i) {
            for (int j = 0; j < density; ++j) {
                float u = static_cast<float>(i) / (density - 1);
                float v = static_cast<float>(j) / (density - 1);

                // EXACT limit evaluation
                Point3D pt = evaluator_.evaluate_limit_point(face_id, u, v);
                samples.push_back(pt);
            }
        }
    }

    return samples;
}

NURBSMoldGenerator::FittingQuality NURBSMoldGenerator::check_fitting_quality(
    Handle(Geom_BSplineSurface) nurbs,
    const std::vector<int>& face_indices) {

    FittingQuality quality;
    quality.max_deviation = 0.0f;
    quality.mean_deviation = 0.0f;
    quality.rms_deviation = 0.0f;
    quality.num_samples = 0;
    quality.passes_tolerance = false;

    if (nurbs.IsNull() || face_indices.empty()) {
        return quality;
    }

    // Sample the original limit surface
    const int check_density = 20;
    std::vector<Point3D> original_samples = sample_limit_surface(face_indices, check_density);

    if (original_samples.empty()) {
        return quality;
    }

    float sum_deviation = 0.0f;
    float sum_sq_deviation = 0.0f;
    int n = check_density;

    // Check deviation at each sample point
    for (size_t idx = 0; idx < original_samples.size(); ++idx) {
        // Map back to UV coordinates
        int i = (idx / n) % n;
        int j = idx % n;
        
        float u = static_cast<float>(i) / (n - 1);
        float v = static_cast<float>(j) / (n - 1);

        // Evaluate NURBS at same UV
        gp_Pnt nurbs_pt;
        nurbs->D0(u, v, nurbs_pt);

        // Compute deviation
        Point3D orig = original_samples[idx];
        float dx = nurbs_pt.X() - orig.x;
        float dy = nurbs_pt.Y() - orig.y;
        float dz = nurbs_pt.Z() - orig.z;
        float deviation = std::sqrt(dx*dx + dy*dy + dz*dz);

        sum_deviation += deviation;
        sum_sq_deviation += deviation * deviation;

        if (deviation > quality.max_deviation) {
            quality.max_deviation = deviation;
        }
    }

    quality.num_samples = static_cast<int>(original_samples.size());
    quality.mean_deviation = sum_deviation / quality.num_samples;
    quality.rms_deviation = std::sqrt(sum_sq_deviation / quality.num_samples);

    // Check tolerance: max deviation must be < 0.1mm
    const float tolerance_mm = 0.1f;
    quality.passes_tolerance = (quality.max_deviation < tolerance_mm);

    return quality;
}

} // namespace latent
