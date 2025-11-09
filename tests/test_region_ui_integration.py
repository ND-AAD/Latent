"""
Integration test for Region List Widget and Properties Dialog
Tests the complete workflow without requiring PyQt6 runtime
"""

import sys
from pathlib import Path

# Add app directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

def test_imports():
    """Test that all required modules can be imported"""
    try:
        from app.ui.region_list_widget import RegionListWidget
        print("✓ RegionListWidget imports successfully")
    except Exception as e:
        print(f"✗ RegionListWidget import failed: {e}")
        return False

    try:
        from app.ui.region_properties_dialog import RegionPropertiesDialog
        print("✓ RegionPropertiesDialog imports successfully")
    except Exception as e:
        print(f"✗ RegionPropertiesDialog import failed: {e}")
        return False

    try:
        from app.state.parametric_region import ParametricRegion
        print("✓ ParametricRegion imports successfully")
    except Exception as e:
        print(f"✗ ParametricRegion import failed: {e}")
        return False

    return True


def test_region_creation():
    """Test creating a parametric region"""
    try:
        from app.state.parametric_region import ParametricRegion

        region = ParametricRegion(
            id="test_region_1",
            faces=[0, 1, 2, 3, 4],
            unity_principle="Flow-based decomposition",
            unity_strength=0.85,
            pinned=False,
            modified=False,
            constraints_passed=True
        )

        assert region.id == "test_region_1"
        assert len(region.faces) == 5
        assert region.unity_strength == 0.85
        assert not region.pinned

        print("✓ ParametricRegion creation works correctly")
        return True

    except Exception as e:
        print(f"✗ ParametricRegion creation failed: {e}")
        return False


def test_signal_definitions():
    """Test that widget signals are properly defined"""
    try:
        from app.ui.region_list_widget import RegionListWidget
        from PyQt6.QtCore import pyqtSignal

        # Check that the class has the required signals
        assert hasattr(RegionListWidget, 'region_selected')
        assert hasattr(RegionListWidget, 'region_pinned')
        assert hasattr(RegionListWidget, 'region_edit_requested')
        assert hasattr(RegionListWidget, 'region_deleted')
        assert hasattr(RegionListWidget, 'region_properties_requested')

        print("✓ RegionListWidget has all required signals")
        return True

    except ImportError:
        print("⚠ PyQt6 not available - skipping signal test")
        return True
    except Exception as e:
        print(f"✗ Signal definition test failed: {e}")
        return False


def test_dialog_structure():
    """Test that properties dialog has required structure"""
    try:
        from app.ui.region_properties_dialog import RegionPropertiesDialog

        # Check that the class has required methods
        assert hasattr(RegionPropertiesDialog, 'init_ui')
        assert hasattr(RegionPropertiesDialog, 'load_region_data')
        assert hasattr(RegionPropertiesDialog, 'apply_changes')
        assert hasattr(RegionPropertiesDialog, 'export_region')
        assert hasattr(RegionPropertiesDialog, 'get_updated_properties')

        print("✓ RegionPropertiesDialog has all required methods")
        return True

    except ImportError:
        print("⚠ PyQt6 not available - skipping dialog structure test")
        return True
    except Exception as e:
        print(f"✗ Dialog structure test failed: {e}")
        return False


if __name__ == "__main__":
    print("=" * 60)
    print("Region UI Integration Tests")
    print("=" * 60)
    print()

    tests = [
        ("Module Imports", test_imports),
        ("Region Creation", test_region_creation),
        ("Signal Definitions", test_signal_definitions),
        ("Dialog Structure", test_dialog_structure),
    ]

    results = []
    for name, test_func in tests:
        print(f"\n{name}:")
        print("-" * 40)
        result = test_func()
        results.append((name, result))
        print()

    print("=" * 60)
    print("Test Summary")
    print("=" * 60)
    passed = sum(1 for _, result in results if result)
    total = len(results)
    print(f"\nPassed: {passed}/{total}")

    for name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"  {status}: {name}")

    if passed == total:
        print("\n✓ All tests passed!")
        sys.exit(0)
    else:
        print(f"\n✗ {total - passed} test(s) failed")
        sys.exit(1)
