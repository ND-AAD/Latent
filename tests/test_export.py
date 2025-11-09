"""
Test NURBS export validation.

Tests the export pipeline for NURBS mold surfaces to Rhino-compatible format.

Author: Agent 57 (Day 8 Morning)
"""

import pytest
import json
import tempfile
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

# Check if NURBSMoldGenerator is available
if not hasattr(cpp_core, 'NURBSMoldGenerator'):
    pytest.skip("NURBSMoldGenerator not yet implemented", allow_module_level=True)

from app.export.nurbs_serializer import NURBSSerializer, RhinoNURBSSurface
from app.export.rhino_formats import validate_nurbs_data, write_json_export


class TestExport:
    """Test NURBS export validation and serialization."""

    def test_serialize_simple_surface(self):
        """Test serialization of simple NURBS surface."""
        # Create test geometry
        cage = self._create_simple_cage()
        evaluator = cpp_core.SubDEvaluator()
        evaluator.initialize(cage)

        # Generate NURBS
        generator = cpp_core.NURBSMoldGenerator(evaluator)
        nurbs = generator.fit_nurbs_surface([0], sample_density=20)

        # Serialize
        serializer = NURBSSerializer()
        rhino_surf = serializer.serialize_surface(nurbs, name="test_mold")

        # Validate structure
        assert rhino_surf.degree_u > 0, "Degree U should be positive"
        assert rhino_surf.degree_v > 0, "Degree V should be positive"
        assert len(rhino_surf.control_points) > 0, "Should have control points"
        assert len(rhino_surf.weights) == len(rhino_surf.control_points), \
            "Weights count should match control points count"
        assert len(rhino_surf.knots_u) > 0, "Should have U knots"
        assert len(rhino_surf.knots_v) > 0, "Should have V knots"

        print(f"  ✅ Serialized surface: {rhino_surf.count_u}x{rhino_surf.count_v} "
              f"control points, degree ({rhino_surf.degree_u}, {rhino_surf.degree_v})")

    def test_control_points_dimensions(self):
        """Test control points array has correct dimensions."""
        cage = self._create_simple_cage()
        evaluator = cpp_core.SubDEvaluator()
        evaluator.initialize(cage)

        generator = cpp_core.NURBSMoldGenerator(evaluator)
        nurbs = generator.fit_nurbs_surface([0], 20)

        serializer = NURBSSerializer()
        rhino_surf = serializer.serialize_surface(nurbs)

        # Check dimensions match
        expected_count = rhino_surf.count_u * rhino_surf.count_v
        actual_count = len(rhino_surf.control_points)

        assert actual_count == expected_count, \
            f"Control points count mismatch: expected {expected_count}, got {actual_count}"

        # Check each control point is 3D
        for i, pt in enumerate(rhino_surf.control_points):
            assert len(pt) == 3, f"Control point {i} should be 3D tuple"
            assert all(isinstance(c, (int, float)) for c in pt), \
                f"Control point {i} should have numeric coordinates"

        print(f"  ✅ Control points: {actual_count} points, all 3D")

    def test_knot_vector_validity(self):
        """Test knot vector extraction and validation."""
        cage = self._create_simple_cage()
        evaluator = cpp_core.SubDEvaluator()
        evaluator.initialize(cage)

        generator = cpp_core.NURBSMoldGenerator(evaluator)
        nurbs = generator.fit_nurbs_surface([0], 20)

        serializer = NURBSSerializer()
        rhino_surf = serializer.serialize_surface(nurbs)

        # Knot vectors should be non-decreasing
        for i in range(len(rhino_surf.knots_u) - 1):
            assert rhino_surf.knots_u[i] <= rhino_surf.knots_u[i+1], \
                f"U knots not non-decreasing at index {i}"

        for i in range(len(rhino_surf.knots_v) - 1):
            assert rhino_surf.knots_v[i] <= rhino_surf.knots_v[i+1], \
                f"V knots not non-decreasing at index {i}"

        # Check knot vector lengths match expected formula
        # For degree p with n control points: knot vector has n + p + 1 entries
        expected_u_knots = rhino_surf.count_u + rhino_surf.degree_u + 1
        expected_v_knots = rhino_surf.count_v + rhino_surf.degree_v + 1

        assert len(rhino_surf.knots_u) == expected_u_knots, \
            f"U knots count mismatch: expected {expected_u_knots}, got {len(rhino_surf.knots_u)}"
        assert len(rhino_surf.knots_v) == expected_v_knots, \
            f"V knots count mismatch: expected {expected_v_knots}, got {len(rhino_surf.knots_v)}"

        print(f"  ✅ Knot vectors valid: U={len(rhino_surf.knots_u)}, V={len(rhino_surf.knots_v)}")

    def test_weights_validity(self):
        """Test that weights are positive and reasonable."""
        cage = self._create_simple_cage()
        evaluator = cpp_core.SubDEvaluator()
        evaluator.initialize(cage)

        generator = cpp_core.NURBSMoldGenerator(evaluator)
        nurbs = generator.fit_nurbs_surface([0], 20)

        serializer = NURBSSerializer()
        rhino_surf = serializer.serialize_surface(nurbs)

        # All weights should be positive
        for i, w in enumerate(rhino_surf.weights):
            assert w > 0, f"Weight {i} should be positive, got {w}"
            assert w <= 10.0, f"Weight {i} unusually large: {w}"

        print(f"  ✅ Weights valid: {len(rhino_surf.weights)} weights, all positive")

    def test_json_serialization(self):
        """Test conversion to JSON."""
        cage = self._create_simple_cage()
        evaluator = cpp_core.SubDEvaluator()
        evaluator.initialize(cage)

        generator = cpp_core.NURBSMoldGenerator(evaluator)
        nurbs = generator.fit_nurbs_surface([0], 20)

        serializer = NURBSSerializer()
        rhino_surf = serializer.serialize_surface(nurbs, name="test_mold", region_id=1)

        # Convert to dict
        data = rhino_surf.to_dict()

        # Validate structure
        assert validate_nurbs_data(data), "NURBS data validation failed"

        # Check metadata
        assert data['name'] == "test_mold"
        assert data['region_id'] == 1

        # Should be JSON-serializable
        json_str = json.dumps(data)
        assert len(json_str) > 0

        # Round-trip
        recovered = json.loads(json_str)
        assert recovered['degree_u'] == data['degree_u']
        assert recovered['degree_v'] == data['degree_v']
        assert recovered['name'] == data['name']
        assert recovered['region_id'] == data['region_id']

        print(f"  ✅ JSON serialization successful: {len(json_str)} bytes")

    def test_json_file_export(self):
        """Test writing NURBS data to JSON file."""
        cage = self._create_simple_cage()
        evaluator = cpp_core.SubDEvaluator()
        evaluator.initialize(cage)

        generator = cpp_core.NURBSMoldGenerator(evaluator)
        nurbs = generator.fit_nurbs_surface([0], 20)

        serializer = NURBSSerializer()
        rhino_surf = serializer.serialize_surface(nurbs)
        data = rhino_surf.to_dict()

        # Write to temp file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            temp_path = f.name

        try:
            write_json_export(data, temp_path, pretty=True)

            # Read back
            with open(temp_path, 'r') as f:
                loaded = json.load(f)

            # Validate
            assert loaded['degree_u'] == data['degree_u']
            assert loaded['degree_v'] == data['degree_v']
            assert len(loaded['control_points']) == len(data['control_points'])

            print(f"  ✅ File export successful: {temp_path}")
        finally:
            # Clean up
            import os
            if os.path.exists(temp_path):
                os.remove(temp_path)

    def test_mold_set_export(self):
        """Test exporting complete mold set."""
        cage = self._create_simple_cage()
        evaluator = cpp_core.SubDEvaluator()
        evaluator.initialize(cage)

        generator = cpp_core.NURBSMoldGenerator(evaluator)

        # Generate multiple molds (simulating multiple regions)
        molds = [
            (generator.fit_nurbs_surface([0], 20), 1),
            (generator.fit_nurbs_surface([0], 20), 2),
        ]

        serializer = NURBSSerializer()
        export_data = serializer.serialize_mold_set(
            molds,
            metadata={'draft_angle': 2.0, 'wall_thickness': 40.0}
        )

        # Validate structure
        assert export_data['type'] == 'ceramic_mold_set'
        assert 'version' in export_data
        assert export_data['version'] == '1.0'
        assert len(export_data['molds']) == 2
        assert 'metadata' in export_data
        assert export_data['metadata']['draft_angle'] == 2.0
        assert export_data['metadata']['wall_thickness'] == 40.0
        assert 'timestamp' in export_data

        # Check individual molds
        for i, mold_data in enumerate(export_data['molds']):
            assert validate_nurbs_data(mold_data), f"Mold {i} validation failed"
            assert mold_data['region_id'] in [1, 2]

        print(f"  ✅ Mold set export: {len(export_data['molds'])} molds, "
              f"metadata={export_data['metadata']}")

    def test_mold_set_json_export(self):
        """Test complete mold set JSON export."""
        cage = self._create_simple_cage()
        evaluator = cpp_core.SubDEvaluator()
        evaluator.initialize(cage)

        generator = cpp_core.NURBSMoldGenerator(evaluator)

        # Generate mold set
        molds = [
            (generator.fit_nurbs_surface([0], 20), 1),
            (generator.fit_nurbs_surface([0], 20), 2),
        ]

        serializer = NURBSSerializer()
        export_data = serializer.serialize_mold_set(
            molds,
            metadata={
                'draft_angle': 2.0,
                'wall_thickness': 40.0,
                'demolding_direction': [0, 0, 1]
            }
        )

        # Should be JSON-serializable
        json_str = json.dumps(export_data)
        assert len(json_str) > 0

        # Round-trip
        recovered = json.loads(json_str)
        assert recovered['type'] == 'ceramic_mold_set'
        assert len(recovered['molds']) == 2

        print(f"  ✅ Mold set JSON export: {len(json_str)} bytes")

    def test_sphere_export(self):
        """Test export of more complex geometry (sphere)."""
        cage = self._create_sphere()
        evaluator = cpp_core.SubDEvaluator()
        evaluator.initialize(cage)

        generator = cpp_core.NURBSMoldGenerator(evaluator)

        # Use subset of faces for hemisphere
        face_indices = list(range(min(10, len(cage.faces))))
        nurbs = generator.fit_nurbs_surface(face_indices, sample_density=30)

        serializer = NURBSSerializer()
        rhino_surf = serializer.serialize_surface(nurbs, name="hemisphere")

        # Validate
        data = rhino_surf.to_dict()
        assert validate_nurbs_data(data), "Sphere export validation failed"

        # Should have reasonable complexity
        assert rhino_surf.count_u > 2, "Sphere should have multiple U control points"
        assert rhino_surf.count_v > 2, "Sphere should have multiple V control points"

        print(f"  ✅ Sphere export: {rhino_surf.count_u}x{rhino_surf.count_v} control points")

    def test_export_with_draft(self):
        """Test export of drafted surface."""
        cage = self._create_simple_cage()
        evaluator = cpp_core.SubDEvaluator()
        evaluator.initialize(cage)

        generator = cpp_core.NURBSMoldGenerator(evaluator)

        # Generate and apply draft
        nurbs = generator.fit_nurbs_surface([0], 20)
        demolding_dir = cpp_core.Point3D(0, 0, 1)
        drafted = generator.apply_draft_angle(nurbs, demolding_dir, 2.0, [])

        # Export drafted surface
        serializer = NURBSSerializer()
        rhino_surf = serializer.serialize_surface(drafted, name="drafted_mold")
        rhino_surf.draft_angle = 2.0  # Store metadata

        # Validate
        data = rhino_surf.to_dict()
        assert validate_nurbs_data(data), "Drafted surface validation failed"
        assert data['draft_angle'] == 2.0

        print(f"  ✅ Drafted surface export: draft_angle={data['draft_angle']}°")

    def test_validate_nurbs_data_invalid(self):
        """Test that validation catches invalid data."""
        # Missing required field
        invalid_data = {
            'degree_u': 3,
            'degree_v': 3,
            # Missing control_points
            'weights': [1.0],
            'count_u': 4,
            'count_v': 4,
            'knots_u': [0, 0, 0, 0, 1, 1, 1, 1],
            'knots_v': [0, 0, 0, 0, 1, 1, 1, 1]
        }

        assert not validate_nurbs_data(invalid_data), \
            "Should reject data missing required fields"

        # Mismatched dimensions
        invalid_data2 = {
            'degree_u': 3,
            'degree_v': 3,
            'control_points': [(0, 0, 0)] * 10,  # Wrong count
            'weights': [1.0] * 16,
            'count_u': 4,
            'count_v': 4,
            'knots_u': [0, 0, 0, 0, 1, 1, 1, 1],
            'knots_v': [0, 0, 0, 0, 1, 1, 1, 1]
        }

        assert not validate_nurbs_data(invalid_data2), \
            "Should reject data with mismatched dimensions"

        print("  ✅ Validation correctly rejects invalid data")

    # ============================================================
    # Helper Methods
    # ============================================================

    def _create_sphere(self):
        """Create icosahedron (sphere approximation) for SubD."""
        import numpy as np
        phi = (1 + np.sqrt(5)) / 2

        cage = cpp_core.SubDControlCage()
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
        cage.faces = [
            [0, 11, 5], [0, 5, 1], [0, 1, 7], [0, 7, 10], [0, 10, 11],
            [1, 5, 9], [5, 11, 4], [11, 10, 2], [10, 7, 6], [7, 1, 8],
            [3, 9, 4], [3, 4, 2], [3, 2, 6], [3, 6, 8], [3, 8, 9],
            [4, 9, 5], [2, 4, 11], [6, 2, 10], [8, 6, 7], [9, 8, 1]
        ]
        return cage

    def _create_simple_cage(self):
        """Create simple quad cage for basic testing."""
        cage = cpp_core.SubDControlCage()
        cage.vertices = [
            cpp_core.Point3D(0, 0, 0),
            cpp_core.Point3D(1, 0, 0),
            cpp_core.Point3D(1, 1, 0),
            cpp_core.Point3D(0, 1, 0)
        ]
        cage.faces = [[0, 1, 2, 3]]
        return cage


if __name__ == "__main__":
    # Allow running directly with pytest
    pytest.main([__file__, "-v"])
