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
    QRadioButton, QButtonGroup, QMessageBox, QTextEdit
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QAction, QTextCursor

# Add app directory to path
sys.path.insert(0, str(Path(__file__).parent))

# Import our components
from app.ui.viewport_3d import Viewport3D
from app.ui.viewport_layout import ViewportLayoutManager, ViewportLayout, ViewType
from app.ui.region_list import RegionListWidget
from app.ui.constraint_panel import ConstraintPanel
from app.ui.edit_mode_toolbar import EditModeToolBar, EditModeWidget
from app.bridge.rhino_bridge import RhinoBridge
from app.bridge.geometry_receiver import GeometryReceiver
from app.state.app_state import ApplicationState, ParametricRegion
from app.state.edit_mode import EditMode


class MainWindow(QMainWindow):
    """Main application window for Ceramic Mold Analyzer"""
    
    def __init__(self):
        super().__init__()

        # Buffer for debug messages before console is created
        self._debug_buffer = []

        # Initialize state and bridge
        self.state = ApplicationState()
        self.rhino_bridge = RhinoBridge()

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
        self.addToolBar(self.edit_mode_toolbar)

        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Main layout with splitter
        main_layout = QHBoxLayout(central_widget)
        splitter = QSplitter(Qt.Orientation.Horizontal)
        main_layout.addWidget(splitter)

        # Left panel - Multi-Viewport Layout
        self.viewport_layout = ViewportLayoutManager()
        splitter.addWidget(self.viewport_layout)

        # Connect debug signals from all viewports (will be connected as they're created)
        # Store reference to primary viewport for compatibility
        self.viewport = None

        # Right panel - Controls
        right_panel = self.create_control_panel()
        splitter.addWidget(right_panel)

        # Set splitter sizes (70% viewport, 30% controls)
        splitter.setSizes([980, 420])

        # Status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)

        # Connection indicator
        self.connection_indicator = QLabel("● Disconnected")
        self.connection_indicator.setStyleSheet("color: #FF3B30;")
        self.status_bar.addPermanentWidget(self.connection_indicator)

        self.status_bar.showMessage("Ready. Connect to Rhino to begin.")

        # Create menus (after viewport is created)
        self.create_menus()
        
    def create_menus(self):
        """Create application menus"""
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu("File")
        
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
        self.debug_console.append(message)
        # Auto-scroll to bottom
        self.debug_console.moveCursor(QTextCursor.MoveOperation.End)
    
    def setup_connections(self):
        """Setup signal/slot connections"""
        # Region list connections
        self.region_list.region_selected.connect(self.on_region_selected)
        self.region_list.region_pinned.connect(self.on_region_pinned)
        self.region_list.region_edit_requested.connect(self.on_region_edit)

        # Viewport connections - connect signals for each viewport as they're created
        # These will be connected when viewports are created in the layout manager
        self.viewport_layout.active_viewport_changed.connect(self.on_active_viewport_changed)

        # Edit mode connections
        self.edit_mode_toolbar.mode_changed.connect(self.on_edit_mode_changed)
        self.state.edit_mode_changed.connect(self.on_edit_mode_changed)
        self.state.selection_changed.connect(self.on_selection_changed)

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

        # Update viewports with selection
        for viewport in self.viewport_layout.viewports:
            viewport.update_selection(selection)

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
        QMessageBox.information(
            self, 
            "Save Session", 
            "Session saving will be implemented.\n\n"
            "This will save:\n"
            "• Current regions\n"
            "• Pin states\n"
            "• Analysis settings\n"
            "• Generated molds"
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
