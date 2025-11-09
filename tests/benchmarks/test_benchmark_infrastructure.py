#!/usr/bin/env python3
"""
Test Benchmark Infrastructure

Verifies that the benchmark suite infrastructure works correctly
without requiring the C++ core to be built.

Author: Agent 61, Day 9 API Sprint
Date: November 2025
"""

import pytest
import time
from pathlib import Path
import sys

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from tests.benchmarks.benchmark_suite import (
    BenchmarkResult,
    BenchmarkSuite,
    PerformanceBenchmark
)


class TestBenchmarkInfrastructure:
    """Test the benchmark infrastructure itself."""

    def test_benchmark_result_creation(self):
        """Test creating a BenchmarkResult."""
        result = BenchmarkResult(
            name="Test Benchmark",
            description="Test description",
            iterations=5,
            times=[0.1, 0.11, 0.09, 0.10, 0.12],
            mean_time=0.104,
            median_time=0.10,
            std_dev=0.011,
            min_time=0.09,
            max_time=0.12,
            target_time=0.15,
            metadata={'test': True}
        )

        assert result.name == "Test Benchmark"
        assert result.iterations == 5
        assert result.mean_time == 0.104
        assert result.meets_target is True
        assert result.metadata['test'] is True

    def test_benchmark_result_missing_target(self):
        """Test BenchmarkResult when target is not met."""
        result = BenchmarkResult(
            name="Slow Benchmark",
            description="Test slow operation",
            iterations=3,
            times=[0.2, 0.21, 0.19],
            mean_time=0.20,
            median_time=0.20,
            std_dev=0.01,
            min_time=0.19,
            max_time=0.21,
            target_time=0.10  # Target is 100ms, but taking 200ms
        )

        assert result.meets_target is False

    def test_benchmark_result_no_target(self):
        """Test BenchmarkResult without a target."""
        result = BenchmarkResult(
            name="Untargeted Benchmark",
            description="No specific target",
            iterations=5,
            times=[0.1] * 5,
            mean_time=0.1,
            median_time=0.1,
            std_dev=0.0,
            min_time=0.1,
            max_time=0.1
        )

        assert result.target_time is None
        assert result.meets_target is None

    def test_run_benchmark_basic(self):
        """Test running a basic benchmark."""
        benchmark = PerformanceBenchmark()

        def dummy_func():
            time.sleep(0.001)  # 1ms
            return {}

        result = benchmark.run_benchmark(
            name="Test Operation",
            description="Simple test",
            func=dummy_func,
            iterations=3,
            warmup=0,
            target_time=0.01  # 10ms
        )

        assert result is not None
        assert result.name == "Test Operation"
        assert result.iterations == 3
        assert result.mean_time > 0
        assert result.mean_time < 0.01  # Should be well under 10ms
        assert result.meets_target is True

    def test_run_benchmark_with_metadata(self):
        """Test benchmark with metadata return."""
        benchmark = PerformanceBenchmark()

        def func_with_metadata():
            time.sleep(0.001)
            return {'vertex_count': 1000, 'success': True}

        result = benchmark.run_benchmark(
            name="Metadata Test",
            description="Test metadata",
            func=func_with_metadata,
            iterations=2
        )

        assert 'vertex_count' in result.metadata
        assert result.metadata['vertex_count'] == 1000
        assert result.metadata['success'] is True

    def test_run_benchmark_with_failure(self):
        """Test benchmark that fails."""
        benchmark = PerformanceBenchmark()

        call_count = [0]

        def failing_func():
            call_count[0] += 1
            if call_count[0] <= 2:
                raise ValueError("Simulated failure")
            time.sleep(0.001)
            return {}

        result = benchmark.run_benchmark(
            name="Failing Test",
            description="Test failure handling",
            func=failing_func,
            iterations=5,
            warmup=0
        )

        # Should have some successful iterations (after the first 2 fail)
        assert result is not None
        assert result.iterations < 5  # Some iterations failed
        assert result.iterations >= 3  # But some succeeded

    def test_benchmark_suite_creation(self):
        """Test creating a BenchmarkSuite."""
        results = [
            BenchmarkResult(
                name="Test 1",
                description="First test",
                iterations=5,
                times=[0.1] * 5,
                mean_time=0.1,
                median_time=0.1,
                std_dev=0.0,
                min_time=0.1,
                max_time=0.1
            ),
            BenchmarkResult(
                name="Test 2",
                description="Second test",
                iterations=3,
                times=[0.2] * 3,
                mean_time=0.2,
                median_time=0.2,
                std_dev=0.0,
                min_time=0.2,
                max_time=0.2
            )
        ]

        suite = BenchmarkSuite(
            results=results,
            total_time=1.5
        )

        assert len(suite.results) == 2
        assert suite.total_time == 1.5

    def test_create_test_geometry_cube(self):
        """Test geometry creation (requires cpp_core)."""
        try:
            import cpp_core
            # Check if cpp_core is actually built (has SubDControlCage)
            if not hasattr(cpp_core, 'SubDControlCage'):
                pytest.skip("cpp_core not fully built")

            benchmark = PerformanceBenchmark()
            cage = benchmark.create_test_geometry('cube')

            assert cage.vertex_count() == 8
            assert cage.face_count() == 6
        except ImportError:
            pytest.skip("cpp_core not available")

    def test_create_test_geometry_sphere(self):
        """Test sphere geometry creation (requires cpp_core)."""
        try:
            import cpp_core
            if not hasattr(cpp_core, 'SubDControlCage'):
                pytest.skip("cpp_core not fully built")

            benchmark = PerformanceBenchmark()
            cage = benchmark.create_test_geometry('sphere')

            assert cage.vertex_count() == 6  # Octahedron
            assert cage.face_count() == 8
        except ImportError:
            pytest.skip("cpp_core not available")

    def test_create_test_geometry_cylinder(self):
        """Test cylinder geometry creation (requires cpp_core)."""
        try:
            import cpp_core
            if not hasattr(cpp_core, 'SubDControlCage'):
                pytest.skip("cpp_core not fully built")

            benchmark = PerformanceBenchmark()
            cage = benchmark.create_test_geometry('cylinder')

            assert cage.vertex_count() == 8
            assert cage.face_count() == 6
        except ImportError:
            pytest.skip("cpp_core not available")

    def test_benchmark_statistics(self):
        """Test statistical calculations."""
        times = [0.10, 0.11, 0.09, 0.10, 0.15, 0.09, 0.10]

        import statistics
        mean = statistics.mean(times)
        median = statistics.median(times)
        std_dev = statistics.stdev(times)
        min_time = min(times)
        max_time = max(times)

        # Verify calculations are reasonable
        assert 0.09 <= mean <= 0.15
        assert median == 0.10
        assert std_dev > 0
        assert min_time == 0.09
        assert max_time == 0.15

        result = BenchmarkResult(
            name="Stats Test",
            description="Test statistics",
            iterations=len(times),
            times=times,
            mean_time=mean,
            median_time=median,
            std_dev=std_dev,
            min_time=min_time,
            max_time=max_time
        )

        assert result.mean_time == mean
        assert result.median_time == median

    def test_high_variance_detection(self):
        """Test detection of high variance operations."""
        # Low variance
        low_var_times = [0.100, 0.101, 0.099, 0.100, 0.102]
        low_var_result = BenchmarkResult(
            name="Low Variance",
            description="Consistent timing",
            iterations=5,
            times=low_var_times,
            mean_time=0.1,
            median_time=0.1,
            std_dev=0.0012,
            min_time=0.099,
            max_time=0.102
        )

        # High variance (>30% of mean) - wider range
        high_var_times = [0.100, 0.200, 0.050, 0.180, 0.070]
        import statistics
        high_var_result = BenchmarkResult(
            name="High Variance",
            description="Inconsistent timing",
            iterations=5,
            times=high_var_times,
            mean_time=statistics.mean(high_var_times),
            median_time=statistics.median(high_var_times),
            std_dev=statistics.stdev(high_var_times),
            min_time=min(high_var_times),
            max_time=max(high_var_times)
        )

        # Low variance should be <30% of mean
        assert low_var_result.std_dev < low_var_result.mean_time * 0.3

        # High variance should be >30% of mean
        assert high_var_result.std_dev > high_var_result.mean_time * 0.3


class TestBenchmarkReporting:
    """Test benchmark reporting functionality."""

    def test_suite_report_generation(self, capsys):
        """Test that suite report can be generated."""
        results = [
            BenchmarkResult(
                name="Fast Op",
                description="Fast operation",
                iterations=5,
                times=[0.001] * 5,
                mean_time=0.001,
                median_time=0.001,
                std_dev=0.0,
                min_time=0.001,
                max_time=0.001,
                target_time=0.01  # Meets target
            ),
            BenchmarkResult(
                name="Slow Op",
                description="Slow operation",
                iterations=3,
                times=[0.2] * 3,
                mean_time=0.2,
                median_time=0.2,
                std_dev=0.0,
                min_time=0.2,
                max_time=0.2,
                target_time=0.1  # Misses target
            )
        ]

        suite = BenchmarkSuite(results=results, total_time=1.0)
        suite.print_report()

        captured = capsys.readouterr()
        output = captured.out

        # Check that report contains expected sections
        assert "PERFORMANCE BENCHMARK SUITE" in output
        assert "DETAILED RESULTS" in output
        assert "OPTIMIZATION OPPORTUNITIES" in output
        assert "Fast Op" in output
        assert "Slow Op" in output
        assert "PASS" in output
        assert "MISS" in output


def test_demo_mode_runs():
    """Test that demo mode can execute successfully."""
    from tests.benchmarks.benchmark_suite import run_demo_benchmarks

    exit_code = run_demo_benchmarks()
    assert exit_code == 0


if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short'])
