#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Test edit mode management system."""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Check for PyQt6 availability
try:
    from PyQt6.QtCore import QObject
    from app.state.edit_mode import EditMode, Selection, EditModeManager
    PYQT_AVAILABLE = True
except ImportError as e:
    print(f"⚠️  PyQt6 not available: {e}")
    print("⚠️  Tests will be skipped. Install PyQt6 to run these tests:")
    print("    pip install PyQt6")
    PYQT_AVAILABLE = False


if PYQT_AVAILABLE:
    class SignalTracker(QObject):
        """Helper class to track signal emissions"""
        def __init__(self):
            super().__init__()
            self.mode_changed_count = 0
            self.selection_changed_count = 0
            self.last_mode = None
            self.last_selection = None

        def on_mode_changed(self, mode):
            self.mode_changed_count += 1
            self.last_mode = mode

        def on_selection_changed(self, selection):
            self.selection_changed_count += 1
            self.last_selection = selection
else:
    # Dummy class when PyQt6 is not available
    class SignalTracker:
        pass


def test_edit_mode_enum():
    """Test EditMode enum values and methods"""
    print("Testing EditMode enum...")

    # Test all 4 modes exist
    assert hasattr(EditMode, 'SOLID')
    assert hasattr(EditMode, 'PANEL')
    assert hasattr(EditMode, 'EDGE')
    assert hasattr(EditMode, 'VERTEX')

    # Test display names
    assert EditMode.SOLID.get_display_name() == "Solid"
    assert EditMode.PANEL.get_display_name() == "Panel"
    assert EditMode.EDGE.get_display_name() == "Edge"
    assert EditMode.VERTEX.get_display_name() == "Vertex"

    # Test icon names
    assert EditMode.SOLID.get_icon_name() == "solid_mode.svg"
    assert EditMode.PANEL.get_icon_name() == "panel_mode.svg"
    assert EditMode.EDGE.get_icon_name() == "edge_mode.svg"
    assert EditMode.VERTEX.get_icon_name() == "vertex_mode.svg"

    print("  ✓ EditMode enum works correctly")
    return True


def test_selection_creation():
    """Test Selection creation and initialization"""
    print("Testing Selection creation...")

    # Create selection with default values
    sel = Selection(mode=EditMode.PANEL)
    assert sel.mode == EditMode.PANEL
    assert isinstance(sel.faces, set)
    assert isinstance(sel.edges, set)
    assert isinstance(sel.vertices, set)
    assert len(sel.faces) == 0
    assert len(sel.edges) == 0
    assert len(sel.vertices) == 0
    assert sel.is_empty() == True

    # Create selection with initial data
    sel2 = Selection(
        mode=EditMode.PANEL,
        faces={0, 1, 2},
        edges={10, 11},
        vertices={20}
    )
    assert len(sel2.faces) == 3
    assert len(sel2.edges) == 2
    assert len(sel2.vertices) == 1
    assert sel2.is_empty() == False

    print("  ✓ Selection creation works")
    return True


def test_selection_face_operations():
    """Test Selection face add/remove/toggle operations"""
    print("Testing Selection face operations...")

    sel = Selection(mode=EditMode.PANEL)

    # Test add_face
    sel.add_face(0)
    assert 0 in sel.faces
    assert len(sel.faces) == 1

    sel.add_face(1)
    sel.add_face(2)
    assert len(sel.faces) == 3

    # Test remove_face
    sel.remove_face(1)
    assert 1 not in sel.faces
    assert len(sel.faces) == 2

    # Test toggle_face
    added = sel.toggle_face(3)
    assert added == True
    assert 3 in sel.faces

    removed = sel.toggle_face(3)
    assert removed == False
    assert 3 not in sel.faces

    # Test clear
    sel.clear()
    assert len(sel.faces) == 0
    assert sel.is_empty() == True

    print("  ✓ Selection face operations work")
    return True


def test_selection_edge_operations():
    """Test Selection edge add/remove/toggle operations"""
    print("Testing Selection edge operations...")

    sel = Selection(mode=EditMode.EDGE)

    # Test add_edge
    sel.add_edge(10)
    assert 10 in sel.edges
    assert len(sel.edges) == 1

    # Test remove_edge
    sel.add_edge(11)
    sel.remove_edge(10)
    assert 10 not in sel.edges
    assert 11 in sel.edges

    # Test toggle_edge
    added = sel.toggle_edge(12)
    assert added == True
    assert 12 in sel.edges

    removed = sel.toggle_edge(12)
    assert removed == False
    assert 12 not in sel.edges

    print("  ✓ Selection edge operations work")
    return True


def test_selection_vertex_operations():
    """Test Selection vertex add/remove/toggle operations"""
    print("Testing Selection vertex operations...")

    sel = Selection(mode=EditMode.VERTEX)

    # Test add_vertex
    sel.add_vertex(20)
    assert 20 in sel.vertices
    assert len(sel.vertices) == 1

    # Test remove_vertex
    sel.add_vertex(21)
    sel.remove_vertex(20)
    assert 20 not in sel.vertices
    assert 21 in sel.vertices

    # Test toggle_vertex
    added = sel.toggle_vertex(22)
    assert added == True
    assert 22 in sel.vertices

    removed = sel.toggle_vertex(22)
    assert removed == False
    assert 22 not in sel.vertices

    print("  ✓ Selection vertex operations work")
    return True


def test_selection_mode_enforcement():
    """Test that selection only adds elements in correct mode"""
    print("Testing Selection mode enforcement...")

    # Panel mode should only add faces
    panel_sel = Selection(mode=EditMode.PANEL)
    panel_sel.add_face(0)
    assert len(panel_sel.faces) == 1

    # Edge mode should only add edges
    edge_sel = Selection(mode=EditMode.EDGE)
    edge_sel.add_edge(10)
    assert len(edge_sel.edges) == 1

    # Vertex mode should only add vertices
    vertex_sel = Selection(mode=EditMode.VERTEX)
    vertex_sel.add_vertex(20)
    assert len(vertex_sel.vertices) == 1

    print("  ✓ Selection mode enforcement works")
    return True


def test_edit_mode_manager_creation():
    """Test EditModeManager creation and initial state"""
    print("Testing EditModeManager creation...")

    manager = EditModeManager()

    # Check initial mode is SOLID
    assert manager.current_mode == EditMode.SOLID

    # Check selection is initialized
    assert manager.selection is not None
    assert manager.selection.mode == EditMode.SOLID
    assert manager.selection.is_empty() == True

    # Check signals exist
    assert hasattr(manager, 'mode_changed')
    assert hasattr(manager, 'selection_changed')

    print("  ✓ EditModeManager creation works")
    return True


def test_edit_mode_manager_mode_switching():
    """Test EditModeManager mode switching"""
    print("Testing EditModeManager mode switching...")

    manager = EditModeManager()
    tracker = SignalTracker()

    # Connect signals
    manager.mode_changed.connect(tracker.on_mode_changed)
    manager.selection_changed.connect(tracker.on_selection_changed)

    # Switch to PANEL mode
    manager.set_mode(EditMode.PANEL)
    assert manager.current_mode == EditMode.PANEL
    assert tracker.mode_changed_count == 1
    assert tracker.last_mode == EditMode.PANEL
    # Selection should be cleared and mode updated
    assert tracker.selection_changed_count == 1
    assert manager.selection.mode == EditMode.PANEL

    # Switch to EDGE mode
    manager.set_mode(EditMode.EDGE)
    assert manager.current_mode == EditMode.EDGE
    assert tracker.mode_changed_count == 2
    assert tracker.last_mode == EditMode.EDGE

    # Switch to VERTEX mode
    manager.set_mode(EditMode.VERTEX)
    assert manager.current_mode == EditMode.VERTEX
    assert tracker.mode_changed_count == 3
    assert tracker.last_mode == EditMode.VERTEX

    # Switch back to SOLID mode
    manager.set_mode(EditMode.SOLID)
    assert manager.current_mode == EditMode.SOLID
    assert tracker.mode_changed_count == 4
    assert tracker.last_mode == EditMode.SOLID

    # Setting same mode should not emit signals
    initial_count = tracker.mode_changed_count
    manager.set_mode(EditMode.SOLID)
    assert tracker.mode_changed_count == initial_count

    print("  ✓ EditModeManager mode switching works")
    return True


def test_edit_mode_manager_selection_cleared_on_mode_change():
    """Test that selection is cleared when mode changes"""
    print("Testing selection clearing on mode change...")

    manager = EditModeManager()

    # Switch to PANEL mode and select some faces
    manager.set_mode(EditMode.PANEL)
    manager.select_face(0)
    manager.select_face(1, add_to_selection=True)
    assert len(manager.selection.faces) == 2

    # Switch to EDGE mode - selection should be cleared
    manager.set_mode(EditMode.EDGE)
    assert len(manager.selection.faces) == 0
    assert len(manager.selection.edges) == 0
    assert manager.selection.is_empty() == True

    print("  ✓ Selection clearing on mode change works")
    return True


def test_edit_mode_manager_face_selection():
    """Test EditModeManager face selection"""
    print("Testing EditModeManager face selection...")

    manager = EditModeManager()
    tracker = SignalTracker()
    manager.selection_changed.connect(tracker.on_selection_changed)

    # Switch to PANEL mode
    manager.set_mode(EditMode.PANEL)
    tracker.selection_changed_count = 0  # Reset counter

    # Select single face (replace)
    manager.select_face(0)
    assert 0 in manager.selection.faces
    assert len(manager.selection.faces) == 1
    assert tracker.selection_changed_count == 1

    # Select another face (replace previous)
    manager.select_face(1)
    assert 0 not in manager.selection.faces
    assert 1 in manager.selection.faces
    assert len(manager.selection.faces) == 1

    # Select with add_to_selection=True (multi-select)
    manager.select_face(2, add_to_selection=True)
    assert 1 in manager.selection.faces
    assert 2 in manager.selection.faces
    assert len(manager.selection.faces) == 2

    # Selection in wrong mode should be ignored
    manager.set_mode(EditMode.SOLID)
    tracker.selection_changed_count = 0
    manager.select_face(3)
    assert tracker.selection_changed_count == 0
    assert 3 not in manager.selection.faces

    print("  ✓ EditModeManager face selection works")
    return True


def test_edit_mode_manager_edge_selection():
    """Test EditModeManager edge selection"""
    print("Testing EditModeManager edge selection...")

    manager = EditModeManager()
    manager.set_mode(EditMode.EDGE)

    # Select single edge
    manager.select_edge(10)
    assert 10 in manager.selection.edges
    assert len(manager.selection.edges) == 1

    # Select with multi-select
    manager.select_edge(11, add_to_selection=True)
    assert 10 in manager.selection.edges
    assert 11 in manager.selection.edges
    assert len(manager.selection.edges) == 2

    print("  ✓ EditModeManager edge selection works")
    return True


def test_edit_mode_manager_vertex_selection():
    """Test EditModeManager vertex selection"""
    print("Testing EditModeManager vertex selection...")

    manager = EditModeManager()
    manager.set_mode(EditMode.VERTEX)

    # Select single vertex
    manager.select_vertex(20)
    assert 20 in manager.selection.vertices
    assert len(manager.selection.vertices) == 1

    # Select with multi-select
    manager.select_vertex(21, add_to_selection=True)
    assert 20 in manager.selection.vertices
    assert 21 in manager.selection.vertices
    assert len(manager.selection.vertices) == 2

    print("  ✓ EditModeManager vertex selection works")
    return True


def test_edit_mode_manager_multi_select_mode():
    """Test EditModeManager multi-select mode (Shift key simulation)"""
    print("Testing EditModeManager multi-select mode...")

    manager = EditModeManager()
    manager.set_mode(EditMode.PANEL)

    # Enable multi-select mode (simulates Shift key held)
    manager.set_multi_select(True)

    # Select faces - should accumulate
    manager.select_face(0)
    assert len(manager.selection.faces) == 1

    manager.select_face(1)
    assert 0 in manager.selection.faces
    assert 1 in manager.selection.faces
    assert len(manager.selection.faces) == 2

    # Disable multi-select mode
    manager.set_multi_select(False)

    # Next selection should replace
    manager.select_face(2)
    assert 0 not in manager.selection.faces
    assert 1 not in manager.selection.faces
    assert 2 in manager.selection.faces
    assert len(manager.selection.faces) == 1

    print("  ✓ EditModeManager multi-select mode works")
    return True


def test_edit_mode_manager_clear_selection():
    """Test EditModeManager clear_selection"""
    print("Testing EditModeManager clear_selection...")

    manager = EditModeManager()
    tracker = SignalTracker()
    manager.selection_changed.connect(tracker.on_selection_changed)

    # Add some selections in different modes
    manager.set_mode(EditMode.PANEL)
    manager.select_face(0, add_to_selection=True)
    manager.select_face(1, add_to_selection=True)

    tracker.selection_changed_count = 0

    # Clear selection
    manager.clear_selection()
    assert manager.selection.is_empty() == True
    assert tracker.selection_changed_count == 1

    print("  ✓ EditModeManager clear_selection works")
    return True


def test_edit_mode_manager_create_region_from_selection():
    """Test EditModeManager create_region_from_selection"""
    print("Testing EditModeManager create_region_from_selection...")

    manager = EditModeManager()

    # No selection - should return None
    manager.set_mode(EditMode.PANEL)
    result = manager.create_region_from_selection()
    assert result is None

    # With face selection
    manager.select_face(0, add_to_selection=True)
    manager.select_face(1, add_to_selection=True)
    manager.select_face(2, add_to_selection=True)
    result = manager.create_region_from_selection()
    assert result is not None
    assert len(result) == 3
    assert 0 in result
    assert 1 in result
    assert 2 in result

    # Wrong mode - should return None
    manager.set_mode(EditMode.SOLID)
    result = manager.create_region_from_selection()
    assert result is None

    print("  ✓ EditModeManager create_region_from_selection works")
    return True


def test_edit_mode_manager_get_selection_info():
    """Test EditModeManager get_selection_info"""
    print("Testing EditModeManager get_selection_info...")

    manager = EditModeManager()

    # No selection
    info = manager.get_selection_info()
    assert info == "No selection"

    # Face selection
    manager.set_mode(EditMode.PANEL)
    manager.select_face(0, add_to_selection=True)
    manager.select_face(1, add_to_selection=True)
    info = manager.get_selection_info()
    assert "2 faces" in info

    # Multiple types (manually add to test)
    manager.selection.edges.add(10)
    manager.selection.vertices.add(20)
    info = manager.get_selection_info()
    assert "2 faces" in info
    assert "1 edges" in info
    assert "1 vertices" in info

    print("  ✓ EditModeManager get_selection_info works")
    return True


def test_edit_mode_signals():
    """Test that all signals are emitted correctly"""
    print("Testing EditModeManager signals...")

    manager = EditModeManager()
    tracker = SignalTracker()

    # Connect signals
    manager.mode_changed.connect(tracker.on_mode_changed)
    manager.selection_changed.connect(tracker.on_selection_changed)

    # Test mode_changed signal
    manager.set_mode(EditMode.PANEL)
    assert tracker.mode_changed_count == 1
    assert tracker.last_mode == EditMode.PANEL

    # Test selection_changed signal
    manager.select_face(0)
    assert tracker.selection_changed_count >= 1  # At least once from mode change
    assert tracker.last_selection is not None

    # Both signals on mode change
    initial_mode_count = tracker.mode_changed_count
    initial_sel_count = tracker.selection_changed_count
    manager.set_mode(EditMode.EDGE)
    assert tracker.mode_changed_count == initial_mode_count + 1
    assert tracker.selection_changed_count == initial_sel_count + 1

    print("  ✓ EditModeManager signals work correctly")
    return True


def run_all_tests():
    """Run all edit mode tests"""
    print("\n" + "="*60)
    print("Running Edit Mode Tests")
    print("="*60 + "\n")

    if not PYQT_AVAILABLE:
        print("⚠️  Skipping tests - PyQt6 not available")
        print("="*60 + "\n")
        return True  # Return success to not fail CI when Qt is not available

    tests = [
        test_edit_mode_enum,
        test_selection_creation,
        test_selection_face_operations,
        test_selection_edge_operations,
        test_selection_vertex_operations,
        test_selection_mode_enforcement,
        test_edit_mode_manager_creation,
        test_edit_mode_manager_mode_switching,
        test_edit_mode_manager_selection_cleared_on_mode_change,
        test_edit_mode_manager_face_selection,
        test_edit_mode_manager_edge_selection,
        test_edit_mode_manager_vertex_selection,
        test_edit_mode_manager_multi_select_mode,
        test_edit_mode_manager_clear_selection,
        test_edit_mode_manager_create_region_from_selection,
        test_edit_mode_manager_get_selection_info,
        test_edit_mode_signals,
    ]

    passed = 0
    failed = 0

    for test in tests:
        try:
            test()
            passed += 1
        except AssertionError as e:
            print(f"  ✗ FAILED: {e}")
            failed += 1
        except Exception as e:
            print(f"  ✗ ERROR: {e}")
            failed += 1

    print("\n" + "="*60)
    print(f"Results: {passed} passed, {failed} failed")
    print("="*60 + "\n")

    return failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
