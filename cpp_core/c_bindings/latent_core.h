// cpp_core/c_bindings/latent_core.h
#ifndef LATENT_CORE_H
#define LATENT_CORE_H

#include "exports.h"
#include <stdbool.h>

#ifdef __cplusplus
extern "C" {
#endif

//=============================================================================
// Handle Types
//=============================================================================

/** Opaque handle to SubD evaluator */
typedef void* LatentEvaluatorHandle;

//=============================================================================
// Evaluator Lifecycle
//=============================================================================

/**
 * Create a new SubD evaluator instance.
 * @return Handle to the evaluator, or NULL on failure
 */
LATENT_API LatentEvaluatorHandle latent_evaluator_create(void);

/**
 * Initialize evaluator with SubD control cage.
 *
 * @param handle Evaluator handle
 * @param vertices Array of vertex coordinates [x,y,z, x,y,z, ...]
 * @param vertex_count Number of vertices
 * @param faces Flattened array of face vertex indices
 * @param face_sizes Array of vertex count for each face
 * @param face_count Number of faces
 * @param crease_edges Array of edge pairs [v1,v2, v1,v2, ...] (may be NULL)
 * @param crease_sharpness Array of sharpness values for each crease (may be NULL)
 * @param crease_count Number of creases
 * @return true on success
 */
LATENT_API bool latent_evaluator_initialize(
    LatentEvaluatorHandle handle,
    const float* vertices,
    int vertex_count,
    const int* faces,
    const int* face_sizes,
    int face_count,
    const int* crease_edges,
    const float* crease_sharpness,
    int crease_count
);

/**
 * Destroy an evaluator and free resources.
 * @param handle Evaluator handle (safe to call with NULL)
 */
LATENT_API void latent_evaluator_destroy(LatentEvaluatorHandle handle);

/**
 * Check if evaluator is initialized.
 * @param handle Evaluator handle
 * @return true if initialized
 */
LATENT_API bool latent_evaluator_is_initialized(LatentEvaluatorHandle handle);

/**
 * Get number of faces in control cage.
 * @param handle Evaluator handle
 * @return Face count
 */
LATENT_API int latent_evaluator_get_face_count(LatentEvaluatorHandle handle);

//=============================================================================
// Forward Evaluation (Parametric → 3D)
//=============================================================================

/**
 * Evaluate a point on the limit surface.
 *
 * @param handle Evaluator handle
 * @param face_id Face index
 * @param u U parameter [0, 1]
 * @param v V parameter [0, 1]
 * @param out_x Output X coordinate
 * @param out_y Output Y coordinate
 * @param out_z Output Z coordinate
 * @return true on success
 */
LATENT_API bool latent_evaluate_point(
    LatentEvaluatorHandle handle,
    int face_id,
    float u, float v,
    float* out_x, float* out_y, float* out_z
);

/**
 * Evaluate a normal on the limit surface.
 *
 * @param handle Evaluator handle
 * @param face_id Face index
 * @param u U parameter [0, 1]
 * @param v V parameter [0, 1]
 * @param out_nx Output normal X component
 * @param out_ny Output normal Y component
 * @param out_nz Output normal Z component
 * @return true on success
 */
LATENT_API bool latent_evaluate_normal(
    LatentEvaluatorHandle handle,
    int face_id,
    float u, float v,
    float* out_nx, float* out_ny, float* out_nz
);

/**
 * Evaluate point and normal together (more efficient than separate calls).
 *
 * @param handle Evaluator handle
 * @param face_id Face index
 * @param u U parameter [0, 1]
 * @param v V parameter [0, 1]
 * @param out_x Output X coordinate
 * @param out_y Output Y coordinate
 * @param out_z Output Z coordinate
 * @param out_nx Output normal X component
 * @param out_ny Output normal Y component
 * @param out_nz Output normal Z component
 * @return true on success
 */
LATENT_API bool latent_evaluate_point_and_normal(
    LatentEvaluatorHandle handle,
    int face_id,
    float u, float v,
    float* out_x, float* out_y, float* out_z,
    float* out_nx, float* out_ny, float* out_nz
);

/**
 * Evaluate point, normal, and derivatives at once.
 *
 * @param handle Evaluator handle
 * @param face_id Face index
 * @param u U parameter [0, 1]
 * @param v V parameter [0, 1]
 * @param out_point Output position (3 floats)
 * @param out_normal Output normal (3 floats)
 * @param out_du Output du derivative (3 floats)
 * @param out_dv Output dv derivative (3 floats)
 * @return true on success
 */
LATENT_API bool latent_evaluate_full(
    LatentEvaluatorHandle handle,
    int face_id, float u, float v,
    float* out_point,
    float* out_normal,
    float* out_du,
    float* out_dv
);

//=============================================================================
// Inverse Evaluation (3D → Parametric)
//=============================================================================

/**
 * Project a 3D point onto the surface and find closest parametric location.
 *
 * @param handle Evaluator handle
 * @param x Point X coordinate
 * @param y Point Y coordinate
 * @param z Point Z coordinate
 * @param out_face_id Output face index
 * @param out_u Output U parameter
 * @param out_v Output V parameter
 * @return true on success
 */
LATENT_API bool latent_project_point(
    LatentEvaluatorHandle handle,
    float x, float y, float z,
    int* out_face_id,
    float* out_u, float* out_v
);

//=============================================================================
// Tessellation (Display Mesh)
//=============================================================================

/**
 * Generate display mesh via uniform subdivision.
 *
 * @param handle Evaluator handle
 * @param subdivision_level Subdivision level (0-5 typical)
 * @param out_vertices Output vertex array (allocated by caller, size: vertex_count * 3)
 * @param out_normals Output normal array (allocated by caller, size: vertex_count * 3)
 * @param out_triangles Output triangle indices (allocated by caller, size: triangle_count * 3)
 * @param out_vertex_count Output: number of vertices generated
 * @param out_triangle_count Output: number of triangles generated
 * @return true on success
 *
 * Note: Call with NULL outputs first to get counts, then allocate and call again.
 */
LATENT_API bool latent_tessellate(
    LatentEvaluatorHandle handle,
    int subdivision_level,
    float* out_vertices,
    float* out_normals,
    int* out_triangles,
    int* out_vertex_count,
    int* out_triangle_count
);

//=============================================================================
// Error Handling
//=============================================================================

/**
 * Get the last error message.
 * @return Error message string (valid until next API call)
 */
LATENT_API const char* latent_get_last_error(void);

#ifdef __cplusplus
}
#endif

#endif // LATENT_CORE_H
