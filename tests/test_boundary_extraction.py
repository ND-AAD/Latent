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
