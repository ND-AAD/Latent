"""
Example integration of collapsible panels into main window.
This shows how to modify the existing dock widgets to use collapsible sections.
"""

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QScrollArea
from app.ui.collapsible_section import CollapsibleSection, SmartCollapsibleManager


def create_collapsible_dock_content(panels_dict):
    """
    Create a widget containing collapsible sections for dock panels.

    Args:
        panels_dict: Dictionary of {title: widget} pairs

    Returns:
        QWidget containing all collapsible sections
    """
    # Main container
    container = QWidget()
    main_layout = QVBoxLayout()
    main_layout.setSpacing(2)
    main_layout.setContentsMargins(4, 4, 4, 4)

    # Create collapsible sections
    sections = []

    for title, widget in panels_dict.items():
        section = CollapsibleSection(title, start_collapsed=True)
        section.set_content_widget(widget)

        # Set status indicators based on panel type
        if title == "Analysis":
            section.set_status_text("Ready")
            section.set_status_indicator("success")
        elif title == "Regions":
            section.set_status_text("0 regions")
        elif title == "Constraints":
            section.set_status_text("Not validated")
        elif title == "Selection Info":
            section.set_status_text("Solid mode")

        main_layout.addWidget(section)
        sections.append(section)

    # Add stretch to push everything to top
    main_layout.addStretch()
    container.setLayout(main_layout)

    # Create smart manager for accordion behavior
    manager = SmartCollapsibleManager(sections, accordion_mode=True)

    # Return both container and manager for external control
    return container, manager


def modify_main_window_for_collapsible(main_window):
    """
    Modify an existing MainWindow instance to use collapsible panels.
    This is a non-destructive modification that preserves existing functionality.
    """
    from PyQt6.QtWidgets import QDockWidget
    from PyQt6.QtCore import Qt

    # Create unified right dock with all panels as collapsible sections
    unified_dock = QDockWidget("Tools", main_window)
    unified_dock.setAllowedAreas(Qt.DockWidgetArea.LeftDockWidgetArea |
                                  Qt.DockWidgetArea.RightDockWidgetArea)

    # Collect existing panels
    panels = {
        "Analysis": main_window.analysis_panel,
        "Regions": main_window.region_list,
        "Constraints": main_window.constraint_panel,
        "Selection Info": main_window.selection_info_panel
    }

    # Create scroll area for the collapsible content
    scroll_area = QScrollArea()
    scroll_area.setWidgetResizable(True)
    scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

    # Create collapsible container
    container, manager = create_collapsible_dock_content(panels)
    scroll_area.setWidget(container)

    # Set as dock content
    unified_dock.setWidget(scroll_area)

    # Hide old docks
    main_window.analysis_dock.hide()
    main_window.region_dock.hide()
    main_window.constraint_dock.hide()
    main_window.selection_dock.hide()

    # Add new unified dock
    main_window.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, unified_dock)

    # Store references
    main_window.unified_dock = unified_dock
    main_window.panel_manager = manager

    # Add keyboard shortcuts
    from PyQt6.QtGui import QShortcut, QKeySequence

    shortcuts = [
        (QKeySequence("Ctrl+1"), lambda: manager.expand_only(manager.sections[0])),  # Analysis
        (QKeySequence("Ctrl+2"), lambda: manager.expand_only(manager.sections[1])),  # Regions
        (QKeySequence("Ctrl+3"), lambda: manager.expand_only(manager.sections[2])),  # Constraints
        (QKeySequence("Ctrl+4"), lambda: manager.expand_only(manager.sections[3])),  # Selection
        (QKeySequence("Ctrl+0"), lambda: manager.collapse_all()),  # Collapse all
    ]

    for key, callback in shortcuts:
        shortcut = QShortcut(key, main_window)
        shortcut.activated.connect(callback)

    return unified_dock, manager


def create_minimal_layout_patch():
    """
    Create a minimal patch that can be applied to main.py.
    This replaces the create_dock_widgets method with a collapsible version.
    """
    patch_code = '''
# Add this import at the top of main.py:
from app.ui.collapsible_main_integration import modify_main_window_for_collapsible

# Add this line after self.create_dock_widgets() in init_ui (around line 163):
modify_main_window_for_collapsible(self)
'''
    return patch_code


# Example of how the sections update their status
def update_section_status(section, panel_type, data):
    """
    Update the status text of a collapsible section based on panel state.

    Args:
        section: CollapsibleSection instance
        panel_type: Type of panel ("analysis", "regions", "constraints", "selection")
        data: Relevant data for status update
    """
    if panel_type == "analysis":
        if data.get("running"):
            section.set_status_text("Analyzing...")
            section.set_status_indicator("warning")
        elif data.get("complete"):
            section.set_status_text(f"Complete ({data.get('lens', 'Unknown')})")
            section.set_status_indicator("success")
        else:
            section.set_status_text("Ready")
            section.set_status_indicator(None)

    elif panel_type == "regions":
        count = data.get("count", 0)
        pinned = data.get("pinned", 0)
        if pinned > 0:
            section.set_status_text(f"{count} regions ({pinned} pinned)")
        else:
            section.set_status_text(f"{count} regions")

    elif panel_type == "constraints":
        errors = data.get("errors", 0)
        warnings = data.get("warnings", 0)
        if errors > 0:
            section.set_status_text(f"{errors} errors, {warnings} warnings")
            section.set_status_indicator("error")
        elif warnings > 0:
            section.set_status_text(f"{warnings} warnings")
            section.set_status_indicator("warning")
        else:
            section.set_status_text("All constraints passed")
            section.set_status_indicator("success")

    elif panel_type == "selection":
        mode = data.get("mode", "Solid")
        count = data.get("count", 0)
        if count > 0:
            section.set_status_text(f"{mode} mode - {count} selected")
        else:
            section.set_status_text(f"{mode} mode")