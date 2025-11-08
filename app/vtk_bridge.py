"""
VTK Bridge - Single Point of VTK Integration

This is the ONLY file that imports VTK directly.
All other files import from this module to get VTK types and our custom implementations.

Architecture:
- Import VTK here
- Customize what we need (interactor style)
- Export everything through a clean interface
- Rest of app never sees raw VTK
"""

import sys

# ============================================================================
# IMPORT VTK (happens ONLY here)
# ============================================================================
import vtk
from vtkmodules.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor


# ============================================================================
# VTK TYPES - Re-export for use elsewhere
# ============================================================================

# Rendering
vtkRenderer = vtk.vtkRenderer
vtkRenderWindow = vtk.vtkRenderWindow
vtkRenderWindowInteractor = vtk.vtkRenderWindowInteractor
vtkActor = vtk.vtkActor
vtkPolyDataMapper = vtk.vtkPolyDataMapper

# Geometry
vtkPoints = vtk.vtkPoints
vtkCellArray = vtk.vtkCellArray
vtkPolyData = vtk.vtkPolyData
vtkQuad = vtk.vtkQuad
vtkTriangle = vtk.vtkTriangle
vtkPolygon = vtk.vtkPolygon
vtkDataArray = vtk.vtkDataArray
vtkFloatArray = vtk.vtkFloatArray  # For normals and other float data

# Sources
vtkCubeSource = vtk.vtkCubeSource
vtkParametricTorus = vtk.vtkParametricTorus
vtkParametricBoy = vtk.vtkParametricBoy  # For complex geometry placeholders
vtkParametricFunctionSource = vtk.vtkParametricFunctionSource

# Pickers
vtkCellPicker = vtk.vtkCellPicker
vtkPointPicker = vtk.vtkPointPicker
vtkPropPicker = vtk.vtkPropPicker

# Filters
vtkPolyDataNormals = vtk.vtkPolyDataNormals
vtkExtractEdges = vtk.vtkExtractEdges
vtkLinearSubdivisionFilter = vtk.vtkLinearSubdivisionFilter
vtkSmoothPolyDataFilter = vtk.vtkSmoothPolyDataFilter
vtkExtractSelection = vtk.vtkExtractSelection
vtkGeometryFilter = vtk.vtkGeometryFilter

# Helpers
vtkAxesActor = vtk.vtkAxesActor
vtkOrientationMarkerWidget = vtk.vtkOrientationMarkerWidget
vtkPlaneSource = vtk.vtkPlaneSource
vtkUnsignedCharArray = vtk.vtkUnsignedCharArray
vtkSphereSource = vtk.vtkSphereSource  # For highlighting vertices

# Selection
vtkSelection = vtk.vtkSelection
vtkSelectionNode = vtk.vtkSelectionNode
vtkIdTypeArray = vtk.vtkIdTypeArray

# Math
vtkMath = vtk.vtkMath

# Qt Integration
QVTKWidget = QVTKRenderWindowInteractor


# ============================================================================
# CUSTOM CAMERA CONTROLLER
# ============================================================================

def debug_print(msg):
    """Print with immediate flush"""
    print(msg)
    sys.stdout.flush()


class CameraController:
    """
    Pure camera manipulation logic - no interactor dependencies
    Handles the actual math of rotating, panning, zooming
    """

    def __init__(self, renderer):
        self.renderer = renderer
        self.camera = renderer.GetActiveCamera()

    def rotate(self, dx, dy):
        """Rotate camera based on mouse delta"""
        if not self.renderer:
            return

        # Convert pixel movement to rotation angles
        azimuth = -dx * 0.25  # Horizontal rotation
        elevation = -dy * 0.25  # Vertical rotation

        # Apply rotation
        self.camera.Azimuth(azimuth)
        self.camera.Elevation(elevation)
        self.camera.OrthogonalizeViewUp()

        # Update clipping planes
        self.renderer.ResetCameraClippingRange()

    def pan(self, dx, dy):
        """Pan camera based on mouse delta"""
        if not self.renderer:
            return

        # Get camera properties
        focal_point = list(self.camera.GetFocalPoint())
        position = list(self.camera.GetPosition())

        # Calculate pan in world coordinates
        scale = 0.01  # Adjust for sensitivity

        # Get camera coordinate system
        view_up = self.camera.GetViewUp()
        view_right = [0, 0, 0]
        vtk.vtkMath.Cross(self.camera.GetDirectionOfProjection(), view_up, view_right)

        # Calculate pan vector (correct signs for natural direction)
        pan_x = [-scale * dx * view_right[i] for i in range(3)]
        pan_y = [-scale * dy * view_up[i] for i in range(3)]

        # Apply pan to both focal point and position
        for i in range(3):
            focal_point[i] += pan_x[i] + pan_y[i]
            position[i] += pan_x[i] + pan_y[i]

        self.camera.SetFocalPoint(focal_point)
        self.camera.SetPosition(position)

        # Update clipping planes
        self.renderer.ResetCameraClippingRange()

    def zoom(self, factor):
        """Zoom camera by factor"""
        if not self.renderer:
            return

        if self.camera.GetParallelProjection():
            # Orthographic projection
            self.camera.SetParallelScale(self.camera.GetParallelScale() / factor)
        else:
            # Perspective projection
            self.camera.Dolly(factor)

        # Update clipping planes
        self.renderer.ResetCameraClippingRange()


# ============================================================================
# CUSTOM INTERACTOR STYLE (Our Rhino-compatible controls)
# ============================================================================

class CustomCameraInteractor(vtk.vtkInteractorStyle):
    """
    Our custom camera controls - replaces VTK's default behavior

    Controls:
    - LEFT:   Selection only (no camera movement)
    - RIGHT:  Rotate camera
    - MIDDLE: Pan camera
    - Shift+RIGHT: Pan camera (alternative)
    - Wheel:  Zoom in/out

    CRITICAL: We must use AddObserver to register event callbacks,
    not just override methods (VTK won't call overridden methods automatically)
    """

    def __init__(self):
        super().__init__()
        debug_print("\n" + "!"*80)
        debug_print("!!! CustomCameraInteractor.__init__() CALLED !!!")
        debug_print("!!! If you see this, our class WAS instantiated !!!")
        debug_print("!"*80 + "\n")

        # Our state
        self.last_x = 0
        self.last_y = 0
        self.camera_controller = None
        self.interactor = None

        # Track which button is down
        self.right_button = False
        self.middle_button = False
        self.left_button = False

        # Picking support (set by viewport)
        self.pick_callback = None  # Callback function for picking

        # Enable auto-adjust clipping range
        self.SetAutoAdjustCameraClippingRange(True)

    def SetInteractor(self, interactor):
        """
        Override SetInteractor to register our event callbacks
        This is the KEY method that VTK calls to hook up events
        """
        debug_print("\n" + "="*80)
        debug_print("🎯 SetInteractor() called - REGISTERING EVENT CALLBACKS")
        debug_print("="*80)

        # Call parent
        super().SetInteractor(interactor)
        self.interactor = interactor

        if interactor:
            # Register ALL our event callbacks explicitly
            interactor.AddObserver("LeftButtonPressEvent", self._on_left_button_down)
            interactor.AddObserver("LeftButtonReleaseEvent", self._on_left_button_up)
            interactor.AddObserver("RightButtonPressEvent", self._on_right_button_down)
            interactor.AddObserver("RightButtonReleaseEvent", self._on_right_button_up)
            interactor.AddObserver("MiddleButtonPressEvent", self._on_middle_button_down)
            interactor.AddObserver("MiddleButtonReleaseEvent", self._on_middle_button_up)
            interactor.AddObserver("MouseMoveEvent", self._on_mouse_move)
            interactor.AddObserver("MouseWheelForwardEvent", self._on_wheel_forward)
            interactor.AddObserver("MouseWheelBackwardEvent", self._on_wheel_backward)
            interactor.AddObserver("CharEvent", self._on_char)

            debug_print("✅ All event callbacks registered!")
            debug_print("   - LeftButtonPress/Release")
            debug_print("   - RightButtonPress/Release")
            debug_print("   - MiddleButtonPress/Release")
            debug_print("   - MouseMove")
            debug_print("   - MouseWheel Forward/Backward")
            debug_print("   - Char (keyboard)")
            debug_print("="*80 + "\n")

    def SetRenderer(self, renderer):
        """Set the renderer and create camera controller"""
        self.SetCurrentRenderer(renderer)
        self.SetDefaultRenderer(renderer)
        self.camera_controller = CameraController(renderer)
        debug_print("✅ Renderer set, camera controller created")

    def SetPickCallback(self, callback):
        """
        Set callback for picking operations

        Args:
            callback: Function(x, y) to call when LEFT click happens
        """
        self.pick_callback = callback
        debug_print("✅ Pick callback registered")

    # ========================================================================
    # Event callback methods (called by VTK via AddObserver)
    # These MUST have signature (self, obj, event)
    # ========================================================================

    def _on_left_button_down(self, obj, event):
        """LEFT button pressed - callback version"""
        self.left_button = True
        self.last_x, self.last_y = self.interactor.GetEventPosition()
        debug_print(f"🖱️  LEFT BUTTON DOWN at ({self.last_x}, {self.last_y}) - SELECTION MODE")
        debug_print("   ⚠️  Camera should NOT move!")

    def _on_left_button_up(self, obj, event):
        """LEFT button released - callback version"""
        # Check if this was a click (not a drag)
        x, y = self.interactor.GetEventPosition()
        dx = abs(x - self.last_x)
        dy = abs(y - self.last_y)

        # If mouse moved less than 5 pixels, consider it a click
        if dx < 5 and dy < 5:
            # Check modifier keys
            shift = self.interactor.GetShiftKey()
            ctrl = self.interactor.GetControlKey()

            if shift:
                debug_print(f"🎯 SHIFT+LEFT CLICK detected at ({x}, {y}) - Add to selection")
            else:
                debug_print(f"🎯 LEFT CLICK detected at ({x}, {y}) - New selection")

            # Call pick callback if set, pass modifier state
            if self.pick_callback:
                # Check if callback accepts modifiers
                import inspect
                sig = inspect.signature(self.pick_callback)
                if len(sig.parameters) >= 3:
                    self.pick_callback(x, y, shift)
                else:
                    self.pick_callback(x, y)
            # Note: If no callback, we're in Solid/view mode (no selection)

        self.left_button = False

    def _on_right_button_down(self, obj, event):
        """RIGHT button pressed - callback version"""
        self.right_button = True
        self.last_x, self.last_y = self.interactor.GetEventPosition()
        shift = self.interactor.GetShiftKey()
        if shift:
            debug_print("🖱️  RIGHT BUTTON (+ Shift) - PAN MODE")
        else:
            debug_print("🖱️  RIGHT BUTTON - ROTATE MODE")

    def _on_right_button_up(self, obj, event):
        """RIGHT button released - callback version"""
        self.right_button = False

    def _on_middle_button_down(self, obj, event):
        """MIDDLE button pressed - callback version"""
        self.middle_button = True
        self.last_x, self.last_y = self.interactor.GetEventPosition()
        debug_print("🖱️  MIDDLE BUTTON - PAN MODE")

    def _on_middle_button_up(self, obj, event):
        """MIDDLE button released - callback version"""
        self.middle_button = False

    def _on_mouse_move(self, obj, event):
        """Mouse moved - callback version"""
        if not self.camera_controller:
            return

        x, y = self.interactor.GetEventPosition()
        dx = x - self.last_x
        dy = y - self.last_y

        # LEFT button: Do nothing (selection only)
        if self.left_button:
            pass

        # RIGHT button: Rotate or Pan
        elif self.right_button:
            shift = self.interactor.GetShiftKey()
            if shift:
                self.camera_controller.pan(dx, dy)
            else:
                self.camera_controller.rotate(dx, dy)
            self.interactor.Render()

        # MIDDLE button: Pan
        elif self.middle_button:
            self.camera_controller.pan(dx, dy)
            self.interactor.Render()

        # Update last position
        self.last_x = x
        self.last_y = y

    def _on_wheel_forward(self, obj, event):
        """Mouse wheel forward - callback version"""
        debug_print("🖱️  WHEEL FORWARD - ZOOM IN")
        if self.camera_controller:
            self.camera_controller.zoom(1.1)
            self.interactor.Render()

    def _on_wheel_backward(self, obj, event):
        """Mouse wheel backward - callback version"""
        debug_print("🖱️  WHEEL BACKWARD - ZOOM OUT")
        if self.camera_controller:
            self.camera_controller.zoom(0.9)
            self.interactor.Render()

    def _on_char(self, obj, event):
        """Keyboard character - callback version"""
        key = self.interactor.GetKeySym()
        debug_print(f"⌨️  KEY PRESSED: {key}")
        # Don't call parent - we want to see if OUR handler is called


# ============================================================================
# FACTORY FUNCTION - This is what other modules should use
# ============================================================================

def create_interactor_style(renderer, interactor=None):
    """
    Create our custom interactor style configured for the given renderer

    This is the ONLY function other modules need to call to get camera controls.

    Args:
        renderer: vtkRenderer instance
        interactor: Optional vtkRenderWindowInteractor (if available, will register events immediately)

    Returns:
        Configured CustomCameraInteractor
    """
    debug_print("\n" + "="*60)
    debug_print("🎮 CREATING CUSTOM CAMERA INTERACTOR")
    debug_print("="*60)
    debug_print("Inheriting from: vtkInteractorStyle (BASE CLASS)")
    debug_print("Custom controls:")
    debug_print("  • LEFT:   Selection only (no camera movement)")
    debug_print("  • RIGHT:  Rotate camera")
    debug_print("  • MIDDLE: Pan camera")
    debug_print("  • Shift+RIGHT: Pan camera (alternative)")
    debug_print("  • Wheel:  Zoom in/out")
    debug_print("="*60 + "\n")

    style = CustomCameraInteractor()
    style.SetRenderer(renderer)

    # If interactor provided, set it explicitly
    if interactor:
        debug_print("⚠️  Interactor provided - calling SetInteractor() explicitly")
        style.SetInteractor(interactor)
    else:
        debug_print("⚠️  No interactor provided - will be set later by VTK")

    return style


# ============================================================================
# VERSION INFO
# ============================================================================

def get_vtk_version():
    """Get VTK version string"""
    return vtk.vtkVersion.GetVTKVersion()
