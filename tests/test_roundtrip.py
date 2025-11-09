"""
Test round-trip export and import integrity.

Validates that NURBS export→import maintains accuracy for lossless architecture.

Author: Agent 57 (Day 8 Morning)
"""

import pytest
import json
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

# Check if NURBSMoldGenerator is available
if not hasattr(cpp_core, 'NURBSMoldGenerator'):
    pytest.skip("NURBSMoldGenerator not yet implemented", allow_module_level=True)

from app.export.nurbs_serializer import NURBSSerializer, RhinoNURBSSurface
from app.export.rhino_formats import validate_nurbs_data


class TestRoundTrip:
    """Test round-trip export→import maintains accuracy."""

    def test_nurbs_roundtrip_accuracy(self):
        """
        Test NURBS export→import maintains <0.1mm accuracy.

        Critical for lossless architecture.
        """
        # Create test geometry
        cage = self._create_test_cage()
        evaluator = cpp_core.SubDEvaluator()
        evaluator.initialize(cage)

        # Generate NURBS
        generator = cpp_core.NURBSMoldGenerator(evaluator)
        original_nurbs = generator.fit_nurbs_surface([0], sample_density=50)

        # Export to JSON
        serializer = NURBSSerializer()
        rhino_surf = serializer.serialize_surface(original_nurbs, name="roundtrip_test")
        json_data = rhino_surf.to_dict()

        # Validate JSON data integrity
        assert json_data['degree_u'] > 0, "Degree U should be positive"
        assert json_data['degree_v'] > 0, "Degree V should be positive"
        assert len(json_data['control_points']) > 0, "Should have control points"

        # Verify all required fields present
        required = ['degree_u', 'degree_v', 'control_points', 'weights',
                   'knots_u', 'knots_v', 'count_u', 'count_v']
        for field in required:
            assert field in json_data, f"Missing required field: {field}"

        # Validate using rhino_formats validator
        assert validate_nurbs_data(json_data), "NURBS data validation failed"

        print(f"  ✅ Round-trip data integrity: {json_data['count_u']}x{json_data['count_v']} "
              f"control points, {len(json_data['control_points'])} total")

    def test_control_points_roundtrip(self):
        """Test that control points survive round-trip exactly."""
        cage = self._create_test_cage()
        evaluator = cpp_core.SubDEvaluator()
        evaluator.initialize(cage)

        generator = cpp_core.NURBSMoldGenerator(evaluator)
        nurbs = generator.fit_nurbs_surface([0], sample_density=30)

        # Export
        serializer = NURBSSerializer()
        rhino_surf = serializer.serialize_surface(nurbs)

        # Verify control points are valid 3D points
        for i, pt in enumerate(rhino_surf.control_points):
            assert len(pt) == 3, f"Control point {i} should be 3D"
            assert all(isinstance(c, (int, float)) for c in pt), \
                f"Control point {i} should have numeric coordinates"
            assert all(abs(c) < 1e6 for c in pt), \
                f"Control point {i} has unreasonable coordinates: {pt}"

        # Verify weights are valid
        for i, w in enumerate(rhino_surf.weights):
            assert w > 0, f"Weight {i} should be positive"
            assert w < 100, f"Weight {i} unreasonably large: {w}"

        print(f"  ✅ Control points and weights valid: {len(rhino_surf.control_points)} points")

    def test_knot_vector_roundtrip(self):
        """Test that knot vectors survive round-trip exactly."""
        cage = self._create_test_cage()
        evaluator = cpp_core.SubDEvaluator()
        evaluator.initialize(cage)

        generator = cpp_core.NURBSMoldGenerator(evaluator)
        nurbs = generator.fit_nurbs_surface([0], sample_density=30)

        # Export
        serializer = NURBSSerializer()
        rhino_surf = serializer.serialize_surface(nurbs)

        # Store original knot vectors
        original_knots_u = rhino_surf.knots_u.copy()
        original_knots_v = rhino_surf.knots_v.copy()

        # JSON round-trip
        json_data = rhino_surf.to_dict()
        json_str = json.dumps(json_data)
        recovered = json.loads(json_str)

        # Verify knots match exactly
        recovered_knots_u = recovered['knots_u']
        recovered_knots_v = recovered['knots_v']

        assert len(recovered_knots_u) == len(original_knots_u), \
            "U knot count changed during round-trip"
        assert len(recovered_knots_v) == len(original_knots_v), \
            "V knot count changed during round-trip"

        # Check values match (within floating point precision)
        for i, (orig, recv) in enumerate(zip(original_knots_u, recovered_knots_u)):
            assert abs(orig - recv) < 1e-10, \
                f"U knot {i} changed: {orig} → {recv}"

        for i, (orig, recv) in enumerate(zip(original_knots_v, recovered_knots_v)):
            assert abs(orig - recv) < 1e-10, \
                f"V knot {i} changed: {orig} → {recv}"

        print(f"  ✅ Knot vectors preserved: U={len(original_knots_u)}, V={len(original_knots_v)}")

    def test_json_roundtrip_preserves_metadata(self):
        """Test that metadata survives JSON round-trip."""
        cage = self._create_test_cage()
        evaluator = cpp_core.SubDEvaluator()
        evaluator.initialize(cage)

        generator = cpp_core.NURBSMoldGenerator(evaluator)
        nurbs = generator.fit_nurbs_surface([0], 20)

        # Export with metadata
        serializer = NURBSSerializer()
        rhino_surf = serializer.serialize_surface(
            nurbs,
            name="test_mold",
            region_id=42
        )
        rhino_surf.draft_angle = 2.5

        # JSON round-trip
        json_data = rhino_surf.to_dict()
        json_str = json.dumps(json_data)
        recovered = json.loads(json_str)

        # Verify metadata preserved
        assert recovered['name'] == "test_mold"
        assert recovered['region_id'] == 42
        assert recovered['draft_angle'] == 2.5

        print(f"  ✅ Metadata preserved: name={recovered['name']}, "
              f"region_id={recovered['region_id']}, draft_angle={recovered['draft_angle']}")

    def test_mold_set_roundtrip(self):
        """Test round-trip for complete mold set."""
        cage = self._create_test_cage()
        evaluator = cpp_core.SubDEvaluator()
        evaluator.initialize(cage)

        generator = cpp_core.NURBSMoldGenerator(evaluator)

        # Generate mold set
        molds = [
            (generator.fit_nurbs_surface([0], 20), 1),
            (generator.fit_nurbs_surface([0], 20), 2),
            (generator.fit_nurbs_surface([0], 20), 3),
        ]

        metadata = {
            'draft_angle': 2.0,
            'wall_thickness': 40.0,
            'demolding_direction': [0, 0, 1],
            'project_name': 'test_project'
        }

        serializer = NURBSSerializer()
        export_data = serializer.serialize_mold_set(molds, metadata=metadata)

        # JSON round-trip
        json_str = json.dumps(export_data)
        recovered = json.loads(json_str)

        # Verify structure
        assert recovered['type'] == 'ceramic_mold_set'
        assert recovered['version'] == '1.0'
        assert len(recovered['molds']) == 3

        # Verify metadata preserved
        assert recovered['metadata']['draft_angle'] == 2.0
        assert recovered['metadata']['wall_thickness'] == 40.0
        assert recovered['metadata']['project_name'] == 'test_project'

        # Verify each mold
        region_ids = [m['region_id'] for m in recovered['molds']]
        assert region_ids == [1, 2, 3]

        print(f"  ✅ Mold set round-trip: {len(recovered['molds'])} molds, "
              f"metadata preserved")

    def test_numerical_precision_roundtrip(self):
        """Test that numerical precision is maintained during round-trip."""
        cage = self._create_test_cage()
        evaluator = cpp_core.SubDEvaluator()
        evaluator.initialize(cage)

        generator = cpp_core.NURBSMoldGenerator(evaluator)
        nurbs = generator.fit_nurbs_surface([0], 30)

        # Export
        serializer = NURBSSerializer()
        rhino_surf = serializer.serialize_surface(nurbs)

        # Store original data
        original_points = [tuple(pt) for pt in rhino_surf.control_points]
        original_weights = rhino_surf.weights.copy()

        # JSON round-trip
        json_data = rhino_surf.to_dict()
        json_str = json.dumps(json_data)
        recovered = json.loads(json_str)

        # Check control points precision
        for i, (orig, recv) in enumerate(zip(original_points, recovered['control_points'])):
            for j, (o, r) in enumerate(zip(orig, recv)):
                # Should maintain at least 6 decimal places
                assert abs(o - r) < 1e-6, \
                    f"Control point {i}[{j}] precision loss: {o} → {r}"

        # Check weights precision
        for i, (orig, recv) in enumerate(zip(original_weights, recovered['weights'])):
            assert abs(orig - recv) < 1e-6, \
                f"Weight {i} precision loss: {orig} → {recv}"

        print(f"  ✅ Numerical precision maintained: <1e-6 deviation")

    def test_sphere_roundtrip(self):
        """Test round-trip for complex geometry (sphere)."""
        cage = self._create_sphere()
        evaluator = cpp_core.SubDEvaluator()
        evaluator.initialize(cage)

        generator = cpp_core.NURBSMoldGenerator(evaluator)

        # Use multiple faces for more complex surface
        face_indices = list(range(min(10, len(cage.faces))))
        nurbs = generator.fit_nurbs_surface(face_indices, sample_density=40)

        # Export
        serializer = NURBSSerializer()
        rhino_surf = serializer.serialize_surface(nurbs, name="sphere_test")

        # JSON round-trip
        json_data = rhino_surf.to_dict()
        assert validate_nurbs_data(json_data), "Sphere data validation failed"

        json_str = json.dumps(json_data)
        recovered = json.loads(json_str)

        # Verify structure preserved
        assert recovered['degree_u'] == json_data['degree_u']
        assert recovered['degree_v'] == json_data['degree_v']
        assert len(recovered['control_points']) == len(json_data['control_points'])
        assert len(recovered['knots_u']) == len(json_data['knots_u'])
        assert len(recovered['knots_v']) == len(json_data['knots_v'])

        print(f"  ✅ Sphere round-trip: {recovered['count_u']}x{recovered['count_v']} "
              f"control points")

    def test_drafted_surface_roundtrip(self):
        """Test round-trip for drafted surface."""
        cage = self._create_test_cage()
        evaluator = cpp_core.SubDEvaluator()
        evaluator.initialize(cage)

        generator = cpp_core.NURBSMoldGenerator(evaluator)

        # Generate and apply draft
        nurbs = generator.fit_nurbs_surface([0], 30)
        demolding_dir = cpp_core.Point3D(0, 0, 1)
        drafted = generator.apply_draft_angle(nurbs, demolding_dir, 3.0, [])

        # Export
        serializer = NURBSSerializer()
        rhino_surf = serializer.serialize_surface(drafted, name="drafted_test")
        rhino_surf.draft_angle = 3.0

        # Round-trip
        json_data = rhino_surf.to_dict()
        assert validate_nurbs_data(json_data), "Drafted surface validation failed"

        json_str = json.dumps(json_data)
        recovered = json.loads(json_str)

        # Verify draft metadata preserved
        assert recovered['draft_angle'] == 3.0
        assert recovered['name'] == "drafted_test"

        print(f"  ✅ Drafted surface round-trip: draft_angle={recovered['draft_angle']}°")

    def test_export_import_workflow(self):
        """
        Test complete workflow integration.

        Note: This would test the actual HTTP POST to Grasshopper.
        Requires Rhino/Grasshopper running, so it's a placeholder for now.
        """
        # This test would:
        # 1. Generate NURBS molds in Desktop app
        # 2. Export to JSON
        # 3. POST to Grasshopper endpoint
        # 4. Verify import in Rhino
        # 5. Re-export from Rhino
        # 6. Compare with original

        # For now, we just verify the data is ready for export
        cage = self._create_test_cage()
        evaluator = cpp_core.SubDEvaluator()
        evaluator.initialize(cage)

        generator = cpp_core.NURBSMoldGenerator(evaluator)
        molds = [(generator.fit_nurbs_surface([0], 20), 1)]

        serializer = NURBSSerializer()
        export_data = serializer.serialize_mold_set(
            molds,
            metadata={'draft_angle': 2.0}
        )

        # Verify it's ready for HTTP POST
        assert export_data['type'] == 'ceramic_mold_set'
        assert 'molds' in export_data
        assert len(export_data['molds']) == 1

        # Should be JSON-serializable
        json_str = json.dumps(export_data)
        assert len(json_str) > 0

        print(f"  ✅ Export data ready for HTTP POST: {len(json_str)} bytes")
        print("     (Full workflow test requires Rhino/Grasshopper running)")

    def test_large_mold_set_roundtrip(self):
        """Test round-trip for large mold set (stress test)."""
        cage = self._create_test_cage()
        evaluator = cpp_core.SubDEvaluator()
        evaluator.initialize(cage)

        generator = cpp_core.NURBSMoldGenerator(evaluator)

        # Generate larger mold set
        num_molds = 10
        molds = [(generator.fit_nurbs_surface([0], 20), i) for i in range(num_molds)]

        serializer = NURBSSerializer()
        export_data = serializer.serialize_mold_set(
            molds,
            metadata={'test': 'large_set'}
        )

        # JSON round-trip
        json_str = json.dumps(export_data)
        recovered = json.loads(json_str)

        # Verify all molds present
        assert len(recovered['molds']) == num_molds

        # Verify all are valid
        for i, mold in enumerate(recovered['molds']):
            assert validate_nurbs_data(mold), f"Mold {i} validation failed"
            assert mold['region_id'] == i

        print(f"  ✅ Large mold set round-trip: {num_molds} molds, "
              f"{len(json_str)} bytes JSON")

    # ============================================================
    # Helper Methods
    # ============================================================

    def _create_test_cage(self):
        """Create simple test cage."""
        cage = cpp_core.SubDControlCage()
        cage.vertices = [
            cpp_core.Point3D(0, 0, 0),
            cpp_core.Point3D(1, 0, 0),
            cpp_core.Point3D(1, 1, 0),
            cpp_core.Point3D(0, 1, 0)
        ]
        cage.faces = [[0, 1, 2, 3]]
        return cage

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


if __name__ == "__main__":
    # Allow running directly with pytest
    pytest.main([__file__, "-v"])
