#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Test application state management, undo/redo, and serialization."""

import sys
import json
import tempfile
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from PyQt6.QtCore import QObject
from app.state.app_state import ApplicationState, HistoryItem
from app.state.parametric_region import ParametricRegion


class SignalTracker(QObject):
    """Helper class to track signal emissions"""
    def __init__(self):
        super().__init__()
        self.state_changed_count = 0
        self.regions_updated_count = 0
        self.region_pinned_count = 0
        self.history_changed_count = 0
        self.last_region_pinned_id = None
        self.last_region_pinned_state = None
        self.last_regions = None

    def on_state_changed(self):
        self.state_changed_count += 1

    def on_regions_updated(self, regions):
        self.regions_updated_count += 1
        self.last_regions = regions

    def on_region_pinned(self, region_id, pinned):
        self.region_pinned_count += 1
        self.last_region_pinned_id = region_id
        self.last_region_pinned_state = pinned

    def on_history_changed(self):
        self.history_changed_count += 1


def test_parametric_region_creation():
    """Test ParametricRegion creation and methods"""
    print("Testing ParametricRegion creation...")

    region = ParametricRegion(
        id="R1",
        faces=[0, 1, 2, 3],
        unity_principle="Differential",
        unity_strength=0.85,
        pinned=False
    )

    assert region.id == "R1"
    assert region.faces == [0, 1, 2, 3]
    assert region.unity_principle == "Differential"
    assert region.unity_strength == 0.85
    assert region.pinned == False
    assert region.get_face_count() == 4
    assert region.contains_face(2) == True
    assert region.contains_face(10) == False

    print("  ✓ ParametricRegion creation works")
    return True


def test_parametric_region_serialization():
    """Test ParametricRegion JSON serialization"""
    print("Testing ParametricRegion serialization...")

    region = ParametricRegion(
        id="R2",
        faces=[5, 6, 7],
        unity_principle="Spectral",
        unity_strength=0.72,
        pinned=True,
        modified=True
    )

    # Serialize
    data = region.to_dict()
    assert data['id'] == "R2"
    assert data['faces'] == [5, 6, 7]
    assert data['unity_principle'] == "Spectral"
    assert data['unity_strength'] == 0.72
    assert data['pinned'] == True
    assert data['modified'] == True

    # Deserialize
    restored = ParametricRegion.from_dict(data)
    assert restored.id == region.id
    assert restored.faces == region.faces
    assert restored.unity_principle == region.unity_principle
    assert restored.unity_strength == region.unity_strength
    assert restored.pinned == region.pinned
    assert restored.modified == region.modified

    print("  ✓ ParametricRegion serialization works")
    return True


def test_application_state_creation():
    """Test ApplicationState initialization"""
    print("Testing ApplicationState creation...")

    state = ApplicationState()

    assert state.subd_geometry is None
    assert len(state.regions) == 0
    assert state.selected_region_id is None
    assert state.current_lens == "Flow"
    assert len(state.history) == 0
    assert state.history_index == -1
    assert state.max_history_size == 100

    print("  ✓ ApplicationState initialization works")
    return True


def test_region_management():
    """Test region add/get/pin operations"""
    print("Testing region management...")

    state = ApplicationState()

    # Create test regions
    r1 = ParametricRegion(id="R1", faces=[0, 1, 2])
    r2 = ParametricRegion(id="R2", faces=[3, 4, 5])
    r3 = ParametricRegion(id="R3", faces=[6, 7, 8])

    # Add regions
    state.add_region(r1)
    assert len(state.regions) == 1
    assert state.get_region("R1") == r1

    state.add_region(r2)
    state.add_region(r3)
    assert len(state.regions) == 3

    # Set regions (batch)
    regions = [r1, r2, r3]
    state.set_regions(regions)
    assert len(state.regions) == 3

    # Get pinned/unpinned regions
    assert len(state.get_pinned_regions()) == 0
    assert len(state.get_unpinned_regions()) == 3

    # Pin a region
    state.set_region_pinned("R1", True)
    assert r1.pinned == True
    assert len(state.get_pinned_regions()) == 1
    assert len(state.get_unpinned_regions()) == 2

    # Unpin
    state.set_region_pinned("R1", False)
    assert r1.pinned == False

    # Select region
    state.select_region("R2")
    assert state.selected_region_id == "R2"

    print("  ✓ Region management works")
    return True


def test_signals_emission():
    """Test that signals are emitted correctly"""
    print("Testing signal emission...")

    state = ApplicationState()
    tracker = SignalTracker()

    # Connect signals
    state.state_changed.connect(tracker.on_state_changed)
    state.regions_updated.connect(tracker.on_regions_updated)
    state.region_pinned.connect(tracker.on_region_pinned)
    state.history_changed.connect(tracker.on_history_changed)

    # Test state_changed signal
    initial_count = tracker.state_changed_count
    state.set_current_lens("Differential")
    assert tracker.state_changed_count > initial_count

    # Test regions_updated signal
    r1 = ParametricRegion(id="R1", faces=[0, 1])
    state.add_region(r1)
    assert tracker.regions_updated_count > 0
    assert tracker.last_regions is not None

    # Test region_pinned signal
    state.set_region_pinned("R1", True)
    assert tracker.region_pinned_count > 0
    assert tracker.last_region_pinned_id == "R1"
    assert tracker.last_region_pinned_state == True

    # Test history_changed signal
    assert tracker.history_changed_count > 0

    print("  ✓ Signal emission works")
    return True


def test_undo_redo():
    """Test undo/redo functionality"""
    print("Testing undo/redo...")

    state = ApplicationState()

    # Add regions
    r1 = ParametricRegion(id="R1", faces=[0, 1, 2])
    r2 = ParametricRegion(id="R2", faces=[3, 4, 5])
    state.set_regions([r1, r2])

    # Initially no undo/redo
    assert state.history_index >= 0  # set_regions adds history
    assert not state.can_redo()

    # Pin region (adds to history)
    state.set_region_pinned("R1", True)
    assert r1.pinned == True
    assert state.can_undo()

    # Undo the pin
    state.undo()
    assert r1.pinned == False
    assert state.can_redo()

    # Redo the pin
    state.redo()
    assert r1.pinned == True

    # Pin another region
    state.set_region_pinned("R2", True)
    assert r2.pinned == True

    # Undo twice
    state.undo()  # Undo R2 pin
    assert r2.pinned == False
    state.undo()  # Undo R1 pin
    assert r1.pinned == False

    # Redo once
    state.redo()
    assert r1.pinned == True
    assert r2.pinned == False

    print("  ✓ Undo/redo works")
    return True


def test_history_limit():
    """Test that history is limited to max_history_size"""
    print("Testing history limit...")

    state = ApplicationState()
    state.max_history_size = 10  # Set small limit for testing

    # Create a region
    r1 = ParametricRegion(id="R1", faces=[0])
    state.add_region(r1)

    # Add many history items
    for i in range(20):
        state.set_region_pinned("R1", i % 2 == 0)

    # Check history is limited
    assert len(state.history) <= state.max_history_size
    assert state.history_index < state.max_history_size

    print("  ✓ History limit works")
    return True


def test_state_serialization():
    """Test ApplicationState JSON serialization"""
    print("Testing state serialization...")

    state = ApplicationState()

    # Add regions
    r1 = ParametricRegion(id="R1", faces=[0, 1, 2], unity_principle="Differential", unity_strength=0.85)
    r2 = ParametricRegion(id="R2", faces=[3, 4], unity_principle="Spectral", unity_strength=0.72, pinned=True)
    state.set_regions([r1, r2])
    state.select_region("R1")
    state.set_current_lens("Differential")

    # Serialize
    data = state.to_dict()
    assert data['version'] == '1.0'
    assert len(data['regions']) == 2
    assert data['selected_region_id'] == "R1"
    assert data['current_lens'] == "Differential"

    # Deserialize to new state
    new_state = ApplicationState()
    new_state.from_dict(data)

    assert len(new_state.regions) == 2
    assert new_state.selected_region_id == "R1"
    assert new_state.current_lens == "Differential"

    # Check regions restored correctly
    restored_r1 = new_state.get_region("R1")
    assert restored_r1 is not None
    assert restored_r1.faces == [0, 1, 2]
    assert restored_r1.unity_principle == "Differential"
    assert restored_r1.unity_strength == 0.85

    restored_r2 = new_state.get_region("R2")
    assert restored_r2 is not None
    assert restored_r2.pinned == True

    print("  ✓ State serialization works")
    return True


def test_json_file_save_load():
    """Test saving and loading state to/from JSON file"""
    print("Testing JSON file save/load...")

    state = ApplicationState()

    # Add regions
    r1 = ParametricRegion(id="R1", faces=[0, 1, 2, 3], unity_principle="Flow", unity_strength=0.90)
    r2 = ParametricRegion(id="R2", faces=[4, 5, 6], unity_principle="Morse", unity_strength=0.65, pinned=True)
    state.set_regions([r1, r2])
    state.select_region("R2")

    # Save to temporary file
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
        temp_path = f.name

    try:
        state.save_to_json(temp_path)

        # Verify file exists and is valid JSON
        with open(temp_path, 'r') as f:
            data = json.load(f)
        assert data['version'] == '1.0'
        assert len(data['regions']) == 2

        # Load into new state
        new_state = ApplicationState()
        new_state.load_from_json(temp_path)

        assert len(new_state.regions) == 2
        assert new_state.selected_region_id == "R2"
        assert new_state.get_region("R1") is not None
        assert new_state.get_region("R2").pinned == True

    finally:
        # Clean up
        Path(temp_path).unlink(missing_ok=True)

    print("  ✓ JSON file save/load works")
    return True


def test_clear_state():
    """Test clearing all state"""
    print("Testing clear state...")

    state = ApplicationState()

    # Add some data
    r1 = ParametricRegion(id="R1", faces=[0, 1])
    state.add_region(r1)
    state.select_region("R1")

    assert len(state.regions) > 0
    assert state.selected_region_id is not None

    # Clear
    state.clear()

    assert state.subd_geometry is None
    assert len(state.regions) == 0
    assert state.selected_region_id is None
    assert len(state.history) == 0
    assert state.history_index == -1

    print("  ✓ Clear state works")
    return True


def test_unpinned_faces():
    """Test getting unpinned face indices"""
    print("Testing unpinned faces tracking...")

    state = ApplicationState()

    # Create mock geometry with faces
    class MockGeometry:
        def __init__(self):
            self.faces = [[0, 1, 2], [3, 4, 5], [6, 7, 8], [9, 10, 11], [12, 13, 14]]

    state.subd_geometry = MockGeometry()

    # Add regions
    r1 = ParametricRegion(id="R1", faces=[0, 1], pinned=True)
    r2 = ParametricRegion(id="R2", faces=[2, 3], pinned=False)
    state.set_regions([r1, r2])

    # Get unpinned faces
    unpinned = state.get_unpinned_faces()
    pinned = state.get_pinned_face_indices()

    assert 0 in pinned
    assert 1 in pinned
    assert 2 not in pinned
    assert 3 not in pinned
    assert 4 in unpinned

    print("  ✓ Unpinned faces tracking works")
    return True


def run_all_tests():
    """Run all state management tests"""
    print("\n" + "="*60)
    print("RUNNING STATE MANAGEMENT TESTS")
    print("="*60 + "\n")

    tests = [
        test_parametric_region_creation,
        test_parametric_region_serialization,
        test_application_state_creation,
        test_region_management,
        test_signals_emission,
        test_undo_redo,
        test_history_limit,
        test_state_serialization,
        test_json_file_save_load,
        test_clear_state,
        test_unpinned_faces,
    ]

    passed = 0
    failed = 0

    for test in tests:
        try:
            result = test()
            if result:
                passed += 1
        except Exception as e:
            print(f"  ✗ FAILED: {e}")
            import traceback
            traceback.print_exc()
            failed += 1

    print("\n" + "="*60)
    print(f"RESULTS: {passed} passed, {failed} failed")
    print("="*60 + "\n")

    return failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
