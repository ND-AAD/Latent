#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <pybind11/numpy.h>
#include "../geometry/types.h"
#include "../geometry/subd_evaluator.h"

namespace py = pybind11;
using namespace latent;

PYBIND11_MODULE(cpp_core, m) {
    m.doc() = "Latent C++ core geometry module - Exact SubD limit surface evaluation";

    // ============================================================
    // Point3D Binding
    // ============================================================
    py::class_<Point3D>(m, "Point3D", "3D point with float precision")
        .def(py::init<>(), "Default constructor (0, 0, 0)")
        .def(py::init<float, float, float>(), "Construct from coordinates",
             py::arg("x"), py::arg("y"), py::arg("z"))
        .def_readwrite("x", &Point3D::x, "X coordinate")
        .def_readwrite("y", &Point3D::y, "Y coordinate")
        .def_readwrite("z", &Point3D::z, "Z coordinate")
        .def("__repr__", [](const Point3D& p) {
            return "Point3D(" + std::to_string(p.x) + ", " +
                   std::to_string(p.y) + ", " +
                   std::to_string(p.z) + ")";
        });

    // ============================================================
    // SubDControlCage Binding
    // ============================================================
    py::class_<SubDControlCage>(m, "SubDControlCage",
                                "SubD control cage with vertices, faces, and creases")
        .def(py::init<>(), "Default constructor")
        .def_readwrite("vertices", &SubDControlCage::vertices,
                      "List of control vertices (Point3D)")
        .def_readwrite("faces", &SubDControlCage::faces,
                      "List of faces (each face is list of vertex indices)")
        .def_readwrite("creases", &SubDControlCage::creases,
                      "List of edge creases (edge_id, sharpness)")
        .def("vertex_count", &SubDControlCage::vertex_count,
             "Get number of vertices")
        .def("face_count", &SubDControlCage::face_count,
             "Get number of faces")
        .def("__repr__", [](const SubDControlCage& cage) {
            return "SubDControlCage(" +
                   std::to_string(cage.vertex_count()) + " vertices, " +
                   std::to_string(cage.face_count()) + " faces)";
        });

    // ============================================================
    // TessellationResult Binding with Numpy Arrays
    // ============================================================
    py::class_<TessellationResult>(m, "TessellationResult",
                                   "Result of subdivision surface tessellation")
        .def(py::init<>(), "Default constructor")
        
        // Vertices property with zero-copy numpy integration
        .def_property("vertices",
            [](TessellationResult& r) {
                // Return as numpy array (zero-copy view)
                return py::array_t<float>(
                    {r.vertex_count(), 3},  // shape (N, 3)
                    {3 * sizeof(float), sizeof(float)},  // strides
                    r.vertices.data(),
                    py::cast(r)  // parent keeps data alive
                );
            },
            [](TessellationResult& r, py::array_t<float> arr) {
                // Set from numpy array
                auto buf = arr.request();
                if (buf.ndim != 2 || buf.shape[1] != 3) {
                    throw std::runtime_error("Expected (N, 3) array");
                }
                r.vertices.assign((float*)buf.ptr,
                                 (float*)buf.ptr + buf.size);
            },
            "Vertex positions as numpy array (N, 3)")
        
        // Normals property with zero-copy numpy integration
        .def_property("normals",
            [](TessellationResult& r) {
                return py::array_t<float>(
                    {r.vertex_count(), 3},
                    {3 * sizeof(float), sizeof(float)},
                    r.normals.data(),
                    py::cast(r)
                );
            },
            [](TessellationResult& r, py::array_t<float> arr) {
                auto buf = arr.request();
                if (buf.ndim != 2 || buf.shape[1] != 3) {
                    throw std::runtime_error("Expected (N, 3) array");
                }
                r.normals.assign((float*)buf.ptr,
                                (float*)buf.ptr + buf.size);
            },
            "Vertex normals as numpy array (N, 3)")
        
        // Triangles property with zero-copy numpy integration
        .def_property("triangles",
            [](TessellationResult& r) {
                return py::array_t<int>(
                    {r.triangle_count(), 3},
                    {3 * sizeof(int), sizeof(int)},
                    r.triangles.data(),
                    py::cast(r)
                );
            },
            [](TessellationResult& r, py::array_t<int> arr) {
                auto buf = arr.request();
                if (buf.ndim != 2 || buf.shape[1] != 3) {
                    throw std::runtime_error("Expected (N, 3) array");
                }
                r.triangles.assign((int*)buf.ptr,
                                  (int*)buf.ptr + buf.size);
            },
            "Triangle indices as numpy array (M, 3)")
        
        .def_readwrite("face_parents", &TessellationResult::face_parents,
                      "Parent face index for each triangle")
        .def("vertex_count", &TessellationResult::vertex_count,
             "Get number of vertices")
        .def("triangle_count", &TessellationResult::triangle_count,
             "Get number of triangles");

    // ============================================================
    // SubDEvaluator Binding
    // ============================================================
    py::class_<SubDEvaluator>(m, "SubDEvaluator",
                              "Evaluates exact limit surface of SubD control cage")
        .def(py::init<>(), "Default constructor")
        
        .def("initialize", &SubDEvaluator::initialize,
             "Initialize from control cage\n\n"
             "Args:\n"
             "    cage: SubDControlCage with vertices, faces, and creases\n",
             py::arg("cage"))
        
        .def("is_initialized", &SubDEvaluator::is_initialized,
             "Check if evaluator has been initialized\n\n"
             "Returns:\n"
             "    bool: True if initialized with a control cage")
        
        .def("tessellate", &SubDEvaluator::tessellate,
             "Tessellate subdivided surface into triangles for display\n\n"
             "Args:\n"
             "    subdivision_level: Number of subdivision iterations (0-6, default 3)\n"
             "    adaptive: Use adaptive subdivision (default False)\n\n"
             "Returns:\n"
             "    TessellationResult: Triangulated mesh with vertices, normals, and topology",
             py::arg("subdivision_level") = 3,
             py::arg("adaptive") = false)
        
        .def("evaluate_limit_point", &SubDEvaluator::evaluate_limit_point,
             "Evaluate exact point on limit surface\n\n"
             "Args:\n"
             "    face_index: Control face index\n"
             "    u: Parametric coordinate (0-1)\n"
             "    v: Parametric coordinate (0-1)\n\n"
             "Returns:\n"
             "    Point3D: Point on limit surface",
             py::arg("face_index"),
             py::arg("u"),
             py::arg("v"))
        
        .def("evaluate_limit",
             [](const SubDEvaluator& eval, int face_idx, float u, float v) {
                 Point3D point, normal;
                 eval.evaluate_limit(face_idx, u, v, point, normal);
                 return py::make_tuple(point, normal);
             },
             "Evaluate point and normal on limit surface\n\n"
             "Args:\n"
             "    face_index: Control face index\n"
             "    u: Parametric coordinate (0-1)\n"
             "    v: Parametric coordinate (0-1)\n\n"
             "Returns:\n"
             "    tuple: (Point3D, Point3D) - point and unit normal at that point",
             py::arg("face_index"),
             py::arg("u"),
             py::arg("v"))
        
        .def("get_parent_face", &SubDEvaluator::get_parent_face,
             "Get parent control face for a tessellated triangle\n\n"
             "Args:\n"
             "    triangle_index: Index into tessellation result triangles\n\n"
             "Returns:\n"
             "    int: Index of parent control face, or -1 if invalid",
             py::arg("triangle_index"))
        
        .def("get_control_vertex_count",
             &SubDEvaluator::get_control_vertex_count,
             "Get number of vertices in control cage\n\n"
             "Returns:\n"
             "    int: Vertex count")
        
        .def("get_control_face_count",
             &SubDEvaluator::get_control_face_count,
             "Get number of faces in control cage\n\n"
             "Returns:\n"
             "    int: Face count");
}
