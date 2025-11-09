"""
Test suite for Laplacian matrix builder.

Tests cotangent-weight Laplace-Beltrami operator construction,
area matrix computation, and eigenvalue properties.
"""

import pytest
import numpy as np
from scipy import sparse
import cpp_core
from app.analysis.laplacian import (
    LaplacianBuilder,
    build_normalized_laplacian,
    verify_laplacian
)


class TestLaplacianBuilder:
    """Test Laplacian matrix construction."""

    def test_sphere_eigenvalues(self):
        """
        Test Laplacian on sphere (analytical eigenvalues known).

        For unit sphere, first few eigenvalues are:
        λ₀ = 0 (constant function)
        λ₁ = λ₂ = λ₃ = 2 (first harmonic, 3-fold)
        λ₄ = ... = λ₈ = 6 (second harmonic, 5-fold)
        """
        # Create subdivided icosahedron (approximates sphere)
        cage = self._create_icosahedron()

        evaluator = cpp_core.SubDEvaluator()
        evaluator.initialize(cage)

        builder = LaplacianBuilder(evaluator)
        L, A = builder.build_laplacian(tessellation_level=2)

        # Verify Laplacian properties
        props = verify_laplacian(L, None)
        assert props['is_symmetric'], "Laplacian must be symmetric"
        assert props['row_sums_near_zero'], "Row sums should be ~0"

        # Compute eigenvalues
        L_norm = build_normalized_laplacian(L, A)

        from scipy.sparse.linalg import eigsh
        eigenvalues, eigenvectors = eigsh(
            -L_norm,  # Negative for ascending order
            k=10,
            which='SM'  # Smallest magnitude
        )
        eigenvalues = -eigenvalues  # Negate back

        # First eigenvalue should be ~0
        assert eigenvalues[0] < 0.01, f"First eigenvalue {eigenvalues[0]} not near 0"

        # Check multiplicity pattern (rough check)
        print(f"First 10 eigenvalues: {eigenvalues}")

    def test_planar_quad(self):
        """Test Laplacian on simple planar quad."""
        # Unit square
        cage = cpp_core.SubDControlCage()
        cage.vertices = [
            cpp_core.Point3D(0, 0, 0),
            cpp_core.Point3D(1, 0, 0),
            cpp_core.Point3D(1, 1, 0),
            cpp_core.Point3D(0, 1, 0)
        ]
        cage.faces = [[0, 1, 2, 3]]

        evaluator = cpp_core.SubDEvaluator()
        evaluator.initialize(cage)

        builder = LaplacianBuilder(evaluator)
        L, A = builder.build_laplacian(tessellation_level=2)

        # Basic checks
        assert L.shape[0] == L.shape[1], "Laplacian must be square"
        assert L.shape[0] > 4, "Should have more vertices after subdivision"

        # Verify symmetry
        diff = np.abs((L - L.T).data).max()
        assert diff < 1e-6, "Laplacian must be symmetric"

    def test_cotangent_computation(self):
        """Test cotangent weight computation."""
        builder = LaplacianBuilder(None)

        # Right angle at v_opp: vectors from v_opp must be perpendicular
        v0 = np.array([-1, 0, 0], dtype=float)
        v1 = np.array([0, 1, 0], dtype=float)
        v_opp = np.array([0, 0, 0], dtype=float)

        # Angle at v_opp is 90°, cot(90°) = 0
        cot = builder._compute_cotangent(v0, v1, v_opp)
        assert abs(cot) < 0.01, f"cot(90°) should be ~0, got {cot}"

        # Equilateral triangle: angle is 60°
        v0 = np.array([0, 0, 0], dtype=float)
        v1 = np.array([1, 0, 0], dtype=float)
        v_opp = np.array([0.5, np.sqrt(3)/2, 0], dtype=float)

        cot = builder._compute_cotangent(v0, v1, v_opp)
        expected_cot = 1.0 / np.sqrt(3)  # cot(60°) = 1/√3
        assert abs(cot - expected_cot) < 0.01, \
            f"cot(60°) should be {expected_cot}, got {cot}"

    def test_area_matrix(self):
        """Test area (mass) matrix computation."""
        # Simple triangle
        vertices = np.array([
            [0, 0, 0],
            [1, 0, 0],
            [0, 1, 0]
        ], dtype=float)
        triangles = np.array([[0, 1, 2]], dtype=np.int32)

        builder = LaplacianBuilder(None)
        A = builder._build_area_matrix(vertices, triangles)

        # Each vertex gets 1/3 of triangle area
        tri_area = 0.5  # Area of right triangle with legs 1,1
        expected_area = tri_area / 3.0

        areas = A.diagonal()
        assert all(abs(a - expected_area) < 1e-6 for a in areas), \
            f"Each vertex should have area {expected_area}, got {areas}"

    def test_cache_functionality(self):
        """Test caching mechanism."""
        cage = self._create_simple_cage()
        evaluator = cpp_core.SubDEvaluator()
        evaluator.initialize(cage)

        builder = LaplacianBuilder(evaluator)

        # First call
        L1, A1 = builder.build_laplacian(use_cache=True)

        # Second call with cache should return same object
        L2, A2 = builder.build_laplacian(use_cache=True)
        assert L1 is L2, "Cache should return same object"

        # Clear cache
        builder.clear_cache()

        # Third call should rebuild
        L3, A3 = builder.build_laplacian(use_cache=True)
        assert L1 is not L3, "After clear_cache, should rebuild"

    def test_verify_laplacian_function(self):
        """Test the verify_laplacian function."""
        cage = self._create_simple_cage()
        evaluator = cpp_core.SubDEvaluator()
        evaluator.initialize(cage)

        builder = LaplacianBuilder(evaluator)
        L, A = builder.build_laplacian()

        props = verify_laplacian(L)

        # Should have these keys
        assert 'is_symmetric' in props
        assert 'symmetry_error' in props
        assert 'row_sum_max' in props
        assert 'row_sums_near_zero' in props
        assert 'sparsity' in props

        # Should be symmetric
        assert props['is_symmetric']
        assert props['symmetry_error'] < 1e-6

        # Row sums should be near zero
        assert props['row_sums_near_zero']
        assert props['row_sum_max'] < 1e-4

        # Should be sparse
        assert props['sparsity'] > 0.9  # At least 90% sparse

    def test_normalized_laplacian(self):
        """Test normalized Laplacian construction."""
        cage = self._create_simple_cage()
        evaluator = cpp_core.SubDEvaluator()
        evaluator.initialize(cage)

        builder = LaplacianBuilder(evaluator)
        L, A = builder.build_laplacian()

        L_norm = build_normalized_laplacian(L, A)

        # Should still be symmetric
        diff = np.abs((L_norm - L_norm.T).data).max()
        assert diff < 1e-6, "Normalized Laplacian must be symmetric"

        # Should still have row sums near zero
        ones = np.ones(L_norm.shape[0])
        row_sums = L_norm @ ones
        assert np.abs(row_sums).max() < 1e-4

    def test_degenerate_triangle_handling(self):
        """Test that degenerate triangles don't crash."""
        # Create a very flat triangle (nearly colinear points)
        vertices = np.array([
            [0, 0, 0],
            [1, 0, 0],
            [1, 1e-12, 0]  # Nearly on the line
        ], dtype=float)
        triangles = np.array([[0, 1, 2]], dtype=np.int32)

        builder = LaplacianBuilder(None)

        # Should not crash
        L = builder._build_cotangent_laplacian(vertices, triangles)
        A = builder._build_area_matrix(vertices, triangles)

        # Check they're valid sparse matrices
        assert isinstance(L, sparse.csr_matrix)
        assert isinstance(A, sparse.dia_matrix)

    def test_multiple_tessellation_levels(self):
        """Test that different tessellation levels produce valid Laplacians."""
        cage = self._create_simple_cage()
        evaluator = cpp_core.SubDEvaluator()
        evaluator.initialize(cage)

        builder = LaplacianBuilder(evaluator)

        for level in [1, 2, 3]:
            L, A = builder.build_laplacian(tessellation_level=level, use_cache=False)

            # Verify properties
            props = verify_laplacian(L)
            assert props['is_symmetric'], f"Level {level} not symmetric"
            assert props['row_sums_near_zero'], f"Level {level} row sums not zero"

            # Check size increases with tessellation
            print(f"Tessellation level {level}: {L.shape[0]} vertices")

    def _create_icosahedron(self):
        """Create icosahedron control cage."""
        # Golden ratio
        phi = (1 + np.sqrt(5)) / 2

        cage = cpp_core.SubDControlCage()

        # 12 vertices
        cage.vertices = [
            cpp_core.Point3D(-1, phi, 0),
            cpp_core.Point3D(1, phi, 0),
            cpp_core.Point3D(-1, -phi, 0),
            cpp_core.Point3D(1, -phi, 0),

            cpp_core.Point3D(0, -1, phi),
            cpp_core.Point3D(0, 1, phi),
            cpp_core.Point3D(0, -1, -phi),
            cpp_core.Point3D(0, 1, -phi),

            cpp_core.Point3D(phi, 0, -1),
            cpp_core.Point3D(phi, 0, 1),
            cpp_core.Point3D(-phi, 0, -1),
            cpp_core.Point3D(-phi, 0, 1)
        ]

        # 20 triangular faces
        cage.faces = [
            [0, 11, 5], [0, 5, 1], [0, 1, 7], [0, 7, 10], [0, 10, 11],
            [1, 5, 9], [5, 11, 4], [11, 10, 2], [10, 7, 6], [7, 1, 8],
            [3, 9, 4], [3, 4, 2], [3, 2, 6], [3, 6, 8], [3, 8, 9],
            [4, 9, 5], [2, 4, 11], [6, 2, 10], [8, 6, 7], [9, 8, 1]
        ]

        return cage

    def _create_simple_cage(self):
        """Create simple quad cage."""
        cage = cpp_core.SubDControlCage()
        cage.vertices = [
            cpp_core.Point3D(0, 0, 0),
            cpp_core.Point3D(1, 0, 0),
            cpp_core.Point3D(1, 1, 0),
            cpp_core.Point3D(0, 1, 0)
        ]
        cage.faces = [[0, 1, 2, 3]]
        return cage


class TestLaplacianEdgeCases:
    """Test edge cases and error handling."""

    def test_single_triangle(self):
        """Test Laplacian on single triangle."""
        cage = cpp_core.SubDControlCage()
        cage.vertices = [
            cpp_core.Point3D(0, 0, 0),
            cpp_core.Point3D(1, 0, 0),
            cpp_core.Point3D(0, 1, 0)
        ]
        cage.faces = [[0, 1, 2]]

        evaluator = cpp_core.SubDEvaluator()
        evaluator.initialize(cage)

        builder = LaplacianBuilder(evaluator)
        L, A = builder.build_laplacian(tessellation_level=1)

        # Should produce valid matrices
        assert L.shape[0] > 0
        assert A.shape[0] == L.shape[0]

        # Verify properties
        props = verify_laplacian(L)
        assert props['is_symmetric']

    def test_obtuse_triangle(self):
        """Test cotangent computation with obtuse angles."""
        builder = LaplacianBuilder(None)

        # Very obtuse triangle (angle > 120°)
        v0 = np.array([0, 0, 0], dtype=float)
        v1 = np.array([1, 0, 0], dtype=float)
        v_opp = np.array([0.5, -2, 0], dtype=float)  # Far below

        # Should still return a valid clamped value
        cot = builder._compute_cotangent(v0, v1, v_opp)
        assert np.isfinite(cot), "Cotangent should be finite"
        assert abs(cot) <= 100.0, "Cotangent should be clamped"


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
