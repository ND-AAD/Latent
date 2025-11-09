#include "subd_evaluator.h"
#include <opensubdiv/far/topologyRefinerFactory.h>
#include <opensubdiv/far/patchTable.h>
#include <opensubdiv/far/patchTableFactory.h>
#include <opensubdiv/far/patchMap.h>
#include <opensubdiv/far/stencilTable.h>
#include <opensubdiv/far/stencilTableFactory.h>
#include <stdexcept>
#include <cmath>
#include <algorithm>

namespace latent {

// Helper struct for OpenSubdiv primvar interpolation
// OpenSubdiv requires types with Clear() and AddWithWeight() methods
struct Vertex {
    float x, y, z;

    Vertex() : x(0), y(0), z(0) {}
    Vertex(float _x, float _y, float _z) : x(_x), y(_y), z(_z) {}

    void Clear() {
        x = y = z = 0.0f;
    }

    void AddWithWeight(const Vertex& src, float weight) {
        x += weight * src.x;
        y += weight * src.y;
        z += weight * src.z;
    }
};

// Forward declaration
static void add_face_normal(const std::vector<float>& vertices,
                            std::vector<float>& normals,
                            int v0, int v1, int v2);

// Store control cage vertices for interpolation
// Note: This is stored outside the class since the header can't be modified
static std::vector<Point3D> g_control_vertices;

SubDEvaluator::SubDEvaluator() : initialized_(false) {}

SubDEvaluator::~SubDEvaluator() {
    // unique_ptr handles cleanup automatically
}

void SubDEvaluator::initialize(const SubDControlCage& cage) {
    using namespace OpenSubdiv;

    if (cage.vertex_count() == 0 || cage.face_count() == 0) {
        throw std::runtime_error("SubDEvaluator: Control cage is empty");
    }

    // Store control vertices for later interpolation
    g_control_vertices = cage.vertices;

    // Store control positions as flat array for patch evaluation
    control_positions_.clear();
    control_positions_.reserve(cage.vertex_count() * 3);
    for (const auto& v : cage.vertices) {
        control_positions_.push_back(v.x);
        control_positions_.push_back(v.y);
        control_positions_.push_back(v.z);
    }

    // Build TopologyDescriptor from cage
    Far::TopologyDescriptor desc;
    desc.numVertices = cage.vertex_count();
    desc.numFaces = cage.face_count();

    // Set face vertex counts and indices
    std::vector<int> num_verts_per_face;
    std::vector<int> face_vert_indices;

    for (const auto& face : cage.faces) {
        if (face.empty()) {
            throw std::runtime_error("SubDEvaluator: Face has no vertices");
        }
        num_verts_per_face.push_back(face.size());
        face_vert_indices.insert(face_vert_indices.end(),
                                  face.begin(), face.end());
    }

    desc.numVertsPerFace = num_verts_per_face.data();
    desc.vertIndicesPerFace = face_vert_indices.data();

    // Handle creases if present
    std::vector<int> crease_vert_pairs;
    std::vector<float> crease_weights;
    if (!cage.creases.empty()) {
        // Note: crease.first is edge ID, which needs conversion to vertex pairs
        // This requires edge enumeration which OpenSubdiv can provide
        // For now, we skip crease handling - it will be added when needed
    }

    // Create refiner
    Far::TopologyRefinerFactory<Far::TopologyDescriptor>::Options options;
    options.schemeType = OpenSubdiv::Sdc::SCHEME_CATMARK;
    options.validateFullTopology = true;

    refiner_.reset(
        Far::TopologyRefinerFactory<Far::TopologyDescriptor>::Create(
            desc, options));

    if (!refiner_) {
        throw std::runtime_error("SubDEvaluator: Failed to create TopologyRefiner");
    }

    initialized_ = true;
}

TessellationResult SubDEvaluator::tessellate(int subdivision_level,
                                             bool adaptive) {
    if (!initialized_) {
        throw std::runtime_error("SubDEvaluator not initialized");
    }

    using namespace OpenSubdiv;

    if (subdivision_level < 0 || subdivision_level > 10) {
        throw std::runtime_error("SubDEvaluator: Invalid subdivision level (must be 0-10)");
    }

    // Refine topology uniformly (only if not already refined to this level)
    int current_max_level = refiner_->GetMaxLevel();
    if (current_max_level < subdivision_level) {
        Far::TopologyRefiner::UniformOptions refine_options(subdivision_level);
        refiner_->RefineUniform(refine_options);
    }

    // Get refined level
    Far::TopologyLevel const& refined_level =
        refiner_->GetLevel(subdivision_level);

    int num_base_verts = refiner_->GetLevel(0).GetNumVertices();
    int num_refined_verts = refined_level.GetNumVertices();
    int num_refined_faces = refined_level.GetNumFaces();

    // Prepare source vertex positions from control cage
    std::vector<Vertex> src_verts(num_base_verts);
    for (int i = 0; i < num_base_verts && i < static_cast<int>(g_control_vertices.size()); ++i) {
        src_verts[i].x = g_control_vertices[i].x;
        src_verts[i].y = g_control_vertices[i].y;
        src_verts[i].z = g_control_vertices[i].z;
    }

    // Interpolate positions using PrimvarRefiner
    Far::PrimvarRefiner primvar_refiner(*refiner_);

    // Always interpolate from level 0 to requested level
    std::vector<Vertex> current_verts = src_verts;
    std::vector<Vertex> next_verts;

    for (int level = 1; level <= subdivision_level; ++level) {
        int num_level_verts = refiner_->GetLevel(level).GetNumVertices();
        next_verts.resize(num_level_verts);

        // Interpolate using OpenSubdiv
        // The API expects first element pointers, store in variables for proper lvalue reference
        if (!current_verts.empty() && !next_verts.empty()) {
            Vertex* src_ptr = &current_verts[0];
            Vertex* dst_ptr = &next_verts[0];
            primvar_refiner.Interpolate(level, src_ptr, dst_ptr);
        }

        current_verts = next_verts;
    }

    // Final refined vertices
    std::vector<Vertex>& refined_verts = current_verts;

    // Build tessellation result
    TessellationResult result;
    triangle_to_face_map_.clear();

    // Copy refined vertices from Vertex struct to flat float array
    result.vertices.resize(num_refined_verts * 3);
    for (int i = 0; i < num_refined_verts; ++i) {
        result.vertices[i * 3 + 0] = refined_verts[i].x;
        result.vertices[i * 3 + 1] = refined_verts[i].y;
        result.vertices[i * 3 + 2] = refined_verts[i].z;
    }

    // Compute normals using face normals and averaging
    // First compute per-face normals
    result.normals.resize(num_refined_verts * 3, 0.0f);

    // Triangulate quads and build triangle list
    for (int face_idx = 0; face_idx < num_refined_faces; ++face_idx) {
        Far::ConstIndexArray face_verts = refined_level.GetFaceVertices(face_idx);
        int num_face_verts = face_verts.size();

        if (num_face_verts == 3) {
            // Already a triangle
            int v0 = face_verts[0], v1 = face_verts[1], v2 = face_verts[2];
            result.triangles.push_back(v0);
            result.triangles.push_back(v1);
            result.triangles.push_back(v2);
            triangle_to_face_map_.push_back(face_idx);

            // Compute face normal and accumulate to vertices
            add_face_normal(result.vertices, result.normals, v0, v1, v2);
        } else if (num_face_verts == 4) {
            // Quad - split into 2 triangles
            int v0 = face_verts[0], v1 = face_verts[1];
            int v2 = face_verts[2], v3 = face_verts[3];

            // Triangle 1: v0, v1, v2
            result.triangles.push_back(v0);
            result.triangles.push_back(v1);
            result.triangles.push_back(v2);
            triangle_to_face_map_.push_back(face_idx);
            add_face_normal(result.vertices, result.normals, v0, v1, v2);

            // Triangle 2: v0, v2, v3
            result.triangles.push_back(v0);
            result.triangles.push_back(v2);
            result.triangles.push_back(v3);
            triangle_to_face_map_.push_back(face_idx);
            add_face_normal(result.vertices, result.normals, v0, v2, v3);
        } else {
            // N-gon - fan triangulation from first vertex
            for (int i = 1; i < num_face_verts - 1; ++i) {
                int v0 = face_verts[0];
                int v1 = face_verts[i];
                int v2 = face_verts[i + 1];

                result.triangles.push_back(v0);
                result.triangles.push_back(v1);
                result.triangles.push_back(v2);
                triangle_to_face_map_.push_back(face_idx);
                add_face_normal(result.vertices, result.normals, v0, v1, v2);
            }
        }
    }

    // Normalize all normals
    for (int i = 0; i < num_refined_verts; ++i) {
        float nx = result.normals[i * 3 + 0];
        float ny = result.normals[i * 3 + 1];
        float nz = result.normals[i * 3 + 2];
        float length = std::sqrt(nx * nx + ny * ny + nz * nz);

        if (length > 1e-6f) {
            result.normals[i * 3 + 0] /= length;
            result.normals[i * 3 + 1] /= length;
            result.normals[i * 3 + 2] /= length;
        } else {
            // Default normal if zero length
            result.normals[i * 3 + 0] = 0.0f;
            result.normals[i * 3 + 1] = 0.0f;
            result.normals[i * 3 + 2] = 1.0f;
        }
    }

    // Map refined faces to control cage faces
    // For now, use refined face index as parent (will be fixed with proper mapping)
    result.face_parents = triangle_to_face_map_;

    return result;
}

// Helper function to compute and accumulate face normal
void add_face_normal(const std::vector<float>& vertices,
                     std::vector<float>& normals,
                     int v0, int v1, int v2) {
    // Get vertex positions
    float p0x = vertices[v0 * 3 + 0], p0y = vertices[v0 * 3 + 1], p0z = vertices[v0 * 3 + 2];
    float p1x = vertices[v1 * 3 + 0], p1y = vertices[v1 * 3 + 1], p1z = vertices[v1 * 3 + 2];
    float p2x = vertices[v2 * 3 + 0], p2y = vertices[v2 * 3 + 1], p2z = vertices[v2 * 3 + 2];

    // Compute edges
    float e1x = p1x - p0x, e1y = p1y - p0y, e1z = p1z - p0z;
    float e2x = p2x - p0x, e2y = p2y - p0y, e2z = p2z - p0z;

    // Compute cross product (face normal)
    float nx = e1y * e2z - e1z * e2y;
    float ny = e1z * e2x - e1x * e2z;
    float nz = e1x * e2y - e1y * e2x;

    // Accumulate to all three vertices
    normals[v0 * 3 + 0] += nx; normals[v0 * 3 + 1] += ny; normals[v0 * 3 + 2] += nz;
    normals[v1 * 3 + 0] += nx; normals[v1 * 3 + 1] += ny; normals[v1 * 3 + 2] += nz;
    normals[v2 * 3 + 0] += nx; normals[v2 * 3 + 1] += ny; normals[v2 * 3 + 2] += nz;
}

Point3D SubDEvaluator::evaluate_limit_point(int face_index,
                                            float u, float v) const {
    if (!initialized_) {
        throw std::runtime_error("SubDEvaluator not initialized");
    }

    using namespace OpenSubdiv;

    // Validate parameters
    if (u < 0.0f || u > 1.0f || v < 0.0f || v > 1.0f) {
        throw std::runtime_error(
            "SubDEvaluator: Invalid parametric coordinates (u,v must be in [0,1])");
    }

    Far::TopologyLevel const& base_level = refiner_->GetLevel(0);
    if (face_index < 0 || face_index >= base_level.GetNumFaces()) {
        throw std::runtime_error(
            "SubDEvaluator: Invalid face index");
    }

    // For a full implementation, we would use PatchTable for exact Stam evaluation
    // This requires:
    // 1. Building PatchTable with PatchTableFactory
    // 2. Using PatchMap to find the patch for (face_index, u, v)
    // 3. Evaluating using PatchTable::EvaluateBasis with control vertices
    //
    // For now, we provide a bilinear approximation using the face corners
    // This gives reasonable results for moderate subdivision levels

    Far::ConstIndexArray face_verts = base_level.GetFaceVertices(face_index);
    int num_face_verts = face_verts.size();

    Point3D result(0.0f, 0.0f, 0.0f);

    if (num_face_verts == 4) {
        // Quad face - bilinear interpolation
        // Corners: v0=(0,0), v1=(1,0), v2=(1,1), v3=(0,1)
        int v0 = face_verts[0], v1 = face_verts[1];
        int v2 = face_verts[2], v3 = face_verts[3];

        // Bilinear weights
        float w0 = (1.0f - u) * (1.0f - v);
        float w1 = u * (1.0f - v);
        float w2 = u * v;
        float w3 = (1.0f - u) * v;

        if (v0 < static_cast<int>(g_control_vertices.size()) &&
            v1 < static_cast<int>(g_control_vertices.size()) &&
            v2 < static_cast<int>(g_control_vertices.size()) &&
            v3 < static_cast<int>(g_control_vertices.size())) {

            result.x = w0 * g_control_vertices[v0].x + w1 * g_control_vertices[v1].x +
                       w2 * g_control_vertices[v2].x + w3 * g_control_vertices[v3].x;
            result.y = w0 * g_control_vertices[v0].y + w1 * g_control_vertices[v1].y +
                       w2 * g_control_vertices[v2].y + w3 * g_control_vertices[v3].y;
            result.z = w0 * g_control_vertices[v0].z + w1 * g_control_vertices[v1].z +
                       w2 * g_control_vertices[v2].z + w3 * g_control_vertices[v3].z;
        }
    } else if (num_face_verts == 3) {
        // Triangle face - barycentric interpolation
        int v0 = face_verts[0], v1 = face_verts[1], v2 = face_verts[2];

        float w0 = 1.0f - u - v;
        float w1 = u;
        float w2 = v;

        if (v0 < static_cast<int>(g_control_vertices.size()) &&
            v1 < static_cast<int>(g_control_vertices.size()) &&
            v2 < static_cast<int>(g_control_vertices.size())) {

            result.x = w0 * g_control_vertices[v0].x + w1 * g_control_vertices[v1].x +
                       w2 * g_control_vertices[v2].x;
            result.y = w0 * g_control_vertices[v0].y + w1 * g_control_vertices[v1].y +
                       w2 * g_control_vertices[v2].y;
            result.z = w0 * g_control_vertices[v0].z + w1 * g_control_vertices[v1].z +
                       w2 * g_control_vertices[v2].z;
        }
    } else {
        // N-gon - simple center approximation
        for (int i = 0; i < num_face_verts; ++i) {
            int v = face_verts[i];
            if (v < static_cast<int>(g_control_vertices.size())) {
                result.x += g_control_vertices[v].x;
                result.y += g_control_vertices[v].y;
                result.z += g_control_vertices[v].z;
            }
        }
        if (num_face_verts > 0) {
            result.x /= num_face_verts;
            result.y /= num_face_verts;
            result.z /= num_face_verts;
        }
    }

    return result;
}

void SubDEvaluator::evaluate_limit(int face_index, float u, float v,
                                   Point3D& point, Point3D& normal) const {
    if (!initialized_) {
        throw std::runtime_error("SubDEvaluator not initialized");
    }

    using namespace OpenSubdiv;

    // Validate parameters
    if (u < 0.0f || u > 1.0f || v < 0.0f || v > 1.0f) {
        throw std::runtime_error(
            "SubDEvaluator: Invalid parametric coordinates");
    }

    Far::TopologyLevel const& base_level = refiner_->GetLevel(0);
    if (face_index < 0 || face_index >= base_level.GetNumFaces()) {
        throw std::runtime_error(
            "SubDEvaluator: Invalid face index");
    }

    // Evaluate point
    point = evaluate_limit_point(face_index, u, v);

    // Compute normal using finite differences
    // Full implementation would use analytical derivatives from PatchTable
    float delta = 0.001f;

    // Compute partial derivatives
    Point3D pu1, pu2, pv1, pv2;

    // du derivative
    if (u + delta <= 1.0f) {
        pu2 = evaluate_limit_point(face_index, u + delta, v);
        pu1 = point;
    } else {
        pu1 = evaluate_limit_point(face_index, u - delta, v);
        pu2 = point;
    }

    // dv derivative
    if (v + delta <= 1.0f) {
        pv2 = evaluate_limit_point(face_index, u, v + delta);
        pv1 = point;
    } else {
        pv1 = evaluate_limit_point(face_index, u, v - delta);
        pv2 = point;
    }

    // Compute tangent vectors
    float dux = pu2.x - pu1.x;
    float duy = pu2.y - pu1.y;
    float duz = pu2.z - pu1.z;

    float dvx = pv2.x - pv1.x;
    float dvy = pv2.y - pv1.y;
    float dvz = pv2.z - pv1.z;

    // Normal = cross(du, dv)
    normal.x = duy * dvz - duz * dvy;
    normal.y = duz * dvx - dux * dvz;
    normal.z = dux * dvy - duy * dvx;

    // Normalize
    float length = std::sqrt(normal.x * normal.x +
                             normal.y * normal.y +
                             normal.z * normal.z);

    if (length > 1e-6f) {
        normal.x /= length;
        normal.y /= length;
        normal.z /= length;
    } else {
        // Default normal if degenerate
        normal.x = 0.0f;
        normal.y = 0.0f;
        normal.z = 1.0f;
    }
}

int SubDEvaluator::get_parent_face(int triangle_index) const {
    if (triangle_index < 0 ||
        triangle_index >= static_cast<int>(triangle_to_face_map_.size())) {
        return -1;
    }
    return triangle_to_face_map_[triangle_index];
}

size_t SubDEvaluator::get_control_vertex_count() const {
    if (!initialized_) return 0;
    return refiner_->GetLevel(0).GetNumVertices();
}

size_t SubDEvaluator::get_control_face_count() const {
    if (!initialized_) return 0;
    return refiner_->GetLevel(0).GetNumFaces();
}

// ============================================================
// Advanced Limit Surface Evaluation (Day 2, Agent 10)
// ============================================================

void SubDEvaluator::ensure_patch_table() const {
    if (patch_table_) return;  // Already built

    using namespace OpenSubdiv;

    // Ensure the refiner has been refined at least once
    int current_max_level = refiner_->GetMaxLevel();
    if (current_max_level < 2) {
        // Need to refine for patch table generation
        Far::TopologyRefiner::UniformOptions options(2);
        refiner_->RefineUniform(options);
    }

    // Create patch table for limit evaluation
    Far::PatchTableFactory::Options options;
    options.endCapType = Far::PatchTableFactory::Options::ENDCAP_GREGORY_BASIS;
    options.useInfSharpPatch = true;
    options.generateFVarTables = false;

    // Build patch table from refiner
    patch_table_.reset(
        Far::PatchTableFactory::Create(*refiner_, options)
    );

    if (!patch_table_) {
        throw std::runtime_error("Failed to create PatchTable");
    }
}

void SubDEvaluator::evaluate_limit_with_derivatives(
    int face_index, float u, float v,
    Point3D& position,
    Point3D& du,
    Point3D& dv) const {

    if (!initialized_) {
        throw std::runtime_error("SubDEvaluator not initialized");
    }

    // Validate parameters
    if (u < 0.0f || u > 1.0f || v < 0.0f || v > 1.0f) {
        throw std::runtime_error("Invalid parametric coordinates (u,v must be in [0,1])");
    }

    using namespace OpenSubdiv;

    Far::TopologyLevel const& base_level = refiner_->GetLevel(0);
    if (face_index < 0 || face_index >= base_level.GetNumFaces()) {
        throw std::runtime_error("Invalid face index");
    }

    ensure_patch_table();

    // Create patch map
    Far::PatchMap patch_map(*patch_table_);

    // Find patch handle for (face, u, v)
    Far::PatchTable::PatchHandle const* handle =
        patch_map.FindPatch(face_index, u, v);

    if (!handle) {
        throw std::runtime_error("Invalid face or parameters - could not find patch");
    }

    // Allocate output buffers
    float p[3], du_out[3], dv_out[3];

    // Evaluate position and derivatives
    patch_table_->Evaluate(*handle, u, v,
                           control_positions_.data(),
                           p, du_out, dv_out);

    // Convert to Point3D
    position = Point3D(p[0], p[1], p[2]);
    du = Point3D(du_out[0], du_out[1], du_out[2]);
    dv = Point3D(dv_out[0], dv_out[1], dv_out[2]);
}

void SubDEvaluator::evaluate_limit_with_second_derivatives(
    int face_index, float u, float v,
    Point3D& position,
    Point3D& du, Point3D& dv,
    Point3D& duu, Point3D& dvv, Point3D& duv) const {

    if (!initialized_) {
        throw std::runtime_error("SubDEvaluator not initialized");
    }

    // Validate parameters
    if (u < 0.0f || u > 1.0f || v < 0.0f || v > 1.0f) {
        throw std::runtime_error("Invalid parametric coordinates");
    }

    using namespace OpenSubdiv;

    Far::TopologyLevel const& base_level = refiner_->GetLevel(0);
    if (face_index < 0 || face_index >= base_level.GetNumFaces()) {
        throw std::runtime_error("Invalid face index");
    }

    ensure_patch_table();

    // Get patch handle
    Far::PatchMap patch_map(*patch_table_);
    Far::PatchTable::PatchHandle const* handle =
        patch_map.FindPatch(face_index, u, v);

    if (!handle) {
        throw std::runtime_error("Invalid face or parameters - could not find patch");
    }

    // Output buffers
    float p[3];
    float d1[6];  // [du_x, du_y, du_z, dv_x, dv_y, dv_z]
    float d2[9];  // [duu_x, duu_y, duu_z, dvv_x, dvv_y, dvv_z, duv_x, duv_y, duv_z]

    // Evaluate with second derivatives
    patch_table_->EvaluateBasis(*handle, u, v,
                                control_positions_.data(),
                                p, d1, d2);

    // Convert outputs
    position = Point3D(p[0], p[1], p[2]);
    du = Point3D(d1[0], d1[1], d1[2]);
    dv = Point3D(d1[3], d1[4], d1[5]);
    duu = Point3D(d2[0], d2[1], d2[2]);
    dvv = Point3D(d2[3], d2[4], d2[5]);
    duv = Point3D(d2[6], d2[7], d2[8]);
}

TessellationResult SubDEvaluator::batch_evaluate_limit(
    const std::vector<int>& face_indices,
    const std::vector<float>& params_u,
    const std::vector<float>& params_v) const {

    if (!initialized_) {
        throw std::runtime_error("SubDEvaluator not initialized");
    }

    size_t num_points = face_indices.size();
    if (params_u.size() != num_points || params_v.size() != num_points) {
        throw std::runtime_error("Parameter array size mismatch");
    }

    TessellationResult result;
    result.vertices.reserve(num_points * 3);
    result.normals.reserve(num_points * 3);
    result.face_parents.reserve(num_points);

    // Evaluate each point
    for (size_t i = 0; i < num_points; ++i) {
        Point3D pos, du, dv;
        evaluate_limit_with_derivatives(
            face_indices[i], params_u[i], params_v[i],
            pos, du, dv
        );

        // Add position
        result.vertices.push_back(pos.x);
        result.vertices.push_back(pos.y);
        result.vertices.push_back(pos.z);

        // Compute normal as cross(du, dv)
        Point3D normal;
        normal.x = du.y * dv.z - du.z * dv.y;
        normal.y = du.z * dv.x - du.x * dv.z;
        normal.z = du.x * dv.y - du.y * dv.x;

        // Normalize
        float length = std::sqrt(
            normal.x * normal.x +
            normal.y * normal.y +
            normal.z * normal.z
        );

        if (length > 1e-8f) {
            normal.x /= length;
            normal.y /= length;
            normal.z /= length;
        } else {
            // Degenerate case - use default normal
            normal.x = 0.0f;
            normal.y = 0.0f;
            normal.z = 1.0f;
        }

        result.normals.push_back(normal.x);
        result.normals.push_back(normal.y);
        result.normals.push_back(normal.z);

        // Store parent face
        result.face_parents.push_back(face_indices[i]);
    }

    return result;
}

void SubDEvaluator::compute_tangent_frame(
    int face_index, float u, float v,
    Point3D& tangent_u,
    Point3D& tangent_v,
    Point3D& normal) const {

    Point3D position;
    evaluate_limit_with_derivatives(face_index, u, v,
                                    position, tangent_u, tangent_v);

    // Normalize tangents
    auto normalize = [](Point3D& v) {
        float len = std::sqrt(v.x*v.x + v.y*v.y + v.z*v.z);
        if (len > 1e-8f) {
            v.x /= len; v.y /= len; v.z /= len;
        }
    };

    normalize(tangent_u);
    normalize(tangent_v);

    // Normal = cross(tangent_u, tangent_v)
    normal.x = tangent_u.y * tangent_v.z - tangent_u.z * tangent_v.y;
    normal.y = tangent_u.z * tangent_v.x - tangent_u.x * tangent_v.z;
    normal.z = tangent_u.x * tangent_v.y - tangent_u.y * tangent_v.x;

    normalize(normal);
}

}  // namespace latent
