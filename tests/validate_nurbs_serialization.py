#!/usr/bin/env python3
"""
Validation script for NURBS serialization module.

Tests the serialization logic with mock data to verify correctness
without requiring the full cpp_core build.
"""

import json
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.export.nurbs_serializer import NURBSSerializer, RhinoNURBSSurface
from app.export.rhino_formats import validate_nurbs_data, write_json_export


def test_dataclass():
    """Test RhinoNURBSSurface dataclass."""
    print("Testing RhinoNURBSSurface dataclass...")

    surf = RhinoNURBSSurface(
        degree_u=3,
        degree_v=3,
        control_points=[(0.0, 0.0, 0.0), (1.0, 0.0, 0.0), (0.0, 1.0, 0.0), (1.0, 1.0, 0.0)],
        weights=[1.0, 1.0, 1.0, 1.0],
        count_u=2,
        count_v=2,
        knots_u=[0, 0, 0, 0, 1, 1],  # 2 + 3 + 1 = 6
        knots_v=[0, 0, 0, 0, 1, 1],
        name="test_mold",
        region_id=1,
        draft_angle=2.0
    )

    assert surf.degree_u == 3
    assert surf.degree_v == 3
    assert len(surf.control_points) == 4
    assert surf.count_u == 2
    assert surf.count_v == 2

    print("  ✅ RhinoNURBSSurface creation")
    return surf


def test_validation(surf):
    """Test validation logic."""
    print("Testing validation logic...")

    data = surf.to_dict()
    assert validate_nurbs_data(data), "Valid data should pass"
    print("  ✅ Valid data passes validation")

    # Test invalid data
    invalid = data.copy()
    del invalid['degree_u']
    assert not validate_nurbs_data(invalid), "Invalid data should fail"
    print("  ✅ Invalid data fails validation")


def test_json_serialization(surf):
    """Test JSON serialization."""
    print("Testing JSON serialization...")

    data = surf.to_dict()
    json_str = json.dumps(data)
    assert len(json_str) > 0
    print("  ✅ JSON encoding")

    recovered = json.loads(json_str)
    assert recovered['degree_u'] == surf.degree_u
    assert recovered['name'] == surf.name
    print("  ✅ JSON round-trip")


def test_mock_occt_surface():
    """Test serialization with mock OpenCASCADE surface."""
    print("Testing with mock OpenCASCADE surface...")

    class MockNURBSSurface:
        """Mock OpenCASCADE Geom_BSplineSurface."""
        def UDegree(self): return 3
        def VDegree(self): return 3
        def NbUPoles(self): return 2
        def NbVPoles(self): return 2
        def Pole(self, i, j):
            class Point:
                def X(self): return float(i)
                def Y(self): return float(j)
                def Z(self): return 0.0
            return Point()
        def Weight(self, i, j): return 1.0
        def NbUKnots(self): return 2
        def NbVKnots(self): return 2
        def UKnot(self, i): return 0.0 if i == 1 else 1.0
        def VKnot(self, i): return 0.0 if i == 1 else 1.0
        def UMultiplicity(self, i): return 4 if i == 1 else 2  # 4 + 2 = 6
        def VMultiplicity(self, i): return 4 if i == 1 else 2

    serializer = NURBSSerializer()
    mock = MockNURBSSurface()

    rhino_surf = serializer.serialize_surface(mock, name="mock_mold", region_id=1)
    assert rhino_surf.degree_u == 3
    assert rhino_surf.degree_v == 3
    assert len(rhino_surf.control_points) == 4
    assert len(rhino_surf.knots_u) == 6
    assert len(rhino_surf.knots_v) == 6
    print("  ✅ Mock surface serialization")

    # Validate
    data = rhino_surf.to_dict()
    assert validate_nurbs_data(data), "Mock surface should be valid"
    print("  ✅ Mock surface validation")

    return mock


def test_mold_set_export(mock):
    """Test mold set export."""
    print("Testing mold set export...")

    serializer = NURBSSerializer()
    molds = [(mock, 1), (mock, 2), (mock, 3)]

    export_data = serializer.serialize_mold_set(
        molds,
        metadata={'draft_angle': 2.0, 'wall_thickness': 40.0}
    )

    assert export_data['type'] == 'ceramic_mold_set'
    assert export_data['version'] == '1.0'
    assert len(export_data['molds']) == 3
    assert export_data['metadata']['draft_angle'] == 2.0
    print("  ✅ Mold set structure")

    # Validate all molds
    for i, mold_data in enumerate(export_data['molds']):
        assert validate_nurbs_data(mold_data), f"Mold {i+1} should be valid"
    print(f"  ✅ All {len(export_data['molds'])} molds valid")

    # Test JSON export
    json_str = json.dumps(export_data, indent=2)
    assert len(json_str) > 0
    print(f"  ✅ JSON export ({len(json_str)} characters)")

    return export_data


def test_file_write(export_data):
    """Test writing to file."""
    print("Testing file export...")

    import tempfile
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        filepath = f.name

    try:
        write_json_export(export_data, filepath, pretty=True)
        print(f"  ✅ Written to {filepath}")

        # Read back
        with open(filepath, 'r') as f:
            recovered = json.load(f)

        assert recovered['type'] == export_data['type']
        assert len(recovered['molds']) == len(export_data['molds'])
        print("  ✅ File round-trip successful")

    finally:
        Path(filepath).unlink()


def main():
    """Run all validation tests."""
    print("=" * 60)
    print("NURBS Serialization Validation")
    print("=" * 60)
    print()

    try:
        surf = test_dataclass()
        test_validation(surf)
        test_json_serialization(surf)
        mock = test_mock_occt_surface()
        export_data = test_mold_set_export(mock)
        test_file_write(export_data)

        print()
        print("=" * 60)
        print("✅ ALL VALIDATION TESTS PASSED")
        print("=" * 60)
        print()
        print("Module is ready for integration with OpenCASCADE NURBS surfaces.")
        print("Tests will run automatically when cpp_core is built.")

        return 0

    except AssertionError as e:
        print()
        print("=" * 60)
        print(f"❌ VALIDATION FAILED: {e}")
        print("=" * 60)
        return 1
    except Exception as e:
        print()
        print("=" * 60)
        print(f"❌ ERROR: {e}")
        print("=" * 60)
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())
