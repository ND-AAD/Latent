"""
RightPanel Component

Right-side panel with vertical icon tabs for contextual tools and settings.

Tabs:
- Viewport: Viewport settings and display options
- Regions: Region list and properties
- Constraints: Constraint violations and status
- Selection: Selection info and statistics
- Parameters: Analysis parameters and settings
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QStackedWidget, QSizePolicy, QComboBox, QCheckBox, QLineEdit,
    QScrollArea, QFrame, QProgressBar, QColorDialog, QDoubleSpinBox,
    QTextEdit, QApplication
)
from PyQt6.QtCore import Qt, pyqtSignal, QSize
from PyQt6.QtGui import QFont, QColor
from typing import Optional, List, Dict, Any


class TabButton(QPushButton):
    """Individual icon button for vertical tab bar"""

    def __init__(self, icon_text: str, label: str, parent=None):
        super().__init__(parent)
        self.label = label
        self.icon_text = icon_text
        self._active = False

        self.setText(icon_text)
        self.setToolTip(label)
        self.setFixedSize(48, 48)
        self.setCursor(Qt.CursorShape.PointingHandCursor)

        # Set font size for icon
        font = QFont()
        font.setPointSize(18)
        self.setFont(font)

        self._update_style()

    def set_active(self, active: bool):
        """Set active state"""
        self._active = active
        self._update_style()

    def _update_style(self):
        """Update button styling based on active state"""
        if self._active:
            self.setStyleSheet("""
                QPushButton {
                    background-color: #FAFAFA;
                    color: #2563EB;
                    border: none;
                    border-left: 2px solid #2563EB;
                    border-bottom: 1px solid #E5E5E7;
                }
                QPushButton:hover {
                    background-color: #F5F5F5;
                }
            """)
        else:
            self.setStyleSheet("""
                QPushButton {
                    background-color: #F5F5F5;
                    color: #9CA3AF;
                    border: none;
                    border-left: 2px solid transparent;
                    border-bottom: 1px solid #E5E5E7;
                }
                QPushButton:hover {
                    background-color: #E5E5E7;
                    color: #6B7280;
                }
            """)


class VerticalIconTabBar(QWidget):
    """Vertical strip of icon buttons for tab selection"""

    tab_changed = pyqtSignal(str)  # Emits tab name

    def __init__(self, parent=None):
        super().__init__()
        self.setFixedWidth(48)

        # Tab definitions: (icon, label, tab_id)
        self.tabs = [
            ("\u25A1", "Viewport", "viewport"),      # □ Square
            ("\u2630", "Regions", "regions"),        # ≡ Triple bar
            ("\u26A0", "Constraints", "constraints"),  # ⚠ Warning sign
            ("\u25B6", "Selection", "selection"),    # ▶ Right arrow
            ("\u2699", "Parameters", "parameters"),  # ⚙ Gear
        ]

        self.buttons = {}
        self.active_tab = "viewport"

        self._setup_ui()

    def _setup_ui(self):
        """Setup UI components"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Create tab buttons
        for icon, label, tab_id in self.tabs:
            btn = TabButton(icon, label, self)
            btn.clicked.connect(lambda checked, tid=tab_id: self._on_tab_clicked(tid))
            self.buttons[tab_id] = btn
            layout.addWidget(btn)

        # Set initial active tab
        self.buttons["viewport"].set_active(True)

        # Add stretch at bottom
        layout.addStretch()

        # Styling
        self.setStyleSheet("""
            VerticalIconTabBar {
                background-color: #F5F5F5;
                border-right: 1px solid #E5E5E7;
            }
        """)

    def _on_tab_clicked(self, tab_id: str):
        """Handle tab click"""
        if tab_id == self.active_tab:
            return

        # Update button states
        self.buttons[self.active_tab].set_active(False)
        self.buttons[tab_id].set_active(True)

        self.active_tab = tab_id
        self.tab_changed.emit(tab_id)

    def set_active_tab(self, tab_id: str):
        """Programmatically set active tab"""
        if tab_id in self.buttons and tab_id != self.active_tab:
            self._on_tab_clicked(tab_id)


# Helper Widgets

class PanelSection(QWidget):
    """Reusable section container with title and optional collapse"""

    toggled = pyqtSignal(bool)  # Emitted when collapsed/expanded

    def __init__(self, title: str, collapsible: bool = False,
                 badge: Optional[str] = None, parent=None):
        super().__init__(parent)
        self.title = title
        self.collapsible = collapsible
        self.badge = badge
        self.expanded = True

        self._setup_ui()

    def _setup_ui(self):
        """Setup UI components"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)

        # Header
        header = QWidget()
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(0, 0, 0, 0)
        header_layout.setSpacing(8)

        # Title
        title_label = QLabel(self.title)
        title_label.setStyleSheet("color: #374151; font-size: 12px; font-weight: 500;")
        header_layout.addWidget(title_label)

        # Badge
        if self.badge:
            badge_label = QLabel()
            badge_label.setFixedSize(8, 8)
            badge_colors = {
                'red': '#EF4444',
                'yellow': '#F59E0B',
                'blue': '#3B82F6',
                'green': '#10B981'
            }
            color = badge_colors.get(self.badge, '#6B7280')
            badge_label.setStyleSheet(f"""
                background-color: {color};
                border-radius: 4px;
            """)
            header_layout.addWidget(badge_label)

        header_layout.addStretch()

        # Collapse indicator
        if self.collapsible:
            self.collapse_indicator = QLabel("▼")
            self.collapse_indicator.setStyleSheet("color: #6B7280; font-size: 10px;")
            header_layout.addWidget(self.collapse_indicator)
            header.setCursor(Qt.CursorShape.PointingHandCursor)
            header.mousePressEvent = self._toggle_collapsed

        layout.addWidget(header)

        # Content container
        self.content_widget = QWidget()
        self.content_layout = QVBoxLayout(self.content_widget)
        self.content_layout.setContentsMargins(0, 0, 0, 0)
        self.content_layout.setSpacing(8)
        layout.addWidget(self.content_widget)

        # Bottom border
        layout.addSpacing(4)
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setStyleSheet("background-color: #E5E7EB; max-height: 1px;")
        layout.addWidget(separator)

    def add_widget(self, widget: QWidget):
        """Add widget to content area"""
        self.content_layout.addWidget(widget)

    def _toggle_collapsed(self, event=None):
        """Toggle collapsed state"""
        if not self.collapsible:
            return
        self.expanded = not self.expanded
        self.content_widget.setVisible(self.expanded)
        self.collapse_indicator.setText("▼" if self.expanded else "▶")
        self.toggled.emit(self.expanded)


class PropertyRow(QWidget):
    """Key-value property display"""

    def __init__(self, label: str, value: str, parent=None):
        super().__init__(parent)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)

        label_widget = QLabel(label)
        label_widget.setStyleSheet("color: #6B7280; font-size: 11px;")
        layout.addWidget(label_widget)

        layout.addStretch()

        self.value_widget = QLabel(value)
        self.value_widget.setStyleSheet("color: #111827; font-size: 11px;")
        layout.addWidget(self.value_widget)

    def set_value(self, value: str):
        """Update the value display"""
        self.value_widget.setText(value)


class RegionItem(QWidget):
    """Individual region display item"""

    selected = pyqtSignal(str)  # region_id
    pinned = pyqtSignal(str, bool)  # region_id, pinned
    deleted = pyqtSignal(str)  # region_id
    edit_requested = pyqtSignal(str)  # region_id

    def __init__(self, region_data, parent=None):
        super().__init__(parent)
        # Handle both dict and ParametricRegion objects
        if hasattr(region_data, 'id'):
            # ParametricRegion object
            self.region_id = region_data.id
            self.region_name = getattr(region_data, 'name', None) or region_data.id
            self.unity_type = getattr(region_data, 'unity_principle', 'Unknown') or 'Unknown'
            self.is_pinned = getattr(region_data, 'pinned', False)
            self.color = region_data.metadata.get('color', '#6B7280') if hasattr(region_data, 'metadata') else '#6B7280'
        else:
            # Dictionary
            self.region_id = region_data.get('id', '')
            self.region_name = region_data.get('name', self.region_id)
            self.unity_type = region_data.get('unity_principle', 'Unknown')
            self.is_pinned = region_data.get('pinned', False)
            self.color = region_data.get('color', '#6B7280')
        self._selected = False

        self._setup_ui()

    def _setup_ui(self):
        """Setup UI components"""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(8, 6, 8, 6)
        layout.setSpacing(8)

        # Color indicator
        color_indicator = QLabel()
        color_indicator.setFixedSize(12, 12)
        color_indicator.setStyleSheet(f"""
            background-color: {self.color};
            border-radius: 2px;
        """)
        layout.addWidget(color_indicator)

        # Text content
        text_layout = QVBoxLayout()
        text_layout.setSpacing(2)

        name_label = QLabel(self.region_name)
        name_label.setStyleSheet("color: #111827; font-size: 11px; font-weight: 500;")
        text_layout.addWidget(name_label)

        unity_label = QLabel(self.unity_type)
        unity_label.setStyleSheet("color: #6B7280; font-size: 10px;")
        text_layout.addWidget(unity_label)

        layout.addLayout(text_layout, 1)

        # Action buttons
        # Pin button
        self.pin_btn = QPushButton("📌" if self.is_pinned else "○")
        self.pin_btn.setFixedSize(20, 20)
        self.pin_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                border: none;
                font-size: 12px;
                color: {"#3B82F6" if self.is_pinned else "#9CA3AF"};
            }}
            QPushButton:hover {{
                background-color: #F3F4F6;
                border-radius: 3px;
            }}
        """)
        self.pin_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.pin_btn.clicked.connect(self._on_pin_clicked)
        layout.addWidget(self.pin_btn)

        # Edit button
        edit_btn = QPushButton("✏")
        edit_btn.setFixedSize(20, 20)
        edit_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: none;
                font-size: 11px;
                color: #6B7280;
            }
            QPushButton:hover {
                background-color: #F3F4F6;
                border-radius: 3px;
            }
        """)
        edit_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        edit_btn.clicked.connect(lambda: self.edit_requested.emit(self.region_id))
        layout.addWidget(edit_btn)

        # Delete button
        delete_btn = QPushButton("🗑")
        delete_btn.setFixedSize(20, 20)
        delete_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: none;
                font-size: 11px;
                color: #6B7280;
            }
            QPushButton:hover {
                background-color: #FEE2E2;
                border-radius: 3px;
                color: #DC2626;
            }
        """)
        delete_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        delete_btn.clicked.connect(lambda: self.deleted.emit(self.region_id))
        layout.addWidget(delete_btn)

        # Container styling
        self._update_style()

    def _on_pin_clicked(self):
        """Toggle pin state"""
        self.is_pinned = not self.is_pinned
        self.pin_btn.setText("📌" if self.is_pinned else "○")
        self.pin_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                border: none;
                font-size: 12px;
                color: {"#3B82F6" if self.is_pinned else "#9CA3AF"};
            }}
            QPushButton:hover {{
                background-color: #F3F4F6;
                border-radius: 3px;
            }}
        """)
        print(f"📌 Pin clicked: region={self.region_id}, pinned={self.is_pinned}")
        self.pinned.emit(self.region_id, self.is_pinned)

    def set_selected(self, selected: bool):
        """Set selected state"""
        self._selected = selected
        self._update_style()

    def _update_style(self):
        """Update widget styling based on state"""
        if self._selected:
            self.setStyleSheet("""
                RegionItem {
                    background-color: #EFF6FF;
                    border: 1px solid #3B82F6;
                    border-radius: 4px;
                }
            """)
        else:
            self.setStyleSheet("""
                RegionItem {
                    background-color: white;
                    border: 1px solid #E5E7EB;
                    border-radius: 4px;
                }
                RegionItem:hover {
                    background-color: #F9FAFB;
                    border-color: #D1D5DB;
                }
            """)

    def mousePressEvent(self, event):
        """Handle click to select"""
        self.selected.emit(self.region_id)
        super().mousePressEvent(event)


# Main Panel Implementations

class ViewportPanel(QWidget):
    """Viewport settings panel"""

    layout_changed = pyqtSignal(str)  # layout name
    shading_changed = pyqtSignal(str)  # shading mode
    edge_display_changed = pyqtSignal(bool)  # edge display
    grid_changed = pyqtSignal(bool)  # grid display
    grid_snap_changed = pyqtSignal(bool)  # grid snap
    material_preview_changed = pyqtSignal(bool)  # material preview
    camera_sync_changed = pyqtSignal(bool)  # camera sync
    background_color_changed = pyqtSignal(QColor)  # background color

    def __init__(self, parent=None):
        super().__init__(parent)
        self.bg_color = QColor("#1A1A1A")
        self._setup_ui()

    def _setup_ui(self):
        """Setup UI components"""
        # Scrollable container
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setStyleSheet("QScrollArea { background-color: #FAFAFA; border: none; }")

        content = QWidget()
        layout = QVBoxLayout(content)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(0)

        # Layout section
        layout_section = PanelSection("Layout")
        layout_combo = QComboBox()
        layout_combo.addItems([
            "Single Viewport",
            "Two Horizontal",
            "Two Vertical",
            "Four Grid"
        ])
        layout_combo.setStyleSheet("""
            QComboBox {
                background-color: white;
                border: 1px solid #D1D5DB;
                border-radius: 4px;
                padding: 4px 8px;
                font-size: 11px;
                color: #374151;
            }
            QComboBox:hover {
                border-color: #9CA3AF;
            }
            QComboBox::drop-down {
                border: none;
            }
        """)
        layout_combo.currentTextChanged.connect(self.layout_changed.emit)
        layout_section.add_widget(layout_combo)
        layout.addWidget(layout_section)

        # Shading Mode section
        shading_section = PanelSection("Shading Mode")
        self.shading_combo = QComboBox()
        self.shading_combo.addItems(["Wireframe", "Shaded", "Rendered"])
        self.shading_combo.setStyleSheet(layout_combo.styleSheet())
        self.shading_combo.currentTextChanged.connect(self.shading_changed.emit)
        shading_section.add_widget(self.shading_combo)
        layout.addWidget(shading_section)

        # Display Options section
        display_section = PanelSection("Display Options")

        self.edge_check = QCheckBox("Edge Display")
        self.edge_check.setStyleSheet("QCheckBox { color: #374151; font-size: 11px; }")
        self.edge_check.stateChanged.connect(lambda state: self.edge_display_changed.emit(state == Qt.CheckState.Checked))
        display_section.add_widget(self.edge_check)

        self.grid_check = QCheckBox("Show Grid")
        self.grid_check.setChecked(True)
        self.grid_check.setStyleSheet("QCheckBox { color: #374151; font-size: 11px; }")
        self.grid_check.stateChanged.connect(lambda state: self.grid_changed.emit(state == Qt.CheckState.Checked))
        display_section.add_widget(self.grid_check)

        self.snap_check = QCheckBox("Grid Snap")
        self.snap_check.setStyleSheet("QCheckBox { color: #374151; font-size: 11px; }")
        self.snap_check.stateChanged.connect(lambda state: self.grid_snap_changed.emit(state == Qt.CheckState.Checked))
        display_section.add_widget(self.snap_check)

        self.material_check = QCheckBox("Material Preview")
        self.material_check.setStyleSheet("QCheckBox { color: #374151; font-size: 11px; }")
        self.material_check.stateChanged.connect(lambda state: self.material_preview_changed.emit(state == Qt.CheckState.Checked))
        display_section.add_widget(self.material_check)

        layout.addWidget(display_section)

        # Camera section
        camera_section = PanelSection("Camera")
        self.sync_check = QCheckBox("Sync All Cameras")
        self.sync_check.setChecked(True)
        self.sync_check.setStyleSheet("QCheckBox { color: #374151; font-size: 11px; }")
        self.sync_check.stateChanged.connect(lambda state: self.camera_sync_changed.emit(state == Qt.CheckState.Checked))
        camera_section.add_widget(self.sync_check)
        layout.addWidget(camera_section)

        # Background section
        bg_section = PanelSection("Background")
        bg_container = QWidget()
        bg_layout = QHBoxLayout(bg_container)
        bg_layout.setContentsMargins(0, 0, 0, 0)
        bg_layout.setSpacing(8)

        self.color_preview = QPushButton()
        self.color_preview.setFixedSize(32, 24)
        self.color_preview.setStyleSheet(f"""
            QPushButton {{
                background-color: {self.bg_color.name()};
                border: 1px solid #D1D5DB;
                border-radius: 4px;
            }}
            QPushButton:hover {{
                border-color: #9CA3AF;
            }}
        """)
        self.color_preview.setCursor(Qt.CursorShape.PointingHandCursor)
        self.color_preview.clicked.connect(self._choose_color)
        bg_layout.addWidget(self.color_preview)

        color_label = QLabel("Color")
        color_label.setStyleSheet("color: #6B7280; font-size: 11px;")
        bg_layout.addWidget(color_label)
        bg_layout.addStretch()

        bg_section.add_widget(bg_container)
        layout.addWidget(bg_section)

        layout.addStretch()

        scroll.setWidget(content)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(scroll)

    def _choose_color(self):
        """Open color picker dialog"""
        color = QColorDialog.getColor(self.bg_color, self, "Choose Background Color")
        if color.isValid():
            self.bg_color = color
            self.color_preview.setStyleSheet(f"""
                QPushButton {{
                    background-color: {self.bg_color.name()};
                    border: 1px solid #D1D5DB;
                    border-radius: 4px;
                }}
                QPushButton:hover {{
                    border-color: #9CA3AF;
                }}
            """)
            # Emit signal for background color change
            self.background_color_changed.emit(self.bg_color)


class RegionsPanel(QWidget):
    """Regions list panel"""

    region_selected = pyqtSignal(str)  # region_id
    region_pinned = pyqtSignal(str, bool)  # region_id, pinned
    region_deleted = pyqtSignal(str)  # region_id

    def __init__(self, parent=None):
        super().__init__(parent)
        self.regions: List[Dict[str, Any]] = []
        self.selected_region_id: Optional[str] = None
        self.region_items: Dict[str, RegionItem] = {}
        self._setup_ui()

    def _setup_ui(self):
        """Setup UI components"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        # Header with count
        self.count_label = QLabel("Regions: 0 (0 pinned)")
        self.count_label.setStyleSheet("color: #6B7280; font-size: 11px;")
        layout.addWidget(self.count_label)

        # Search box
        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText("Search regions...")
        self.search_box.setStyleSheet("""
            QLineEdit {
                background-color: white;
                border: 1px solid #D1D5DB;
                border-radius: 4px;
                padding: 6px 8px;
                font-size: 11px;
                color: #374151;
            }
            QLineEdit:focus {
                border-color: #3B82F6;
                outline: none;
            }
        """)
        self.search_box.textChanged.connect(self._filter_regions)
        layout.addWidget(self.search_box)

        # Sort dropdown
        self.sort_combo = QComboBox()
        self.sort_combo.addItems([
            "Sort by Name",
            "Sort by Unity",
            "Pinned First"
        ])
        self.sort_combo.setStyleSheet("""
            QComboBox {
                background-color: white;
                border: 1px solid #D1D5DB;
                border-radius: 4px;
                padding: 4px 8px;
                font-size: 11px;
                color: #374151;
            }
        """)
        self.sort_combo.currentTextChanged.connect(self._sort_regions)
        layout.addWidget(self.sort_combo)

        # Scrollable region list
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setStyleSheet("QScrollArea { background-color: transparent; border: none; }")

        self.region_list_widget = QWidget()
        self.region_list_layout = QVBoxLayout(self.region_list_widget)
        self.region_list_layout.setContentsMargins(0, 0, 0, 0)
        self.region_list_layout.setSpacing(8)
        self.region_list_layout.addStretch()

        scroll.setWidget(self.region_list_widget)
        layout.addWidget(scroll, 1)

        # Selected Region Properties (collapsible)
        self.properties_section = PanelSection("Selected Region Properties", collapsible=True)
        self.properties_section.expanded = False
        self.properties_section.content_widget.setVisible(False)

        self.name_row = PropertyRow("Name", "")
        self.properties_section.add_widget(self.name_row)

        self.unity_row = PropertyRow("Unity Principle", "")
        self.properties_section.add_widget(self.unity_row)

        self.face_count_row = PropertyRow("Face Count", "0")
        self.properties_section.add_widget(self.face_count_row)

        # Unity strength progress bar
        strength_container = QWidget()
        strength_layout = QVBoxLayout(strength_container)
        strength_layout.setContentsMargins(0, 8, 0, 0)
        strength_layout.setSpacing(4)

        strength_label = QLabel("Unity Strength")
        strength_label.setStyleSheet("color: #6B7280; font-size: 11px;")
        strength_layout.addWidget(strength_label)

        self.strength_bar = QProgressBar()
        self.strength_bar.setRange(0, 100)
        self.strength_bar.setValue(0)
        self.strength_bar.setTextVisible(False)
        self.strength_bar.setFixedHeight(8)
        self.strength_bar.setStyleSheet("""
            QProgressBar {
                background-color: #E5E7EB;
                border-radius: 4px;
                border: none;
            }
            QProgressBar::chunk {
                background-color: #10B981;
                border-radius: 4px;
            }
        """)
        strength_layout.addWidget(self.strength_bar)

        self.strength_value = QLabel("0.00")
        self.strength_value.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.strength_value.setStyleSheet("color: #6B7280; font-size: 11px;")
        strength_layout.addWidget(self.strength_value)

        self.properties_section.add_widget(strength_container)
        layout.addWidget(self.properties_section)

    def set_regions(self, regions: List[Dict[str, Any]]):
        """Update the regions list"""
        self.regions = regions
        self._rebuild_region_list()
        self._update_count()

    def _rebuild_region_list(self):
        """Rebuild the region item list"""
        # Clear existing items
        while self.region_list_layout.count() > 1:  # Keep stretch
            item = self.region_list_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        self.region_items.clear()

        # Add region items
        for region in self.regions:
            item = RegionItem(region)
            item.selected.connect(self._on_region_selected)
            item.pinned.connect(self.region_pinned.emit)
            item.deleted.connect(self.region_deleted.emit)

            # Get region ID (handle both dict and ParametricRegion)
            region_id = region.id if hasattr(region, 'id') else region.get('id', '')
            self.region_items[region_id] = item
            self.region_list_layout.insertWidget(
                self.region_list_layout.count() - 1, item
            )

    def _update_count(self):
        """Update the region count label"""
        total = len(self.regions)
        # Handle both dict and ParametricRegion
        pinned = sum(1 for r in self.regions if (r.pinned if hasattr(r, 'pinned') else r.get('pinned', False)))
        self.count_label.setText(f"Regions: {total} ({pinned} pinned)")

    def _filter_regions(self, text: str):
        """Filter regions by search text"""
        text = text.lower()
        for region_id, item in self.region_items.items():
            matches = (text in item.region_name.lower() or
                      text in item.unity_type.lower())
            item.setVisible(matches)

    def _sort_regions(self, sort_type: str):
        """Sort regions by selected criteria"""
        # Helper to get attribute from dict or ParametricRegion
        def get_attr(r, attr, default=''):
            if hasattr(r, attr):
                return getattr(r, attr) or default
            return r.get(attr, default)

        def get_id(r):
            return r.id if hasattr(r, 'id') else r.get('id', '')

        if sort_type == "Sort by Name":
            self.regions.sort(key=lambda r: get_attr(r, 'name', get_id(r)))
        elif sort_type == "Sort by Unity":
            self.regions.sort(key=lambda r: get_attr(r, 'unity_principle', ''))
        elif sort_type == "Pinned First":
            self.regions.sort(key=lambda r: (not get_attr(r, 'pinned', False), get_attr(r, 'name', get_id(r))))

        self._rebuild_region_list()

    def _on_region_selected(self, region_id: str):
        """Handle region selection"""
        # Update visual selection
        if self.selected_region_id in self.region_items:
            self.region_items[self.selected_region_id].set_selected(False)

        self.selected_region_id = region_id
        if region_id in self.region_items:
            self.region_items[region_id].set_selected(True)

        # Update properties panel
        region = next((r for r in self.regions if r['id'] == region_id), None)
        if region:
            self._update_properties(region)
            if not self.properties_section.expanded:
                self.properties_section._toggle_collapsed()

        self.region_selected.emit(region_id)

    def _update_properties(self, region: Dict[str, Any]):
        """Update the properties panel with region data"""
        # Update property rows using the set_value method
        self.name_row.set_value(region.get('name', region['id']))
        self.unity_row.set_value(region.get('unity_principle', 'Unknown'))
        self.face_count_row.set_value(str(len(region.get('faces', []))))

        # Update strength bar
        strength = region.get('unity_strength', 0.0)
        self.strength_bar.setValue(int(strength * 100))
        self.strength_value.setText(f"{strength:.2f}")


class ConstraintItem(QWidget):
    """Individual constraint display item"""

    quick_fix_clicked = pyqtSignal(str)  # constraint_id
    constraint_selected = pyqtSignal(str)  # constraint_id

    def __init__(self, constraint_data: Dict[str, Any], parent=None):
        super().__init__(parent)
        self.constraint_id = constraint_data.get('id', '')
        self.title = constraint_data.get('title', 'Unknown')
        self.description = constraint_data.get('description', '')
        self.severity = constraint_data.get('severity', 0.0)
        self.constraint_type = constraint_data.get('type', 'warning')  # 'error' or 'warning'

        self._setup_ui()

    def _setup_ui(self):
        """Setup UI components"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(6)

        # Title
        title_label = QLabel(self.title)
        title_label.setStyleSheet("color: #111827; font-size: 11px; font-weight: bold;")
        title_label.setWordWrap(True)
        layout.addWidget(title_label)

        # Description
        desc_label = QLabel(self.description)
        desc_label.setStyleSheet("color: #6B7280; font-size: 10px;")
        desc_label.setWordWrap(True)
        layout.addWidget(desc_label)

        # Bottom row: severity and quick fix button
        bottom_row = QWidget()
        bottom_layout = QHBoxLayout(bottom_row)
        bottom_layout.setContentsMargins(0, 0, 0, 0)
        bottom_layout.setSpacing(8)

        # Severity display
        severity_container = QWidget()
        severity_layout = QHBoxLayout(severity_container)
        severity_layout.setContentsMargins(0, 0, 0, 0)
        severity_layout.setSpacing(4)

        severity_label = QLabel("Severity:")
        severity_label.setStyleSheet("color: #6B7280; font-size: 10px;")
        severity_layout.addWidget(severity_label)

        # Color-coded severity value
        severity_color = '#EF4444' if self.constraint_type == 'error' else '#F59E0B'
        severity_value = QLabel(f"{self.severity:.2f}")
        severity_value.setStyleSheet(f"color: {severity_color}; font-size: 10px; font-weight: 500;")
        severity_layout.addWidget(severity_value)

        bottom_layout.addWidget(severity_container)
        bottom_layout.addStretch()

        # Quick Fix button
        self.quick_fix_btn = QPushButton("Quick Fix")
        self.quick_fix_btn.setFixedHeight(24)
        self.quick_fix_btn.setStyleSheet("""
            QPushButton {
                background-color: #3B82F6;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 4px 12px;
                font-size: 10px;
                font-weight: 500;
            }
            QPushButton:hover {
                background-color: #2563EB;
            }
            QPushButton:pressed {
                background-color: #1D4ED8;
            }
        """)
        self.quick_fix_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.quick_fix_btn.clicked.connect(lambda: self.quick_fix_clicked.emit(self.constraint_id))
        bottom_layout.addWidget(self.quick_fix_btn)

        layout.addWidget(bottom_row)

        # Container styling
        self.setStyleSheet("""
            ConstraintItem {
                background-color: white;
                border: 1px solid #E5E7EB;
                border-radius: 4px;
            }
            ConstraintItem:hover {
                background-color: #F9FAFB;
                border-color: #D1D5DB;
            }
        """)
        self.setCursor(Qt.CursorShape.PointingHandCursor)

    def mousePressEvent(self, event):
        """Handle click to select constraint"""
        self.constraint_selected.emit(self.constraint_id)
        super().mousePressEvent(event)


class CollapsibleConstraintSection(QWidget):
    """Collapsible section for constraint groups with badge indicator"""

    toggled = pyqtSignal(bool)  # Emitted when collapsed/expanded

    def __init__(self, title: str, badge_color: str = "gray",
                 default_expanded: bool = False, parent=None):
        super().__init__(parent)
        self.title = title
        self.badge_color = badge_color
        self.expanded = default_expanded
        self.constraint_items: List[ConstraintItem] = []

        self._setup_ui()

    def _setup_ui(self):
        """Setup UI components"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 8)
        layout.setSpacing(4)

        # Header
        self.header = QWidget()
        header_layout = QHBoxLayout(self.header)
        header_layout.setContentsMargins(0, 0, 0, 0)
        header_layout.setSpacing(8)

        # Collapse indicator
        self.collapse_indicator = QLabel("▼" if self.expanded else "▶")
        self.collapse_indicator.setStyleSheet("color: #6B7280; font-size: 10px;")
        header_layout.addWidget(self.collapse_indicator)

        # Title
        title_label = QLabel(self.title.split('(')[0].strip())
        title_label.setStyleSheet("color: #374151; font-size: 12px; font-weight: 500;")
        header_layout.addWidget(title_label)

        # Badge with count
        self.badge_label = QLabel()
        self.badge_label.setFixedHeight(20)
        badge_colors = {
            'red': ('#EF4444', '#FFFFFF'),
            'yellow': ('#F59E0B', '#FFFFFF'),
            'blue': ('#3B82F6', '#FFFFFF'),
            'green': ('#10B981', '#FFFFFF'),
            'gray': ('#6B7280', '#FFFFFF')
        }
        bg_color, text_color = badge_colors.get(self.badge_color, badge_colors['gray'])
        self.badge_label.setStyleSheet(f"""
            background-color: {bg_color};
            color: {text_color};
            border-radius: 10px;
            padding: 2px 8px;
            font-size: 10px;
            font-weight: 500;
        """)
        self._update_badge(0)
        header_layout.addWidget(self.badge_label)

        header_layout.addStretch()

        self.header.setCursor(Qt.CursorShape.PointingHandCursor)
        self.header.mousePressEvent = self._toggle_collapsed
        layout.addWidget(self.header)

        # Content container
        self.content_widget = QWidget()
        self.content_layout = QVBoxLayout(self.content_widget)
        self.content_layout.setContentsMargins(0, 0, 0, 0)
        self.content_layout.setSpacing(8)
        self.content_widget.setVisible(self.expanded)
        layout.addWidget(self.content_widget)

    def _update_badge(self, count: int):
        """Update badge with count"""
        self.badge_label.setText(str(count))
        self.badge_label.setVisible(count > 0)

    def _toggle_collapsed(self, event=None):
        """Toggle collapsed state"""
        self.expanded = not self.expanded
        self.content_widget.setVisible(self.expanded)
        self.collapse_indicator.setText("▼" if self.expanded else "▶")
        self.toggled.emit(self.expanded)

    def set_constraints(self, constraints: List[Dict[str, Any]]):
        """Set constraint items in this section"""
        # Clear existing items
        while self.content_layout.count():
            item = self.content_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        self.constraint_items.clear()

        # Add constraint items or empty state
        if constraints:
            for constraint in constraints:
                item = ConstraintItem(constraint)
                self.constraint_items.append(item)
                self.content_layout.addWidget(item)
        else:
            # Empty state
            empty_label = QLabel("No manual edits or overrides")
            empty_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            empty_label.setStyleSheet("color: #9CA3AF; font-size: 10px; padding: 16px;")
            self.content_layout.addWidget(empty_label)

        # Update badge count
        self._update_badge(len(constraints))

    def get_constraint_items(self) -> List[ConstraintItem]:
        """Get all constraint items"""
        return self.constraint_items


class ConstraintsPanel(QWidget):
    """Constraints status panel"""

    quick_fix_clicked = pyqtSignal(str)  # constraint_id
    constraint_selected = pyqtSignal(str)  # constraint_id

    def __init__(self, parent=None):
        super().__init__(parent)
        self.constraints: List[Dict[str, Any]] = []
        self._setup_ui()

    def _setup_ui(self):
        """Setup UI components"""
        # Scrollable container
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setStyleSheet("QScrollArea { background-color: #FAFAFA; border: none; }")

        content = QWidget()
        layout = QVBoxLayout(content)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(16)

        # Overall Status Card
        status_card = QWidget()
        status_card.setStyleSheet("""
            QWidget {
                background-color: #F3F4F6;
                border-radius: 6px;
            }
        """)
        status_layout = QVBoxLayout(status_card)
        status_layout.setContentsMargins(12, 12, 12, 12)
        status_layout.setSpacing(6)

        status_title = QLabel("Overall Status")
        status_title.setStyleSheet("color: #6B7280; font-size: 10px;")
        status_layout.addWidget(status_title)

        status_row = QWidget()
        status_row_layout = QHBoxLayout(status_row)
        status_row_layout.setContentsMargins(0, 0, 0, 0)
        status_row_layout.setSpacing(8)

        # Status indicator dot
        self.status_dot = QLabel()
        self.status_dot.setFixedSize(12, 12)
        self.status_dot.setStyleSheet("""
            background-color: #10B981;
            border-radius: 6px;
        """)
        status_row_layout.addWidget(self.status_dot)

        # Status text
        self.status_text = QLabel("All Clear")
        self.status_text.setStyleSheet("color: #111827; font-size: 12px; font-weight: 500;")
        status_row_layout.addWidget(self.status_text)
        status_row_layout.addStretch()

        status_layout.addWidget(status_row)
        layout.addWidget(status_card)

        # Errors Section
        self.errors_section = CollapsibleConstraintSection(
            "Errors", badge_color="red", default_expanded=False
        )
        self.errors_section.toggled.connect(lambda expanded: None)
        layout.addWidget(self.errors_section)

        # Warnings Section
        self.warnings_section = CollapsibleConstraintSection(
            "Warnings", badge_color="yellow", default_expanded=False
        )
        self.warnings_section.toggled.connect(lambda expanded: None)
        layout.addWidget(self.warnings_section)

        # Features Section
        self.features_section = CollapsibleConstraintSection(
            "Features", badge_color="blue", default_expanded=False
        )
        self.features_section.toggled.connect(lambda expanded: None)
        layout.addWidget(self.features_section)

        layout.addStretch()

        scroll.setWidget(content)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(scroll)

    def set_constraints(self, constraints: List[Dict[str, Any]]):
        """Update constraints list and display"""
        self.constraints = constraints

        # Group constraints by type
        errors = [c for c in constraints if c.get('type') == 'error']
        warnings = [c for c in constraints if c.get('type') == 'warning']
        features = [c for c in constraints if c.get('type') == 'feature']

        # Update sections
        self.errors_section.set_constraints(errors)
        self.warnings_section.set_constraints(warnings)
        self.features_section.set_constraints(features)

        # Connect signals from constraint items
        for section in [self.errors_section, self.warnings_section, self.features_section]:
            for item in section.get_constraint_items():
                item.quick_fix_clicked.connect(self.quick_fix_clicked.emit)
                item.constraint_selected.connect(self.constraint_selected.emit)

        # Auto-expand errors if present
        if errors:
            self.errors_section.expanded = True
            self.errors_section.content_widget.setVisible(True)
            self.errors_section.collapse_indicator.setText("▼")

        # Update overall status
        self._update_overall_status(len(errors), len(warnings))

    def _update_overall_status(self, error_count: int, warning_count: int):
        """Update the overall status card"""
        if error_count > 0:
            # Red for errors
            self.status_dot.setStyleSheet("""
                background-color: #EF4444;
                border-radius: 6px;
            """)
            self.status_text.setText(f"{error_count} Error{'s' if error_count != 1 else ''}, {warning_count} Warning{'s' if warning_count != 1 else ''}")
        elif warning_count > 0:
            # Yellow for warnings only
            self.status_dot.setStyleSheet("""
                background-color: #F59E0B;
                border-radius: 6px;
            """)
            self.status_text.setText(f"{warning_count} Warning{'s' if warning_count != 1 else ''}")
        else:
            # Green for all clear
            self.status_dot.setStyleSheet("""
                background-color: #10B981;
                border-radius: 6px;
            """)
            self.status_text.setText("All Clear")


class SelectionPanel(QWidget):
    """Selection info panel"""

    copy_indices_clicked = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_mode = "Solid Mode"
        self.selection_data = {
            'faces': 0,
            'edges': 0,
            'vertices': 0,
            'total_area': 0.0,
            'bounding_box': (0, 0, 0),
            'indices': []
        }
        self._setup_ui()

    def _setup_ui(self):
        """Setup UI components"""
        # Scrollable container
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setStyleSheet("QScrollArea { background-color: #FAFAFA; border: none; }")

        content = QWidget()
        layout = QVBoxLayout(content)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(0)

        # Current Mode section
        mode_section = PanelSection("Current Mode")
        mode_container = QWidget()
        mode_layout = QHBoxLayout(mode_container)
        mode_layout.setContentsMargins(0, 0, 0, 0)
        mode_layout.setSpacing(8)

        self.mode_badge = QLabel(self.current_mode)
        self.mode_badge.setStyleSheet("""
            QLabel {
                background-color: #2563EB;
                color: white;
                font-size: 11px;
                padding: 4px 12px;
                border-radius: 10px;
            }
        """)
        mode_layout.addWidget(self.mode_badge)
        mode_layout.addStretch()

        mode_section.add_widget(mode_container)
        layout.addWidget(mode_section)

        # Selection Count section
        count_section = PanelSection("Selection Count")
        self.faces_row = PropertyRow("Faces", "0")
        count_section.add_widget(self.faces_row)

        self.edges_row = PropertyRow("Edges", "0")
        count_section.add_widget(self.edges_row)

        self.vertices_row = PropertyRow("Vertices", "0")
        count_section.add_widget(self.vertices_row)

        layout.addWidget(count_section)

        # Statistics section
        stats_section = PanelSection("Statistics")
        self.area_row = PropertyRow("Total Area", "0.0 mm²")
        stats_section.add_widget(self.area_row)

        self.bbox_row = PropertyRow("Bounding Box", "0×0×0 mm")
        stats_section.add_widget(self.bbox_row)

        layout.addWidget(stats_section)

        # Selected Indices section (collapsible)
        indices_section = PanelSection("Selected Indices", collapsible=True)

        # Monospace text display
        self.indices_display = QTextEdit()
        self.indices_display.setReadOnly(True)
        self.indices_display.setMaximumHeight(96)
        self.indices_display.setStyleSheet("""
            QTextEdit {
                background-color: #F3F4F6;
                color: #374151;
                border: 1px solid #D1D5DB;
                border-radius: 4px;
                padding: 8px;
                font-family: monospace;
                font-size: 11px;
            }
        """)
        self.indices_display.setPlainText("[]")
        indices_section.add_widget(self.indices_display)

        # Copy button
        copy_btn = QPushButton("Copy Indices")
        copy_btn.setStyleSheet("""
            QPushButton {
                background-color: white;
                border: 1px solid #D1D5DB;
                border-radius: 4px;
                padding: 6px 12px;
                font-size: 11px;
                color: #374151;
            }
            QPushButton:hover {
                background-color: #F9FAFB;
                border-color: #9CA3AF;
            }
            QPushButton:pressed {
                background-color: #F3F4F6;
            }
        """)
        copy_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        copy_btn.clicked.connect(self.copy_indices_to_clipboard)
        copy_btn.clicked.connect(self.copy_indices_clicked.emit)  # Also emit signal for logging
        indices_section.add_widget(copy_btn)

        layout.addWidget(indices_section)

        layout.addStretch()

        scroll.setWidget(content)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(scroll)

    def set_edit_mode(self, mode: str):
        """Set the current edit mode"""
        self.current_mode = mode
        self.mode_badge.setText(mode)

    def update_selection(self, selection_data: Dict[str, Any]):
        """Update selection display with new data"""
        self.selection_data = selection_data

        # Update counts
        self.faces_row.set_value(str(selection_data.get('faces', 0)))
        self.edges_row.set_value(str(selection_data.get('edges', 0)))
        self.vertices_row.set_value(str(selection_data.get('vertices', 0)))

        # Update statistics
        area = selection_data.get('total_area', 0.0)
        self.area_row.set_value(f"{area:.1f} mm²")

        bbox = selection_data.get('bounding_box', (0, 0, 0))
        self.bbox_row.set_value(f"{bbox[0]:.0f}×{bbox[1]:.0f}×{bbox[2]:.0f} mm")

        # Update indices
        indices = selection_data.get('indices', [])
        indices_str = str(indices) if indices else "[]"
        self.indices_display.setPlainText(indices_str)

    def copy_indices_to_clipboard(self):
        """Copy indices to system clipboard"""
        indices = self.selection_data.get('indices', [])
        indices_str = str(indices)
        QApplication.clipboard().setText(indices_str)


class ParametersPanel(QWidget):
    """Analysis parameters panel"""

    parameters_changed = pyqtSignal(dict)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.settings = {
            'resolution': 'Medium',
            'min_region_size': 'Small',
            'colormap': 'Viridis',
            'auto_range': True,
            'min_value': 0.0,
            'max_value': 1.0
        }
        self._setup_ui()

    def _setup_ui(self):
        """Setup UI components"""
        # Scrollable container
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setStyleSheet("QScrollArea { background-color: #FAFAFA; border: none; }")

        content = QWidget()
        layout = QVBoxLayout(content)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(0)

        # Analysis Settings section
        settings_section = PanelSection("Analysis Settings")

        # Resolution dropdown
        resolution_container = QWidget()
        resolution_layout = QVBoxLayout(resolution_container)
        resolution_layout.setContentsMargins(0, 0, 0, 0)
        resolution_layout.setSpacing(4)

        resolution_label = QLabel("Resolution")
        resolution_label.setStyleSheet("color: #6B7280; font-size: 11px;")
        resolution_layout.addWidget(resolution_label)

        self.resolution_combo = QComboBox()
        self.resolution_combo.addItems(["Low", "Medium", "High", "Ultra"])
        self.resolution_combo.setCurrentText("Medium")
        self.resolution_combo.setStyleSheet("""
            QComboBox {
                background-color: white;
                border: 1px solid #D1D5DB;
                border-radius: 4px;
                padding: 4px 8px;
                font-size: 11px;
                color: #374151;
            }
            QComboBox:hover {
                border-color: #9CA3AF;
            }
            QComboBox::drop-down {
                border: none;
            }
        """)
        self.resolution_combo.currentTextChanged.connect(self._on_parameter_changed)
        resolution_layout.addWidget(self.resolution_combo)

        settings_section.add_widget(resolution_container)

        # Min Region Size dropdown
        region_size_container = QWidget()
        region_size_layout = QVBoxLayout(region_size_container)
        region_size_layout.setContentsMargins(0, 0, 0, 0)
        region_size_layout.setSpacing(4)

        region_size_label = QLabel("Min Region Size")
        region_size_label.setStyleSheet("color: #6B7280; font-size: 11px;")
        region_size_layout.addWidget(region_size_label)

        self.region_size_combo = QComboBox()
        self.region_size_combo.addItems(["Tiny", "Small", "Medium", "Large"])
        self.region_size_combo.setCurrentText("Small")
        self.region_size_combo.setStyleSheet(self.resolution_combo.styleSheet())
        self.region_size_combo.currentTextChanged.connect(self._on_parameter_changed)
        region_size_layout.addWidget(self.region_size_combo)

        settings_section.add_widget(region_size_container)

        # Colormap dropdown
        colormap_container = QWidget()
        colormap_layout = QVBoxLayout(colormap_container)
        colormap_layout.setContentsMargins(0, 0, 0, 0)
        colormap_layout.setSpacing(4)

        colormap_label = QLabel("Colormap")
        colormap_label.setStyleSheet("color: #6B7280; font-size: 11px;")
        colormap_layout.addWidget(colormap_label)

        self.colormap_combo = QComboBox()
        self.colormap_combo.addItems(["Viridis", "Plasma", "Jet", "Rainbow"])
        self.colormap_combo.setCurrentText("Viridis")
        self.colormap_combo.setStyleSheet(self.resolution_combo.styleSheet())
        self.colormap_combo.currentTextChanged.connect(self._on_parameter_changed)
        colormap_layout.addWidget(self.colormap_combo)

        settings_section.add_widget(colormap_container)

        # Auto-range checkbox
        self.auto_range_check = QCheckBox("Auto-range")
        self.auto_range_check.setChecked(True)
        self.auto_range_check.setStyleSheet("QCheckBox { color: #374151; font-size: 11px; }")
        self.auto_range_check.stateChanged.connect(self._on_auto_range_changed)
        settings_section.add_widget(self.auto_range_check)

        layout.addWidget(settings_section)

        # Value Range section
        range_section = PanelSection("Value Range")

        # Min Value
        min_container = QWidget()
        min_layout = QVBoxLayout(min_container)
        min_layout.setContentsMargins(0, 0, 0, 0)
        min_layout.setSpacing(4)

        min_label = QLabel("Min Value")
        min_label.setStyleSheet("color: #6B7280; font-size: 11px;")
        min_layout.addWidget(min_label)

        self.min_value_spin = QDoubleSpinBox()
        self.min_value_spin.setRange(-1000.0, 1000.0)
        self.min_value_spin.setValue(0.0)
        self.min_value_spin.setSingleStep(0.1)
        self.min_value_spin.setDecimals(1)
        self.min_value_spin.setEnabled(False)  # Disabled by default (auto-range is on)
        self.min_value_spin.setStyleSheet("""
            QDoubleSpinBox {
                background-color: white;
                border: 1px solid #D1D5DB;
                border-radius: 4px;
                padding: 4px 8px;
                font-size: 11px;
                color: #374151;
            }
            QDoubleSpinBox:hover {
                border-color: #9CA3AF;
            }
            QDoubleSpinBox:disabled {
                background-color: #F3F4F6;
                color: #9CA3AF;
            }
        """)
        self.min_value_spin.valueChanged.connect(self._on_parameter_changed)
        min_layout.addWidget(self.min_value_spin)

        range_section.add_widget(min_container)

        # Max Value
        max_container = QWidget()
        max_layout = QVBoxLayout(max_container)
        max_layout.setContentsMargins(0, 0, 0, 0)
        max_layout.setSpacing(4)

        max_label = QLabel("Max Value")
        max_label.setStyleSheet("color: #6B7280; font-size: 11px;")
        max_layout.addWidget(max_label)

        self.max_value_spin = QDoubleSpinBox()
        self.max_value_spin.setRange(-1000.0, 1000.0)
        self.max_value_spin.setValue(1.0)
        self.max_value_spin.setSingleStep(0.1)
        self.max_value_spin.setDecimals(1)
        self.max_value_spin.setEnabled(False)  # Disabled by default (auto-range is on)
        self.max_value_spin.setStyleSheet(self.min_value_spin.styleSheet())
        self.max_value_spin.valueChanged.connect(self._on_parameter_changed)
        max_layout.addWidget(self.max_value_spin)

        range_section.add_widget(max_container)

        layout.addWidget(range_section)

        # Histogram section
        histogram_section = PanelSection("Histogram")

        # Placeholder histogram display
        histogram_placeholder = QWidget()
        histogram_placeholder.setFixedHeight(96)
        histogram_placeholder.setStyleSheet("""
            QWidget {
                background-color: #F3F4F6;
                border: 1px solid #D1D5DB;
                border-radius: 4px;
            }
        """)

        histogram_layout = QVBoxLayout(histogram_placeholder)
        histogram_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        histogram_label = QLabel("Histogram Display")
        histogram_label.setStyleSheet("color: #9CA3AF; font-size: 11px;")
        histogram_layout.addWidget(histogram_label)

        histogram_section.add_widget(histogram_placeholder)
        layout.addWidget(histogram_section)

        layout.addStretch()

        scroll.setWidget(content)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(scroll)

    def _on_auto_range_changed(self):
        """Handle auto-range checkbox toggle"""
        auto_range = self.auto_range_check.isChecked()
        self.min_value_spin.setEnabled(not auto_range)
        self.max_value_spin.setEnabled(not auto_range)
        self._on_parameter_changed()

    def _on_parameter_changed(self):
        """Emit signal when any parameter changes"""
        self.settings = self.get_settings()
        self.parameters_changed.emit(self.settings)

    def get_settings(self) -> Dict[str, Any]:
        """Get current parameter settings"""
        return {
            'resolution': self.resolution_combo.currentText(),
            'min_region_size': self.region_size_combo.currentText(),
            'colormap': self.colormap_combo.currentText(),
            'auto_range': self.auto_range_check.isChecked(),
            'min_value': self.min_value_spin.value(),
            'max_value': self.max_value_spin.value()
        }

    def set_settings(self, settings: Dict[str, Any]):
        """Set parameter settings"""
        # Block signals during bulk update
        self.resolution_combo.blockSignals(True)
        self.region_size_combo.blockSignals(True)
        self.colormap_combo.blockSignals(True)
        self.auto_range_check.blockSignals(True)
        self.min_value_spin.blockSignals(True)
        self.max_value_spin.blockSignals(True)

        # Update controls
        if 'resolution' in settings:
            self.resolution_combo.setCurrentText(settings['resolution'])
        if 'min_region_size' in settings:
            self.region_size_combo.setCurrentText(settings['min_region_size'])
        if 'colormap' in settings:
            self.colormap_combo.setCurrentText(settings['colormap'])
        if 'auto_range' in settings:
            self.auto_range_check.setChecked(settings['auto_range'])
            self.min_value_spin.setEnabled(not settings['auto_range'])
            self.max_value_spin.setEnabled(not settings['auto_range'])
        if 'min_value' in settings:
            self.min_value_spin.setValue(settings['min_value'])
        if 'max_value' in settings:
            self.max_value_spin.setValue(settings['max_value'])

        # Unblock signals
        self.resolution_combo.blockSignals(False)
        self.region_size_combo.blockSignals(False)
        self.colormap_combo.blockSignals(False)
        self.auto_range_check.blockSignals(False)
        self.min_value_spin.blockSignals(False)
        self.max_value_spin.blockSignals(False)

        self.settings = settings


class RightPanel(QWidget):
    """
    Right panel with vertical icon tabs.

    Layout:
    - Left edge: VerticalIconTabBar (48px wide)
    - Right: Panel content area that switches based on active tab
    - Width: 320px default (240px min, 450px max)

    Signals:
        tab_changed(str): Emitted when tab selection changes
        layout_changed(str): Emitted when viewport layout changes
        region_selected(str): Emitted when region is selected
        region_pinned(str, bool): Emitted when region pin state changes
        region_deleted(str): Emitted when region is deleted
        quick_fix_clicked(str): Emitted when constraint quick fix clicked
        constraint_selected(str): Emitted when constraint is selected
        copy_indices_clicked(): Emitted when copy indices button clicked
        parameters_changed(dict): Emitted when analysis parameters change
    """

    tab_changed = pyqtSignal(str)  # Emits tab name
    layout_changed = pyqtSignal(str)  # viewport layout
    region_selected = pyqtSignal(str)  # region_id
    region_pinned = pyqtSignal(str, bool)  # region_id, pinned
    region_deleted = pyqtSignal(str)  # region_id
    quick_fix_clicked = pyqtSignal(str)  # constraint_id
    constraint_selected = pyqtSignal(str)  # constraint_id
    copy_indices_clicked = pyqtSignal()  # selection copy button
    parameters_changed = pyqtSignal(dict)  # analysis parameters

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumWidth(240)
        self.setMaximumWidth(450)
        self.resize(320, 600)  # Default size

        self._setup_ui()

    def _setup_ui(self):
        """Setup UI components"""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Vertical icon tab bar
        self.tab_bar = VerticalIconTabBar(self)
        self.tab_bar.tab_changed.connect(self._on_tab_changed)
        layout.addWidget(self.tab_bar)

        # Stacked widget for panel content
        self.content_stack = QStackedWidget(self)
        layout.addWidget(self.content_stack)

        # Create panel instances
        self.viewport_panel = ViewportPanel(self)
        self.regions_panel = RegionsPanel(self)
        self.constraints_panel = ConstraintsPanel(self)
        self.selection_panel = SelectionPanel(self)
        self.parameters_panel = ParametersPanel(self)

        # Create and add panels
        self.panels = {
            "viewport": self.viewport_panel,
            "regions": self.regions_panel,
            "constraints": self.constraints_panel,
            "selection": self.selection_panel,
            "parameters": self.parameters_panel,
        }

        for panel in self.panels.values():
            self.content_stack.addWidget(panel)

        # Connect panel signals
        self.viewport_panel.layout_changed.connect(self.layout_changed.emit)
        self.regions_panel.region_selected.connect(self.region_selected.emit)
        self.regions_panel.region_pinned.connect(self.region_pinned.emit)
        self.regions_panel.region_deleted.connect(self.region_deleted.emit)
        self.constraints_panel.quick_fix_clicked.connect(self.quick_fix_clicked.emit)
        self.constraints_panel.constraint_selected.connect(self.constraint_selected.emit)
        self.selection_panel.copy_indices_clicked.connect(self.copy_indices_clicked.emit)
        self.parameters_panel.parameters_changed.connect(self.parameters_changed.emit)

        # Show initial panel
        self.content_stack.setCurrentWidget(self.panels["viewport"])

        # Styling
        self.setStyleSheet("""
            RightPanel {
                background-color: #FAFAFA;
                border-left: 1px solid #D1D1D6;
            }
        """)

    def _on_tab_changed(self, tab_id: str):
        """Handle tab change"""
        if tab_id in self.panels:
            self.content_stack.setCurrentWidget(self.panels[tab_id])
            self.tab_changed.emit(tab_id)

    def set_active_tab(self, tab_id: str):
        """Programmatically set active tab"""
        self.tab_bar.set_active_tab(tab_id)

    def get_active_tab(self) -> str:
        """Get current active tab ID"""
        return self.tab_bar.active_tab

    def set_regions(self, regions: List[Dict[str, Any]]):
        """Update regions list in RegionsPanel"""
        self.regions_panel.set_regions(regions)

    def set_constraints(self, constraints: List[Dict[str, Any]]):
        """Update constraints list in ConstraintsPanel"""
        self.constraints_panel.set_constraints(constraints)


if __name__ == "__main__":
    import sys
    from PyQt6.QtWidgets import QApplication

    app = QApplication(sys.argv)

    # Test window
    panel = RightPanel()
    panel.tab_changed.connect(lambda tab: print(f"Tab changed: {tab}"))
    panel.layout_changed.connect(lambda layout: print(f"Layout changed: {layout}"))
    panel.region_selected.connect(lambda rid: print(f"Region selected: {rid}"))
    panel.region_pinned.connect(lambda rid, pinned: print(f"Region {rid} pinned: {pinned}"))
    panel.region_deleted.connect(lambda rid: print(f"Region deleted: {rid}"))
    panel.quick_fix_clicked.connect(lambda cid: print(f"Quick fix clicked: {cid}"))
    panel.constraint_selected.connect(lambda cid: print(f"Constraint selected: {cid}"))

    # Add test data to regions panel
    test_regions = [
        {
            'id': 'region_1',
            'name': 'Base Region',
            'unity_principle': 'Curvature Unity',
            'unity_strength': 0.92,
            'pinned': True,
            'color': '#10B981',  # Green
            'faces': list(range(50))
        },
        {
            'id': 'region_2',
            'name': 'Handle Region',
            'unity_principle': 'Flow Unity',
            'unity_strength': 0.87,
            'pinned': False,
            'color': '#F59E0B',  # Yellow
            'faces': list(range(30))
        },
        {
            'id': 'region_3',
            'name': 'Rim Region',
            'unity_principle': 'Topological Unity',
            'unity_strength': 0.74,
            'pinned': True,
            'color': '#F97316',  # Orange
            'faces': list(range(25))
        },
    ]
    panel.set_regions(test_regions)

    # Add test constraint data
    test_constraints = [
        {
            'id': 'constraint_1',
            'title': 'Undercut violation',
            'description': 'Region 1: Base - faces 45-67',
            'severity': 0.85,
            'type': 'error'
        },
        {
            'id': 'constraint_2',
            'title': 'Trapped volume detected',
            'description': 'Region 2: Handle - cavity inaccessible',
            'severity': 0.72,
            'type': 'error'
        },
        {
            'id': 'constraint_3',
            'title': 'Insufficient draft angle',
            'description': 'Region 1: Base - 2.5 degrees (min 3 degrees)',
            'severity': 0.45,
            'type': 'warning'
        },
        {
            'id': 'constraint_4',
            'title': 'Wall thickness issue',
            'description': 'Region 3: Rim - 1.8mm (min 2.0mm)',
            'severity': 0.38,
            'type': 'warning'
        },
        {
            'id': 'constraint_5',
            'title': 'Seam gap detected',
            'description': 'Between Region 1 & 2 - 0.3mm gap',
            'severity': 0.28,
            'type': 'warning'
        },
    ]
    panel.set_constraints(test_constraints)

    # Switch to constraints tab to show test data
    panel.set_active_tab('constraints')

    panel.show()

    sys.exit(app.exec())
