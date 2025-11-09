#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test Multi-Viewport Layout Manager

Tests for viewport layout configurations, camera independence,
active viewport tracking, and layout switching functionality.
"""

import sys
import os
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Set headless mode for Qt
os.environ['QT_QPA_PLATFORM'] = 'offscreen'

try:
    from PyQt6.QtWidgets import QApplication
    from app.ui.viewport_layout import ViewportLayoutManager, ViewportLayout, ViewType
    PYQT_AVAILABLE = True
except ImportError as e:
    print(f"[WARN] PyQt6 not available: {e}")
    print("       Layout tests will be skipped")
    PYQT_AVAILABLE = False


def get_or_create_qapp():
    """Get existing QApplication or create new one"""
    if not PYQT_AVAILABLE:
        return None
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    return app


def test_layout_modes():
    """Test all 4 layout modes create correct number of viewports"""
    print("Testing layout modes...")

    if not PYQT_AVAILABLE:
        print("  [SKIP] PyQt6 not available")
        return True

    app = get_or_create_qapp()
    layout_manager = ViewportLayoutManager()

    # Test SINGLE layout
    layout_manager.set_layout(ViewportLayout.SINGLE)
    assert len(layout_manager.viewports) == 1, "SINGLE layout should have 1 viewport"
    assert layout_manager.current_layout == ViewportLayout.SINGLE
    print("  [PASS] SINGLE layout: 1 viewport")

    # Test TWO_HORIZONTAL layout
    layout_manager.set_layout(ViewportLayout.TWO_HORIZONTAL)
    assert len(layout_manager.viewports) == 2, "TWO_HORIZONTAL layout should have 2 viewports"
    assert layout_manager.current_layout == ViewportLayout.TWO_HORIZONTAL
    print("  [PASS] TWO_HORIZONTAL layout: 2 viewports")

    # Test TWO_VERTICAL layout
    layout_manager.set_layout(ViewportLayout.TWO_VERTICAL)
    assert len(layout_manager.viewports) == 2, "TWO_VERTICAL layout should have 2 viewports"
    assert layout_manager.current_layout == ViewportLayout.TWO_VERTICAL
    print("  [PASS] TWO_VERTICAL layout: 2 viewports")

    # Test FOUR_GRID layout
    layout_manager.set_layout(ViewportLayout.FOUR_GRID)
    assert len(layout_manager.viewports) == 4, "FOUR_GRID layout should have 4 viewports"
    assert layout_manager.current_layout == ViewportLayout.FOUR_GRID
    print("  [PASS] FOUR_GRID layout: 4 viewports")

    return True


def test_camera_independence():
    """Test that each viewport has independent camera"""
    print("\nTesting camera independence...")

    if not PYQT_AVAILABLE:
        print("  [SKIP] PyQt6 not available")
        return True

    app = get_or_create_qapp()
    layout_manager = ViewportLayoutManager()

    # Use FOUR_GRID for maximum viewport count
    layout_manager.set_layout(ViewportLayout.FOUR_GRID)

    # Get cameras from all viewports
    cameras = []
    for viewport in layout_manager.viewports:
        camera = viewport.renderer.GetActiveCamera()
        cameras.append(camera)

    # Verify all cameras are different objects
    for i in range(len(cameras)):
        for j in range(i + 1, len(cameras)):
            # Compare object identity, not equality
            assert cameras[i] is not cameras[j], f"Viewport {i} and {j} share the same camera object"

    print(f"  [PASS] All {len(cameras)} viewports have independent cameras")

    # Verify cameras have different initial positions/orientations
    positions = [camera.GetPosition() for camera in cameras]

    # Cameras should have different view types and thus different positions
    unique_positions = set(positions)
    assert len(unique_positions) >= 2, "Viewports should have different camera positions"
    print(f"  [PASS] Cameras have {len(unique_positions)} unique positions")

    return True


def test_active_viewport_tracking():
    """Test active viewport tracking and visual indication"""
    print("\nTesting active viewport tracking...")

    if not PYQT_AVAILABLE:
        print("  [SKIP] PyQt6 not available")
        return True

    app = get_or_create_qapp()
    layout_manager = ViewportLayoutManager()

    layout_manager.set_layout(ViewportLayout.FOUR_GRID)

    # Test setting each viewport as active
    for i in range(len(layout_manager.viewports)):
        layout_manager.set_active_viewport(i)

        # Verify active index updated
        assert layout_manager.active_viewport_index == i, f"Active index should be {i}"

        # Verify correct viewport is marked active
        for j, viewport in enumerate(layout_manager.viewports):
            if j == i:
                assert viewport.is_active, f"Viewport {i} should be active"
            else:
                assert not viewport.is_active, f"Viewport {j} should not be active"

        print(f"  [PASS] Viewport {i} correctly set as active")

    # Test get_active_viewport
    layout_manager.set_active_viewport(2)
    active = layout_manager.get_active_viewport()
    assert active is layout_manager.viewports[2], "get_active_viewport should return correct viewport"
    print("  [PASS] get_active_viewport returns correct viewport")

    return True


def test_layout_switching():
    """Test switching between layouts preserves geometry"""
    print("\nTesting layout switching...")

    if not PYQT_AVAILABLE:
        print("  [SKIP] PyQt6 not available")
        return True

    app = get_or_create_qapp()
    layout_manager = ViewportLayoutManager()

    # Start with SINGLE layout
    layout_manager.set_layout(ViewportLayout.SINGLE)
    initial_viewport_count = len(layout_manager.viewports)

    # Switch to FOUR_GRID
    layout_manager.set_layout(ViewportLayout.FOUR_GRID)
    assert len(layout_manager.viewports) == 4, "Should have 4 viewports after switch"
    print("  [PASS] Switch from SINGLE to FOUR_GRID")

    # Switch to TWO_HORIZONTAL
    layout_manager.set_layout(ViewportLayout.TWO_HORIZONTAL)
    assert len(layout_manager.viewports) == 2, "Should have 2 viewports after switch"
    print("  [PASS] Switch from FOUR_GRID to TWO_HORIZONTAL")

    # Switch back to SINGLE
    layout_manager.set_layout(ViewportLayout.SINGLE)
    assert len(layout_manager.viewports) == 1, "Should have 1 viewport after switch"
    print("  [PASS] Switch from TWO_HORIZONTAL to SINGLE")

    return True


def test_viewport_view_types():
    """Test that viewports have correct view types assigned"""
    print("\nTesting viewport view types...")

    if not PYQT_AVAILABLE:
        print("  [SKIP] PyQt6 not available")
        return True

    app = get_or_create_qapp()
    layout_manager = ViewportLayoutManager()

    # Test SINGLE layout
    layout_manager.set_layout(ViewportLayout.SINGLE)
    assert layout_manager.viewports[0].view_type == ViewType.PERSPECTIVE
    print("  [PASS] SINGLE layout has PERSPECTIVE view")

    # Test FOUR_GRID layout (standard Rhino layout)
    layout_manager.set_layout(ViewportLayout.FOUR_GRID)
    expected_views = [ViewType.TOP, ViewType.PERSPECTIVE, ViewType.FRONT, ViewType.RIGHT]

    for i, expected_view in enumerate(expected_views):
        actual_view = layout_manager.viewports[i].view_type
        assert actual_view == expected_view, f"Viewport {i} should be {expected_view}, got {actual_view}"
        print(f"  [PASS] Viewport {i} is {expected_view.value}")

    return True


def test_camera_reset():
    """Test reset_all_cameras functionality"""
    print("\nTesting camera reset...")

    if not PYQT_AVAILABLE:
        print("  [SKIP] PyQt6 not available")
        return True

    app = get_or_create_qapp()
    layout_manager = ViewportLayoutManager()

    layout_manager.set_layout(ViewportLayout.FOUR_GRID)

    # Modify camera positions
    for viewport in layout_manager.viewports:
        camera = viewport.renderer.GetActiveCamera()
        camera.SetPosition(100, 200, 300)  # Arbitrary position

    # Reset all cameras
    layout_manager.reset_all_cameras()

    # Verify cameras were reset (not at the arbitrary position)
    for i, viewport in enumerate(layout_manager.viewports):
        camera = viewport.renderer.GetActiveCamera()
        pos = camera.GetPosition()
        # Position should not be at the arbitrary location
        assert pos != (100, 200, 300), f"Camera {i} should be reset"

    print("  [PASS] All cameras reset to default positions")

    return True


def test_camera_sync():
    """Test camera synchronization between viewports"""
    print("\nTesting camera synchronization...")

    if not PYQT_AVAILABLE:
        print("  [SKIP] PyQt6 not available")
        return True

    app = get_or_create_qapp()
    layout_manager = ViewportLayoutManager()

    layout_manager.set_layout(ViewportLayout.FOUR_GRID)

    # Set a specific camera position on viewport 0
    source_camera = layout_manager.viewports[0].renderer.GetActiveCamera()
    test_position = (10, 20, 30)
    test_focal = (5, 10, 15)
    test_up = (0, 0, 1)

    source_camera.SetPosition(*test_position)
    source_camera.SetFocalPoint(*test_focal)
    source_camera.SetViewUp(*test_up)

    # Sync cameras from viewport 0
    layout_manager.sync_cameras(0)

    # Verify all other viewports have the same camera settings
    for i in range(1, len(layout_manager.viewports)):
        camera = layout_manager.viewports[i].renderer.GetActiveCamera()
        assert camera.GetPosition() == test_position, f"Viewport {i} position should match"
        assert camera.GetFocalPoint() == test_focal, f"Viewport {i} focal point should match"
        assert camera.GetViewUp() == test_up, f"Viewport {i} view up should match"

    print("  [PASS] Camera sync from viewport 0 successful")

    return True


def test_viewport_labels():
    """Test that viewport labels are set correctly"""
    print("\nTesting viewport labels...")

    if not PYQT_AVAILABLE:
        print("  [SKIP] PyQt6 not available")
        return True

    app = get_or_create_qapp()
    layout_manager = ViewportLayoutManager()

    layout_manager.set_layout(ViewportLayout.FOUR_GRID)

    expected_labels = ["Top", "Perspective", "Front", "Right"]

    for i, expected_label in enumerate(expected_labels):
        actual_label = layout_manager.viewports[i].view_label.text()
        assert actual_label == expected_label, f"Viewport {i} label should be '{expected_label}', got '{actual_label}'"
        print(f"  [PASS] Viewport {i} label is '{actual_label}'")

    return True


def test_active_viewport_visual_indicator():
    """Test that active viewport has green border"""
    print("\nTesting active viewport visual indicator...")

    if not PYQT_AVAILABLE:
        print("  [SKIP] PyQt6 not available")
        return True

    app = get_or_create_qapp()
    layout_manager = ViewportLayoutManager()

    layout_manager.set_layout(ViewportLayout.FOUR_GRID)

    # Set viewport 1 as active
    layout_manager.set_active_viewport(1)

    # Check that viewport 1 has green border style
    active_style = layout_manager.viewports[1].styleSheet()
    assert "4CAF50" in active_style or "green" in active_style.lower(), "Active viewport should have green border"
    print("  [PASS] Active viewport has green border indicator")

    # Check that other viewports have inactive style
    for i in [0, 2, 3]:
        inactive_style = layout_manager.viewports[i].styleSheet()
        assert "333333" in inactive_style or inactive_style == "border: 1px solid #333333;", f"Inactive viewport {i} should have dark border"

    print("  [PASS] Inactive viewports have dark border")

    return True


def main():
    """Run all tests"""
    print("=" * 60)
    print("Testing Multi-Viewport Layout Manager")
    print("=" * 60)
    print()

    try:
        success = True

        # Run all tests
        success = test_layout_modes() and success
        success = test_camera_independence() and success
        success = test_active_viewport_tracking() and success
        success = test_layout_switching() and success
        success = test_viewport_view_types() and success
        success = test_camera_reset() and success
        success = test_camera_sync() and success
        success = test_viewport_labels() and success
        success = test_active_viewport_visual_indicator() and success

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
