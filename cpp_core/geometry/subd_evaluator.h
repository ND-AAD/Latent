#pragma once
#include "types.h"
#include <opensubdiv/far/topologyRefiner.h>
#include <opensubdiv/far/topologyDescriptor.h>
#include <opensubdiv/far/primvarRefiner.h>
#include <opensubdiv/far/patchTable.h>
#include <memory>
#include <vector>

namespace latent {

/**
 * @brief Evaluates exact limit surface of SubD control cage
 *
 * Uses OpenSubdiv to build TopologyRefiner and evaluate limit surface
 * using Stam's eigenanalysis. Provides both tessellation for display
 * and exact point evaluation for analysis.
 *
 * Example:
 * @code
 *   SubDControlCage cage = ...;
 *   SubDEvaluator eval;
 *   eval.initialize(cage);
 *   TessellationResult mesh = eval.tessellate(3);  // Level 3
 *   Point3D pt = eval.evaluate_limit_point(0, 0.5, 0.5);
 * @endcode
 */
class SubDEvaluator {
private:
    std::unique_ptr<OpenSubdiv::Far::TopologyRefiner> refiner_;
    mutable std::vector<int> triangle_to_face_map_;  // Mutable for tessellation caching
    bool initialized_;

public:
    SubDEvaluator();
    ~SubDEvaluator();

    /**
     * @brief Build subdivision topology from control cage
     * @param cage Control cage with vertices, faces, and creases
     */
    void initialize(const SubDControlCage& cage);

    /**
     * @brief Check if evaluator has been initialized
     * @return true if initialized with a control cage
     */
    bool is_initialized() const { return initialized_; }

    /**
     * @brief Tessellate subdivided surface into triangles for display
     * @param subdivision_level Number of subdivision iterations (default 3)
     * @param adaptive Use adaptive subdivision (default false)
     * @return Triangulated mesh with vertices, normals, and topology
     */
    TessellationResult tessellate(int subdivision_level = 3,
                                   bool adaptive = false) const;

    /**
     * @brief Evaluate exact point on limit surface
     * @param face_index Control face index
     * @param u Parametric coordinate (0-1)
     * @param v Parametric coordinate (0-1)
     * @return Point on limit surface
     */
    Point3D evaluate_limit_point(int face_index, float u, float v) const;

    /**
     * @brief Evaluate point and normal on limit surface
     * @param face_index Control face index
     * @param u Parametric coordinate (0-1)
     * @param v Parametric coordinate (0-1)
     * @param point Output: point on limit surface
     * @param normal Output: unit normal at point
     */
    void evaluate_limit(int face_index, float u, float v,
                       Point3D& point, Point3D& normal) const;

    /**
     * @brief Get parent control face for a tessellated triangle
     * @param triangle_index Index into tessellation result triangles
     * @return Index of parent control face
     */
    int get_parent_face(int triangle_index) const;

    /**
     * @brief Get number of vertices in control cage
     * @return Vertex count
     */
    size_t get_control_vertex_count() const;

    /**
     * @brief Get number of faces in control cage
     * @return Face count
     */
    size_t get_control_face_count() const;

    // ============================================================
    // Advanced Limit Surface Evaluation (Day 2, Agent 10)
    // ============================================================

    /**
     * Evaluate limit position and first derivatives
     *
     * @param face_index Control face index
     * @param u Parameter u in [0,1]
     * @param v Parameter v in [0,1]
     * @param position Output: limit position
     * @param du Output: first derivative wrt u
     * @param dv Output: first derivative wrt v
     */
    void evaluate_limit_with_derivatives(
        int face_index, float u, float v,
        Point3D& position,
        Point3D& du,
        Point3D& dv) const;

    /**
     * Evaluate limit position and first/second derivatives
     *
     * @param face_index Control face index
     * @param u Parameter u in [0,1]
     * @param v Parameter v in [0,1]
     * @param position Output: limit position
     * @param du, dv Output: first derivatives
     * @param duu, dvv, duv Output: second derivatives
     */
    void evaluate_limit_with_second_derivatives(
        int face_index, float u, float v,
        Point3D& position,
        Point3D& du, Point3D& dv,
        Point3D& duu, Point3D& dvv, Point3D& duv) const;

    /**
     * Batch evaluate multiple points on limit surface
     * More efficient than individual calls
     *
     * @param face_indices Face index for each point
     * @param params_u U parameters for each point
     * @param params_v V parameters for each point
     * @return TessellationResult with evaluated points
     */
    TessellationResult batch_evaluate_limit(
        const std::vector<int>& face_indices,
        const std::vector<float>& params_u,
        const std::vector<float>& params_v) const;

    /**
     * Compute tangent frame (tangent_u, tangent_v, normal)
     *
     * @param face_index Control face index
     * @param u Parameter u in [0,1]
     * @param v Parameter v in [0,1]
     * @param tangent_u Output: normalized tangent in u direction
     * @param tangent_v Output: normalized tangent in v direction
     * @param normal Output: unit normal (cross product of tangents)
     */
    void compute_tangent_frame(
        int face_index, float u, float v,
        Point3D& tangent_u,
        Point3D& tangent_v,
        Point3D& normal) const;

private:
    // Helper for derivative evaluation - PatchTable for exact limit evaluation
    mutable std::unique_ptr<OpenSubdiv::Far::PatchTable const> patch_table_;

    // Control vertex positions stored as flat array for patch evaluation
    std::vector<float> control_positions_;

    // Build patch table on first use (lazy initialization)
    void ensure_patch_table() const;
};

}  // namespace latent
