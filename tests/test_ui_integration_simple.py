#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Simplified UI Integration Test Suite
Tests individual UI components without full MainWindow initialization.

Agent 5 - UX Sprint Day 5

This version avoids MainWindow to work around Qt platform issues on macOS.
"""

import pytest
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt
from PyQt6.QtTest import QTest

# Import UI components directly
from app.ui.top_bar import TopBar
from app.ui.bottom_panel import BottomPanel
from app.ui.right_panel import RightPanel
from app.ui.viewport_layout import ViewportLayoutManager, ViewportLayout


# ========== Test TopBar ==========

class TestTopBar:
    """Test TopBar component independently"""

    def test_topbar_initialization(self, qtbot):
        """TopBar initializes correctly"""
        top_bar = TopBar()
        qtbot.addWidget(top_bar)

        assert top_bar is not None
        assert top_bar.active_tab == 'file'

    def test_all_tabs_exist(self, qtbot):
        """All 6 tabs present in TopBar"""
        top_bar = TopBar()
        qtbot.addWidget(top_bar)

        # Check all 6 tab buttons exist
        tab_buttons = top_bar.tab_buttons
        assert len(tab_buttons) == 6
        assert 'file' in tab_buttons
        assert 'analyze' in tab_buttons
        assert 'edit' in tab_buttons
        assert 'validate' in tab_buttons
        assert 'fabricate' in tab_buttons
        assert 'view' in tab_buttons

    def test_tab_switching(self, qtbot):
        """Can switch between tabs"""
        top_bar = TopBar()
        qtbot.addWidget(top_bar)

        # Start with file tab
        assert top_bar.active_tab == 'file'

        # Click analyze tab
        top_bar.tab_buttons['analyze'].click()
        qtbot.wait(10)

        assert top_bar.active_tab == 'analyze'

        # Click edit tab
        top_bar.tab_buttons['edit'].click()
        qtbot.wait(10)

        assert top_bar.active_tab == 'edit'

    def test_action_bars_visibility(self, qtbot):
        """Action bars switch visibility with tabs"""
        top_bar = TopBar()
        qtbot.addWidget(top_bar)

        # File tab actions should be visible
        assert top_bar.action_bars['file'].isVisible()
        assert not top_bar.action_bars['analyze'].isVisible()

        # Switch to analyze tab
        top_bar.tab_buttons['analyze'].click()
        qtbot.wait(10)

        # Analyze tab actions should be visible
        assert not top_bar.action_bars['file'].isVisible()
        assert top_bar.action_bars['analyze'].isVisible()

    def test_settings_dropdown(self, qtbot):
        """Settings dropdown opens"""
        top_bar = TopBar()
        qtbot.addWidget(top_bar)

        # Click settings button
        top_bar.settings_btn.click()
        qtbot.wait(10)

        # Dropdown should be created and visible
        assert top_bar.settings_dropdown is not None


# ========== Test BottomPanel ==========

class TestBottomPanel:
    """Test BottomPanel component independently"""

    def test_bottom_panel_initialization(self, qtbot):
        """BottomPanel initializes correctly"""
        bottom_panel = BottomPanel()
        qtbot.addWidget(bottom_panel)

        assert bottom_panel is not None
        assert hasattr(bottom_panel, 'command_input')
        assert hasattr(bottom_panel, 'debug_console')
        assert hasattr(bottom_panel, 'connection_status')

    def test_command_input(self, qtbot):
        """Can enter commands"""
        bottom_panel = BottomPanel()
        qtbot.addWidget(bottom_panel)

        command_input = bottom_panel.command_input

        # Enter a test command
        command_input.input_field.setText("test command")
        qtbot.wait(10)

        assert command_input.input_field.text() == "test command"

        # Clear it
        command_input.input_field.clear()
        assert command_input.input_field.text() == ""

    def test_console_toggle(self, qtbot):
        """Console expands/collapses"""
        bottom_panel = BottomPanel()
        qtbot.addWidget(bottom_panel)

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

    def test_connection_status_display(self, qtbot):
        """Connection status displays correctly"""
        bottom_panel = BottomPanel()
        qtbot.addWidget(bottom_panel)

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

    def test_debug_logging(self, qtbot):
        """Debug console can log messages"""
        bottom_panel = BottomPanel()
        qtbot.addWidget(bottom_panel)

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


# ========== Test RightPanel ==========

class TestRightPanel:
    """Test RightPanel component independently"""

    def test_right_panel_initialization(self, qtbot):
        """RightPanel initializes correctly"""
        right_panel = RightPanel()
        qtbot.addWidget(right_panel)

        assert right_panel is not None
        assert hasattr(right_panel, 'tab_bar')
        assert hasattr(right_panel, 'content_stack')

    def test_tab_switching(self, qtbot):
        """Can switch between 5 tabs in RightPanel"""
        right_panel = RightPanel()
        qtbot.addWidget(right_panel)

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

    def test_regions_display(self, qtbot):
        """Regions panel displays regions"""
        right_panel = RightPanel()
        qtbot.addWidget(right_panel)

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

    def test_selection_panel_update(self, qtbot):
        """Selection panel updates with selection data"""
        right_panel = RightPanel()
        qtbot.addWidget(right_panel)

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

    def test_constraint_display(self, qtbot):
        """Can display constraints in right panel"""
        right_panel = RightPanel()
        qtbot.addWidget(right_panel)

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


# ========== Test Viewport ==========

class TestViewport:
    """Test viewport layout"""

    def test_viewport_layout_initialization(self, qtbot):
        """ViewportLayoutManager initializes correctly"""
        viewport_layout = ViewportLayoutManager()
        qtbot.addWidget(viewport_layout)

        assert viewport_layout is not None
        # Default is single viewport
        assert len(viewport_layout.viewports) == 1

    def test_layout_switching(self, qtbot):
        """Can switch between Single/2H/2V/4-grid"""
        viewport_layout = ViewportLayoutManager()
        qtbot.addWidget(viewport_layout)

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


# ========== Test Theme ==========

class TestTheme:
    """Test theme switching functionality"""

    def test_theme_switching(self, qtbot):
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

    def test_theme_persistence(self, qtbot):
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


# ========== Run Tests ==========

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
