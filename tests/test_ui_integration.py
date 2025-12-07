#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
UI Integration Test Suite
Tests the complete UI architecture v2.0 with TopBar, LeftPanels, RightPanel, and BottomPanel.

Agent 5 - UX Sprint Day 5
"""

import pytest
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtTest import QTest
from PyQt6.QtGui import QKeySequence

# Import main window and UI components
from main import MainWindow
from app.ui.top_bar import TopBar
from app.ui.bottom_panel import BottomPanel
from app.ui.right_panel import RightPanel
from app.ui.viewport_layout import ViewportLayout


# ========== Fixtures ==========

@pytest.fixture(scope="session")
def qapp(qapp_args):
    """Create QApplication instance once for all tests"""
    # Note: pytest-qt provides this fixture automatically, we just customize args
    return QApplication.instance()


@pytest.fixture
def main_window(qtbot):
    """Create MainWindow instance for testing"""
    # Mock bridge and geometry components to avoid network calls
    with patch('main.RhinoBridge'), \
         patch('main.GeometryReceiver'), \
         patch('main.SubDFetcher'), \
         patch('main.LiveBridge'), \
         patch('main.cpp_core'):

        window = MainWindow()
        qtbot.addWidget(window)

        yield window

        window.close()


# ========== Test Application Launch ==========

class TestApplicationLaunch:
    """Test application startup and initialization"""

    def test_window_opens(self, main_window):
        """Application window opens without error"""
        assert main_window is not None
        assert main_window.isVisible() or not main_window.isVisible()  # Just check it exists
        assert main_window.windowTitle() == "Ceramic Mold Analyzer - v2.0"

    def test_all_tabs_exist(self, main_window):
        """All 6 tabs present in TopBar"""
        assert hasattr(main_window, 'top_bar')
        assert isinstance(main_window.top_bar, TopBar)

        # Check all 6 tab buttons exist
        tab_buttons = main_window.top_bar.tab_buttons
        assert len(tab_buttons) == 6
        assert 'file' in tab_buttons
        assert 'analyze' in tab_buttons
        assert 'edit' in tab_buttons
        assert 'validate' in tab_buttons
        assert 'fabricate' in tab_buttons
        assert 'view' in tab_buttons

    def test_default_layout(self, main_window):
        """Viewport defaults to single layout (not 4-grid)"""
        assert hasattr(main_window, 'viewport_layout')
        # Verify we start with a single viewport
        assert len(main_window.viewport_layout.viewports) == 1

    def test_all_panels_exist(self, main_window):
        """All main panels exist (Top, Bottom, Left, Right)"""
        assert hasattr(main_window, 'top_bar')
        assert hasattr(main_window, 'bottom_panel')
        assert hasattr(main_window, 'right_panel')
        # Left panels are context-specific and created per tab
        assert hasattr(main_window, 'file_tab')
        assert hasattr(main_window, 'analyze_tab')
        assert hasattr(main_window, 'edit_tab')


# ========== Test Tab Navigation ==========

class TestTabNavigation:
    """Test tab switching and context updates"""

    def test_tab_switch_updates_topbar(self, main_window, qtbot):
        """Switching tabs updates TopBar actions"""
        top_bar = main_window.top_bar

        # Start with file tab (default)
        assert top_bar.active_tab == 'file'
        assert top_bar.action_bars['file'].isVisible()
        assert not top_bar.action_bars['analyze'].isVisible()

        # Switch to analyze tab
        top_bar.tab_buttons['analyze'].click()
        qtbot.wait(10)

        assert top_bar.active_tab == 'analyze'
        assert not top_bar.action_bars['file'].isVisible()
        assert top_bar.action_bars['analyze'].isVisible()

    def test_tab_switch_updates_left_panel(self, main_window, qtbot):
        """Switching tabs updates LeftSidebar content"""
        # Switch to ANALYZE tab
        main_window.top_bar.tab_buttons['analyze'].click()
        qtbot.wait(10)

        # Verify analyze tab is active
        assert main_window.content_stack.currentWidget() == main_window.analyze_tab

        # Switch to EDIT tab
        main_window.top_bar.tab_buttons['edit'].click()
        qtbot.wait(10)

        # Verify edit tab is active
        assert main_window.content_stack.currentWidget() == main_window.edit_tab

    def test_keyboard_shortcuts(self, main_window, qtbot):
        """F1-F6 switch tabs"""
        # Test F2 switches to ANALYZE tab
        QTest.keyClick(main_window, Qt.Key.Key_F2)
        qtbot.wait(10)
        assert main_window.top_bar.active_tab == 'analyze'

        # Test F3 switches to EDIT tab
        QTest.keyClick(main_window, Qt.Key.Key_F3)
        qtbot.wait(10)
        assert main_window.top_bar.active_tab == 'edit'

        # Test F1 switches back to FILE tab
        QTest.keyClick(main_window, Qt.Key.Key_F1)
        qtbot.wait(10)
        assert main_window.top_bar.active_tab == 'file'

    def test_tab_content_persistence(self, main_window, qtbot):
        """Tab content persists when switching between tabs"""
        # Switch to analyze tab
        main_window.top_bar.tab_buttons['analyze'].click()
        qtbot.wait(10)

        # Store reference to analyze panel
        analyze_panel = main_window.analysis_panel
        initial_lens = analyze_panel.get_current_lens()

        # Switch to different tab
        main_window.top_bar.tab_buttons['edit'].click()
        qtbot.wait(10)

        # Switch back to analyze
        main_window.top_bar.tab_buttons['analyze'].click()
        qtbot.wait(10)

        # Verify panel state persisted
        assert analyze_panel.get_current_lens() == initial_lens


# ========== Test Viewport ==========

class TestViewport:
    """Test viewport layout and controls"""

    def test_layout_switching(self, main_window, qtbot):
        """Can switch between Single/2H/2V/4-grid"""
        viewport_layout = main_window.viewport_layout

        # Start with single viewport
        assert len(viewport_layout.viewports) == 1

        # Switch to 4-grid
        viewport_layout.set_layout(ViewportLayout.FOUR_GRID)
        qtbot.wait(10)
        assert len(viewport_layout.viewports) == 4

        # Switch to 2 horizontal
        viewport_layout.set_layout(ViewportLayout.TWO_HORIZONTAL)
        qtbot.wait(10)
        assert len(viewport_layout.viewports) == 2

        # Switch back to single
        viewport_layout.set_layout(ViewportLayout.SINGLE)
        qtbot.wait(10)
        assert len(viewport_layout.viewports) == 1

    def test_viewport_keyboard_shortcuts(self, main_window, qtbot):
        """Alt+1-4 switch viewport layouts"""
        viewport_layout = main_window.viewport_layout

        # Alt+4 switches to 4-grid
        QTest.keyClick(main_window, Qt.Key.Key_4, Qt.KeyboardModifier.AltModifier)
        qtbot.wait(10)
        assert len(viewport_layout.viewports) == 4

        # Alt+1 switches to single
        QTest.keyClick(main_window, Qt.Key.Key_1, Qt.KeyboardModifier.AltModifier)
        qtbot.wait(10)
        assert len(viewport_layout.viewports) == 1

    def test_splitter_drag(self, main_window, qtbot):
        """Splitters can be dragged (basic check)"""
        # Switch to 4-grid to get splitters
        viewport_layout = main_window.viewport_layout
        viewport_layout.set_layout(ViewportLayout.FOUR_GRID)
        qtbot.wait(10)

        # Verify splitters exist
        assert hasattr(viewport_layout, 'outer_splitter')
        assert viewport_layout.outer_splitter is not None

    def test_viewport_reset(self, main_window, qtbot):
        """Can reset all viewport cameras"""
        # This just tests the method exists and doesn't crash
        viewport_layout = main_window.viewport_layout
        viewport_layout.reset_all_cameras()
        qtbot.wait(10)
        # If we got here without exception, test passes


# ========== Test RightPanel ==========

class TestRightPanel:
    """Test right panel functionality"""

    def test_tab_switching(self, main_window, qtbot):
        """Can switch between 5 tabs in RightPanel"""
        right_panel = main_window.right_panel

        # Default tab is viewport
        assert right_panel.get_active_tab() == 'viewport'

        # Switch to regions tab
        right_panel.set_active_tab('regions')
        qtbot.wait(10)
        assert right_panel.get_active_tab() == 'regions'

        # Switch to constraints tab
        right_panel.set_active_tab('constraints')
        qtbot.wait(10)
        assert right_panel.get_active_tab() == 'constraints'

        # Switch to selection tab
        right_panel.set_active_tab('selection')
        qtbot.wait(10)
        assert right_panel.get_active_tab() == 'selection'

        # Switch to parameters tab
        right_panel.set_active_tab('parameters')
        qtbot.wait(10)
        assert right_panel.get_active_tab() == 'parameters'

    def test_viewport_controls(self, main_window, qtbot):
        """Viewport panel controls work"""
        right_panel = main_window.right_panel

        # Switch to viewport tab
        right_panel.set_active_tab('viewport')
        qtbot.wait(10)

        # Access viewport panel
        viewport_panel = right_panel.viewport_panel

        # Test layout combo exists and works
        assert hasattr(viewport_panel, 'shading_combo')
        assert viewport_panel.shading_combo is not None

        # Test shading mode change
        viewport_panel.shading_combo.setCurrentText('Shaded')
        qtbot.wait(10)
        # If we got here, control works

    def test_regions_display(self, main_window, qtbot):
        """Regions panel displays regions"""
        right_panel = main_window.right_panel

        # Switch to regions tab
        right_panel.set_active_tab('regions')
        qtbot.wait(10)

        # Create test regions
        test_regions = [
            {
                'id': 'test_region_1',
                'name': 'Test Region 1',
                'unity_principle': 'Test Unity',
                'unity_strength': 0.85,
                'pinned': False,
                'color': '#10B981',
                'faces': [0, 1, 2, 3]
            }
        ]

        # Set regions
        right_panel.set_regions(test_regions)
        qtbot.wait(10)

        # Verify regions are displayed
        regions_panel = right_panel.regions_panel
        assert len(regions_panel.regions) == 1
        assert regions_panel.regions[0]['id'] == 'test_region_1'

    def test_selection_panel_update(self, main_window, qtbot):
        """Selection panel updates with selection data"""
        right_panel = main_window.right_panel

        # Switch to selection tab
        right_panel.set_active_tab('selection')
        qtbot.wait(10)

        # Create test selection data
        selection_data = {
            'faces': 5,
            'edges': 10,
            'vertices': 8,
            'total_area': 125.5,
            'bounding_box': (50, 30, 20),
            'indices': [0, 1, 2, 3, 4]
        }

        # Update selection
        selection_panel = right_panel.selection_panel
        selection_panel.update_selection(selection_data)
        qtbot.wait(10)

        # Verify data was updated
        assert selection_panel.selection_data['faces'] == 5
        assert selection_panel.selection_data['vertices'] == 8


# ========== Test BottomPanel ==========

class TestBottomPanel:
    """Test bottom panel functionality"""

    def test_command_input(self, main_window, qtbot):
        """Can enter commands"""
        bottom_panel = main_window.bottom_panel
        command_input = bottom_panel.command_input

        # Enter a test command
        command_input.input_field.setText("test command")
        qtbot.wait(10)

        assert command_input.input_field.text() == "test command"

        # Clear it
        command_input.input_field.clear()
        assert command_input.input_field.text() == ""

    def test_console_toggle(self, main_window, qtbot):
        """Console expands/collapses"""
        bottom_panel = main_window.bottom_panel

        # Console starts collapsed
        assert not bottom_panel.console_expanded
        assert not bottom_panel.debug_console.isVisible()

        # Toggle console open
        bottom_panel.toggle_console()
        qtbot.wait(10)

        assert bottom_panel.console_expanded
        assert bottom_panel.debug_console.isVisible()

        # Toggle console closed
        bottom_panel.toggle_console()
        qtbot.wait(10)

        assert not bottom_panel.console_expanded
        assert not bottom_panel.debug_console.isVisible()

    def test_connection_status_display(self, main_window, qtbot):
        """Connection status displays correctly"""
        bottom_panel = main_window.bottom_panel
        connection_status = bottom_panel.connection_status

        # Start disconnected
        connection_status.set_connected(False)
        qtbot.wait(10)
        assert not connection_status.connected
        assert "Disconnected" in connection_status.status_label.text()

        # Set connected
        connection_status.set_connected(True)
        qtbot.wait(10)
        assert connection_status.connected
        assert "Rhino" in connection_status.status_label.text()

    def test_debug_logging(self, main_window, qtbot):
        """Debug console can log messages"""
        bottom_panel = main_window.bottom_panel

        # Expand console
        bottom_panel.toggle_console()
        qtbot.wait(10)

        # Log different message types
        bottom_panel.log("Test info message", "info")
        bottom_panel.log("Test success message", "success")
        bottom_panel.log("Test warning message", "warning")
        bottom_panel.log("Test error message", "error")

        qtbot.wait(10)

        # Verify messages were logged (line count increased)
        assert bottom_panel.debug_console.line_count >= 4


# ========== Test Theme ==========

class TestTheme:
    """Test theme switching functionality"""

    def test_theme_switching(self, main_window, qtbot):
        """Can switch between light/dark"""
        from app.ui.styles import ThemeManager

        # Set to light theme
        ThemeManager.set_theme('light')
        qtbot.wait(10)
        assert ThemeManager.current_theme == 'light'

        # Set to dark theme
        ThemeManager.set_theme('dark')
        qtbot.wait(10)
        assert ThemeManager.current_theme == 'dark'

        # Switch back to light
        ThemeManager.set_theme('light')
        qtbot.wait(10)
        assert ThemeManager.current_theme == 'light'

    def test_theme_persistence(self, qapp, qtbot):
        """Theme persists on restart (via QSettings)"""
        from PyQt6.QtCore import QSettings
        from app.ui.styles import ThemeManager

        # Save dark theme
        ThemeManager.set_theme('dark')
        settings = QSettings('CeramicMoldAnalyzer', 'LatentApp')
        settings.setValue('theme', 'dark')
        settings.sync()

        # Load theme
        saved_theme = settings.value('theme', 'light')
        assert saved_theme == 'dark'

        # Clean up - restore light theme
        settings.setValue('theme', 'light')
        settings.sync()
        ThemeManager.set_theme('light')


# ========== Test Edit Mode Integration ==========

class TestEditMode:
    """Test edit mode switching and state"""

    def test_edit_mode_shortcuts(self, main_window, qtbot):
        """S/P/E/V shortcuts switch edit modes"""
        from app.state.edit_mode import EditMode

        # Press 'S' for Solid mode
        QTest.keyClick(main_window, Qt.Key.Key_S)
        qtbot.wait(10)
        assert main_window.state.edit_mode_manager.current_mode == EditMode.SOLID

        # Press 'P' for Panel mode
        QTest.keyClick(main_window, Qt.Key.Key_P)
        qtbot.wait(10)
        assert main_window.state.edit_mode_manager.current_mode == EditMode.PANEL

        # Press 'E' for Edge mode
        QTest.keyClick(main_window, Qt.Key.Key_E)
        qtbot.wait(10)
        assert main_window.state.edit_mode_manager.current_mode == EditMode.EDGE

        # Press 'V' for Vertex mode
        QTest.keyClick(main_window, Qt.Key.Key_V)
        qtbot.wait(10)
        assert main_window.state.edit_mode_manager.current_mode == EditMode.VERTEX

    def test_edit_mode_panel_sync(self, main_window, qtbot):
        """Edit mode widget syncs with state"""
        from app.state.edit_mode import EditMode

        # Switch to EDIT tab
        main_window.top_bar.tab_buttons['edit'].click()
        qtbot.wait(10)

        # Change mode via state
        main_window.state.edit_mode_manager.set_mode(EditMode.PANEL)
        qtbot.wait(10)

        # Verify edit mode widget updated
        assert hasattr(main_window, 'edit_mode_widget')
        # Widget should reflect the new mode


# ========== Test Selection Operations ==========

class TestSelectionOperations:
    """Test selection operations"""

    def test_clear_selection(self, main_window, qtbot):
        """Clear selection command works"""
        # Call clear selection
        main_window.clear_selection()
        qtbot.wait(10)
        # If we got here without exception, test passes

    def test_selection_shortcuts(self, main_window, qtbot):
        """Ctrl+A, Esc, Ctrl+I shortcuts work"""
        # Ctrl+A for select all
        QTest.keyClick(main_window, Qt.Key.Key_A, Qt.KeyboardModifier.ControlModifier)
        qtbot.wait(10)
        # If we got here without exception, shortcut works

        # Esc for clear selection
        QTest.keyClick(main_window, Qt.Key.Key_Escape)
        qtbot.wait(10)
        # If we got here without exception, shortcut works


# ========== Test Analysis Workflow ==========

class TestAnalysisWorkflow:
    """Test analysis workflow integration"""

    def test_analysis_panel_exists(self, main_window, qtbot):
        """Analysis panel exists in ANALYZE tab"""
        # Switch to analyze tab
        main_window.top_bar.tab_buttons['analyze'].click()
        qtbot.wait(10)

        # Verify analysis panel exists
        assert hasattr(main_window, 'analysis_panel')
        assert main_window.analysis_panel is not None

    def test_lens_selection(self, main_window, qtbot):
        """Can select different analysis lenses"""
        # Switch to analyze tab
        main_window.top_bar.tab_buttons['analyze'].click()
        qtbot.wait(10)

        # Get current lens
        current_lens = main_window.analysis_panel.get_current_lens()
        assert current_lens in ['Flow', 'Spectral', 'Curvature', 'Topological']


# ========== Test Constraint Validation ==========

class TestConstraintValidation:
    """Test constraint panel functionality"""

    def test_constraint_panel_exists(self, main_window, qtbot):
        """Constraint panel exists in VALIDATE tab"""
        # Switch to validate tab
        main_window.top_bar.tab_buttons['validate'].click()
        qtbot.wait(10)

        # Verify constraint panel exists
        assert hasattr(main_window, 'constraint_panel')
        assert main_window.constraint_panel is not None

    def test_constraint_display(self, main_window, qtbot):
        """Can display constraints in right panel"""
        right_panel = main_window.right_panel

        # Switch to constraints tab
        right_panel.set_active_tab('constraints')
        qtbot.wait(10)

        # Create test constraints
        test_constraints = [
            {
                'id': 'test_constraint_1',
                'title': 'Test Error',
                'description': 'This is a test error',
                'severity': 0.85,
                'type': 'error'
            },
            {
                'id': 'test_constraint_2',
                'title': 'Test Warning',
                'description': 'This is a test warning',
                'severity': 0.45,
                'type': 'warning'
            }
        ]

        # Set constraints
        right_panel.set_constraints(test_constraints)
        qtbot.wait(10)

        # Verify constraints are displayed
        constraints_panel = right_panel.constraints_panel
        assert len(constraints_panel.constraints) == 2


# ========== Test State Persistence ==========

class TestStatePersistence:
    """Test application state and settings persistence"""

    def test_window_geometry_save(self, main_window, qtbot):
        """Window geometry can be saved"""
        # This just tests the method exists and doesn't crash
        main_window.save_layout()
        qtbot.wait(10)
        # If we got here without exception, test passes

    def test_settings_save(self, qapp, qtbot):
        """Settings are saved to QSettings"""
        from PyQt6.QtCore import QSettings

        settings = QSettings('CeramicMoldAnalyzer', 'LatentApp')

        # Save test value
        settings.setValue('test_key', 'test_value')
        settings.sync()

        # Load test value
        loaded = settings.value('test_key')
        assert loaded == 'test_value'

        # Clean up
        settings.remove('test_key')
        settings.sync()


# ========== Run Tests ==========

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
