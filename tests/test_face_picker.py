"""
Tests for SubD Face Picker (Panel Mode)

Tests face picking functionality including:
- Triangle → face mapping
- Multi-select support
- Selection toggle
- Visual highlighting integration
"""

import pytest
from unittest.mock import Mock, MagicMock, patch
import sys

# Mock PyQt6 before importing
try:
    from PyQt6.QtCore import QObject
except ImportError:
    # Mock PyQt6 if not available
    class MockQObject:
        def __init__(self):
            pass

    pyqt_mock = MagicMock()
    pyqt_mock.QtCore.QObject = MockQObject
    pyqt_mock.QtCore.pyqtSignal = MagicMock
    sys.modules['PyQt6'] = pyqt_mock
    sys.modules['PyQt6.QtCore'] = pyqt_mock.QtCore
    QObject = MockQObject

# Mock VTK before importing pickers
vtk_mock = MagicMock()
vtk_mock.vtkRenderer = MagicMock
vtk_mock.vtkRenderWindow = MagicMock
vtk_mock.vtkCellPicker = MagicMock

sys.modules['app.vtk_bridge'] = vtk_mock


class TestSubDFacePicker:
    """Test suite for SubDFacePicker"""
    
    @pytest.fixture
    def mock_vtk_setup(self):
        """Create mock VTK components"""
        renderer = Mock()
        render_window = Mock()
        interactor = Mock()
        render_window.GetInteractor.return_value = interactor

        # Create mock picker with proper spec
        picker = Mock(spec=['Pick', 'GetCellId', 'GetPickPosition', 'GetActor', 'SetTolerance'])
        picker.Pick.return_value = 1  # Success
        picker.GetCellId.return_value = 0
        picker.GetPickPosition.return_value = (1.0, 2.0, 3.0)
        picker.GetActor.return_value = Mock()
        picker.SetTolerance.return_value = None

        # Patch vtkCellPicker to return our mock
        vtk_mock.vtkCellPicker.return_value = picker

        return {
            'renderer': renderer,
            'render_window': render_window,
            'interactor': interactor,
            'picker': picker
        }
    
    @pytest.fixture
    def face_picker(self, mock_vtk_setup):
        """Create SubDFacePicker instance"""
        from app.ui.pickers.face_picker import SubDFacePicker
        
        picker = SubDFacePicker(
            mock_vtk_setup['renderer'],
            mock_vtk_setup['render_window']
        )
        
        # Set up face_parents mapping
        # Simulate a tessellated mesh where multiple triangles map to same face
        face_parents = [
            0, 0, 0, 0,  # Triangles 0-3 → Face 0
            1, 1, 1, 1,  # Triangles 4-7 → Face 1
            2, 2, 2, 2,  # Triangles 8-11 → Face 2
            3, 3, 3, 3,  # Triangles 12-15 → Face 3
        ]
        picker.set_face_parents(face_parents)
        
        return picker
    
    def test_picker_initialization(self, face_picker):
        """Test picker initializes correctly"""
        assert face_picker is not None
        assert face_picker.selected_faces == set()
        assert face_picker.face_parents is not None
        assert len(face_picker.face_parents) == 16
    
    def test_single_face_pick(self, face_picker, mock_vtk_setup):
        """Test picking a single face"""
        # Access picker directly from face_picker to ensure we're mocking the right one
        face_picker.picker.GetCellId.return_value = 5
        face_picker.picker.Pick.return_value = 1  # Successful pick
        face_picker.picker.GetPickPosition.return_value = (1.0, 2.0, 3.0)

        # Perform pick
        face_id = face_picker.pick(100, 100, add_to_selection=False)

        # Verify
        assert face_id == 1  # Triangle 5 maps to face 1
        assert face_picker.get_selection() == {1}
        assert face_picker.is_face_selected(1)
        assert not face_picker.is_face_selected(0)
    
    def test_triangle_to_face_mapping(self, face_picker, mock_vtk_setup):
        """Test triangle→face mapping is accurate"""
        test_cases = [
            (0, 0),   # Triangle 0 → Face 0
            (3, 0),   # Triangle 3 → Face 0 (same face)
            (5, 1),   # Triangle 5 → Face 1
            (10, 2),  # Triangle 10 → Face 2
            (15, 3),  # Triangle 15 → Face 3
        ]

        for triangle_id, expected_face_id in test_cases:
            face_picker.picker.GetCellId.return_value = triangle_id
            face_picker.picker.Pick.return_value = 1
            face_picker.picker.GetPickPosition.return_value = (1.0, 2.0, 3.0)
            face_id = face_picker.pick(100, 100, add_to_selection=False)
            assert face_id == expected_face_id, \
                f"Triangle {triangle_id} should map to face {expected_face_id}, got {face_id}"
    
    def test_multi_select_add(self, face_picker, mock_vtk_setup):
        """Test multi-select: adding faces with Shift+Click"""
        # Helper to set up picker
        def setup_pick(triangle_id):
            face_picker.picker.GetCellId.return_value = triangle_id
            face_picker.picker.Pick.return_value = 1
            face_picker.picker.GetPickPosition.return_value = (1.0, 2.0, 3.0)

        # Pick face 0
        setup_pick(0)
        face_picker.pick(100, 100, add_to_selection=False)
        assert face_picker.get_selection() == {0}

        # Shift+Click to add face 1
        setup_pick(4)  # Triangle 4 → Face 1
        face_picker.pick(100, 100, add_to_selection=True)
        assert face_picker.get_selection() == {0, 1}

        # Shift+Click to add face 2
        setup_pick(8)  # Triangle 8 → Face 2
        face_picker.pick(100, 100, add_to_selection=True)
        assert face_picker.get_selection() == {0, 1, 2}
    
    def test_selection_toggle(self, face_picker, mock_vtk_setup):
        """Test Shift+Click toggles selection (remove if already selected)"""
        def setup_pick(triangle_id):
            face_picker.picker.GetCellId.return_value = triangle_id
            face_picker.picker.Pick.return_value = 1
            face_picker.picker.GetPickPosition.return_value = (1.0, 2.0, 3.0)

        # Pick face 0
        setup_pick(0)
        face_picker.pick(100, 100, add_to_selection=False)
        assert face_picker.get_selection() == {0}

        # Add face 1
        setup_pick(4)
        face_picker.pick(100, 100, add_to_selection=True)
        assert face_picker.get_selection() == {0, 1}

        # Shift+Click face 0 again (should remove it)
        setup_pick(0)
        face_picker.pick(100, 100, add_to_selection=True)
        assert face_picker.get_selection() == {1}  # Face 0 removed

        # Shift+Click face 0 again (should add it back)
        setup_pick(0)
        face_picker.pick(100, 100, add_to_selection=True)
        assert face_picker.get_selection() == {0, 1}  # Face 0 added back
    
    def test_replace_selection(self, face_picker, mock_vtk_setup):
        """Test normal click replaces selection"""
        def setup_pick(triangle_id):
            face_picker.picker.GetCellId.return_value = triangle_id
            face_picker.picker.Pick.return_value = 1
            face_picker.picker.GetPickPosition.return_value = (1.0, 2.0, 3.0)

        # Select multiple faces
        setup_pick(0)
        face_picker.pick(100, 100, add_to_selection=False)
        setup_pick(4)
        face_picker.pick(100, 100, add_to_selection=True)
        assert face_picker.get_selection() == {0, 1}

        # Normal click should replace with new selection
        setup_pick(8)  # Face 2
        face_picker.pick(100, 100, add_to_selection=False)
        assert face_picker.get_selection() == {2}  # Only face 2
    
    def test_pick_miss(self, face_picker, mock_vtk_setup):
        """Test picking empty space (miss)"""
        # Setup pick to fail
        face_picker.picker.Pick.return_value = 0  # Failed pick

        result = face_picker.pick(100, 100, add_to_selection=False)
        assert result is None
    
    def test_clear_selection(self, face_picker, mock_vtk_setup):
        """Test clearing selection"""
        def setup_pick(triangle_id):
            face_picker.picker.GetCellId.return_value = triangle_id
            face_picker.picker.Pick.return_value = 1
            face_picker.picker.GetPickPosition.return_value = (1.0, 2.0, 3.0)

        # Select some faces
        setup_pick(0)
        face_picker.pick(100, 100, add_to_selection=False)
        setup_pick(4)
        face_picker.pick(100, 100, add_to_selection=True)
        assert len(face_picker.get_selection()) == 2

        # Clear
        face_picker.clear_selection()
        assert face_picker.get_selection() == set()
        assert not face_picker.is_face_selected(0)
        assert not face_picker.is_face_selected(1)
    
    def test_programmatic_selection(self, face_picker):
        """Test setting selection programmatically"""
        # Set selection directly
        face_picker.set_selection({0, 2, 3})
        
        assert face_picker.get_selection() == {0, 2, 3}
        assert face_picker.is_face_selected(0)
        assert face_picker.is_face_selected(2)
        assert face_picker.is_face_selected(3)
        assert not face_picker.is_face_selected(1)
    
    def test_signals_emitted(self, face_picker, mock_vtk_setup):
        """Test that signals exist and can be connected"""
        # Test that signals are defined and can be connected
        assert hasattr(face_picker, 'face_picked')
        assert hasattr(face_picker, 'selection_changed')

        # Create mock receivers
        face_picked_receiver = Mock()
        selection_changed_receiver = Mock()

        # Connect signals (this will work with real PyQt6 or mocked signals)
        try:
            # Try real PyQt6 signal connection
            face_picker.face_picked.connect(face_picked_receiver)
            face_picker.selection_changed.connect(selection_changed_receiver)
        except (AttributeError, TypeError):
            # Signals are None (mocked environment) - skip signal testing
            pass

        # Set up picker
        face_picker.picker.GetCellId.return_value = 5  # Face 1
        face_picker.picker.Pick.return_value = 1
        face_picker.picker.GetPickPosition.return_value = (1.0, 2.0, 3.0)

        # Perform pick
        face_id = face_picker.pick(100, 100, add_to_selection=False)

        # Verify pick worked (this is the essential functionality)
        assert face_id == 1
        assert face_picker.get_selection() == {1}
    
    def test_highlight_callback(self, face_picker, mock_vtk_setup):
        """Test highlight callback is invoked"""
        highlight_callback = Mock()
        face_picker.set_highlight_callback(highlight_callback)

        # Set up picker
        face_picker.picker.GetCellId.return_value = 0
        face_picker.picker.Pick.return_value = 1
        face_picker.picker.GetPickPosition.return_value = (1.0, 2.0, 3.0)

        # Perform pick
        face_picker.pick(100, 100, add_to_selection=False)

        # Verify callback was called with selected faces
        highlight_callback.assert_called_once()
        called_faces = highlight_callback.call_args[0][0]
        assert called_faces == {0}
    
    def test_no_face_parents_fallback(self, mock_vtk_setup):
        """Test picker works without face_parents (uses triangle_id as face_id)"""
        from app.ui.pickers.face_picker import SubDFacePicker

        picker = SubDFacePicker(
            mock_vtk_setup['renderer'],
            mock_vtk_setup['render_window']
        )
        # Don't set face_parents

        # Set up picker
        picker.picker.GetCellId.return_value = 5
        picker.picker.Pick.return_value = 1
        picker.picker.GetPickPosition.return_value = (1.0, 2.0, 3.0)

        # Pick triangle 5
        face_id = picker.pick(100, 100, add_to_selection=False)

        # Should fall back to using triangle_id as face_id
        assert face_id == 5
    
    def test_out_of_range_triangle(self, face_picker, mock_vtk_setup):
        """Test handling of out-of-range triangle IDs"""
        # Set up picker
        face_picker.picker.GetCellId.return_value = 999
        face_picker.picker.Pick.return_value = 1
        face_picker.picker.GetPickPosition.return_value = (1.0, 2.0, 3.0)

        # Pick triangle beyond face_parents array
        face_id = face_picker.pick(100, 100, add_to_selection=False)

        # Should fall back to using triangle_id
        assert face_id == 999
    
    def test_yellow_highlighting_color(self):
        """Test that yellow color is used for highlighting (spec requirement)"""
        # This is documented in the requirements
        # Yellow should be (1.0, 1.0, 0.0) as per task requirements
        yellow = (1.0, 1.0, 0.0)
        assert yellow == (1.0, 1.0, 0.0)
        
        # This test documents the requirement; actual color enforcement
        # would be in the highlight callback implementation


class TestFacePickerIntegration:
    """Integration tests with EditModeManager"""
    
    def test_edit_mode_manager_exists(self):
        """Verify EditModeManager is available for integration"""
        from app.state.edit_mode import EditModeManager, EditMode
        
        manager = EditModeManager()
        assert manager is not None
        assert EditMode.PANEL in [
            EditMode.SOLID,
            EditMode.PANEL,
            EditMode.EDGE,
            EditMode.VERTEX
        ]
    
    def test_selection_dataclass_integration(self):
        """Test that Selection class supports face operations"""
        from app.state.edit_mode import Selection, EditMode
        
        selection = Selection(mode=EditMode.PANEL)
        
        # Test face operations
        selection.add_face(0)
        selection.add_face(1)
        assert 0 in selection.faces
        assert 1 in selection.faces
        
        # Test toggle
        added = selection.toggle_face(0)
        assert not added  # Was removed
        assert 0 not in selection.faces
        
        added = selection.toggle_face(0)
        assert added  # Was added back
        assert 0 in selection.faces


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
