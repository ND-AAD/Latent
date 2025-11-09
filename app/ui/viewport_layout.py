"""
Multi-Viewport Layout Manager
Provides 1, 2H, 2V, and 4-grid viewport configurations matching Rhino's standard layouts
"""

from PyQt6.QtWidgets import QWidget, QSplitter, QVBoxLayout, QHBoxLayout
from PyQt6.QtCore import Qt, pyqtSignal
from enum import Enum
from typing import List, Optional

# Import VTK types from our bridge - DO NOT import vtk directly
from app import vtk_bridge as vtk

from app.ui.viewport_3d import Viewport3D


class ViewportLayout(Enum):
    """Standard viewport layout configurations"""
    SINGLE = "1"  # Single viewport
    TWO_HORIZONTAL = "2H"  # Two viewports split horizontally
    TWO_VERTICAL = "2V"  # Two viewports split vertically
    FOUR_GRID = "4"  # Four viewports in 2x2 grid


class ViewType(Enum):
    """Standard view types for viewports"""
    PERSPECTIVE = "Perspective"
    TOP = "Top"
    FRONT = "Front"
    RIGHT = "Right"
    BACK = "Back"
    LEFT = "Left"
    BOTTOM = "Bottom"
    ISOMETRIC = "Isometric"


class ViewportLayoutManager(QWidget):
    """
    Manages multiple viewport configurations
    Matches Rhino's standard viewport layouts
    """

    # Signals
    active_viewport_changed = pyqtSignal(int)  # Emits viewport index
    layout_changed = pyqtSignal(ViewportLayout)

    def __init__(self):
        super().__init__()

        # Viewport storage
        self.viewports: List[Viewport3D] = []
        self.active_viewport_index = 0

        # Layout configuration
        self.current_layout = ViewportLayout.FOUR_GRID

        # Main layout
        self.main_layout = QVBoxLayout()
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.main_layout)

        # Splitters for layout management
        self.main_splitter = None

        # Initialize with default layout
        self.set_layout(ViewportLayout.FOUR_GRID)

    def set_layout(self, layout: ViewportLayout):
        """
        Change the viewport layout configuration

        Args:
            layout: The desired viewport layout
        """
        # Store current geometry if any
        geometry_data = None
        if self.viewports and self.viewports[0].current_subd:
            geometry_data = self.viewports[0].current_subd

        # Clear existing viewports
        self._clear_viewports()

        # Create new layout
        self.current_layout = layout

        if layout == ViewportLayout.SINGLE:
            self._create_single_layout()
        elif layout == ViewportLayout.TWO_HORIZONTAL:
            self._create_two_horizontal_layout()
        elif layout == ViewportLayout.TWO_VERTICAL:
            self._create_two_vertical_layout()
        elif layout == ViewportLayout.FOUR_GRID:
            self._create_four_grid_layout()

        # Restore geometry to all viewports
        if geometry_data:
            for viewport in self.viewports:
                viewport.display_subd(geometry_data)

        # Set the first viewport as active
        if self.viewports:
            self.set_active_viewport(0)

        # Emit signal
        self.layout_changed.emit(layout)

    def _clear_viewports(self):
        """Clear all existing viewports and layout"""
        # Remove all viewports
        for viewport in self.viewports:
            viewport.setParent(None)
            viewport.deleteLater()
        self.viewports.clear()

        # Remove splitter
        if self.main_splitter:
            self.main_splitter.setParent(None)
            self.main_splitter.deleteLater()
            self.main_splitter = None

        # Clear layout
        while self.main_layout.count():
            item = self.main_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

    def _create_single_layout(self):
        """Create a single viewport layout"""
        viewport = self._create_viewport(ViewType.PERSPECTIVE)
        self.viewports = [viewport]
        self.main_layout.addWidget(viewport)

    def _create_two_horizontal_layout(self):
        """Create two viewports split horizontally (top and bottom)"""
        self.main_splitter = QSplitter(Qt.Orientation.Vertical)

        # Top viewport (Perspective)
        top_viewport = self._create_viewport(ViewType.PERSPECTIVE)
        self.main_splitter.addWidget(top_viewport)

        # Bottom viewport (Top view)
        bottom_viewport = self._create_viewport(ViewType.TOP)
        self.main_splitter.addWidget(bottom_viewport)

        self.viewports = [top_viewport, bottom_viewport]
        self.main_splitter.setSizes([400, 400])  # Equal sizes
        self.main_layout.addWidget(self.main_splitter)

    def _create_two_vertical_layout(self):
        """Create two viewports split vertically (side by side)"""
        self.main_splitter = QSplitter(Qt.Orientation.Horizontal)

        # Left viewport (Front view)
        left_viewport = self._create_viewport(ViewType.FRONT)
        self.main_splitter.addWidget(left_viewport)

        # Right viewport (Perspective)
        right_viewport = self._create_viewport(ViewType.PERSPECTIVE)
        self.main_splitter.addWidget(right_viewport)

        self.viewports = [left_viewport, right_viewport]
        self.main_splitter.setSizes([400, 400])  # Equal sizes
        self.main_layout.addWidget(self.main_splitter)

    def _create_four_grid_layout(self):
        """Create four viewports in a 2x2 grid (Rhino default)"""
        # Main vertical splitter
        self.main_splitter = QSplitter(Qt.Orientation.Vertical)

        # Top horizontal splitter
        top_splitter = QSplitter(Qt.Orientation.Horizontal)

        # Top-left: Top view
        tl_viewport = self._create_viewport(ViewType.TOP)
        top_splitter.addWidget(tl_viewport)

        # Top-right: Perspective
        tr_viewport = self._create_viewport(ViewType.PERSPECTIVE)
        top_splitter.addWidget(tr_viewport)

        # Bottom horizontal splitter
        bottom_splitter = QSplitter(Qt.Orientation.Horizontal)

        # Bottom-left: Front view
        bl_viewport = self._create_viewport(ViewType.FRONT)
        bottom_splitter.addWidget(bl_viewport)

        # Bottom-right: Right view
        br_viewport = self._create_viewport(ViewType.RIGHT)
        bottom_splitter.addWidget(br_viewport)

        # Add to main splitter
        self.main_splitter.addWidget(top_splitter)
        self.main_splitter.addWidget(bottom_splitter)

        # Store viewports in reading order
        self.viewports = [tl_viewport, tr_viewport, bl_viewport, br_viewport]

        # Set equal sizes
        self.main_splitter.setSizes([400, 400])
        top_splitter.setSizes([400, 400])
        bottom_splitter.setSizes([400, 400])

        self.main_layout.addWidget(self.main_splitter)

    def _create_viewport(self, view_type: ViewType) -> Viewport3D:
        """
        Create a new viewport with specified view type

        Args:
            view_type: The type of view for this viewport

        Returns:
            Configured Viewport3D instance
        """
        viewport = Viewport3D()

        # Set viewport type and label
        viewport.set_view_type(view_type)

        # Configure camera based on view type
        self._setup_viewport_camera(viewport, view_type)

        # Connect click signal
        original_mousePressEvent = viewport.mousePressEvent
        def handle_click(event):
            self._on_viewport_clicked(viewport, event)
            original_mousePressEvent(event)
        viewport.mousePressEvent = handle_click

        # Connect view change signal
        viewport.view_changed.connect(lambda view_name: self._on_view_change_requested(viewport, view_name))

        return viewport

    def _setup_viewport_camera(self, viewport: Viewport3D, view_type: ViewType):
        """
        Configure camera for specific view type

        Args:
            viewport: The viewport to configure
            view_type: The desired view type
        """
        if not viewport.renderer:
            return

        camera = viewport.renderer.GetActiveCamera()

        if view_type == ViewType.TOP:
            # Looking down Z axis
            camera.SetPosition(0, 0, 10)
            camera.SetFocalPoint(0, 0, 0)
            camera.SetViewUp(0, 1, 0)
            camera.ParallelProjectionOn()

        elif view_type == ViewType.FRONT:
            # Looking along Y axis
            camera.SetPosition(0, -10, 0)
            camera.SetFocalPoint(0, 0, 0)
            camera.SetViewUp(0, 0, 1)
            camera.ParallelProjectionOn()

        elif view_type == ViewType.RIGHT:
            # Looking along X axis
            camera.SetPosition(10, 0, 0)
            camera.SetFocalPoint(0, 0, 0)
            camera.SetViewUp(0, 0, 1)
            camera.ParallelProjectionOn()

        elif view_type == ViewType.BACK:
            # Looking along negative Y axis
            camera.SetPosition(0, 10, 0)
            camera.SetFocalPoint(0, 0, 0)
            camera.SetViewUp(0, 0, 1)
            camera.ParallelProjectionOn()

        elif view_type == ViewType.LEFT:
            # Looking along negative X axis
            camera.SetPosition(-10, 0, 0)
            camera.SetFocalPoint(0, 0, 0)
            camera.SetViewUp(0, 0, 1)
            camera.ParallelProjectionOn()

        elif view_type == ViewType.BOTTOM:
            # Looking up Z axis
            camera.SetPosition(0, 0, -10)
            camera.SetFocalPoint(0, 0, 0)
            camera.SetViewUp(0, 1, 0)
            camera.ParallelProjectionOn()

        elif view_type == ViewType.ISOMETRIC:
            # Southeast isometric view
            camera.SetPosition(10, -10, 10)
            camera.SetFocalPoint(0, 0, 0)
            camera.SetViewUp(0, 0, 1)
            camera.ParallelProjectionOn()

        else:  # PERSPECTIVE
            # Default perspective view
            camera.SetPosition(10, -10, 10)
            camera.SetFocalPoint(0, 0, 0)
            camera.SetViewUp(0, 0, 1)
            camera.ParallelProjectionOff()

        viewport.renderer.ResetCamera()
        viewport.render_window.Render()

    def _on_viewport_clicked(self, viewport: Viewport3D, event):
        """Handle viewport click to set it as active"""
        if viewport in self.viewports:
            index = self.viewports.index(viewport)
            self.set_active_viewport(index)

    def set_active_viewport(self, index: int):
        """
        Set the active viewport by index

        Args:
            index: Index of viewport to activate
        """
        if 0 <= index < len(self.viewports):
            self.active_viewport_index = index

            # Update visual indication using the new set_active method
            for i, viewport in enumerate(self.viewports):
                viewport.set_active(i == index)

            self.active_viewport_changed.emit(index)

    def get_active_viewport(self) -> Optional[Viewport3D]:
        """Get the currently active viewport"""
        if 0 <= self.active_viewport_index < len(self.viewports):
            return self.viewports[self.active_viewport_index]
        return None

    def display_geometry(self, geometry_data):
        """
        Display geometry in all viewports

        Args:
            geometry_data: The geometry to display
        """
        for viewport in self.viewports:
            viewport.display_subd(geometry_data)

    def display_regions(self, regions):
        """
        Display regions in all viewports

        Args:
            regions: List of regions to display
        """
        for viewport in self.viewports:
            viewport.display_regions(regions)

    def reset_all_cameras(self):
        """Reset cameras in all viewports to their default positions"""
        for i, viewport in enumerate(self.viewports):
            if hasattr(viewport, 'view_type'):
                self._setup_viewport_camera(viewport, viewport.view_type)

    def clear_selection(self):
        """Clear selection in all viewports"""
        for viewport in self.viewports:
            if hasattr(viewport, 'clear_selection'):
                viewport.clear_selection()

    def _on_view_change_requested(self, viewport: Viewport3D, view_name: str):
        """Handle view change request from viewport context menu"""
        # Map string to ViewType enum
        view_map = {
            "Perspective": ViewType.PERSPECTIVE,
            "Top": ViewType.TOP,
            "Front": ViewType.FRONT,
            "Right": ViewType.RIGHT,
            "Back": ViewType.BACK,
            "Left": ViewType.LEFT,
            "Bottom": ViewType.BOTTOM,
            "Isometric": ViewType.ISOMETRIC
        }

        if view_name in view_map:
            view_type = view_map[view_name]
            viewport.set_view_type(view_type)
            self._setup_viewport_camera(viewport, view_type)

    def sync_cameras(self, source_index: int):
        """
        Synchronize all viewport cameras with the source viewport

        Args:
            source_index: Index of the source viewport
        """
        if not (0 <= source_index < len(self.viewports)):
            return

        source = self.viewports[source_index]
        source_camera = source.renderer.GetActiveCamera()

        for i, viewport in enumerate(self.viewports):
            if i != source_index:
                target_camera = viewport.renderer.GetActiveCamera()
                target_camera.SetPosition(source_camera.GetPosition())
                target_camera.SetFocalPoint(source_camera.GetFocalPoint())
                target_camera.SetViewUp(source_camera.GetViewUp())
                viewport.render_window.Render()