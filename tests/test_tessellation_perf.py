#!/usr/bin/env python3
"""Benchmark tessellation performance."""

import sys
import time
sys.path.insert(0, 'cpp_core/build')

import cpp_core
from app.bridge.subd_fetcher import SubDFetcher


def main():
    print("Benchmarking tessellation performance...")

    fetcher = SubDFetcher()
    cage = fetcher.fetch_control_cage()

    if cage is None:
        print("❌ No geometry available")
        return 1

    evaluator = cpp_core.SubDEvaluator()

    # Benchmark initialization
    start = time.time()
    evaluator.initialize(cage)
    init_time = time.time() - start

    print(f"\nInitialization: {init_time*1000:.2f} ms")

    # Benchmark tessellation at different levels
    for level in [1, 2, 3, 4]:
        times = []
        for _ in range(5):  # 5 runs
            start = time.time()
            result = evaluator.tessellate(level)
            times.append(time.time() - start)

        avg_time = sum(times) / len(times) * 1000
        print(f"Level {level}: {avg_time:6.2f} ms avg "
              f"({result.triangle_count()} triangles)")

    # Benchmark limit evaluation
    n_points = 10000
    start = time.time()
    for i in range(n_points):
        u = (i % 100) / 100.0
        v = (i // 100) / 100.0
        pt = evaluator.evaluate_limit_point(0, u, v)
    eval_time = time.time() - start

    print(f"\nLimit evaluation: {n_points} points in "
          f"{eval_time*1000:.2f} ms")
    print(f"  ({n_points/eval_time:.0f} points/sec)")

    print("\n✅ Performance tests complete")
    return 0


if __name__ == '__main__':
    sys.exit(main())
