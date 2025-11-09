#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tests for ParametricRegion and ParametricCurve classes
"""

import sys
import json
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.state.parametric_region import ParametricRegion, ParametricCurve


class TestParametricCurve:
    """Tests for ParametricCurve class"""

    def test_create_empty_curve(self):
        """Test creating an empty curve"""
        curve = ParametricCurve()
        assert curve.points == []
        assert curve.is_closed is False
        assert curve.length_parameter is None
        assert curve.curvature_integral is None

    def test_create_curve_with_points(self):
        """Test creating a curve with points"""
        points = [(0, 0.5, 0.5), (0, 0.6, 0.6), (0, 0.7, 0.7)]
        curve = ParametricCurve(points=points, is_closed=False)
        assert len(curve.points) == 3
        assert curve.points[0] == (0, 0.5, 0.5)
        assert curve.is_closed is False

    def test_evaluate_single_point_curve(self):
        """Test evaluating curve with single point"""
        curve = ParametricCurve(points=[(0, 0.5, 0.5)])
        result = curve.evaluate(0.5)
        assert result == (0, 0.5, 0.5)

    def test_evaluate_multi_point_curve(self):
        """Test evaluating curve with multiple points"""
        points = [(0, 0.0, 0.0), (0, 1.0, 1.0)]
        curve = ParametricCurve(points=points)

        # Start point
        result = curve.evaluate(0.0)
        assert result == (0, 0.0, 0.0)

        # End point
        result = curve.evaluate(1.0)
        assert result[0] == 0
        assert abs(result[1] - 1.0) < 0.01
        assert abs(result[2] - 1.0) < 0.01

        # Midpoint
        result = curve.evaluate(0.5)
        assert result[0] == 0
        assert abs(result[1] - 0.5) < 0.01
        assert abs(result[2] - 0.5) < 0.01

    def test_evaluate_empty_curve_raises_error(self):
        """Test that evaluating empty curve raises error"""
        curve = ParametricCurve()
        try:
            curve.evaluate(0.5)
            assert False, "Expected ValueError"
        except ValueError as e:
            assert "Cannot evaluate empty curve" in str(e)

    def test_curve_to_json(self):
        """Test curve JSON serialization"""
        points = [(0, 0.5, 0.5), (1, 0.6, 0.6)]
        curve = ParametricCurve(
            points=points,
            is_closed=True,
            length_parameter=1.5,
            curvature_integral=0.8
        )

        data = curve.to_json()
        assert data['points'] == points
        assert data['is_closed'] is True
        assert data['length_parameter'] == 1.5
        assert data['curvature_integral'] == 0.8

    def test_curve_from_json(self):
        """Test curve JSON deserialization"""
        data = {
            'points': [[0, 0.5, 0.5], [1, 0.6, 0.6]],
            'is_closed': True,
            'length_parameter': 1.5,
            'curvature_integral': 0.8
        }

        curve = ParametricCurve.from_json(data)
        assert len(curve.points) == 2
        assert curve.points[0] == (0, 0.5, 0.5)
        assert curve.points[1] == (1, 0.6, 0.6)
        assert curve.is_closed is True
        assert curve.length_parameter == 1.5
        assert curve.curvature_integral == 0.8

    def test_curve_json_roundtrip(self):
        """Test that curve survives JSON serialization/deserialization"""
        points = [(0, 0.1, 0.2), (1, 0.3, 0.4), (2, 0.5, 0.6)]
        original = ParametricCurve(points=points, is_closed=False)

        # Serialize and deserialize
        data = original.to_json()
        restored = ParametricCurve.from_json(data)

        assert restored.points == original.points
        assert restored.is_closed == original.is_closed


class TestParametricRegion:
    """Tests for ParametricRegion class"""

    def test_create_minimal_region(self):
        """Test creating a region with minimal parameters"""
        region = ParametricRegion(id="R1", faces=[0, 1, 2])
        assert region.id == "R1"
        assert region.faces == [0, 1, 2]
        assert region.boundary == []
        assert region.unity_principle == ""
        assert region.unity_strength == 0.0
        assert region.pinned is False
        assert region.metadata == {}

    def test_create_full_region(self):
        """Test creating a region with all parameters"""
        curve = ParametricCurve(points=[(0, 0.5, 0.5), (1, 0.6, 0.6)])
        region = ParametricRegion(
            id="R1",
            faces=[0, 1, 2, 3],
            boundary=[curve],
            unity_principle="Curvature",
            unity_strength=0.85,
            pinned=True,
            metadata={"max_curvature": 2.5, "min_curvature": 0.1}
        )

        assert region.id == "R1"
        assert len(region.faces) == 4
        assert len(region.boundary) == 1
        assert region.unity_principle == "Curvature"
        assert region.unity_strength == 0.85
        assert region.pinned is True
        assert region.metadata["max_curvature"] == 2.5

    def test_region_hash(self):
        """Test that regions are hashable by ID"""
        region1 = ParametricRegion(id="R1", faces=[0, 1])
        region2 = ParametricRegion(id="R1", faces=[2, 3])
        region3 = ParametricRegion(id="R2", faces=[0, 1])

        # Same ID should have same hash
        assert hash(region1) == hash(region2)
        # Different ID should have different hash
        assert hash(region1) != hash(region3)

    def test_to_json(self):
        """Test region JSON serialization"""
        curve = ParametricCurve(points=[(0, 0.5, 0.5)])
        region = ParametricRegion(
            id="R1",
            faces=[0, 1, 2],
            boundary=[curve],
            unity_principle="Spectral",
            unity_strength=0.9,
            pinned=True,
            metadata={"eigenvalue": 1.5}
        )

        data = region.to_json()
        assert data['id'] == "R1"
        assert data['faces'] == [0, 1, 2]
        assert len(data['boundary']) == 1
        assert data['unity_principle'] == "Spectral"
        assert data['unity_strength'] == 0.9
        assert data['pinned'] is True
        assert data['metadata']['eigenvalue'] == 1.5

    def test_from_json(self):
        """Test region JSON deserialization"""
        data = {
            'id': "R1",
            'faces': [0, 1, 2],
            'boundary': [
                {'points': [[0, 0.5, 0.5]], 'is_closed': False, 'length_parameter': None, 'curvature_integral': None}
            ],
            'unity_principle': "Spectral",
            'unity_strength': 0.9,
            'pinned': True,
            'metadata': {"eigenvalue": 1.5}
        }

        region = ParametricRegion.from_json(data)
        assert region.id == "R1"
        assert region.faces == [0, 1, 2]
        assert len(region.boundary) == 1
        assert region.unity_principle == "Spectral"
        assert region.unity_strength == 0.9
        assert region.pinned is True
        assert region.metadata['eigenvalue'] == 1.5

    def test_json_roundtrip(self):
        """Test that region survives JSON serialization/deserialization"""
        curve = ParametricCurve(points=[(0, 0.1, 0.2), (1, 0.3, 0.4)])
        original = ParametricRegion(
            id="R1",
            faces=[0, 1, 2, 3],
            boundary=[curve],
            unity_principle="Curvature",
            unity_strength=0.75,
            pinned=False,
            metadata={"test": "value"}
        )

        # Serialize and deserialize
        data = original.to_json()
        restored = ParametricRegion.from_json(data)

        assert restored.id == original.id
        assert restored.faces == original.faces
        assert len(restored.boundary) == len(original.boundary)
        assert restored.unity_principle == original.unity_principle
        assert restored.unity_strength == original.unity_strength
        assert restored.pinned == original.pinned
        assert restored.metadata == original.metadata

    def test_legacy_to_dict_from_dict(self):
        """Test that legacy to_dict/from_dict methods still work"""
        region = ParametricRegion(id="R1", faces=[0, 1], unity_strength=0.5)

        # to_dict should work
        data = region.to_dict()
        assert data['id'] == "R1"

        # from_dict should work
        restored = ParametricRegion.from_dict(data)
        assert restored.id == "R1"
        assert restored.faces == [0, 1]

    def test_contains_point(self):
        """Test point-in-region test"""
        region = ParametricRegion(id="R1", faces=[0, 1, 2])

        # Points in faces that belong to region
        assert region.contains_point(0, 0.5, 0.5) is True
        assert region.contains_point(1, 0.3, 0.7) is True
        assert region.contains_point(2, 0.1, 0.9) is True

        # Points in faces that don't belong to region
        assert region.contains_point(3, 0.5, 0.5) is False
        assert region.contains_point(10, 0.5, 0.5) is False

    def test_compute_area(self):
        """Test area computation"""
        region1 = ParametricRegion(id="R1", faces=[0, 1, 2])
        assert region1.compute_area() == 3.0

        region2 = ParametricRegion(id="R2", faces=[0, 1, 2, 3, 4])
        assert region2.compute_area() == 5.0

        region3 = ParametricRegion(id="R3", faces=[])
        assert region3.compute_area() == 0.0

    def test_merge_basic(self):
        """Test basic region merging"""
        region1 = ParametricRegion(
            id="R1",
            faces=[0, 1, 2],
            unity_principle="Curvature",
            unity_strength=0.8,
            pinned=False
        )

        region2 = ParametricRegion(
            id="R2",
            faces=[3, 4, 5],
            unity_principle="Spectral",
            unity_strength=0.6,
            pinned=False
        )

        merged = region1.merge(region2)

        # Check merged faces (should be union, sorted)
        assert sorted(merged.faces) == [0, 1, 2, 3, 4, 5]

        # Should take stronger unity principle
        assert merged.unity_principle == "Curvature+Spectral"
        assert merged.unity_strength == 0.7  # Average

        # Should be marked as modified
        assert merged.modified is True

    def test_merge_overlapping_faces(self):
        """Test merging regions with overlapping faces"""
        region1 = ParametricRegion(id="R1", faces=[0, 1, 2, 3])
        region2 = ParametricRegion(id="R2", faces=[2, 3, 4, 5])

        merged = region1.merge(region2)

        # Should have unique faces only
        assert sorted(merged.faces) == [0, 1, 2, 3, 4, 5]

    def test_merge_preserves_pinned(self):
        """Test that merging preserves pinned status"""
        region1 = ParametricRegion(id="R1", faces=[0, 1], pinned=True)
        region2 = ParametricRegion(id="R2", faces=[2, 3], pinned=False)

        merged = region1.merge(region2)
        assert merged.pinned is True  # Should preserve if either is pinned

        merged2 = region2.merge(region1)
        assert merged2.pinned is True

    def test_merge_combines_metadata(self):
        """Test that merging combines metadata"""
        region1 = ParametricRegion(
            id="R1",
            faces=[0, 1],
            metadata={"key1": "value1", "shared": "from_r1"}
        )
        region2 = ParametricRegion(
            id="R2",
            faces=[2, 3],
            metadata={"key2": "value2", "shared": "from_r2"}
        )

        merged = region1.merge(region2)

        # Should have both keys
        assert "key1" in merged.metadata
        assert "key2" in merged.metadata
        # Later metadata should override
        assert merged.metadata["shared"] == "from_r2"

    def test_merge_combines_boundaries(self):
        """Test that merging combines boundary curves"""
        curve1 = ParametricCurve(points=[(0, 0.5, 0.5)])
        curve2 = ParametricCurve(points=[(1, 0.6, 0.6)])

        region1 = ParametricRegion(id="R1", faces=[0, 1], boundary=[curve1])
        region2 = ParametricRegion(id="R2", faces=[2, 3], boundary=[curve2])

        merged = region1.merge(region2)
        assert len(merged.boundary) == 2

    def test_get_face_count(self):
        """Test getting face count"""
        region = ParametricRegion(id="R1", faces=[0, 1, 2, 3, 4])
        assert region.get_face_count() == 5

    def test_contains_face(self):
        """Test face containment check"""
        region = ParametricRegion(id="R1", faces=[0, 2, 4, 6])

        assert region.contains_face(0) is True
        assert region.contains_face(2) is True
        assert region.contains_face(4) is True
        assert region.contains_face(6) is True

        assert region.contains_face(1) is False
        assert region.contains_face(3) is False
        assert region.contains_face(5) is False

    def test_get_info(self):
        """Test human-readable info string"""
        region = ParametricRegion(
            id="R1",
            faces=[0, 1, 2],
            unity_principle="Curvature",
            unity_strength=0.85,
            pinned=True
        )

        info = region.get_info()
        assert "R1" in info
        assert "3 faces" in info
        assert "Curvature" in info
        assert "0.85" in info
        assert "Pinned" in info

    def test_parametric_storage(self):
        """Test that regions are truly stored in parameter space, not geometry"""
        # This is a conceptual test - regions should only store:
        # - Face indices (parametric reference)
        # - Boundary curves in (face_id, u, v) space
        # - Metadata
        # NO 3D geometry data!

        curve = ParametricCurve(points=[(0, 0.5, 0.5), (1, 0.6, 0.6)])
        region = ParametricRegion(
            id="R1",
            faces=[0, 1, 2],
            boundary=[curve],
            metadata={"analysis_type": "curvature"}
        )

        # Verify no 3D vertex data is stored
        data = region.to_json()

        # Should only have parametric data
        assert 'faces' in data  # Face indices (parametric)
        assert 'boundary' in data  # Curves in parameter space
        assert 'metadata' in data  # Analysis metadata

        # Should NOT have 3D geometry
        assert 'vertices' not in data
        assert 'points_3d' not in data
        assert 'mesh' not in data

        # Boundary curves should be in parameter space
        for boundary_data in data['boundary']:
            assert 'points' in boundary_data
            # Each point should be (face_id, u, v) - 3 values
            for point in boundary_data['points']:
                assert len(point) == 3
                assert isinstance(point[0], int)  # face_id
                assert isinstance(point[1], (int, float))  # u
                assert isinstance(point[2], (int, float))  # v


def run_all_tests():
    """Run all parametric region tests"""
    print("\n" + "="*60)
    print("RUNNING PARAMETRIC REGION TESTS")
    print("="*60 + "\n")

    # Instantiate test classes
    curve_tests = TestParametricCurve()
    region_tests = TestParametricRegion()

    # Collect all test methods
    tests = []

    # ParametricCurve tests
    for attr_name in dir(curve_tests):
        if attr_name.startswith('test_'):
            tests.append((attr_name, getattr(curve_tests, attr_name)))

    # ParametricRegion tests
    for attr_name in dir(region_tests):
        if attr_name.startswith('test_'):
            tests.append((attr_name, getattr(region_tests, attr_name)))

    passed = 0
    failed = 0

    for test_name, test_func in tests:
        try:
            test_func()
            print(f"✅ {test_name}")
            passed += 1
        except AssertionError as e:
            print(f"❌ {test_name}: {e}")
            failed += 1
        except Exception as e:
            print(f"❌ {test_name}: Unexpected error: {e}")
            failed += 1

    print("\n" + "="*60)
    print(f"RESULTS: {passed} passed, {failed} failed")
    print("="*60 + "\n")

    return failed == 0


if __name__ == '__main__':
    success = run_all_tests()
    sys.exit(0 if success else 1)
