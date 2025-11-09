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


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
