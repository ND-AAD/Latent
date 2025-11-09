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
