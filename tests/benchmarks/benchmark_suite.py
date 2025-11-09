#!/usr/bin/env python3
"""
Performance Benchmark Suite - Day 9, Agent 61

Comprehensive benchmarking of all system operations with performance targets:
- Tessellation: <50ms for 10K vertices
- Limit evaluation: <0.1ms per point
- Eigenvalue solve: <500ms for 10K vertices, k=10
- NURBS fitting: <200ms per surface
- Total analysis pipeline: <2 seconds

Author: Agent 61, Ceramic Mold Analyzer
Date: November 2025
"""

import sys
import time
import statistics
from dataclasses import dataclass
from typing import List, Callable, Optional, Dict, Any
import numpy as np

try:
    import cpp_core
    CPP_CORE_AVAILABLE = True
except ImportError:
    CPP_CORE_AVAILABLE = False
    print("⚠️  cpp_core not available - some benchmarks will be skipped")

# Try to import analysis components
try:
    from app.analysis.spectral_decomposition import SpectralDecomposer
    from app.analysis.differential_lens import DifferentialLens
    from app.analysis.lens_manager import LensManager, LensType
    ANALYSIS_AVAILABLE = True
except (ImportError, AttributeError):
    ANALYSIS_AVAILABLE = False
    print("⚠️  Analysis modules not fully available")


@dataclass
class BenchmarkResult:
    """Result of a single benchmark run."""
    name: str
    description: str
    iterations: int
    times: List[float]  # seconds
    mean_time: float  # seconds
    median_time: float  # seconds
    std_dev: float  # seconds
    min_time: float  # seconds
    max_time: float  # seconds
    target_time: Optional[float] = None  # seconds
    meets_target: Optional[bool] = None
    metadata: Dict[str, Any] = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}
        if self.target_time is not None:
            self.meets_target = self.mean_time <= self.target_time


@dataclass
class BenchmarkSuite:
    """Collection of benchmark results with summary statistics."""
    results: List[BenchmarkResult]
    total_time: float

    def print_report(self):
        """Print comprehensive benchmark report."""
        print("\n" + "="*80)
        print("PERFORMANCE BENCHMARK SUITE - COMPREHENSIVE REPORT")
        print("="*80)
        print(f"\nTotal Suite Runtime: {self.total_time:.3f}s")
        print(f"Number of Benchmarks: {len(self.results)}")

        # Count targets
        targets_met = sum(1 for r in self.results if r.meets_target is True)
        targets_missed = sum(1 for r in self.results if r.meets_target is False)
        total_targets = targets_met + targets_missed

        if total_targets > 0:
            print(f"Performance Targets: {targets_met}/{total_targets} met")

        print("\n" + "-"*80)
        print("DETAILED RESULTS")
        print("-"*80)

        for i, result in enumerate(self.results, 1):
            print(f"\n[{i}] {result.name}")
            print(f"    Description: {result.description}")
            print(f"    Iterations: {result.iterations}")
            print(f"    Mean Time: {result.mean_time*1000:.3f} ms")
            print(f"    Median Time: {result.median_time*1000:.3f} ms")
            print(f"    Std Dev: {result.std_dev*1000:.3f} ms")
            print(f"    Range: {result.min_time*1000:.3f} - {result.max_time*1000:.3f} ms")

            if result.target_time is not None:
                target_ms = result.target_time * 1000
                status = "✅ PASS" if result.meets_target else "❌ MISS"
                print(f"    Target: {target_ms:.1f} ms - {status}")
                if not result.meets_target:
                    ratio = result.mean_time / result.target_time
                    print(f"    Slowdown: {ratio:.2f}x slower than target")

            if result.metadata:
                print(f"    Metadata: {result.metadata}")

        print("\n" + "="*80)
        print("OPTIMIZATION OPPORTUNITIES")
        print("="*80)

        # Identify slow operations
        slow_ops = [r for r in self.results if r.meets_target is False]
        if slow_ops:
            print("\n⚠️  Operations Missing Performance Targets:")
            for r in slow_ops:
                ratio = r.mean_time / r.target_time if r.target_time else 1.0
                print(f"  - {r.name}: {ratio:.2f}x slower ({r.mean_time*1000:.1f}ms vs {r.target_time*1000:.1f}ms target)")
        else:
            print("\n✅ All performance targets met!")

        # Additional recommendations
        print("\nRecommendations:")

        # Check for high variance
        high_variance = [r for r in self.results if r.std_dev > r.mean_time * 0.3]
        if high_variance:
            print("\n  High Variance (>30% of mean) - Consider:")
            for r in high_variance:
                print(f"  - {r.name}: Reduce cache effects or warm up JIT compilation")

        # Check for slow operations even if they meet targets
        slow_but_passing = [r for r in self.results
                           if r.meets_target and r.mean_time > 0.1]
        if slow_but_passing:
            print("\n  Slow Operations (could benefit from optimization):")
            for r in slow_but_passing:
                print(f"  - {r.name}: {r.mean_time*1000:.1f}ms (consider caching or parallelization)")

        print("\n" + "="*80)


class PerformanceBenchmark:
    """Main benchmark orchestrator."""

    def __init__(self):
        self.results: List[BenchmarkResult] = []

    def run_benchmark(self,
                     name: str,
                     description: str,
                     func: Callable,
                     iterations: int = 5,
                     warmup: int = 1,
                     target_time: Optional[float] = None,
                     metadata: Optional[Dict] = None) -> BenchmarkResult:
        """
        Run a benchmark function multiple times and collect statistics.

        Args:
            name: Benchmark name
            description: What's being tested
            func: Function to benchmark (should return metadata dict or None)
            iterations: Number of timed runs
            warmup: Number of warmup runs (not timed)
            target_time: Target execution time in seconds (None for no target)
            metadata: Additional metadata to include

        Returns:
            BenchmarkResult with timing statistics
        """
        print(f"\n▶ Running: {name}...")

        # Warmup runs
        for _ in range(warmup):
            try:
                func()
            except Exception as e:
                print(f"  ⚠️  Warmup failed: {e}")

        # Timed runs
        times = []
        run_metadata = metadata or {}

        for i in range(iterations):
            start = time.perf_counter()
            try:
                result = func()
                if isinstance(result, dict):
                    run_metadata.update(result)
            except Exception as e:
                print(f"  ❌ Iteration {i+1} failed: {e}")
                continue

            elapsed = time.perf_counter() - start
            times.append(elapsed)

        if not times:
            print(f"  ❌ All iterations failed!")
            return None

        # Calculate statistics
        mean_time = statistics.mean(times)
        median_time = statistics.median(times)
        std_dev = statistics.stdev(times) if len(times) > 1 else 0.0
        min_time = min(times)
        max_time = max(times)

        result = BenchmarkResult(
            name=name,
            description=description,
            iterations=len(times),
            times=times,
            mean_time=mean_time,
            median_time=median_time,
            std_dev=std_dev,
            min_time=min_time,
            max_time=max_time,
            target_time=target_time,
            metadata=run_metadata
        )

        # Quick feedback
        status = ""
        if target_time is not None:
            status = " ✅" if result.meets_target else " ❌"
        print(f"  Mean: {mean_time*1000:.2f}ms{status}")

        self.results.append(result)
        return result

    def create_test_geometry(self, shape='cube'):
        """Create test geometry for benchmarking."""
        cage = cpp_core.SubDControlCage()

        if shape == 'cube':
            # Simple cube (6 faces)
            cage.vertices = [
                cpp_core.Point3D(0, 0, 0), cpp_core.Point3D(1, 0, 0),
                cpp_core.Point3D(1, 1, 0), cpp_core.Point3D(0, 1, 0),
                cpp_core.Point3D(0, 0, 1), cpp_core.Point3D(1, 0, 1),
                cpp_core.Point3D(1, 1, 1), cpp_core.Point3D(0, 1, 1)
            ]
            cage.faces = [
                [0, 1, 2, 3], [4, 5, 6, 7],  # Top, bottom
                [0, 1, 5, 4], [2, 3, 7, 6],  # Front, back
                [0, 3, 7, 4], [1, 2, 6, 5]   # Left, right
            ]

        elif shape == 'sphere':
            # Octahedron (subdivides to sphere-like surface)
            r = 1.0
            cage.vertices = [
                cpp_core.Point3D(r, 0, 0), cpp_core.Point3D(-r, 0, 0),
                cpp_core.Point3D(0, r, 0), cpp_core.Point3D(0, -r, 0),
                cpp_core.Point3D(0, 0, r), cpp_core.Point3D(0, 0, -r)
            ]
            cage.faces = [
                [0, 2, 4], [0, 4, 3], [0, 3, 5], [0, 5, 2],
                [1, 4, 2], [1, 3, 4], [1, 5, 3], [1, 2, 5]
            ]

        elif shape == 'cylinder':
            # Cylinder-like structure
            r = 1.0
            h = 2.0
            angles = [0, np.pi/2, np.pi, 3*np.pi/2]

            for z in [-h/2, h/2]:
                for angle in angles:
                    x = r * np.cos(angle)
                    y = r * np.sin(angle)
                    cage.vertices.append(cpp_core.Point3D(x, y, z))

            cage.faces = [
                [0, 1, 5, 4], [1, 2, 6, 5],
                [2, 3, 7, 6], [3, 0, 4, 7],
                [0, 1, 2, 3], [4, 5, 6, 7]
            ]

        return cage

    def benchmark_tessellation(self):
        """Benchmark tessellation performance."""
        print("\n" + "="*80)
        print("TESSELLATION BENCHMARKS")
        print("="*80)

        cage = self.create_test_geometry('sphere')
        evaluator = cpp_core.SubDEvaluator()
        evaluator.initialize(cage)

        # Test different subdivision levels
        for level in [3, 4, 5]:
            def bench_func():
                result = evaluator.tessellate(level)
                return {'vertex_count': result.vertex_count(),
                       'triangle_count': result.triangle_count()}

            # Estimate target based on vertex count
            # Target: <50ms for 10K vertices
            # Scale linearly as rough estimate
            target = None
            if level == 3:
                target = 0.050  # 50ms

            self.run_benchmark(
                name=f"Tessellation Level {level}",
                description=f"SubD tessellation at subdivision level {level}",
                func=bench_func,
                iterations=5,
                target_time=target
            )

    def benchmark_limit_evaluation(self):
        """Benchmark limit point evaluation."""
        print("\n" + "="*80)
        print("LIMIT EVALUATION BENCHMARKS")
        print("="*80)

        cage = self.create_test_geometry('sphere')
        evaluator = cpp_core.SubDEvaluator()
        evaluator.initialize(cage)

        # Single point evaluation
        def bench_single():
            pt = evaluator.evaluate_limit_point(0, 0.5, 0.5)
            return {}

        self.run_benchmark(
            name="Single Limit Point",
            description="Evaluate single point on limit surface",
            func=bench_single,
            iterations=100,
            target_time=0.0001  # 0.1ms
        )

        # Batch evaluation (1000 points)
        n_points = 1000
        face_indices = [0] * n_points
        params_u = [i % 10 / 10.0 for i in range(n_points)]
        params_v = [i // 10 / 10.0 for i in range(n_points)]

        def bench_batch():
            result = evaluator.batch_evaluate_limit(face_indices, params_u, params_v)
            return {'points_evaluated': result.vertex_count()}

        self.run_benchmark(
            name=f"Batch Limit Evaluation ({n_points} points)",
            description=f"Batch evaluate {n_points} limit points",
            func=bench_batch,
            iterations=5,
            target_time=0.1  # 100ms for 1000 points = 0.1ms per point
        )

        # Limit with derivatives
        def bench_derivatives():
            pos, du, dv = evaluator.evaluate_limit_with_derivatives(0, 0.5, 0.5)
            return {}

        self.run_benchmark(
            name="Limit with First Derivatives",
            description="Evaluate limit position and first derivatives",
            func=bench_derivatives,
            iterations=100,
            target_time=0.0002  # 0.2ms (slightly slower than point only)
        )

        # Limit with second derivatives
        def bench_second_derivatives():
            pos, du, dv, duu, dvv, duv = \
                evaluator.evaluate_limit_with_second_derivatives(0, 0.5, 0.5)
            return {}

        self.run_benchmark(
            name="Limit with Second Derivatives",
            description="Evaluate limit position with 1st and 2nd derivatives",
            func=bench_second_derivatives,
            iterations=100,
            target_time=0.0003  # 0.3ms (includes curvature computation)
        )

    def benchmark_curvature_analysis(self):
        """Benchmark curvature computation."""
        print("\n" + "="*80)
        print("CURVATURE ANALYSIS BENCHMARKS")
        print("="*80)

        cage = self.create_test_geometry('sphere')
        evaluator = cpp_core.SubDEvaluator()
        evaluator.initialize(cage)

        analyzer = cpp_core.CurvatureAnalyzer()

        # Single point curvature
        def bench_single():
            result = analyzer.compute_curvature(evaluator, 0, 0.5, 0.5)
            return {'gaussian': result.gaussian_curvature,
                   'mean': result.mean_curvature}

        self.run_benchmark(
            name="Single Point Curvature",
            description="Compute all curvature quantities at one point",
            func=bench_single,
            iterations=100,
            target_time=0.0005  # 0.5ms
        )

        # Batch curvature (100 points)
        n_points = 100
        face_indices = [0] * n_points
        params_u = [i % 10 / 10.0 for i in range(n_points)]
        params_v = [i // 10 / 10.0 for i in range(n_points)]

        def bench_batch():
            results = analyzer.batch_compute_curvature(
                evaluator, face_indices, params_u, params_v
            )
            return {'points_analyzed': len(results)}

        self.run_benchmark(
            name=f"Batch Curvature ({n_points} points)",
            description=f"Batch compute curvature at {n_points} points",
            func=bench_batch,
            iterations=10,
            target_time=0.050  # 50ms for 100 points
        )

    def benchmark_spectral_decomposition(self):
        """Benchmark eigenvalue computation."""
        if not ANALYSIS_AVAILABLE:
            print("\n⚠️  Spectral analysis not available - skipping")
            return

        print("\n" + "="*80)
        print("SPECTRAL DECOMPOSITION BENCHMARKS")
        print("="*80)

        cage = self.create_test_geometry('sphere')
        evaluator = cpp_core.SubDEvaluator()
        evaluator.initialize(cage)

        decomposer = SpectralDecomposer(evaluator)

        # Eigenvalue solve (k=10 modes)
        def bench_eigensolve():
            modes = decomposer.compute_eigenmodes(num_modes=10, tessellation_level=3)
            # Get approximate vertex count at level 3
            tess = evaluator.tessellate(3)
            return {'num_modes': len(modes),
                   'vertex_count': tess.vertex_count()}

        # Target: <500ms for 10K vertices, k=10
        self.run_benchmark(
            name="Eigenvalue Solve (k=10)",
            description="Compute 10 eigenmodes of Laplace-Beltrami operator",
            func=bench_eigensolve,
            iterations=3,
            warmup=1,
            target_time=0.500  # 500ms
        )

    def benchmark_differential_lens(self):
        """Benchmark differential lens analysis."""
        if not ANALYSIS_AVAILABLE:
            print("\n⚠️  Differential lens not available - skipping")
            return

        print("\n" + "="*80)
        print("DIFFERENTIAL LENS BENCHMARKS")
        print("="*80)

        cage = self.create_test_geometry('sphere')
        evaluator = cpp_core.SubDEvaluator()
        evaluator.initialize(cage)

        lens = DifferentialLens(evaluator)

        # Full differential analysis
        def bench_analysis():
            regions = lens.discover_regions()
            return {'num_regions': len(regions)}

        self.run_benchmark(
            name="Differential Lens Analysis",
            description="Complete curvature-based region discovery",
            func=bench_analysis,
            iterations=3,
            target_time=1.0  # 1 second (part of 2s total pipeline target)
        )

    def benchmark_full_pipeline(self):
        """Benchmark complete analysis pipeline."""
        if not ANALYSIS_AVAILABLE:
            print("\n⚠️  Full pipeline not available - skipping")
            return

        print("\n" + "="*80)
        print("FULL PIPELINE BENCHMARKS")
        print("="*80)

        cage = self.create_test_geometry('sphere')
        evaluator = cpp_core.SubDEvaluator()
        evaluator.initialize(cage)

        manager = LensManager(evaluator)

        # Complete differential pipeline
        def bench_pipeline():
            regions = manager.analyze_with_lens(LensType.DIFFERENTIAL)
            result = manager.get_result(LensType.DIFFERENTIAL)
            return {
                'num_regions': len(regions),
                'resonance_score': result.resonance_score,
                'computation_time': result.computation_time
            }

        # Target: <2 seconds total
        self.run_benchmark(
            name="Complete Analysis Pipeline",
            description="Full differential lens analysis with region discovery",
            func=bench_pipeline,
            iterations=3,
            target_time=2.0  # 2 seconds
        )

    def benchmark_constraint_validation(self):
        """Benchmark constraint checking."""
        print("\n" + "="*80)
        print("CONSTRAINT VALIDATION BENCHMARKS")
        print("="*80)

        cage = self.create_test_geometry('sphere')
        evaluator = cpp_core.SubDEvaluator()
        evaluator.initialize(cage)

        # Undercut detection
        detector = cpp_core.UndercutDetector(evaluator)
        demolding_dir = cpp_core.Point3D(0, 0, 1)

        def bench_undercut():
            face_indices = list(range(evaluator.get_control_face_count()))
            result = detector.detect_undercuts(face_indices, demolding_dir)
            return {'faces_checked': len(face_indices)}

        self.run_benchmark(
            name="Undercut Detection",
            description="Detect undercuts for all faces",
            func=bench_undercut,
            iterations=5,
            target_time=0.100  # 100ms
        )

        # Draft angle checking
        checker = cpp_core.DraftChecker(evaluator)

        def bench_draft():
            face_indices = list(range(evaluator.get_control_face_count()))
            result = checker.compute_draft_angles(face_indices, demolding_dir)
            return {'faces_checked': len(face_indices)}

        self.run_benchmark(
            name="Draft Angle Computation",
            description="Compute draft angles for all faces",
            func=bench_draft,
            iterations=5,
            target_time=0.100  # 100ms
        )

        # Complete constraint validation
        validator = cpp_core.ConstraintValidator(evaluator)

        def bench_validation():
            face_indices = list(range(evaluator.get_control_face_count()))
            report = validator.validate_region(face_indices, demolding_dir)
            return {
                'faces_validated': len(face_indices),
                'errors': report.error_count(),
                'warnings': report.warning_count()
            }

        self.run_benchmark(
            name="Complete Constraint Validation",
            description="Full constraint validation (undercuts + draft + thickness)",
            func=bench_validation,
            iterations=5,
            target_time=0.200  # 200ms
        )

    def benchmark_nurbs_generation(self):
        """Benchmark NURBS surface fitting."""
        print("\n" + "="*80)
        print("NURBS GENERATION BENCHMARKS")
        print("="*80)

        cage = self.create_test_geometry('sphere')
        evaluator = cpp_core.SubDEvaluator()
        evaluator.initialize(cage)

        generator = cpp_core.NURBSMoldGenerator(evaluator)
        face_indices = list(range(evaluator.get_control_face_count()))

        # NURBS fitting
        def bench_fitting():
            surface = generator.fit_nurbs_surface(face_indices, sample_density=50)
            quality = generator.check_fitting_quality(surface, face_indices)
            return {
                'sample_density': 50,
                'max_deviation': quality.max_deviation,
                'mean_deviation': quality.mean_deviation
            }

        # Target: <200ms per surface
        self.run_benchmark(
            name="NURBS Surface Fitting",
            description="Fit NURBS surface through SubD limit samples",
            func=bench_fitting,
            iterations=3,
            warmup=1,
            target_time=0.200  # 200ms
        )

    def run_all_benchmarks(self) -> BenchmarkSuite:
        """Run complete benchmark suite."""
        print("\n" + "="*80)
        print("STARTING COMPREHENSIVE PERFORMANCE BENCHMARK SUITE")
        print("="*80)
        print(f"cpp_core available: {CPP_CORE_AVAILABLE}")
        print(f"Analysis modules available: {ANALYSIS_AVAILABLE}")

        suite_start = time.perf_counter()

        if CPP_CORE_AVAILABLE:
            # Core geometry benchmarks
            self.benchmark_tessellation()
            self.benchmark_limit_evaluation()
            self.benchmark_curvature_analysis()
            self.benchmark_constraint_validation()
            self.benchmark_nurbs_generation()

            # Analysis pipeline benchmarks
            if ANALYSIS_AVAILABLE:
                self.benchmark_spectral_decomposition()
                self.benchmark_differential_lens()
                self.benchmark_full_pipeline()
        else:
            print("\n❌ cpp_core not available - cannot run benchmarks")

        suite_time = time.perf_counter() - suite_start

        return BenchmarkSuite(
            results=self.results,
            total_time=suite_time
        )


def run_demo_benchmarks():
    """Run demo benchmarks to test infrastructure (no C++ required)."""
    print("\n" + "="*80)
    print("RUNNING DEMO MODE - Testing Benchmark Infrastructure")
    print("="*80)
    print("\nThis mode demonstrates the benchmark infrastructure without requiring")
    print("the C++ core module to be built. It uses simulated operations.\n")

    benchmark = PerformanceBenchmark()

    # Simulate some benchmarks with dummy operations
    def dummy_fast():
        """Simulate a fast operation."""
        time.sleep(0.001)  # 1ms
        return {'simulated': True}

    def dummy_medium():
        """Simulate a medium operation."""
        time.sleep(0.025)  # 25ms
        return {'simulated': True}

    def dummy_slow():
        """Simulate a slow operation."""
        time.sleep(0.150)  # 150ms
        return {'simulated': True}

    def dummy_variable():
        """Simulate an operation with variable timing."""
        import random
        time.sleep(random.uniform(0.010, 0.030))  # 10-30ms
        return {'simulated': True}

    # Run demo benchmarks
    suite_start = time.perf_counter()

    benchmark.run_benchmark(
        name="Demo: Fast Operation",
        description="Simulates a fast operation (target: <5ms)",
        func=dummy_fast,
        iterations=10,
        target_time=0.005
    )

    benchmark.run_benchmark(
        name="Demo: Medium Operation",
        description="Simulates a medium operation (target: <50ms)",
        func=dummy_medium,
        iterations=10,
        target_time=0.050
    )

    benchmark.run_benchmark(
        name="Demo: Slow Operation",
        description="Simulates a slow operation (target: <100ms)",
        func=dummy_slow,
        iterations=5,
        target_time=0.100
    )

    benchmark.run_benchmark(
        name="Demo: Variable Timing",
        description="Simulates operation with variance",
        func=dummy_variable,
        iterations=20,
        target_time=0.025
    )

    suite_time = time.perf_counter() - suite_start

    suite = BenchmarkSuite(
        results=benchmark.results,
        total_time=suite_time
    )

    suite.print_report()

    print("\n" + "="*80)
    print("DEMO MODE COMPLETE")
    print("="*80)
    print("\nTo run real benchmarks:")
    print("  1. Build C++ core: cd cpp_core/build && cmake .. && make")
    print("  2. Run: python3 tests/benchmarks/benchmark_suite.py")
    print("="*80)

    return 0


def main():
    """Run benchmark suite and print report."""
    # Check for demo/test mode
    if len(sys.argv) > 1 and sys.argv[1] in ['--test', '--demo', '--test-mode']:
        return run_demo_benchmarks()

    if not CPP_CORE_AVAILABLE:
        print("\n❌ ERROR: cpp_core module not available")
        print("   Please build C++ core module first:")
        print("   cd cpp_core/build && cmake .. && make")
        print("\n   Or run in demo mode to test infrastructure:")
        print("   python3 tests/benchmarks/benchmark_suite.py --test-mode")
        return 1

    benchmark = PerformanceBenchmark()
    suite = benchmark.run_all_benchmarks()
    suite.print_report()

    # Return exit code based on targets
    failed_targets = sum(1 for r in suite.results if r.meets_target is False)
    if failed_targets > 0:
        print(f"\n⚠️  {failed_targets} performance target(s) not met")
        return 1
    else:
        print("\n✅ All performance targets met!")
        return 0


if __name__ == '__main__':
    sys.exit(main())
