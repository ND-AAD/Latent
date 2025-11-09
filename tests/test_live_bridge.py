#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Test live bridge change detection."""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Add cpp_core to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'cpp_core' / 'build'))

try:
    import cpp_core
except ImportError:
    print("[WARN] cpp_core module not available. Build C++ module first.")
    cpp_core = None

from app.bridge.live_bridge import LiveBridge
from app.bridge.subd_fetcher import SubDFetcher


def test_hash_computation():
    """Test cage hash computation."""
    print("Testing hash computation...")

    if cpp_core is None:
        print("  [WARN] cpp_core not available, skipping test")
        return True

    # Create identical cages
    cage1 = cpp_core.SubDControlCage()
    cage1.vertices = [
        cpp_core.Point3D(0, 0, 0),
        cpp_core.Point3D(1, 0, 0),
        cpp_core.Point3D(1, 1, 0),
        cpp_core.Point3D(0, 1, 0)
    ]
    cage1.faces = [[0, 1, 2, 3]]

    cage2 = cpp_core.SubDControlCage()
    cage2.vertices = [
        cpp_core.Point3D(0, 0, 0),
        cpp_core.Point3D(1, 0, 0),
        cpp_core.Point3D(1, 1, 0),
        cpp_core.Point3D(0, 1, 0)
    ]
    cage2.faces = [[0, 1, 2, 3]]

    # Create bridge (dummy callback)
    bridge = LiveBridge(
        fetcher=None,
        on_geometry_changed=lambda c: None
    )

    # Compute hashes
    hash1 = bridge._compute_cage_hash(cage1)
    hash2 = bridge._compute_cage_hash(cage2)

    print(f"  Hash 1: {hash1[:16]}...")
    print(f"  Hash 2: {hash2[:16]}...")

    assert hash1 == hash2, "Identical cages should have same hash"
    print("  [PASS] Identical cages have same hash")

    # Modify cage2
    cage2.vertices[0].x = 0.1

    hash3 = bridge._compute_cage_hash(cage2)
    print(f"  Hash 3: {hash3[:16]}... (after modification)")

    assert hash1 != hash3, "Different cages should have different hash"
    print("  [PASS] Different cages have different hash")

    return True


def test_connection_status():
    """Test connection status reporting."""
    print("\nTesting connection status...")

    fetcher = SubDFetcher()

    change_count = [0]  # Mutable for closure

    def on_change(cage):
        change_count[0] += 1
        if cpp_core:
            print(f"  Change detected: {cage.vertex_count()} vertices")
        else:
            print("  Change detected (cpp_core not available)")

    bridge = LiveBridge(fetcher, on_change, poll_interval_ms=1000)

    # Check initial status
    status = bridge.get_connection_status()
    assert not status['connected']
    assert not status['active']
    print("  [PASS] Initial status correct (disconnected)")

    # Try to start (may fail if server not running)
    if fetcher.is_server_available():
        bridge.start()
        status = bridge.get_connection_status()
        assert status['connected']
        assert status['active']
        print("  [PASS] Active status correct (connected)")

        bridge.stop()
        status = bridge.get_connection_status()
        assert not status['active']
        print("  [PASS] Stopped status correct")
    else:
        print("  [WARN] Server not available, skipping active tests")

    return True


def main():
    print("=" * 60)
    print("Testing Live Bridge")
    print("=" * 60)
    print()

    try:
        success = True

        # Run tests
        success = test_hash_computation() and success
        success = test_connection_status() and success

        print("\n" + "=" * 60)
        if success:
            print("[PASS] ALL TESTS PASSED")
        else:
            print("[FAIL] SOME TESTS FAILED")
        print("=" * 60)
        return 0 if success else 1

    except AssertionError as e:
        print(f"\n[FAIL] TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return 1
    except Exception as e:
        print(f"\n[FAIL] UNEXPECTED ERROR: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())
