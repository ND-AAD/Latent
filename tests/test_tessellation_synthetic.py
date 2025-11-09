#!/usr/bin/env python3
"""Test tessellation with synthetic geometry (no Grasshopper server required)."""

import sys
sys.path.insert(0, 'cpp_core/build')

import cpp_core
import numpy as np


def create_simple_cube():
    """Create a simple cube control cage."""
    cage = cpp_core.SubDControlCage()

    # Cube vertices
    vertices_data = [
        # Bottom face
        (-1, -1, -1), (1, -1, -1), (1, 1, -1), (-1, 1, -1),
        # Top face
        (-1, -1, 1), (1, -1, 1), (1, 1, 1), (-1, 1, 1)
    ]

    # Convert to Point3D list
    cage.vertices = [cpp_core.Point3D(v[0], v[1], v[2]) for v in vertices_data]

    # Cube faces (quads)
    cage.faces = [
        [0, 1, 2, 3],  # bottom
        [4, 5, 6, 7],  # top
        [0, 1, 5, 4],  # front
        [2, 3, 7, 6],  # back
        [0, 3, 7, 4],  # left
        [1, 2, 6, 5],  # right
    ]

    return cage


def main():
    print("Testing tessellation with synthetic geometry...")

    # Create simple cube
    cage = create_simple_cube()

    print(f"\nControl cage: {cage.vertex_count()} vertices, "
          f"{cage.face_count()} faces\n")

    # Test subdivision levels
    evaluator = cpp_core.SubDEvaluator()
    evaluator.initialize(cage)

    print("Testing subdivision levels:")

    # Note: OpenSubdiv evaluator can only tessellate once
    # Test each level with a fresh evaluator
    for level in range(1, 5):
        eval_test = cpp_core.SubDEvaluator()
        eval_test.initialize(cage)
        result = eval_test.tessellate(level)
        print(f"  Level {level}: {result.vertex_count():6d} vertices, "
              f"{result.triangle_count():6d} triangles")

        # Verify data integrity
        assert result.vertices.shape[0] == result.vertex_count()
        assert result.triangles.shape[0] == result.triangle_count()
        assert len(result.face_parents) == result.triangle_count()

        # Verify vertices are numpy arrays with correct shape
        assert result.vertices.shape[1] == 3
        assert result.normals.shape[1] == 3
        assert result.triangles.shape[1] == 3

    print("\n✅ All tessellation tests passed")

    # Test limit evaluation
    print("\nTesting limit evaluation:")
    pt = evaluator.evaluate_limit_point(0, 0.5, 0.5)
    print(f"  Limit point at face 0, (0.5, 0.5): ({pt.x:.3f}, {pt.y:.3f}, {pt.z:.3f})")

    # Test multiple limit points
    for u, v in [(0.25, 0.25), (0.75, 0.75), (0.0, 0.0), (1.0, 1.0)]:
        pt = evaluator.evaluate_limit_point(0, u, v)
        print(f"  Limit point at ({u:.2f}, {v:.2f}): ({pt.x:.3f}, {pt.y:.3f}, {pt.z:.3f})")

    print("\n✅ All tests passed successfully")
    return 0


if __name__ == '__main__':
    sys.exit(main())
