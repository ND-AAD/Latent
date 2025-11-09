#include "curvature_analyzer.h"
#include <cmath>
#include <stdexcept>
#include <algorithm>

namespace latent {

CurvatureResult CurvatureAnalyzer::compute_curvature(
    const SubDEvaluator& evaluator,
    int face_index,
    float u,
    float v) const {

    if (!evaluator.is_initialized()) {
        throw std::runtime_error("CurvatureAnalyzer: Evaluator not initialized");
    }

    CurvatureResult result;

    // Get limit surface derivatives
    Point3D position, du, dv, duu, dvv, duv;
    evaluator.evaluate_limit_with_second_derivatives(
        face_index, u, v,
        position, du, dv, duu, dvv, duv
    );

    // Compute surface normal
    result.normal = compute_normal(du, dv);

    // Compute first fundamental form (metric tensor)
    compute_first_fundamental_form(du, dv,
        result.E, result.F, result.G);

    // Compute second fundamental form (shape)
    compute_second_fundamental_form(duu, dvv, duv, result.normal,
        result.L, result.M, result.N);

    // Compute shape operator S = I^(-1) * II
    std::array<float, 4> S = compute_shape_operator(
        result.E, result.F, result.G,
        result.L, result.M, result.N
    );

    // Compute eigenvalues (principal curvatures) and eigenvectors (principal directions)
    std::array<float, 2> v1_param, v2_param;
    compute_eigensystem_2x2(S, result.kappa1, result.kappa2, v1_param, v2_param);

    // Convert parametric directions to 3D surface directions
    result.dir1 = parametric_to_surface_direction(v1_param, du, dv);
    result.dir2 = parametric_to_surface_direction(v2_param, du, dv);

    // Compute derived curvatures
    result.gaussian_curvature = result.kappa1 * result.kappa2;
    result.mean_curvature = (result.kappa1 + result.kappa2) * 0.5f;
    result.abs_mean_curvature = std::abs(result.mean_curvature);
    result.rms_curvature = std::sqrt(
        (result.kappa1 * result.kappa1 + result.kappa2 * result.kappa2) * 0.5f
    );

    return result;
}

std::vector<CurvatureResult> CurvatureAnalyzer::batch_compute_curvature(
    const SubDEvaluator& evaluator,
    const std::vector<int>& face_indices,
    const std::vector<float>& params_u,
    const std::vector<float>& params_v) const {

    if (!evaluator.is_initialized()) {
        throw std::runtime_error("CurvatureAnalyzer: Evaluator not initialized");
    }

    size_t num_points = face_indices.size();
    if (params_u.size() != num_points || params_v.size() != num_points) {
        throw std::runtime_error("CurvatureAnalyzer: Parameter array size mismatch");
    }

    std::vector<CurvatureResult> results;
    results.reserve(num_points);

    for (size_t i = 0; i < num_points; ++i) {
        results.push_back(
            compute_curvature(evaluator, face_indices[i], params_u[i], params_v[i])
        );
    }

    return results;
}

void CurvatureAnalyzer::compute_first_fundamental_form(
    const Point3D& du,
    const Point3D& dv,
    float& E, float& F, float& G) const {

    // First fundamental form coefficients
    // E = <du, du>
    // F = <du, dv>
    // G = <dv, dv>

    E = dot(du, du);
    F = dot(du, dv);
    G = dot(dv, dv);
}

void CurvatureAnalyzer::compute_second_fundamental_form(
    const Point3D& duu,
    const Point3D& dvv,
    const Point3D& duv,
    const Point3D& normal,
    float& L, float& M, float& N) const {

    // Second fundamental form coefficients
    // L = <duu, n>
    // M = <duv, n>
    // N = <dvv, n>

    L = dot(duu, normal);
    M = dot(duv, normal);
    N = dot(dvv, normal);
}

std::array<float, 4> CurvatureAnalyzer::compute_shape_operator(
    float E, float F, float G,
    float L, float M, float N) const {

    // Shape operator S = I^(-1) * II
    // where I is first fundamental form, II is second fundamental form
    //
    // I = [E F]    II = [L M]
    //     [F G]         [M N]
    //
    // First compute I^(-1):
    // I^(-1) = 1/(EG - F²) * [ G  -F]
    //                         [-F   E]

    float det_I = E * G - F * F;

    if (std::abs(det_I) < 1e-10f) {
        // Degenerate metric - return zero shape operator
        return {0.0f, 0.0f, 0.0f, 0.0f};
    }

    float inv_det = 1.0f / det_I;

    // I^(-1) in row-major order
    float I_inv_11 = G * inv_det;
    float I_inv_12 = -F * inv_det;
    float I_inv_21 = -F * inv_det;
    float I_inv_22 = E * inv_det;

    // S = I^(-1) * II
    // [S11 S12] = [I_inv_11 I_inv_12] * [L M]
    // [S21 S22]   [I_inv_21 I_inv_22]   [M N]

    float S11 = I_inv_11 * L + I_inv_12 * M;
    float S12 = I_inv_11 * M + I_inv_12 * N;
    float S21 = I_inv_21 * L + I_inv_22 * M;
    float S22 = I_inv_21 * M + I_inv_22 * N;

    return {S11, S12, S21, S22};
}

void CurvatureAnalyzer::compute_eigensystem_2x2(
    const std::array<float, 4>& matrix,
    float& lambda1, float& lambda2,
    std::array<float, 2>& v1,
    std::array<float, 2>& v2) const {

    // Extract matrix elements
    // [a b]
    // [c d]
    float a = matrix[0];
    float b = matrix[1];
    float c = matrix[2];
    float d = matrix[3];

    // For 2x2 matrix, eigenvalues are:
    // λ = (trace ± √(trace² - 4*det)) / 2
    //
    // where:
    // trace = a + d
    // det = ad - bc

    float trace = a + d;
    float det = a * d - b * c;
    float discriminant = trace * trace - 4.0f * det;

    // Handle negative discriminant (numerical error)
    if (discriminant < 0.0f) {
        discriminant = 0.0f;
    }

    float sqrt_disc = std::sqrt(discriminant);

    // Eigenvalues (ordered: lambda1 >= lambda2)
    lambda1 = (trace + sqrt_disc) * 0.5f;
    lambda2 = (trace - sqrt_disc) * 0.5f;

    // Ensure lambda1 has larger absolute value
    if (std::abs(lambda2) > std::abs(lambda1)) {
        std::swap(lambda1, lambda2);
    }

    // Compute eigenvectors
    // For eigenvalue λ, eigenvector v satisfies: (A - λI)v = 0
    //
    // For symmetric matrix, if b != 0, we can use:
    // v = [b, λ - a]
    //
    // Otherwise, use standard approach

    if (std::abs(b) > 1e-10f) {
        // Off-diagonal element significant
        v1[0] = b;
        v1[1] = lambda1 - a;
        v2[0] = b;
        v2[1] = lambda2 - a;
    } else if (std::abs(c) > 1e-10f) {
        // Use other off-diagonal element
        v1[0] = lambda1 - d;
        v1[1] = c;
        v2[0] = lambda2 - d;
        v2[1] = c;
    } else {
        // Diagonal matrix - eigenvectors are standard basis
        v1[0] = 1.0f;
        v1[1] = 0.0f;
        v2[0] = 0.0f;
        v2[1] = 1.0f;
    }

    // Normalize eigenvectors
    auto normalize_2d = [](std::array<float, 2>& v) {
        float len = std::sqrt(v[0] * v[0] + v[1] * v[1]);
        if (len > 1e-10f) {
            v[0] /= len;
            v[1] /= len;
        } else {
            v[0] = 1.0f;
            v[1] = 0.0f;
        }
    };

    normalize_2d(v1);
    normalize_2d(v2);
}

Point3D CurvatureAnalyzer::parametric_to_surface_direction(
    const std::array<float, 2>& param_dir,
    const Point3D& du,
    const Point3D& dv) const {

    // Direction (a, b) in parameter space corresponds to
    // tangent vector: a * du + b * dv

    Point3D dir;
    dir.x = param_dir[0] * du.x + param_dir[1] * dv.x;
    dir.y = param_dir[0] * du.y + param_dir[1] * dv.y;
    dir.z = param_dir[0] * du.z + param_dir[1] * dv.z;

    return normalize(dir);
}

Point3D CurvatureAnalyzer::compute_normal(const Point3D& du, const Point3D& dv) const {
    // Normal = du × dv (normalized)
    Point3D n = cross(du, dv);
    return normalize(n);
}

Point3D CurvatureAnalyzer::normalize(const Point3D& v) const {
    float len = std::sqrt(v.x * v.x + v.y * v.y + v.z * v.z);

    if (len > 1e-10f) {
        return Point3D(v.x / len, v.y / len, v.z / len);
    } else {
        // Degenerate case - return arbitrary unit vector
        return Point3D(0.0f, 0.0f, 1.0f);
    }
}

}  // namespace latent
