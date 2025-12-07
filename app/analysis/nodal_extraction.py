"""
Nodal line extraction from eigenfunction data.

Extracts zero-crossings of eigenfunctions defined on a tessellation,
returning curves in parametric (face_id, u, v) representation.
"""

from dataclasses import dataclass
from typing import List, Tuple, Dict, Optional, Set
import numpy as np


# Minimal stubs for boundary extraction classes (Agent 2B's domain)
# TODO: Replace with imports from boundary_extraction.py when available

@dataclass
class ParametricPoint:
    """A point in parametric (face_id, u, v) space."""
    face_id: int
    u: float
    v: float


@dataclass
class ParametricSegment:
    """A segment connecting two parametric points."""
    start: ParametricPoint
    end: ParametricPoint


@dataclass
class ParametricCurve:
    """A curve in parametric space."""
    points: List[ParametricPoint]
    is_closed: bool = False

    def to_control_points(self) -> List[Tuple[int, float, float]]:
        """Convert to list of (face_id, u, v) tuples."""
        return [(p.face_id, p.u, p.v) for p in self.points]


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

            # TODO: Handle edge case where val0 or val1 is exactly 0 (crossing lands
            # exactly on a vertex). Currently this is missed because 0 * x = 0, not < 0.
            # Should detect val0 == 0 or val1 == 0 and treat vertex as crossing point.
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
