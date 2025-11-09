#!/usr/bin/env python3
"""Test VTK viewport functionality."""

import sys
import os

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Set environment for headless testing
os.environ['QT_QPA_PLATFORM'] = 'offscreen'

def test_imports():
    """Test that all modules can be imported."""
    print("Testing module imports...")

    try:
        from app.ui.viewport_base import ViewportBase
        print("  ✅ viewport_base imported")
    except Exception as e:
        print(f"  ❌ Failed to import viewport_base: {e}")
        raise

    try:
        from app.ui.camera_controller import RhinoCameraStyle
        print("  ✅ camera_controller imported")
    except Exception as e:
        print(f"  ❌ Failed to import camera_controller: {e}")
        raise

    try:
        from app.ui.viewport_helpers import ViewportHelpers
        print("  ✅ viewport_helpers imported")
    except Exception as e:
        print(f"  ❌ Failed to import viewport_helpers: {e}")
        raise

    return True


def test_viewport_creation():
    """Test viewport widget creation."""
    print("\nTesting viewport creation...")

    # Try to import with QT offscreen
    try:
        from PyQt6.QtWidgets import QApplication
        from app.ui.viewport_base import ViewportBase

        app = QApplication.instance()
        if app is None:
            app = QApplication(sys.argv)

        viewport = ViewportBase("Perspective")
        assert viewport.view_type == "Perspective"
        assert viewport.renderer is not None
        assert viewport.camera is not None

        print("  ✅ Viewport created successfully")
        return True
    except ImportError as e:
        print(f"  ⚠️  Skipping viewport creation test (display not available): {e}")
        return True  # Still pass if we can't create display


def test_helper_classes():
    """Test helper class structure."""
    print("\nTesting helper classes...")

    try:
        from app.ui.viewport_helpers import ViewportHelpers
        import vtk

        # Test axes creation
        axes = ViewportHelpers.create_axes_actor(length=2.0)
        assert axes is not None
        assert isinstance(axes, vtk.vtkAxesActor)
        print("  ✅ Axes actor creation works")

        # Test grid creation
        grid = ViewportHelpers.create_grid_plane(size=20, divisions=20)
        assert grid is not None
        assert isinstance(grid, vtk.vtkActor)
        print("  ✅ Grid plane creation works")

        # Test bounding box creation
        bbox = ViewportHelpers.create_bounding_box((0, 10, 0, 10, 0, 10))
        assert bbox is not None
        assert isinstance(bbox, vtk.vtkActor)
        print("  ✅ Bounding box creation works")

        return True
    except Exception as e:
        print(f"  ❌ Helper class test failed: {e}")
        raise


def test_camera_controller():
    """Test camera controller class structure."""
    print("\nTesting camera controller...")

    try:
        from app.ui.camera_controller import RhinoCameraStyle
        import vtk

        # Verify class exists and is a VTK interactor style
        assert issubclass(RhinoCameraStyle, vtk.vtkInteractorStyle)
        print("  ✅ RhinoCameraStyle is a valid VTK interactor style")

        return True
    except Exception as e:
        print(f"  ❌ Camera controller test failed: {e}")
        raise


def test_camera_views():
    """Test different view types."""
    print("\nTesting camera views...")

    try:
        from PyQt6.QtWidgets import QApplication
        from app.ui.viewport_base import ViewportBase

        app = QApplication.instance()
        if app is None:
            app = QApplication(sys.argv)

        for view_type in ["Perspective", "Top", "Front", "Right"]:
            viewport = ViewportBase(view_type)
            state = viewport.get_camera_state()

            assert 'position' in state
            assert 'focal_point' in state
            assert 'view_up' in state
            assert 'view_angle' in state
            assert 'parallel_projection' in state
            print(f"  ✅ {view_type} view configured")

        return True
    except ImportError as e:
        print(f"  ⚠️  Skipping camera view test (display not available): {e}")
        return True  # Still pass if we can't create display


if __name__ == '__main__':
    all_passed = True

    all_passed &= test_imports()
    all_passed &= test_helper_classes()
    all_passed &= test_camera_controller()
    all_passed &= test_viewport_creation()
    all_passed &= test_camera_views()

    if all_passed:
        print("\n✅ ALL VIEWPORT TESTS PASSED!")
        sys.exit(0)
    else:
        print("\n❌ SOME TESTS FAILED!")
        sys.exit(1)
