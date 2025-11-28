# Agent 5: pybind11 Python Bindings

**Day**: 1
**Phase**: Phase 0 - C++ Core Foundation
**Duration**: 3-4 hours
**Estimated Cost**: $4-6 (50K tokens, Sonnet)

---

## Mission

Create pybind11 bindings to expose C++ SubD evaluation classes to Python with zero-copy numpy array sharing.

---

## Context

You are creating the Python interface to the C++ core geometry module. This enables:
- Python code to call C++ SubDEvaluator methods
- Zero-copy data sharing via numpy arrays (no serialization overhead)
- Seamless integration between PyQt6 UI and C++ geometry engine
- Pythonic API while maintaining C++ performance

**Critical**: Use pybind11's numpy integration for efficient array passing.

**Dependencies**:
- Agent 1's `types.h` (Point3D, SubDControlCage, TessellationResult)
- Agent 2's `subd_evaluator.h`
- Agent 4's `subd_evaluator.cpp`
- pybind11 (installed via pip/brew)

---

## Deliverables

**File to Create**: `cpp_core/python_bindings/bindings.cpp`

---

## Requirements

### 1. Module Definition
```cpp
#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <pybind11/numpy.h>
#include "../geometry/types.h"
#include "../geometry/subd_evaluator.h"

namespace py = pybind11;
using namespace latent;

PYBIND11_MODULE(cpp_core, m) {
    m.doc() = "Latent C++ core geometry module";

    // Bind classes here
}
```

### 2. Point3D Binding
```cpp
py::class_<Point3D>(m, "Point3D")
    .def(py::init<>())
    .def(py::init<float, float, float>())
    .def_readwrite("x", &Point3D::x)
    .def_readwrite("y", &Point3D::y)
    .def_readwrite("z", &Point3D::z)
    .def("__repr__", [](const Point3D& p) {
        return "Point3D(" + std::to_string(p.x) + ", " +
               std::to_string(p.y) + ", " +
               std::to_string(p.z) + ")";
    });
```

### 3. SubDControlCage Binding
```cpp
py::class_<SubDControlCage>(m, "SubDControlCage")
    .def(py::init<>())
    .def_readwrite("vertices", &SubDControlCage::vertices)
    .def_readwrite("faces", &SubDControlCage::faces)
    .def_readwrite("creases", &SubDControlCage::creases)
    .def("vertex_count", &SubDControlCage::vertex_count)
    .def("face_count", &SubDControlCage::face_count)
    .def("__repr__", [](const SubDControlCage& cage) {
        return "SubDControlCage(" +
               std::to_string(cage.vertex_count()) + " vertices, " +
               std::to_string(cage.face_count()) + " faces)";
    });
```

### 4. TessellationResult Binding with Numpy Arrays
```cpp
py::class_<TessellationResult>(m, "TessellationResult")
    .def(py::init<>())
    .def_property("vertices",
        [](TessellationResult& r) {
            // Return as numpy array (zero-copy view)
            return py::array_t<float>(
                {r.vertex_count(), 3},  // shape
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
        })
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
            r.normals.assign((float*)buf.ptr,
                            (float*)buf.ptr + buf.size);
        })
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
            r.triangles.assign((int*)buf.ptr,
                              (int*)buf.ptr + buf.size);
        })
    .def_readwrite("face_parents", &TessellationResult::face_parents)
    .def("vertex_count", &TessellationResult::vertex_count)
    .def("triangle_count", &TessellationResult::triangle_count);
```

### 5. SubDEvaluator Binding
```cpp
py::class_<SubDEvaluator>(m, "SubDEvaluator")
    .def(py::init<>())
    .def("initialize", &SubDEvaluator::initialize,
         "Initialize from control cage",
         py::arg("cage"))
    .def("is_initialized", &SubDEvaluator::is_initialized)
    .def("tessellate", &SubDEvaluator::tessellate,
         "Tessellate refined surface for display",
         py::arg("subdivision_level") = 3,
         py::arg("adaptive") = false)
    .def("evaluate_limit_point", &SubDEvaluator::evaluate_limit_point,
         "Evaluate exact point on limit surface",
         py::arg("face_index"),
         py::arg("u"),
         py::arg("v"))
    .def("evaluate_limit",
         [](const SubDEvaluator& eval, int face_idx, float u, float v) {
             Point3D point, normal;
             eval.evaluate_limit(face_idx, u, v, point, normal);
             return py::make_tuple(point, normal);
         },
         "Evaluate point and normal on limit surface",
         py::arg("face_index"),
         py::arg("u"),
         py::arg("v"))
    .def("get_parent_face", &SubDEvaluator::get_parent_face,
         "Get parent control face for tessellated triangle",
         py::arg("triangle_index"))
    .def("get_control_vertex_count",
         &SubDEvaluator::get_control_vertex_count)
    .def("get_control_face_count",
         &SubDEvaluator::get_control_face_count);
```

---

## Python API Design

The bindings should enable this Python usage:

```python
import cpp_core
import numpy as np

# Create control cage
cage = cpp_core.SubDControlCage()

# Add vertices
cage.vertices = [
    cpp_core.Point3D(0, 0, 0),
    cpp_core.Point3D(1, 0, 0),
    cpp_core.Point3D(1, 1, 0),
    cpp_core.Point3D(0, 1, 0)
]

# Add faces
cage.faces = [[0, 1, 2, 3]]  # Quad face

# Create evaluator
evaluator = cpp_core.SubDEvaluator()
evaluator.initialize(cage)

# Tessellate for display
result = evaluator.tessellate(subdivision_level=3)

# Access as numpy arrays (zero-copy!)
vertices = result.vertices  # numpy array (N, 3)
normals = result.normals    # numpy array (N, 3)
triangles = result.triangles  # numpy array (M, 3)

print(f"Generated {vertices.shape[0]} vertices")
print(f"Generated {triangles.shape[0]} triangles")

# Evaluate exact limit point
point = evaluator.evaluate_limit_point(face_index=0, u=0.5, v=0.5)
print(f"Limit point: ({point.x}, {point.y}, {point.z})")

# Evaluate with normal
point, normal = evaluator.evaluate_limit(0, 0.5, 0.5)
```

---

## Testing

**Test File**: `cpp_core/python_bindings/test_bindings.py`

```python
#!/usr/bin/env python3
"""Test pybind11 bindings for cpp_core module."""

import sys
import numpy as np

# Import the C++ module
try:
    import cpp_core
except ImportError as e:
    print(f"❌ Failed to import cpp_core: {e}")
    print("Make sure the module is built and in PYTHONPATH")
    sys.exit(1)

def test_point3d():
    """Test Point3D binding."""
    print("Test: Point3D...")

    # Default constructor
    p1 = cpp_core.Point3D()
    assert p1.x == 0.0 and p1.y == 0.0 and p1.z == 0.0

    # Parameterized constructor
    p2 = cpp_core.Point3D(1.0, 2.0, 3.0)
    assert p2.x == 1.0
    assert p2.y == 2.0
    assert p2.z == 3.0

    # Modify attributes
    p2.x = 5.0
    assert p2.x == 5.0

    # String representation
    repr_str = repr(p2)
    assert "Point3D" in repr_str
    assert "5.0" in repr_str

    print("  ✅ Point3D binding working")

def test_control_cage():
    """Test SubDControlCage binding."""
    print("\nTest: SubDControlCage...")

    cage = cpp_core.SubDControlCage()

    # Add vertices
    cage.vertices = [
        cpp_core.Point3D(0, 0, 0),
        cpp_core.Point3D(1, 0, 0),
        cpp_core.Point3D(1, 1, 0),
        cpp_core.Point3D(0, 1, 0)
    ]

    assert cage.vertex_count() == 4

    # Add faces
    cage.faces = [[0, 1, 2, 3]]
    assert cage.face_count() == 1

    # String representation
    repr_str = repr(cage)
    assert "4 vertices" in repr_str
    assert "1 faces" in repr_str

    print("  ✅ SubDControlCage binding working")

def test_subd_evaluator():
    """Test SubDEvaluator binding."""
    print("\nTest: SubDEvaluator...")

    # Create simple quad
    cage = cpp_core.SubDControlCage()
    cage.vertices = [
        cpp_core.Point3D(0, 0, 0),
        cpp_core.Point3D(1, 0, 0),
        cpp_core.Point3D(1, 1, 0),
        cpp_core.Point3D(0, 1, 0)
    ]
    cage.faces = [[0, 1, 2, 3]]

    # Create evaluator
    eval = cpp_core.SubDEvaluator()
    assert not eval.is_initialized()

    # Initialize
    eval.initialize(cage)
    assert eval.is_initialized()
    assert eval.get_control_vertex_count() == 4
    assert eval.get_control_face_count() == 1

    print("  ✅ Initialization working")

    # Tessellate
    result = eval.tessellate(subdivision_level=2)
    assert result.vertex_count() > 4
    assert result.triangle_count() > 0

    print(f"  ✅ Tessellation: {result.vertex_count()} verts, "
          f"{result.triangle_count()} tris")

    # Evaluate limit point
    point = eval.evaluate_limit_point(0, 0.5, 0.5)
    assert hasattr(point, 'x') and hasattr(point, 'y') and hasattr(point, 'z')
    print(f"  ✅ Limit point: ({point.x:.3f}, {point.y:.3f}, {point.z:.3f})")

    # Evaluate with normal
    point, normal = eval.evaluate_limit(0, 0.5, 0.5)

    # Check normal is unit length
    length = np.sqrt(normal.x**2 + normal.y**2 + normal.z**2)
    assert abs(length - 1.0) < 0.01, f"Normal not unit: {length}"

    print(f"  ✅ Normal: ({normal.x:.3f}, {normal.y:.3f}, {normal.z:.3f})")

def test_numpy_integration():
    """Test zero-copy numpy array integration."""
    print("\nTest: Numpy integration...")

    # Create and tessellate
    cage = cpp_core.SubDControlCage()
    cage.vertices = [
        cpp_core.Point3D(0, 0, 0),
        cpp_core.Point3D(1, 0, 0),
        cpp_core.Point3D(1, 1, 0),
        cpp_core.Point3D(0, 1, 0)
    ]
    cage.faces = [[0, 1, 2, 3]]

    eval = cpp_core.SubDEvaluator()
    eval.initialize(cage)
    result = eval.tessellate(3)

    # Get as numpy arrays
    vertices = result.vertices
    normals = result.normals
    triangles = result.triangles

    # Check types
    assert isinstance(vertices, np.ndarray)
    assert isinstance(normals, np.ndarray)
    assert isinstance(triangles, np.ndarray)

    # Check shapes
    assert vertices.ndim == 2 and vertices.shape[1] == 3
    assert normals.ndim == 2 and normals.shape[1] == 3
    assert triangles.ndim == 2 and triangles.shape[1] == 3

    # Check dtypes
    assert vertices.dtype == np.float32
    assert normals.dtype == np.float32
    assert triangles.dtype == np.int32

    print(f"  ✅ Vertices shape: {vertices.shape}, dtype: {vertices.dtype}")
    print(f"  ✅ Normals shape: {normals.shape}, dtype: {normals.dtype}")
    print(f"  ✅ Triangles shape: {triangles.shape}, dtype: {triangles.dtype}")

    # Test numpy operations work
    min_coord = vertices.min(axis=0)
    max_coord = vertices.max(axis=0)
    print(f"  ✅ Bounding box: {min_coord} to {max_coord}")

    # Check all normals are unit length
    lengths = np.linalg.norm(normals, axis=1)
    assert np.allclose(lengths, 1.0, atol=0.01)
    print(f"  ✅ All normals are unit vectors")

def test_cube_example():
    """Test with a cube - more complex geometry."""
    print("\nTest: Cube subdivision...")

    cage = cpp_core.SubDControlCage()

    # 8 vertices of unit cube
    cage.vertices = [
        cpp_core.Point3D(0, 0, 0),
        cpp_core.Point3D(1, 0, 0),
        cpp_core.Point3D(1, 1, 0),
        cpp_core.Point3D(0, 1, 0),
        cpp_core.Point3D(0, 0, 1),
        cpp_core.Point3D(1, 0, 1),
        cpp_core.Point3D(1, 1, 1),
        cpp_core.Point3D(0, 1, 1)
    ]

    # 6 quad faces
    cage.faces = [
        [0, 1, 2, 3],  # bottom
        [4, 5, 6, 7],  # top
        [0, 1, 5, 4],  # front
        [2, 3, 7, 6],  # back
        [0, 3, 7, 4],  # left
        [1, 2, 6, 5]   # right
    ]

    eval = cpp_core.SubDEvaluator()
    eval.initialize(cage)

    # Test different subdivision levels
    for level in [1, 2, 3]:
        result = eval.tessellate(level)
        print(f"  Level {level}: {result.vertex_count()} vertices, "
              f"{result.triangle_count()} triangles")

        # Verify parent mapping
        for tri_idx in range(min(10, result.triangle_count())):
            parent = eval.get_parent_face(tri_idx)
            assert 0 <= parent < 6, f"Invalid parent face: {parent}"

    print("  ✅ Cube subdivision working")

def main():
    """Run all tests."""
    print("=" * 60)
    print("Testing cpp_core Python bindings")
    print("=" * 60)

    try:
        test_point3d()
        test_control_cage()
        test_subd_evaluator()
        test_numpy_integration()
        test_cube_example()

        print("\n" + "=" * 60)
        print("✅ ALL TESTS PASSED!")
        print("=" * 60)
        return 0

    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return 1
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())
```

**Run Tests**:
```bash
cd cpp_core
python3 python_bindings/test_bindings.py
```

---

## CMake Integration

Add to `cpp_core/CMakeLists.txt` (Agent 3 will create base file):

```cmake
# Python bindings
find_package(Python3 COMPONENTS Interpreter Development REQUIRED)
find_package(pybind11 REQUIRED)

pybind11_add_module(cpp_core
    python_bindings/bindings.cpp
    geometry/subd_evaluator.cpp
)

target_link_libraries(cpp_core PRIVATE
    ${OPENSUBDIV_LIBRARIES}
)

target_include_directories(cpp_core PRIVATE
    ${CMAKE_CURRENT_SOURCE_DIR}
    ${OPENSUBDIV_INCLUDE_DIR}
)

# Install Python module
install(TARGETS cpp_core
    LIBRARY DESTINATION ${Python3_SITELIB}
)
```

---

## Success Criteria

- [ ] Bindings compile without errors
- [ ] Python can import `cpp_core` module
- [ ] All C++ classes accessible from Python
- [ ] Numpy arrays work with zero-copy
- [ ] All test cases pass
- [ ] No memory leaks (pybind11 handles ref counting)
- [ ] Pythonic API (snake_case methods, __repr__, etc.)

---

## Performance Notes

**Zero-Copy Numpy Integration**:
- No data copying between C++ and Python
- Numpy arrays are views into C++ std::vector data
- Lifetime management handled by pybind11
- Can pass arrays of millions of points efficiently

**Expected Overhead**:
- C++ → Python call: ~100ns per call (negligible)
- Array creation: Zero-copy, just creates view
- Total overhead: <1% for typical workloads

---

## Integration Notes

**Used by**:
- Agent 6 (Grasshopper server) will use for SubD transfer
- Agent 8 (Desktop bridge) will use for Python integration
- All Python-based analysis engines will use these bindings

**Depends on**:
- Agent 1 (types.h)
- Agent 2 (subd_evaluator.h)
- Agent 4 (subd_evaluator.cpp)

**File Placement**:
```
cpp_core/
├── python_bindings/
│   ├── bindings.cpp           (You create this) ← HERE
│   └── test_bindings.py       (You create this) ← HERE
└── build/
    └── cpp_core.so         (Generated by CMake)
```

---

## Common Issues and Solutions

**Issue**: "ImportError: cpp_core not found"
- **Fix**: Add build directory to PYTHONPATH: `export PYTHONPATH=cpp_core/build:$PYTHONPATH`

**Issue**: "Numpy array dtype mismatch"
- **Fix**: Ensure std::vector uses float (not double) for vertices
- **Fix**: Use explicit dtype in py::array_t<float>

**Issue**: "Segfault when accessing numpy array"
- **Fix**: Ensure parent object keeps data alive with `py::cast(r)`
- **Fix**: Don't return dangling pointers

**Issue**: "pybind11 not found"
- **Fix**: Install via pip: `pip install pybind11`
- **Fix**: Or via brew: `brew install pybind11`

---

## Output Format

Provide:
1. Complete `bindings.cpp` implementation
2. Complete `test_bindings.py` test suite
3. Test output showing all tests passing
4. Brief explanation of numpy integration strategy
5. Integration notes for Python layer

---

**Ready to begin!**
