"""
Tests for Agent 22 components: Edit Mode Toolbar and Selection Info Panel
"""

import pytest
import sys
from pathlib import Path

# Add app directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Check for PyQt6 availability
try:
    from PyQt6.QtWidgets import QApplication
    from PyQt6.QtCore import Qt, QTimer
    from app.ui.edit_mode_toolbar import EditModeToolBar
    from app.ui.selection_info_panel import SelectionInfoPanel
    from app.state.edit_mode import EditMode, Selection
    PYQT_AVAILABLE = True
except ImportError as e:
    PYQT_AVAILABLE = False
    pytestmark = pytest.mark.skip(reason="PyQt6 not available")


@pytest.fixture(scope="module")
def qapp():
    """Create QApplication instance for tests"""
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    yield app


@pytest.fixture
def edit_mode_toolbar(qapp):
    """Create EditModeToolBar instance for testing"""
    toolbar = EditModeToolBar()
    yield toolbar
    toolbar.close()


@pytest.fixture
def selection_info_panel(qapp):
    """Create SelectionInfoPanel instance for testing"""
    panel = SelectionInfoPanel()
    yield panel
    panel.close()


# EditModeToolBar Tests

def test_toolbar_initialization(edit_mode_toolbar):
    """Test that toolbar initializes properly"""
    assert edit_mode_toolbar is not None
    assert edit_mode_toolbar.button_group is not None
    assert edit_mode_toolbar.mode_buttons is not None
    assert edit_mode_toolbar.selection_info is not None


def test_toolbar_has_all_mode_buttons(edit_mode_toolbar):
    """Test that all edit mode buttons exist"""
    assert EditMode.SOLID in edit_mode_toolbar.mode_buttons
    assert EditMode.PANEL in edit_mode_toolbar.mode_buttons
    assert EditMode.EDGE in edit_mode_toolbar.mode_buttons
    assert EditMode.VERTEX in edit_mode_toolbar.mode_buttons


def test_toolbar_default_mode(edit_mode_toolbar):
    """Test that default mode is SOLID"""
    solid_button = edit_mode_toolbar.mode_buttons[EditMode.SOLID]
    assert solid_button.isChecked()


def test_toolbar_set_mode(edit_mode_toolbar):
    """Test programmatically setting mode"""
    edit_mode_toolbar.set_mode(EditMode.PANEL)
    panel_button = edit_mode_toolbar.mode_buttons[EditMode.PANEL]
    assert panel_button.isChecked()

    edit_mode_toolbar.set_mode(EditMode.EDGE)
    edge_button = edit_mode_toolbar.mode_buttons[EditMode.EDGE]
    assert edge_button.isChecked()


def test_toolbar_mode_changed_signal(edit_mode_toolbar):
    """Test that mode_changed signal is emitted"""
    signal_received = []

    def on_mode_changed(mode):
        signal_received.append(mode)

    edit_mode_toolbar.mode_changed.connect(on_mode_changed)

    # Click panel button
    panel_button = edit_mode_toolbar.mode_buttons[EditMode.PANEL]
    panel_button.click()

    # Signal should have been emitted
    assert len(signal_received) == 1
    assert signal_received[0] == EditMode.PANEL


def test_toolbar_update_selection_info(edit_mode_toolbar):
    """Test updating selection info display"""
    edit_mode_toolbar.update_selection_info("5 faces")
    assert edit_mode_toolbar.selection_info.text() == "5 faces"

    edit_mode_toolbar.update_selection_info("No selection")
    assert edit_mode_toolbar.selection_info.text() == "No selection"


def test_toolbar_clear_selection_signal(edit_mode_toolbar):
    """Test clear_selection_requested signal"""
    signal_received = []

    def on_clear():
        signal_received.append(True)

    edit_mode_toolbar.clear_selection_requested.connect(on_clear)
    edit_mode_toolbar.clear_selection()

    assert len(signal_received) == 1


def test_toolbar_select_all_signal(edit_mode_toolbar):
    """Test select_all_requested signal"""
    signal_received = []

    def on_select_all():
        signal_received.append(True)

    edit_mode_toolbar.select_all_requested.connect(on_select_all)
    edit_mode_toolbar.select_all()

    assert len(signal_received) == 1


def test_toolbar_invert_selection_signal(edit_mode_toolbar):
    """Test invert_selection_requested signal"""
    signal_received = []

    def on_invert():
        signal_received.append(True)

    edit_mode_toolbar.invert_selection_requested.connect(on_invert)
    edit_mode_toolbar.invert_selection()

    assert len(signal_received) == 1


def test_toolbar_grow_selection_signal(edit_mode_toolbar):
    """Test grow_selection_requested signal"""
    signal_received = []

    def on_grow():
        signal_received.append(True)

    edit_mode_toolbar.grow_selection_requested.connect(on_grow)
    edit_mode_toolbar.grow_selection()

    assert len(signal_received) == 1


def test_toolbar_shrink_selection_signal(edit_mode_toolbar):
    """Test shrink_selection_requested signal"""
    signal_received = []

    def on_shrink():
        signal_received.append(True)

    edit_mode_toolbar.shrink_selection_requested.connect(on_shrink)
    edit_mode_toolbar.shrink_selection()

    assert len(signal_received) == 1


# SelectionInfoPanel Tests

def test_panel_initialization(selection_info_panel):
    """Test that panel initializes properly"""
    assert selection_info_panel is not None
    assert selection_info_panel.mode_label is not None
    assert selection_info_panel.faces_label is not None
    assert selection_info_panel.edges_label is not None
    assert selection_info_panel.vertices_label is not None
    assert selection_info_panel.indices_list is not None
    assert selection_info_panel.export_btn is not None
    assert selection_info_panel.copy_btn is not None


def test_panel_default_display(selection_info_panel):
    """Test default display state"""
    assert "Mode: Solid" in selection_info_panel.mode_label.text()
    assert "Faces: 0" in selection_info_panel.faces_label.text()
    assert "Edges: 0" in selection_info_panel.edges_label.text()
    assert "Vertices: 0" in selection_info_panel.vertices_label.text()
    assert not selection_info_panel.export_btn.isEnabled()
    assert not selection_info_panel.copy_btn.isEnabled()


def test_panel_update_with_face_selection(selection_info_panel):
    """Test updating panel with face selection"""
    selection = Selection(mode=EditMode.PANEL)
    selection.faces.add(0)
    selection.faces.add(1)
    selection.faces.add(2)

    selection_info_panel.update_selection(selection)

    assert "Mode: Panel" in selection_info_panel.mode_label.text()
    assert "Faces: 3" in selection_info_panel.faces_label.text()
    assert selection_info_panel.export_btn.isEnabled()
    assert selection_info_panel.copy_btn.isEnabled()


def test_panel_update_with_edge_selection(selection_info_panel):
    """Test updating panel with edge selection"""
    selection = Selection(mode=EditMode.EDGE)
    selection.edges.add(10)
    selection.edges.add(11)

    selection_info_panel.update_selection(selection)

    assert "Mode: Edge" in selection_info_panel.mode_label.text()
    assert "Edges: 2" in selection_info_panel.edges_label.text()
    assert not selection_info_panel.export_btn.isEnabled()  # Only for faces
    assert selection_info_panel.copy_btn.isEnabled()


def test_panel_update_with_vertex_selection(selection_info_panel):
    """Test updating panel with vertex selection"""
    selection = Selection(mode=EditMode.VERTEX)
    selection.vertices.add(20)
    selection.vertices.add(21)
    selection.vertices.add(22)

    selection_info_panel.update_selection(selection)

    assert "Mode: Vertex" in selection_info_panel.mode_label.text()
    assert "Vertices: 3" in selection_info_panel.vertices_label.text()
    assert not selection_info_panel.export_btn.isEnabled()  # Only for faces
    assert selection_info_panel.copy_btn.isEnabled()


def test_panel_indices_list_display(selection_info_panel):
    """Test that indices are displayed in the list"""
    selection = Selection(mode=EditMode.PANEL)
    selection.faces.add(0)
    selection.faces.add(5)
    selection.faces.add(10)

    selection_info_panel.update_selection(selection)

    # Check that list has items
    assert selection_info_panel.indices_list.count() > 0

    # Find items with face indices
    items = [selection_info_panel.indices_list.item(i).text()
             for i in range(selection_info_panel.indices_list.count())]

    # Should contain face section and indices
    assert any("Faces" in item for item in items)
    assert any("0" in item for item in items)
    assert any("5" in item for item in items)
    assert any("10" in item for item in items)


def test_panel_empty_selection_display(selection_info_panel):
    """Test display with empty selection"""
    selection = Selection(mode=EditMode.SOLID)

    selection_info_panel.update_selection(selection)

    assert "Faces: 0" in selection_info_panel.faces_label.text()
    assert "Edges: 0" in selection_info_panel.edges_label.text()
    assert "Vertices: 0" in selection_info_panel.vertices_label.text()

    # Check for "No selection" message in list
    items = [selection_info_panel.indices_list.item(i).text()
             for i in range(selection_info_panel.indices_list.count())]
    assert any("No selection" in item for item in items)


def test_panel_export_signal(selection_info_panel):
    """Test export_to_region_requested signal"""
    signal_received = []

    def on_export():
        signal_received.append(True)

    selection_info_panel.export_to_region_requested.connect(on_export)

    # Set up a face selection to enable the button
    selection = Selection(mode=EditMode.PANEL)
    selection.faces.add(0)
    selection_info_panel.update_selection(selection)

    # Click the export button
    selection_info_panel.export_btn.click()

    assert len(signal_received) == 1


def test_panel_clear(selection_info_panel):
    """Test clearing the panel"""
    # First add some selection
    selection = Selection(mode=EditMode.PANEL)
    selection.faces.add(0)
    selection_info_panel.update_selection(selection)

    # Now clear
    selection_info_panel.clear()

    # Should be back to empty state
    assert "Faces: 0" in selection_info_panel.faces_label.text()
    assert not selection_info_panel.export_btn.isEnabled()


def test_panel_mixed_selection_display(selection_info_panel):
    """Test displaying mixed selection (multiple types)"""
    selection = Selection(mode=EditMode.PANEL)
    selection.faces.add(0)
    selection.faces.add(1)
    selection.edges.add(10)  # Manually added for testing
    selection.vertices.add(20)  # Manually added for testing

    selection_info_panel.update_selection(selection)

    assert "Faces: 2" in selection_info_panel.faces_label.text()
    assert "Edges: 1" in selection_info_panel.edges_label.text()
    assert "Vertices: 1" in selection_info_panel.vertices_label.text()


def test_panel_statistics_labels_exist(selection_info_panel):
    """Test that statistics labels exist (even if showing placeholder)"""
    assert selection_info_panel.area_label is not None
    assert selection_info_panel.length_label is not None
    assert selection_info_panel.bounds_label is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
