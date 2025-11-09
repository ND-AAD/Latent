#pragma once
#include "../geometry/types.h"
#include "../geometry/subd_evaluator.h"
#include <array>

namespace latent {

/**
 * @brief Result of curvature analysis at a point on the surface
 *
 * Contains all differential geometry quantities computed from
 * first and second fundamental forms.
 */
struct CurvatureResult {
    // Principal curvatures (eigenvalues of shape operator)
    float kappa1;  // Maximum principal curvature
    float kappa2;  // Minimum principal curvature

    // Principal directions (eigenvectors of shape operator)
    Point3D dir1;  // Direction of maximum curvature
    Point3D dir2;  // Direction of minimum curvature

    // Derived curvatures
    float gaussian_curvature;   // K = kappa1 * kappa2
    float mean_curvature;       // H = (kappa1 + kappa2) / 2
    float abs_mean_curvature;   // |H|
    float rms_curvature;        // sqrt((kappa1^2 + kappa2^2) / 2)

    // Fundamental form coefficients
    float E, F, G;  // First fundamental form
    float L, M, N;  // Second fundamental form

    // Surface normal at evaluation point
    Point3D normal;

    CurvatureResult()
        : kappa1(0), kappa2(0)
        , dir1(1, 0, 0), dir2(0, 1, 0)
        , gaussian_curvature(0), mean_curvature(0)
        , abs_mean_curvature(0), rms_curvature(0)
        , E(1), F(0), G(1)
        , L(0), M(0), N(0)
        , normal(0, 0, 1) {}
};

/**
 * @brief Curvature analyzer for SubD limit surfaces
 *
 * Computes differential geometry quantities using exact second derivatives
 * from SubD limit surface evaluation. Implements standard differential
 * geometry formulas for:
 *
 * - First fundamental form (I): metric tensor in parametric space
 * - Second fundamental form (II): shape operator in parametric space
 * - Principal curvatures: eigenvalues of shape operator S = I^(-1) * II
 * - Principal directions: eigenvectors of shape operator
 *
 * Reference: do Carmo, "Differential Geometry of Curves and Surfaces"
 *
 * Example:
 * @code
 *   SubDEvaluator eval;
 *   eval.initialize(cage);
 *
 *   CurvatureAnalyzer curvature_analyzer;
 *   CurvatureResult curv = curvature_analyzer.compute_curvature(eval, face_id, u, v);
 *
 *   std::cout << "Gaussian curvature: " << curv.gaussian_curvature << std::endl;
 *   std::cout << "Mean curvature: " << curv.mean_curvature << std::endl;
 * @endcode
 */
class CurvatureAnalyzer {
public:
    CurvatureAnalyzer() = default;

    /**
     * @brief Compute all curvature quantities at a point on the surface
     *
     * Uses exact limit surface evaluation with second derivatives to compute:
     * - First and second fundamental forms
     * - Shape operator and its eigendecomposition
     * - Principal curvatures and directions
     * - Gaussian and mean curvatures
     *
     * @param evaluator SubD evaluator (must be initialized)
     * @param face_index Control face index
     * @param u Parametric coordinate in [0,1]
     * @param v Parametric coordinate in [0,1]
     * @return CurvatureResult with all curvature data
     */
    CurvatureResult compute_curvature(
        const SubDEvaluator& evaluator,
        int face_index,
        float u,
        float v) const;

    /**
     * @brief Batch compute curvature at multiple points
     *
     * More efficient than individual calls for large numbers of points.
     *
     * @param evaluator SubD evaluator (must be initialized)
     * @param face_indices Face index for each point
     * @param params_u U parameters for each point
     * @param params_v V parameters for each point
     * @return Vector of CurvatureResult for each point
     */
    std::vector<CurvatureResult> batch_compute_curvature(
        const SubDEvaluator& evaluator,
        const std::vector<int>& face_indices,
        const std::vector<float>& params_u,
        const std::vector<float>& params_v) const;

private:
    /**
     * @brief Compute first fundamental form coefficients E, F, G
     *
     * First fundamental form (metric tensor):
     * I = E du^2 + 2F du dv + G dv^2
     * where:
     *   E = <du, du>
     *   F = <du, dv>
     *   G = <dv, dv>
     *
     * @param du First derivative wrt u
     * @param dv First derivative wrt v
     * @param E Output: E coefficient
     * @param F Output: F coefficient
     * @param G Output: G coefficient
     */
    void compute_first_fundamental_form(
        const Point3D& du,
        const Point3D& dv,
        float& E, float& F, float& G) const;

    /**
     * @brief Compute second fundamental form coefficients L, M, N
     *
     * Second fundamental form (shape operator):
     * II = L du^2 + 2M du dv + N dv^2
     * where:
     *   L = <duu, n>
     *   M = <duv, n>
     *   N = <dvv, n>
     *
     * @param duu Second derivative d²r/du²
     * @param dvv Second derivative d²r/dv²
     * @param duv Mixed derivative d²r/dudv
     * @param normal Unit surface normal
     * @param L Output: L coefficient
     * @param M Output: M coefficient
     * @param N Output: N coefficient
     */
    void compute_second_fundamental_form(
        const Point3D& duu,
        const Point3D& dvv,
        const Point3D& duv,
        const Point3D& normal,
        float& L, float& M, float& N) const;

    /**
     * @brief Compute shape operator S = I^(-1) * II
     *
     * The shape operator is a 2x2 matrix whose eigenvalues are the
     * principal curvatures and whose eigenvectors are the principal
     * directions.
     *
     * S = [E F]^(-1) * [L M]
     *     [F G]        [M N]
     *
     * @param E, F, G First fundamental form coefficients
     * @param L, M, N Second fundamental form coefficients
     * @return 2x2 shape operator matrix (row-major: [S11, S12, S21, S22])
     */
    std::array<float, 4> compute_shape_operator(
        float E, float F, float G,
        float L, float M, float N) const;

    /**
     * @brief Compute eigenvalues and eigenvectors of 2x2 symmetric matrix
     *
     * For shape operator, eigenvalues are principal curvatures and
     * eigenvectors are principal directions.
     *
     * @param matrix 2x2 matrix in row-major order [m11, m12, m21, m22]
     * @param lambda1 Output: larger eigenvalue
     * @param lambda2 Output: smaller eigenvalue
     * @param v1 Output: eigenvector for lambda1 (2D in parametric space)
     * @param v2 Output: eigenvector for lambda2 (2D in parametric space)
     */
    void compute_eigensystem_2x2(
        const std::array<float, 4>& matrix,
        float& lambda1, float& lambda2,
        std::array<float, 2>& v1,
        std::array<float, 2>& v2) const;

    /**
     * @brief Convert 2D parametric direction to 3D surface direction
     *
     * A direction (a, b) in parameter space corresponds to
     * tangent vector a*du + b*dv in 3D.
     *
     * @param param_dir Direction in parameter space [a, b]
     * @param du First derivative wrt u
     * @param dv First derivative wrt v
     * @return Normalized direction in 3D
     */
    Point3D parametric_to_surface_direction(
        const std::array<float, 2>& param_dir,
        const Point3D& du,
        const Point3D& dv) const;

    /**
     * @brief Compute surface normal from first derivatives
     *
     * Normal = (du × dv) / |du × dv|
     *
     * @param du First derivative wrt u
     * @param dv First derivative wrt v
     * @return Unit normal vector
     */
    Point3D compute_normal(const Point3D& du, const Point3D& dv) const;

    /**
     * @brief Dot product of two 3D vectors
     */
    float dot(const Point3D& a, const Point3D& b) const {
        return a.x * b.x + a.y * b.y + a.z * b.z;
    }

    /**
     * @brief Cross product of two 3D vectors
     */
    Point3D cross(const Point3D& a, const Point3D& b) const {
        return Point3D(
            a.y * b.z - a.z * b.y,
            a.z * b.x - a.x * b.z,
            a.x * b.y - a.y * b.x
        );
    }

    /**
     * @brief Normalize a 3D vector to unit length
     */
    Point3D normalize(const Point3D& v) const;
};

}  // namespace latent
