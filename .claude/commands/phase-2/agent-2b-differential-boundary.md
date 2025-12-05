# Agent 2B: Boundary Curve Extraction - Differential Lens

## Objective

Implement boundary curve extraction from curvature analysis using marching squares.

## Working Directory

`/Users/NickDuch/Desktop/Ind Designs/NDAAD/RhinoProjects/Latent`

## Read First

- `app/analysis/differential_lens.py` - existing curvature lens implementation
- `docs/plans/2025-12-04-rhino-plugin-architecture-design.md` - boundary curve requirements
- `analysis_service/handlers.py` - where results will be integrated

## Files to Create

1. `app/analysis/boundary_extraction.py` - marching squares implementation
2. `tests/test_boundary_extraction.py` - boundary extraction tests

## Files to Modify

1. `app/analysis/differential_lens.py` - add boundary extraction methods

## Tasks

### 1. Create boundary_extraction.py

```python
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
```

### 2. Update differential_lens.py

Add these methods to the `DifferentialLens` class:

```python
# Add to app/analysis/differential_lens.py

from .boundary_extraction import (
    extract_curvature_contours,
    extract_ridge_lines,
    extract_valley_lines,
    ParametricCurve
)


class DifferentialLens:
    # ... existing code ...

    def extract_boundary_curves(
        self,
        curvature_type: str = "mean",
        threshold: float = 0.0,
        resolution: int = 20
    ) -> List[ParametricCurve]:
        """
        Extract boundary curves where curvature crosses threshold.

        Args:
            curvature_type: "mean" (H), "gaussian" (K), "k1", or "k2"
            threshold: Curvature value to extract contour at
            resolution: Sampling resolution per face

        Returns:
            List of boundary curves in parametric space
        """
        all_curves = []

        def sample_curvature(face_id: int, u: float, v: float) -> float:
            k1, k2 = self._compute_principal_curvatures(face_id, u, v)
            if curvature_type == "mean":
                return (k1 + k2) / 2
            elif curvature_type == "gaussian":
                return k1 * k2
            elif curvature_type == "k1":
                return k1
            else:  # k2
                return k2

        for face_id in range(self.evaluator.get_control_face_count()):
            curves = extract_curvature_contours(
                sample_curvature,
                face_id,
                threshold,
                resolution
            )
            all_curves.extend(curves)

        return all_curves

    def extract_ridges(
        self,
        resolution: int = 20,
        percentile: float = 90
    ) -> List[ParametricCurve]:
        """
        Extract ridge lines (high |κ₁| regions).

        Args:
            resolution: Sampling resolution per face
            percentile: Threshold percentile

        Returns:
            List of ridge curves
        """
        all_curves = []

        def curvature_func(face_id: int, u: float, v: float) -> Tuple[float, float]:
            return self._compute_principal_curvatures(face_id, u, v)

        for face_id in range(self.evaluator.get_control_face_count()):
            curves = extract_ridge_lines(
                curvature_func,
                face_id,
                resolution,
                percentile
            )
            all_curves.extend(curves)

        return all_curves

    def extract_valleys(
        self,
        resolution: int = 20,
        percentile: float = 10
    ) -> List[ParametricCurve]:
        """
        Extract valley lines (low |κ₁| regions).
        """
        all_curves = []

        def curvature_func(face_id: int, u: float, v: float) -> Tuple[float, float]:
            return self._compute_principal_curvatures(face_id, u, v)

        for face_id in range(self.evaluator.get_control_face_count()):
            curves = extract_valley_lines(
                curvature_func,
                face_id,
                resolution,
                percentile
            )
            all_curves.extend(curves)

        return all_curves

    def discover_regions_with_boundaries(
        self,
        curvature_tolerance: float = 0.3,
        resolution: int = 20
    ) -> List[dict]:
        """
        Discover regions and extract their boundary curves.

        Returns list of dicts with region info including boundary curves.
        """
        # Get base regions
        regions = self.discover_regions(curvature_tolerance)

        # Extract boundaries at tolerance threshold
        mean_curves = self.extract_boundary_curves(
            curvature_type="mean",
            threshold=curvature_tolerance,
            resolution=resolution
        )

        # TODO: Match curves to regions based on spatial relationship
        # For now, return curves with the first region
        result = []
        for i, region in enumerate(regions):
            region_dict = {
                "id": f"r{i}",
                "unity_principle": region.unity_principle,
                "resonance_score": region.resonance_score,
                "boundary_curves": [c.to_control_points() for c in mean_curves] if i == 0 else []
            }
            result.append(region_dict)

        return result
```

### 3. Create Tests

```python
# tests/test_boundary_extraction.py
"""Tests for boundary curve extraction."""

import pytest
import numpy as np

from app.analysis.boundary_extraction import (
    marching_squares,
    connect_segments,
    extract_curvature_contours,
    ParametricPoint,
    ParametricSegment,
    ParametricCurve
)


class TestMarchingSquares:
    """Test marching squares algorithm."""

    def test_no_contour_below_threshold(self):
        # Grid all below threshold
        grid = np.zeros((5, 5))
        segments = marching_squares(grid, 0.5, face_id=0)
        assert len(segments) == 0

    def test_no_contour_above_threshold(self):
        # Grid all above threshold
        grid = np.ones((5, 5))
        segments = marching_squares(grid, 0.5, face_id=0)
        assert len(segments) == 0

    def test_horizontal_contour(self):
        # Create a gradient that should produce horizontal contour
        grid = np.array([
            [0.0, 0.0, 0.0],
            [0.5, 0.5, 0.5],
            [1.0, 1.0, 1.0]
        ])
        segments = marching_squares(grid, 0.5, face_id=0)

        # Should have segments along middle row
        assert len(segments) >= 1

        # All points should have v ≈ 0.5 (middle of grid)
        for seg in segments:
            assert 0.4 <= seg.start.v <= 0.6
            assert 0.4 <= seg.end.v <= 0.6

    def test_circular_contour(self):
        # Create a radial gradient from center
        n = 10
        grid = np.zeros((n, n))
        cx, cy = n // 2, n // 2
        for i in range(n):
            for j in range(n):
                grid[i, j] = np.sqrt((i - cy)**2 + (j - cx)**2)

        # Threshold at radius 3
        segments = marching_squares(grid, 3.0, face_id=0)

        # Should have multiple segments forming a rough circle
        assert len(segments) >= 4

    def test_face_id_preserved(self):
        grid = np.array([[0, 1], [1, 0]])
        segments = marching_squares(grid, 0.5, face_id=42)

        for seg in segments:
            assert seg.start.face_id == 42
            assert seg.end.face_id == 42


class TestConnectSegments:
    """Test segment connection algorithm."""

    def test_empty_input(self):
        curves = connect_segments([])
        assert len(curves) == 0

    def test_single_segment(self):
        seg = ParametricSegment(
            ParametricPoint(0, 0.0, 0.0),
            ParametricPoint(0, 1.0, 0.0)
        )
        curves = connect_segments([seg])

        assert len(curves) == 1
        assert len(curves[0].points) == 2

    def test_two_connected_segments(self):
        seg1 = ParametricSegment(
            ParametricPoint(0, 0.0, 0.0),
            ParametricPoint(0, 0.5, 0.0)
        )
        seg2 = ParametricSegment(
            ParametricPoint(0, 0.5, 0.0),
            ParametricPoint(0, 1.0, 0.0)
        )
        curves = connect_segments([seg1, seg2])

        assert len(curves) == 1
        assert len(curves[0].points) == 3

    def test_closed_loop(self):
        # Create a square loop
        segments = [
            ParametricSegment(ParametricPoint(0, 0, 0), ParametricPoint(0, 1, 0)),
            ParametricSegment(ParametricPoint(0, 1, 0), ParametricPoint(0, 1, 1)),
            ParametricSegment(ParametricPoint(0, 1, 1), ParametricPoint(0, 0, 1)),
            ParametricSegment(ParametricPoint(0, 0, 1), ParametricPoint(0, 0, 0)),
        ]
        curves = connect_segments(segments)

        assert len(curves) == 1
        assert curves[0].is_closed

    def test_two_separate_curves(self):
        # Two disconnected segments
        seg1 = ParametricSegment(
            ParametricPoint(0, 0.0, 0.0),
            ParametricPoint(0, 0.5, 0.0)
        )
        seg2 = ParametricSegment(
            ParametricPoint(0, 0.0, 1.0),
            ParametricPoint(0, 0.5, 1.0)
        )
        curves = connect_segments([seg1, seg2])

        assert len(curves) == 2


class TestCurvatureContours:
    """Test curvature contour extraction."""

    def test_extract_contours(self):
        # Simple linear curvature function
        def sample_func(face_id, u, v):
            return u  # Curvature increases with u

        curves = extract_curvature_contours(
            sample_func,
            face_id=0,
            threshold=0.5,
            resolution=10
        )

        # Should have at least one curve at u ≈ 0.5
        assert len(curves) >= 1

        # All points should have u ≈ 0.5
        for curve in curves:
            for point in curve.points:
                assert 0.4 <= point.u <= 0.6


class TestParametricCurve:
    """Test ParametricCurve methods."""

    def test_to_control_points(self):
        curve = ParametricCurve([
            ParametricPoint(0, 0.0, 0.0),
            ParametricPoint(0, 0.5, 0.5),
            ParametricPoint(0, 1.0, 1.0)
        ])

        control_points = curve.to_control_points()

        assert len(control_points) == 3
        assert control_points[0] == [0, 0.0, 0.0]
        assert control_points[1] == [0, 0.5, 0.5]
        assert control_points[2] == [0, 1.0, 1.0]
```

## Success Criteria

- [ ] Marching squares extracts contours correctly
- [ ] Segments connect into continuous curves
- [ ] Closed loops are detected
- [ ] Curvature contours extracted from mock data
- [ ] DifferentialLens has boundary extraction methods
- [ ] All unit tests pass

## Verification Commands

```bash
cd /Users/NickDuch/Desktop/Ind Designs/NDAAD/RhinoProjects/Latent

# Run boundary extraction tests
python -m pytest tests/test_boundary_extraction.py -v

# Test with actual lens (if evaluator is available)
python -c "
from app.analysis.boundary_extraction import marching_squares
import numpy as np

# Simple test
grid = np.array([[0,0,0],[0.5,0.5,0.5],[1,1,1]])
segments = marching_squares(grid, 0.5, face_id=0)
print(f'Found {len(segments)} segments')
"
```

## Do Not Modify

- `analysis_service/server.py` (Agent 2A's domain)
- `app/analysis/spectral_lens.py` (Agent 2C's domain)
- Files in `cpp_core/`

## Skills to Use

- `superpowers:test-driven-development` - write tests first
- `superpowers:verification-before-completion` - run all tests

## Notes

**Region-to-curve matching**: The current implementation extracts all contour curves but doesn't yet match them to specific regions. This is a TODO for integration - the region discovery needs to identify which curves bound each region.

**Cross-face curves**: Curves may cross face boundaries. The current implementation handles each face independently. Connecting curves across faces would require additional logic to match endpoints at face edges.

## Report

When complete, provide:
1. Test output showing all tests pass
2. Example of extracted contours from a simple test case
3. Any edge cases discovered
