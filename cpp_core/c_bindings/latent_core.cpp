// cpp_core/c_bindings/latent_core.cpp
#include "latent_core.h"
#include "../geometry/subd_evaluator.h"
#include "../geometry/types.h"
#include <vector>
#include <cmath>
#include <string>
#include <cstring>

using namespace latent;

// Thread-local error message
static thread_local std::string g_last_error;

static void set_error(const std::string& msg) {
    g_last_error = msg;
}

//=============================================================================
// Evaluator Lifecycle
//=============================================================================

LATENT_API LatentEvaluatorHandle latent_evaluator_create(void) {
    try {
        return static_cast<LatentEvaluatorHandle>(new SubDEvaluator());
    } catch (const std::exception& e) {
        set_error(std::string("Failed to create evaluator: ") + e.what());
        return nullptr;
    } catch (...) {
        set_error("Failed to create evaluator: unknown error");
        return nullptr;
    }
}

LATENT_API bool latent_evaluator_initialize(
    LatentEvaluatorHandle handle,
    const float* vertices,
    int vertex_count,
    const int* faces,
    const int* face_sizes,
    int face_count,
    const int* crease_edges,
    const float* crease_sharpness,
    int crease_count)
{
    if (!handle || !vertices || !faces || !face_sizes) {
        set_error("Null parameter in initialize");
        return false;
    }

    try {
        auto* evaluator = static_cast<SubDEvaluator*>(handle);

        // Build control cage
        SubDControlCage cage;

        // Copy vertices
        cage.vertices.reserve(vertex_count);
        for (int i = 0; i < vertex_count; ++i) {
            cage.vertices.emplace_back(
                vertices[i * 3 + 0],
                vertices[i * 3 + 1],
                vertices[i * 3 + 2]
            );
        }

        // Copy faces
        cage.faces.reserve(face_count);
        int face_offset = 0;
        for (int i = 0; i < face_count; ++i) {
            int size = face_sizes[i];
            std::vector<int> face;
            face.reserve(size);
            for (int j = 0; j < size; ++j) {
                face.push_back(faces[face_offset + j]);
            }
            cage.faces.push_back(face);
            face_offset += size;
        }

        // Copy creases (if provided)
        if (crease_edges && crease_sharpness) {
            cage.creases.reserve(crease_count);
            for (int i = 0; i < crease_count; ++i) {
                // NOTE: Storing edge as pair of vertex indices
                // This may need adjustment based on SubDControlCage implementation
                cage.creases.emplace_back(i, crease_sharpness[i]);
            }
        }

        // Initialize evaluator
        evaluator->initialize(cage);
        return true;

    } catch (const std::exception& e) {
        set_error(std::string("Initialization failed: ") + e.what());
        return false;
    } catch (...) {
        set_error("Initialization failed: unknown error");
        return false;
    }
}

LATENT_API void latent_evaluator_destroy(LatentEvaluatorHandle handle) {
    if (handle) {
        delete static_cast<SubDEvaluator*>(handle);
    }
}

LATENT_API bool latent_evaluator_is_initialized(LatentEvaluatorHandle handle) {
    if (!handle) return false;
    auto* evaluator = static_cast<SubDEvaluator*>(handle);
    return evaluator->is_initialized();
}

LATENT_API int latent_evaluator_get_face_count(LatentEvaluatorHandle handle) {
    if (!handle) return 0;
    auto* evaluator = static_cast<SubDEvaluator*>(handle);
    return static_cast<int>(evaluator->get_control_face_count());
}

//=============================================================================
// Forward Evaluation (Parametric → 3D)
//=============================================================================

LATENT_API bool latent_evaluate_point(
    LatentEvaluatorHandle handle,
    int face_id,
    float u, float v,
    float* out_x, float* out_y, float* out_z)
{
    if (!handle || !out_x || !out_y || !out_z) {
        set_error("Null parameter");
        return false;
    }

    try {
        auto* evaluator = static_cast<SubDEvaluator*>(handle);
        Point3D point = evaluator->evaluate_limit_point(face_id, u, v);

        *out_x = point.x;
        *out_y = point.y;
        *out_z = point.z;
        return true;

    } catch (const std::exception& e) {
        set_error(std::string("Evaluation failed: ") + e.what());
        return false;
    } catch (...) {
        set_error("Evaluation failed: unknown error");
        return false;
    }
}

LATENT_API bool latent_evaluate_normal(
    LatentEvaluatorHandle handle,
    int face_id,
    float u, float v,
    float* out_nx, float* out_ny, float* out_nz)
{
    if (!handle || !out_nx || !out_ny || !out_nz) {
        set_error("Null parameter");
        return false;
    }

    try {
        auto* evaluator = static_cast<SubDEvaluator*>(handle);
        Point3D point, normal;
        evaluator->evaluate_limit(face_id, u, v, point, normal);

        *out_nx = normal.x;
        *out_ny = normal.y;
        *out_nz = normal.z;
        return true;

    } catch (const std::exception& e) {
        set_error(std::string("Normal evaluation failed: ") + e.what());
        return false;
    } catch (...) {
        set_error("Normal evaluation failed: unknown error");
        return false;
    }
}

LATENT_API bool latent_evaluate_point_and_normal(
    LatentEvaluatorHandle handle,
    int face_id,
    float u, float v,
    float* out_x, float* out_y, float* out_z,
    float* out_nx, float* out_ny, float* out_nz)
{
    if (!handle || !out_x || !out_y || !out_z || !out_nx || !out_ny || !out_nz) {
        set_error("Null parameter");
        return false;
    }

    try {
        auto* evaluator = static_cast<SubDEvaluator*>(handle);
        Point3D point, normal;
        evaluator->evaluate_limit(face_id, u, v, point, normal);

        *out_x = point.x;
        *out_y = point.y;
        *out_z = point.z;
        *out_nx = normal.x;
        *out_ny = normal.y;
        *out_nz = normal.z;
        return true;

    } catch (const std::exception& e) {
        set_error(std::string("Point and normal evaluation failed: ") + e.what());
        return false;
    } catch (...) {
        set_error("Point and normal evaluation failed: unknown error");
        return false;
    }
}

LATENT_API bool latent_evaluate_full(
    LatentEvaluatorHandle handle,
    int face_id, float u, float v,
    float* out_point,
    float* out_normal,
    float* out_du,
    float* out_dv)
{
    if (!handle || !out_point || !out_normal || !out_du || !out_dv) {
        set_error("Null parameter");
        return false;
    }

    try {
        auto* evaluator = static_cast<SubDEvaluator*>(handle);
        Point3D point;
        Point3D du, dv;
        evaluator->evaluate_limit_with_derivatives(face_id, u, v, point, du, dv);

        out_point[0] = point.x;
        out_point[1] = point.y;
        out_point[2] = point.z;

        // Normal = du × dv (normalized)
        Vector3 du_vec(du);
        Vector3 dv_vec(dv);
        Vector3 normal = du_vec.cross(dv_vec);
        float len = normal.length();
        if (len > 0.0f) {
            normal.x /= len;
            normal.y /= len;
            normal.z /= len;
        }
        out_normal[0] = normal.x;
        out_normal[1] = normal.y;
        out_normal[2] = normal.z;

        out_du[0] = du.x;
        out_du[1] = du.y;
        out_du[2] = du.z;

        out_dv[0] = dv.x;
        out_dv[1] = dv.y;
        out_dv[2] = dv.z;

        return true;

    } catch (const std::exception& e) {
        set_error(std::string("Full evaluation failed: ") + e.what());
        return false;
    } catch (...) {
        set_error("Full evaluation failed: unknown error");
        return false;
    }
}

//=============================================================================
// Inverse Evaluation (3D → Parametric)
//=============================================================================

LATENT_API bool latent_project_point(
    LatentEvaluatorHandle handle,
    float x, float y, float z,
    int* out_face_id,
    float* out_u, float* out_v)
{
    if (!handle || !out_face_id || !out_u || !out_v) {
        set_error("Null parameter");
        return false;
    }

    try {
        auto* evaluator = static_cast<SubDEvaluator*>(handle);
        Point3D point(x, y, z);

        // Note: This depends on Agent 1A's implementation
        // If not yet available, this will fail gracefully
        return evaluator->project_point_onto_surface(
            point, *out_face_id, *out_u, *out_v
        );

    } catch (const std::exception& e) {
        set_error(std::string("Projection failed: ") + e.what());
        return false;
    } catch (...) {
        set_error("Projection failed: unknown error");
        return false;
    }
}

//=============================================================================
// Tessellation (Display Mesh)
//=============================================================================

LATENT_API bool latent_tessellate(
    LatentEvaluatorHandle handle,
    int subdivision_level,
    float* out_vertices,
    float* out_normals,
    int* out_triangles,
    int* out_vertex_count,
    int* out_triangle_count)
{
    if (!handle || !out_vertex_count || !out_triangle_count) {
        set_error("Null parameter");
        return false;
    }

    try {
        auto* evaluator = static_cast<SubDEvaluator*>(handle);

        // Generate tessellation
        TessellationResult result = evaluator->tessellate(subdivision_level, false);

        *out_vertex_count = static_cast<int>(result.vertex_count());
        *out_triangle_count = static_cast<int>(result.triangle_count());

        // If output arrays are NULL, caller is just querying sizes
        if (!out_vertices || !out_normals || !out_triangles) {
            return true;
        }

        // Copy vertices
        for (size_t i = 0; i < result.vertices.size(); ++i) {
            out_vertices[i] = result.vertices[i];
        }

        // Copy normals
        for (size_t i = 0; i < result.normals.size(); ++i) {
            out_normals[i] = result.normals[i];
        }

        // Copy triangles
        for (size_t i = 0; i < result.triangles.size(); ++i) {
            out_triangles[i] = result.triangles[i];
        }

        return true;

    } catch (const std::exception& e) {
        set_error(std::string("Tessellation failed: ") + e.what());
        return false;
    } catch (...) {
        set_error("Tessellation failed: unknown error");
        return false;
    }
}


//=============================================================================
// Error Handling
//=============================================================================

LATENT_API const char* latent_get_last_error(void) {
    return g_last_error.c_str();
}
