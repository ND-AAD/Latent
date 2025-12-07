"""
Accessibility Module

Provides centralized accessibility features including:
- Keyboard shortcut management
- Screen reader support
- Focus management
- Tab order configuration
"""

from PyQt6.QtWidgets import QWidget, QMessageBox
from PyQt6.QtGui import QShortcut, QKeySequence
from PyQt6.QtCore import Qt
from typing import Callable, Optional


class AccessibilityManager:
    """
    Centralized accessibility management for the application.

    Provides methods to:
    - Register keyboard shortcuts with descriptions
    - Set accessible names and descriptions
    - Manage focus order
    - Generate help dialogs
    """

    def __init__(self, main_window):
        """
        Initialize the accessibility manager.

        Args:
            main_window: Reference to the main application window
        """
        self.main_window = main_window
        self.shortcuts = {}  # Store all registered shortcuts

    def register_shortcut(self, key: str, callback: Callable,
                         description: str, context: str = "General"):
        """
        Register a keyboard shortcut with description.

        Args:
            key: Shortcut key sequence (e.g., "Ctrl+S")
            callback: Function to call when shortcut is activated
            description: Human-readable description
            context: Category (e.g., "File", "Edit", "View")
        """
        shortcut = QShortcut(QKeySequence(key), self.main_window)
        shortcut.activated.connect(callback)
        shortcut.setContext(Qt.ShortcutContext.ApplicationShortcut)

        self.shortcuts[key] = {
            'description': description,
            'context': context,
            'shortcut': shortcut
        }

    def set_accessible_properties(self, widget: QWidget, name: str,
                                  description: Optional[str] = None):
        """
        Set accessible name and description for a widget.

        Args:
            widget: Widget to set properties for
            name: Accessible name
            description: Optional detailed description
        """
        widget.setAccessibleName(name)
        if description:
            widget.setAccessibleDescription(description)

    def set_tab_order(self, widgets: list):
        """
        Set the tab order for a list of widgets.

        Args:
            widgets: List of widgets in desired tab order
        """
        for i in range(len(widgets) - 1):
            QWidget.setTabOrder(widgets[i], widgets[i + 1])

    def generate_help_html(self) -> str:
        """
        Generate HTML help text for all registered shortcuts.

        Returns:
            HTML formatted help text
        """
        # Group shortcuts by context
        by_context = {}
        for key, info in self.shortcuts.items():
            context = info['context']
            if context not in by_context:
                by_context[context] = []
            by_context[context].append((key, info['description']))

        # Build HTML
        html = "<h2>Keyboard Shortcuts</h2>\n"

        for context in sorted(by_context.keys()):
            html += f"<h3>{context}</h3>\n<ul>\n"
            for key, desc in sorted(by_context[context]):
                html += f"<li><b>{key}</b> - {desc}</li>\n"
            html += "</ul>\n"

        return html

    def show_help_dialog(self):
        """Show keyboard shortcuts help dialog"""
        help_text = self.generate_help_html()
        QMessageBox.information(self.main_window, "Keyboard Shortcuts", help_text)


def setup_standard_shortcuts(accessibility_manager: AccessibilityManager, app):
    """
    Setup standard accessibility shortcuts for the application.

    Args:
        accessibility_manager: AccessibilityManager instance
        app: Main application instance
    """
    # Tab navigation (F1-F6)
    tab_names = ["FILE", "ANALYZE", "EDIT", "VALIDATE", "FABRICATE", "VIEW"]
    for i, name in enumerate(tab_names):
        key = f"F{i+1}"
        accessibility_manager.register_shortcut(
            key,
            lambda idx=i: app.content_stack.setCurrentIndex(idx),
            f"{name} tab",
            "Tab Navigation"
        )

    # Edit modes (S, P, E, V)
    from app.state.edit_mode import EditMode
    mode_shortcuts = [
        ("S", EditMode.SOLID, "Solid mode"),
        ("P", EditMode.PANEL, "Panel mode"),
        ("E", EditMode.EDGE, "Edge mode"),
        ("V", EditMode.VERTEX, "Vertex mode"),
    ]
    for key, mode, desc in mode_shortcuts:
        accessibility_manager.register_shortcut(
            key,
            lambda m=mode: app.state.edit_mode_manager.set_mode(m),
            desc,
            "Edit Modes"
        )

    # File operations
    file_shortcuts = [
        ("Ctrl+S", app.save_session, "Save session"),
        ("Ctrl+O", app.connect_to_rhino, "Connect to Rhino"),
        ("Ctrl+R", app.load_from_rhino, "Load from Rhino"),
        ("Ctrl+L", app.start_live_sync, "Start live sync"),
        ("Ctrl+Q", app.close, "Quit application"),
    ]
    for key, callback, desc in file_shortcuts:
        accessibility_manager.register_shortcut(key, callback, desc, "File Operations")

    # Edit operations
    edit_shortcuts = [
        ("Ctrl+Z", app.undo, "Undo"),
        ("Ctrl+Shift+Z", app.redo, "Redo"),
        ("Escape", app.clear_selection, "Clear selection"),
        ("Ctrl+A", app.select_all, "Select all"),
        ("Ctrl+I", app.invert_selection, "Invert selection"),
        ("Ctrl+>", app.grow_selection, "Grow selection"),
        ("Ctrl+<", app.shrink_selection, "Shrink selection"),
    ]
    for key, callback, desc in edit_shortcuts:
        accessibility_manager.register_shortcut(key, callback, desc, "Edit Operations")

    # View controls
    from app.ui.viewport_layout import ViewportLayout
    view_shortcuts = [
        ("Alt+1", lambda: app.viewport_layout.set_layout(ViewportLayout.SINGLE), "Single viewport"),
        ("Alt+2", lambda: app.viewport_layout.set_layout(ViewportLayout.TWO_HORIZONTAL), "Two horizontal"),
        ("Alt+3", lambda: app.viewport_layout.set_layout(ViewportLayout.TWO_VERTICAL), "Two vertical"),
        ("Alt+4", lambda: app.viewport_layout.set_layout(ViewportLayout.FOUR_GRID), "Four grid"),
        ("Space", app.viewport_layout.reset_all_cameras, "Reset camera"),
    ]
    for key, callback, desc in view_shortcuts:
        accessibility_manager.register_shortcut(key, callback, desc, "View Controls")

    # System shortcuts
    system_shortcuts = [
        ("F5", app.force_refresh, "Refresh geometry"),
        ("F1", accessibility_manager.show_help_dialog, "Show keyboard shortcuts help"),
    ]
    for key, callback, desc in system_shortcuts:
        accessibility_manager.register_shortcut(key, callback, desc, "System")


def setup_focus_policies(main_window):
    """
    Setup focus policies for main UI components.

    Args:
        main_window: Main application window
    """
    # Bottom panel command input should have strong focus
    if hasattr(main_window, 'bottom_panel'):
        if hasattr(main_window.bottom_panel, 'command_input'):
            if hasattr(main_window.bottom_panel.command_input, 'input_field'):
                main_window.bottom_panel.command_input.input_field.setFocusPolicy(
                    Qt.FocusPolicy.StrongFocus
                )

    # Buttons should be clickable with space/enter
    # This is default Qt behavior, but we ensure it's set
    from PyQt6.QtWidgets import QPushButton
    for button in main_window.findChildren(QPushButton):
        button.setFocusPolicy(Qt.FocusPolicy.StrongFocus)


def setup_accessible_names(main_window):
    """
    Setup accessible names and descriptions for screen readers.

    Args:
        main_window: Main application window
    """
    # Main window
    main_window.setAccessibleName("Ceramic Mold Analyzer Main Window")
    main_window.setAccessibleDescription(
        "Main application window for discovering mathematical decompositions of SubD surfaces"
    )

    # Top bar
    if hasattr(main_window, 'top_bar'):
        main_window.top_bar.setAccessibleName("Top Navigation Bar")
        main_window.top_bar.setAccessibleDescription("Main navigation tabs and primary actions")

    # Bottom panel
    if hasattr(main_window, 'bottom_panel'):
        main_window.bottom_panel.setAccessibleName("Bottom System Panel")
        main_window.bottom_panel.setAccessibleDescription(
            "Connection status, command input, and debug console"
        )

    # Viewport
    if hasattr(main_window, 'viewport_layout'):
        main_window.viewport_layout.setAccessibleName("3D Viewport Area")
        main_window.viewport_layout.setAccessibleDescription(
            "Main 3D visualization area showing SubD geometry and analysis results"
        )

    # Right panel
    if hasattr(main_window, 'right_panel'):
        main_window.right_panel.setAccessibleName("Properties Panel")
        main_window.right_panel.setAccessibleDescription("Contextual properties and settings panel")

    # Tab content areas
    for tab_name in ["FILE", "ANALYZE", "EDIT", "VALIDATE", "FABRICATE", "VIEW"]:
        attr_name = f'{tab_name.lower()}_tab'
        if hasattr(main_window, attr_name):
            tab = getattr(main_window, attr_name)
            tab.setAccessibleName(f"{tab_name} Tab Content")
            tab.setAccessibleDescription(f"Content and tools for {tab_name} operations")


def add_tooltips_with_shortcuts(widget, tooltip_text: str, shortcut: Optional[str] = None):
    """
    Add tooltip with optional keyboard shortcut display.

    Args:
        widget: Widget to add tooltip to
        tooltip_text: Base tooltip text
        shortcut: Optional shortcut key (e.g., "Ctrl+S")
    """
    if shortcut:
        full_tooltip = f"{tooltip_text} ({shortcut})"
    else:
        full_tooltip = tooltip_text

    widget.setToolTip(full_tooltip)
