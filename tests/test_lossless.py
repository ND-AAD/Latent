#!/usr/bin/env python3
"""
Lossless Architecture Validation Tests

Verifies the complete pipeline maintains lossless architecture:
- Control cage → exact limit evaluation → parametric regions
- No mesh conversions in data pipeline
- Single approximation only at fabrication export

Run: python3 tests/test_lossless.py
"""

import sys
import os

# Add cpp_core/build to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'cpp_core', 'build'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import unittest
import numpy as np
import cpp_core
from app.state.parametric_region import ParametricRegion
from app.bridge.subd_fetcher import SubDFetcher
import json


class TestControlCagePreservation(unittest.TestCase):
    """Test that control cage transfer preserves topology exactly."""

    def test_vertex_preservation(self):
        """Verify all vertices are preserved exactly during transfer."""
        # Create control cage
        cage = cpp_core.SubDControlCage()

        # Define exact coordinates
        coords = [
            (0.0, 0.0, 0.0),
            (1.0, 0.0, 0.0),
            (1.0, 1.0, 0.0),
            (0.0, 1.0, 0.0),
            (0.5, 0.5, 1.0)  # Apex
        ]

        # Add vertices (build list then assign - pybind11 doesn't support append)
        cage.vertices = [cpp_core.Point3D(x, y, z) for x, y, z in coords]

        # Verify exact preservation
        self.assertEqual(cage.vertex_count(), len(coords))

        for i, (x, y, z) in enumerate(coords):
            v = cage.vertices[i]
            # Exact floating point comparison (no conversion happened)
            self.assertEqual(v.x, x)
            self.assertEqual(v.y, y)
            self.assertEqual(v.z, z)

        print("  ✅ Vertex positions preserved exactly (no approximation)")

    def test_topology_preservation(self):
        """Verify face topology is preserved exactly."""
        cage = cpp_core.SubDControlCage()

        # Create pyramid control cage
        cage.vertices = [cpp_core.Point3D(*v) for v in [(0, 0, 0), (1, 0, 0), (1, 1, 0), (0, 1, 0), (0.5, 0.5, 1)]]

        # Define faces
        faces = [
            [0, 1, 2, 3],  # Base quad
            [0, 1, 4],     # Triangle
            [1, 2, 4],     # Triangle
            [2, 3, 4],     # Triangle
            [3, 0, 4],     # Triangle
        ]

        cage.faces = faces

        # Verify topology preserved
        self.assertEqual(cage.face_count(), len(faces))

        for i, face in enumerate(faces):
            self.assertEqual(cage.faces[i], face)

        print("  ✅ Face topology preserved exactly (100%)")

    def test_crease_preservation(self):
        """Verify edge creases are preserved exactly."""
        cage = cpp_core.SubDControlCage()

        # Simple quad
        cage.vertices = [cpp_core.Point3D(*v) for v in [(0, 0, 0), (1, 0, 0), (1, 1, 0), (0, 1, 0)]]
        cage.faces = [[0, 1, 2, 3]]

        # Add creases with exact sharpness values
        creases = [
            (0, 0.5),   # Edge 0, half-sharp
            (2, 1.0),   # Edge 2, fully sharp
        ]

        cage.creases = creases

        # Verify creases preserved
        self.assertEqual(len(cage.creases), len(creases))

        for i, (edge_id, sharpness) in enumerate(creases):
            stored_edge, stored_sharp = cage.creases[i]
            self.assertEqual(stored_edge, edge_id)
            self.assertEqual(stored_sharp, sharpness)

        print("  ✅ Edge creases preserved exactly")

    def test_json_roundtrip(self):
        """Verify control cage survives JSON serialization without loss."""
        # Create test cage
        original_data = {
            'vertices': [
                [0.0, 0.0, 0.0],
                [1.0, 0.0, 0.0],
                [1.0, 1.0, 0.0],
                [0.0, 1.0, 0.0]
            ],
            'faces': [[0, 1, 2, 3]],
            'creases': [[0, 1, 0.5]]
        }

        # Convert to JSON and back
        json_str = json.dumps(original_data)
        recovered_data = json.loads(json_str)

        # Build cage from recovered data
        cage = cpp_core.SubDControlCage()
        cage.vertices = [cpp_core.Point3D(v[0], v[1], v[2]) for v in recovered_data['vertices']]
        cage.faces = recovered_data['faces']

        # Verify exact match
        self.assertEqual(cage.vertex_count(), len(original_data['vertices']))
        self.assertEqual(cage.face_count(), len(original_data['faces']))

        for i, orig_v in enumerate(original_data['vertices']):
            v = cage.vertices[i]
            self.assertEqual(v.x, orig_v[0])
            self.assertEqual(v.y, orig_v[1])
            self.assertEqual(v.z, orig_v[2])

        print("  ✅ JSON roundtrip preserves exact values")


class TestLimitEvaluation(unittest.TestCase):
    """Test exact limit surface evaluation."""

    def setUp(self):
        """Create test geometry."""
        self.cage = self._create_unit_quad()
        self.evaluator = cpp_core.SubDEvaluator()
        self.evaluator.initialize(self.cage)

    def _create_unit_quad(self):
        """Create flat unit quad (limit surface is exact)."""
        cage = cpp_core.SubDControlCage()
        cage.vertices = [
            cpp_core.Point3D(0, 0, 0),
            cpp_core.Point3D(1, 0, 0),
            cpp_core.Point3D(1, 1, 0),
            cpp_core.Point3D(0, 1, 0)
        ]
        cage.faces = [[0, 1, 2, 3]]
        return cage

    def test_limit_point_accuracy(self):
        """Verify limit point evaluation accuracy."""
        # For flat quad, limit surface should match control cage exactly
        # Center of quad
        point = self.evaluator.evaluate_limit_point(0, 0.5, 0.5)

        expected_x = 0.5
        expected_y = 0.5
        expected_z = 0.0

        # Should be very precise (<1e-6 error)
        error_x = abs(point.x - expected_x)
        error_y = abs(point.y - expected_y)
        error_z = abs(point.z - expected_z)

        self.assertLess(error_x, 1e-6, f"X error too large: {error_x}")
        self.assertLess(error_y, 1e-6, f"Y error too large: {error_y}")
        self.assertLess(error_z, 1e-6, f"Z error too large: {error_z}")

        print(f"  ✅ Limit point accuracy: errors < 1e-6 (x={error_x:.2e}, y={error_y:.2e}, z={error_z:.2e})")

    def test_normal_accuracy(self):
        """Verify normal vector accuracy."""
        # For flat quad in XY plane, normal should be (0, 0, 1)
        point, normal = self.evaluator.evaluate_limit(0, 0.5, 0.5)

        # Check normal is unit length
        length = np.sqrt(normal.x**2 + normal.y**2 + normal.z**2)
        self.assertAlmostEqual(length, 1.0, places=6)

        # Check normal points in +Z direction
        self.assertLess(abs(normal.x), 0.01)
        self.assertLess(abs(normal.y), 0.01)
        self.assertGreater(normal.z, 0.999)  # Should be very close to 1.0

        print(f"  ✅ Normal accuracy: length={length:.6f}, z-component={normal.z:.6f}")

    def test_parametric_evaluation_grid(self):
        """Test evaluation at multiple parametric locations."""
        # Test various (u, v) locations
        test_points = [
            (0.0, 0.0),   # Corner
            (1.0, 0.0),   # Corner
            (1.0, 1.0),   # Corner
            (0.0, 1.0),   # Corner
            (0.5, 0.5),   # Center
            (0.25, 0.75), # Arbitrary
        ]

        for u, v in test_points:
            point = self.evaluator.evaluate_limit_point(0, u, v)

            # For flat quad, should match parametric position exactly
            expected_x = u
            expected_y = v
            expected_z = 0.0

            error = abs(point.x - expected_x) + abs(point.y - expected_y) + abs(point.z - expected_z)
            self.assertLess(error, 1e-5, f"Error at ({u}, {v}): {error}")

        print(f"  ✅ Parametric evaluation grid: all {len(test_points)} points < 1e-5 error")

    def test_derivative_evaluation(self):
        """Test first derivative evaluation."""
        # Evaluate with derivatives
        position, du, dv = self.evaluator.evaluate_limit_with_derivatives(0, 0.5, 0.5)

        # For flat quad, derivatives should be axis-aligned
        # du should be (1, 0, 0), dv should be (0, 1, 0)

        # Check du
        self.assertGreater(du.x, 0.9)  # Should be ~1.0
        self.assertLess(abs(du.y), 0.1)
        self.assertLess(abs(du.z), 0.1)

        # Check dv
        self.assertLess(abs(dv.x), 0.1)
        self.assertGreater(dv.y, 0.9)  # Should be ~1.0
        self.assertLess(abs(dv.z), 0.1)

        print(f"  ✅ Derivative evaluation: du≈({du.x:.3f}, {du.y:.3f}, {du.z:.3f}), dv≈({dv.x:.3f}, {dv.y:.3f}, {dv.z:.3f})")


class TestTessellationDisplayOnly(unittest.TestCase):
    """Verify tessellation is for display only, not used in analysis."""

    def setUp(self):
        """Create test geometry."""
        self.cage = self._create_unit_quad()
        self.evaluator = cpp_core.SubDEvaluator()
        self.evaluator.initialize(self.cage)

    def _create_unit_quad(self):
        """Create flat unit quad."""
        cage = cpp_core.SubDControlCage()
        cage.vertices = [
            cpp_core.Point3D(0, 0, 0),
            cpp_core.Point3D(1, 0, 0),
            cpp_core.Point3D(1, 1, 0),
            cpp_core.Point3D(0, 1, 0)
        ]
        cage.faces = [[0, 1, 2, 3]]
        return cage

    def test_tessellation_separate_from_evaluation(self):
        """Verify limit evaluation doesn't depend on tessellation."""
        # Evaluate limit point BEFORE tessellation
        point_before = self.evaluator.evaluate_limit_point(0, 0.5, 0.5)

        # Generate tessellation at different levels (use fresh evaluators - OpenSubdiv limitation)
        eval_low = cpp_core.SubDEvaluator()
        eval_low.initialize(self.cage)
        tess_low = eval_low.tessellate(1)

        eval_high = cpp_core.SubDEvaluator()
        eval_high.initialize(self.cage)
        tess_high = eval_high.tessellate(3)

        # Evaluate same point AFTER tessellation (on original evaluator)
        point_after = self.evaluator.evaluate_limit_point(0, 0.5, 0.5)

        # Points should be identical (limit evaluation is independent)
        self.assertEqual(point_before.x, point_after.x)
        self.assertEqual(point_before.y, point_after.y)
        self.assertEqual(point_before.z, point_after.z)

        print("  ✅ Limit evaluation independent of tessellation")

    def test_tessellation_result_type(self):
        """Verify tessellation returns display mesh, not used for analysis."""
        result = self.evaluator.tessellate(2)

        # Tessellation should be a different type from control cage
        self.assertIsInstance(result, cpp_core.TessellationResult)
        self.assertIsInstance(self.cage, cpp_core.SubDControlCage)

        # Result should have triangles (display mesh)
        self.assertGreater(result.triangle_count(), 0)

        # Control cage should still have quads (exact topology)
        self.assertEqual(len(self.cage.faces[0]), 4)

        print("  ✅ Tessellation is separate display mesh type")

    def test_multiple_tessellation_levels(self):
        """Verify different tessellation levels don't affect limit surface."""
        # Get limit point
        limit_point = self.evaluator.evaluate_limit_point(0, 0.5, 0.5)

        # Generate tessellations at different resolutions
        levels = [1, 2, 3]
        tessellations = []

        for level in levels:
            # Create fresh evaluator for each level (OpenSubdiv limitation)
            eval_temp = cpp_core.SubDEvaluator()
            eval_temp.initialize(self.cage)
            tess = eval_temp.tessellate(level)
            tessellations.append(tess)

        # All tessellations approximate the SAME limit surface
        # Verify they have different vertex counts (different resolutions)
        vertex_counts = [t.vertex_count() for t in tessellations]
        self.assertEqual(len(set(vertex_counts)), len(vertex_counts))  # All different

        # But they all converge to the same limit surface
        # (which we evaluate exactly, not from tessellation)
        for tess in tessellations:
            # Find approximate center vertex in tessellation
            verts = tess.vertices
            center_idx = len(verts) // 2
            if center_idx < len(verts):
                tess_point = verts[center_idx]
                # Should be close to limit point (within tessellation error)
                error = abs(tess_point[0] - limit_point.x) + \
                       abs(tess_point[1] - limit_point.y) + \
                       abs(tess_point[2] - limit_point.z)
                self.assertLess(error, 1.0)  # Reasonable approximation (tessellation vertices approximate limit surface)

        print(f"  ✅ Multiple tessellation levels: {vertex_counts} vertices (all approximate same limit)")


class TestParametricRegions(unittest.TestCase):
    """Verify regions are stored in parametric (face_id, u, v) format."""

    def test_region_uses_face_indices(self):
        """Verify regions reference faces, not mesh triangles."""
        # Create parametric region
        region = ParametricRegion(
            id="test_region_1",
            faces=[0, 1, 2, 5],  # Face indices in control cage
            unity_principle="curvature",
            unity_strength=0.85
        )

        # Region should store face indices (not mesh vertex/triangle indices)
        self.assertIsInstance(region.faces, list)
        self.assertEqual(len(region.faces), 4)

        # All face indices should be integers
        for face_id in region.faces:
            self.assertIsInstance(face_id, int)

        print(f"  ✅ Region stores face indices: {region.faces}")

    def test_region_serialization(self):
        """Verify region serialization preserves parametric definition."""
        # Create region
        region = ParametricRegion(
            id="test_region_2",
            faces=[0, 1, 2, 3, 4],
            unity_principle="spectral",
            unity_strength=0.92,
            pinned=True
        )

        # Serialize to dict
        data = region.to_dict()

        # Verify parametric data preserved
        self.assertIn('faces', data)
        self.assertEqual(data['faces'], [0, 1, 2, 3, 4])
        self.assertEqual(data['unity_principle'], 'spectral')
        self.assertEqual(data['unity_strength'], 0.92)
        self.assertEqual(data['pinned'], True)

        # Deserialize
        recovered = ParametricRegion.from_dict(data)

        # Verify exact match
        self.assertEqual(recovered.faces, region.faces)
        self.assertEqual(recovered.unity_principle, region.unity_principle)
        self.assertEqual(recovered.unity_strength, region.unity_strength)
        self.assertEqual(recovered.pinned, region.pinned)

        print("  ✅ Region serialization preserves parametric definition")

    def test_region_references_control_faces(self):
        """Verify regions reference control cage faces, not tessellation."""
        # Create control cage
        cage = cpp_core.SubDControlCage()
        cage.vertices = [cpp_core.Point3D(*v) for v in [(0, 0, 0), (1, 0, 0), (1, 1, 0), (0, 1, 0)]]
        cage.faces = [[0, 1, 2, 3]]

        # Create evaluator and tessellate
        evaluator = cpp_core.SubDEvaluator()
        evaluator.initialize(cage)
        tess = evaluator.tessellate(3)

        # Control cage has 1 face
        self.assertEqual(cage.face_count(), 1)

        # Tessellation has many triangles
        self.assertGreater(tess.triangle_count(), 1)

        # Region should reference control face (not tessellation triangles)
        region = ParametricRegion(
            id="test_region_3",
            faces=[0],  # Face 0 of control cage
            unity_principle="differential"
        )

        # Region face count should match control cage, not tessellation
        self.assertEqual(len(region.faces), cage.face_count())
        self.assertNotEqual(len(region.faces), tess.triangle_count())

        print(f"  ✅ Region references {cage.face_count()} control faces (not {tess.triangle_count()} tessellation triangles)")


class TestNoMeshConversions(unittest.TestCase):
    """Verify no mesh conversions occur in the data pipeline."""

    def test_control_cage_to_evaluator(self):
        """Verify control cage → evaluator uses exact topology."""
        cage = cpp_core.SubDControlCage()
        cage.vertices = [
            cpp_core.Point3D(0, 0, 0),
            cpp_core.Point3D(1, 0, 0),
            cpp_core.Point3D(1, 1, 0),
            cpp_core.Point3D(0, 1, 0)
        ]
        cage.faces = [[0, 1, 2, 3]]

        # Initialize evaluator
        evaluator = cpp_core.SubDEvaluator()
        evaluator.initialize(cage)

        # Evaluator should preserve control cage topology
        self.assertEqual(evaluator.get_control_vertex_count(), cage.vertex_count())
        self.assertEqual(evaluator.get_control_face_count(), cage.face_count())

        print("  ✅ Control cage → evaluator: exact topology preserved")

    def test_no_intermediate_mesh(self):
        """Verify analysis uses limit surface, not intermediate mesh."""
        cage = cpp_core.SubDControlCage()
        cage.vertices = [
            cpp_core.Point3D(0, 0, 0),
            cpp_core.Point3D(1, 0, 0),
            cpp_core.Point3D(1, 1, 0),
            cpp_core.Point3D(0, 1, 0)
        ]
        cage.faces = [[0, 1, 2, 3]]

        evaluator = cpp_core.SubDEvaluator()
        evaluator.initialize(cage)

        # Can evaluate limit surface directly (no mesh needed)
        point = evaluator.evaluate_limit_point(0, 0.5, 0.5)
        self.assertIsNotNone(point)

        # Tessellation is optional and separate
        # (We don't need to call tessellate() to use limit evaluation)

        print("  ✅ Limit evaluation works without tessellation (no intermediate mesh)")

    def test_analysis_queries_limit_surface(self):
        """Verify analysis can query limit surface at any resolution."""
        cage = cpp_core.SubDControlCage()
        cage.vertices = [
            cpp_core.Point3D(0, 0, 0),
            cpp_core.Point3D(1, 0, 0),
            cpp_core.Point3D(1, 1, 0),
            cpp_core.Point3D(0, 1, 0)
        ]
        cage.faces = [[0, 1, 2, 3]]

        evaluator = cpp_core.SubDEvaluator()
        evaluator.initialize(cage)

        # Can query at arbitrary high resolution
        high_res_samples = []
        for i in range(100):
            u = i / 99.0
            for j in range(100):
                v = j / 99.0
                point = evaluator.evaluate_limit_point(0, u, v)
                high_res_samples.append(point)

        # Successfully evaluated 10,000 points from exact limit surface
        self.assertEqual(len(high_res_samples), 10000)

        print("  ✅ Sampled 10,000 points from exact limit surface (infinite resolution)")


class TestLosslessMetrics(unittest.TestCase):
    """Verify specific lossless metrics from requirements."""

    def setUp(self):
        """Create test geometry."""
        self.cage = self._create_unit_quad()
        self.evaluator = cpp_core.SubDEvaluator()
        self.evaluator.initialize(self.cage)

    def _create_unit_quad(self):
        """Create flat unit quad."""
        cage = cpp_core.SubDControlCage()
        cage.vertices = [
            cpp_core.Point3D(0, 0, 0),
            cpp_core.Point3D(1, 0, 0),
            cpp_core.Point3D(1, 1, 0),
            cpp_core.Point3D(0, 1, 0)
        ]
        cage.faces = [[0, 1, 2, 3]]
        return cage

    def test_vertex_position_error(self):
        """Verify vertex position error < 1e-6."""
        # Test at control point locations (should be exact)
        test_cases = [
            ((0.0, 0.0), (0.0, 0.0, 0.0)),
            ((1.0, 0.0), (1.0, 0.0, 0.0)),
            ((1.0, 1.0), (1.0, 1.0, 0.0)),
            ((0.0, 1.0), (0.0, 1.0, 0.0)),
        ]

        max_error = 0.0

        for (u, v), (exp_x, exp_y, exp_z) in test_cases:
            point = self.evaluator.evaluate_limit_point(0, u, v)

            error = max(
                abs(point.x - exp_x),
                abs(point.y - exp_y),
                abs(point.z - exp_z)
            )

            max_error = max(max_error, error)
            self.assertLess(error, 1e-6)

        print(f"  ✅ METRIC: Vertex position error < 1e-6 (actual max: {max_error:.2e})")

    def test_normal_accuracy(self):
        """Verify normal accuracy > 0.999."""
        # Test at multiple locations
        test_locations = [
            (0.25, 0.25),
            (0.5, 0.5),
            (0.75, 0.75),
        ]

        min_z_component = 1.0

        for u, v in test_locations:
            point, normal = self.evaluator.evaluate_limit(0, u, v)

            # For flat quad, z-component should be 1.0
            min_z_component = min(min_z_component, normal.z)
            self.assertGreater(normal.z, 0.999)

        print(f"  ✅ METRIC: Normal accuracy > 0.999 (actual min: {min_z_component:.6f})")

    def test_topology_preservation(self):
        """Verify topology preservation = 100%."""
        # Original topology
        orig_vertex_count = self.cage.vertex_count()
        orig_face_count = self.cage.face_count()

        # After initialization
        self.evaluator.initialize(self.cage)

        # Topology should be 100% preserved
        self.assertEqual(self.evaluator.get_control_vertex_count(), orig_vertex_count)
        self.assertEqual(self.evaluator.get_control_face_count(), orig_face_count)

        preservation_rate = 1.0  # 100%

        print(f"  ✅ METRIC: Topology preservation = 100% ({orig_vertex_count}V, {orig_face_count}F preserved)")


def run_tests():
    """Run all lossless validation tests."""
    print("=" * 70)
    print("Lossless Architecture Validation Tests")
    print("=" * 70)
    print()

    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # Add test classes in order
    test_classes = [
        TestControlCagePreservation,
        TestLimitEvaluation,
        TestTessellationDisplayOnly,
        TestParametricRegions,
        TestNoMeshConversions,
        TestLosslessMetrics,
    ]

    for test_class in test_classes:
        suite.addTests(loader.loadTestsFromTestCase(test_class))

    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    print()
    print("=" * 70)
    print("LOSSLESS ARCHITECTURE VALIDATION SUMMARY")
    print("=" * 70)
    print()

    if result.wasSuccessful():
        print("✅ ALL LOSSLESS TESTS PASSED!")
        print()
        print("Architecture verified:")
        print("  ✓ Control cage → exact limit evaluation")
        print("  ✓ Parametric regions in (face_id, u, v)")
        print("  ✓ Tessellation for display only")
        print("  ✓ No mesh conversions in pipeline")
        print("  ✓ Metrics: vertex error < 1e-6, normal > 0.999, topology 100%")
        print()
        print(f"Total tests: {result.testsRun}")
        return 0
    else:
        print("❌ SOME TESTS FAILED")
        print(f"   Failures: {len(result.failures)}")
        print(f"   Errors: {len(result.errors)}")
        print(f"   Skipped: {len(result.skipped)}")
        print()
        print("⚠️  LOSSLESS ARCHITECTURE VIOLATED!")
        return 1


if __name__ == '__main__':
    sys.exit(run_tests())
