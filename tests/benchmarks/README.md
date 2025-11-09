# Performance Benchmark Suite

**Agent 61 - Day 9**

Comprehensive performance benchmarking for the Ceramic Mold Analyzer system.

## Overview

This benchmark suite measures performance across all critical operations with specific targets aligned to user experience and real-time interaction requirements.

## Performance Targets

| Operation | Target | Rationale |
|-----------|--------|-----------|
| **Tessellation** | <50ms for 10K vertices | Real-time viewport responsiveness |
| **Limit Evaluation** | <0.1ms per point | Interactive surface queries |
| **Eigenvalue Solve** | <500ms for 10K vertices, k=10 | Spectral lens responsiveness |
| **NURBS Fitting** | <200ms per surface | Mold generation workflow |
| **Total Analysis Pipeline** | <2 seconds | Complete region discovery |

## Running Benchmarks

### Prerequisites

1. **Build C++ Core Module**:
   ```bash
   cd cpp_core/build
   cmake ..
   make -j$(nproc)
   ```

2. **Install Python Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

### Execute Benchmark Suite

```bash
# From project root
python3 tests/benchmarks/benchmark_suite.py

# Or make it executable and run directly
chmod +x tests/benchmarks/benchmark_suite.py
./tests/benchmarks/benchmark_suite.py
```

### Test Mode (No C++ Required)

To verify the benchmark infrastructure without building C++:

```bash
python3 tests/benchmarks/benchmark_suite.py --test-mode
```

## Benchmark Categories

### 1. Tessellation Benchmarks

Tests SubD tessellation at various subdivision levels:
- Level 3: ~1K vertices (baseline)
- Level 4: ~4K vertices
- Level 5: ~16K vertices (stress test)

**Key Metrics**:
- Vertices/second throughput
- Memory allocation patterns
- Subdivision level scaling

### 2. Limit Evaluation Benchmarks

Tests exact limit surface evaluation:
- Single point evaluation
- Batch evaluation (1000 points)
- Evaluation with first derivatives
- Evaluation with second derivatives

**Key Metrics**:
- Per-point evaluation time
- Batch efficiency vs individual calls
- Derivative computation overhead

### 3. Curvature Analysis Benchmarks

Tests differential geometry computations:
- Single point curvature (Gaussian, Mean, Principal)
- Batch curvature computation
- Fundamental forms computation

**Key Metrics**:
- Eigendecomposition performance (shape operator)
- Memory efficiency for batch operations
- Numerical stability

### 4. Spectral Decomposition Benchmarks

Tests Laplace-Beltrami eigenvalue computation:
- Eigenvalue solve (k=10 modes)
- Laplacian matrix construction
- Sparse solver performance

**Key Metrics**:
- Eigenvalue solve time vs mesh resolution
- Memory usage for sparse matrices
- Convergence characteristics

### 5. Differential Lens Benchmarks

Tests curvature-based region discovery:
- Complete differential analysis
- Curvature field computation
- Region boundary extraction

**Key Metrics**:
- End-to-end analysis time
- Number of regions discovered
- Quality of decomposition (resonance score)

### 6. Constraint Validation Benchmarks

Tests manufacturability checking:
- Undercut detection
- Draft angle computation
- Complete constraint validation

**Key Metrics**:
- Faces processed per second
- Ray-casting performance
- Validation completeness

### 7. NURBS Generation Benchmarks

Tests mold surface fitting:
- NURBS surface fitting
- Quality assessment
- Draft angle transformation

**Key Metrics**:
- Fitting time vs sample density
- Approximation error (max, mean, RMS)
- Surface smoothness

### 8. Full Pipeline Benchmarks

Tests complete analysis workflow:
- Initialization → Analysis → Results
- Caching effectiveness
- Memory footprint

**Key Metrics**:
- Total pipeline time
- Cache hit rates
- Peak memory usage

## Understanding Results

### Benchmark Output

The suite provides:

1. **Mean Time**: Average across all iterations
2. **Median Time**: Middle value (less affected by outliers)
3. **Std Dev**: Variation between runs (lower is better)
4. **Range**: Min to max time observed

### Performance Status

- ✅ **PASS**: Meets performance target
- ❌ **MISS**: Slower than target (optimization needed)
- ⚠️ **High Variance**: >30% std dev (inconsistent performance)

### Optimization Opportunities

The report automatically identifies:

1. **Operations Missing Targets**: Sorted by slowdown factor
2. **High Variance Operations**: May need warm-up or caching
3. **Slow Operations**: Could benefit from optimization even if passing

## Example Output

```
================================================================================
PERFORMANCE BENCHMARK SUITE - COMPREHENSIVE REPORT
================================================================================

Total Suite Runtime: 45.234s
Number of Benchmarks: 18
Performance Targets: 16/18 met

--------------------------------------------------------------------------------
DETAILED RESULTS
--------------------------------------------------------------------------------

[1] Tessellation Level 3
    Description: SubD tessellation at subdivision level 3
    Iterations: 5
    Mean Time: 23.456 ms
    Median Time: 23.123 ms
    Std Dev: 1.234 ms
    Range: 22.001 - 25.678 ms
    Target: 50.0 ms - ✅ PASS
    Metadata: {'vertex_count': 1024, 'triangle_count': 2048}

[2] Single Limit Point
    Description: Evaluate single point on limit surface
    Iterations: 100
    Mean Time: 0.087 ms
    Median Time: 0.085 ms
    Std Dev: 0.012 ms
    Range: 0.075 - 0.112 ms
    Target: 0.1 ms - ✅ PASS

...

================================================================================
OPTIMIZATION OPPORTUNITIES
================================================================================

⚠️  Operations Missing Performance Targets:
  - Eigenvalue Solve (k=10): 1.45x slower (725ms vs 500ms target)
  - NURBS Surface Fitting: 1.15x slower (230ms vs 200ms target)

Recommendations:

  High Variance (>30% of mean) - Consider:
  - Eigenvalue Solve (k=10): Reduce cache effects or warm up JIT compilation

  Slow Operations (could benefit from optimization):
  - Complete Analysis Pipeline: 1850ms (consider caching or parallelization)

================================================================================
```

## Integration with CI/CD

### Regression Testing

Add to CI pipeline to detect performance regressions:

```yaml
- name: Performance Benchmarks
  run: |
    python3 tests/benchmarks/benchmark_suite.py
    # Exit code 1 if targets not met
```

### Performance Tracking

Track metrics over time:

```bash
# Save results with timestamp
python3 tests/benchmarks/benchmark_suite.py > results/benchmark_$(date +%Y%m%d).txt
```

## Interpreting Performance Targets

### Why These Targets?

1. **<50ms Tessellation**:
   - 60 FPS = 16.67ms frame budget
   - Tessellation should be <1/3 of frame time
   - Leaves room for rendering and UI

2. **<0.1ms Limit Evaluation**:
   - Interactive picking requires <100ms total
   - 1000 points at 0.1ms = 100ms
   - Sufficient for real-time analysis

3. **<500ms Eigenvalue Solve**:
   - User tolerance for "heavy" computation: ~1 second
   - 500ms allows for UI overhead
   - Still feels responsive

4. **<200ms NURBS Fitting**:
   - Mold generation per region
   - 5 regions × 200ms = 1 second total
   - Acceptable for batch operation

5. **<2s Total Pipeline**:
   - Complete analysis feels "fast" under 3 seconds
   - 2s target provides headroom
   - Allows for larger models

## Profiling Deep Dives

For detailed profiling of specific operations:

```python
import cProfile
import pstats

# Profile specific operation
profiler = cProfile.Profile()
profiler.enable()

# ... operation to profile ...

profiler.disable()
stats = pstats.Stats(profiler)
stats.sort_stats('cumulative')
stats.print_stats(20)  # Top 20 functions
```

## Hardware Considerations

Benchmark results vary by hardware:

- **CPU**: Single-threaded performance matters most
- **Memory**: Large meshes require >8GB RAM
- **Cache**: L2/L3 cache size affects batch operations
- **Platform**: macOS (Metal) vs Linux (OpenGL) backends

Reference hardware (2023 M2 MacBook Pro):
- All targets should be met
- Tessellation: ~25ms for 10K vertices
- Eigenvalue: ~350ms for 10K vertices, k=10

## Troubleshooting

### Slow Performance

1. **Check Build Type**: Release builds are 10-50x faster than Debug
   ```bash
   cmake -DCMAKE_BUILD_TYPE=Release ..
   ```

2. **Verify OpenSubdiv Backend**: Metal (macOS) or TBB (Linux) for parallel processing

3. **Profile to Find Bottleneck**: Use cProfile or instruments

### High Variance

1. **Warm-up Runs**: JIT compilation, cache effects
2. **Background Processes**: Close other applications
3. **Thermal Throttling**: Ensure adequate cooling

### Import Errors

```bash
# Ensure cpp_core is built and in path
export PYTHONPATH=/path/to/Latent/cpp_core/build:$PYTHONPATH
```

## Future Enhancements

Potential improvements to benchmark suite:

1. **Memory Profiling**: Track allocation patterns
2. **GPU Benchmarks**: Measure Metal/CUDA performance
3. **Parallel Scaling**: Test multi-threading efficiency
4. **Comparative Analysis**: Track performance over commits
5. **Stress Testing**: Very large models (>1M vertices)

## References

- OpenSubdiv Performance: https://graphics.pixar.com/opensubdiv/docs/performance.html
- SciPy eigsh Performance: https://docs.scipy.org/doc/scipy/reference/sparse.linalg.html
- VTK Benchmarking: https://vtk.org/Wiki/VTK/Tutorials/Performance

---

**Last Updated**: November 2025
**Author**: Agent 61, Day 9 API Sprint
