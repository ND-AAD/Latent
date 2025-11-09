#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <pybind11/numpy.h>
#include "../geometry/types.h"
#include "../geometry/subd_evaluator.h"
#include "../analysis/curvature_analyzer.h"

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
                std::vector<ssize_t> shape = {static_cast<ssize_t>(r.vertex_count()), 3};
                std::vector<ssize_t> strides = {3 * sizeof(float), sizeof(float)};
                return py::array_t<float>(
                    shape,
                    strides,
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
                std::vector<ssize_t> shape = {static_cast<ssize_t>(r.vertex_count()), 3};
                std::vector<ssize_t> strides = {3 * sizeof(float), sizeof(float)};
                return py::array_t<float>(
                    shape,
                    strides,
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
                std::vector<ssize_t> shape = {static_cast<ssize_t>(r.triangle_count()), 3};
                std::vector<ssize_t> strides = {3 * sizeof(int), sizeof(int)};
                return py::array_t<int>(
                    shape,
                    strides,
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
             "    int: Face count")

        // ============================================================
        // Advanced Limit Surface Evaluation (Day 2, Agent 10)
        // ============================================================

        .def("evaluate_limit_with_derivatives",
             [](const SubDEvaluator& eval, int face_idx, float u, float v) {
                 Point3D position, du, dv;
                 eval.evaluate_limit_with_derivatives(face_idx, u, v,
                                                     position, du, dv);
                 return py::make_tuple(position, du, dv);
             },
             "Evaluate limit position and first derivatives\n\n"
             "Args:\n"
             "    face_index: Control face index\n"
             "    u: Parametric coordinate (0-1)\n"
             "    v: Parametric coordinate (0-1)\n\n"
             "Returns:\n"
             "    tuple: (position, du, dv) - Point3D for position and derivatives",
             py::arg("face_index"), py::arg("u"), py::arg("v"))

        .def("evaluate_limit_with_second_derivatives",
             [](const SubDEvaluator& eval, int face_idx, float u, float v) {
                 Point3D pos, du, dv, duu, dvv, duv;
                 eval.evaluate_limit_with_second_derivatives(
                     face_idx, u, v, pos, du, dv, duu, dvv, duv
                 );
                 return py::make_tuple(pos, du, dv, duu, dvv, duv);
             },
             "Evaluate limit position with first and second derivatives\n\n"
             "Args:\n"
             "    face_index: Control face index\n"
             "    u: Parametric coordinate (0-1)\n"
             "    v: Parametric coordinate (0-1)\n\n"
             "Returns:\n"
             "    tuple: (pos, du, dv, duu, dvv, duv) - Point3D for all derivatives",
             py::arg("face_index"), py::arg("u"), py::arg("v"))

        .def("batch_evaluate_limit",
             &SubDEvaluator::batch_evaluate_limit,
             "Batch evaluate multiple points on limit surface\n\n"
             "More efficient than individual calls.\n\n"
             "Args:\n"
             "    face_indices: List of face indices\n"
             "    params_u: List of u parameters\n"
             "    params_v: List of v parameters\n\n"
             "Returns:\n"
             "    TessellationResult: Evaluated points with normals",
             py::arg("face_indices"),
             py::arg("params_u"),
             py::arg("params_v"))

        .def("compute_tangent_frame",
             [](const SubDEvaluator& eval, int face_idx, float u, float v) {
                 Point3D tangent_u, tangent_v, normal;
                 eval.compute_tangent_frame(face_idx, u, v,
                                           tangent_u, tangent_v, normal);
                 return py::make_tuple(tangent_u, tangent_v, normal);
             },
             "Compute tangent frame (tangent_u, tangent_v, normal)\n\n"
             "Args:\n"
             "    face_index: Control face index\n"
             "    u: Parametric coordinate (0-1)\n"
             "    v: Parametric coordinate (0-1)\n\n"
             "Returns:\n"
             "    tuple: (tangent_u, tangent_v, normal) - normalized Point3D vectors",
             py::arg("face_index"), py::arg("u"), py::arg("v"));

    // ============================================================
    // CurvatureResult Binding (Day 4, Agent 28)
    // ============================================================
    py::class_<CurvatureResult>(m, "CurvatureResult",
                                "Result of curvature analysis at a point")
        .def(py::init<>(), "Default constructor")

        // Principal curvatures
        .def_readwrite("kappa1", &CurvatureResult::kappa1,
                      "Maximum principal curvature")
        .def_readwrite("kappa2", &CurvatureResult::kappa2,
                      "Minimum principal curvature")

        // Principal directions
        .def_readwrite("dir1", &CurvatureResult::dir1,
                      "Direction of maximum curvature")
        .def_readwrite("dir2", &CurvatureResult::dir2,
                      "Direction of minimum curvature")

        // Derived curvatures
        .def_readwrite("gaussian_curvature", &CurvatureResult::gaussian_curvature,
                      "Gaussian curvature (K = kappa1 * kappa2)")
        .def_readwrite("mean_curvature", &CurvatureResult::mean_curvature,
                      "Mean curvature (H = (kappa1 + kappa2) / 2)")
        .def_readwrite("abs_mean_curvature", &CurvatureResult::abs_mean_curvature,
                      "Absolute mean curvature |H|")
        .def_readwrite("rms_curvature", &CurvatureResult::rms_curvature,
                      "RMS curvature sqrt((kappa1^2 + kappa2^2) / 2)")

        // Fundamental forms
        .def_readwrite("E", &CurvatureResult::E, "First fundamental form E")
        .def_readwrite("F", &CurvatureResult::F, "First fundamental form F")
        .def_readwrite("G", &CurvatureResult::G, "First fundamental form G")
        .def_readwrite("L", &CurvatureResult::L, "Second fundamental form L")
        .def_readwrite("M", &CurvatureResult::M, "Second fundamental form M")
        .def_readwrite("N", &CurvatureResult::N, "Second fundamental form N")

        // Surface normal
        .def_readwrite("normal", &CurvatureResult::normal, "Surface unit normal")

        .def("__repr__", [](const CurvatureResult& r) {
            return "CurvatureResult(K=" + std::to_string(r.gaussian_curvature) +
                   ", H=" + std::to_string(r.mean_curvature) +
                   ", k1=" + std::to_string(r.kappa1) +
                   ", k2=" + std::to_string(r.kappa2) + ")";
        });

    // ============================================================
    // CurvatureAnalyzer Binding (Day 4, Agent 28)
    // ============================================================
    py::class_<CurvatureAnalyzer>(m, "CurvatureAnalyzer",
                                  "Analyzes curvature properties of subdivision surfaces")
        .def(py::init<>(), "Default constructor")

        .def("compute_curvature", &CurvatureAnalyzer::compute_curvature,
             "Compute all curvature quantities at a point\n\n"
             "Uses exact limit surface evaluation with second derivatives to compute:\n"
             "- First and second fundamental forms\n"
             "- Shape operator and eigendecomposition\n"
             "- Principal curvatures and directions\n"
             "- Gaussian and mean curvatures\n\n"
             "Args:\n"
             "    evaluator: SubDEvaluator (must be initialized)\n"
             "    face_index: Control face index\n"
             "    u: Parametric coordinate (0-1)\n"
             "    v: Parametric coordinate (0-1)\n\n"
             "Returns:\n"
             "    CurvatureResult: All curvature data at the point",
             py::arg("evaluator"),
             py::arg("face_index"),
             py::arg("u"),
             py::arg("v"))

        .def("batch_compute_curvature", &CurvatureAnalyzer::batch_compute_curvature,
             "Batch compute curvature at multiple points\n\n"
             "More efficient than individual calls for large numbers of points.\n\n"
             "Args:\n"
             "    evaluator: SubDEvaluator (must be initialized)\n"
             "    face_indices: List of face indices\n"
             "    params_u: List of u parameters\n"
             "    params_v: List of v parameters\n\n"
             "Returns:\n"
             "    List[CurvatureResult]: Curvature data for each point",
             py::arg("evaluator"),
             py::arg("face_indices"),
             py::arg("params_u"),
             py::arg("params_v"));
}
