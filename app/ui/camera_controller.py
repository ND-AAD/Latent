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
