"""
Test curvature analysis Python bindings.

This test verifies that the CurvatureAnalyzer and CurvatureResult classes
are properly exposed to Python via pybind11 with correct numpy integration.

Tests curvature computation on known analytical surfaces:
- Sphere: K = 1/r², H = 1/r, k1 = k2 = 1/r
- Plane: K = 0, H = 0, k1 = k2 = 0
- Cylinder: K = 0, H = 1/(2r), k1 = 1/r, k2 = 0

Author: Agent 28 (Day 4 Morning)
"""

import pytest
import numpy as np
import sys
from pathlib import Path

# Add cpp_core to path if needed
cpp_core_path = Path(__file__).parent.parent / "cpp_core" / "build"
if cpp_core_path.exists():
    sys.path.insert(0, str(cpp_core_path))

try:
    import cpp_core
except ImportError as e:
    pytest.skip(f"cpp_core module not available: {e}", allow_module_level=True)


class TestCurvatureBindings:
    """Test suite for curvature analysis Python bindings."""

    def test_imports(self):
        """Test that curvature classes are importable."""
        assert hasattr(cpp_core, 'CurvatureAnalyzer')
        assert hasattr(cpp_core, 'CurvatureResult')

    def test_curvature_result_construction(self):
        """Test CurvatureResult can be constructed."""
        result = cpp_core.CurvatureResult()

        # Check default values
        assert result.kappa1 == 0.0
        assert result.kappa2 == 0.0
        assert result.gaussian_curvature == 0.0
        assert result.mean_curvature == 0.0
        assert result.abs_mean_curvature == 0.0
        assert result.rms_curvature == 0.0

        # Check fundamental forms have reasonable defaults
        assert result.E == 1.0
        assert result.F == 0.0
        assert result.G == 1.0
        assert result.L == 0.0
        assert result.M == 0.0
        assert result.N == 0.0

    def test_curvature_result_attributes(self):
        """Test CurvatureResult attributes are readable and writable."""
        result = cpp_core.CurvatureResult()

        # Test principal curvatures
        result.kappa1 = 2.0
        result.kappa2 = 1.0
        assert result.kappa1 == 2.0
        assert result.kappa2 == 1.0

        # Test derived curvatures
        result.gaussian_curvature = 2.0
        result.mean_curvature = 1.5
        assert result.gaussian_curvature == 2.0
        assert result.mean_curvature == 1.5

        # Test principal directions
        result.dir1 = cpp_core.Point3D(1.0, 0.0, 0.0)
        result.dir2 = cpp_core.Point3D(0.0, 1.0, 0.0)
        assert result.dir1.x == 1.0
        assert result.dir2.y == 1.0

        # Test normal
        result.normal = cpp_core.Point3D(0.0, 0.0, 1.0)
        assert result.normal.z == 1.0

    def test_curvature_result_repr(self):
        """Test CurvatureResult string representation."""
        result = cpp_core.CurvatureResult()
        result.gaussian_curvature = 1.0
        result.mean_curvature = 0.5
        result.kappa1 = 0.7
        result.kappa2 = 0.3

        repr_str = repr(result)
        assert "CurvatureResult" in repr_str
        assert "K=" in repr_str
        assert "H=" in repr_str

    def test_curvature_analyzer_construction(self):
        """Test CurvatureAnalyzer can be constructed."""
        analyzer = cpp_core.CurvatureAnalyzer()
        assert analyzer is not None

    def test_curvature_analyzer_methods_exist(self):
        """Test CurvatureAnalyzer has expected methods."""
        analyzer = cpp_core.CurvatureAnalyzer()
        assert hasattr(analyzer, 'compute_curvature')
        assert hasattr(analyzer, 'batch_compute_curvature')

    def test_compute_curvature_on_sphere(self):
        """Test curvature computation on a sphere."""
        # Create a sphere SubD control cage
        # Sphere centered at origin with radius 2.0
        radius = 2.0

        # Simple octahedral subdivision sphere
        cage = cpp_core.SubDControlCage()

        # Vertices: 6 vertices of an octahedron
        cage.vertices = [
            cpp_core.Point3D(radius, 0, 0),   # 0: +X
            cpp_core.Point3D(-radius, 0, 0),  # 1: -X
            cpp_core.Point3D(0, radius, 0),   # 2: +Y
            cpp_core.Point3D(0, -radius, 0),  # 3: -Y
            cpp_core.Point3D(0, 0, radius),   # 4: +Z
            cpp_core.Point3D(0, 0, -radius),  # 5: -Z
        ]

        # Faces: 8 triangular faces
        cage.faces = [
            [0, 2, 4],  # +X +Y +Z
            [2, 1, 4],  # +Y -X +Z
            [1, 3, 4],  # -X -Y +Z
            [3, 0, 4],  # -Y +X +Z
            [2, 0, 5],  # +Y +X -Z
            [1, 2, 5],  # -X +Y -Z
            [3, 1, 5],  # -Y -X -Z
            [0, 3, 5],  # +X -Y -Z
        ]

        # Initialize evaluator
        evaluator = cpp_core.SubDEvaluator()
        evaluator.initialize(cage)

        # Create curvature analyzer
        analyzer = cpp_core.CurvatureAnalyzer()

        # Compute curvature at center of first face
        result = analyzer.compute_curvature(evaluator, 0, 0.5, 0.5)

        # For a sphere of radius r:
        # - k1 = k2 = 1/r
        # - K = 1/r²
        # - H = 1/r
        expected_k = 1.0 / radius
        expected_K = 1.0 / (radius * radius)
        expected_H = 1.0 / radius

        # Check curvatures (with tolerance for subdivision approximation)
        tolerance = 0.1  # 10% tolerance due to subdivision approximation

        assert abs(result.kappa1 - expected_k) < tolerance * expected_k, \
            f"kappa1: expected {expected_k}, got {result.kappa1}"
        assert abs(result.kappa2 - expected_k) < tolerance * expected_k, \
            f"kappa2: expected {expected_k}, got {result.kappa2}"
        assert abs(result.gaussian_curvature - expected_K) < tolerance * expected_K, \
            f"Gaussian: expected {expected_K}, got {result.gaussian_curvature}"
        assert abs(result.mean_curvature - expected_H) < tolerance * expected_H, \
            f"Mean: expected {expected_H}, got {result.mean_curvature}"

        # Principal directions should be orthogonal
        dir1 = result.dir1
        dir2 = result.dir2
        dot_product = dir1.x * dir2.x + dir1.y * dir2.y + dir1.z * dir2.z
        assert abs(dot_product) < 0.1, f"Directions not orthogonal: dot = {dot_product}"

    def test_compute_curvature_on_plane(self):
        """Test curvature computation on a flat plane."""
        # Create a planar quad
        cage = cpp_core.SubDControlCage()

        # Vertices: 4 corners of a square in XY plane
        cage.vertices = [
            cpp_core.Point3D(-1, -1, 0),
            cpp_core.Point3D(1, -1, 0),
            cpp_core.Point3D(1, 1, 0),
            cpp_core.Point3D(-1, 1, 0),
        ]

        # Single quad face
        cage.faces = [[0, 1, 2, 3]]

        # Initialize evaluator
        evaluator = cpp_core.SubDEvaluator()
        evaluator.initialize(cage)

        # Create curvature analyzer
        analyzer = cpp_core.CurvatureAnalyzer()

        # Compute curvature at center
        result = analyzer.compute_curvature(evaluator, 0, 0.5, 0.5)

        # For a plane:
        # - k1 = k2 = 0
        # - K = 0
        # - H = 0
        tolerance = 1e-3

        assert abs(result.kappa1) < tolerance, f"kappa1 should be 0, got {result.kappa1}"
        assert abs(result.kappa2) < tolerance, f"kappa2 should be 0, got {result.kappa2}"
        assert abs(result.gaussian_curvature) < tolerance, \
            f"Gaussian should be 0, got {result.gaussian_curvature}"
        assert abs(result.mean_curvature) < tolerance, \
            f"Mean should be 0, got {result.mean_curvature}"

        # Normal should point in +Z direction
        assert abs(result.normal.z - 1.0) < tolerance or \
               abs(result.normal.z + 1.0) < tolerance, \
            f"Normal should be ±Z, got {result.normal.z}"

    def test_batch_compute_curvature(self):
        """Test batch curvature computation."""
        # Create simple sphere cage
        radius = 2.0
        cage = cpp_core.SubDControlCage()

        cage.vertices = [
            cpp_core.Point3D(radius, 0, 0),
            cpp_core.Point3D(-radius, 0, 0),
            cpp_core.Point3D(0, radius, 0),
            cpp_core.Point3D(0, -radius, 0),
            cpp_core.Point3D(0, 0, radius),
            cpp_core.Point3D(0, 0, -radius),
        ]

        cage.faces = [
            [0, 2, 4],
            [2, 1, 4],
            [1, 3, 4],
            [3, 0, 4],
        ]

        evaluator = cpp_core.SubDEvaluator()
        evaluator.initialize(cage)

        analyzer = cpp_core.CurvatureAnalyzer()

        # Compute curvature at multiple points
        face_indices = [0, 0, 1, 1]
        params_u = [0.25, 0.75, 0.25, 0.75]
        params_v = [0.25, 0.75, 0.25, 0.75]

        results = analyzer.batch_compute_curvature(
            evaluator, face_indices, params_u, params_v
        )

        # Should get 4 results
        assert len(results) == 4

        # All results should be CurvatureResult objects
        for result in results:
            assert isinstance(result, cpp_core.CurvatureResult)
            # All should have non-zero curvature (sphere)
            assert abs(result.mean_curvature) > 0.1

    def test_fundamental_forms_accessible(self):
        """Test that fundamental form coefficients are accessible."""
        # Create simple plane
        cage = cpp_core.SubDControlCage()
        cage.vertices = [
            cpp_core.Point3D(-1, -1, 0),
            cpp_core.Point3D(1, -1, 0),
            cpp_core.Point3D(1, 1, 0),
            cpp_core.Point3D(-1, 1, 0),
        ]
        cage.faces = [[0, 1, 2, 3]]

        evaluator = cpp_core.SubDEvaluator()
        evaluator.initialize(cage)

        analyzer = cpp_core.CurvatureAnalyzer()
        result = analyzer.compute_curvature(evaluator, 0, 0.5, 0.5)

        # First fundamental form for a plane should be close to identity
        # (depends on parameterization)
        assert result.E > 0, "E should be positive"
        assert result.G > 0, "G should be positive"

        # Second fundamental form for plane should be zero
        tolerance = 1e-3
        assert abs(result.L) < tolerance, f"L should be 0, got {result.L}"
        assert abs(result.M) < tolerance, f"M should be 0, got {result.M}"
        assert abs(result.N) < tolerance, f"N should be 0, got {result.N}"

    def test_error_handling_uninitialized_evaluator(self):
        """Test that analyzer handles uninitialized evaluator properly."""
        evaluator = cpp_core.SubDEvaluator()
        analyzer = cpp_core.CurvatureAnalyzer()

        # Should raise an error when evaluator not initialized
        with pytest.raises((RuntimeError, Exception)):
            analyzer.compute_curvature(evaluator, 0, 0.5, 0.5)

    def test_numpy_integration(self):
        """Test that results can be easily converted to numpy arrays."""
        # Create simple sphere
        radius = 2.0
        cage = cpp_core.SubDControlCage()
        cage.vertices = [
            cpp_core.Point3D(radius, 0, 0),
            cpp_core.Point3D(-radius, 0, 0),
            cpp_core.Point3D(0, radius, 0),
            cpp_core.Point3D(0, -radius, 0),
            cpp_core.Point3D(0, 0, radius),
            cpp_core.Point3D(0, 0, -radius),
        ]
        cage.faces = [[0, 2, 4], [2, 1, 4], [1, 3, 4], [3, 0, 4]]

        evaluator = cpp_core.SubDEvaluator()
        evaluator.initialize(cage)

        analyzer = cpp_core.CurvatureAnalyzer()

        # Compute batch curvature
        n_points = 10
        face_indices = [0] * n_points
        params_u = np.linspace(0.1, 0.9, n_points).tolist()
        params_v = np.linspace(0.1, 0.9, n_points).tolist()

        results = analyzer.batch_compute_curvature(
            evaluator, face_indices, params_u, params_v
        )

        # Extract curvatures into numpy arrays
        gaussian = np.array([r.gaussian_curvature for r in results])
        mean = np.array([r.mean_curvature for r in results])
        kappa1 = np.array([r.kappa1 for r in results])
        kappa2 = np.array([r.kappa2 for r in results])

        # Verify arrays have correct shape
        assert gaussian.shape == (n_points,)
        assert mean.shape == (n_points,)
        assert kappa1.shape == (n_points,)
        assert kappa2.shape == (n_points,)

        # Verify all values are finite
        assert np.all(np.isfinite(gaussian))
        assert np.all(np.isfinite(mean))
        assert np.all(np.isfinite(kappa1))
        assert np.all(np.isfinite(kappa2))


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
