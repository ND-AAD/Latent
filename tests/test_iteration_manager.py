#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Comprehensive tests for the iteration management system

Tests:
- DesignIteration creation and serialization
- IterationManager CRUD operations
- State save/load with iterations
- Iteration switching and state restoration
- Integration with ApplicationState
"""

import sys
import json
import tempfile
import unittest
from pathlib import Path
from datetime import datetime

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.state.iteration_manager import DesignIteration, IterationManager
from app.state.parametric_region import ParametricRegion
from app.state.app_state import ApplicationState


class TestDesignIteration(unittest.TestCase):
    """Test DesignIteration data class"""

    def test_create_iteration(self):
        """Test creating a basic iteration"""
        iteration = DesignIteration(
            id="test_id",
            name="Test Iteration",
            timestamp=datetime.now(),
            regions=[],
        )

        assert iteration.id == "test_id"
        assert iteration.name == "Test Iteration"
        assert len(iteration.regions) == 0

    def test_iteration_with_regions(self):
        """Test iteration with regions"""
        regions = [
            ParametricRegion(
                id="region1",
                faces=[0, 1, 2],
                unity_principle="Test",
                unity_strength=0.8
            ),
            ParametricRegion(
                id="region2",
                faces=[3, 4, 5],
                unity_principle="Test",
                unity_strength=0.7
            )
        ]

        iteration = DesignIteration(
            id="test_id",
            name="Test",
            timestamp=datetime.now(),
            regions=regions,
            lens_used="Differential",
        )

        assert len(iteration.regions) == 2
        assert iteration.lens_used == "Differential"

    def test_iteration_serialization(self):
        """Test iteration to_json/from_json"""
        regions = [
            ParametricRegion(
                id="region1",
                faces=[0, 1, 2],
                unity_principle="Test",
                unity_strength=0.8
            )
        ]

        original = DesignIteration(
            id="test_id",
            name="Test Iteration",
            timestamp=datetime.now(),
            regions=regions,
            lens_used="Differential",
            parameters={"threshold": 0.5},
        )

        # Serialize
        data = original.to_json()

        # Deserialize
        restored = DesignIteration.from_json(data)

        # Verify
        assert restored.id == original.id
        assert restored.name == original.name
        assert len(restored.regions) == len(original.regions)
        assert restored.lens_used == original.lens_used
        assert restored.parameters == original.parameters

    def test_iteration_with_control_cage(self):
        """Test iteration with control cage data"""
        control_cage_data = {
            'vertices': [[0, 0, 0], [1, 0, 0], [1, 1, 0], [0, 1, 0]],
            'faces': [[0, 1, 2, 3]],
            'creases': [],
        }

        iteration = DesignIteration(
            id="test_id",
            name="Test",
            timestamp=datetime.now(),
            regions=[],
            control_cage_data=control_cage_data,
        )

        assert iteration.control_cage_data is not None
        assert len(iteration.control_cage_data['vertices']) == 4
        assert len(iteration.control_cage_data['faces']) == 1

    def test_iteration_summary(self):
        """Test get_summary method"""
        iteration = DesignIteration(
            id="test_id",
            name="Test Iteration",
            timestamp=datetime(2025, 11, 9, 14, 30),
            regions=[
                ParametricRegion(id="r1", faces=[0, 1], unity_principle="Test", unity_strength=0.8),
                ParametricRegion(id="r2", faces=[2, 3], unity_principle="Test", unity_strength=0.7),
            ],
            lens_used="Differential",
        )

        summary = iteration.get_summary()
        assert "Test Iteration" in summary
        assert "2 regions" in summary
        assert "Differential" in summary


class TestIterationManager(unittest.TestCase):
    """Test IterationManager functionality"""

    def test_create_manager(self):
        """Test creating iteration manager"""
        manager = IterationManager()
        assert manager.get_iteration_count() == 0
        assert manager.current_iteration_id is None

    def test_create_iteration(self):
        """Test creating an iteration"""
        manager = IterationManager()

        regions = [
            ParametricRegion(id="r1", faces=[0, 1], unity_principle="Test", unity_strength=0.8)
        ]

        iteration = manager.create_iteration(
            name="First Iteration",
            regions=regions,
            lens_used="Differential",
        )

        assert iteration is not None
        assert iteration.name == "First Iteration"
        assert manager.get_iteration_count() == 1
        assert manager.current_iteration_id == iteration.id

    def test_get_iteration(self):
        """Test retrieving iteration by ID"""
        manager = IterationManager()

        iteration = manager.create_iteration(
            name="Test",
            regions=[],
        )

        retrieved = manager.get_iteration(iteration.id)
        assert retrieved is not None
        assert retrieved.id == iteration.id
        assert retrieved.name == iteration.name

    def test_get_nonexistent_iteration(self):
        """Test getting non-existent iteration returns None"""
        manager = IterationManager()
        assert manager.get_iteration("nonexistent") is None

    def test_duplicate_iteration(self):
        """Test duplicating an iteration"""
        manager = IterationManager()

        # Create original
        regions = [
            ParametricRegion(id="r1", faces=[0, 1, 2], unity_principle="Test", unity_strength=0.8)
        ]

        original = manager.create_iteration(
            name="Original",
            regions=regions,
            lens_used="Differential",
        )

        # Duplicate
        duplicate = manager.duplicate_iteration(original.id, "Duplicate")

        assert duplicate is not None
        assert duplicate.id != original.id  # Different ID
        assert duplicate.name == "Duplicate"
        assert len(duplicate.regions) == len(original.regions)
        assert duplicate.lens_used == original.lens_used
        assert manager.get_iteration_count() == 2

    def test_duplicate_with_default_name(self):
        """Test duplicating without providing new name"""
        manager = IterationManager()

        original = manager.create_iteration(name="Original", regions=[])
        duplicate = manager.duplicate_iteration(original.id)

        assert duplicate is not None
        assert "Copy of Original" in duplicate.name

    def test_delete_iteration(self):
        """Test deleting an iteration"""
        manager = IterationManager()

        iteration = manager.create_iteration(name="Test", regions=[])
        iteration_id = iteration.id

        assert manager.get_iteration_count() == 1

        # Delete
        result = manager.delete_iteration(iteration_id)

        assert result is True
        assert manager.get_iteration_count() == 0
        assert manager.get_iteration(iteration_id) is None

    def test_delete_current_iteration(self):
        """Test deleting current iteration updates current_id"""
        manager = IterationManager()

        iter1 = manager.create_iteration(name="First", regions=[])
        iter2 = manager.create_iteration(name="Second", regions=[])

        assert manager.current_iteration_id == iter2.id

        # Delete current
        manager.delete_iteration(iter2.id)

        # Should fall back to iter1
        assert manager.current_iteration_id == iter1.id

    def test_set_current_iteration(self):
        """Test switching current iteration"""
        manager = IterationManager()

        iter1 = manager.create_iteration(name="First", regions=[])
        iter2 = manager.create_iteration(name="Second", regions=[])

        # Switch to iter1
        result = manager.set_current_iteration(iter1.id)

        assert result is True
        assert manager.current_iteration_id == iter1.id

    def test_get_all_iterations(self):
        """Test getting all iterations sorted by timestamp"""
        manager = IterationManager()

        iter1 = manager.create_iteration(name="First", regions=[])
        iter2 = manager.create_iteration(name="Second", regions=[])
        iter3 = manager.create_iteration(name="Third", regions=[])

        all_iterations = manager.get_all_iterations()

        # Should be sorted newest first
        assert len(all_iterations) == 3
        assert all_iterations[0].id == iter3.id  # Most recent
        assert all_iterations[2].id == iter1.id  # Oldest

    def test_save_and_load_iterations(self):
        """Test save/load iteration persistence"""
        with tempfile.TemporaryDirectory() as tmpdir:
            filepath = Path(tmpdir) / "iterations.json"

            # Create manager with iterations
            manager = IterationManager()

            regions = [
                ParametricRegion(id="r1", faces=[0, 1, 2], unity_principle="Test", unity_strength=0.8)
            ]

            iter1 = manager.create_iteration(
                name="First",
                regions=regions,
                lens_used="Differential",
                parameters={"threshold": 0.5},
            )

            iter2 = manager.create_iteration(
                name="Second",
                regions=[],
                lens_used="Spectral",
            )

            # Save
            result = manager.save_to_file(filepath)
            assert result is True
            assert filepath.exists()

            # Load into new manager
            manager2 = IterationManager()
            result = manager2.load_from_file(filepath)

            assert result is True
            assert manager2.get_iteration_count() == 2
            assert manager2.current_iteration_id == manager.current_iteration_id

            # Verify data
            loaded_iter1 = manager2.get_iteration(iter1.id)
            assert loaded_iter1 is not None
            assert loaded_iter1.name == "First"
            assert loaded_iter1.lens_used == "Differential"
            assert loaded_iter1.parameters == {"threshold": 0.5}
            assert len(loaded_iter1.regions) == 1

    def test_clear_iterations(self):
        """Test clearing all iterations"""
        manager = IterationManager()

        manager.create_iteration(name="First", regions=[])
        manager.create_iteration(name="Second", regions=[])

        assert manager.get_iteration_count() == 2

        manager.clear()

        assert manager.get_iteration_count() == 0
        assert manager.current_iteration_id is None


class TestIterationApplicationStateIntegration(unittest.TestCase):
    """Test integration with ApplicationState"""

    def test_state_has_iteration_manager(self):
        """Test that ApplicationState includes IterationManager"""
        state = ApplicationState()
        assert hasattr(state, 'iteration_manager')
        assert isinstance(state.iteration_manager, IterationManager)

    def test_create_iteration_snapshot(self):
        """Test creating iteration snapshot from state"""
        state = ApplicationState()

        # Add some regions
        regions = [
            ParametricRegion(id="r1", faces=[0, 1, 2], unity_principle="Test", unity_strength=0.8),
            ParametricRegion(id="r2", faces=[3, 4, 5], unity_principle="Test", unity_strength=0.7),
        ]
        state.set_regions(regions)
        state.set_current_lens("Differential")

        # Create snapshot
        iteration_id = state.create_iteration_snapshot("Test Snapshot")

        assert iteration_id is not None
        iteration = state.iteration_manager.get_iteration(iteration_id)
        assert iteration is not None
        assert iteration.name == "Test Snapshot"
        assert len(iteration.regions) == 2
        assert iteration.lens_used == "Differential"

    def test_restore_from_iteration(self):
        """Test restoring state from iteration"""
        state = ApplicationState()

        # Create first state
        regions1 = [
            ParametricRegion(id="r1", faces=[0, 1, 2], unity_principle="Test1", unity_strength=0.8)
        ]
        state.set_regions(regions1)
        state.set_current_lens("Differential")
        iter1_id = state.create_iteration_snapshot("First")

        # Create second state
        regions2 = [
            ParametricRegion(id="r2", faces=[3, 4, 5], unity_principle="Test2", unity_strength=0.7),
            ParametricRegion(id="r3", faces=[6, 7, 8], unity_principle="Test2", unity_strength=0.9),
        ]
        state.set_regions(regions2)
        state.set_current_lens("Spectral")
        iter2_id = state.create_iteration_snapshot("Second")

        # Verify we're in second state
        assert len(state.regions) == 2
        assert state.current_lens == "Spectral"

        # Restore first state
        result = state.restore_from_iteration(iter1_id)

        assert result is True
        assert len(state.regions) == 1
        assert state.regions[0].id == "r1"
        assert state.current_lens == "Differential"
        assert state.iteration_manager.current_iteration_id == iter1_id

    def test_iteration_signals(self):
        """Test that iteration changes emit signals"""
        state = ApplicationState()

        # Track signal emissions
        signal_emitted = []

        def on_iteration_changed(iter_id):
            signal_emitted.append(iter_id)

        state.iteration_changed.connect(on_iteration_changed)

        # Create iteration
        iter_id = state.create_iteration_snapshot("Test")

        # Signal should have been emitted
        assert len(signal_emitted) > 0
        assert signal_emitted[-1] == iter_id


class TestIterationManagerSignals(unittest.TestCase):
    """Test IterationManager signal emissions"""

    def test_iterations_changed_signal(self):
        """Test iterations_changed signal"""
        manager = IterationManager()

        signal_count = []

        def on_changed():
            signal_count.append(1)

        manager.iterations_changed.connect(on_changed)

        # Create iteration
        manager.create_iteration(name="Test", regions=[])
        assert len(signal_count) == 1

        # Delete iteration
        iteration_id = manager.iterations[0].id
        manager.delete_iteration(iteration_id)
        assert len(signal_count) == 2

    def test_current_iteration_changed_signal(self):
        """Test current_iteration_changed signal"""
        manager = IterationManager()

        emitted_ids = []

        def on_changed(iter_id):
            emitted_ids.append(iter_id)

        manager.current_iteration_changed.connect(on_changed)

        # Create iterations
        iter1 = manager.create_iteration(name="First", regions=[])
        assert iter1.id in emitted_ids

        iter2 = manager.create_iteration(name="Second", regions=[])
        assert iter2.id in emitted_ids

        # Switch
        manager.set_current_iteration(iter1.id)
        assert emitted_ids[-1] == iter1.id


if __name__ == '__main__':
    unittest.main()
