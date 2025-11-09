"""
Test script for Grasshopper POST /molds endpoint.

This script tests the mold import functionality by sending test mold data
to the Grasshopper HTTP server.

Usage:
    python tests/test_grasshopper_post.py
"""

import json
import requests
import sys
from pathlib import Path


def test_mold_post(url="http://localhost:8888/molds", test_file="tests/test_mold.json"):
    """
    Test POST /molds endpoint with test mold data.

    Args:
        url: URL of the POST endpoint
        test_file: Path to test mold JSON file
    """
    # Load test mold data
    test_path = Path(__file__).parent.parent / test_file

    if not test_path.exists():
        print(f"❌ Test file not found: {test_path}")
        return False

    with open(test_path, 'r') as f:
        mold_data = json.load(f)

    print(f"📤 Sending {len(mold_data['molds'])} molds to {url}")
    print(f"   Test file: {test_path}")

    # Send POST request
    try:
        response = requests.post(
            url,
            json=mold_data,
            headers={'Content-Type': 'application/json'},
            timeout=10
        )

        # Check response
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Success! Imported {result['imported_count']} molds")
            print(f"   GUIDs: {result['guids']}")
            return True
        else:
            print(f"❌ Request failed with status {response.status_code}")
            print(f"   Response: {response.text}")
            return False

    except requests.exceptions.ConnectionError:
        print(f"❌ Connection failed - is Grasshopper server running at {url}?")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def test_invalid_data(url="http://localhost:8888/molds"):
    """Test endpoint with invalid data to verify error handling."""

    print("\n📤 Testing error handling with invalid data...")

    # Test 1: Invalid type
    invalid_data = {
        "type": "wrong_type",
        "molds": []
    }

    try:
        response = requests.post(
            url,
            json=invalid_data,
            headers={'Content-Type': 'application/json'},
            timeout=10
        )

        if response.status_code == 400:
            print("✅ Correctly rejected invalid data type")
        else:
            print(f"❌ Expected 400 status, got {response.status_code}")

    except Exception as e:
        print(f"❌ Error: {e}")


def test_status(url="http://localhost:8888/status"):
    """Test server status endpoint."""

    print("\n📤 Testing server status...")

    try:
        response = requests.get(url, timeout=5)

        if response.status_code == 200:
            status = response.json()
            print(f"✅ Server is running")
            print(f"   Status: {status}")
            return True
        else:
            print(f"❌ Status check failed: {response.status_code}")
            return False

    except requests.exceptions.ConnectionError:
        print(f"❌ Connection failed - is Grasshopper server running?")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def main():
    """Run all tests."""

    print("=" * 60)
    print("GRASSHOPPER POST ENDPOINT TEST")
    print("=" * 60)

    # Test 1: Server status
    if not test_status():
        print("\n⚠️  Server not running. Start Grasshopper server and try again.")
        sys.exit(1)

    # Test 2: Valid mold data
    success = test_mold_post()

    # Test 3: Invalid data (error handling)
    test_invalid_data()

    print("\n" + "=" * 60)
    if success:
        print("✅ ALL TESTS PASSED")
    else:
        print("❌ SOME TESTS FAILED")
    print("=" * 60)

    return 0 if success else 1


if __name__ == '__main__':
    sys.exit(main())
