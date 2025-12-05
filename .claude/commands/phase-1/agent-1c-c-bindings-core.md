# Agent 1C: C Bindings - Core Functions

## Objective

Create C-compatible wrapper for core SubD evaluator functions, enabling P/Invoke from C#.

## Working Directory

`/Users/NickDuch/.claude-worktrees/Latent/focused-robinson`

## Read First

- `cpp_core/c_bindings/exports.h` - export macros (created in Phase 0)
- `cpp_core/geometry/subd_evaluator.h` - C++ class interface

## Dependencies

- **Agent 1A**: `project_point_onto_surface()` method must exist
  - If not available yet, create a stub that returns false
  - Mark with TODO comment for Agent 1A to complete

## Files to Create

1. `cpp_core/c_bindings/latent_core.h` - C API header
2. `cpp_core/c_bindings/latent_core.cpp` - C API implementation

## Files to Modify

1. `cpp_core/c_bindings/CMakeLists.txt` - add sources

## Tasks

### 1. Create latent_core.h

```cpp
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
 * Create a new SubD evaluator.
 * @return Handle to the evaluator, or NULL on failure
 */
LATENT_API LatentEvaluatorHandle latent_evaluator_create(void);

/**
 * Destroy a SubD evaluator and free resources.
 * @param handle Evaluator handle (safe to call with NULL)
 */
LATENT_API void latent_evaluator_destroy(LatentEvaluatorHandle handle);

/**
 * Initialize the evaluator with a SubD control cage.
 *
 * @param handle Evaluator handle
 * @param vertices Flat array of vertex positions [x0,y0,z0, x1,y1,z1, ...]
 * @param vertex_count Number of vertices
 * @param faces Flat array of face vertex indices
 * @param face_sizes Array of face sizes (number of vertices per face)
 * @param face_count Number of faces
 * @param crease_edges Flat array of crease edge pairs [v0,v1, v2,v3, ...]
 * @param crease_sharpness Array of sharpness values per crease
 * @param crease_count Number of creased edges
 * @return true on success, false on failure
 */
LATENT_API bool latent_evaluator_initialize(
    LatentEvaluatorHandle handle,
    const float* vertices, int vertex_count,
    const int* faces, const int* face_sizes, int face_count,
    const int* crease_edges, const float* crease_sharpness, int crease_count
);

/**
 * Check if the evaluator has been initialized.
 * @param handle Evaluator handle
 * @return true if initialized, false otherwise
 */
LATENT_API bool latent_evaluator_is_initialized(LatentEvaluatorHandle handle);

/**
 * Get the number of control faces.
 * @param handle Evaluator handle
 * @return Number of faces, or 0 if not initialized
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
    int face_id, float u, float v,
    float* out_x, float* out_y, float* out_z
);

/**
 * Evaluate the surface normal at a point.
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
    int face_id, float u, float v,
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
 * Project a 3D point onto the limit surface.
 *
 * Finds the closest point on the surface to the input point.
 *
 * @param handle Evaluator handle
 * @param px Input X coordinate
 * @param py Input Y coordinate
 * @param pz Input Z coordinate
 * @param out_face_id Output face index
 * @param out_u Output U parameter
 * @param out_v Output V parameter
 * @return true if projection succeeded
 */
LATENT_API bool latent_project_point(
    LatentEvaluatorHandle handle,
    float px, float py, float pz,
    int* out_face_id, float* out_u, float* out_v
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
```

### 2. Create latent_core.cpp

```cpp
// cpp_core/c_bindings/latent_core.cpp
#include "latent_core.h"
#include "../geometry/subd_evaluator.h"
#include <string>
#include <cstring>

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
    }
}

LATENT_API void latent_evaluator_destroy(LatentEvaluatorHandle handle) {
    if (handle) {
        delete static_cast<SubDEvaluator*>(handle);
    }
}

LATENT_API bool latent_evaluator_initialize(
    LatentEvaluatorHandle handle,
    const float* vertices, int vertex_count,
    const int* faces, const int* face_sizes, int face_count,
    const int* crease_edges, const float* crease_sharpness, int crease_count)
{
    if (!handle) {
        set_error("Null handle");
        return false;
    }

    try {
        auto* evaluator = static_cast<SubDEvaluator*>(handle);
        return evaluator->initialize(
            vertices, vertex_count,
            faces, face_sizes, face_count,
            crease_edges, crease_sharpness, crease_count
        );
    } catch (const std::exception& e) {
        set_error(std::string("Initialization failed: ") + e.what());
        return false;
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
    return evaluator->get_control_face_count();
}

//=============================================================================
// Forward Evaluation
//=============================================================================

LATENT_API bool latent_evaluate_point(
    LatentEvaluatorHandle handle,
    int face_id, float u, float v,
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
    }
}

LATENT_API bool latent_evaluate_normal(
    LatentEvaluatorHandle handle,
    int face_id, float u, float v,
    float* out_nx, float* out_ny, float* out_nz)
{
    if (!handle || !out_nx || !out_ny || !out_nz) {
        set_error("Null parameter");
        return false;
    }

    try {
        auto* evaluator = static_cast<SubDEvaluator*>(handle);
        Point3D point;
        Vector3 normal;
        evaluator->evaluate_limit(face_id, u, v, point, normal);
        *out_nx = normal.x;
        *out_ny = normal.y;
        *out_nz = normal.z;
        return true;
    } catch (const std::exception& e) {
        set_error(std::string("Normal evaluation failed: ") + e.what());
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
        Vector3 du, dv;
        evaluator->evaluate_limit_with_derivatives(face_id, u, v, point, du, dv);

        out_point[0] = point.x;
        out_point[1] = point.y;
        out_point[2] = point.z;

        // Normal = du × dv (normalized)
        Vector3 normal = du.cross(dv);
        normal.normalize();
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
    }
}

//=============================================================================
// Inverse Evaluation
//=============================================================================

LATENT_API bool latent_project_point(
    LatentEvaluatorHandle handle,
    float px, float py, float pz,
    int* out_face_id, float* out_u, float* out_v)
{
    if (!handle || !out_face_id || !out_u || !out_v) {
        set_error("Null parameter");
        return false;
    }

    try {
        auto* evaluator = static_cast<SubDEvaluator*>(handle);
        Point3D point(px, py, pz);

        // Note: This depends on Agent 1A's implementation
        // If not yet available, this will fail gracefully
        return evaluator->project_point_onto_surface(
            point, *out_face_id, *out_u, *out_v
        );
    } catch (const std::exception& e) {
        set_error(std::string("Projection failed: ") + e.what());
        return false;
    }
}

//=============================================================================
// Error Handling
//=============================================================================

LATENT_API const char* latent_get_last_error(void) {
    return g_last_error.c_str();
}
```

### 3. Update CMakeLists.txt

```cmake
# cpp_core/c_bindings/CMakeLists.txt

set(C_BINDINGS_SOURCES
    latent_core.cpp
)

# Add c_bindings sources to the shared library
target_sources(latent_core PRIVATE
    ${CMAKE_CURRENT_SOURCE_DIR}/latent_core.cpp
)

# Ensure headers are included
target_include_directories(latent_core PUBLIC
    ${CMAKE_CURRENT_SOURCE_DIR}
)

# Install headers
install(FILES
    exports.h
    latent_core.h
    DESTINATION include/latent
)
```

## Success Criteria

- [ ] All functions compile without errors
- [ ] Handle lifecycle works (create/destroy without leaks)
- [ ] Forward evaluation matches C++ API results exactly
- [ ] Inverse evaluation works (or gracefully fails if Agent 1A incomplete)
- [ ] Error messages are accessible via `latent_get_last_error()`
- [ ] Library exports are visible (check with `nm -gU` on macOS)

## Verification Commands

```bash
cd cpp_core/build
cmake .. && make -j4

# Check exports
nm -gU liblatent_core.dylib | grep latent_

# Should show:
# latent_evaluator_create
# latent_evaluator_destroy
# latent_evaluator_initialize
# latent_evaluate_point
# latent_evaluate_normal
# latent_project_point
# etc.
```

## Do Not Modify

- Files in `geometry/` (Agent 1A/1B's domain)
- Files outside `c_bindings/` directory

## Skills to Use

- `superpowers:test-driven-development` - consider edge cases
- `superpowers:verification-before-completion` - verify exports

## Notes

**Dependency on Agent 1A**: The `latent_project_point()` function calls `project_point_onto_surface()`. If Agent 1A hasn't completed this yet, the function will fail gracefully and return false. The integration tests in Phase 1 consolidation will verify the end-to-end flow.

## Report

When complete, provide:
1. List of exported symbols
2. Verification that create/destroy doesn't leak memory
3. Any compilation warnings encountered
