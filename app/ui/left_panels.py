"""
Left sidebar panels with advanced tools for each workflow tab.

Architecture:
- LeftSidebar: Main container that switches content based on active tab
- Tab-specific tool panels: FileTools, AnalyzeTools, EditTools, ValidateTools, FabricateTools, ViewTools
- SidebarButton: Consistent button styling for all tools
- ExpandableSection: Collapsible sections for complex tool groups
- SectionLabel: Section headers for grouping related tools

Edge Cases & Polish:
- Disabled button styling (grey text, no hover, not-allowed cursor)
- Expandable section state persistence via QSettings
- Scroll for long tool lists with QScrollArea
- Tool availability based on application state
- Descriptive tooltips with keyboard shortcuts
- Error handling without crashes
- Visual feedback (highlight, loading, success)
- Full keyboard navigation support
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFrame, QSpinBox, QDoubleSpinBox, QComboBox, QSizePolicy,
    QScrollArea, QGraphicsOpacityEffect
)
from PyQt6.QtCore import Qt, pyqtSignal, QSize, QSettings, QTimer, QPropertyAnimation
from PyQt6.QtGui import QFont, QColor


class SectionLabel(QLabel):
    """Section header label with small caps styling."""

    def __init__(self, text: str, parent=None):
        super().__init__(text, parent)

        font = QFont()
        font.setPointSize(9)
        font.setCapitalization(QFont.Capitalization.AllUppercase)
        self.setFont(font)

        self.setStyleSheet("""
            QLabel {
                color: #888;
                padding-left: 12px;
                padding-top: 4px;
                padding-bottom: 2px;
            }
        """)


class SidebarButton(QPushButton):
    """Consistent button styling for sidebar tools with state-aware behavior."""

    def __init__(self, text: str, parent=None, enabled: bool = True,
                 tooltip: str = "", disabled_reason: str = "", shortcut: str = ""):
        super().__init__(text, parent)

        self.base_text = text
        self.disabled_reason = disabled_reason
        self.shortcut = shortcut
        self._is_loading = False
        self._animation = None

        self.setEnabled(enabled)
        self.update_cursor()
        self.update_tooltip(tooltip, disabled_reason, shortcut)

        font = QFont()
        font.setPointSize(10)
        self.setFont(font)

        self.setStyleSheet("""
            QPushButton {
                text-align: left;
                padding: 6px 12px;
                border: none;
                border-radius: 4px;
                background: transparent;
                color: #333;
            }
            QPushButton:hover:enabled {
                background: #e0e0e0;
                color: #000;
            }
            QPushButton:pressed:enabled {
                background: #d0d0d0;
            }
            QPushButton:disabled {
                color: #999;
                background: transparent;
            }
            QPushButton:focus {
                outline: 2px solid #2196F3;
                outline-offset: -2px;
            }
        """)

        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.setMinimumHeight(28)

        # Enable keyboard focus
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)

    def update_cursor(self):
        """Update cursor based on enabled state."""
        if self.isEnabled():
            self.setCursor(Qt.CursorShape.PointingHandCursor)
        else:
            self.setCursor(Qt.CursorShape.ForbiddenCursor)

    def update_tooltip(self, tooltip: str = "", disabled_reason: str = "", shortcut: str = ""):
        """Update tooltip with description, shortcut, and disabled reason."""
        parts = []

        if tooltip:
            parts.append(tooltip)

        if shortcut:
            parts.append(f"\n\nShortcut: {shortcut}")

        if not self.isEnabled() and (disabled_reason or self.disabled_reason):
            reason = disabled_reason or self.disabled_reason
            parts.append(f"\n\nDisabled: {reason}")

        self.setToolTip("".join(parts) if parts else "")

    def setEnabled(self, enabled: bool):
        """Override setEnabled to update cursor and tooltip."""
        super().setEnabled(enabled)
        self.update_cursor()
        self.update_tooltip()

    def set_loading(self, loading: bool):
        """Show loading state for long operations."""
        self._is_loading = loading
        if loading:
            self.setText(f"⏳ {self.base_text}")
            self.setEnabled(False)
        else:
            self.setText(self.base_text)
            self.setEnabled(True)

    def flash_success(self):
        """Briefly show success checkmark."""
        original_text = self.text()
        self.setText(f"✓ {self.base_text}")

        # Change back after 1 second
        QTimer.singleShot(1000, lambda: self.setText(original_text))

    def flash_highlight(self):
        """Brief highlight when tool clicked."""
        # Store original stylesheet
        original_style = self.styleSheet()

        # Add highlight
        highlight_style = original_style + """
            QPushButton {
                background: #bbdefb !important;
            }
        """
        self.setStyleSheet(highlight_style)

        # Restore after 150ms
        QTimer.singleShot(150, lambda: self.setStyleSheet(original_style))

    def keyPressEvent(self, event):
        """Handle keyboard activation."""
        if event.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter, Qt.Key.Key_Space):
            if self.isEnabled():
                self.click()
        else:
            super().keyPressEvent(event)


class ExpandableSection(QWidget):
    """Collapsible section with header and content area with persistent state."""

    clicked = pyqtSignal(str)  # Emits tool name when content buttons are clicked
    toggled = pyqtSignal(bool)  # Emits when expanded/collapsed

    def __init__(self, title: str, parent=None, settings_key: str = None):
        super().__init__(parent)

        self.title = title
        self.settings_key = settings_key or f"expandable_section/{title}"

        # Restore saved state or default to collapsed
        settings = QSettings("NDAAD", "CeramicMoldAnalyzer")
        self.is_expanded = settings.value(self.settings_key, False, type=bool)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)

        # Header button
        arrow = "▼" if self.is_expanded else "▶"
        self.header_btn = QPushButton(f"{arrow} {title}")
        self.header_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.header_btn.setFocusPolicy(Qt.FocusPolicy.StrongFocus)

        font = QFont()
        font.setPointSize(10)
        self.header_btn.setFont(font)

        self.header_btn.setStyleSheet("""
            QPushButton {
                text-align: left;
                padding: 6px 12px;
                border: none;
                border-radius: 4px;
                background: transparent;
                color: #333;
            }
            QPushButton:hover {
                background: #e0e0e0;
                color: #000;
            }
            QPushButton:focus {
                outline: 2px solid #2196F3;
                outline-offset: -2px;
            }
        """)

        self.header_btn.clicked.connect(self._toggle)
        layout.addWidget(self.header_btn)

        # Content area
        self.content_widget = QWidget()
        self.content_widget.setStyleSheet("""
            QWidget {
                background: #f5f5f5;
                border-radius: 4px;
                padding: 8px;
                margin-left: 16px;
            }
        """)
        self.content_layout = QVBoxLayout(self.content_widget)
        self.content_layout.setContentsMargins(8, 8, 8, 8)
        self.content_layout.setSpacing(8)

        # Set initial visibility
        self.content_widget.setVisible(self.is_expanded)
        layout.addWidget(self.content_widget)

    def _toggle(self):
        """Toggle expanded/collapsed state and save to settings."""
        self.is_expanded = not self.is_expanded

        if self.is_expanded:
            self.header_btn.setText(f"▼ {self.title}")
            self.content_widget.show()
        else:
            self.header_btn.setText(f"▶ {self.title}")
            self.content_widget.hide()

        # Save state
        settings = QSettings("NDAAD", "CeramicMoldAnalyzer")
        settings.setValue(self.settings_key, self.is_expanded)

        # Emit signal
        self.toggled.emit(self.is_expanded)

    def keyPressEvent(self, event):
        """Handle keyboard navigation in section."""
        if event.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter, Qt.Key.Key_Space):
            self._toggle()
        elif event.key() == Qt.Key.Key_Down:
            # Move focus to first child button
            if self.is_expanded:
                for i in range(self.content_layout.count()):
                    widget = self.content_layout.itemAt(i).widget()
                    if isinstance(widget, QPushButton) and widget.isEnabled():
                        widget.setFocus()
                        break
        else:
            super().keyPressEvent(event)

    def add_button(self, text: str, tool_name: str = None):
        """Add a button to the content area."""
        btn = QPushButton(text)
        btn.setStyleSheet("""
            QPushButton {
                background: white;
                border: 1px solid #ccc;
                border-radius: 4px;
                padding: 6px 8px;
                text-align: left;
                color: #333;
            }
            QPushButton:hover {
                background: #f9f9f9;
                border-color: #999;
            }
        """)

        font = QFont()
        font.setPointSize(10)
        btn.setFont(font)

        if tool_name:
            btn.clicked.connect(lambda: self.clicked.emit(tool_name))

        self.content_layout.addWidget(btn)
        return btn

    def add_widget(self, widget: QWidget):
        """Add a custom widget to the content area."""
        self.content_layout.addWidget(widget)


class BaseToolPanel(QWidget):
    """Base class for tool panels with common functionality."""

    tool_clicked = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)

        # Button registry for state-based updates
        self._buttons = {}

        # Application state reference (set by parent)
        self.app_state = None

    def _create_scrollable_layout(self):
        """Create a scrollable layout for long tool lists."""
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)

        scroll.setStyleSheet("""
            QScrollArea {
                border: none;
                background: transparent;
            }
            QScrollBar:vertical {
                border: none;
                background: #f0f0f0;
                width: 10px;
                margin: 0;
            }
            QScrollBar::handle:vertical {
                background: #c0c0c0;
                border-radius: 5px;
                min-height: 20px;
            }
            QScrollBar::handle:vertical:hover {
                background: #a0a0a0;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
        """)

        content = QWidget()
        layout = QVBoxLayout(content)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(4)

        scroll.setWidget(content)

        return scroll, layout

    def _create_button(self, text: str, enabled: bool = True, tooltip: str = "",
                      disabled_reason: str = "", shortcut: str = "", button_id: str = None):
        """Create a sidebar button with enhanced features."""
        btn = SidebarButton(text, enabled=enabled, tooltip=tooltip,
                           disabled_reason=disabled_reason, shortcut=shortcut)

        if enabled:
            btn.clicked.connect(lambda: self._handle_tool_click(text, btn))

        # Register button for state-based updates
        if button_id:
            self._buttons[button_id] = btn

        return btn

    def _handle_tool_click(self, tool_name: str, button: SidebarButton):
        """Handle tool click with visual feedback and error handling."""
        try:
            # Flash highlight
            button.flash_highlight()

            # Emit tool clicked signal
            self.tool_clicked.emit(tool_name)

        except Exception as e:
            print(f"Error executing tool '{tool_name}': {e}")
            # Don't crash - just log the error
            import traceback
            traceback.print_exc()

    def _create_separator(self):
        """Create a horizontal separator."""
        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setFrameShadow(QFrame.Shadow.Sunken)
        line.setStyleSheet("QFrame { color: #ddd; margin: 4px 0; }")
        return line

    def update_tool_availability(self):
        """Update tool button states based on application state. Override in subclasses."""
        pass

    def set_app_state(self, app_state):
        """Set application state reference and update tool availability."""
        self.app_state = app_state
        if app_state:
            # Connect to state changes
            app_state.geometry_changed.connect(self.update_tool_availability)
            app_state.regions_changed.connect(self.update_tool_availability)
            app_state.edit_mode_changed.connect(self.update_tool_availability)
        self.update_tool_availability()


class FileTools(BaseToolPanel):
    """Advanced file management tools."""

    def __init__(self, parent=None):
        super().__init__(parent)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        scroll, layout = self._create_scrollable_layout()
        main_layout.addWidget(scroll)

        # Template management
        layout.addWidget(self._create_button(
            "Save Template",
            tooltip="Save current settings as reusable template",
            shortcut="Ctrl+Shift+S"
        ))
        layout.addWidget(self._create_button(
            "Load Template",
            tooltip="Load saved template settings",
            shortcut="Ctrl+Shift+O"
        ))

        layout.addWidget(self._create_separator())

        # Recent files
        layout.addWidget(self._create_button(
            "Recent Files",
            tooltip="View and open recently used files",
            shortcut="Ctrl+R"
        ))

        layout.addWidget(self._create_separator())

        # Export reports
        layout.addWidget(self._create_button(
            "Export Analysis Report",
            tooltip="Export detailed analysis report to PDF"
        ))
        layout.addWidget(self._create_button(
            "Export Validation Report",
            tooltip="Export validation results and constraint checks"
        ))
        layout.addWidget(self._create_button(
            "Batch Export",
            tooltip="Export multiple formats at once"
        ))

        layout.addWidget(self._create_separator())

        # Disabled features (future)
        layout.addWidget(self._create_button(
            "Auto-save Settings",
            enabled=False,
            disabled_reason="Feature coming soon"
        ))
        layout.addWidget(self._create_button(
            "Version History",
            enabled=False,
            disabled_reason="Feature coming soon"
        ))
        layout.addWidget(self._create_button(
            "Cloud Sync",
            enabled=False,
            disabled_reason="Feature coming soon"
        ))

        layout.addStretch()


class AnalyzeTools(BaseToolPanel):
    """Advanced analysis tools."""

    def __init__(self, parent=None):
        super().__init__(parent)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        scroll, layout = self._create_scrollable_layout()
        main_layout.addWidget(scroll)

        # Comparison tools
        layout.addWidget(self._create_button(
            "Compare Analyses",
            tooltip="Compare results from different mathematical lenses"
        ))
        layout.addWidget(self._create_button(
            "Differential Analysis",
            tooltip="Perform differential geometry analysis"
        ))
        layout.addWidget(self._create_button(
            "Batch Analysis",
            tooltip="Run multiple analysis types at once",
            button_id="batch_analysis"
        ))

        layout.addWidget(self._create_separator())

        # History
        layout.addWidget(self._create_button(
            "Analysis History Timeline",
            tooltip="View timeline of all analysis iterations"
        ))

        layout.addWidget(self._create_separator())

        # Presets
        layout.addWidget(self._create_button(
            "Save Analysis Preset",
            tooltip="Save current lens configuration as preset"
        ))
        layout.addWidget(self._create_button(
            "Load Analysis Preset",
            tooltip="Load saved analysis configuration"
        ))

        layout.addWidget(self._create_separator())

        # Disabled features (future)
        layout.addWidget(self._create_button(
            "Custom Analysis Scripts",
            enabled=False,
            disabled_reason="Feature coming soon - Python scripting API"
        ))
        layout.addWidget(self._create_button(
            "ML-Based Region Suggestion",
            enabled=False,
            disabled_reason="Feature coming soon - AI-powered recommendations"
        ))

        layout.addStretch()

    def update_tool_availability(self):
        """Update tool states based on geometry availability."""
        if not self.app_state:
            return

        has_geometry = self.app_state.get_current_geometry() is not None

        # Batch analysis requires geometry
        if "batch_analysis" in self._buttons:
            btn = self._buttons["batch_analysis"]
            if has_geometry:
                btn.setEnabled(True)
                btn.update_tooltip("Run multiple analysis types at once")
            else:
                btn.setEnabled(False)
                btn.update_tooltip(
                    "Run multiple analysis types at once",
                    disabled_reason="No geometry loaded"
                )


class EditTools(BaseToolPanel):
    """Advanced editing tools with state-aware button enabling."""

    def __init__(self, parent=None):
        super().__init__(parent)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        scroll, layout = self._create_scrollable_layout()
        main_layout.addWidget(scroll)

        # Selection tools
        layout.addWidget(self._create_button(
            "Grow Selection",
            tooltip="Expand selection to adjacent faces",
            shortcut="Ctrl+G",
            button_id="grow_selection"
        ))
        layout.addWidget(self._create_button(
            "Shrink Selection",
            tooltip="Contract selection from edges",
            shortcut="Ctrl+Shift+G",
            button_id="shrink_selection"
        ))

        layout.addWidget(self._create_separator())

        # Boundary editing
        layout.addWidget(self._create_button(
            "Edit Boundary",
            tooltip="Interactively edit region boundary curves",
            button_id="edit_boundary"
        ))
        layout.addWidget(self._create_button(
            "Export Selection to Region",
            tooltip="Create new parametric region from current selection",
            shortcut="Ctrl+E",
            button_id="export_to_region"
        ))

        layout.addWidget(self._create_separator())

        # Region operations
        layout.addWidget(self._create_button(
            "Merge Regions",
            tooltip="Combine selected regions into one",
            shortcut="Ctrl+M",
            button_id="merge_regions"
        ))
        layout.addWidget(self._create_button(
            "Split Regions",
            tooltip="Split selected region into multiple parts",
            button_id="split_regions"
        ))

        layout.addWidget(self._create_separator())

        # Batch operations
        layout.addWidget(self._create_button(
            "Pin All Regions",
            tooltip="Lock all regions from editing",
            button_id="pin_all"
        ))
        layout.addWidget(self._create_button(
            "Unpin All Regions",
            tooltip="Unlock all regions for editing",
            button_id="unpin_all"
        ))
        layout.addWidget(self._create_button(
            "Batch Region Operations",
            tooltip="Apply operations to multiple regions at once"
        ))

        layout.addWidget(self._create_separator())

        # Disabled features (future)
        layout.addWidget(self._create_button(
            "Selection Filters",
            enabled=False,
            disabled_reason="Feature coming soon - Filter by curvature, area, etc."
        ))

        layout.addStretch()

    def update_tool_availability(self):
        """Update tool states based on selection and region state."""
        if not self.app_state:
            return

        # Get current state
        has_selection = False
        num_selected_regions = 0
        has_regions = len(self.app_state.regions) > 0

        if hasattr(self.app_state, 'edit_mode_manager'):
            selection = self.app_state.edit_mode_manager.selection
            has_selection = not selection.is_empty()

        # Count selected regions (would need region selection tracking)
        # For now, assume this is tracked elsewhere
        num_selected_regions = 0  # TODO: Get from state

        # Update "Grow Selection" and "Shrink Selection"
        for btn_id in ["grow_selection", "shrink_selection"]:
            if btn_id in self._buttons:
                btn = self._buttons[btn_id]
                if has_selection:
                    btn.setEnabled(True)
                else:
                    btn.setEnabled(False)
                    btn.update_tooltip(
                        btn.toolTip().split("\n")[0],  # Keep original tooltip
                        disabled_reason="No faces selected"
                    )

        # Update "Export Selection to Region"
        if "export_to_region" in self._buttons:
            btn = self._buttons["export_to_region"]
            if has_selection:
                btn.setEnabled(True)
            else:
                btn.setEnabled(False)
                btn.update_tooltip(
                    "Create new parametric region from current selection",
                    disabled_reason="No faces selected"
                )

        # Update "Edit Boundary"
        if "edit_boundary" in self._buttons:
            btn = self._buttons["edit_boundary"]
            if has_selection:
                btn.setEnabled(True)
            else:
                btn.setEnabled(False)
                btn.update_tooltip(
                    "Interactively edit region boundary curves",
                    disabled_reason="No region selected"
                )

        # Update "Merge Regions" - needs at least 2 regions selected
        if "merge_regions" in self._buttons:
            btn = self._buttons["merge_regions"]
            if num_selected_regions >= 2:
                btn.setEnabled(True)
            else:
                btn.setEnabled(False)
                btn.update_tooltip(
                    "Combine selected regions into one",
                    disabled_reason="Select at least 2 regions to merge"
                )

        # Update "Split Regions"
        if "split_regions" in self._buttons:
            btn = self._buttons["split_regions"]
            if num_selected_regions >= 1:
                btn.setEnabled(True)
            else:
                btn.setEnabled(False)
                btn.update_tooltip(
                    "Split selected region into multiple parts",
                    disabled_reason="Select a region to split"
                )

        # Update "Pin All" and "Unpin All"
        for btn_id in ["pin_all", "unpin_all"]:
            if btn_id in self._buttons:
                btn = self._buttons[btn_id]
                if has_regions:
                    btn.setEnabled(True)
                else:
                    btn.setEnabled(False)
                    btn.update_tooltip(
                        btn.toolTip().split("\n")[0],
                        disabled_reason="No regions exist"
                    )


class ValidateTools(BaseToolPanel):
    """Advanced validation and constraint tools."""

    def __init__(self, parent=None):
        super().__init__(parent)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        scroll, layout = self._create_scrollable_layout()
        main_layout.addWidget(scroll)

        # Quick Fixes section
        layout.addWidget(SectionLabel("QUICK FIXES"))
        layout.addWidget(self._create_button(
            "Fix Undercuts",
            tooltip="Automatically adjust geometry to remove undercuts"
        ))
        layout.addWidget(self._create_button(
            "Adjust Pull Direction",
            tooltip="Change mold pull direction to resolve conflicts"
        ))
        layout.addWidget(self._create_button(
            "Auto-Fix Draft Angles",
            tooltip="Automatically adjust surfaces to meet draft angle requirements"
        ))
        layout.addWidget(self._create_button(
            "Adjust Wall Thickness",
            tooltip="Modify wall thickness to meet minimum requirements"
        ))
        layout.addWidget(self._create_button(
            "Repair Seam Gaps",
            tooltip="Close gaps between mold pieces at seams"
        ))

        layout.addWidget(self._create_separator())

        # Configuration section
        layout.addWidget(SectionLabel("CONFIGURATION"))
        layout.addWidget(self._create_button(
            "Custom Constraint Editor",
            tooltip="Create and edit custom fabrication constraints"
        ))
        layout.addWidget(self._create_button(
            "Tolerance Overrides",
            tooltip="Override default tolerances for specific regions"
        ))
        layout.addWidget(self._create_button(
            "Exemption Manager",
            tooltip="Mark regions as exempt from certain constraints"
        ))

        layout.addWidget(self._create_separator())

        # Disabled features
        layout.addWidget(self._create_button(
            "Validation Profiles",
            enabled=False,
            disabled_reason="Feature coming soon - Save/load validation presets"
        ))

        layout.addStretch()


class FabricateTools(BaseToolPanel):
    """Advanced fabrication and export tools."""

    def __init__(self, parent=None):
        super().__init__(parent)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        scroll, layout = self._create_scrollable_layout()
        main_layout.addWidget(scroll)

        # Custom profiles
        layout.addWidget(self._create_button(
            "Custom Key Profiles",
            tooltip="Design custom key and socket profiles for mold alignment"
        ))
        layout.addWidget(self._create_button(
            "Optimize Seam Placement",
            tooltip="Automatically optimize seam locations for aesthetics"
        ))

        layout.addWidget(self._create_separator())

        # Documentation
        layout.addWidget(self._create_button(
            "Add Part Numbers/Labels",
            tooltip="Label mold pieces with part numbers"
        ))
        layout.addWidget(self._create_button(
            "Generate Assembly Diagram",
            tooltip="Create visual diagram showing mold assembly order"
        ))

        layout.addWidget(self._create_separator())

        # Manufacturing planning
        layout.addWidget(self._create_button(
            "Multi-pour Strategy",
            tooltip="Plan strategy for multi-part molds with staged pours"
        ))
        layout.addWidget(self._create_button(
            "Drying Time Calculator",
            tooltip="Calculate optimal drying times based on thickness"
        ))
        layout.addWidget(self._create_button(
            "Add Witness Marks",
            tooltip="Add alignment marks for mold reassembly"
        ))
        layout.addWidget(self._create_button(
            "Mold Weight Calculator",
            tooltip="Estimate total plaster weight needed"
        ))

        layout.addWidget(self._create_separator())

        # Instructions
        layout.addWidget(self._create_button(
            "Generate Casting Instructions",
            tooltip="Generate step-by-step casting instructions"
        ))

        layout.addWidget(self._create_separator())

        # Export Settings - Expandable with persistence
        self.export_section = ExpandableSection(
            "Export Settings",
            settings_key="fabricate/export_settings"
        )
        self.export_section.clicked.connect(self.tool_clicked.emit)

        # Add section label
        section_label = QLabel("Export Destination")
        section_label.setStyleSheet("color: #666; font-size: 9px; padding-bottom: 4px; border-bottom: 1px solid #ddd;")
        self.export_section.add_widget(section_label)

        # Add export buttons
        self.export_section.add_button("📄 Export G-Code", "Export G-Code")
        self.export_section.add_button("🔄 Push to Rhino", "Push to Rhino")

        # Add info label
        info_label = QLabel("Additional export options will be available here")
        info_label.setWordWrap(True)
        info_label.setStyleSheet("color: #888; font-size: 9px; padding-top: 4px; border-top: 1px solid #ddd;")
        self.export_section.add_widget(info_label)

        layout.addWidget(self.export_section)

        layout.addWidget(self._create_separator())

        # Disabled features
        layout.addWidget(self._create_button(
            "QC Checklist Generator",
            enabled=False,
            disabled_reason="Feature coming soon - Quality control checklist"
        ))
        layout.addWidget(self._create_button(
            "Kiln Schedule Generator",
            enabled=False,
            disabled_reason="Feature coming soon - Firing schedule calculator"
        ))

        layout.addStretch()


class ViewTools(BaseToolPanel):
    """Advanced view and camera tools."""

    def __init__(self, parent=None):
        super().__init__(parent)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        scroll, layout = self._create_scrollable_layout()
        main_layout.addWidget(scroll)

        # Named views
        layout.addWidget(self._create_button(
            "Save Named View",
            tooltip="Save current camera position as named view",
            shortcut="Ctrl+Shift+V"
        ))
        layout.addWidget(self._create_button(
            "Restore Named View",
            tooltip="Restore a previously saved camera position"
        ))

        layout.addWidget(self._create_separator())

        # Lock Camera - Toggle button
        self.lock_camera_btn = QPushButton("Lock Camera")
        self.lock_camera_btn.setCheckable(True)
        self.lock_camera_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.lock_camera_btn.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.lock_camera_btn.setToolTip("Lock camera to prevent accidental movement")

        font = QFont()
        font.setPointSize(10)
        self.lock_camera_btn.setFont(font)

        self.lock_camera_btn.setStyleSheet("""
            QPushButton {
                text-align: left;
                padding: 6px 12px;
                border: none;
                border-radius: 4px;
                background: transparent;
                color: #333;
            }
            QPushButton:hover {
                background: #e0e0e0;
                color: #000;
            }
            QPushButton:checked {
                background: #2196F3;
                color: white;
            }
            QPushButton:checked:hover {
                background: #1976D2;
            }
            QPushButton:focus {
                outline: 2px solid #2196F3;
                outline-offset: -2px;
            }
        """)

        self.lock_camera_btn.toggled.connect(self._on_camera_lock_toggled)
        layout.addWidget(self.lock_camera_btn)

        # Camera Properties - Expandable with persistence
        self.camera_props_section = ExpandableSection(
            "Camera Properties",
            settings_key="view/camera_properties"
        )

        # FOV input
        fov_container = QWidget()
        fov_layout = QVBoxLayout(fov_container)
        fov_layout.setContentsMargins(0, 0, 0, 0)
        fov_layout.setSpacing(4)

        fov_label = QLabel("FOV (Field of View)")
        fov_label.setStyleSheet("color: #666; font-size: 9px;")
        fov_layout.addWidget(fov_label)

        self.fov_input = QSpinBox()
        self.fov_input.setRange(1, 180)
        self.fov_input.setValue(60)
        self.fov_input.setStyleSheet("""
            QSpinBox {
                background: white;
                border: 1px solid #ccc;
                border-radius: 4px;
                padding: 4px;
            }
        """)
        fov_layout.addWidget(self.fov_input)

        self.camera_props_section.add_widget(fov_container)

        # Near Clip input
        near_container = QWidget()
        near_layout = QVBoxLayout(near_container)
        near_layout.setContentsMargins(0, 0, 0, 0)
        near_layout.setSpacing(4)

        near_label = QLabel("Near Clip")
        near_label.setStyleSheet("color: #666; font-size: 9px;")
        near_layout.addWidget(near_label)

        self.near_clip_input = QDoubleSpinBox()
        self.near_clip_input.setRange(0.01, 100)
        self.near_clip_input.setValue(0.1)
        self.near_clip_input.setSingleStep(0.1)
        self.near_clip_input.setStyleSheet("""
            QDoubleSpinBox {
                background: white;
                border: 1px solid #ccc;
                border-radius: 4px;
                padding: 4px;
            }
        """)
        near_layout.addWidget(self.near_clip_input)

        self.camera_props_section.add_widget(near_container)

        # Far Clip input
        far_container = QWidget()
        far_layout = QVBoxLayout(far_container)
        far_layout.setContentsMargins(0, 0, 0, 0)
        far_layout.setSpacing(4)

        far_label = QLabel("Far Clip")
        far_label.setStyleSheet("color: #666; font-size: 9px;")
        far_layout.addWidget(far_label)

        self.far_clip_input = QDoubleSpinBox()
        self.far_clip_input.setRange(1, 10000)
        self.far_clip_input.setValue(1000)
        self.far_clip_input.setSingleStep(10)
        self.far_clip_input.setStyleSheet("""
            QDoubleSpinBox {
                background: white;
                border: 1px solid #ccc;
                border-radius: 4px;
                padding: 4px;
            }
        """)
        far_layout.addWidget(self.far_clip_input)

        self.camera_props_section.add_widget(far_container)

        # Projection dropdown
        proj_container = QWidget()
        proj_layout = QVBoxLayout(proj_container)
        proj_layout.setContentsMargins(0, 0, 0, 0)
        proj_layout.setSpacing(4)

        proj_label = QLabel("Projection")
        proj_label.setStyleSheet("color: #666; font-size: 9px;")
        proj_layout.addWidget(proj_label)

        self.projection_combo = QComboBox()
        self.projection_combo.addItems(["Perspective", "Orthographic"])
        self.projection_combo.setStyleSheet("""
            QComboBox {
                background: white;
                border: 1px solid #ccc;
                border-radius: 4px;
                padding: 4px;
            }
        """)
        proj_layout.addWidget(self.projection_combo)

        self.camera_props_section.add_widget(proj_container)

        # Apply Changes button
        apply_btn = QPushButton("Apply Changes")
        apply_btn.setStyleSheet("""
            QPushButton {
                background: #2196F3;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 6px;
            }
            QPushButton:hover {
                background: #1976D2;
            }
        """)
        apply_btn.clicked.connect(lambda: self.tool_clicked.emit("Apply Camera Changes"))
        self.camera_props_section.add_widget(apply_btn)

        layout.addWidget(self.camera_props_section)

        layout.addWidget(self._create_separator())

        # Layout tools
        layout.addWidget(self._create_button(
            "Reset Panel Layout",
            tooltip="Reset all panels to default layout",
            shortcut="Ctrl+Shift+R"
        ))
        layout.addWidget(self._create_button(
            "Toggle Full Screen",
            tooltip="Toggle full screen viewport mode",
            shortcut="F11"
        ))

        layout.addWidget(self._create_separator())

        # Disabled features
        layout.addWidget(self._create_button(
            "Section Planes",
            enabled=False,
            disabled_reason="Feature coming soon - Cut plane visualization"
        ))
        layout.addWidget(self._create_button(
            "Display Modes",
            enabled=False,
            disabled_reason="Feature coming soon - Wireframe, shaded, X-ray modes"
        ))
        layout.addWidget(self._create_button(
            "Turntable Animation",
            enabled=False,
            disabled_reason="Feature coming soon - Animated rotation for presentation"
        ))

        layout.addStretch()

    def _on_camera_lock_toggled(self, checked: bool):
        """Handle camera lock toggle."""
        if checked:
            self.lock_camera_btn.setText("🔒 Camera Locked")
            self.tool_clicked.emit("Lock Camera")
        else:
            self.lock_camera_btn.setText("Lock Camera")
            self.tool_clicked.emit("Unlock Camera")


class LeftSidebar(QWidget):
    """Main left sidebar container that switches content based on active tab."""

    tool_clicked = pyqtSignal(str)

    def __init__(self, parent=None, app_state=None):
        super().__init__(parent)

        self.app_state = app_state

        self.setMinimumWidth(160)
        self.setMaximumWidth(280)
        self.setFixedWidth(220)

        self.setStyleSheet("""
            LeftSidebar {
                background: #f9f9f9;
                border-right: 1px solid #ddd;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Header
        header = QWidget()
        header.setStyleSheet("""
            QWidget {
                background: #f0f0f0;
                border-bottom: 1px solid #ddd;
            }
        """)

        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(12, 8, 12, 8)
        header_layout.setSpacing(8)

        # Icon placeholder (would use actual icons in production)
        icon_label = QLabel("🔧")
        icon_label.setStyleSheet("font-size: 14px; color: #666;")
        header_layout.addWidget(icon_label)

        # Title
        title_label = QLabel("ADVANCED TOOLS")
        title_font = QFont()
        title_font.setPointSize(9)
        title_font.setCapitalization(QFont.Capitalization.AllUppercase)
        title_label.setFont(title_font)
        title_label.setStyleSheet("color: #666;")
        header_layout.addWidget(title_label, 1)

        layout.addWidget(header)

        # Content area - will be populated with tab-specific tools
        self.content_area = QWidget()
        self.content_layout = QVBoxLayout(self.content_area)
        self.content_layout.setContentsMargins(0, 0, 0, 0)
        self.content_layout.setSpacing(0)

        layout.addWidget(self.content_area, 1)

        # Create all tool panels
        self.file_tools = FileTools()
        self.analyze_tools = AnalyzeTools()
        self.edit_tools = EditTools()
        self.validate_tools = ValidateTools()
        self.fabricate_tools = FabricateTools()
        self.view_tools = ViewTools()

        # Connect app_state to all panels
        if app_state:
            self.set_app_state(app_state)

        # Connect signals
        self.file_tools.tool_clicked.connect(self.tool_clicked.emit)
        self.analyze_tools.tool_clicked.connect(self.tool_clicked.emit)
        self.edit_tools.tool_clicked.connect(self.tool_clicked.emit)
        self.validate_tools.tool_clicked.connect(self.tool_clicked.emit)
        self.fabricate_tools.tool_clicked.connect(self.tool_clicked.emit)
        self.view_tools.tool_clicked.connect(self.tool_clicked.emit)

        # Start with file tools
        self.set_active_tab("file")

    def set_app_state(self, app_state):
        """Set application state for all tool panels."""
        self.app_state = app_state

        # Propagate to all panels
        for panel in [self.file_tools, self.analyze_tools, self.edit_tools,
                      self.validate_tools, self.fabricate_tools, self.view_tools]:
            panel.set_app_state(app_state)

    def set_active_tab(self, tab: str):
        """Switch the displayed tools based on active tab."""
        # Clear current content
        while self.content_layout.count():
            item = self.content_layout.takeAt(0)
            if item.widget():
                item.widget().setParent(None)

        # Add appropriate tool panel
        if tab == "file":
            self.content_layout.addWidget(self.file_tools)
        elif tab == "analyze":
            self.content_layout.addWidget(self.analyze_tools)
        elif tab == "edit":
            self.content_layout.addWidget(self.edit_tools)
        elif tab == "validate":
            self.content_layout.addWidget(self.validate_tools)
        elif tab == "fabricate":
            self.content_layout.addWidget(self.fabricate_tools)
        elif tab == "view":
            self.content_layout.addWidget(self.view_tools)


if __name__ == "__main__":
    """Test the left sidebar components."""
    import sys
    from PyQt6.QtWidgets import QApplication, QMainWindow, QHBoxLayout, QPushButton

    app = QApplication(sys.argv)

    window = QMainWindow()
    window.setWindowTitle("Left Sidebar Test")
    window.resize(900, 700)

    central = QWidget()
    layout = QHBoxLayout(central)

    # Create sidebar
    sidebar = LeftSidebar()
    sidebar.tool_clicked.connect(lambda tool: print(f"Tool clicked: {tool}"))
    layout.addWidget(sidebar)

    # Create tab buttons for testing
    tab_buttons = QWidget()
    tab_layout = QVBoxLayout(tab_buttons)

    for tab in ["file", "analyze", "edit", "validate", "fabricate", "view"]:
        btn = QPushButton(tab.upper())
        btn.clicked.connect(lambda checked, t=tab: sidebar.set_active_tab(t))
        tab_layout.addWidget(btn)

    tab_layout.addStretch()
    layout.addWidget(tab_buttons)

    layout.addStretch()

    window.setCentralWidget(central)
    window.show()

    sys.exit(app.exec())
