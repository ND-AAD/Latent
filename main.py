#!/usr/bin/env python3
"""
Ceramic Mold Analyzer - Main Application
Desktop application for discovering mathematical decompositions of SubD surfaces
"""

import sys
import numpy as np
from pathlib import Path
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QSplitter, QStatusBar, QPushButton, QLabel, QGroupBox,
    QRadioButton, QButtonGroup, QMessageBox, QTextEdit,
    QDockWidget, QToolBar, QTabWidget, QStackedWidget,
    QScrollArea, QListWidget, QComboBox, QCheckBox,
    QSpinBox, QDoubleSpinBox, QLineEdit, QProgressBar,
    QFrame, QGridLayout, QSizePolicy
)
from PyQt6.QtCore import Qt, QTimer, QSettings, pyqtSignal
from PyQt6.QtGui import QAction, QTextCursor, QShortcut, QKeySequence, QFont

# Add app directory to path
sys.path.insert(0, str(Path(__file__).parent))

# Add cpp_core build directory to path for compiled module
cpp_build_path = Path(__file__).parent / "cpp_core" / "build"
if cpp_build_path.exists():
    sys.path.insert(0, str(cpp_build_path))

# Import our components
from app.ui.viewport_3d import Viewport3D
from app.ui.viewport_layout import ViewportLayoutManager, ViewportLayout, ViewType
from app.ui.region_list_widget import RegionListWidget
from app.ui.region_properties_dialog import RegionPropertiesDialog
from app.ui.analysis_panel import AnalysisPanel
from app.ui.constraint_panel import ConstraintPanel
from app.ui.edit_mode_toolbar import EditModeToolBar, EditModeWidget
from app.ui.selection_info_panel import SelectionInfoPanel
from app.bridge.rhino_bridge import RhinoBridge
from app.bridge.geometry_receiver import GeometryReceiver
from app.bridge.subd_fetcher import SubDFetcher
from app.bridge.live_bridge import LiveBridge
from app.geometry.subd_display import SubDDisplayManager
from app.state.app_state import ApplicationState
from app.state.parametric_region import ParametricRegion
from app.state.edit_mode import EditMode
import cpp_core


class ConnectionStatusWidget(QWidget):
    """Show connection status to Grasshopper server."""

    def __init__(self, live_bridge):
        super().__init__()
        self.live_bridge = live_bridge

        layout = QHBoxLayout()
        layout.setContentsMargins(5, 2, 5, 2)

        # Status indicator (colored dot)
        self.status_label = QLabel("●")
        self.status_label.setStyleSheet("font-size: 16px;")

        # Status text
        self.text_label = QLabel("Disconnected")

        layout.addWidget(self.status_label)
        layout.addWidget(self.text_label)
        layout.addStretch()

        self.setLayout(layout)

        # Update timer
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update_status)
        self.update_timer.start(500)  # Update UI every 500ms

    def update_status(self):
        """Update status display."""
        status = self.live_bridge.get_connection_status()

        if status['connected'] and status['active']:
            self.status_label.setStyleSheet("color: green; font-size: 16px;")
            self.text_label.setText("Live sync active")
        elif status['connected']:
            self.status_label.setStyleSheet("color: orange; font-size: 16px;")
            self.text_label.setText("Connected (manual)")
        else:
            self.status_label.setStyleSheet("color: red; font-size: 16px;")
            self.text_label.setText("Disconnected")


class MainWindow(QMainWindow):
    """Main application window for Ceramic Mold Analyzer"""
    
    def __init__(self):
        super().__init__()

        # Buffer for debug messages before console is created
        self._debug_buffer = []

        # Initialize state and bridge
        self.state = ApplicationState()
        self.rhino_bridge = RhinoBridge()

        # Add SubD components (C++ integration)
        self.subd_fetcher = SubDFetcher()
        self.subd_evaluator = cpp_core.SubDEvaluator()
        self.current_cage = None

        # Create live bridge (before UI init so ConnectionStatusWidget can use it)
        self.live_bridge = LiveBridge(
            fetcher=self.subd_fetcher,
            on_geometry_changed=self.on_geometry_updated
        )

        # Initialize geometry receiver (listens for pushes from Grasshopper)
        # Use port 8800 to avoid conflict with macOS ControlCenter (AirPlay on 5000)
        self.geometry_receiver = GeometryReceiver(port=8800)
        self.geometry_receiver.start()

        self.init_ui()
        self.setup_connections()

        # Flush buffered messages to console
        for msg in self._debug_buffer:
            self.debug_console.append(msg)
        self._debug_buffer = None

        # Initial debug message
        self.log_debug("🎨 Ceramic Mold Analyzer initialized")
        self.log_debug("📍 Controls: LEFT=Select | RIGHT or MIDDLE=Rotate | Shift+RIGHT=Pan | Wheel=Zoom")
        self.log_debug("📡 Listening for geometry on port 8800 (manual push mode)")
        self.log_debug("💡 In Grasshopper: Click button to push geometry")
        
    def init_ui(self):
        """Initialize the user interface with four-sided architecture v2.0"""
        self.setWindowTitle("Ceramic Mold Analyzer - v2.0")

        # Set window size to 90% of screen (as per UX spec v2.0)
        screen = QApplication.primaryScreen().availableGeometry()
        width = int(screen.width() * 0.9)
        height = int(screen.height() * 0.9)

        # Apply constraints from spec
        width = min(max(width, 1280), 2400)
        height = max(height, 720)

        x = (screen.width() - width) // 2
        y = (screen.height() - height) // 2
        self.setGeometry(x, y, width, height)

        # Create the main four-sided layout
        self.create_main_layout()

        # Setup keyboard shortcuts
        self.setup_edit_mode_shortcuts()
        self.setup_tab_shortcuts()

        # Status bar (part of bottom panel now, but keep for compatibility)
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.setVisible(False)  # Hide default status bar

        # Keep references for compatibility
        self.connection_indicator = QLabel("● Disconnected")
        self.connection_indicator.setStyleSheet("color: #FF3B30;")

        # Initial message in bottom panel
        if hasattr(self, 'status_label'):
            self.status_label.setText("Ready. Connect to Rhino to begin.")

        # Create menus (after viewport is created)
        self.create_menus()

        # Apply global styling
        self.apply_styling()

    def create_main_layout(self):
        """Create the four-sided UI architecture v2.0"""
        # Central widget container
        central = QWidget()
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # TOP: Tab system for workflow
        self.tab_widget = self.create_tab_widget()

        # The tab widget will contain the main content area
        # Each tab has its own LEFT panel + center content

        main_layout.addWidget(self.tab_widget)

        # BOTTOM: System communication panel
        self.bottom_panel = self.create_bottom_panel()
        main_layout.addWidget(self.bottom_panel)

        central.setLayout(main_layout)
        self.setCentralWidget(central)

        # Create the viewport and right panel that will be shared
        self.create_shared_components()

        # Store references for compatibility with existing code
        self.store_compatibility_references()

    def create_shared_components(self):
        """Create the shared viewport and right panel components"""
        # Create viewport manager for center area
        self.viewport_layout = ViewportLayoutManager()
        self.viewport = None  # Keep reference for compatibility

        # Set to single viewport by default (not 4-grid)
        self.viewport_layout.set_layout(ViewportLayout.SINGLE)

        # Create right panel with vertical tabs
        self.right_panel = self.create_right_panel()

    def create_tab_widget(self):
        """Create main workflow tab system - 6 tabs with proper layout"""
        tabs = QTabWidget()
        tabs.setTabPosition(QTabWidget.TabPosition.North)
        tabs.setStyleSheet("""
            QTabWidget::pane {
                border: 1px solid #D1D1D6;
                background: #FFFFFF;
            }
            QTabBar::tab {
                background: #F5F5F5;
                padding: 8px 20px;
                margin-right: 2px;
                border: 1px solid #D1D1D6;
                border-bottom: none;
                min-width: 80px;
            }
            QTabBar::tab:selected {
                background: #FFFFFF;
                border-bottom: 1px solid #FFFFFF;
            }
        """)

        # Create main container for each tab that includes viewport and right panel
        self.file_tab = self.create_tab_with_layout("FILE")
        self.analyze_tab = self.create_tab_with_layout("ANALYZE")
        self.edit_tab = self.create_tab_with_layout("EDIT")
        self.validate_tab = self.create_tab_with_layout("VALIDATE")
        self.fabricate_tab = self.create_tab_with_layout("FABRICATE")
        self.view_tab = self.create_tab_with_layout("VIEW")

        # Add tabs
        tabs.addTab(self.file_tab, "FILE")
        tabs.addTab(self.analyze_tab, "ANALYZE")
        tabs.addTab(self.edit_tab, "EDIT")
        tabs.addTab(self.validate_tab, "VALIDATE")
        tabs.addTab(self.fabricate_tab, "FABRICATE")
        tabs.addTab(self.view_tab, "VIEW")

        # Set tooltips
        tabs.setTabToolTip(0, "File Operations (F1)")
        tabs.setTabToolTip(1, "Mathematical Analysis (F2)")
        tabs.setTabToolTip(2, "Region Editing (F3)")
        tabs.setTabToolTip(3, "Constraint Validation (F4)")
        tabs.setTabToolTip(4, "Mold Fabrication (F5)")
        tabs.setTabToolTip(5, "View Controls (F6)")

        # Connect tab change signal
        tabs.currentChanged.connect(self.on_tab_changed)

        return tabs

    def create_tab_with_layout(self, tab_name):
        """Create a tab with proper three-column layout: LEFT | CENTER | RIGHT"""
        tab_widget = QWidget()
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Create horizontal splitter for the three sections
        splitter = QSplitter(Qt.Orientation.Horizontal)

        # LEFT: Secondary/advanced tools (context-specific)
        left_panel = self.create_left_panel_for_tab(tab_name)
        left_panel.setMinimumWidth(180)
        left_panel.setMaximumWidth(280)

        # CENTER: Main content area (viewport in most cases)
        if tab_name in ["ANALYZE", "EDIT", "VALIDATE", "FABRICATE", "VIEW"]:
            # These tabs need the viewport
            center_content = self.viewport_layout if hasattr(self, 'viewport_layout') else QWidget()
        else:
            # FILE tab doesn't need viewport, just a content area
            center_content = QWidget()
            center_content.setStyleSheet("background-color: #F5F5F5;")

        # RIGHT: Properties panel (shared across all tabs)
        right_panel = self.right_panel if hasattr(self, 'right_panel') else QWidget()

        # Add to splitter
        splitter.addWidget(left_panel)
        splitter.addWidget(center_content)
        splitter.addWidget(right_panel)

        # Set proportions
        splitter.setStretchFactor(0, 0)  # Left panel fixed
        splitter.setStretchFactor(1, 1)  # Center expandable
        splitter.setStretchFactor(2, 0)  # Right panel fixed

        # Set sizes
        splitter.setSizes([200, 800, 300])

        layout.addWidget(splitter)
        tab_widget.setLayout(layout)

        return tab_widget

    def create_left_panel_for_tab(self, tab_name):
        """Create the LEFT panel content based on the tab"""
        panel = QWidget()
        panel.setStyleSheet("background-color: #FAFAFA; border-right: 1px solid #D1D1D6;")
        layout = QVBoxLayout()
        layout.setContentsMargins(10, 10, 10, 10)

        if tab_name == "FILE":
            panel = self.create_file_left_panel()
        elif tab_name == "ANALYZE":
            panel = self.create_analyze_left_panel()
        elif tab_name == "EDIT":
            panel = self.create_edit_left_panel()
        elif tab_name == "VALIDATE":
            panel = self.create_validate_left_panel()
        elif tab_name == "FABRICATE":
            panel = self.create_fabricate_left_panel()
        elif tab_name == "VIEW":
            panel = self.create_view_left_panel()

        return panel

    def setup_tab_shortcuts(self):
        """Set up F1-F6 shortcuts for tabs"""
        for i in range(6):
            shortcut = QShortcut(QKeySequence(f"F{i+1}"), self)
            shortcut.activated.connect(lambda idx=i: self.tab_widget.setCurrentIndex(idx))

    def create_file_left_panel(self):
        """Create LEFT panel for FILE tab"""
        panel = QWidget()
        panel.setStyleSheet("background-color: #FAFAFA; border-right: 1px solid #D1D1D6;")
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        # Primary actions section
        layout.addWidget(QLabel("<b>File Operations</b>"))

        btn_new = QPushButton("New Session")
        btn_open = QPushButton("Open Session")
        btn_save = QPushButton("Save Session")
        btn_save.clicked.connect(self.save_session)
        btn_save_as = QPushButton("Save As...")

        layout.addWidget(QLabel("<b>Import/Export</b>"))
        btn_import = QPushButton("Import from Rhino")
        btn_import.clicked.connect(self.load_from_rhino)
        btn_export = QPushButton("Export to Rhino")

        for btn in [btn_new, btn_open, btn_save, btn_save_as, btn_import, btn_export]:
            btn.setMinimumHeight(28)
            layout.addWidget(btn)

        # Separator
        layout.addWidget(QFrame())

        # Advanced section
        layout.addWidget(QLabel("<b>Advanced</b>"))

        btn_template = QPushButton("Save Template")
        btn_load_template = QPushButton("Load Template")
        btn_batch = QPushButton("Batch Export")

        for btn in [btn_template, btn_load_template, btn_batch]:
            btn.setMinimumHeight(28)
            layout.addWidget(btn)

        layout.addStretch()
        panel.setLayout(layout)
        return panel

    def create_analyze_left_panel(self):
        """Create LEFT panel for ANALYZE tab"""
        panel = QWidget()
        panel.setStyleSheet("background-color: #FAFAFA; border-right: 1px solid #D1D1D6;")
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        # Create and add the analysis panel (contains the lens controls)
        self.analysis_panel = AnalysisPanel()
        self.analysis_panel.lens_changed.connect(self.on_lens_changed)
        self.analysis_panel.analysis_requested.connect(self.run_analysis)
        layout.addWidget(self.analysis_panel)

        # Advanced section
        layout.addWidget(QLabel("<b>Advanced Analysis</b>"))

        btn_compare = QPushButton("Compare Analyses")
        btn_differential = QPushButton("Differential Analysis")
        btn_batch = QPushButton("Batch Analysis")

        for btn in [btn_compare, btn_differential, btn_batch]:
            btn.setMinimumHeight(28)
            layout.addWidget(btn)

        layout.addWidget(QLabel("<b>Presets</b>"))
        btn_save_preset = QPushButton("Save Preset")
        btn_load_preset = QPushButton("Load Preset")

        for btn in [btn_save_preset, btn_load_preset]:
            btn.setMinimumHeight(28)
            layout.addWidget(btn)

        layout.addStretch()
        panel.setLayout(layout)
        return panel

    def create_edit_left_panel(self):
        """Create LEFT panel for EDIT tab"""
        panel = QWidget()
        panel.setStyleSheet("background-color: #FAFAFA; border-right: 1px solid #D1D1D6;")
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        # Edit mode widget
        layout.addWidget(QLabel("<b>Edit Mode</b>"))
        self.edit_mode_widget = EditModeWidget()
        self.state.edit_mode_manager.mode_changed.connect(self.edit_mode_widget.set_mode)
        self.edit_mode_widget.mode_changed.connect(self.state.edit_mode_manager.set_mode)
        layout.addWidget(self.edit_mode_widget)

        # Selection operations
        layout.addWidget(QLabel("<b>Selection</b>"))
        btn_select_all = QPushButton("Select All")
        btn_select_all.clicked.connect(self.select_all)
        btn_clear = QPushButton("Clear Selection")
        btn_clear.clicked.connect(self.clear_selection)
        btn_invert = QPushButton("Invert Selection")
        btn_invert.clicked.connect(self.invert_selection)

        for btn in [btn_select_all, btn_clear, btn_invert]:
            btn.setMinimumHeight(28)
            layout.addWidget(btn)

        # Region operations
        layout.addWidget(QLabel("<b>Region Operations</b>"))
        btn_pin = QPushButton("Pin/Unpin Region")
        btn_delete = QPushButton("Delete Region")

        for btn in [btn_pin, btn_delete]:
            btn.setMinimumHeight(28)
            layout.addWidget(btn)

        # Advanced section
        layout.addWidget(QLabel("<b>Advanced</b>"))
        btn_grow = QPushButton("Grow Selection")
        btn_grow.clicked.connect(self.grow_selection)
        btn_shrink = QPushButton("Shrink Selection")
        btn_shrink.clicked.connect(self.shrink_selection)
        btn_merge = QPushButton("Merge Regions")
        btn_split = QPushButton("Split Region")

        for btn in [btn_grow, btn_shrink, btn_merge, btn_split]:
            btn.setMinimumHeight(28)
            layout.addWidget(btn)

        layout.addStretch()
        panel.setLayout(layout)
        return panel

    def create_validate_left_panel(self):
        """Create LEFT panel for VALIDATE tab"""
        panel = QWidget()
        panel.setStyleSheet("background-color: #FAFAFA; border-right: 1px solid #D1D1D6;")
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        # Add constraint panel
        self.constraint_panel = ConstraintPanel()
        layout.addWidget(self.constraint_panel)

        # Validation controls
        layout.addWidget(QLabel("<b>Validation</b>"))
        btn_check = QPushButton("Run Constraint Check")
        btn_clear = QPushButton("Clear Validation")
        btn_revalidate = QPushButton("Re-validate All")

        for btn in [btn_check, btn_clear, btn_revalidate]:
            btn.setMinimumHeight(28)
            layout.addWidget(btn)

        # Automatic fixes
        layout.addWidget(QLabel("<b>Automatic Fixes</b>"))
        btn_fix_undercuts = QPushButton("Fix Undercuts")
        btn_fix_draft = QPushButton("Auto-Fix Draft Angles")
        btn_adjust_thickness = QPushButton("Adjust Wall Thickness")
        btn_repair_seams = QPushButton("Repair Seam Gaps")

        for btn in [btn_fix_undercuts, btn_fix_draft, btn_adjust_thickness, btn_repair_seams]:
            btn.setMinimumHeight(28)
            layout.addWidget(btn)

        layout.addStretch()
        panel.setLayout(layout)
        return panel

    def create_fabricate_left_panel(self):
        """Create LEFT panel for FABRICATE tab"""
        panel = QWidget()
        panel.setStyleSheet("background-color: #FAFAFA; border-right: 1px solid #D1D1D6;")
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        # Primary fabrication
        layout.addWidget(QLabel("<b>Mold Generation</b>"))
        btn_generate = QPushButton("Generate Mold Shells")
        btn_generate.setMinimumHeight(40)
        btn_generate.setStyleSheet("""
            QPushButton {
                background-color: #34C759;
                color: white;
                font-weight: bold;
            }
        """)
        btn_generate.clicked.connect(self.generate_molds)
        layout.addWidget(btn_generate)

        btn_send = QPushButton("Send to Rhino")
        btn_send.clicked.connect(self.send_to_rhino)
        layout.addWidget(btn_send)

        # Mold features
        layout.addWidget(QLabel("<b>Mold Features</b>"))
        btn_keys = QPushButton("Add Registration Keys")
        btn_bands = QPushButton("Add Band Grooves")
        btn_spouts = QPushButton("Add Pour Spouts")

        for btn in [btn_keys, btn_bands, btn_spouts]:
            btn.setMinimumHeight(28)
            layout.addWidget(btn)

        # Export
        layout.addWidget(QLabel("<b>Export</b>"))
        btn_calculate = QPushButton("Calculate Slip Volume")
        btn_export = QPushButton("Export for 3D Printing")

        for btn in [btn_calculate, btn_export]:
            btn.setMinimumHeight(28)
            layout.addWidget(btn)

        layout.addStretch()
        panel.setLayout(layout)
        return panel

    def create_view_left_panel(self):
        """Create LEFT panel for VIEW tab"""
        panel = QWidget()
        panel.setStyleSheet("background-color: #FAFAFA; border-right: 1px solid #D1D1D6;")
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        # View controls
        layout.addWidget(QLabel("<b>View Controls</b>"))
        btn_reset_all = QPushButton("Reset All Views")
        btn_reset_current = QPushButton("Reset Current View")
        btn_frame_all = QPushButton("Frame All Geometry")
        btn_frame_selected = QPushButton("Frame Selected")

        for btn in [btn_reset_all, btn_reset_current, btn_frame_all, btn_frame_selected]:
            btn.setMinimumHeight(28)
            layout.addWidget(btn)

        # Display options
        layout.addWidget(QLabel("<b>Display Options</b>"))
        chk_axes = QCheckBox("Show Axes")
        chk_grid = QCheckBox("Show Grid")
        chk_edges = QCheckBox("Show Edges")
        chk_axes.setChecked(True)
        chk_grid.setChecked(True)

        for chk in [chk_axes, chk_grid, chk_edges]:
            layout.addWidget(chk)

        # Advanced
        layout.addWidget(QLabel("<b>Advanced View</b>"))
        btn_save_view = QPushButton("Save Named View")
        btn_camera_props = QPushButton("Camera Properties")

        for btn in [btn_save_view, btn_camera_props]:
            btn.setMinimumHeight(28)
            layout.addWidget(btn)

        layout.addStretch()
        panel.setLayout(layout)
        return panel

    def create_right_panel(self):
        """Create right panel with vertical tabs for properties"""
        right_tabs = QTabWidget()
        right_tabs.setTabPosition(QTabWidget.TabPosition.East)
        right_tabs.setMinimumWidth(240)
        right_tabs.setMaximumWidth(450)

        # VIEWPORT tab
        viewport_tab = QScrollArea()
        viewport_tab.setWidgetResizable(True)
        viewport_content = QWidget()
        viewport_layout = QVBoxLayout()
        viewport_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        # Layout selector
        viewport_layout.addWidget(QLabel("<b>Layout</b>"))
        layout_combo = QComboBox()
        layout_combo.addItems(["Single", "Two Horizontal", "Two Vertical", "Four Grid"])
        layout_combo.currentIndexChanged.connect(self.on_layout_changed)
        viewport_layout.addWidget(layout_combo)

        viewport_layout.addStretch()
        viewport_content.setLayout(viewport_layout)
        viewport_tab.setWidget(viewport_content)

        # REGIONS tab - reuse existing region list
        self.region_list = RegionListWidget()
        self.region_list.region_selected.connect(self.on_region_selected)
        self.region_list.region_pinned.connect(self.on_region_pinned)

        # CONSTRAINTS tab - already created in validate tab
        constraints_scroll = QScrollArea()
        constraints_scroll.setWidgetResizable(True)
        constraints_content = QWidget()
        constraints_layout = QVBoxLayout()
        constraints_layout.addWidget(QLabel("<b>Constraint Results</b>"))
        constraints_layout.addStretch()
        constraints_content.setLayout(constraints_layout)
        constraints_scroll.setWidget(constraints_content)

        # SELECTION tab - reuse existing selection info panel
        self.selection_info_panel = SelectionInfoPanel()

        # PARAMETERS tab - context-sensitive
        params_scroll = QScrollArea()
        params_scroll.setWidgetResizable(True)
        params_content = QWidget()
        params_layout = QVBoxLayout()
        params_layout.addWidget(QLabel("<b>Parameters</b>"))
        params_layout.addStretch()
        params_content.setLayout(params_layout)
        params_scroll.setWidget(params_content)

        # Add tabs
        right_tabs.addTab(viewport_tab, "VIEWPORT")
        right_tabs.addTab(self.region_list, "REGIONS")
        right_tabs.addTab(constraints_scroll, "CONSTRAINTS")
        right_tabs.addTab(self.selection_info_panel, "SELECTION")
        right_tabs.addTab(params_scroll, "PARAMETERS")

        return right_tabs

    def create_bottom_panel(self):
        """Create bottom panel for system communication"""
        panel = QWidget()
        panel.setMaximumHeight(160)
        panel.setMinimumHeight(100)

        layout = QHBoxLayout()
        layout.setContentsMargins(5, 5, 5, 5)

        # Command input (30%)
        cmd_widget = QWidget()
        cmd_layout = QVBoxLayout()
        cmd_layout.addWidget(QLabel("Command"))

        cmd_input_widget = QWidget()
        cmd_input_layout = QHBoxLayout()
        cmd_input_layout.setContentsMargins(0, 0, 0, 0)
        cmd_input_layout.addWidget(QLabel(">"))
        self.command_input = QLineEdit()
        self.command_input.setPlaceholderText("Type command...")
        self.command_input.returnPressed.connect(self.execute_command)
        cmd_input_layout.addWidget(self.command_input)
        cmd_input_widget.setLayout(cmd_input_layout)

        cmd_layout.addWidget(cmd_input_widget)
        cmd_widget.setLayout(cmd_layout)
        layout.addWidget(cmd_widget, 3)

        # Command history / Debug console (40%)
        history_widget = QWidget()
        history_layout = QVBoxLayout()
        history_layout.addWidget(QLabel("Console"))
        self.debug_console = QTextEdit()
        self.debug_console.setReadOnly(True)
        self.debug_console.setStyleSheet(
            "font-family: monospace; font-size: 10px; "
            "background-color: #1E1E1E; color: #D4D4D4;"
        )
        history_layout.addWidget(self.debug_console)
        history_widget.setLayout(history_layout)
        layout.addWidget(history_widget, 4)

        # Connection status (15%)
        conn_widget = QWidget()
        conn_layout = QVBoxLayout()
        conn_layout.addWidget(QLabel("Connection"))

        # Use existing connection status widget
        self.status_widget = ConnectionStatusWidget(self.live_bridge)
        conn_layout.addWidget(self.status_widget)

        btn_reconnect = QPushButton("Reconnect")
        btn_reconnect.setMaximumHeight(24)
        btn_reconnect.clicked.connect(self.connect_to_rhino)
        conn_layout.addWidget(btn_reconnect)

        conn_widget.setLayout(conn_layout)
        layout.addWidget(conn_widget, 2)

        # System status (15%)
        status_widget = QWidget()
        status_layout = QVBoxLayout()
        status_layout.addWidget(QLabel("Status"))

        self.status_label = QLabel("Ready")
        status_layout.addWidget(self.status_label)

        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        status_layout.addWidget(self.progress_bar)

        status_widget.setLayout(status_layout)
        layout.addWidget(status_widget, 2)

        panel.setLayout(layout)
        return panel

    def store_compatibility_references(self):
        """Store references for backward compatibility with existing code"""
        # These allow existing methods to continue working
        self.analysis_dock = None  # No longer using docks
        self.region_dock = None
        self.constraint_dock = None
        self.selection_dock = None
        self.debug_dock = None

        # Remove old toolbar references
        self.edit_mode_toolbar = None
        self.analysis_toolbar = None

    def on_tab_changed(self, index):
        """Handle tab change - update context-sensitive panels"""
        # Update status
        tabs = ["FILE", "ANALYZE", "EDIT", "VALIDATE", "FABRICATE", "VIEW"]
        if hasattr(self, 'status_label'):
            self.status_label.setText(f"Active: {tabs[index]}")

    def on_layout_changed(self, index):
        """Handle viewport layout change"""
        layouts = [ViewportLayout.SINGLE, ViewportLayout.TWO_HORIZONTAL,
                  ViewportLayout.TWO_VERTICAL, ViewportLayout.FOUR_GRID]
        self.viewport_layout.set_layout(layouts[index])

    def execute_command(self):
        """Execute command from bottom panel input"""
        command = self.command_input.text()
        if command:
            self.log_debug(f"> {command}")
            self.command_input.clear()
            # Add command processing here

    def apply_styling(self):
        """Apply global styling per UX spec v2.0"""
        self.setStyleSheet("""
            QMainWindow {
                background-color: #FFFFFF;
            }
            QWidget {
                font-family: -apple-system, BlinkMacSystemFont, "Segoe UI",
                            Roboto, Helvetica, Arial, sans-serif;
                font-size: 11px;
            }
            QTabWidget::pane {
                border: 1px solid #D1D1D6;
                background: #FFFFFF;
            }
            QTabBar::tab {
                background: #F5F5F5;
                padding: 8px 16px;
                margin-right: 2px;
                border: 1px solid #D1D1D6;
                border-bottom: none;
            }
            QTabBar::tab:selected {
                background: #FFFFFF;
                border-bottom: 1px solid #FFFFFF;
            }
            QTabBar::tab:hover {
                background: #E8E8E8;
            }
            QPushButton {
                padding: 5px 10px;
                border: 1px solid #D1D1D6;
                border-radius: 4px;
                background-color: #F5F5F5;
            }
            QPushButton:hover {
                background-color: #E8E8E8;
            }
            QPushButton:pressed {
                background-color: #D1D1D6;
            }
            QGroupBox {
                font-weight: bold;
                border: 1px solid #D1D1D6;
                border-radius: 4px;
                margin-top: 8px;
                padding-top: 8px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 8px;
                padding: 0 5px;
            }
        """)

    def create_menus(self):
        """Create application menus"""
        menubar = self.menuBar()

        # File menu
        file_menu = menubar.addMenu("File")

        # Load from Rhino (C++ SubD pipeline)
        load_rhino = QAction("Load from &Rhino", self)
        load_rhino.setShortcut("Ctrl+R")
        load_rhino.setToolTip("Load SubD geometry from Grasshopper server (Ctrl+R)")
        load_rhino.triggered.connect(self.load_from_rhino)
        file_menu.addAction(load_rhino)

        # Start live sync
        start_sync = QAction("Start &Live Sync", self)
        start_sync.setShortcut("Ctrl+L")
        start_sync.setToolTip("Enable automatic geometry synchronization (Ctrl+L)")
        start_sync.triggered.connect(self.start_live_sync)
        file_menu.addAction(start_sync)

        # Stop live sync
        stop_sync = QAction("Stop Live Sync", self)
        stop_sync.setToolTip("Disable automatic geometry synchronization")
        stop_sync.triggered.connect(self.stop_live_sync)
        file_menu.addAction(stop_sync)

        file_menu.addSeparator()

        # Force refresh
        refresh = QAction("&Refresh", self)
        refresh.setShortcut("F5")
        refresh.setToolTip("Force geometry refresh from Grasshopper (F5)")
        refresh.triggered.connect(self.force_refresh)
        file_menu.addAction(refresh)

        file_menu.addSeparator()

        connect_action = QAction("Connect to Rhino", self)
        connect_action.setShortcut("Ctrl+O")
        connect_action.setToolTip("Connect to Grasshopper HTTP server (Ctrl+O)")
        connect_action.triggered.connect(self.connect_to_rhino)
        file_menu.addAction(connect_action)

        file_menu.addSeparator()

        save_action = QAction("Save Session", self)
        save_action.setShortcut("Ctrl+S")
        save_action.setToolTip("Save current window layout and session (Ctrl+S)")
        save_action.triggered.connect(self.save_session)
        file_menu.addAction(save_action)

        file_menu.addSeparator()

        quit_action = QAction("Quit", self)
        quit_action.setShortcut("Ctrl+Q")
        quit_action.setToolTip("Exit application (Ctrl+Q)")
        quit_action.triggered.connect(self.close)
        file_menu.addAction(quit_action)
        
        # Edit menu
        edit_menu = menubar.addMenu("Edit")

        undo_action = QAction("Undo", self)
        undo_action.setShortcut("Ctrl+Z")
        undo_action.setToolTip("Undo last action (Ctrl+Z)")
        undo_action.triggered.connect(self.undo)
        edit_menu.addAction(undo_action)

        redo_action = QAction("Redo", self)
        redo_action.setShortcut("Ctrl+Shift+Z")
        redo_action.setToolTip("Redo last undone action (Ctrl+Shift+Z)")
        redo_action.triggered.connect(self.redo)
        edit_menu.addAction(redo_action)

        edit_menu.addSeparator()

        # Selection operations
        clear_sel_action = QAction("Clear Selection", self)
        clear_sel_action.setShortcut("Esc")
        clear_sel_action.setToolTip("Clear current selection (Esc)")
        clear_sel_action.triggered.connect(self.clear_selection)
        edit_menu.addAction(clear_sel_action)

        select_all_action = QAction("Select All", self)
        select_all_action.setShortcut("Ctrl+A")
        select_all_action.setToolTip("Select all elements in current edit mode (Ctrl+A)")
        select_all_action.triggered.connect(self.select_all)
        edit_menu.addAction(select_all_action)

        invert_sel_action = QAction("Invert Selection", self)
        invert_sel_action.setShortcut("Ctrl+I")
        invert_sel_action.setToolTip("Invert current selection (Ctrl+I)")
        invert_sel_action.triggered.connect(self.invert_selection)
        edit_menu.addAction(invert_sel_action)

        edit_menu.addSeparator()

        grow_sel_action = QAction("Grow Selection", self)
        grow_sel_action.setShortcut("Ctrl+>")
        grow_sel_action.setToolTip("Grow selection to topological neighbors (Ctrl+>)")
        grow_sel_action.triggered.connect(self.grow_selection)
        edit_menu.addAction(grow_sel_action)

        shrink_sel_action = QAction("Shrink Selection", self)
        shrink_sel_action.setShortcut("Ctrl+<")
        shrink_sel_action.setToolTip("Shrink selection by removing boundary elements (Ctrl+<)")
        shrink_sel_action.triggered.connect(self.shrink_selection)
        edit_menu.addAction(shrink_sel_action)

        # Analysis menu
        analysis_menu = menubar.addMenu("Analysis")
        
        for lens in ["Flow", "Spectral", "Curvature", "Topological"]:
            action = QAction(f"{lens} Lens", self)
            action.triggered.connect(lambda checked, l=lens: self.run_analysis(l))
            analysis_menu.addAction(action)
        
        # View menu
        view_menu = menubar.addMenu("View")

        # Viewport Layout submenu
        layout_menu = view_menu.addMenu("Viewport Layout")
        layout_menu.setToolTipsVisible(True)

        layout_single = QAction("Single", self)
        layout_single.setShortcut("Alt+1")
        layout_single.setToolTip("Single viewport layout (Alt+1)")
        layout_single.triggered.connect(lambda: self.viewport_layout.set_layout(ViewportLayout.SINGLE))
        layout_menu.addAction(layout_single)

        layout_2h = QAction("Two Horizontal", self)
        layout_2h.setShortcut("Alt+2")
        layout_2h.setToolTip("Two viewports side-by-side (Alt+2)")
        layout_2h.triggered.connect(lambda: self.viewport_layout.set_layout(ViewportLayout.TWO_HORIZONTAL))
        layout_menu.addAction(layout_2h)

        layout_2v = QAction("Two Vertical", self)
        layout_2v.setShortcut("Alt+3")
        layout_2v.setToolTip("Two viewports stacked vertically (Alt+3)")
        layout_2v.triggered.connect(lambda: self.viewport_layout.set_layout(ViewportLayout.TWO_VERTICAL))
        layout_menu.addAction(layout_2v)

        layout_4grid = QAction("Four Grid", self)
        layout_4grid.setShortcut("Alt+4")
        layout_4grid.setToolTip("Four viewports in grid layout (Alt+4)")
        layout_4grid.triggered.connect(lambda: self.viewport_layout.set_layout(ViewportLayout.FOUR_GRID))
        layout_menu.addAction(layout_4grid)

        view_menu.addSeparator()

        reset_view = QAction("Reset All Cameras", self)
        reset_view.setShortcut("Space")
        reset_view.setToolTip("Reset all viewport cameras to fit geometry (Space)")
        reset_view.triggered.connect(self.viewport_layout.reset_all_cameras)
        view_menu.addAction(reset_view)

        view_menu.addSeparator()

        # Test geometry for VTK verification (Week 1 Day 2-4)
        test_cube = QAction("Show Test Cube", self)
        test_cube.triggered.connect(self.show_test_cube)
        view_menu.addAction(test_cube)

        test_sphere = QAction("Show Test SubD Sphere", self)
        test_sphere.triggered.connect(self.show_test_subd_sphere)
        view_menu.addAction(test_sphere)

        test_torus = QAction("Show Test SubD Torus", self)
        test_torus.triggered.connect(self.show_test_subd_torus)
        view_menu.addAction(test_torus)

        test_colored_cube = QAction("Show Colored Cube (Regions)", self)
        test_colored_cube.triggered.connect(self.show_test_colored_cube)
        view_menu.addAction(test_colored_cube)

        # Help menu
        help_menu = menubar.addMenu("Help")
        about_action = QAction("About", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)

    def setup_edit_mode_shortcuts(self):
        """Setup keyboard shortcuts for edit mode switching"""
        # S = Solid mode
        solid_shortcut = QShortcut(QKeySequence("S"), self)
        solid_shortcut.activated.connect(
            lambda: self.state.edit_mode_manager.set_mode(EditMode.SOLID)
        )

        # P = Panel mode
        panel_shortcut = QShortcut(QKeySequence("P"), self)
        panel_shortcut.activated.connect(
            lambda: self.state.edit_mode_manager.set_mode(EditMode.PANEL)
        )

        # E = Edge mode
        edge_shortcut = QShortcut(QKeySequence("E"), self)
        edge_shortcut.activated.connect(
            lambda: self.state.edit_mode_manager.set_mode(EditMode.EDGE)
        )

        # V = Vertex mode
        vertex_shortcut = QShortcut(QKeySequence("V"), self)
        vertex_shortcut.activated.connect(
            lambda: self.state.edit_mode_manager.set_mode(EditMode.VERTEX)
        )

        self.log_debug("⌨️ Edit mode shortcuts: S=Solid | P=Panel | E=Edge | V=Vertex")

    # NOTE: create_analysis_toolbar and create_dock_widgets are no longer needed in v2.0
    # These are retained but not called for backward compatibility

    def save_layout(self):
        """Save window layout"""
        settings = QSettings("ComputationalCeramics", "CeramicMoldAnalyzer")
        settings.setValue("geometry", self.saveGeometry())
        # Tab state saving could be added here
        self.log_debug("💾 Layout saved")

    def restore_layout(self):
        """Restore window layout"""
        settings = QSettings("ComputationalCeramics", "CeramicMoldAnalyzer")
        geometry = settings.value("geometry")

        if geometry:
            self.restoreGeometry(geometry)
            self.log_debug("📂 Layout restored")

    def create_control_panel(self):
        """Create the right control panel"""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        
        # Mathematical Lens Selection
        lens_group = QGroupBox("Mathematical Lens")
        lens_layout = QVBoxLayout()
        
        self.lens_buttons = QButtonGroup()
        lenses = ["Flow (Geodesic)", "Spectral (Vibration)", 
                  "Curvature (Ridge/Valley)", "Topological"]
        
        for i, lens in enumerate(lenses):
            radio = QRadioButton(lens)
            if i == 0:
                radio.setChecked(True)
            self.lens_buttons.addButton(radio, i)
            lens_layout.addWidget(radio)
        
        analyze_btn = QPushButton("Analyze")
        analyze_btn.clicked.connect(self.run_current_analysis)
        lens_layout.addWidget(analyze_btn)
        
        lens_group.setLayout(lens_layout)
        layout.addWidget(lens_group)
        
        # Discovered Regions
        regions_group = QGroupBox("Discovered Regions")
        regions_layout = QVBoxLayout()
        
        self.region_list = RegionListWidget()
        regions_layout.addWidget(self.region_list)
        
        regions_group.setLayout(regions_layout)
        layout.addWidget(regions_group)
        
        # Constraints
        constraints_group = QGroupBox("Constraints")
        constraints_layout = QVBoxLayout()
        
        self.constraint_panel = ConstraintPanel()
        constraints_layout.addWidget(self.constraint_panel)
        
        constraints_group.setLayout(constraints_layout)
        layout.addWidget(constraints_group)

        # Debug Console (for development)
        debug_group = QGroupBox("Debug Console")
        debug_layout = QVBoxLayout()

        self.debug_console = QTextEdit()
        self.debug_console.setReadOnly(True)
        self.debug_console.setMaximumHeight(120)
        self.debug_console.setStyleSheet("font-family: monospace; font-size: 10px; background-color: #1E1E1E; color: #D4D4D4;")
        debug_layout.addWidget(self.debug_console)

        # Test button to verify console works
        test_btn = QPushButton("Test Debug")
        test_btn.clicked.connect(lambda: self.log_debug("✅ Debug console is working!"))
        debug_layout.addWidget(test_btn)

        debug_group.setLayout(debug_layout)
        layout.addWidget(debug_group)

        # Action buttons
        button_layout = QHBoxLayout()

        self.generate_btn = QPushButton("🔨 Generate Molds")
        self.generate_btn.clicked.connect(self.generate_molds)
        self.generate_btn.setEnabled(False)

        self.send_btn = QPushButton("📤 Send to Rhino")
        self.send_btn.clicked.connect(self.send_to_rhino)
        self.send_btn.setEnabled(False)

        button_layout.addWidget(self.generate_btn)
        button_layout.addWidget(self.send_btn)

        layout.addLayout(button_layout)
        layout.addStretch()

        return panel

    def _buffer_debug_message(self, message):
        """Buffer debug messages before console exists"""
        if self._debug_buffer is not None:
            self._debug_buffer.append(message)
        else:
            self.log_debug(message)

    def log_debug(self, message):
        """Add message to debug console"""
        if hasattr(self, 'debug_console') and self.debug_console:
            self.debug_console.append(message)
            # Auto-scroll to bottom
            self.debug_console.moveCursor(QTextCursor.MoveOperation.End)
    
    def setup_connections(self):
        """Setup signal/slot connections for v2.0 UI"""
        # Analysis panel connections (in ANALYZE tab)
        if hasattr(self, 'analysis_panel'):
            # The signals might not exist in AnalysisPanel yet, wrap in try-except
            try:
                self.analysis_panel.analysis_requested.connect(self.run_analysis)
                self.analysis_panel.lens_changed.connect(self.on_lens_changed)
            except:
                pass

        # Region list connections (in right panel)
        if hasattr(self, 'region_list'):
            try:
                self.region_list.region_selected.connect(self.on_region_selected)
                self.region_list.region_pinned.connect(self.on_region_pinned)
                self.region_list.region_edit_requested.connect(self.on_region_edit)
                self.region_list.region_properties_requested.connect(self.on_region_properties)
            except:
                pass

        # Viewport connections
        if hasattr(self, 'viewport_layout'):
            self.viewport_layout.active_viewport_changed.connect(self.on_active_viewport_changed)

        # Edit mode connections (in EDIT tab)
        if hasattr(self, 'edit_mode_widget'):
            try:
                # Connect to state manager
                self.state.edit_mode_changed.connect(self.on_edit_mode_changed)
                self.state.selection_changed.connect(self.on_selection_changed)
            except:
                pass

        # Selection info panel connections (in right panel)
        if hasattr(self, 'selection_info_panel'):
            try:
                self.selection_info_panel.export_to_region_requested.connect(self.export_selection_to_region)
            except:
                pass

        # Bridge connections
        self.rhino_bridge.geometry_received.connect(self.on_geometry_received)
        self.rhino_bridge.connection_status_changed.connect(self.on_connection_changed)

        # Geometry receiver connection (manual push from Grasshopper)
        self.geometry_receiver.geometry_received.connect(self.on_geometry_pushed)

        # State connections
        self.state.regions_updated.connect(self.on_regions_updated)
    
    def connect_to_rhino(self):
        """Connect to Rhino via HTTP bridge"""
        self.status_bar.showMessage("Connecting to Rhino...")
        
        success = self.rhino_bridge.connect()
        if success:
            self.connection_indicator.setText("● Connected")
            self.connection_indicator.setStyleSheet("color: #34C759;")
            self.status_bar.showMessage("Connected to Rhino (manual push mode)", 3000)

            # Manual push mode - no automatic fetching
            # Geometry will arrive when you click the button in Grasshopper
            self.log_debug("✅ Connected to Grasshopper - waiting for manual push")
            self.log_debug("📤 Click the button in Grasshopper to send geometry")
        else:
            # Server not running
            self.connection_indicator.setText("● Disconnected")
            self.connection_indicator.setStyleSheet("color: #FF3B30;")
            self.status_bar.showMessage("Could not connect to Rhino HTTP server", 3000)

            QMessageBox.information(
                self,
                "Rhino Connection",
                "To connect to Rhino:\n\n"
                "1. Open Rhino 8 with your SubD model\n"
                "2. Open Grasshopper\n"
                "3. Create a GhPython component\n"
                "4. Load 'grasshopper_http_server.py' from rhino/ folder\n"
                "5. Connect your SubD to the 'subd' input\n"
                "6. The server will start on port 8888\n"
                "7. Click 'Connect to Rhino' again\n\n"
                "The connection maintains EXACT SubD representation\n"
                "(Lossless Until Fabrication principle)"
            )

    def load_from_rhino(self):
        """Load SubD geometry from Grasshopper server."""
        # Check server availability
        if not self.subd_fetcher.is_server_available():
            print("❌ Grasshopper server not available on localhost:8888")
            print("   Start server in Grasshopper first")
            self.log_debug("❌ Grasshopper server not available on localhost:8888")
            self.log_debug("   Start server in Grasshopper first (Agent 6)")
            return

        # Fetch control cage
        cage = self.subd_fetcher.fetch_control_cage()
        if cage is None:
            print("❌ Failed to fetch geometry from Rhino")
            self.log_debug("❌ Failed to fetch geometry from Rhino")
            return

        self.current_cage = cage

        # Initialize evaluator
        self.subd_evaluator.initialize(cage)

        # Tessellate for display
        print(f"Tessellating {cage.vertex_count()} control vertices...")
        self.log_debug(f"🔄 Tessellating {cage.vertex_count()} control vertices...")
        result = self.subd_evaluator.tessellate(subdivision_level=3)

        print(f"✅ Generated {result.vertex_count()} vertices, "
              f"{result.triangle_count()} triangles")
        self.log_debug(f"✅ Generated {result.vertex_count()} vertices, "
                      f"{result.triangle_count()} triangles")

        # Display in viewport
        self.display_tessellation(result, cage)

    def display_tessellation(self, result, cage):
        """Display tessellated SubD in viewport."""
        # Get first viewport
        viewport = self.viewport_layout.viewports[0]

        # Clear existing geometry
        viewport.renderer.RemoveAllViewProps()

        # Create mesh actor
        mesh_actor = SubDDisplayManager.create_mesh_actor(
            result,
            color=(0.7, 0.8, 0.9),
            show_edges=True
        )
        viewport.renderer.AddActor(mesh_actor)

        # Create control cage actor (optional)
        # cage_actor = SubDDisplayManager.create_control_cage_actor(
        #     cage,
        #     color=(1.0, 0.0, 0.0)
        # )
        # viewport.renderer.AddActor(cage_actor)

        # Reset camera to fit
        viewport.renderer.ResetCamera()

        # Refresh
        viewport.render_window.Render()

        print("✅ Geometry displayed in viewport")
        self.log_debug("✅ Geometry displayed in viewport")

    def start_live_sync(self):
        """Start live synchronization with Grasshopper."""
        if self.live_bridge.start():
            self.log_debug("✅ Live sync enabled")
        else:
            self.log_debug("❌ Failed to start live sync")

    def stop_live_sync(self):
        """Stop live synchronization."""
        self.live_bridge.stop()
        self.log_debug("🛑 Live sync stopped")

    def force_refresh(self):
        """Force geometry refresh."""
        self.log_debug("🔄 Forcing refresh...")
        self.live_bridge.force_update()

    def on_geometry_updated(self, cage):
        """Called when geometry changes in Grasshopper.

        Args:
            cage: Updated SubD control cage
        """
        self.log_debug(f"📥 Received updated geometry: "
                      f"{cage.vertex_count()} vertices, {cage.face_count()} faces")

        self.current_cage = cage

        # Re-initialize evaluator
        self.subd_evaluator.initialize(cage)

        # Re-tessellate
        result = self.subd_evaluator.tessellate(subdivision_level=3)

        # Update display
        self.display_tessellation(result, cage)

        self.log_debug("✅ Display updated")

    def show_test_cube(self):
        """Show test cube in all viewports"""
        for viewport in self.viewport_layout.viewports:
            viewport.create_test_cube()
        self.status_bar.showMessage("Test cube displayed - LEFT to select | RIGHT/MIDDLE to rotate | Shift+RIGHT to pan | Wheel to zoom", 5000)

    def show_test_subd_sphere(self):
        """Show test SubD sphere in all viewports"""
        # TODO: rhino3dm 8.17.0 API changed - need to update SubD creation
        self.log_debug("⚠️ Test SubD geometry creation needs updating for rhino3dm 8.17.0")
        self.status_bar.showMessage("Test SubD geometry temporarily disabled (API update needed)", 3000)
        # for viewport in self.viewport_layout.viewports:
        #     viewport.create_test_subd_sphere()

    def show_test_subd_torus(self):
        """Show test SubD torus in all viewports"""
        # TODO: rhino3dm 8.17.0 API changed - need to update SubD creation
        self.log_debug("⚠️ Test SubD geometry creation needs updating for rhino3dm 8.17.0")
        self.status_bar.showMessage("Test SubD geometry temporarily disabled (API update needed)", 3000)
        # for viewport in self.viewport_layout.viewports:
        #     viewport.create_test_subd_torus()

    def show_test_colored_cube(self):
        """Show colored cube demonstrating region visualization in all viewports"""
        for viewport in self.viewport_layout.viewports:
            viewport.create_test_colored_cube()
        self.status_bar.showMessage("Colored cube displayed - 6 regions with distinct colors (simulating mathematical decomposition)", 5000)

    def check_rhino_updates(self):
        """Check for updates from Rhino"""
        if self.rhino_bridge.is_connected():
            self.rhino_bridge.check_for_updates()
    
    def on_geometry_received(self, geometry):
        """Handle EXACT SubD geometry received from Rhino"""
        self.status_bar.showMessage(f"SubD received: {geometry.vertex_count} vertices, {geometry.face_count} faces")
        self.state.set_subd_geometry(geometry)

        # Display in all viewports
        self.viewport_layout.display_geometry(geometry)

    def on_geometry_pushed(self, geometry_data):
        """Handle geometry PUSHED from Grasshopper (manual mode)"""
        self.log_debug(f"📥 Geometry pushed from Grasshopper")

        # Convert to SubDGeometry via bridge
        geometry = self.rhino_bridge.receive_geometry(geometry_data)

        if geometry:
            self.on_geometry_received(geometry)

    def on_connection_changed(self, is_connected):
        """Handle connection status change"""
        if is_connected:
            self.connection_indicator.setText("● Connected")
            self.connection_indicator.setStyleSheet("color: #34C759;")
        else:
            self.connection_indicator.setText("● Disconnected")
            self.connection_indicator.setStyleSheet("color: #FF3B30;")
    
    def run_analysis(self, lens_type):
        """Run analysis with specified lens"""
        self.status_bar.showMessage(f"Running {lens_type} analysis...")
        self.state.set_current_lens(lens_type)

        # Get current geometry
        geometry = self.state.get_current_geometry()

        if not geometry or not geometry.mesh_data:
            # No geometry loaded - use test geometry for development
            self.log_debug("⚠️ No geometry loaded - using test sphere for analysis")
            from app.geometry.test_meshes import create_sphere_mesh
            vertices, faces = create_sphere_mesh(radius=1.0, subdivisions=3)
        else:
            # Use actual geometry from Rhino
            self.log_debug("✅ Using geometry from Rhino")
            vertices = np.array(geometry.mesh_data['vertices'])
            faces = np.array(geometry.mesh_data['faces'])

        # Run actual differential decomposition
        if lens_type.lower() == "curvature":
            from app.analysis.differential_decomposition import DifferentialDecomposition

            self.log_debug(f"🔍 Running Differential Decomposition on {len(faces)} faces...")

            engine = DifferentialDecomposition()
            pinned_faces = self.state.get_pinned_face_indices()

            try:
                regions = engine.analyze(vertices, faces, pinned_faces)

                # Update state
                self.state.set_regions(regions)

                self.log_debug(f"✅ Discovered {len(regions)} regions")
                for region in regions:
                    self.log_debug(f"   • {region.id}: {region.unity_principle} (strength: {region.unity_strength:.2f})")

                self.status_bar.showMessage(f"Discovered {len(regions)} regions", 3000)
                self.generate_btn.setEnabled(True)

            except Exception as e:
                self.log_debug(f"❌ Analysis failed: {e}")
                import traceback
                traceback.print_exc()
                self.status_bar.showMessage(f"Analysis failed: {e}", 5000)

        else:
            # Other lenses not yet implemented
            self.log_debug(f"⚠️ {lens_type} lens not yet implemented - showing placeholder")

            # Simulate discovering regions (placeholder for other lenses)
            regions = []
            for i in range(4):
                region = ParametricRegion(
                    id=f"{lens_type.lower()}_region_{i+1}",
                    faces=list(range(i*10, (i+1)*10)),  # Fake face indices
                    unity_principle=f"{lens_type} coherence (placeholder)",
                    unity_strength=0.6 + i * 0.1,
                    pinned=False
                )
                regions.append(region)

            # Update state
            self.state.set_regions(regions)

            self.status_bar.showMessage(f"Discovered {len(regions)} placeholder regions", 3000)
            self.generate_btn.setEnabled(True)
    
    def run_current_analysis(self):
        """Run analysis with currently selected lens"""
        selected = self.lens_buttons.checkedButton()
        if selected:
            lens_name = selected.text().split(" ")[0]
            self.run_analysis(lens_name)
    
    def on_regions_updated(self, regions):
        """Handle regions update from state"""
        self.region_list.set_regions(regions)
        self.viewport_layout.display_regions(regions)

    def on_lens_changed(self, lens_type):
        """Handle lens selection change from analysis panel"""
        self.state.set_current_lens(lens_type)
        self.log_debug(f"🔍 Lens changed to: {lens_type}")
    
    def on_region_selected(self, region_id):
        """Handle region selection"""
        self.state.select_region(region_id)
        region = self.state.get_region(region_id)
        
        if region:
            self.viewport.highlight_region(region_id)
            self.constraint_panel.show_constraints_for_region(region)
            self.status_bar.showMessage(f"Selected: {region_id}")
    
    def on_region_pinned(self, region_id, is_pinned):
        """Handle region pinning"""
        self.state.set_region_pinned(region_id, is_pinned)
        self.viewport.update_region_display(region_id, pinned=is_pinned)
        
        action = "Pinned" if is_pinned else "Unpinned"
        self.status_bar.showMessage(f"{action} {region_id}", 2000)
    
    def on_region_edit(self, region_id):
        """Handle region edit request"""
        active_viewport = self.viewport_layout.get_active_viewport()
        if active_viewport:
            active_viewport.enable_boundary_editing(region_id)
        self.status_bar.showMessage(f"Editing boundary of {region_id}")

    def on_region_properties(self, region_id):
        """Handle region properties dialog request"""
        region = self.state.get_region(region_id)
        if region:
            # Create and show properties dialog
            dialog = RegionPropertiesDialog(region, self)

            # Connect dialog signals
            dialog.properties_changed.connect(self.on_region_properties_changed)

            # Show dialog modally
            dialog.exec()

    def on_region_properties_changed(self, region_id, updated_properties):
        """Handle changes from properties dialog"""
        # Apply changes through state manager
        if 'pinned' in updated_properties:
            self.state.set_region_pinned(region_id, updated_properties['pinned'])

        # Update region list display
        self.region_list.set_regions(self.state.regions)

        # Update viewport display
        active_viewport = self.viewport_layout.get_active_viewport()
        if active_viewport:
            active_viewport.update_region_display(region_id)

        self.status_bar.showMessage(f"Updated properties for {region_id}", 2000)

    def on_viewport_region_clicked(self, region_id):
        """Handle region click in viewport"""
        self.region_list.select_region(region_id)

    def on_active_viewport_changed(self, viewport_index):
        """Handle active viewport change"""
        self.status_bar.showMessage(f"Active viewport: {viewport_index + 1}", 2000)

    def on_edit_mode_changed(self, mode: EditMode):
        """Handle edit mode change"""
        # Update state
        self.state.edit_mode_manager.set_mode(mode)

        # Update toolbar if not originating from there
        if self.sender() != self.edit_mode_toolbar:
            self.edit_mode_toolbar.set_mode(mode)

        # Update status bar
        mode_name = mode.get_display_name()
        self.status_bar.showMessage(f"Edit Mode: {mode_name}", 3000)
        self.log_debug(f"📝 Edit mode changed to: {mode_name}")

        # Update viewports
        for viewport in self.viewport_layout.viewports:
            viewport.set_edit_mode(mode)

    def on_selection_changed(self, selection):
        """Handle selection change"""
        info = self.state.edit_mode_manager.get_selection_info()
        self.edit_mode_toolbar.update_selection_info(info)

        # Update selection info panel
        self.selection_info_panel.update_selection(selection)

        # Update viewports with selection
        for viewport in self.viewport_layout.viewports:
            viewport.update_selection(selection)

    def clear_selection(self):
        """Clear current selection"""
        self.state.edit_mode_manager.clear_selection()
        # Clear visual selection in viewports
        self.viewport_layout.clear_selection()
        self.log_debug("🔄 Selection cleared")

    def select_all(self):
        """Select all elements in current mode"""
        # TODO: Implement when we have actual geometry
        self.log_debug("⚠️ Select All not yet implemented (requires geometry)")
        self.status_bar.showMessage("Select All requires SubD geometry", 2000)

    def invert_selection(self):
        """Invert current selection"""
        # TODO: Implement when we have actual geometry
        self.log_debug("⚠️ Invert Selection not yet implemented (requires geometry)")
        self.status_bar.showMessage("Invert Selection requires SubD geometry", 2000)

    def grow_selection(self):
        """Grow selection to topological neighbors"""
        # TODO: Implement when we have actual geometry with topology
        self.log_debug("⚠️ Grow Selection not yet implemented (requires topology)")
        self.status_bar.showMessage("Grow Selection requires SubD topology", 2000)

    def shrink_selection(self):
        """Shrink selection by removing boundary elements"""
        # TODO: Implement when we have actual geometry with topology
        self.log_debug("⚠️ Shrink Selection not yet implemented (requires topology)")
        self.status_bar.showMessage("Shrink Selection requires SubD topology", 2000)

    def export_selection_to_region(self):
        """Export selected faces to a new parametric region"""
        face_indices = self.state.edit_mode_manager.create_region_from_selection()

        if face_indices:
            # Create a new region from selected faces
            region = ParametricRegion(
                id=f"user_region_{len(self.state.regions) + 1}",
                faces=face_indices,
                unity_principle="User-defined region",
                unity_strength=1.0,
                pinned=True
            )
            self.state.add_region(region)
            self.log_debug(f"✅ Created region from {len(face_indices)} selected faces")
            self.status_bar.showMessage(f"Created region with {len(face_indices)} faces", 3000)
        else:
            self.log_debug("⚠️ No faces selected - select faces in Panel mode first")
            self.status_bar.showMessage("Select faces in Panel mode to export", 2000)

    def generate_molds(self):
        """Generate mold geometry"""
        self.status_bar.showMessage("Generating mold geometry...")
        
        QMessageBox.information(
            self,
            "Generate Molds",
            "Mold generation will:\n\n"
            "• Apply draft angles (2°)\n"
            "• Add wall thickness (3.5mm ceramic, 45mm plaster)\n"
            "• Create registration keys\n"
            "• Validate all constraints\n\n"
            f"Generating molds for {len(self.state.regions)} regions.\n\n"
            "This feature is in development."
        )
        
        self.send_btn.setEnabled(True)
    
    def send_to_rhino(self):
        """Send molds to Rhino"""
        self.status_bar.showMessage("Sending to Rhino...")
        
        # This will use the bridge when implemented
        success = self.rhino_bridge.send_molds([])
        
        if not success:
            QMessageBox.information(
                self,
                "Send to Rhino",
                "Mold geometry will be sent to Rhino.\n\n"
                "The molds will appear in your viewport,\n"
                "ready for 3D printing preparation.\n\n"
                "This feature is in development."
            )
    
    def save_session(self):
        """Save current session"""
        # Save window layout
        self.save_layout()

        # TODO: Save session data (regions, pin states, etc.)
        QMessageBox.information(
            self,
            "Save Session",
            "Window layout saved!\n\n"
            "Session data saving (regions, pin states, etc.)\n"
            "will be implemented in the future."
        )
    
    def undo(self):
        """Undo last action"""
        if self.state.can_undo():
            self.state.undo()
            self.status_bar.showMessage("Undone", 2000)
            
            # Refresh UI
            self.region_list.set_regions(self.state.regions)
        else:
            self.status_bar.showMessage("Nothing to undo", 2000)
    
    def redo(self):
        """Redo last undone action"""
        if self.state.can_redo():
            self.state.redo()
            self.status_bar.showMessage("Redone", 2000)
            
            # Refresh UI
            self.region_list.set_regions(self.state.regions)
        else:
            self.status_bar.showMessage("Nothing to redo", 2000)
    
    def show_about(self):
        """Show about dialog"""
        QMessageBox.about(
            self,
            "About Ceramic Mold Analyzer",
            "Ceramic Mold Analyzer\nVersion 0.1.0\n\n"
            "A tool for discovering natural mathematical decompositions "
            "of SubD surfaces for ceramic slip-casting molds.\n\n"
            "Every form contains inherent mathematical coherences.\n"
            "This tool reveals them through different analytical lenses,\n"
            "creating a dialogue between mathematics and material.\n\n"
            "Inspired by Peter Pincus, who showed us that\n"
            "seams are not flaws to hide but truths to celebrate.\n\n"
            "© 2025 - Built with passion for ceramic art"
        )
    
    def closeEvent(self, event):
        """Handle window close"""
        # Save layout before closing
        self.save_layout()

        # Stop live bridge
        if hasattr(self, 'live_bridge'):
            self.live_bridge.stop()

        # Stop geometry receiver
        if hasattr(self, 'geometry_receiver'):
            self.geometry_receiver.stop()

        # Disconnect from Rhino
        if hasattr(self, 'rhino_bridge'):
            self.rhino_bridge.disconnect()

        event.accept()


def main():
    """Main entry point"""
    app = QApplication(sys.argv)
    app.setStyle("Fusion")  # Modern look
    
    # Set application metadata
    app.setApplicationName("Ceramic Mold Analyzer")
    app.setOrganizationName("Computational Ceramics")
    
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
