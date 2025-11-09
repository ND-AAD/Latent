"""Base VTK viewport widget for 3D visualization."""

import vtk
from vtkmodules.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PyQt6.QtCore import Qt, pyqtSignal
from typing import Optional


class ViewportBase(QWidget):
    """Base class for VTK 3D viewports.

    Signals:
        camera_changed: Emitted when camera moves
        selection_changed: Emitted when selection changes
    """

    camera_changed = pyqtSignal()
    selection_changed = pyqtSignal(list)  # List of selected actor IDs

    def __init__(self, view_type: str = "Perspective", parent=None):
        """Initialize viewport.

        Args:
            view_type: View type ("Perspective", "Top", "Front", etc.)
            parent: Parent widget
        """
        super().__init__(parent)

        self.view_type = view_type
        self.is_active = False

        # Create layout
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)

        # View label
        self.label = QLabel(view_type)
        self.label.setStyleSheet("""
            QLabel {
                background-color: rgba(50, 50, 50, 180);
                color: white;
                padding: 4px 8px;
                border-radius: 3px;
                font-size: 11px;
            }
        """)
        self.label.setMaximumHeight(25)

        # VTK widget
        self.vtk_widget = QVTKRenderWindowInteractor(self)

        layout.addWidget(self.label)
        layout.addWidget(self.vtk_widget)
        self.setLayout(layout)

        # Setup VTK pipeline
        self.renderer = vtk.vtkRenderer()
        self.renderer.SetBackground(0.15, 0.15, 0.15)  # Dark gray

        self.render_window = self.vtk_widget.GetRenderWindow()
        self.render_window.AddRenderer(self.renderer)

        # Camera
        self.camera = self.renderer.GetActiveCamera()
        self._setup_camera_for_view_type()

        # Interactor (will be enhanced with custom style)
        self.interactor = self.render_window.GetInteractor()

        # Setup lighting
        self._setup_lights()

        # Actors
        self.actors = {}  # ID -> vtkActor mapping
        self.selected_actors = set()

    def _setup_camera_for_view_type(self):
        """Configure camera based on view type."""
        if self.view_type == "Perspective":
            self.camera.SetPosition(5, 5, 5)
            self.camera.SetFocalPoint(0, 0, 0)
            self.camera.SetViewUp(0, 0, 1)
            self.camera.SetViewAngle(45)

        elif self.view_type == "Top":
            self.camera.SetPosition(0, 0, 10)
            self.camera.SetFocalPoint(0, 0, 0)
            self.camera.SetViewUp(0, 1, 0)
            self.camera.ParallelProjectionOn()

        elif self.view_type == "Front":
            self.camera.SetPosition(0, -10, 0)
            self.camera.SetFocalPoint(0, 0, 0)
            self.camera.SetViewUp(0, 0, 1)
            self.camera.ParallelProjectionOn()

        elif self.view_type == "Right":
            self.camera.SetPosition(10, 0, 0)
            self.camera.SetFocalPoint(0, 0, 0)
            self.camera.SetViewUp(0, 0, 1)
            self.camera.ParallelProjectionOn()

        # Add other standard views as needed

    def _setup_lights(self):
        """Setup professional 3-point lighting."""
        # Key light (main directional)
        key_light = vtk.vtkLight()
        key_light.SetPosition(10, 10, 10)
        key_light.SetFocalPoint(0, 0, 0)
        key_light.SetColor(1.0, 1.0, 1.0)
        key_light.SetIntensity(0.8)
        self.renderer.AddLight(key_light)

        # Fill light (softer, from opposite)
        fill_light = vtk.vtkLight()
        fill_light.SetPosition(-5, -5, 5)
        fill_light.SetFocalPoint(0, 0, 0)
        fill_light.SetColor(0.8, 0.8, 1.0)
        fill_light.SetIntensity(0.3)
        self.renderer.AddLight(fill_light)

        # Back light (rim lighting)
        back_light = vtk.vtkLight()
        back_light.SetPosition(0, -10, -5)
        back_light.SetFocalPoint(0, 0, 0)
        back_light.SetColor(1.0, 1.0, 1.0)
        back_light.SetIntensity(0.2)
        self.renderer.AddLight(back_light)

    def add_actor(self, actor: vtk.vtkActor, actor_id: str = None) -> str:
        """Add actor to viewport.

        Args:
            actor: VTK actor to add
            actor_id: Optional ID for actor (auto-generated if None)

        Returns:
            Actor ID
        """
        if actor_id is None:
            actor_id = f"actor_{len(self.actors)}"

        self.actors[actor_id] = actor
        self.renderer.AddActor(actor)
        return actor_id

    def remove_actor(self, actor_id: str):
        """Remove actor from viewport."""
        if actor_id in self.actors:
            self.renderer.RemoveActor(self.actors[actor_id])
            del self.actors[actor_id]

    def clear_actors(self):
        """Remove all actors."""
        for actor in self.actors.values():
            self.renderer.RemoveActor(actor)
        self.actors.clear()
        self.selected_actors.clear()

    def reset_camera(self):
        """Reset camera to fit all geometry."""
        self.renderer.ResetCamera()
        self.render_window.Render()
        self.camera_changed.emit()

    def set_active(self, active: bool):
        """Set viewport active state."""
        self.is_active = active

        # Update visual indicator
        if active:
            self.label.setStyleSheet("""
                QLabel {
                    background-color: rgba(0, 120, 0, 200);
                    color: white;
                    padding: 4px 8px;
                    border-radius: 3px;
                    font-size: 11px;
                    border: 2px solid rgb(0, 255, 0);
                }
            """)
        else:
            self.label.setStyleSheet("""
                QLabel {
                    background-color: rgba(50, 50, 50, 180);
                    color: white;
                    padding: 4px 8px;
                    border-radius: 3px;
                    font-size: 11px;
                }
            """)

    def get_camera_state(self) -> dict:
        """Get current camera state for saving/restoring."""
        pos = self.camera.GetPosition()
        focal = self.camera.GetFocalPoint()
        up = self.camera.GetViewUp()

        return {
            'position': list(pos),
            'focal_point': list(focal),
            'view_up': list(up),
            'view_angle': self.camera.GetViewAngle(),
            'parallel_projection': self.camera.GetParallelProjection()
        }

    def set_camera_state(self, state: dict):
        """Restore camera state."""
        self.camera.SetPosition(state['position'])
        self.camera.SetFocalPoint(state['focal_point'])
        self.camera.SetViewUp(state['view_up'])
        self.camera.SetViewAngle(state['view_angle'])

        if state['parallel_projection']:
            self.camera.ParallelProjectionOn()
        else:
            self.camera.ParallelProjectionOff()

        self.render_window.Render()

    def render(self):
        """Trigger render."""
        self.render_window.Render()
