#!/usr/bin/env python3
"""
Minimal test for camera controls using VTK BRIDGE architecture

IMPORTANT: This script imports ONLY from vtk_bridge - never imports VTK directly.
This demonstrates the clean architecture where VTK is hidden behind our interface.

Run this to test if camera controls work:
    python3 test_camera_controls.py

Expected behavior:
- RIGHT drag: Rotate cube
- MIDDLE drag: Pan camera
- Shift + RIGHT drag: Pan camera (alternative)
- Mouse wheel: Zoom in/out
- LEFT click: Should print position but NOT move camera
"""

import sys
import os

# Add the ceramic_mold_analyzer directory to path
script_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, script_dir)

# Force unbuffered output
sys.stdout.reconfigure(line_buffering=True)
sys.stderr.reconfigure(line_buffering=True)

print("=" * 80)
print("CAMERA CONTROLS TEST - VTK BRIDGE ARCHITECTURE")
print("=" * 80)
print(f"Python version: {sys.version}")
print()

# Import ONLY from vtk_bridge - this is the single point of VTK integration
print("Importing from vtk_bridge...")
sys.stdout.flush()

from app import vtk_bridge as vtk

print("✅ vtk_bridge imported!")
print(f"   VTK version: {vtk.get_vtk_version()}")
print()


def main():
    """Create minimal VTK scene with our camera controls"""

    # Create renderer
    renderer = vtk.vtkRenderer()
    renderer.SetBackground(0.1, 0.1, 0.15)

    # Create a simple cube
    cube = vtk.vtkCubeSource()
    cube.SetXLength(2.0)
    cube.SetYLength(2.0)
    cube.SetZLength(2.0)

    mapper = vtk.vtkPolyDataMapper()
    mapper.SetInputConnection(cube.GetOutputPort())

    actor = vtk.vtkActor()
    actor.SetMapper(mapper)
    actor.GetProperty().SetColor(0.8, 0.8, 0.9)
    actor.GetProperty().EdgeVisibilityOn()
    actor.GetProperty().SetEdgeColor(0.2, 0.2, 0.3)

    renderer.AddActor(actor)

    # Create render window
    render_window = vtk.vtkRenderWindow()
    render_window.AddRenderer(renderer)
    render_window.SetSize(800, 600)
    render_window.SetWindowName("Camera Controls Test - VTK Bridge Architecture")

    # Create interactor
    interactor = vtk.vtkRenderWindowInteractor()
    interactor.SetRenderWindow(render_window)

    # *** USE OUR CUSTOM CAMERA INTERACTOR from vtk_bridge ***
    print("\n" + "=" * 80)
    print("SETTING UP CUSTOM CAMERA INTERACTOR")
    print("=" * 80)
    sys.stdout.flush()

    # CRITICAL: Pass the interactor to our factory function
    # This ensures SetInteractor() is called and events are registered
    camera_style = vtk.create_interactor_style(renderer, interactor)

    print(f"\nCamera style created: {camera_style}")
    print(f"Type: {type(camera_style)}")
    sys.stdout.flush()

    # VTK should now have our style registered
    print("Checking if VTK recognizes our style...")
    sys.stdout.flush()

    # VERIFY the interactor style was set correctly
    print("\n🔍 DIAGNOSTIC CHECK:")
    actual_style = interactor.GetInteractorStyle()
    print(f"   Interactor style type: {type(actual_style).__name__}")
    print(f"   Is our style? {actual_style is camera_style}")

    if actual_style is not camera_style:
        print("   ❌ ERROR: VTK is NOT using our custom style!")
    else:
        print("   ✅ SUCCESS: Our custom style is active")
    print()

    # Add axes helper
    axes = vtk.vtkAxesActor()
    axes.SetTotalLength(1.0, 1.0, 1.0)

    axes_widget = vtk.vtkOrientationMarkerWidget()
    axes_widget.SetOrientationMarker(axes)
    axes_widget.SetInteractor(interactor)
    axes_widget.SetViewport(0.0, 0.0, 0.2, 0.2)
    axes_widget.EnabledOn()
    axes_widget.InteractiveOff()

    # Reset camera
    renderer.ResetCamera()
    camera = renderer.GetActiveCamera()
    camera.Elevation(30)
    camera.Azimuth(45)
    renderer.ResetCameraClippingRange()

    # Print instructions
    print("\n" + "="*80)
    print("CONTROLS:")
    print("="*80)
    print("  RIGHT drag:        Rotate camera")
    print("  MIDDLE drag:       Pan camera")
    print("  Shift + RIGHT:     Pan camera (alternative)")
    print("  Mouse wheel:       Zoom in/out")
    print("  LEFT click:        Selection (should NOT move camera)")
    print("\nKeyboard:")
    print("  W:                 Wireframe mode")
    print("  S:                 Shaded mode")
    print("  Q:                 Quit")
    print("\nWatch console for mouse event debug messages!")
    print("="*80 + "\n")

    # Start interaction
    interactor.Initialize()

    # CRITICAL: Re-set our style AFTER Initialize()
    # because VTK replaces it with vtkInteractorStyleSwitch
    print("⚠️  Re-setting our custom style after Initialize()...")
    interactor.SetInteractorStyle(camera_style)

    # Verify it stuck this time
    actual_style = interactor.GetInteractorStyle()
    print(f"   Final style: {type(actual_style).__name__}")
    if actual_style is camera_style:
        print("   ✅ SUCCESS: Our style is active!")
    else:
        print(f"   ❌ STILL WRONG: Got {type(actual_style).__name__}")
    print()

    render_window.Render()
    interactor.Start()


if __name__ == '__main__':
    main()
