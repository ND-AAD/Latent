#pragma once
#include "types.h"
#include <opensubdiv/far/topologyRefiner.h>
#include <opensubdiv/far/topologyDescriptor.h>
#include <opensubdiv/far/primvarRefiner.h>
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
    std::vector<int> triangle_to_face_map_;
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
                                   bool adaptive = false);

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
};

}  // namespace latent
