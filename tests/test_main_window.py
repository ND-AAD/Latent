"""
Tests for MainWindow functionality
Tests dockable panels, toolbars, and layout persistence
"""

import pytest
import sys
from pathlib import Path
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QSettings, Qt

# Add app directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from main import MainWindow


@pytest.fixture(scope="module")
def qapp():
    """Create QApplication instance for tests"""
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    yield app


@pytest.fixture
def main_window(qapp):
    """Create MainWindow instance for testing"""
    # Clear previous settings
    settings = QSettings("ComputationalCeramics", "CeramicMoldAnalyzer")
    settings.clear()

    window = MainWindow()
    yield window
    window.close()


def test_main_window_initialization(main_window):
    """Test that main window initializes properly"""
    assert main_window is not None
    assert main_window.windowTitle() == "Ceramic Mold Analyzer - v0.1.0"


def test_dockable_panels_exist(main_window):
    """Test that all dockable panels are created"""
    assert hasattr(main_window, 'analysis_dock')
    assert hasattr(main_window, 'region_dock')
    assert hasattr(main_window, 'constraint_dock')
    assert hasattr(main_window, 'debug_dock')

    assert main_window.analysis_dock is not None
    assert main_window.region_dock is not None
    assert main_window.constraint_dock is not None
    assert main_window.debug_dock is not None


def test_analysis_panel_exists(main_window):
    """Test that analysis panel is created and accessible"""
    assert hasattr(main_window, 'analysis_panel')
    assert main_window.analysis_panel is not None


def test_region_list_exists(main_window):
    """Test that region list widget is created and accessible"""
    assert hasattr(main_window, 'region_list')
    assert main_window.region_list is not None


def test_toolbars_exist(main_window):
    """Test that toolbars are created"""
    assert hasattr(main_window, 'edit_mode_toolbar')
    assert hasattr(main_window, 'analysis_toolbar')

    assert main_window.edit_mode_toolbar is not None
    assert main_window.analysis_toolbar is not None


def test_menus_exist(main_window):
    """Test that all menus are created"""
    menubar = main_window.menuBar()
    menus = [action.text() for action in menubar.actions()]

    assert "File" in menus
    assert "Edit" in menus
    assert "Analysis" in menus
    assert "View" in menus
    assert "Help" in menus


def test_dock_widgets_are_dockable(main_window):
    """Test that dock widgets can be moved"""
    # Check that docks have proper allowed areas
    assert main_window.analysis_dock.allowedAreas() & Qt.DockWidgetArea.RightDockWidgetArea
    assert main_window.region_dock.allowedAreas() & Qt.DockWidgetArea.RightDockWidgetArea
    assert main_window.debug_dock.allowedAreas() & Qt.DockWidgetArea.BottomDockWidgetArea


def test_layout_save_restore(main_window, qapp):
    """Test that layout can be saved and restored"""
    # Save layout
    main_window.save_layout()

    # Verify settings were saved
    settings = QSettings("ComputationalCeramics", "CeramicMoldAnalyzer")
    assert settings.value("geometry") is not None
    assert settings.value("windowState") is not None


def test_reset_panel_layout(main_window):
    """Test that panel layout can be reset"""
    # This should not crash
    main_window.reset_panel_layout()

    # All docks should be visible after reset
    assert main_window.analysis_dock.isVisible()
    assert main_window.region_dock.isVisible()
    assert main_window.constraint_dock.isVisible()
    assert main_window.debug_dock.isVisible()


def test_status_bar_exists(main_window):
    """Test that status bar is created"""
    assert main_window.status_bar is not None
    assert main_window.status_widget is not None


def test_viewport_layout_is_central(main_window):
    """Test that viewport layout is the central widget"""
    central = main_window.centralWidget()
    assert central is main_window.viewport_layout


def test_analysis_panel_signals_connected(main_window):
    """Test that analysis panel signals are connected"""
    # This tests that the connections don't crash
    # Actual signal emission would require more complex testing
    assert main_window.analysis_panel.receivers(
        main_window.analysis_panel.analysis_requested
    ) > 0


def test_region_list_signals_connected(main_window):
    """Test that region list signals are connected"""
    assert main_window.region_list.receivers(
        main_window.region_list.region_selected
    ) > 0
    assert main_window.region_list.receivers(
        main_window.region_list.region_pinned
    ) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
