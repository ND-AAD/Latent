"""
One-Line Accessibility Integration

This module provides a single function to apply all accessibility features
to the main application window.

Usage:
    from app.ui.apply_accessibility import apply_all_accessibility
    apply_all_accessibility(main_window)
"""

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QWidget
from app.ui.accessibility import (
    AccessibilityManager,
    setup_accessible_names,
    setup_focus_policies,
    add_tooltips_with_shortcuts
)
from app.ui.focus_styles import get_accessibility_stylesheet


def apply_all_accessibility(main_window, enable_high_contrast: bool = False):
    """
    Apply all accessibility features to the main window.

    This is the one-line integration function that sets up:
    - Keyboard shortcuts
    - Screen reader support
    - Tab order
    - Focus policies
    - Accessible names and descriptions
    - Focus visibility styles

    Args:
        main_window: MainWindow instance
        enable_high_contrast: Enable high contrast mode (default: False)

    Example:
        >>> from app.ui.apply_accessibility import apply_all_accessibility
        >>> apply_all_accessibility(self)
    """
    print("🔧 Applying accessibility features...")

    # 1. Create accessibility manager
    main_window.accessibility = AccessibilityManager(main_window)

    # 2. Setup keyboard shortcuts
    setup_keyboard_shortcuts(main_window)

    # 3. Setup accessible names for screen readers
    setup_accessible_names(main_window)

    # 4. Setup focus policies
    setup_focus_policies(main_window)

    # 5. Setup tab order
    setup_tab_order(main_window)

    # 6. Apply focus styles
    apply_focus_styles(main_window, enable_high_contrast)

    # 7. Add tooltips with shortcuts
    add_shortcuts_to_tooltips(main_window)

    print("✅ Accessibility features applied successfully!")
    print(f"   - {len(main_window.accessibility.shortcuts)} keyboard shortcuts registered")
    print("   - Screen reader support enabled")
    print("   - Focus visibility enhanced")
    print("   - Tab order configured")
    print("\nPress F1 to see all keyboard shortcuts")


def setup_keyboard_shortcuts(main_window):
    """Setup all standard keyboard shortcuts"""
    acc = main_window.accessibility

    # Tab navigation (F1-F6)
    tab_names = ["FILE", "ANALYZE", "EDIT", "VALIDATE", "FABRICATE", "VIEW"]
    for i, name in enumerate(tab_names):
        key = f"F{i+1}"
        acc.register_shortcut(
            key,
            lambda idx=i: main_window.content_stack.setCurrentIndex(idx)
                if hasattr(main_window, 'content_stack') else None,
            f"{name} tab",
            "Tab Navigation"
        )

    # Edit modes (S, P, E, V)
    if hasattr(main_window, 'state'):
        from app.state.edit_mode import EditMode
        mode_shortcuts = [
            ("S", EditMode.SOLID, "Solid mode"),
            ("P", EditMode.PANEL, "Panel mode"),
            ("E", EditMode.EDGE, "Edge mode"),
            ("V", EditMode.VERTEX, "Vertex mode"),
        ]
        for key, mode, desc in mode_shortcuts:
            acc.register_shortcut(
                key,
                lambda m=mode: main_window.state.edit_mode_manager.set_mode(m),
                desc,
                "Edit Modes"
            )

    # File operations
    file_shortcuts = [
        ("Ctrl+S", "save_session", "Save session"),
        ("Ctrl+O", "connect_to_rhino", "Connect to Rhino"),
        ("Ctrl+R", "load_from_rhino", "Load from Rhino"),
        ("Ctrl+L", "start_live_sync", "Start live sync"),
        ("Ctrl+Q", "close", "Quit application"),
    ]
    for key, method_name, desc in file_shortcuts:
        if hasattr(main_window, method_name):
            acc.register_shortcut(
                key,
                getattr(main_window, method_name),
                desc,
                "File Operations"
            )

    # Edit operations
    edit_shortcuts = [
        ("Ctrl+Z", "undo", "Undo"),
        ("Ctrl+Shift+Z", "redo", "Redo"),
        ("Escape", "clear_selection", "Clear selection"),
        ("Ctrl+A", "select_all", "Select all"),
        ("Ctrl+I", "invert_selection", "Invert selection"),
        ("Ctrl+>", "grow_selection", "Grow selection"),
        ("Ctrl+<", "shrink_selection", "Shrink selection"),
    ]
    for key, method_name, desc in edit_shortcuts:
        if hasattr(main_window, method_name):
            acc.register_shortcut(
                key,
                getattr(main_window, method_name),
                desc,
                "Edit Operations"
            )

    # View controls
    if hasattr(main_window, 'viewport_layout'):
        from app.ui.viewport_layout import ViewportLayout
        view_shortcuts = [
            ("Alt+1", lambda: main_window.viewport_layout.set_layout(ViewportLayout.SINGLE), "Single viewport"),
            ("Alt+2", lambda: main_window.viewport_layout.set_layout(ViewportLayout.TWO_HORIZONTAL), "Two horizontal"),
            ("Alt+3", lambda: main_window.viewport_layout.set_layout(ViewportLayout.TWO_VERTICAL), "Two vertical"),
            ("Alt+4", lambda: main_window.viewport_layout.set_layout(ViewportLayout.FOUR_GRID), "Four grid"),
            ("Space", main_window.viewport_layout.reset_all_cameras, "Reset camera"),
        ]
        for key, callback, desc in view_shortcuts:
            acc.register_shortcut(key, callback, desc, "View Controls")

    # System shortcuts
    system_shortcuts = [
        ("F5", "force_refresh", "Refresh geometry"),
        ("Ctrl+F", "focus_search", "Focus command input"),
        ("Ctrl+`", "toggle_console", "Toggle debug console"),
    ]
    for key, method_name, desc in system_shortcuts:
        if hasattr(main_window, method_name):
            acc.register_shortcut(
                key,
                getattr(main_window, method_name),
                desc,
                "System"
            )

    # Help shortcut
    acc.register_shortcut(
        "F1",
        acc.show_help_dialog,
        "Show keyboard shortcuts help",
        "Help"
    )


def setup_tab_order(main_window):
    """Setup logical tab order for keyboard navigation"""
    # Collect focusable widgets in order
    focusable_widgets = []

    # Top bar buttons
    if hasattr(main_window, 'top_bar'):
        if hasattr(main_window.top_bar, 'tab_buttons'):
            focusable_widgets.extend(main_window.top_bar.tab_buttons.values())

    # Left panel buttons (will vary by active tab)
    # This is dynamically managed by tab content

    # Right panel tabs
    if hasattr(main_window, 'right_panel'):
        # Add right panel tab buttons if they exist
        pass

    # Bottom panel command input
    if hasattr(main_window, 'bottom_panel'):
        if hasattr(main_window.bottom_panel, 'command_input'):
            if hasattr(main_window.bottom_panel.command_input, 'input_field'):
                focusable_widgets.append(main_window.bottom_panel.command_input.input_field)

    # Set tab order
    if len(focusable_widgets) > 1:
        for i in range(len(focusable_widgets) - 1):
            QWidget.setTabOrder(focusable_widgets[i], focusable_widgets[i + 1])


def apply_focus_styles(main_window, enable_high_contrast: bool = False):
    """Apply focus visibility styles"""
    from app.ui.focus_styles import get_accessibility_stylesheet
    from app.ui.styles import ThemeManager

    # Get current theme
    theme = ThemeManager.get_theme()

    # Apply accessibility stylesheet
    accessibility_styles = get_accessibility_stylesheet(theme, enable_high_contrast)

    # Get existing stylesheet
    existing_stylesheet = main_window.styleSheet()

    # Combine stylesheets
    combined_stylesheet = f"""
        {existing_stylesheet}

        /* Accessibility enhancements */
        {accessibility_styles}
    """

    main_window.setStyleSheet(combined_stylesheet)


def add_shortcuts_to_tooltips(main_window):
    """Add keyboard shortcuts to all button tooltips"""
    from PyQt6.QtWidgets import QPushButton, QToolButton

    # Get all shortcuts from accessibility manager
    shortcuts = {}
    if hasattr(main_window, 'accessibility'):
        for key, info in main_window.accessibility.shortcuts.items():
            shortcuts[info['description'].lower()] = key

    # Find all buttons and update tooltips
    for button in main_window.findChildren(QPushButton):
        current_tooltip = button.toolTip()
        if current_tooltip:
            # Check if tooltip text matches a shortcut
            for desc, shortcut in shortcuts.items():
                if desc.lower() in current_tooltip.lower() and '(' not in current_tooltip:
                    button.setToolTip(f"{current_tooltip} ({shortcut})")
                    break

    for button in main_window.findChildren(QToolButton):
        current_tooltip = button.toolTip()
        if current_tooltip:
            for desc, shortcut in shortcuts.items():
                if desc.lower() in current_tooltip.lower() and '(' not in current_tooltip:
                    button.setToolTip(f"{current_tooltip} ({shortcut})")
                    break


def focus_search(main_window):
    """Helper to focus command input"""
    if hasattr(main_window, 'bottom_panel'):
        if hasattr(main_window.bottom_panel, 'command_input'):
            if hasattr(main_window.bottom_panel.command_input, 'input_field'):
                main_window.bottom_panel.command_input.input_field.setFocus()
                if hasattr(main_window, 'log_debug'):
                    main_window.log_debug("Command input focused (Ctrl+F)", "info")


def toggle_console(main_window):
    """Helper to toggle debug console"""
    if hasattr(main_window, 'bottom_panel'):
        main_window.bottom_panel.toggle_console()


# Add these as methods to main window
def add_helper_methods(main_window):
    """Add helper methods to main window if they don't exist"""
    if not hasattr(main_window, 'focus_search'):
        main_window.focus_search = lambda: focus_search(main_window)

    if not hasattr(main_window, 'toggle_console'):
        main_window.toggle_console = lambda: toggle_console(main_window)


# Convenience function for testing
def test_accessibility(main_window):
    """
    Test all accessibility features and report status.

    Args:
        main_window: MainWindow instance

    Returns:
        dict: Test results
    """
    results = {
        'shortcuts': 0,
        'accessible_names': 0,
        'focus_policies': 0,
        'tab_order': 0,
        'tooltips': 0,
    }

    # Count shortcuts
    if hasattr(main_window, 'accessibility'):
        results['shortcuts'] = len(main_window.accessibility.shortcuts)

    # Count accessible names
    for widget in main_window.findChildren(QWidget):
        if widget.accessibleName():
            results['accessible_names'] += 1

    # Count widgets with strong focus policy
    for widget in main_window.findChildren(QWidget):
        if widget.focusPolicy() == Qt.FocusPolicy.StrongFocus:
            results['focus_policies'] += 1

    # Count tooltips
    from PyQt6.QtWidgets import QPushButton, QToolButton
    for button in main_window.findChildren(QPushButton) + main_window.findChildren(QToolButton):
        if button.toolTip():
            results['tooltips'] += 1

    # Print report
    print("\n" + "="*50)
    print("ACCESSIBILITY TEST REPORT")
    print("="*50)
    print(f"Keyboard shortcuts: {results['shortcuts']}")
    print(f"Accessible names:   {results['accessible_names']}")
    print(f"Focus policies:     {results['focus_policies']}")
    print(f"Tooltips:          {results['tooltips']}")
    print("="*50 + "\n")

    return results
