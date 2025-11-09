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
    QDockWidget, QToolBar
)
from PyQt6.QtCore import Qt, QTimer, QSettings
from PyQt6.QtGui import QAction, QTextCursor, QShortcut, QKeySequence

# Add app directory to path
sys.path.insert(0, str(Path(__file__).parent))

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
        """Initialize the user interface"""
        self.setWindowTitle("Ceramic Mold Analyzer - v0.1.0")
        self.setGeometry(100, 100, 1400, 900)

        # Create edit mode toolbar
        self.edit_mode_toolbar = EditModeToolBar(self)
        self.addToolBar(Qt.ToolBarArea.TopToolBarArea, self.edit_mode_toolbar)

        # Setup keyboard shortcuts for edit modes
        self.setup_edit_mode_shortcuts()

        # Create analysis toolbar
        self.create_analysis_toolbar()

        # Create central widget - Viewport Layout
        self.viewport_layout = ViewportLayoutManager()
        self.setCentralWidget(self.viewport_layout)

        # Store reference to primary viewport for compatibility
        self.viewport = None

        # Create dockable panels
        self.create_dock_widgets()

        # Status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)

        # Connection status widget (LiveBridge monitoring)
        self.status_widget = ConnectionStatusWidget(self.live_bridge)
        self.status_bar.addPermanentWidget(self.status_widget)

        # Keep old connection_indicator for compatibility with old code
        self.connection_indicator = QLabel("● Disconnected")
        self.connection_indicator.setStyleSheet("color: #FF3B30;")
        # Don't add to status bar, just keep reference

        self.status_bar.showMessage("Ready. Connect to Rhino to begin.")

        # Create menus (after viewport is created)
        self.create_menus()

        # Restore previous layout if exists
        self.restore_layout()
        
    def create_menus(self):
        """Create application menus"""
        menubar = self.menuBar()

        # File menu
        file_menu = menubar.addMenu("File")

        # Load from Rhino (C++ SubD pipeline)
        load_rhino = QAction("Load from &Rhino", self)
        load_rhino.setShortcut("Ctrl+R")
        load_rhino.triggered.connect(self.load_from_rhino)
        file_menu.addAction(load_rhino)

        # Start live sync
        start_sync = QAction("Start &Live Sync", self)
        start_sync.setShortcut("Ctrl+L")
        start_sync.triggered.connect(self.start_live_sync)
        file_menu.addAction(start_sync)

        # Stop live sync
        stop_sync = QAction("Stop Live Sync", self)
        stop_sync.triggered.connect(self.stop_live_sync)
        file_menu.addAction(stop_sync)

        file_menu.addSeparator()

        # Force refresh
        refresh = QAction("&Refresh", self)
        refresh.setShortcut("F5")
        refresh.triggered.connect(self.force_refresh)
        file_menu.addAction(refresh)

        file_menu.addSeparator()

        connect_action = QAction("Connect to Rhino", self)
        connect_action.setShortcut("Ctrl+O")
        connect_action.triggered.connect(self.connect_to_rhino)
        file_menu.addAction(connect_action)

        file_menu.addSeparator()
        
        save_action = QAction("Save Session", self)
        save_action.setShortcut("Ctrl+S")
        save_action.triggered.connect(self.save_session)
        file_menu.addAction(save_action)
        
        file_menu.addSeparator()
        
        quit_action = QAction("Quit", self)
        quit_action.setShortcut("Ctrl+Q")
        quit_action.triggered.connect(self.close)
        file_menu.addAction(quit_action)
        
        # Edit menu
        edit_menu = menubar.addMenu("Edit")
        
        undo_action = QAction("Undo", self)
        undo_action.setShortcut("Ctrl+Z")
        undo_action.triggered.connect(self.undo)
        edit_menu.addAction(undo_action)
        
        redo_action = QAction("Redo", self)
        redo_action.setShortcut("Ctrl+Shift+Z")
        redo_action.triggered.connect(self.redo)
        edit_menu.addAction(redo_action)

        edit_menu.addSeparator()

        # Selection operations
        clear_sel_action = QAction("Clear Selection", self)
        clear_sel_action.setShortcut("Esc")
        clear_sel_action.triggered.connect(self.clear_selection)
        edit_menu.addAction(clear_sel_action)

        select_all_action = QAction("Select All", self)
        select_all_action.setShortcut("Ctrl+A")
        select_all_action.triggered.connect(self.select_all)
        edit_menu.addAction(select_all_action)

        invert_sel_action = QAction("Invert Selection", self)
        invert_sel_action.setShortcut("Ctrl+I")
        invert_sel_action.triggered.connect(self.invert_selection)
        edit_menu.addAction(invert_sel_action)

        edit_menu.addSeparator()

        grow_sel_action = QAction("Grow Selection", self)
        grow_sel_action.setShortcut("Ctrl+>")
        grow_sel_action.triggered.connect(self.grow_selection)
        edit_menu.addAction(grow_sel_action)

        shrink_sel_action = QAction("Shrink Selection", self)
        shrink_sel_action.setShortcut("Ctrl+<")
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

        layout_single = QAction("Single", self)
        layout_single.setShortcut("Alt+1")
        layout_single.triggered.connect(lambda: self.viewport_layout.set_layout(ViewportLayout.SINGLE))
        layout_menu.addAction(layout_single)

        layout_2h = QAction("Two Horizontal", self)
        layout_2h.setShortcut("Alt+2")
        layout_2h.triggered.connect(lambda: self.viewport_layout.set_layout(ViewportLayout.TWO_HORIZONTAL))
        layout_menu.addAction(layout_2h)

        layout_2v = QAction("Two Vertical", self)
        layout_2v.setShortcut("Alt+3")
        layout_2v.triggered.connect(lambda: self.viewport_layout.set_layout(ViewportLayout.TWO_VERTICAL))
        layout_menu.addAction(layout_2v)

        layout_4grid = QAction("Four Grid", self)
        layout_4grid.setShortcut("Alt+4")
        layout_4grid.triggered.connect(lambda: self.viewport_layout.set_layout(ViewportLayout.FOUR_GRID))
        layout_menu.addAction(layout_4grid)

        view_menu.addSeparator()

        reset_view = QAction("Reset All Cameras", self)
        reset_view.setShortcut("Space")
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

    def create_analysis_toolbar(self):
        """Create analysis toolbar with quick actions"""
        toolbar = QToolBar("Analysis Tools")
        toolbar.setMovable(True)
        toolbar.setFloatable(False)
        self.addToolBar(Qt.ToolBarArea.TopToolBarArea, toolbar)

        # Quick lens selection buttons
        toolbar.addWidget(QLabel("Quick Lens: "))
        toolbar.addSeparator()

        flow_action = QAction("🌊 Flow", self)
        flow_action.setToolTip("Run Flow (Geodesic) analysis")
        flow_action.triggered.connect(lambda: self.run_analysis("Flow"))
        toolbar.addAction(flow_action)

        spectral_action = QAction("〰️ Spectral", self)
        spectral_action.setToolTip("Run Spectral (Vibration) analysis")
        spectral_action.triggered.connect(lambda: self.run_analysis("Spectral"))
        toolbar.addAction(spectral_action)

        curvature_action = QAction("📐 Curvature", self)
        curvature_action.setToolTip("Run Curvature (Ridge/Valley) analysis")
        curvature_action.triggered.connect(lambda: self.run_analysis("Curvature"))
        toolbar.addAction(curvature_action)

        topo_action = QAction("🔷 Topological", self)
        topo_action.setToolTip("Run Topological analysis")
        topo_action.triggered.connect(lambda: self.run_analysis("Topological"))
        toolbar.addAction(topo_action)

        toolbar.addSeparator()

        # Mold generation
        generate_action = QAction("🔨 Generate Molds", self)
        generate_action.setToolTip("Generate mold geometry from pinned regions")
        generate_action.triggered.connect(self.generate_molds)
        toolbar.addAction(generate_action)
        self.toolbar_generate_action = generate_action

        # Send to Rhino
        send_action = QAction("📤 Send to Rhino", self)
        send_action.setToolTip("Send generated molds to Rhino")
        send_action.triggered.connect(self.send_to_rhino)
        toolbar.addAction(send_action)
        self.toolbar_send_action = send_action

        self.analysis_toolbar = toolbar

    def create_dock_widgets(self):
        """Create dockable panels for UI components"""
        # Analysis Panel (right side, top)
        self.analysis_panel = AnalysisPanel()
        analysis_dock = QDockWidget("Analysis", self)
        analysis_dock.setWidget(self.analysis_panel)
        analysis_dock.setAllowedAreas(Qt.DockWidgetArea.LeftDockWidgetArea |
                                       Qt.DockWidgetArea.RightDockWidgetArea)
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, analysis_dock)
        self.analysis_dock = analysis_dock

        # Region List Panel (right side, middle)
        self.region_list = RegionListWidget()
        region_dock = QDockWidget("Regions", self)
        region_dock.setWidget(self.region_list)
        region_dock.setAllowedAreas(Qt.DockWidgetArea.LeftDockWidgetArea |
                                     Qt.DockWidgetArea.RightDockWidgetArea)
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, region_dock)
        self.region_dock = region_dock

        # Constraint Panel (right side, below regions)
        self.constraint_panel = ConstraintPanel()
        constraint_dock = QDockWidget("Constraints", self)
        constraint_dock.setWidget(self.constraint_panel)
        constraint_dock.setAllowedAreas(Qt.DockWidgetArea.LeftDockWidgetArea |
                                         Qt.DockWidgetArea.RightDockWidgetArea |
                                         Qt.DockWidgetArea.BottomDockWidgetArea)
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, constraint_dock)
        self.constraint_dock = constraint_dock

        # Selection Info Panel (right side, bottom)
        self.selection_info_panel = SelectionInfoPanel()
        selection_dock = QDockWidget("Selection Info", self)
        selection_dock.setWidget(self.selection_info_panel)
        selection_dock.setAllowedAreas(Qt.DockWidgetArea.LeftDockWidgetArea |
                                        Qt.DockWidgetArea.RightDockWidgetArea |
                                        Qt.DockWidgetArea.BottomDockWidgetArea)
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, selection_dock)
        self.selection_dock = selection_dock

        # Debug Console (bottom)
        debug_widget = QWidget()
        debug_layout = QVBoxLayout(debug_widget)
        debug_layout.setContentsMargins(5, 5, 5, 5)

        self.debug_console = QTextEdit()
        self.debug_console.setReadOnly(True)
        self.debug_console.setMaximumHeight(150)
        self.debug_console.setStyleSheet(
            "font-family: monospace; font-size: 10px; "
            "background-color: #1E1E1E; color: #D4D4D4;"
        )
        debug_layout.addWidget(self.debug_console)

        # Test button
        test_btn = QPushButton("Test Debug")
        test_btn.clicked.connect(lambda: self.log_debug("✅ Debug console is working!"))
        test_btn.setMaximumWidth(100)
        debug_layout.addWidget(test_btn)

        debug_dock = QDockWidget("Debug Console", self)
        debug_dock.setWidget(debug_widget)
        debug_dock.setAllowedAreas(Qt.DockWidgetArea.BottomDockWidgetArea |
                                    Qt.DockWidgetArea.LeftDockWidgetArea |
                                    Qt.DockWidgetArea.RightDockWidgetArea)
        self.addDockWidget(Qt.DockWidgetArea.BottomDockWidgetArea, debug_dock)
        self.debug_dock = debug_dock

        # Stack the right-side docks vertically
        self.tabifyDockWidget(constraint_dock, analysis_dock)
        self.tabifyDockWidget(constraint_dock, selection_dock)
        analysis_dock.raise_()  # Bring analysis to front

        # Add menu actions to show/hide docks
        self.add_dock_menu_actions()

    def add_dock_menu_actions(self):
        """Add menu actions for showing/hiding dock widgets"""
        # Add to View menu
        # Skip if menus not created yet
        if not self.menuBar().actions():
            return
        view_menu = self.menuBar().actions()[3].menu()  # View is 4th menu
        view_menu.addSeparator()

        # Add toggle actions for each dock
        view_menu.addAction(self.analysis_dock.toggleViewAction())
        view_menu.addAction(self.region_dock.toggleViewAction())
        view_menu.addAction(self.constraint_dock.toggleViewAction())
        view_menu.addAction(self.selection_dock.toggleViewAction())
        view_menu.addAction(self.debug_dock.toggleViewAction())

        view_menu.addSeparator()

        # Reset layout action
        reset_layout_action = QAction("Reset Panel Layout", self)
        reset_layout_action.triggered.connect(self.reset_panel_layout)
        view_menu.addAction(reset_layout_action)

    def reset_panel_layout(self):
        """Reset dock widget layout to default"""
        # Remove all docks
        self.removeDockWidget(self.analysis_dock)
        self.removeDockWidget(self.region_dock)
        self.removeDockWidget(self.constraint_dock)
        self.removeDockWidget(self.selection_dock)
        self.removeDockWidget(self.debug_dock)

        # Re-add in default positions
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, self.analysis_dock)
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, self.region_dock)
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, self.constraint_dock)
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, self.selection_dock)
        self.addDockWidget(Qt.DockWidgetArea.BottomDockWidgetArea, self.debug_dock)

        # Stack analysis, constraint, and selection
        self.tabifyDockWidget(self.constraint_dock, self.analysis_dock)
        self.tabifyDockWidget(self.constraint_dock, self.selection_dock)
        self.analysis_dock.raise_()

        # Show all docks
        self.analysis_dock.show()
        self.region_dock.show()
        self.constraint_dock.show()
        self.selection_dock.show()
        self.debug_dock.show()

        self.status_bar.showMessage("Panel layout reset to default", 2000)

    def save_layout(self):
        """Save window layout and dock positions"""
        settings = QSettings("ComputationalCeramics", "CeramicMoldAnalyzer")
        settings.setValue("geometry", self.saveGeometry())
        settings.setValue("windowState", self.saveState())
        self.log_debug("💾 Layout saved")

    def restore_layout(self):
        """Restore window layout and dock positions"""
        settings = QSettings("ComputationalCeramics", "CeramicMoldAnalyzer")
        geometry = settings.value("geometry")
        state = settings.value("windowState")

        if geometry:
            self.restoreGeometry(geometry)
        if state:
            self.restoreState(state)
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
        """Setup signal/slot connections"""
        # Analysis panel connections
        self.analysis_panel.analysis_requested.connect(self.run_analysis)
        self.analysis_panel.lens_changed.connect(self.on_lens_changed)

        # Region list connections
        self.region_list.region_selected.connect(self.on_region_selected)
        self.region_list.region_pinned.connect(self.on_region_pinned)
        self.region_list.region_edit_requested.connect(self.on_region_edit)
        self.region_list.region_properties_requested.connect(self.on_region_properties)

        # Viewport connections - connect signals for each viewport as they're created
        # These will be connected when viewports are created in the layout manager
        self.viewport_layout.active_viewport_changed.connect(self.on_active_viewport_changed)

        # Edit mode connections
        self.edit_mode_toolbar.mode_changed.connect(self.on_edit_mode_changed)
        self.state.edit_mode_changed.connect(self.on_edit_mode_changed)
        self.state.selection_changed.connect(self.on_selection_changed)

        # Edit mode toolbar selection operations
        self.edit_mode_toolbar.clear_selection_requested.connect(self.clear_selection)
        self.edit_mode_toolbar.select_all_requested.connect(self.select_all)
        self.edit_mode_toolbar.invert_selection_requested.connect(self.invert_selection)
        self.edit_mode_toolbar.grow_selection_requested.connect(self.grow_selection)
        self.edit_mode_toolbar.shrink_selection_requested.connect(self.shrink_selection)

        # Selection info panel connections
        self.selection_info_panel.export_to_region_requested.connect(self.export_selection_to_region)

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
