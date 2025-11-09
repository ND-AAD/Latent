#!/usr/bin/env python3
"""
Test Grasshopper HTTP Server
==============================

Tests the Grasshopper control cage HTTP server.

Usage:
  1. Start Grasshopper server with SubD geometry
  2. Run: python3 test_gh_server.py

Expected:
  - Server running on http://localhost:8888
  - /status endpoint returns status
  - /geometry endpoint returns control cage data
"""

import requests
import json
import sys


def test_status():
    """Test /status endpoint."""
    print("Testing /status endpoint...")

    try:
        response = requests.get('http://localhost:8888/status', timeout=2)
        response.raise_for_status()

        data = response.json()
        print(f"  Status: {data['status']}")
        print(f"  Port: {data['port']}")
        print(f"  Has geometry: {data['has_geometry']}")
        print("  ✅ Status endpoint working\n")
        return True

    except requests.exceptions.ConnectionError:
        print("  ❌ Failed: Cannot connect to server")
        print("     Make sure Grasshopper server is running!\n")
        return False
    except Exception as e:
        print(f"  ❌ Failed: {e}\n")
        return False


def test_geometry():
    """Test /geometry endpoint."""
    print("Testing /geometry endpoint...")

    try:
        response = requests.get('http://localhost:8888/geometry', timeout=2)
        response.raise_for_status()

        data = response.json()

        # Check for error response
        if 'error' in data:
            print(f"  ⚠️  Server returned error: {data['error']}")
            print("     Make sure SubD geometry is connected in Grasshopper\n")
            return False

        # Check structure
        assert 'vertices' in data, "Missing vertices"
        assert 'faces' in data, "Missing faces"
        assert 'metadata' in data, "Missing metadata"
        assert 'creases' in data, "Missing creases"

        meta = data['metadata']
        print(f"  Vertices: {meta['vertex_count']}")
        print(f"  Faces: {meta['face_count']}")
        print(f"  Edges: {meta['edge_count']}")
        print(f"  Creases: {meta['crease_count']}")

        # Validate data
        assert len(data['vertices']) == meta['vertex_count'], \
            f"Vertex count mismatch: {len(data['vertices'])} vs {meta['vertex_count']}"
        assert len(data['faces']) == meta['face_count'], \
            f"Face count mismatch: {len(data['faces'])} vs {meta['face_count']}"

        # Check vertex format
        if data['vertices']:
            v = data['vertices'][0]
            assert len(v) == 3, f"Vertex should be [x,y,z], got {len(v)} elements"
            assert all(isinstance(c, (int, float)) for c in v), \
                "Vertex coordinates should be numbers"
            print(f"  Sample vertex: [{v[0]:.3f}, {v[1]:.3f}, {v[2]:.3f}]")

        # Check face format
        if data['faces']:
            f = data['faces'][0]
            assert all(isinstance(i, int) for i in f), \
                "Face indices should be integers"
            assert all(0 <= i < meta['vertex_count'] for i in f), \
                f"Face indices out of range [0, {meta['vertex_count']})"
            print(f"  Sample face: {f[:4]}{'...' if len(f) > 4 else ''} ({len(f)} vertices)")

        # Check crease format
        if data['creases']:
            c = data['creases'][0]
            assert len(c) == 3, "Crease should be [v1, v2, sharpness]"
            assert isinstance(c[0], int) and isinstance(c[1], int), \
                "Crease vertex indices should be integers"
            assert isinstance(c[2], (int, float)), \
                "Crease sharpness should be a number"
            print(f"  Sample crease: vertex {c[0]} -> {c[1]}, sharpness {c[2]}")
        else:
            print("  No creases (smooth SubD)")

        print("  ✅ Geometry endpoint working\n")
        return True

    except requests.exceptions.ConnectionError:
        print("  ❌ Failed: Cannot connect to server")
        print("     Make sure Grasshopper server is running!\n")
        return False
    except AssertionError as e:
        print(f"  ❌ Validation failed: {e}\n")
        import traceback
        traceback.print_exc()
        return False
    except Exception as e:
        print(f"  ❌ Failed: {e}\n")
        import traceback
        traceback.print_exc()
        return False


def test_data_integrity():
    """Test data integrity and relationships."""
    print("Testing data integrity...")

    try:
        response = requests.get('http://localhost:8888/geometry', timeout=2)
        response.raise_for_status()
        data = response.json()

        if 'error' in data:
            print("  ⚠️  Skipping (no geometry available)\n")
            return True

        vertices = data['vertices']
        faces = data['faces']
        creases = data['creases']
        vertex_count = len(vertices)

        # Check all face indices are valid
        for i, face in enumerate(faces):
            for v_idx in face:
                assert 0 <= v_idx < vertex_count, \
                    f"Face {i} has invalid vertex index {v_idx}"

        # Check all crease indices are valid
        for i, crease in enumerate(creases):
            assert 0 <= crease[0] < vertex_count, \
                f"Crease {i} has invalid start vertex {crease[0]}"
            assert 0 <= crease[1] < vertex_count, \
                f"Crease {i} has invalid end vertex {crease[1]}"
            assert 0 <= crease[2] <= 1.0, \
                f"Crease {i} has invalid sharpness {crease[2]} (should be 0-1)"

        # Check face topology (should have at least 3 vertices)
        for i, face in enumerate(faces):
            assert len(face) >= 3, \
                f"Face {i} has only {len(face)} vertices (needs at least 3)"

        print("  ✅ Data integrity validated\n")
        return True

    except requests.exceptions.ConnectionError:
        print("  ⚠️  Skipping (server not running)\n")
        return True  # Don't fail if server isn't running
    except AssertionError as e:
        print(f"  ❌ Integrity check failed: {e}\n")
        return False
    except Exception as e:
        print(f"  ❌ Failed: {e}\n")
        import traceback
        traceback.print_exc()
        return False


def show_sample_output():
    """Show sample JSON output."""
    print("Sample JSON output:")

    try:
        response = requests.get('http://localhost:8888/geometry', timeout=2)
        response.raise_for_status()
        data = response.json()

        if 'error' in data:
            print("  (No geometry available)")
            return

        # Show truncated version
        sample = {
            'vertices': data['vertices'][:3] if data['vertices'] else [],
            'faces': data['faces'][:3] if data['faces'] else [],
            'creases': data['creases'][:3] if data['creases'] else [],
            'metadata': data['metadata']
        }

        print(json.dumps(sample, indent=2))
        print()

    except:
        print("  (Unable to fetch sample)")
        print()


def main():
    """Run all tests."""
    print("=" * 60)
    print("Testing Grasshopper HTTP Server - Control Cage Transfer")
    print("=" * 60)
    print()

    # Test both endpoints
    status_ok = test_status()
    geometry_ok = test_geometry()
    integrity_ok = test_data_integrity()

    # Show sample output
    if status_ok and geometry_ok:
        show_sample_output()

    print("=" * 60)
    if status_ok and geometry_ok and integrity_ok:
        print("✅ ALL TESTS PASSED")
        print("=" * 60)
        return 0
    else:
        print("❌ SOME TESTS FAILED")
        print("=" * 60)
        print()
        print("Troubleshooting:")
        print("1. Make sure Grasshopper is running with server component")
        print("2. Verify SubD geometry is connected to component")
        print("3. Check Run input is set to True")
        print("4. Verify no firewall blocking port 8888")
        return 1


if __name__ == '__main__':
    sys.exit(main())
