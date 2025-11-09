#!/usr/bin/env python3
"""Test tessellation at different subdivision levels."""

import sys
sys.path.insert(0, 'cpp_core/build')

import cpp_core
from app.bridge.subd_fetcher import SubDFetcher


def main():
    print("Testing tessellation levels...")

    # Fetch geometry
    fetcher = SubDFetcher()

    if not fetcher.is_server_available():
        print("❌ Server not available")
        return 1

    cage = fetcher.fetch_control_cage()
    if cage is None:
        print("❌ Failed to fetch cage")
        return 1

    print(f"\nControl cage: {cage.vertex_count()} vertices, "
          f"{cage.face_count()} faces\n")

    # Test subdivision levels
    evaluator = cpp_core.SubDEvaluator()
    evaluator.initialize(cage)

    for level in range(1, 5):
        result = evaluator.tessellate(level)
        print(f"Level {level}: {result.vertex_count():6d} vertices, "
              f"{result.triangle_count():6d} triangles")

        # Verify data integrity
        assert result.vertices.shape[0] == result.vertex_count()
        assert result.triangles.shape[0] == result.triangle_count()
        assert len(result.face_parents) == result.triangle_count()

    print("\n✅ All levels working correctly")
    return 0


if __name__ == '__main__':
    sys.exit(main())
