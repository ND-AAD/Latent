# Agent 9: Basic Integration Tests

**Day**: 1
**Phase**: Phase 0 - C++ Core Foundation
**Duration**: 2-3 hours
**Estimated Cost**: $1-2 (20K tokens, Haiku)

---

## Mission

Create comprehensive integration tests for Day 1 deliverables, verifying the complete pipeline from Grasshopper to desktop display.

---

## Context

You are creating the test suite that validates all Day 1 components work together:
- C++ types and SubDEvaluator
- pybind11 bindings
- Grasshopper HTTP server
- Desktop bridge and display
- End-to-end workflow

**Critical**: These tests establish baseline functionality. All must pass before Day 2 begins.

**Dependencies**: All Agents 1-8 complete

---

## Deliverables

**Files to Create**:
1. `tests/test_day1_integration.py` - Complete integration test suite
2. `tests/run_all_tests.sh` - Convenient test runner
3. `tests/README.md` - Testing documentation

---

## Requirements

### 1. Integration Test Suite

**File**: `tests/test_day1_integration.py`

```python
#!/usr/bin/env python3
"""
Day 1 Integration Tests

Validates complete pipeline:
- C++ core (types, SubDEvaluator)
- pybind11 bindings
- Grasshopper server
- Desktop bridge
- VTK display

Run: python3 tests/test_day1_integration.py
"""

import sys
import os

# Add cpp_core/build to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'cpp_core', 'build'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import unittest
import numpy as np
import cpp_core
from app.bridge.subd_fetcher import SubDFetcher
from app.geometry.subd_display import SubDDisplayManager

class TestCppCore(unittest.TestCase):
    """Test C++ core functionality."""

    def test_point3d(self):
        """Test Point3D struct."""
        p = cpp_core.Point3D(1.0, 2.0, 3.0)
        self.assertEqual(p.x, 1.0)
        self.assertEqual(p.y, 2.0)
        self.assertEqual(p.z, 3.0)

    def test_control_cage(self):
        """Test SubDControlCage struct."""
        cage = cpp_core.SubDControlCage()

        # Add vertices
        cage.vertices = [
            cpp_core.Point3D(0, 0, 0),
            cpp_core.Point3D(1, 0, 0),
            cpp_core.Point3D(1, 1, 0),
            cpp_core.Point3D(0, 1, 0)
        ]

        self.assertEqual(cage.vertex_count(), 4)

        # Add face
        cage.faces = [[0, 1, 2, 3]]
        self.assertEqual(cage.face_count(), 1)

    def test_subd_evaluator_initialization(self):
        """Test SubDEvaluator initialization."""
        cage = self._create_quad_cage()

        evaluator = cpp_core.SubDEvaluator()
        self.assertFalse(evaluator.is_initialized())

        evaluator.initialize(cage)
        self.assertTrue(evaluator.is_initialized())
        self.assertEqual(evaluator.get_control_vertex_count(), 4)
        self.assertEqual(evaluator.get_control_face_count(), 1)

    def test_tessellation(self):
        """Test tessellation at multiple levels."""
        cage = self._create_quad_cage()
        evaluator = cpp_core.SubDEvaluator()
        evaluator.initialize(cage)

        for level in [1, 2, 3]:
            result = evaluator.tessellate(level)

            # Verify structure
            self.assertGreater(result.vertex_count(), 0)
            self.assertGreater(result.triangle_count(), 0)

            # Verify array shapes
            self.assertEqual(result.vertices.shape[1], 3)
            self.assertEqual(result.normals.shape[1], 3)
            self.assertEqual(result.triangles.shape[1], 3)

            # Verify sizes match
            self.assertEqual(result.vertices.shape[0], result.vertex_count())
            self.assertEqual(result.normals.shape[0], result.vertex_count())
            self.assertEqual(result.triangles.shape[0], result.triangle_count())

    def test_limit_evaluation(self):
        """Test exact limit surface evaluation."""
        cage = self._create_quad_cage()
        evaluator = cpp_core.SubDEvaluator()
        evaluator.initialize(cage)

        # Evaluate at face center
        point = evaluator.evaluate_limit_point(0, 0.5, 0.5)

        # Should be between 0 and 1 for unit quad
        self.assertGreaterEqual(point.x, 0.0)
        self.assertLessEqual(point.x, 1.0)
        self.assertGreaterEqual(point.y, 0.0)
        self.assertLessEqual(point.y, 1.0)

        # Test with normal
        point, normal = evaluator.evaluate_limit(0, 0.5, 0.5)

        # Normal should be unit length
        length = np.sqrt(normal.x**2 + normal.y**2 + normal.z**2)
        self.assertAlmostEqual(length, 1.0, places=2)

    def _create_quad_cage(self):
        """Helper to create simple quad cage."""
        cage = cpp_core.SubDControlCage()
        cage.vertices = [
            cpp_core.Point3D(0, 0, 0),
            cpp_core.Point3D(1, 0, 0),
            cpp_core.Point3D(1, 1, 0),
            cpp_core.Point3D(0, 1, 0)
        ]
        cage.faces = [[0, 1, 2, 3]]
        return cage


class TestGrasshopperBridge(unittest.TestCase):
    """Test Grasshopper HTTP server connection."""

    def setUp(self):
        """Set up fetcher."""
        self.fetcher = SubDFetcher()

    def test_server_availability(self):
        """Test server availability check."""
        # Note: This may fail if server not running
        is_available = self.fetcher.is_server_available()

        if is_available:
            print("  ✅ Server available")
        else:
            print("  ⚠️  Server not available (start Grasshopper component)")

    def test_fetch_geometry(self):
        """Test fetching geometry from server."""
        if not self.fetcher.is_server_available():
            self.skipTest("Grasshopper server not available")

        cage = self.fetcher.fetch_control_cage()

        if cage is None:
            self.skipTest("No geometry on server")

        # Verify cage structure
        self.assertGreater(cage.vertex_count(), 0)
        self.assertGreater(cage.face_count(), 0)

        print(f"  ✅ Fetched {cage.vertex_count()} vertices, "
              f"{cage.face_count()} faces")

    def test_metadata(self):
        """Test metadata fetch."""
        if not self.fetcher.is_server_available():
            self.skipTest("Grasshopper server not available")

        metadata = self.fetcher.get_metadata()

        if metadata:
            self.assertIn('vertex_count', metadata)
            self.assertIn('face_count', metadata)
            print(f"  ✅ Metadata: {metadata}")


class TestVTKDisplay(unittest.TestCase):
    """Test VTK display utilities."""

    def test_create_mesh_actor(self):
        """Test creating VTK actor from tessellation."""
        # Create simple tessellation
        cage = self._create_quad_cage()
        evaluator = cpp_core.SubDEvaluator()
        evaluator.initialize(cage)
        result = evaluator.tessellate(2)

        # Create actor
        actor = SubDDisplayManager.create_mesh_actor(result)

        # Verify actor created
        self.assertIsNotNone(actor)
        self.assertIsNotNone(actor.GetMapper())

        print("  ✅ Mesh actor created successfully")

    def test_create_control_cage_actor(self):
        """Test creating control cage wireframe actor."""
        cage = self._create_quad_cage()

        actor = SubDDisplayManager.create_control_cage_actor(cage)

        self.assertIsNotNone(actor)
        self.assertIsNotNone(actor.GetMapper())

        print("  ✅ Control cage actor created successfully")

    def test_bounding_box(self):
        """Test bounding box computation."""
        cage = self._create_quad_cage()
        evaluator = cpp_core.SubDEvaluator()
        evaluator.initialize(cage)
        result = evaluator.tessellate(2)

        min_corner, max_corner = SubDDisplayManager.compute_bounding_box(result)

        # Verify structure
        self.assertEqual(len(min_corner), 3)
        self.assertEqual(len(max_corner), 3)

        # Verify min < max
        for i in range(3):
            self.assertLessEqual(min_corner[i], max_corner[i])

        print(f"  ✅ Bounding box: {min_corner} to {max_corner}")

    def _create_quad_cage(self):
        """Helper to create simple quad cage."""
        cage = cpp_core.SubDControlCage()
        cage.vertices = [
            cpp_core.Point3D(0, 0, 0),
            cpp_core.Point3D(1, 0, 0),
            cpp_core.Point3D(1, 1, 0),
            cpp_core.Point3D(0, 1, 0)
        ]
        cage.faces = [[0, 1, 2, 3]]
        return cage


class TestEndToEnd(unittest.TestCase):
    """Test complete end-to-end workflow."""

    def test_full_pipeline(self):
        """Test complete pipeline from Grasshopper to display."""
        # 1. Fetch from Grasshopper
        fetcher = SubDFetcher()

        if not fetcher.is_server_available():
            self.skipTest("Grasshopper server not available")

        cage = fetcher.fetch_control_cage()

        if cage is None:
            self.skipTest("No geometry available")

        print(f"\n  Step 1: Fetched {cage.vertex_count()} vertices ✅")

        # 2. Initialize evaluator
        evaluator = cpp_core.SubDEvaluator()
        evaluator.initialize(cage)

        self.assertTrue(evaluator.is_initialized())
        print(f"  Step 2: Evaluator initialized ✅")

        # 3. Tessellate
        result = evaluator.tessellate(3)

        self.assertGreater(result.vertex_count(), cage.vertex_count())
        print(f"  Step 3: Tessellated to {result.vertex_count()} vertices ✅")

        # 4. Create VTK actor
        actor = SubDDisplayManager.create_mesh_actor(result)

        self.assertIsNotNone(actor)
        print(f"  Step 4: VTK actor created ✅")

        # 5. Test limit evaluation
        point = evaluator.evaluate_limit_point(0, 0.5, 0.5)

        self.assertIsNotNone(point)
        print(f"  Step 5: Limit evaluation at ({point.x:.3f}, {point.y:.3f}, {point.z:.3f}) ✅")

        print("\n  🎉 FULL PIPELINE WORKING!")


def run_tests():
    """Run all tests with detailed output."""
    print("=" * 70)
    print("Day 1 Integration Tests")
    print("=" * 70)
    print()

    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # Add test classes
    suite.addTests(loader.loadTestsFromTestCase(TestCppCore))
    suite.addTests(loader.loadTestsFromTestCase(TestGrasshopperBridge))
    suite.addTests(loader.loadTestsFromTestCase(TestVTKDisplay))
    suite.addTests(loader.loadTestsFromTestCase(TestEndToEnd))

    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    print()
    print("=" * 70)

    if result.wasSuccessful():
        print("✅ ALL TESTS PASSED!")
        print(f"   Ran {result.testsRun} tests")
        return 0
    else:
        print("❌ SOME TESTS FAILED")
        print(f"   Failures: {len(result.failures)}")
        print(f"   Errors: {len(result.errors)}")
        print(f"   Skipped: {len(result.skipped)}")
        return 1


if __name__ == '__main__':
    sys.exit(run_tests())
```

### 2. Test Runner Script

**File**: `tests/run_all_tests.sh`

```bash
#!/bin/bash
# Run all Day 1 tests

set -e  # Exit on error

echo "======================================================================"
echo "Running Day 1 Test Suite"
echo "======================================================================"
echo ""

# Check C++ build exists
if [ ! -f "cpp_core/build/cpp_core.so" ]; then
    echo "❌ C++ module not built. Run:"
    echo "   cd cpp_core/build && cmake .. && make"
    exit 1
fi

# Check Grasshopper server (optional warning)
if ! curl -s http://localhost:8888/status > /dev/null 2>&1; then
    echo "⚠️  Grasshopper server not detected on port 8888"
    echo "   Some tests will be skipped"
    echo ""
fi

# Run C++ unit tests (if built)
if [ -f "cpp_core/build/test_subd_evaluator" ]; then
    echo "Running C++ unit tests..."
    echo "----------------------------------------------------------------------"
    cpp_core/build/test_subd_evaluator
    echo ""
fi

# Run Python binding tests
echo "Running Python binding tests..."
echo "----------------------------------------------------------------------"
python3 cpp_core/python_bindings/test_bindings.py
echo ""

# Run integration tests
echo "Running integration tests..."
echo "----------------------------------------------------------------------"
python3 tests/test_day1_integration.py
echo ""

# Summary
echo "======================================================================"
echo "✅ All tests completed!"
echo "======================================================================"
```

**Make executable**:
```bash
chmod +x tests/run_all_tests.sh
```

### 3. Testing Documentation

**File**: `tests/README.md`

```markdown
# Latent Test Suite

Comprehensive tests for the Latent ceramic mold generation system.

## Running Tests

### Quick Start

Run all Day 1 tests:
```bash
./tests/run_all_tests.sh
```

### Individual Test Suites

**C++ Unit Tests**:
```bash
cd cpp_core/build
./test_subd_evaluator
```

**Python Binding Tests**:
```bash
python3 cpp_core/python_bindings/test_bindings.py
```

**Integration Tests**:
```bash
python3 tests/test_day1_integration.py
```

## Test Coverage

### Day 1 Tests

- ✅ C++ core types (Point3D, SubDControlCage, TessellationResult)
- ✅ SubDEvaluator initialization and tessellation
- ✅ Exact limit surface evaluation
- ✅ pybind11 bindings (zero-copy numpy integration)
- ✅ Grasshopper HTTP server connection
- ✅ VTK display utilities
- ✅ End-to-end pipeline (Rhino → Desktop)

## Requirements

### For All Tests:
- C++ module built (`cpp_core/build/cpp_core.so`)
- Python dependencies installed (`pip install -r requirements.txt`)

### For Grasshopper Tests:
- Rhino 8 running
- Grasshopper HTTP server component active (port 8888)
- SubD geometry loaded in Grasshopper

## Test Structure

```
tests/
├── README.md                    # This file
├── run_all_tests.sh             # Run all tests
└── test_day1_integration.py     # Day 1 integration tests

cpp_core/
├── test_subd_evaluator.cpp      # C++ unit tests
└── python_bindings/
    └── test_bindings.py         # pybind11 tests
```

## Continuous Integration

Tests should be run:
- After each agent completes
- Before starting next day
- Before committing major changes
- When debugging issues

## Expected Results

**All tests passing**:
```
======================================================================
✅ ALL TESTS PASSED!
   Ran 15 tests
======================================================================
```

**Some tests skipped** (server not available):
```
⚠️  Grasshopper server not detected on port 8888
   Some tests will be skipped

...

✅ ALL TESTS PASSED!
   Ran 12 tests (3 skipped)
```

## Troubleshooting

**"cpp_core module not found"**:
- Build C++ module: `cd cpp_core/build && cmake .. && make`
- Add to PYTHONPATH: `export PYTHONPATH=cpp_core/build:$PYTHONPATH`

**"Grasshopper tests failing"**:
- Start Grasshopper HTTP server (Agent 6's component)
- Ensure SubD geometry is connected to server
- Check port 8888 is not blocked

**"VTK import error"**:
- Install VTK: `pip install vtk`
- Check Python version (3.12+ required)

**"Tessellation tests fail"**:
- Verify OpenSubdiv installed: `pkg-config --modversion opensubdiv`
- Rebuild C++ module with verbose output: `cmake .. -DCMAKE_VERBOSE_MAKEFILE=ON`

## Performance Benchmarks

Expected performance (on M1 Mac):

| Operation | Target | Typical |
|-----------|--------|---------|
| Initialization | <20ms | ~5ms |
| Tessellation (L3) | <100ms | ~30ms |
| Limit evaluation | >10K pts/sec | ~50K pts/sec |
| Full pipeline | <200ms | ~100ms |

Run benchmarks:
```bash
python3 tests/test_tessellation_perf.py
```
```

---

## Success Criteria

- [ ] All C++ unit tests pass
- [ ] All Python binding tests pass
- [ ] All integration tests pass (or skip gracefully if server unavailable)
- [ ] End-to-end pipeline test completes successfully
- [ ] Test runner script works
- [ ] Documentation is clear and complete
- [ ] All tests run in <30 seconds total
- [ ] No memory leaks detected
- [ ] Performance meets benchmarks

---

## Integration Notes

**Validates**:
- Agent 1 (types)
- Agent 2 (SubDEvaluator header)
- Agent 3 (CMake build)
- Agent 4 (SubDEvaluator implementation)
- Agent 5 (pybind11 bindings)
- Agent 6 (Grasshopper server)
- Agent 7 (tessellation and display)
- Agent 8 (desktop bridge)

**File Structure**:
```
tests/
├── README.md                     (You create) ← HERE
├── run_all_tests.sh              (You create) ← HERE
└── test_day1_integration.py      (You create) ← HERE
```

---

## Output Format

Provide:
1. Complete `test_day1_integration.py` test suite
2. Complete `run_all_tests.sh` script
3. Complete `tests/README.md` documentation
4. Test run output showing results
5. Summary of test coverage
6. Any issues encountered and solutions

---

**Ready to begin!**
