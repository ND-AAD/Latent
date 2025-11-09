"""
SubD Viewport - Specialized 3D viewport for subdivision surface visualization.

Extends base viewport functionality with SubD-specific features:
- Integration with SubDRenderer for optimized display
- Display mode switching (solid/wireframe/shaded_wireframe/points)
- Selection highlighting with proper z-ordering
- Performance monitoring for large meshes
"""

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PyQt6.QtCore import pyqtSignal, Qt
import vtk
from typing import Optional, List, Tuple

from app.geometry.subd_renderer import SubDRenderer

try:
    import cpp_core
except ImportError:
    cpp_core = None


class SubDViewport(QWidget):
    """
    Specialized viewport for SubD visualization with VTK.

    Features:
    - Rhino-compatible camera controls
    - Multiple display modes
    - Selection highlighting
    - Performance optimization
    """

    # Signals
    element_selected = pyqtSignal(int)  # Emitted when face/edge/vertex selected
    view_changed = pyqtSignal(str)  # Emitted when view changes

    def __init__(self, view_name: str = "Perspective"):
        """
        Initialize SubD viewport.

        Args:
            view_name: Name of this viewport (e.g., "Perspective", "Top", "Front")
        """
        super().__init__()

        self.view_name = view_name
        self.is_active = False

        # VTK components
        self.vtk_widget = None
        self.renderer = None
        self.render_window = None
        self.interactor = None

        # SubD rendering
        self.subd_renderer = SubDRenderer()
        self.main_actor = None
        self.control_cage_actor = None
        self.show_control_cage = False

        # Grid and axes
        self.grid_actor = None
        self.axes_widget = None

        self.init_ui()

    def init_ui(self):
        """Initialize the viewport UI."""
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        self.setLayout(layout)

        # Viewport label
        self.view_label = QLabel(self.view_name)
        self.view_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.view_label.setStyleSheet("""
            QLabel {
                background-color: #2b2b2b;
                color: #ffffff;
                padding: 4px;
                font-weight: bold;
                font-size: 11px;
            }
        """)
        layout.addWidget(self.view_label)

        # VTK widget
        from vtkmodules.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor
        self.vtk_widget = QVTKRenderWindowInteractor(self)
        layout.addWidget(self.vtk_widget)

        # Setup VTK pipeline
        self.renderer = vtk.vtkRenderer()
        self.renderer.SetBackground(0.1, 0.1, 0.15)  # Dark blue-gray

        self.render_window = self.vtk_widget.GetRenderWindow()
        self.render_window.AddRenderer(self.renderer)

        self.interactor = self.render_window.GetInteractor()

        # Setup camera controls (Rhino-compatible)
        self._setup_camera_controls()

        # Add grid and axes
        self._add_grid_plane()
        self._add_axes_widget()

        # Initialize interactor
        self.interactor.Initialize()

    def _setup_camera_controls(self):
        """Setup Rhino-compatible camera controls."""
        style = vtk.vtkInteractorStyleTrackballCamera()
        self.interactor.SetInteractorStyle(style)

    def _add_grid_plane(self):
        """Add grid plane at Z=0."""
        plane = vtk.vtkPlaneSource()
        plane.SetOrigin(-10.0, -10.0, 0.0)
        plane.SetPoint1(10.0, -10.0, 0.0)
        plane.SetPoint2(-10.0, 10.0, 0.0)
        plane.SetXResolution(20)
        plane.SetYResolution(20)

        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInputConnection(plane.GetOutputPort())

        self.grid_actor = vtk.vtkActor()
        self.grid_actor.SetMapper(mapper)
        self.grid_actor.GetProperty().SetRepresentationToWireframe()
        self.grid_actor.GetProperty().SetColor(0.3, 0.3, 0.3)
        self.grid_actor.GetProperty().SetOpacity(0.3)

        self.renderer.AddActor(self.grid_actor)

    def _add_axes_widget(self):
        """Add orientation axes widget."""
        axes = vtk.vtkAxesActor()
        axes.SetTotalLength(1.0, 1.0, 1.0)
        axes.SetShaftTypeToCylinder()
        axes.SetCylinderRadius(0.02)

        self.axes_widget = vtk.vtkOrientationMarkerWidget()
        self.axes_widget.SetOrientationMarker(axes)
        self.axes_widget.SetInteractor(self.interactor)
        self.axes_widget.SetViewport(0.0, 0.0, 0.2, 0.2)
        self.axes_widget.EnabledOn()
        self.axes_widget.InteractiveOff()

    def display_subd(
        self,
        tessellation_result,  # cpp_core.TessellationResult
        control_cage=None,  # Optional[cpp_core.SubDControlCage]
        color: Tuple[float, float, float] = (0.8, 0.8, 0.9)
    ):
        """
        Display a subdivision surface.

        Args:
            tessellation_result: Tessellated SubD from C++ evaluator
            control_cage: Optional control cage to display
            color: RGB color for surface
        """
        # Clear existing actors
        if self.main_actor:
            self.renderer.RemoveActor(self.main_actor)
        if self.control_cage_actor:
            self.renderer.RemoveActor(self.control_cage_actor)

        # Create main SubD actor
        self.main_actor = self.subd_renderer.create_subd_actor(
            tessellation_result,
            color=color
        )
        self.renderer.AddActor(self.main_actor)

        # Create control cage if provided
        if control_cage and self.show_control_cage:
            self.control_cage_actor = self.subd_renderer.create_control_cage_actor(
                control_cage
            )
            self.renderer.AddActor(self.control_cage_actor)

        # Reset camera and render
        self.reset_camera()
        self.render()

    def set_display_mode(self, mode: str):
        """
        Set display mode for SubD surface.

        Args:
            mode: One of "solid", "wireframe", "shaded_wireframe", "points"
        """
        self.subd_renderer.set_display_mode(mode)
        self.render()

    def update_selection(self, selected_faces: List[int]):
        """
        Update face selection highlighting.

        Args:
            selected_faces: List of face indices to highlight
        """
        self.subd_renderer.update_selection_highlighting(
            selected_faces,
            self.renderer,
            highlight_color=(1.0, 1.0, 0.0)  # Yellow
        )
        self.render()

    def set_control_cage_visible(self, visible: bool):
        """
        Show or hide control cage.

        Args:
            visible: True to show control cage
        """
        self.show_control_cage = visible

        if self.control_cage_actor:
            self.control_cage_actor.SetVisibility(visible)
            self.render()

    def reset_camera(self):
        """Reset camera to view all geometry."""
        self.renderer.ResetCamera()

        # Set nice viewing angle for perspective view
        if self.view_name == "Perspective":
            camera = self.renderer.GetActiveCamera()
            camera.Elevation(30)
            camera.Azimuth(45)

        self.renderer.ResetCameraClippingRange()
        self.render()

    def render(self):
        """Trigger a render of the viewport."""
        self.render_window.Render()

    def set_active(self, active: bool):
        """
        Set whether this viewport is the active viewport.

        Args:
            active: True if this is the active viewport
        """
        self.is_active = active

        if active:
            self.setStyleSheet("border: 2px solid #4CAF50;")  # Green
            self.view_label.setStyleSheet("""
                QLabel {
                    background-color: #4CAF50;
                    color: #ffffff;
                    padding: 4px;
                    font-weight: bold;
                    font-size: 11px;
                }
            """)
        else:
            self.setStyleSheet("border: 1px solid #333333;")
            self.view_label.setStyleSheet("""
                QLabel {
                    background-color: #2b2b2b;
                    color: #ffffff;
                    padding: 4px;
                    font-weight: bold;
                    font-size: 11px;
                }
            """)

    def get_performance_stats(self) -> dict:
        """
        Get performance statistics for displayed geometry.

        Returns:
            Dictionary with performance metrics
        """
        stats = self.subd_renderer.get_performance_stats()

        # Add viewport-specific stats
        stats["view_name"] = self.view_name
        stats["is_active"] = self.is_active
        stats["display_mode"] = self.subd_renderer.display_mode

        return stats

    def closeEvent(self, event):
        """Clean up VTK resources."""
        if self.interactor:
            self.interactor.TerminateApp()
        super().closeEvent(event)


class MultiViewportLayout(QWidget):
    """
    Layout manager for multiple SubD viewports.

    Provides standard 4-viewport layout (Perspective, Top, Front, Right).
    """

    # Signals
    active_viewport_changed = pyqtSignal(str)  # Emits viewport name

    def __init__(self):
        """Initialize multi-viewport layout."""
        super().__init__()

        self.viewports = {}
        self.active_viewport = None

        self.init_ui()

    def init_ui(self):
        """Initialize the viewport layout."""
        from PyQt6.QtWidgets import QGridLayout

        layout = QGridLayout()
        layout.setSpacing(2)
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)

        # Create viewports
        self.viewports["Perspective"] = SubDViewport("Perspective")
        self.viewports["Top"] = SubDViewport("Top")
        self.viewports["Front"] = SubDViewport("Front")
        self.viewports["Right"] = SubDViewport("Right")

        # Add to grid
        layout.addWidget(self.viewports["Perspective"], 0, 0)
        layout.addWidget(self.viewports["Top"], 0, 1)
        layout.addWidget(self.viewports["Front"], 1, 0)
        layout.addWidget(self.viewports["Right"], 1, 1)

        # Set perspective as active
        self.set_active_viewport("Perspective")

    def set_active_viewport(self, name: str):
        """
        Set the active viewport.

        Args:
            name: Name of viewport to activate
        """
        # Deactivate all
        for vp in self.viewports.values():
            vp.set_active(False)

        # Activate selected
        if name in self.viewports:
            self.active_viewport = name
            self.viewports[name].set_active(True)
            self.active_viewport_changed.emit(name)

    def get_active_viewport(self) -> Optional[SubDViewport]:
        """
        Get the currently active viewport.

        Returns:
            Active SubDViewport or None
        """
        if self.active_viewport:
            return self.viewports[self.active_viewport]
        return None

    def display_subd_all(self, tessellation_result, control_cage=None):
        """
        Display SubD in all viewports.

        Args:
            tessellation_result: Tessellated SubD
            control_cage: Optional control cage
        """
        for vp in self.viewports.values():
            vp.display_subd(tessellation_result, control_cage)
