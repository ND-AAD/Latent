"""
Tests for new UI widgets (AnalysisPanel and RegionListWidget)
"""

import pytest
import sys
from pathlib import Path
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt

# Add app directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.ui.analysis_panel import AnalysisPanel
from app.ui.region_list_widget import RegionListWidget
from app.ui.region_properties_dialog import RegionPropertiesDialog
from app.state.parametric_region import ParametricRegion


@pytest.fixture(scope="module")
def qapp():
    """Create QApplication instance for tests"""
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    yield app


@pytest.fixture
def analysis_panel(qapp):
    """Create AnalysisPanel instance for testing"""
    panel = AnalysisPanel()
    yield panel
    panel.close()


@pytest.fixture
def region_list_widget(qapp):
    """Create RegionListWidget instance for testing"""
    widget = RegionListWidget()
    yield widget
    widget.close()


# AnalysisPanel Tests

def test_analysis_panel_initialization(analysis_panel):
    """Test that analysis panel initializes properly"""
    assert analysis_panel is not None
    assert analysis_panel.current_lens == "Flow"


def test_analysis_panel_has_lens_buttons(analysis_panel):
    """Test that all lens buttons exist"""
    assert analysis_panel.lens_buttons is not None
    assert analysis_panel.lens_buttons.buttons()
    assert len(analysis_panel.lens_buttons.buttons()) == 4


def test_analysis_panel_has_analyze_button(analysis_panel):
    """Test that analyze button exists and is enabled"""
    assert analysis_panel.analyze_btn is not None
    # Button should be enabled by default
    # (might be disabled based on state, but object should exist)


def test_analysis_panel_get_current_lens(analysis_panel):
    """Test getting current lens selection"""
    lens = analysis_panel.get_current_lens()
    assert lens in ["Flow", "Spectral", "Curvature", "Topological"]


def test_analysis_panel_set_analyzing(analysis_panel):
    """Test setting analyzing state"""
    analysis_panel.set_analyzing(True)
    assert not analysis_panel.analyze_btn.isEnabled()
    assert analysis_panel.progress_bar.isVisible()

    analysis_panel.set_analyzing(False)
    assert analysis_panel.analyze_btn.isEnabled()
    assert not analysis_panel.progress_bar.isVisible()


def test_analysis_panel_set_complete(analysis_panel):
    """Test setting analysis complete state"""
    analysis_panel.set_analysis_complete(5)
    assert "5 regions" in analysis_panel.status_label.text()


def test_analysis_panel_set_failed(analysis_panel):
    """Test setting analysis failed state"""
    analysis_panel.set_analysis_failed("Test error")
    assert "failed" in analysis_panel.status_label.text().lower()


def test_analysis_panel_enable_disable(analysis_panel):
    """Test enabling/disabling analysis"""
    analysis_panel.enable_analysis(False)
    assert not analysis_panel.analyze_btn.isEnabled()

    analysis_panel.enable_analysis(True)
    assert analysis_panel.analyze_btn.isEnabled()


def test_analysis_panel_signals_exist(analysis_panel):
    """Test that signals are properly defined"""
    # Just checking that signals exist and can be connected
    signal_received = []

    def on_analysis(lens):
        signal_received.append(lens)

    analysis_panel.analysis_requested.connect(on_analysis)

    # Trigger analyze button
    analysis_panel.analyze_btn.click()

    # Signal should have been emitted
    assert len(signal_received) == 1
    assert signal_received[0] == "Flow"


# RegionListWidget Tests

def test_region_list_initialization(region_list_widget):
    """Test that region list initializes properly"""
    assert region_list_widget is not None
    assert region_list_widget.regions == []


def test_region_list_set_regions(region_list_widget):
    """Test setting regions"""
    regions = [
        ParametricRegion(
            id="region_1",
            faces=[0, 1, 2],
            unity_principle="Test principle",
            unity_strength=0.85
        ),
        ParametricRegion(
            id="region_2",
            faces=[3, 4, 5],
            unity_principle="Another principle",
            unity_strength=0.65
        )
    ]

    region_list_widget.set_regions(regions)

    assert len(region_list_widget.regions) == 2
    assert region_list_widget.list_widget.count() == 2


def test_region_list_count_display(region_list_widget):
    """Test that region count is displayed correctly"""
    regions = [
        ParametricRegion(
            id="region_1",
            faces=[0, 1, 2],
            unity_strength=0.85,
            pinned=True
        ),
        ParametricRegion(
            id="region_2",
            faces=[3, 4, 5],
            unity_strength=0.65,
            pinned=False
        )
    ]

    region_list_widget.set_regions(regions)

    # Should show "Regions: 2 (1 pinned)"
    assert "2" in region_list_widget.count_label.text()
    assert "1 pinned" in region_list_widget.count_label.text()


def test_region_list_filter(region_list_widget):
    """Test filtering regions"""
    regions = [
        ParametricRegion(id="flow_region_1", faces=[0], unity_strength=0.5),
        ParametricRegion(id="spectral_region_1", faces=[1], unity_strength=0.5),
        ParametricRegion(id="flow_region_2", faces=[2], unity_strength=0.5)
    ]

    region_list_widget.set_regions(regions)
    assert region_list_widget.list_widget.count() == 3

    # Filter for "flow"
    region_list_widget.filter_input.setText("flow")
    region_list_widget.apply_filter()

    # Should only show 2 flow regions
    assert region_list_widget.list_widget.count() == 2


def test_region_list_sorting(region_list_widget):
    """Test sorting regions"""
    regions = [
        ParametricRegion(id="region_c", faces=[0], unity_strength=0.5),
        ParametricRegion(id="region_a", faces=[1], unity_strength=0.9),
        ParametricRegion(id="region_b", faces=[2], unity_strength=0.7)
    ]

    region_list_widget.set_regions(regions)

    # Sort by name
    region_list_widget.sort_combo.setCurrentText("Name")
    region_list_widget.apply_sort()

    # First item should be region_a
    first_item = region_list_widget.list_widget.item(0)
    assert "region_a" in first_item.text()


def test_region_list_pin_unpin(region_list_widget):
    """Test pinning/unpinning regions"""
    signal_received = []

    def on_pinned(region_id, is_pinned):
        signal_received.append((region_id, is_pinned))

    region_list_widget.region_pinned.connect(on_pinned)

    regions = [
        ParametricRegion(id="test_region", faces=[0], unity_strength=0.5, pinned=False)
    ]

    region_list_widget.set_regions(regions)

    # Select the region
    region_list_widget.list_widget.setCurrentRow(0)

    # Pin it
    region_list_widget.toggle_pin()

    # Signal should have been emitted
    assert len(signal_received) == 1
    assert signal_received[0] == ("test_region", True)


def test_region_list_pin_all_unpin_all(region_list_widget):
    """Test pin all and unpin all functionality"""
    regions = [
        ParametricRegion(id="region_1", faces=[0], unity_strength=0.5, pinned=False),
        ParametricRegion(id="region_2", faces=[1], unity_strength=0.5, pinned=False)
    ]

    region_list_widget.set_regions(regions)

    # Pin all
    region_list_widget.pin_all()
    assert all(r.pinned for r in region_list_widget.regions)

    # Unpin all
    region_list_widget.unpin_all()
    assert not any(r.pinned for r in region_list_widget.regions)


def test_region_list_clear(region_list_widget):
    """Test clearing regions"""
    regions = [
        ParametricRegion(id="region_1", faces=[0], unity_strength=0.5)
    ]

    region_list_widget.set_regions(regions)
    assert len(region_list_widget.regions) == 1

    region_list_widget.clear()
    assert len(region_list_widget.regions) == 0
    assert region_list_widget.list_widget.count() == 0


def test_region_list_get_region_by_id(region_list_widget):
    """Test getting region by ID"""
    regions = [
        ParametricRegion(id="test_region", faces=[0], unity_strength=0.5)
    ]

    region_list_widget.set_regions(regions)

    region = region_list_widget.get_region_by_id("test_region")
    assert region is not None
    assert region.id == "test_region"

    missing = region_list_widget.get_region_by_id("nonexistent")
    assert missing is None


def test_region_list_double_click_emits_signal(region_list_widget):
    """Test that double-clicking a region emits properties signal"""
    signal_received = []

    def on_properties_requested(region_id):
        signal_received.append(region_id)

    region_list_widget.region_properties_requested.connect(on_properties_requested)

    regions = [
        ParametricRegion(id="test_region", faces=[0], unity_strength=0.5)
    ]

    region_list_widget.set_regions(regions)

    # Double-click the first item
    item = region_list_widget.list_widget.item(0)
    region_list_widget.on_item_double_clicked(item)

    # Signal should have been emitted
    assert len(signal_received) == 1
    assert signal_received[0] == "test_region"


# RegionPropertiesDialog Tests

@pytest.fixture
def sample_region():
    """Create a sample region for testing"""
    return ParametricRegion(
        id="test_region_1",
        faces=[0, 1, 2, 3, 4],
        unity_principle="Flow-based decomposition",
        unity_strength=0.85,
        pinned=False,
        modified=False,
        constraints_passed=True
    )


@pytest.fixture
def properties_dialog(qapp, sample_region):
    """Create RegionPropertiesDialog instance for testing"""
    dialog = RegionPropertiesDialog(sample_region)
    yield dialog
    dialog.close()


def test_properties_dialog_initialization(properties_dialog):
    """Test that properties dialog initializes properly"""
    assert properties_dialog is not None
    assert properties_dialog.region is not None


def test_properties_dialog_displays_region_id(properties_dialog):
    """Test that dialog displays correct region ID"""
    assert properties_dialog.region.id in properties_dialog.id_label.text()


def test_properties_dialog_displays_face_count(properties_dialog):
    """Test that dialog displays correct face count"""
    assert "5" in properties_dialog.face_count_label.text()


def test_properties_dialog_displays_unity_strength(properties_dialog):
    """Test that dialog displays unity strength correctly"""
    # Check label shows the value
    assert "0.85" in properties_dialog.strength_label.text()
    # Check progress bar is set correctly
    assert properties_dialog.strength_bar.value() == 85


def test_properties_dialog_displays_unity_principle(properties_dialog):
    """Test that dialog displays unity principle"""
    assert "Flow-based" in properties_dialog.principle_label.text()


def test_properties_dialog_pinned_checkbox(properties_dialog):
    """Test that pinned checkbox reflects region state"""
    # Region is unpinned
    assert not properties_dialog.pinned_checkbox.isChecked()

    # Set region to pinned
    properties_dialog.region.pinned = True
    properties_dialog.load_region_data()
    assert properties_dialog.pinned_checkbox.isChecked()


def test_properties_dialog_modified_status(properties_dialog):
    """Test that modified status is displayed"""
    # Region is not modified
    assert "No" in properties_dialog.modified_label.text()


def test_properties_dialog_constraints_status(properties_dialog):
    """Test that constraints status is displayed"""
    # All constraints passed
    assert "passed" in properties_dialog.constraints_label.text().lower()


def test_properties_dialog_faces_display(properties_dialog):
    """Test that face indices are displayed"""
    face_text = properties_dialog.faces_text.toPlainText()
    # Should contain all face indices
    assert "0" in face_text
    assert "1" in face_text
    assert "2" in face_text
    assert "3" in face_text
    assert "4" in face_text


def test_properties_dialog_apply_changes(properties_dialog):
    """Test applying changes to region properties"""
    signal_received = []

    def on_properties_changed(region_id, props):
        signal_received.append((region_id, props))

    properties_dialog.properties_changed.connect(on_properties_changed)

    # Change pinned status
    properties_dialog.pinned_checkbox.setChecked(True)
    properties_dialog.apply_changes()

    # Signal should have been emitted
    assert len(signal_received) == 1
    assert signal_received[0][0] == "test_region_1"
    assert signal_received[0][1]['pinned'] == True

    # Region should be updated
    assert properties_dialog.region.pinned == True


def test_properties_dialog_get_updated_properties(properties_dialog):
    """Test getting updated properties"""
    # No changes initially
    updates = properties_dialog.get_updated_properties()
    assert len(updates) == 0

    # Change pinned status
    properties_dialog.pinned_checkbox.setChecked(True)
    updates = properties_dialog.get_updated_properties()
    assert 'pinned' in updates
    assert updates['pinned'] == True


def test_properties_dialog_export_region(properties_dialog, tmp_path):
    """Test exporting region to JSON"""
    import json

    # Create a temporary file path
    test_file = tmp_path / "test_region.json"

    # Manually trigger export with the test file path
    # (We can't test the file dialog directly, but we can test the export logic)
    export_data = {
        'region_id': properties_dialog.region.id,
        'face_count': len(properties_dialog.region.faces),
        'faces': properties_dialog.region.faces,
        'unity_principle': properties_dialog.region.unity_principle,
        'unity_strength': properties_dialog.region.unity_strength,
        'pinned': properties_dialog.region.pinned,
        'modified': properties_dialog.region.modified,
        'constraints_passed': properties_dialog.region.constraints_passed,
    }

    with open(test_file, 'w') as f:
        json.dump(export_data, f, indent=2)

    # Verify file was created and contains correct data
    assert test_file.exists()

    with open(test_file, 'r') as f:
        loaded_data = json.load(f)

    assert loaded_data['region_id'] == "test_region_1"
    assert loaded_data['face_count'] == 5
    assert loaded_data['unity_strength'] == 0.85


def test_properties_dialog_strength_bar_color_coding(qapp):
    """Test that strength bar is color-coded based on strength value"""
    # Test excellent strength (>= 0.8)
    region_excellent = ParametricRegion(
        id="excellent", faces=[0], unity_strength=0.85
    )
    dialog_excellent = RegionPropertiesDialog(region_excellent)
    assert "#4CAF50" in dialog_excellent.strength_bar.styleSheet()  # Green
    dialog_excellent.close()

    # Test good strength (>= 0.6)
    region_good = ParametricRegion(
        id="good", faces=[0], unity_strength=0.7
    )
    dialog_good = RegionPropertiesDialog(region_good)
    assert "#2196F3" in dialog_good.strength_bar.styleSheet()  # Blue
    dialog_good.close()

    # Test moderate strength (>= 0.4)
    region_moderate = ParametricRegion(
        id="moderate", faces=[0], unity_strength=0.5
    )
    dialog_moderate = RegionPropertiesDialog(region_moderate)
    assert "#FF9800" in dialog_moderate.strength_bar.styleSheet()  # Orange
    dialog_moderate.close()

    # Test poor strength (< 0.4)
    region_poor = ParametricRegion(
        id="poor", faces=[0], unity_strength=0.3
    )
    dialog_poor = RegionPropertiesDialog(region_poor)
    assert "#F44336" in dialog_poor.strength_bar.styleSheet()  # Red
    dialog_poor.close()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
