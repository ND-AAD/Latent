#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <pybind11/numpy.h>
#include <pybind11/operators.h>
#include "../geometry/types.h"
#include "../geometry/subd_evaluator.h"
#include "../geometry/nurbs_generator.h"
#include "../analysis/curvature_analyzer.h"
#include "../constraints/validator.h"
#include <stdexcept>
#include <sstream>

namespace py = pybind11;
using namespace latent;

// ============================================================
// Exception Handling Wrappers
// ============================================================

// Custom exception translator for better error messages
void translate_cpp_exception(const std::exception& e) {
    PyErr_SetString(PyExc_RuntimeError, e.what());
}

// Safe wrapper for evaluator operations
template<typename Func>
auto safe_evaluator_call(const char* operation, Func&& func) -> decltype(func()) {
    try {
        return func();
    } catch (const std::runtime_error& e) {
        std::stringstream ss;
        ss << "Evaluator error during " << operation << ": " << e.what();
        throw std::runtime_error(ss.str());
    } catch (const std::exception& e) {
        std::stringstream ss;
        ss << "Unexpected error during " << operation << ": " << e.what();
        throw std::runtime_error(ss.str());
    }
}

// Declare OpenCASCADE Handle types as opaque
// These types are not directly usable from Python yet
// Full serialization/conversion will be implemented for Python interop
// For now, methods that return these types will work but the objects
// can only be passed back to C++ methods, not inspected from Python

PYBIND11_MODULE(cpp_core, m) {
    m.doc() = "Latent C++ core geometry module - Exact SubD limit surface evaluation";

    // Register exception translator
    py::register_exception_translator([](std::exception_ptr p) {
        try {
            if (p) std::rethrow_exception(p);
        } catch (const std::runtime_error& e) {
            PyErr_SetString(PyExc_RuntimeError, e.what());
        } catch (const std::invalid_argument& e) {
            PyErr_SetString(PyExc_ValueError, e.what());
        } catch (const std::exception& e) {
            PyErr_SetString(PyExc_RuntimeError, e.what());
        }
    });

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
        
        .def("initialize",
             [](SubDEvaluator& eval, const SubDControlCage& cage) {
                 return safe_evaluator_call("initialize", [&]() {
                     if (cage.vertices.empty()) {
                         throw std::invalid_argument("Cannot initialize with empty control cage");
                     }
                     if (cage.faces.empty()) {
                         throw std::invalid_argument("Cannot initialize with no faces");
                     }
                     return eval.initialize(cage);
                 });
             },
             "Initialize from control cage\n\n"
             "Args:\n"
             "    cage: SubDControlCage with vertices, faces, and creases\n"
             "Raises:\n"
             "    ValueError: If cage is invalid or empty\n"
             "    RuntimeError: If initialization fails\n",
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
        
        .def("evaluate_limit_point",
             [](const SubDEvaluator& eval, int face_idx, float u, float v) {
                 return safe_evaluator_call("evaluate_limit_point", [&]() {
                     if (!eval.is_initialized()) {
                         throw std::runtime_error("Evaluator not initialized - call initialize() first");
                     }
                     if (u < 0.0f || u > 1.0f || v < 0.0f || v > 1.0f) {
                         throw std::invalid_argument("Parametric coordinates must be in range [0, 1]");
                     }
                     return eval.evaluate_limit_point(face_idx, u, v);
                 });
             },
             "Evaluate exact point on limit surface\n\n"
             "Args:\n"
             "    face_index: Control face index\n"
             "    u: Parametric coordinate (0-1)\n"
             "    v: Parametric coordinate (0-1)\n\n"
             "Returns:\n"
             "    Point3D: Point on limit surface\n"
             "Raises:\n"
             "    RuntimeError: If evaluator not initialized\n"
             "    ValueError: If parameters out of range\n",
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

        .def("compute_curvature",
             [](CurvatureAnalyzer& analyzer, const SubDEvaluator& eval,
                int face_idx, float u, float v) {
                 return safe_evaluator_call("compute_curvature", [&]() {
                     if (!eval.is_initialized()) {
                         throw std::runtime_error("Evaluator not initialized");
                     }
                     if (u < 0.0f || u > 1.0f || v < 0.0f || v > 1.0f) {
                         throw std::invalid_argument("Parametric coordinates must be in range [0, 1]");
                     }
                     return analyzer.compute_curvature(eval, face_idx, u, v);
                 });
             },
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
             "    CurvatureResult: All curvature data at the point\n"
             "Raises:\n"
             "    RuntimeError: If evaluator not initialized\n"
             "    ValueError: If parameters out of range\n",
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

    // ============================================================
    // Constraint Validation (Day 6, Agents 41-43)
    // ============================================================

    // UndercutDetector class (Agent 41)
    py::class_<UndercutDetector>(m, "UndercutDetector",
                                 "Detects undercuts in subdivision surfaces using ray-casting")
        .def(py::init<const SubDEvaluator&>(),
             "Construct undercut detector\n\n"
             "Args:\n"
             "    evaluator: SubDEvaluator (must be initialized)",
             py::arg("evaluator"))

        .def("detect_undercuts", &UndercutDetector::detect_undercuts,
             "Detect undercuts along demolding direction\n\n"
             "Uses ray-casting to detect faces that would be occluded when\n"
             "demolding in the specified direction. Any occlusion indicates\n"
             "an undercut that requires additional mold pieces.\n\n"
             "Args:\n"
             "    face_indices: List of face indices to check\n"
             "    demolding_direction: Vector3 direction of demolding\n\n"
             "Returns:\n"
             "    dict: Map from face_id to severity (0.0-1.0)",
             py::arg("face_indices"),
             py::arg("demolding_direction"))

        .def("check_face_undercut", &UndercutDetector::check_face_undercut,
             "Check single face for undercut\n\n"
             "Args:\n"
             "    face_id: Face index to check\n"
             "    demolding_direction: Vector3 direction of demolding\n\n"
             "Returns:\n"
             "    float: Severity (0.0 = no undercut, >0.0 = undercut detected)",
             py::arg("face_id"),
             py::arg("demolding_direction"));

    // DraftChecker class (Agent 42)
    py::class_<DraftChecker>(m, "DraftChecker",
                             "Checks draft angles for mold demolding")
        .def(py::init<const SubDEvaluator&>(),
             "Construct draft checker\n\n"
             "Args:\n"
             "    evaluator: SubDEvaluator (must be initialized)",
             py::arg("evaluator"))

        .def("compute_draft_angles", &DraftChecker::compute_draft_angles,
             "Compute draft angles for all faces\n\n"
             "Args:\n"
             "    face_indices: List of face indices to check\n"
             "    demolding_direction: Vector3 direction of demolding\n\n"
             "Returns:\n"
             "    dict: Map from face_id to draft angle in degrees",
             py::arg("face_indices"),
             py::arg("demolding_direction"))

        .def("check_face_draft", &DraftChecker::check_face_draft,
             "Check single face draft angle\n\n"
             "Args:\n"
             "    face_id: Face index to check\n"
             "    demolding_direction: Vector3 direction of demolding\n\n"
             "Returns:\n"
             "    float: Draft angle in degrees",
             py::arg("face_id"),
             py::arg("demolding_direction"))

        .def_property_readonly_static("MIN_DRAFT_ANGLE",
            [](py::object) { return DraftChecker::MIN_DRAFT_ANGLE; },
            "Minimum acceptable draft angle (0.5°)")

        .def_property_readonly_static("RECOMMENDED_DRAFT_ANGLE",
            [](py::object) { return DraftChecker::RECOMMENDED_DRAFT_ANGLE; },
            "Recommended draft angle (2.0°)");

    // ConstraintLevel enum
    py::enum_<ConstraintLevel>(m, "ConstraintLevel",
                               "Constraint severity levels for mold validation")
        .value("ERROR", ConstraintLevel::ERROR,
               "Physical impossibility - must fix")
        .value("WARNING", ConstraintLevel::WARNING,
               "Manufacturing challenge - negotiable")
        .value("FEATURE", ConstraintLevel::FEATURE,
               "Mathematical tension - aesthetic feature");

    // ConstraintViolation struct
    py::class_<ConstraintViolation>(m, "ConstraintViolation",
                                    "Report of a single constraint violation")
        .def(py::init<>(), "Default constructor")
        .def_readonly("level", &ConstraintViolation::level,
                     "Severity level (ERROR/WARNING/FEATURE)")
        .def_readonly("description", &ConstraintViolation::description,
                     "Human-readable description of the violation")
        .def_readonly("face_id", &ConstraintViolation::face_id,
                     "Which face violates the constraint")
        .def_readonly("severity", &ConstraintViolation::severity,
                     "Magnitude of violation (0.0-1.0)")
        .def_readonly("suggestion", &ConstraintViolation::suggestion,
                     "How to fix the violation")
        .def("__repr__", [](const ConstraintViolation& v) {
            std::string level_str;
            switch(v.level) {
                case ConstraintLevel::ERROR: level_str = "ERROR"; break;
                case ConstraintLevel::WARNING: level_str = "WARNING"; break;
                case ConstraintLevel::FEATURE: level_str = "FEATURE"; break;
            }
            return "ConstraintViolation(" + level_str + ", face=" +
                   std::to_string(v.face_id) + ", severity=" +
                   std::to_string(v.severity) + ")";
        });

    // ConstraintReport class
    py::class_<ConstraintReport>(m, "ConstraintReport",
                                 "Complete constraint report for a region")
        .def(py::init<>(), "Default constructor")
        .def_readwrite("violations", &ConstraintReport::violations,
                      "List of all constraint violations")
        .def("add_error", &ConstraintReport::add_error,
             "Add an ERROR-level violation",
             py::arg("description"), py::arg("face_id"), py::arg("severity"))
        .def("add_warning", &ConstraintReport::add_warning,
             "Add a WARNING-level violation",
             py::arg("description"), py::arg("face_id"), py::arg("severity"))
        .def("add_feature", &ConstraintReport::add_feature,
             "Add a FEATURE-level observation",
             py::arg("description"), py::arg("face_id"))
        .def("has_errors", &ConstraintReport::has_errors,
             "Check if report contains any errors")
        .def("has_warnings", &ConstraintReport::has_warnings,
             "Check if report contains any warnings")
        .def("error_count", &ConstraintReport::error_count,
             "Get number of errors in report")
        .def("warning_count", &ConstraintReport::warning_count,
             "Get number of warnings in report");

    // ConstraintValidator class
    py::class_<ConstraintValidator>(m, "ConstraintValidator",
                                    "Complete constraint validator for mold regions")
        .def(py::init<const SubDEvaluator&>(),
             "Construct validator from SubD evaluator",
             py::arg("evaluator"))
        .def("validate_region",
             [](ConstraintValidator& validator, const std::vector<int>& face_indices,
                const Vector3& demolding_dir, float min_wall_thickness) {
                 return safe_evaluator_call("validate_region", [&]() {
                     if (face_indices.empty()) {
                         throw std::invalid_argument("Cannot validate empty region");
                     }
                     if (min_wall_thickness <= 0.0f) {
                         throw std::invalid_argument("Wall thickness must be positive");
                     }
                     // Validate demolding direction is normalized
                     float len = std::sqrt(demolding_dir.x * demolding_dir.x +
                                          demolding_dir.y * demolding_dir.y +
                                          demolding_dir.z * demolding_dir.z);
                     if (len < 0.01f) {
                         throw std::invalid_argument("Demolding direction must be non-zero");
                     }
                     return validator.validate_region(face_indices, demolding_dir,
                                                     min_wall_thickness);
                 });
             },
             "Validate a region for manufacturability\n\n"
             "Checks for:\n"
             "- Undercuts (ERROR if detected)\n"
             "- Draft angles (ERROR if < 0.5°, WARNING if < 2.0°)\n"
             "- Wall thickness (if implemented)\n\n"
             "Args:\n"
             "    face_indices: List of face indices in the region\n"
             "    demolding_direction: Direction for mold removal (Vector3)\n"
             "    min_wall_thickness: Minimum wall thickness in mm (default 3.0)\n\n"
             "Returns:\n"
             "    ConstraintReport: Complete validation report\n"
             "Raises:\n"
             "    ValueError: If parameters are invalid\n"
             "    RuntimeError: If validation fails\n",
             py::arg("face_indices"),
             py::arg("demolding_direction"),
             py::arg("min_wall_thickness") = 3.0f);

    // ============================================================
    // NURBS Mold Generation (Day 7, Agent 50)
    // ============================================================

    // FittingQuality struct
    py::class_<NURBSMoldGenerator::FittingQuality>(m, "FittingQuality",
                                                   "Quality metrics for NURBS surface fitting")
        .def(py::init<>(), "Default constructor")
        .def_readwrite("max_deviation", &NURBSMoldGenerator::FittingQuality::max_deviation,
                      "Maximum distance from sample to NURBS (mm)")
        .def_readwrite("mean_deviation", &NURBSMoldGenerator::FittingQuality::mean_deviation,
                      "Mean distance from samples to NURBS (mm)")
        .def_readwrite("rms_deviation", &NURBSMoldGenerator::FittingQuality::rms_deviation,
                      "RMS distance from samples to NURBS (mm)")
        .def_readwrite("num_samples", &NURBSMoldGenerator::FittingQuality::num_samples,
                      "Number of sample points used")
        .def("__repr__", [](const NURBSMoldGenerator::FittingQuality& q) {
            return "FittingQuality(max=" + std::to_string(q.max_deviation) +
                   "mm, mean=" + std::to_string(q.mean_deviation) +
                   "mm, rms=" + std::to_string(q.rms_deviation) +
                   "mm, n=" + std::to_string(q.num_samples) + ")";
        });

    // NURBSMoldGenerator class
    py::class_<NURBSMoldGenerator>(m, "NURBSMoldGenerator",
                                   "NURBS mold generator using OpenCASCADE\n\n"
                                   "Implements the lossless-until-fabrication pipeline:\n"
                                   "1. Sample exact limit surface from SubDEvaluator\n"
                                   "2. Fit analytical NURBS through sampled points\n"
                                   "3. Apply draft angle transformation (exact vector math)\n"
                                   "4. Create mold solids with Boolean ops (exact)\n\n"
                                   "NOTE: Currently returns opaque OpenCASCADE types.\n"
                                   "      Full serialization support will be added for Python interop.")
        .def(py::init<const SubDEvaluator&>(),
             "Construct NURBS generator from SubD evaluator\n\n"
             "Args:\n"
             "    evaluator: SubDEvaluator (must be initialized)",
             py::arg("evaluator"))

        .def("fit_nurbs_surface",
             [](NURBSMoldGenerator& gen, const std::vector<int>& face_indices,
                int sample_density) {
                 return safe_evaluator_call("fit_nurbs_surface", [&]() {
                     if (face_indices.empty()) {
                         throw std::invalid_argument("Cannot fit NURBS with no faces");
                     }
                     if (sample_density < 2) {
                         throw std::invalid_argument("Sample density must be at least 2");
                     }
                     if (sample_density > 200) {
                         throw std::invalid_argument("Sample density too high (max 200)");
                     }
                     return gen.fit_nurbs_surface(face_indices, sample_density);
                 });
             },
             "Sample exact limit surface and fit NURBS\n\n"
             "Samples the SubD limit surface at a regular grid using exact\n"
             "evaluation, then fits an analytical B-spline surface through\n"
             "the sampled points using OpenCASCADE approximation algorithms.\n\n"
             "Args:\n"
             "    face_indices: Control face indices to include in surface\n"
             "    sample_density: Samples per face dimension (default 50)\n\n"
             "Returns:\n"
             "    Handle_Geom_BSplineSurface: Fitted B-spline surface (opaque type)\n\n"
             "Raises:\n"
             "    ValueError: If face_indices empty or sample_density invalid\n"
             "    RuntimeError: If NURBS fitting fails\n\n"
             "Note: Return type is currently opaque. Use check_fitting_quality\n"
             "      to verify fit, or serialize to STEP/IGES for Rhino export.",
             py::arg("face_indices"),
             py::arg("sample_density") = 50)

        .def("apply_draft_angle", &NURBSMoldGenerator::apply_draft_angle,
             "Apply draft angle transformation for demolding\n\n"
             "Applies draft angle by transforming surface points away from\n"
             "the demolding direction. Points on the parting line remain fixed.\n"
             "Uses exact vector math to maintain mathematical precision.\n\n"
             "Args:\n"
             "    surface: Input B-spline surface (Handle type)\n"
             "    demolding_direction: Direction of mold removal (Vector3)\n"
             "    draft_angle_degrees: Draft angle in degrees (typically 2-5°)\n"
             "    parting_line: Fixed base curve (list of Point3D)\n\n"
             "Returns:\n"
             "    Handle_Geom_BSplineSurface: Transformed surface with draft (opaque)",
             py::arg("surface"),
             py::arg("demolding_direction"),
             py::arg("draft_angle_degrees"),
             py::arg("parting_line"))

        .def("create_mold_solid", &NURBSMoldGenerator::create_mold_solid,
             "Create solid mold cavity from surface\n\n"
             "Generates a solid mold by offsetting the surface inward/outward\n"
             "to create cavity walls. Uses OpenCASCADE Boolean operations to\n"
             "create a watertight solid suitable for 3D printing.\n\n"
             "Args:\n"
             "    surface: B-spline surface defining cavity inner surface\n"
             "    wall_thickness: Wall thickness in mm (default 40.0)\n\n"
             "Returns:\n"
             "    TopoDS_Shape: Solid mold cavity (opaque type)\n\n"
             "Note: Export to STEP/STL for fabrication using OpenCASCADE I/O.",
             py::arg("surface"),
             py::arg("wall_thickness") = 40.0f)

        .def("add_registration_keys", &NURBSMoldGenerator::add_registration_keys,
             "Add registration features (keys/notches) for mold alignment\n\n"
             "Adds geometric features to ensure proper alignment when assembling\n"
             "multi-part molds. Keys on one part fit into notches on the mating part.\n\n"
             "Args:\n"
             "    mold: Input mold solid (TopoDS_Shape)\n"
             "    key_positions: Positions where registration keys should be added\n\n"
             "Returns:\n"
             "    TopoDS_Shape: Mold with registration features added (opaque)",
             py::arg("mold"),
             py::arg("key_positions"))

        .def("check_fitting_quality", &NURBSMoldGenerator::check_fitting_quality,
             "Check NURBS fitting quality against exact limit surface\n\n"
             "Evaluates the fitted NURBS at sample points and compares to exact\n"
             "limit surface evaluation to ensure fitting accuracy meets tolerances.\n\n"
             "Args:\n"
             "    nurbs: Fitted B-spline surface to check (Handle type)\n"
             "    face_indices: Original face indices used for fitting\n\n"
             "Returns:\n"
             "    FittingQuality: Quality metrics for the fitted surface",
             py::arg("nurbs"),
             py::arg("face_indices"));
}
