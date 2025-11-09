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
