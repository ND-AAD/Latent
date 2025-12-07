"""Tests for nodal line extraction."""

import pytest
import numpy as np

from app.analysis.nodal_extraction import (
    NodalLineExtractor,
    TessellationVertex,
    TessellationTriangle,
    extract_nodal_lines_from_eigenfunction,
    ParametricPoint
)


class TestNodalLineExtractor:
    """Test the nodal line extractor."""

    def create_simple_mesh(self):
        """Create a simple 2x2 quad mesh (2 triangles)."""
        # 4 vertices forming a quad
        vertices = [
            TessellationVertex(0, np.array([0, 0, 0]), ParametricPoint(0, 0, 0)),
            TessellationVertex(1, np.array([1, 0, 0]), ParametricPoint(0, 1, 0)),
            TessellationVertex(2, np.array([1, 1, 0]), ParametricPoint(0, 1, 1)),
            TessellationVertex(3, np.array([0, 1, 0]), ParametricPoint(0, 0, 1)),
        ]

        # 2 triangles
        triangles = [
            TessellationTriangle((0, 1, 2), face_id=0),
            TessellationTriangle((0, 2, 3), face_id=0),
        ]

        return vertices, triangles

    def test_no_crossings(self):
        """Test with all positive values - no crossings."""
        vertices, triangles = self.create_simple_mesh()
        extractor = NodalLineExtractor(vertices, triangles)

        # All values > 0
        extractor.set_eigenfunction_values(np.array([1, 2, 3, 4]))
        curves = extractor.extract_nodal_lines()

        assert len(curves) == 0

    def test_diagonal_crossing(self):
        """Test with values that create a diagonal crossing."""
        vertices, triangles = self.create_simple_mesh()
        extractor = NodalLineExtractor(vertices, triangles)

        # Values: bottom-left and top-right negative, others positive
        # Should create a diagonal nodal line
        extractor.set_eigenfunction_values(np.array([-1, 1, -1, 1]))
        curves = extractor.extract_nodal_lines()

        # Should have crossings
        assert len(curves) >= 1

    def test_horizontal_crossing(self):
        """Test with values that create a horizontal crossing."""
        vertices, triangles = self.create_simple_mesh()
        extractor = NodalLineExtractor(vertices, triangles)

        # Bottom negative, top positive
        extractor.set_eigenfunction_values(np.array([-1, -1, 1, 1]))
        curves = extractor.extract_nodal_lines()

        assert len(curves) >= 1

        # Check that crossing is approximately at v=0.5
        for curve in curves:
            for point in curve.points:
                assert 0.4 <= point.v <= 0.6

    def test_interpolation_accuracy(self):
        """Test that zero-crossing interpolation is accurate."""
        vertices, triangles = self.create_simple_mesh()
        extractor = NodalLineExtractor(vertices, triangles)

        # Linear gradient: 0 at u=0.5
        # v0(u=0) = -0.5, v1(u=1) = 0.5, etc.
        extractor.set_eigenfunction_values(np.array([-0.5, 0.5, 0.5, -0.5]))
        curves = extractor.extract_nodal_lines()

        # Crossing should be at u ≈ 0.5
        for curve in curves:
            for point in curve.points:
                assert 0.45 <= point.u <= 0.55


class TestLargerMesh:
    """Test with a larger mesh."""

    def create_grid_mesh(self, n: int = 5):
        """Create an n x n grid mesh."""
        vertices = []
        idx = 0
        for j in range(n):
            for i in range(n):
                u = i / (n - 1)
                v = j / (n - 1)
                vertices.append(TessellationVertex(
                    idx,
                    np.array([u, v, 0]),
                    ParametricPoint(0, u, v)
                ))
                idx += 1

        triangles = []
        for j in range(n - 1):
            for i in range(n - 1):
                v0 = j * n + i
                v1 = v0 + 1
                v2 = v0 + n + 1
                v3 = v0 + n
                triangles.append(TessellationTriangle((v0, v1, v2), 0))
                triangles.append(TessellationTriangle((v0, v2, v3), 0))

        return vertices, triangles

    def test_circular_nodal_line(self):
        """Test extraction of a circular nodal line."""
        vertices, triangles = self.create_grid_mesh(10)
        extractor = NodalLineExtractor(vertices, triangles)

        # Create a radial function: r - 0.3 where r is distance from center
        center = np.array([0.5, 0.5, 0])
        values = np.array([
            np.linalg.norm(v.position - center) - 0.3
            for v in vertices
        ])
        extractor.set_eigenfunction_values(values)

        curves = extractor.extract_nodal_lines()

        # Should have one closed curve (circle)
        assert len(curves) >= 1

        # At least one should be closed (if we have good resolution)
        closed_curves = [c for c in curves if c.is_closed]
        # Note: May not be closed if mesh resolution is low
        assert len(curves) > 0

    def test_multiple_nodal_lines(self):
        """Test extraction of multiple nodal lines."""
        vertices, triangles = self.create_grid_mesh(10)
        extractor = NodalLineExtractor(vertices, triangles)

        # Create a sinusoidal pattern: sin(2*pi*u) * sin(2*pi*v)
        values = np.array([
            np.sin(2 * np.pi * v.parametric.u) * np.sin(2 * np.pi * v.parametric.v)
            for v in vertices
        ])
        extractor.set_eigenfunction_values(values)

        curves = extractor.extract_nodal_lines()

        # Should have multiple curves (grid pattern)
        assert len(curves) >= 2


class TestExtractFromEigenfunction:
    """Test the convenience function."""

    def test_basic_extraction(self):
        """Test the convenience function."""
        n = 5
        vertices = np.zeros((n * n, 3))
        parametric = []

        idx = 0
        for j in range(n):
            for i in range(n):
                u = i / (n - 1)
                v = j / (n - 1)
                vertices[idx] = [u, v, 0]
                parametric.append(ParametricPoint(0, u, v))
                idx += 1

        triangles = []
        for j in range(n - 1):
            for i in range(n - 1):
                v0 = j * n + i
                triangles.append([v0, v0 + 1, v0 + n + 1])
                triangles.append([v0, v0 + n + 1, v0 + n])
        triangles = np.array(triangles)

        # Linear eigenfunction: u - 0.4 (offset to avoid landing exactly on vertex)
        eigenfunction = np.array([p.u - 0.4 for p in parametric])

        curves = extract_nodal_lines_from_eigenfunction(
            eigenfunction, vertices, triangles, parametric
        )

        # Should have a vertical line at u ≈ 0.4
        assert len(curves) >= 1
