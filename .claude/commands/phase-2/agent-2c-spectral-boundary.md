# Agent 2C: Boundary Curve Extraction - Spectral Lens

## Objective

Implement nodal line extraction from eigenfunction analysis using zero-crossing detection.

## Working Directory

`/Users/NickDuch/Desktop/Ind Designs/NDAAD/RhinoProjects/Latent`

## Read First

- `app/analysis/spectral_lens.py` - existing spectral lens implementation
- `app/analysis/spectral_decomposition.py` - eigenfunction computation
- `app/analysis/boundary_extraction.py` - marching squares from Agent 2B

## Files to Create

1. `app/analysis/nodal_extraction.py` - nodal line extraction
2. `tests/test_nodal_extraction.py` - nodal extraction tests

## Files to Modify

1. `app/analysis/spectral_lens.py` - add nodal line extraction methods

## Tasks

### 1. Create nodal_extraction.py

```python
# app/analysis/nodal_extraction.py
"""
Nodal line extraction from eigenfunction data.

Extracts zero-crossings of eigenfunctions defined on a tessellation,
returning curves in parametric (face_id, u, v) representation.
"""

from dataclasses import dataclass
from typing import List, Tuple, Dict, Optional, Set
import numpy as np

from .boundary_extraction import ParametricPoint, ParametricCurve, ParametricSegment


@dataclass
class TessellationVertex:
    """A vertex in the surface tessellation."""
    index: int
    position: np.ndarray  # (x, y, z)
    parametric: ParametricPoint
    value: float = 0.0  # Eigenfunction value at this vertex


@dataclass
class TessellationTriangle:
    """A triangle in the surface tessellation."""
    vertices: Tuple[int, int, int]  # Vertex indices
    face_id: int  # SubD face this triangle belongs to


class NodalLineExtractor:
    """
    Extracts nodal lines (zero-crossings) from eigenfunction data on a tessellation.

    The algorithm:
    1. For each triangle edge, check if eigenfunction changes sign
    2. Interpolate the exact zero-crossing position
    3. Connect crossings into continuous curves
    """

    def __init__(
        self,
        vertices: List[TessellationVertex],
        triangles: List[TessellationTriangle]
    ):
        """
        Initialize with tessellation data.

        Args:
            vertices: List of tessellation vertices with positions and parametric coords
            triangles: List of triangles with vertex indices
        """
        self.vertices = vertices
        self.triangles = triangles
        self._build_edge_map()

    def _build_edge_map(self):
        """Build a map of edges to triangles for connectivity."""
        self.edge_to_triangles: Dict[Tuple[int, int], List[int]] = {}

        for tri_idx, tri in enumerate(self.triangles):
            v0, v1, v2 = tri.vertices
            edges = [(v0, v1), (v1, v2), (v2, v0)]

            for e in edges:
                key = (min(e), max(e))  # Canonical edge key
                if key not in self.edge_to_triangles:
                    self.edge_to_triangles[key] = []
                self.edge_to_triangles[key].append(tri_idx)

    def set_eigenfunction_values(self, values: np.ndarray):
        """
        Set eigenfunction values at vertices.

        Args:
            values: Array of eigenfunction values (one per vertex)
        """
        if len(values) != len(self.vertices):
            raise ValueError(f"Expected {len(self.vertices)} values, got {len(values)}")

        for i, v in enumerate(self.vertices):
            v.value = values[i]

    def extract_nodal_lines(self, threshold: float = 0.0) -> List[ParametricCurve]:
        """
        Extract nodal lines where eigenfunction equals threshold.

        Args:
            threshold: Value to extract (default 0.0 for nodal lines)

        Returns:
            List of curves in parametric space
        """
        # Find all zero-crossings on edges
        crossings = self._find_crossings(threshold)

        # Connect crossings into curves
        curves = self._connect_crossings(crossings)

        return curves

    def _find_crossings(self, threshold: float) -> Dict[Tuple[int, int], ParametricPoint]:
        """
        Find all edge crossings where the eigenfunction crosses the threshold.

        Returns:
            Map from edge (v0, v1) to crossing point
        """
        crossings = {}

        for (v0_idx, v1_idx), tri_indices in self.edge_to_triangles.items():
            v0 = self.vertices[v0_idx]
            v1 = self.vertices[v1_idx]

            # Check if eigenfunction crosses threshold on this edge
            val0 = v0.value - threshold
            val1 = v1.value - threshold

            if val0 * val1 < 0:  # Different signs = crossing
                # Linear interpolation of crossing position
                t = abs(val0) / (abs(val0) + abs(val1))

                # Interpolate in parametric space
                if v0.parametric.face_id == v1.parametric.face_id:
                    # Same face - simple interpolation
                    crossing = ParametricPoint(
                        face_id=v0.parametric.face_id,
                        u=(1 - t) * v0.parametric.u + t * v1.parametric.u,
                        v=(1 - t) * v0.parametric.v + t * v1.parametric.v
                    )
                else:
                    # Cross-face edge - use the face of the closer vertex
                    crossing = ParametricPoint(
                        face_id=v0.parametric.face_id if t < 0.5 else v1.parametric.face_id,
                        u=(1 - t) * v0.parametric.u + t * v1.parametric.u,
                        v=(1 - t) * v0.parametric.v + t * v1.parametric.v
                    )

                crossings[(v0_idx, v1_idx)] = crossing

        return crossings

    def _connect_crossings(
        self,
        crossings: Dict[Tuple[int, int], ParametricPoint]
    ) -> List[ParametricCurve]:
        """
        Connect crossing points into continuous curves.

        Uses triangle adjacency to trace through the mesh.
        """
        if not crossings:
            return []

        curves = []
        used_edges: Set[Tuple[int, int]] = set()

        # Process each triangle to find connected crossings
        for tri_idx, tri in enumerate(self.triangles):
            v0, v1, v2 = tri.vertices
            edges = [
                (min(v0, v1), max(v0, v1)),
                (min(v1, v2), max(v1, v2)),
                (min(v2, v0), max(v2, v0))
            ]

            # Find crossings in this triangle
            tri_crossings = []
            for edge in edges:
                if edge in crossings and edge not in used_edges:
                    tri_crossings.append((edge, crossings[edge]))

            # If we have exactly 2 crossings, they form a segment
            if len(tri_crossings) == 2:
                edge1, point1 = tri_crossings[0]
                edge2, point2 = tri_crossings[1]

                # Try to extend into a longer curve
                curve_points = self._trace_curve(
                    crossings, used_edges, edge1, point1, edge2, point2, tri_idx
                )

                if curve_points:
                    is_closed = self._points_close(curve_points[0], curve_points[-1])
                    if is_closed:
                        curve_points = curve_points[:-1]
                    curves.append(ParametricCurve(curve_points, is_closed))

        return curves

    def _trace_curve(
        self,
        crossings: Dict[Tuple[int, int], ParametricPoint],
        used_edges: Set[Tuple[int, int]],
        start_edge: Tuple[int, int],
        start_point: ParametricPoint,
        end_edge: Tuple[int, int],
        end_point: ParametricPoint,
        start_tri: int
    ) -> List[ParametricPoint]:
        """
        Trace a curve through the mesh starting from a segment.

        Returns list of points forming the curve.
        """
        curve_points = [start_point, end_point]
        used_edges.add(start_edge)
        used_edges.add(end_edge)

        # Trace forward from end_edge
        current_edge = end_edge
        while True:
            next_edge, next_point = self._find_next_crossing(
                crossings, used_edges, current_edge
            )
            if next_edge is None:
                break
            curve_points.append(next_point)
            used_edges.add(next_edge)
            current_edge = next_edge

        # Trace backward from start_edge
        current_edge = start_edge
        while True:
            next_edge, next_point = self._find_next_crossing(
                crossings, used_edges, current_edge
            )
            if next_edge is None:
                break
            curve_points.insert(0, next_point)
            used_edges.add(next_edge)
            current_edge = next_edge

        return curve_points

    def _find_next_crossing(
        self,
        crossings: Dict[Tuple[int, int], ParametricPoint],
        used_edges: Set[Tuple[int, int]],
        current_edge: Tuple[int, int]
    ) -> Tuple[Optional[Tuple[int, int]], Optional[ParametricPoint]]:
        """
        Find the next crossing connected to current_edge via a triangle.
        """
        # Get triangles sharing this edge
        if current_edge not in self.edge_to_triangles:
            return None, None

        for tri_idx in self.edge_to_triangles[current_edge]:
            tri = self.triangles[tri_idx]
            v0, v1, v2 = tri.vertices
            edges = [
                (min(v0, v1), max(v0, v1)),
                (min(v1, v2), max(v1, v2)),
                (min(v2, v0), max(v2, v0))
            ]

            # Find other crossing in this triangle
            for edge in edges:
                if edge != current_edge and edge in crossings and edge not in used_edges:
                    return edge, crossings[edge]

        return None, None

    def _points_close(self, p1: ParametricPoint, p2: ParametricPoint, tol: float = 1e-6) -> bool:
        """Check if two parametric points are close."""
        if p1.face_id != p2.face_id:
            return False
        return abs(p1.u - p2.u) < tol and abs(p1.v - p2.v) < tol


def extract_nodal_lines_from_eigenfunction(
    eigenfunction: np.ndarray,
    vertices: np.ndarray,
    triangles: np.ndarray,
    parametric_coords: List[ParametricPoint]
) -> List[ParametricCurve]:
    """
    Convenience function to extract nodal lines from eigenfunction data.

    Args:
        eigenfunction: Array of eigenfunction values at vertices
        vertices: Nx3 array of vertex positions
        triangles: Mx3 array of triangle vertex indices
        parametric_coords: Parametric coordinates for each vertex

    Returns:
        List of nodal line curves
    """
    # Build tessellation vertices
    tess_vertices = []
    for i, (pos, param) in enumerate(zip(vertices, parametric_coords)):
        tess_vertices.append(TessellationVertex(
            index=i,
            position=pos,
            parametric=param,
            value=eigenfunction[i]
        ))

    # Build triangles (assuming all belong to face 0 for now)
    # TODO: Properly track which SubD face each triangle belongs to
    tess_triangles = []
    for i, tri in enumerate(triangles):
        # Use the face_id from the first vertex
        face_id = parametric_coords[tri[0]].face_id
        tess_triangles.append(TessellationTriangle(
            vertices=tuple(tri),
            face_id=face_id
        ))

    # Extract nodal lines
    extractor = NodalLineExtractor(tess_vertices, tess_triangles)
    return extractor.extract_nodal_lines(threshold=0.0)
```

### 2. Update spectral_lens.py

Add these methods to the `SpectralLens` class:

```python
# Add to app/analysis/spectral_lens.py

from .nodal_extraction import (
    NodalLineExtractor,
    TessellationVertex,
    TessellationTriangle,
    extract_nodal_lines_from_eigenfunction
)
from .boundary_extraction import ParametricPoint, ParametricCurve


class SpectralLens:
    # ... existing code ...

    def extract_nodal_curves(
        self,
        eigenfunction_index: int = 1,
        threshold: float = 0.0
    ) -> List[ParametricCurve]:
        """
        Extract nodal lines from a specific eigenfunction.

        Args:
            eigenfunction_index: Which eigenfunction to use (0=first, 1=second, etc.)
            threshold: Value to extract (0.0 for nodal lines)

        Returns:
            List of nodal curves in parametric space
        """
        # Get eigenfunction values
        eigenfunctions = self._compute_eigenfunctions()
        if eigenfunction_index >= len(eigenfunctions):
            raise ValueError(f"Eigenfunction {eigenfunction_index} not available")

        eigenfunction = eigenfunctions[eigenfunction_index]

        # Get tessellation data
        vertices, triangles = self._get_tessellation()
        parametric_coords = self._get_parametric_coordinates()

        # Extract nodal lines
        curves = extract_nodal_lines_from_eigenfunction(
            eigenfunction,
            vertices,
            triangles,
            parametric_coords
        )

        return curves

    def extract_all_nodal_curves(
        self,
        num_eigenfunctions: int = 5
    ) -> Dict[int, List[ParametricCurve]]:
        """
        Extract nodal lines from multiple eigenfunctions.

        Args:
            num_eigenfunctions: Number of eigenfunctions to process

        Returns:
            Dict mapping eigenfunction index to its nodal curves
        """
        result = {}

        for i in range(num_eigenfunctions):
            try:
                curves = self.extract_nodal_curves(eigenfunction_index=i)
                if curves:
                    result[i] = curves
            except (ValueError, IndexError):
                break

        return result

    def discover_regions_with_boundaries(
        self,
        num_eigenfunctions: int = 3
    ) -> List[dict]:
        """
        Discover regions and extract their boundary curves from nodal lines.

        Returns list of dicts with region info including boundary curves.
        """
        # Get base regions
        regions = self.discover_regions(num_eigenfunctions)

        # Extract nodal lines from first few eigenfunctions
        all_curves = self.extract_all_nodal_curves(num_eigenfunctions)

        # TODO: Match curves to regions based on spatial relationship
        # For now, attach all curves from eigenfunction i to region i
        result = []
        for i, region in enumerate(regions):
            curves = all_curves.get(i, [])
            region_dict = {
                "id": f"r{i}",
                "unity_principle": region.unity_principle,
                "resonance_score": region.resonance_score,
                "boundary_curves": [c.to_control_points() for c in curves],
                "eigenfunction_index": i
            }
            result.append(region_dict)

        return result

    def _compute_eigenfunctions(self) -> List[np.ndarray]:
        """
        Compute eigenfunctions of the Laplace-Beltrami operator.

        Returns list of eigenfunction arrays (one value per tessellation vertex).
        """
        # Use existing spectral decomposition
        # This should already exist in spectral_decomposition.py
        from .spectral_decomposition import compute_mesh_eigenfunctions

        vertices, triangles = self._get_tessellation()
        eigenvalues, eigenvectors = compute_mesh_eigenfunctions(
            vertices, triangles, num_eigenvalues=10
        )

        return [eigenvectors[:, i] for i in range(eigenvectors.shape[1])]

    def _get_tessellation(self) -> Tuple[np.ndarray, np.ndarray]:
        """
        Get or compute the surface tessellation.

        Returns:
            vertices: Nx3 array of vertex positions
            triangles: Mx3 array of triangle vertex indices
        """
        # Use existing tessellation from evaluator
        # This should sample the SubD limit surface
        return self.evaluator.get_tessellation()

    def _get_parametric_coordinates(self) -> List[ParametricPoint]:
        """
        Get parametric coordinates for each tessellation vertex.

        Returns:
            List of ParametricPoint for each vertex
        """
        # Get mapping from tessellation vertices to parametric space
        return self.evaluator.get_vertex_parametric_coords()
```

### 3. Create Tests

```python
# tests/test_nodal_extraction.py
"""Tests for nodal line extraction."""

import pytest
import numpy as np

from app.analysis.nodal_extraction import (
    NodalLineExtractor,
    TessellationVertex,
    TessellationTriangle,
    extract_nodal_lines_from_eigenfunction
)
from app.analysis.boundary_extraction import ParametricPoint


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

        # Linear eigenfunction: u - 0.5
        eigenfunction = np.array([p.u - 0.5 for p in parametric])

        curves = extract_nodal_lines_from_eigenfunction(
            eigenfunction, vertices, triangles, parametric
        )

        # Should have a vertical line at u = 0.5
        assert len(curves) >= 1
```

## Success Criteria

- [ ] Zero-crossing detection works on triangle edges
- [ ] Crossings connect into continuous curves
- [ ] Closed nodal loops are detected
- [ ] SpectralLens has nodal line extraction methods
- [ ] Multiple eigenfunctions can be processed
- [ ] All unit tests pass

## Verification Commands

```bash
cd /Users/NickDuch/Desktop/Ind Designs/NDAAD/RhinoProjects/Latent

# Run nodal extraction tests
python -m pytest tests/test_nodal_extraction.py -v

# Quick integration test
python -c "
import numpy as np
from app.analysis.nodal_extraction import (
    NodalLineExtractor,
    TessellationVertex,
    TessellationTriangle
)
from app.analysis.boundary_extraction import ParametricPoint

# Create simple mesh
vertices = [
    TessellationVertex(0, np.array([0,0,0]), ParametricPoint(0, 0, 0)),
    TessellationVertex(1, np.array([1,0,0]), ParametricPoint(0, 1, 0)),
    TessellationVertex(2, np.array([1,1,0]), ParametricPoint(0, 1, 1)),
    TessellationVertex(3, np.array([0,1,0]), ParametricPoint(0, 0, 1)),
]
triangles = [
    TessellationTriangle((0,1,2), 0),
    TessellationTriangle((0,2,3), 0),
]

extractor = NodalLineExtractor(vertices, triangles)
extractor.set_eigenfunction_values(np.array([-1, 1, 1, -1]))
curves = extractor.extract_nodal_lines()
print(f'Found {len(curves)} nodal curves')
"
```

## Do Not Modify

- `analysis_service/server.py` (Agent 2A's domain)
- `app/analysis/differential_lens.py` (Agent 2B's domain)
- `app/analysis/boundary_extraction.py` (Agent 2B's domain)
- Files in `cpp_core/`

## Skills to Use

- `superpowers:test-driven-development` - write tests first
- `superpowers:verification-before-completion` - run all tests

## Notes

**Tessellation dependency**: The spectral lens needs a tessellation of the SubD surface. This may come from the C++ evaluator or be computed in Python. The implementation assumes tessellation methods exist on the evaluator.

**Eigenfunction computation**: Uses existing `spectral_decomposition.py` for computing the Laplace-Beltrami eigenfunctions. If this doesn't exist yet, stub it and document the interface needed.

## Report

When complete, provide:
1. Test output showing all tests pass
2. Example of extracted nodal lines from a sinusoidal test case
3. Any integration issues with existing spectral lens code
