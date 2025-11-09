# Agent 11: VTK Viewport Base Classes

**Day**: 2
**Phase**: Phase 1 - Desktop Application
**Duration**: 4-5 hours
**Estimated Cost**: $5-8 (60K tokens, Sonnet)

---

## Mission

Create professional VTK viewport infrastructure with proper camera controls, rendering pipeline, and Rhino-compatible interaction.

---

## Context

You are building the foundation for 3D visualization in the desktop app. This includes:
- VTK rendering window integrated with PyQt6
- Professional camera controls (Rhino-style)
- Proper lighting and material setup
- Axes helper and grid plane
- Viewport management base class
- Ready for multi-viewport extension (Day 2, Agent 13)

**Critical**: Must match Rhino 8 viewport navigation EXACTLY (documented in CLAUDE.md).

**Dependencies**:
- PyQt6 6.9.1
- VTK 9.3.0
- Existing app structure from Week 1-3

---

## Deliverables

**Files to Create/Update**:
1. `app/ui/viewport_base.py` - Base viewport widget with VTK
2. `app/ui/camera_controller.py` - Rhino-style camera interaction
3. `app/ui/viewport_helpers.py` - Axes, grid, lighting utilities
4. `tests/test_viewport.py` - Viewport rendering tests

---

## Requirements

### 1. Base Viewport Widget

**File**: `app/ui/viewport_base.py`

```python
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
```

### 2. Rhino-Style Camera Controller

**File**: `app/ui/camera_controller.py`

```python
"""Rhino-compatible camera interaction for VTK viewports."""

import vtk
from PyQt6.QtCore import Qt

class RhinoCameraStyle(vtk.vtkInteractorStyle):
    """VTK interactor style matching Rhino 8 navigation.

    Controls:
        RIGHT drag or MIDDLE drag: Rotate/orbit
        Shift + RIGHT: Pan
        Ctrl + RIGHT or Mouse wheel: Zoom
        LEFT click: Selection (handled separately)
    """

    def __init__(self, viewport):
        """Initialize camera controller.

        Args:
            viewport: ViewportBase instance
        """
        super().__init__()
        self.viewport = viewport

        self.rotating = False
        self.panning = False
        self.zooming = False

        self.last_pos = None

    def OnLeftButtonDown(self, obj, event):
        """LEFT click reserved for selection."""
        # Don't modify camera - selection handled by picker
        self.last_pos = self.GetInteractor().GetEventPosition()
        self.OnLeftButtonDown()  # Call parent for other behaviors

    def OnRightButtonDown(self, obj, event):
        """RIGHT click starts rotate or pan."""
        interactor = self.GetInteractor()

        if interactor.GetShiftKey():
            # Shift + RIGHT = Pan
            self.panning = True
            self.StartPan()
        else:
            # RIGHT = Rotate
            self.rotating = True
            self.StartRotate()

        self.last_pos = interactor.GetEventPosition()

    def OnRightButtonUp(self, obj, event):
        """RIGHT release stops rotate/pan."""
        if self.rotating:
            self.EndRotate()
            self.rotating = False
        if self.panning:
            self.EndPan()
            self.panning = False

        self.viewport.camera_changed.emit()

    def OnMiddleButtonDown(self, obj, event):
        """MIDDLE click = Rotate (alternative)."""
        self.rotating = True
        self.StartRotate()
        self.last_pos = self.GetInteractor().GetEventPosition()

    def OnMiddleButtonUp(self, obj, event):
        """MIDDLE release stops rotate."""
        if self.rotating:
            self.EndRotate()
            self.rotating = False
        self.viewport.camera_changed.emit()

    def OnMouseMove(self, obj, event):
        """Handle mouse movement for camera."""
        interactor = self.GetInteractor()
        current_pos = interactor.GetEventPosition()

        if self.rotating:
            self.Rotate()
        elif self.panning:
            self.Pan()
        elif self.zooming:
            self.Dolly()

        self.last_pos = current_pos
        self.InvokeEvent(vtk.vtkCommand.InteractionEvent)

    def OnMouseWheelForward(self, obj, event):
        """Mouse wheel forward = Zoom in."""
        camera = self.viewport.camera
        camera.Dolly(1.1)
        camera.GetRenderer().ResetCameraClippingRange()
        self.viewport.render_window.Render()
        self.viewport.camera_changed.emit()

    def OnMouseWheelBackward(self, obj, event):
        """Mouse wheel backward = Zoom out."""
        camera = self.viewport.camera
        camera.Dolly(0.9)
        camera.GetRenderer().ResetCameraClippingRange()
        self.viewport.render_window.Render()
        self.viewport.camera_changed.emit()

    def OnKeyPress(self, obj, event):
        """Handle keyboard shortcuts."""
        interactor = self.GetInteractor()
        key = interactor.GetKeySym()

        if key == "space":
            # Space = Reset camera
            self.viewport.reset_camera()
        elif key == "Home":
            # Home = Undo view (not implemented yet)
            pass
        elif key == "End":
            # End = Redo view (not implemented yet)
            pass
```

### 3. Viewport Helpers

**File**: `app/ui/viewport_helpers.py`

```python
"""Viewport helper utilities (axes, grid, etc)."""

import vtk

class ViewportHelpers:
    """Factory for common viewport visual aids."""

    @staticmethod
    def create_axes_actor(length: float = 1.0) -> vtk.vtkAxesActor:
        """Create RGB axes helper (X=Red, Y=Green, Z=Blue).

        Args:
            length: Axis length

        Returns:
            vtkAxesActor
        """
        axes = vtk.vtkAxesActor()
        axes.SetTotalLength(length, length, length)
        axes.SetShaftTypeToCylinder()
        axes.SetCylinderRadius(0.02)
        axes.SetConeRadius(0.1)
        axes.SetNormalizedShaftLength(0.8, 0.8, 0.8)
        axes.SetNormalizedTipLength(0.2, 0.2, 0.2)

        # Labels
        axes.GetXAxisCaptionActor2D().GetTextActor().SetTextScaleModeToNone()
        axes.GetYAxisCaptionActor2D().GetTextActor().SetTextScaleModeToNone()
        axes.GetZAxisCaptionActor2D().GetTextActor().SetTextScaleModeToNone()

        return axes

    @staticmethod
    def create_grid_plane(size: float = 10.0,
                          divisions: int = 10,
                          color: tuple = (0.3, 0.3, 0.3)) -> vtk.vtkActor:
        """Create ground plane grid.

        Args:
            size: Grid size
            divisions: Number of grid divisions
            color: Grid line color (R,G,B)

        Returns:
            vtkActor for grid
        """
        # Create grid points
        points = vtk.vtkPoints()
        lines = vtk.vtkCellArray()

        step = size / divisions
        half_size = size / 2.0

        # Horizontal lines
        for i in range(divisions + 1):
            y = -half_size + i * step

            p1_id = points.InsertNextPoint(-half_size, y, 0)
            p2_id = points.InsertNextPoint(half_size, y, 0)

            line = vtk.vtkLine()
            line.GetPointIds().SetId(0, p1_id)
            line.GetPointIds().SetId(1, p2_id)
            lines.InsertNextCell(line)

        # Vertical lines
        for i in range(divisions + 1):
            x = -half_size + i * step

            p1_id = points.InsertNextPoint(x, -half_size, 0)
            p2_id = points.InsertNextPoint(x, half_size, 0)

            line = vtk.vtkLine()
            line.GetPointIds().SetId(0, p1_id)
            line.GetPointIds().SetId(1, p2_id)
            lines.InsertNextCell(line)

        # Create polydata
        grid = vtk.vtkPolyData()
        grid.SetPoints(points)
        grid.SetLines(lines)

        # Mapper and actor
        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInputData(grid)

        actor = vtk.vtkActor()
        actor.SetMapper(mapper)
        actor.GetProperty().SetColor(*color)
        actor.GetProperty().SetLineWidth(1.0)
        actor.GetProperty().SetOpacity(0.5)

        return actor

    @staticmethod
    def create_bounding_box(bounds: tuple) -> vtk.vtkActor:
        """Create wireframe bounding box.

        Args:
            bounds: (xmin, xmax, ymin, ymax, zmin, zmax)

        Returns:
            vtkActor for bounding box
        """
        outline = vtk.vtkOutlineSource()
        outline.SetBounds(bounds)

        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInputConnection(outline.GetOutputPort())

        actor = vtk.vtkActor()
        actor.SetMapper(mapper)
        actor.GetProperty().SetColor(0.5, 0.5, 0.5)
        actor.GetProperty().SetLineWidth(1.5)

        return actor
```

---

## Testing

**Test File**: `tests/test_viewport.py`

```python
#!/usr/bin/env python3
"""Test VTK viewport functionality."""

import sys
from PyQt6.QtWidgets import QApplication
from app.ui.viewport_base import ViewportBase
from app.ui.viewport_helpers import ViewportHelpers
import vtk

def test_viewport_creation():
    """Test viewport widget creation."""
    print("Testing viewport creation...")

    app = QApplication(sys.argv)

    viewport = ViewportBase("Perspective")
    assert viewport.view_type == "Perspective"
    assert viewport.renderer is not None
    assert viewport.camera is not None

    print("  ✅ Viewport created successfully")

def test_axes_and_grid():
    """Test helper objects."""
    print("\nTesting axes and grid...")

    app = QApplication(sys.argv)
    viewport = ViewportBase()

    # Add axes
    axes = ViewportHelpers.create_axes_actor(length=2.0)
    viewport.renderer.AddActor(axes)

    # Add grid
    grid = ViewportHelpers.create_grid_plane(size=20, divisions=20)
    viewport.add_actor(grid, "grid")

    assert "grid" in viewport.actors
    print("  ✅ Axes and grid added")

def test_camera_views():
    """Test different view types."""
    print("\nTesting camera views...")

    app = QApplication(sys.argv)

    for view_type in ["Perspective", "Top", "Front", "Right"]:
        viewport = ViewportBase(view_type)
        state = viewport.get_camera_state()

        assert 'position' in state
        assert 'focal_point' in state
        print(f"  ✅ {view_type} view configured")

if __name__ == '__main__':
    test_viewport_creation()
    test_axes_and_grid()
    test_camera_views()

    print("\n✅ ALL VIEWPORT TESTS PASSED!")
```

---

## Success Criteria

- [ ] ViewportBase widget created and functional
- [ ] VTK rendering pipeline working
- [ ] Camera controls match Rhino (RIGHT=rotate, Shift+RIGHT=pan, wheel=zoom)
- [ ] Lighting setup professional (3-point lighting)
- [ ] Axes and grid helpers working
- [ ] Multiple view types supported
- [ ] Camera state save/restore working
- [ ] All tests pass

---

## Integration Notes

**Used by**:
- Agent 12: SubD display will use this base
- Agent 13: Multi-viewport layout will manage multiple instances
- Agent 19-21: Edit mode pickers will extend interaction

**File Structure**:
```
app/ui/
├── viewport_base.py           (Create) ← HERE
├── camera_controller.py       (Create) ← HERE
└── viewport_helpers.py        (Create) ← HERE
tests/test_viewport.py         (Create) ← HERE
```

---

**Ready to begin!**
