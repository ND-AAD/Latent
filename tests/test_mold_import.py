"""
Unit tests for Grasshopper mold import functionality.

Tests the NURBS surface reconstruction from serialized mold data.
"""

import unittest
import json
from pathlib import Path


class TestMoldDataFormat(unittest.TestCase):
    """Test mold data format validation."""

    def setUp(self):
        """Load test mold data."""
        test_file = Path(__file__).parent / 'test_mold.json'
        with open(test_file, 'r') as f:
            self.mold_data = json.load(f)

    def test_data_structure(self):
        """Test that mold data has correct structure."""
        self.assertIn('type', self.mold_data)
        self.assertEqual(self.mold_data['type'], 'ceramic_mold_set')
        self.assertIn('molds', self.mold_data)
        self.assertIsInstance(self.mold_data['molds'], list)

    def test_mold_fields(self):
        """Test that each mold has required fields."""
        required_fields = [
            'name', 'degree_u', 'degree_v',
            'count_u', 'count_v',
            'control_points', 'weights',
            'knots_u', 'knots_v'
        ]

        for mold in self.mold_data['molds']:
            for field in required_fields:
                self.assertIn(field, mold, f"Mold missing field: {field}")

    def test_control_point_count(self):
        """Test that control points match count_u * count_v."""
        for mold in self.mold_data['molds']:
            count_u = mold['count_u']
            count_v = mold['count_v']
            expected_count = count_u * count_v

            actual_count = len(mold['control_points'])
            self.assertEqual(
                actual_count, expected_count,
                f"Expected {expected_count} control points, got {actual_count}"
            )

            actual_weights = len(mold['weights'])
            self.assertEqual(
                actual_weights, expected_count,
                f"Expected {expected_count} weights, got {actual_weights}"
            )

    def test_knot_vector_length(self):
        """Test that knot vectors have correct length."""
        for mold in self.mold_data['molds']:
            degree_u = mold['degree_u']
            degree_v = mold['degree_v']
            count_u = mold['count_u']
            count_v = mold['count_v']

            # For B-spline: knot_count = control_point_count + degree + 1
            expected_knots_u = count_u + degree_u + 1
            expected_knots_v = count_v + degree_v + 1

            actual_knots_u = len(mold['knots_u'])
            actual_knots_v = len(mold['knots_v'])

            self.assertEqual(
                actual_knots_u, expected_knots_u,
                f"Expected {expected_knots_u} U knots, got {actual_knots_u}"
            )
            self.assertEqual(
                actual_knots_v, expected_knots_v,
                f"Expected {expected_knots_v} V knots, got {actual_knots_v}"
            )

    def test_control_point_format(self):
        """Test that control points are 3D coordinates."""
        for mold in self.mold_data['molds']:
            for i, pt in enumerate(mold['control_points']):
                self.assertEqual(
                    len(pt), 3,
                    f"Control point {i} should be [x,y,z]"
                )
                for coord in pt:
                    self.assertIsInstance(
                        coord, (int, float),
                        f"Control point coordinate should be numeric"
                    )

    def test_weights_positive(self):
        """Test that all weights are positive."""
        for mold in self.mold_data['molds']:
            for i, w in enumerate(mold['weights']):
                self.assertGreater(
                    w, 0,
                    f"Weight {i} should be positive, got {w}"
                )

    def test_knot_vectors_non_decreasing(self):
        """Test that knot vectors are non-decreasing."""
        for mold in self.mold_data['molds']:
            # Test U knots
            for i in range(len(mold['knots_u']) - 1):
                self.assertLessEqual(
                    mold['knots_u'][i], mold['knots_u'][i + 1],
                    f"U knots should be non-decreasing"
                )

            # Test V knots
            for i in range(len(mold['knots_v']) - 1):
                self.assertLessEqual(
                    mold['knots_v'][i], mold['knots_v'][i + 1],
                    f"V knots should be non-decreasing"
                )


class TestMoldSerialization(unittest.TestCase):
    """Test mold serialization/deserialization."""

    def test_json_roundtrip(self):
        """Test that mold data can be serialized and deserialized."""
        test_file = Path(__file__).parent / 'test_mold.json'
        with open(test_file, 'r') as f:
            original = json.load(f)

        # Serialize and deserialize
        serialized = json.dumps(original)
        deserialized = json.loads(serialized)

        # Compare
        self.assertEqual(original, deserialized)

    def test_minimal_mold(self):
        """Test minimal valid mold data."""
        minimal_mold = {
            "type": "ceramic_mold_set",
            "molds": [
                {
                    "name": "minimal",
                    "degree_u": 1,
                    "degree_v": 1,
                    "count_u": 2,
                    "count_v": 2,
                    "control_points": [
                        [0.0, 0.0, 0.0],
                        [1.0, 0.0, 0.0],
                        [0.0, 1.0, 0.0],
                        [1.0, 1.0, 0.0]
                    ],
                    "weights": [1.0, 1.0, 1.0, 1.0],
                    "knots_u": [0.0, 0.0, 1.0, 1.0],
                    "knots_v": [0.0, 0.0, 1.0, 1.0]
                }
            ]
        }

        # Verify it can be serialized
        serialized = json.dumps(minimal_mold)
        self.assertIsInstance(serialized, str)

        # Verify it can be deserialized
        deserialized = json.loads(serialized)
        self.assertEqual(minimal_mold, deserialized)


class TestNURBSParameters(unittest.TestCase):
    """Test NURBS surface parameter validation."""

    def test_degree_validity(self):
        """Test that degrees are valid for NURBS surfaces."""
        test_file = Path(__file__).parent / 'test_mold.json'
        with open(test_file, 'r') as f:
            data = json.load(f)

        for mold in data['molds']:
            # Degree should be >= 1
            self.assertGreaterEqual(mold['degree_u'], 1)
            self.assertGreaterEqual(mold['degree_v'], 1)

            # Degree should be < control point count
            self.assertLess(mold['degree_u'], mold['count_u'])
            self.assertLess(mold['degree_v'], mold['count_v'])

    def test_order_calculation(self):
        """Test Rhino order = degree + 1 conversion."""
        test_file = Path(__file__).parent / 'test_mold.json'
        with open(test_file, 'r') as f:
            data = json.load(f)

        for mold in data['molds']:
            degree_u = mold['degree_u']
            degree_v = mold['degree_v']

            # Rhino uses order = degree + 1
            order_u = degree_u + 1
            order_v = degree_v + 1

            # Order should be valid
            self.assertGreaterEqual(order_u, 2)
            self.assertGreaterEqual(order_v, 2)


def run_tests():
    """Run all tests and report results."""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestMoldDataFormat))
    suite.addTests(loader.loadTestsFromTestCase(TestMoldSerialization))
    suite.addTests(loader.loadTestsFromTestCase(TestNURBSParameters))

    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    return result.wasSuccessful()


if __name__ == '__main__':
    import sys
    success = run_tests()
    sys.exit(0 if success else 1)
