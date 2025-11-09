"""
Test NURBS Serialization for Rhino Export

Tests serialization of OpenCASCADE NURBS surfaces to Rhino-compatible format.
"""

import pytest
import json
import sys

# Try to import cpp_core
try:
    import cpp_core
    # Check if NURBSMoldGenerator is available
    if not hasattr(cpp_core, 'NURBSMoldGenerator'):
        pytest.skip("NURBSMoldGenerator not yet implemented - build cpp_core first", allow_module_level=True)
except ImportError:
    pytest.skip("cpp_core module not available - build cpp_core first", allow_module_level=True)

from app.export.nurbs_serializer import NURBSSerializer, RhinoNURBSSurface
from app.export.rhino_formats import validate_nurbs_data


class TestNURBSExport:
    """Test NURBS serialization for Rhino export."""

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
        assert rhino_surf.degree_u > 0
        assert rhino_surf.degree_v > 0
        assert len(rhino_surf.control_points) > 0
        assert len(rhino_surf.weights) == len(rhino_surf.control_points)
        assert len(rhino_surf.knots_u) > 0
        assert len(rhino_surf.knots_v) > 0

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
        assert all(rhino_surf.knots_u[i] <= rhino_surf.knots_u[i+1]
                  for i in range(len(rhino_surf.knots_u) - 1))
        assert all(rhino_surf.knots_v[i] <= rhino_surf.knots_v[i+1]
                  for i in range(len(rhino_surf.knots_v) - 1))

    def test_json_serialization(self):
        """Test conversion to JSON."""
        cage = self._create_simple_cage()
        evaluator = cpp_core.SubDEvaluator()
        evaluator.initialize(cage)

        generator = cpp_core.NURBSMoldGenerator(evaluator)
        nurbs = generator.fit_nurbs_surface([0], 20)

        serializer = NURBSSerializer()
        rhino_surf = serializer.serialize_surface(nurbs)

        # Convert to dict
        data = rhino_surf.to_dict()

        # Validate
        assert validate_nurbs_data(data)

        # Should be JSON-serializable
        json_str = json.dumps(data)
        assert len(json_str) > 0

        # Round-trip
        recovered = json.loads(json_str)
        assert recovered['degree_u'] == data['degree_u']
        assert recovered['degree_v'] == data['degree_v']

    def test_mold_set_export(self):
        """Test exporting complete mold set."""
        cage = self._create_simple_cage()
        evaluator = cpp_core.SubDEvaluator()
        evaluator.initialize(cage)

        generator = cpp_core.NURBSMoldGenerator(evaluator)

        # Generate multiple molds
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
        assert len(export_data['molds']) == 2
        assert 'metadata' in export_data
        assert export_data['metadata']['draft_angle'] == 2.0

    def _create_simple_cage(self):
        cage = cpp_core.SubDControlCage()
        cage.vertices = [
            cpp_core.Point3D(0, 0, 0),
            cpp_core.Point3D(1, 0, 0),
            cpp_core.Point3D(1, 1, 0),
            cpp_core.Point3D(0, 1, 0)
        ]
        cage.faces = [[0, 1, 2, 3]]
        return cage


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
