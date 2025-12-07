# app/analysis/boundary_extraction.py
"""
Boundary curve extraction using marching squares algorithm.

Extracts iso-contours from scalar fields defined on SubD faces,
returning curves in parametric (face_id, u, v) representation.
"""

from dataclasses import dataclass
from typing import List, Tuple, Optional, Callable
import numpy as np


@dataclass
class ParametricPoint:
    """A point in SubD parametric space."""
    face_id: int
    u: float
    v: float

    def to_tuple(self) -> Tuple[int, float, float]:
        return (self.face_id, self.u, self.v)


@dataclass
class ParametricSegment:
    """A line segment in parametric space."""
    start: ParametricPoint
    end: ParametricPoint


@dataclass
class ParametricCurve:
    """A curve defined by ordered points in parametric space."""
    points: List[ParametricPoint]
    is_closed: bool = False

    def to_control_points(self) -> List[List]:
        """Convert to control point format for JSON."""
        return [[p.face_id, p.u, p.v] for p in self.points]


# Marching squares edge table
# For each cell configuration (4 bits), lists edges that the contour crosses
# Edges: 0=bottom, 1=right, 2=top, 3=left
EDGE_TABLE = {
    0: [],
    1: [(3, 0)],
    2: [(0, 1)],
    3: [(3, 1)],
    4: [(1, 2)],
    5: [(3, 0), (1, 2)],  # Saddle - two segments
    6: [(0, 2)],
    7: [(3, 2)],
    8: [(2, 3)],
    9: [(2, 0)],
    10: [(0, 1), (2, 3)],  # Saddle - two segments
    11: [(2, 1)],
    12: [(1, 3)],
    13: [(1, 0)],
    14: [(0, 3)],
    15: [],
}


def marching_squares(
    grid: np.ndarray,
    threshold: float,
    face_id: int,
    u_range: Tuple[float, float] = (0.0, 1.0),
    v_range: Tuple[float, float] = (0.0, 1.0)
) -> List[ParametricSegment]:
    """
    Extract iso-contour segments using marching squares.

    Args:
        grid: 2D array of scalar values (resolution x resolution)
        threshold: Contour value to extract
        face_id: Face ID for all output points
        u_range: Range of u parameter
        v_range: Range of v parameter

    Returns:
        List of line segments in parametric space
    """
    rows, cols = grid.shape
    segments = []

    # Cell size in parametric space
    du = (u_range[1] - u_range[0]) / (cols - 1)
    dv = (v_range[1] - v_range[0]) / (rows - 1)

    # Edge midpoint interpolation
    def interp_edge(edge: int, i: int, j: int, vals: List[float]) -> ParametricPoint:
        """Interpolate position along edge based on values."""
        # vals = [bottom-left, bottom-right, top-right, top-left]
        u0 = u_range[0] + j * du
        v0 = v_range[0] + i * dv

        if edge == 0:  # Bottom edge
            t = (threshold - vals[0]) / (vals[1] - vals[0]) if vals[1] != vals[0] else 0.5
            return ParametricPoint(face_id, u0 + t * du, v0)
        elif edge == 1:  # Right edge
            t = (threshold - vals[1]) / (vals[2] - vals[1]) if vals[2] != vals[1] else 0.5
            return ParametricPoint(face_id, u0 + du, v0 + t * dv)
        elif edge == 2:  # Top edge
            t = (threshold - vals[3]) / (vals[2] - vals[3]) if vals[2] != vals[3] else 0.5
            return ParametricPoint(face_id, u0 + t * du, v0 + dv)
        else:  # Left edge (3)
            t = (threshold - vals[0]) / (vals[3] - vals[0]) if vals[3] != vals[0] else 0.5
            return ParametricPoint(face_id, u0, v0 + t * dv)

    # Process each cell
    for i in range(rows - 1):
        for j in range(cols - 1):
            # Get corner values: [bottom-left, bottom-right, top-right, top-left]
            vals = [
                grid[i, j],
                grid[i, j + 1],
                grid[i + 1, j + 1],
                grid[i + 1, j]
            ]

            # Compute cell configuration
            config = 0
            for k, v in enumerate(vals):
                if v >= threshold:
                    config |= (1 << k)

            # Get edge pairs for this configuration
            edges = EDGE_TABLE.get(config, [])

            # Create segments
            for e1, e2 in edges:
                p1 = interp_edge(e1, i, j, vals)
                p2 = interp_edge(e2, i, j, vals)
                segments.append(ParametricSegment(p1, p2))

    return segments


def connect_segments(segments: List[ParametricSegment], tolerance: float = 1e-6) -> List[ParametricCurve]:
    """
    Connect line segments into continuous curves.

    Args:
        segments: List of disconnected segments
        tolerance: Distance threshold for connecting endpoints

    Returns:
        List of connected curves
    """
    if not segments:
        return []

    def points_close(p1: ParametricPoint, p2: ParametricPoint) -> bool:
        if p1.face_id != p2.face_id:
            return False
        return abs(p1.u - p2.u) < tolerance and abs(p1.v - p2.v) < tolerance

    # Build curves by connecting segments
    curves = []
    remaining = list(segments)

    while remaining:
        # Start a new curve
        seg = remaining.pop(0)
        curve_points = [seg.start, seg.end]

        # Try to extend the curve
        changed = True
        while changed:
            changed = False

            for i, seg in enumerate(remaining):
                # Check if segment connects to end
                if points_close(seg.start, curve_points[-1]):
                    curve_points.append(seg.end)
                    remaining.pop(i)
                    changed = True
                    break
                elif points_close(seg.end, curve_points[-1]):
                    curve_points.append(seg.start)
                    remaining.pop(i)
                    changed = True
                    break
                # Check if segment connects to start
                elif points_close(seg.end, curve_points[0]):
                    curve_points.insert(0, seg.start)
                    remaining.pop(i)
                    changed = True
                    break
                elif points_close(seg.start, curve_points[0]):
                    curve_points.insert(0, seg.end)
                    remaining.pop(i)
                    changed = True
                    break

        # Check if curve is closed
        is_closed = points_close(curve_points[0], curve_points[-1])
        if is_closed:
            curve_points = curve_points[:-1]  # Remove duplicate endpoint

        curves.append(ParametricCurve(curve_points, is_closed))

    return curves


def extract_curvature_contours(
    sample_func: Callable[[int, float, float], float],
    face_id: int,
    threshold: float,
    resolution: int = 20
) -> List[ParametricCurve]:
    """
    Extract curvature iso-contours on a single face.

    Args:
        sample_func: Function (face_id, u, v) -> curvature value
        face_id: Face to sample
        threshold: Curvature threshold
        resolution: Grid resolution

    Returns:
        List of contour curves in parametric space
    """
    # Sample curvature on grid
    grid = np.zeros((resolution, resolution))
    for i in range(resolution):
        for j in range(resolution):
            u = j / (resolution - 1)
            v = i / (resolution - 1)
            grid[i, j] = sample_func(face_id, u, v)

    # Extract contour segments
    segments = marching_squares(grid, threshold, face_id)

    # Connect into curves
    curves = connect_segments(segments)

    return curves


def extract_ridge_lines(
    curvature_func: Callable[[int, float, float], Tuple[float, float]],
    face_id: int,
    resolution: int = 20,
    percentile: float = 90
) -> List[ParametricCurve]:
    """
    Extract ridge lines where |κ₁| is in top percentile.

    Args:
        curvature_func: Function (face_id, u, v) -> (k1, k2)
        face_id: Face to analyze
        resolution: Grid resolution
        percentile: Percentile threshold for ridge detection

    Returns:
        List of ridge curves
    """
    # Sample |κ₁| on grid
    k1_grid = np.zeros((resolution, resolution))
    for i in range(resolution):
        for j in range(resolution):
            u = j / (resolution - 1)
            v = i / (resolution - 1)
            k1, k2 = curvature_func(face_id, u, v)
            k1_grid[i, j] = abs(k1)

    # Find threshold at percentile
    threshold = np.percentile(k1_grid, percentile)

    # Extract contours at threshold
    segments = marching_squares(k1_grid, threshold, face_id)
    curves = connect_segments(segments)

    return curves


def extract_valley_lines(
    curvature_func: Callable[[int, float, float], Tuple[float, float]],
    face_id: int,
    resolution: int = 20,
    percentile: float = 10
) -> List[ParametricCurve]:
    """
    Extract valley lines where |κ₁| is in bottom percentile.

    Args:
        curvature_func: Function (face_id, u, v) -> (k1, k2)
        face_id: Face to analyze
        resolution: Grid resolution
        percentile: Percentile threshold for valley detection

    Returns:
        List of valley curves
    """
    # Sample |κ₁| on grid
    k1_grid = np.zeros((resolution, resolution))
    for i in range(resolution):
        for j in range(resolution):
            u = j / (resolution - 1)
            v = i / (resolution - 1)
            k1, k2 = curvature_func(face_id, u, v)
            k1_grid[i, j] = abs(k1)

    # Find threshold at percentile
    threshold = np.percentile(k1_grid, percentile)

    # Extract contours at threshold (inverted - looking for low values)
    # We invert and use high threshold
    inverted = k1_grid.max() - k1_grid
    inv_threshold = k1_grid.max() - threshold

    segments = marching_squares(inverted, inv_threshold, face_id)
    curves = connect_segments(segments)

    return curves
