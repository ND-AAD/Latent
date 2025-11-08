# VTK Bridge Architecture

## Overview

**Single Point of VTK Integration** - All VTK imports happen in ONE file only.

## Architecture Principle

```
┌─────────────────────────────────────────────────────────────┐
│  app/vtk_bridge.py                                          │
│  - ONLY file that imports VTK                               │
│  - Customizes VTK interactor (camera controls)              │
│  - Re-exports VTK types                                     │
│  - Exports create_interactor_style() factory                │
└─────────────────────────────────────────────────────────────┘
                          │
                          │ import
                          ↓
┌─────────────────────────────────────────────────────────────┐
│  All other files:                                           │
│  - from app import vtk_bridge as vtk                        │
│  - Use vtk.vtkRenderer(), vtk.vtkActor(), etc.              │
│  - Use vtk.create_interactor_style(renderer)                │
│  - NEVER import VTK directly                                │
└─────────────────────────────────────────────────────────────┘
```

## Files Refactored

### ✅ Updated to use vtk_bridge:
- [app/ui/picker.py](app/ui/picker.py) - Picking system
- [app/geometry/subd_display.py](app/geometry/subd_display.py) - SubD visualization
- [app/ui/viewport_3d.py](app/ui/viewport_3d.py) - 3D viewport
- [app/ui/viewport_layout.py](app/ui/viewport_layout.py) - Multi-viewport layout
- [test_camera_controls.py](test_camera_controls.py) - Test script

### ❌ Deleted (obsolete):
- `app/ui/camera_controls.py` - Functionality moved to vtk_bridge.py
- `app/ui/rhino_interactor.py` - Functionality moved to vtk_bridge.py

## How to Use

### Import Pattern:
```python
# In ANY file that needs VTK:
from app import vtk_bridge as vtk

# Use as normal:
renderer = vtk.vtkRenderer()
actor = vtk.vtkActor()
picker = vtk.vtkCellPicker()
```

### Camera Controls:
```python
# Create custom camera interactor:
interactor_style = vtk.create_interactor_style(renderer)
interactor.SetInteractorStyle(interactor_style)
```

## Benefits

1. **Single Point of Control**: Customize VTK behavior in one place
2. **No Import Conflicts**: Can't accidentally import raw VTK
3. **Easier Testing**: Mock vtk_bridge for unit tests
4. **Clean Dependencies**: Clear what VTK types are used
5. **Custom Defaults**: Our interactor is the default, not VTK's

## What's in vtk_bridge.py

### Re-exported VTK Types:
- **Rendering**: vtkRenderer, vtkRenderWindow, vtkActor, etc.
- **Geometry**: vtkPoints, vtkPolyData, vtkCellArray, etc.
- **Pickers**: vtkCellPicker, vtkPointPicker, vtkPropPicker
- **Filters**: vtkPolyDataNormals, vtkExtractEdges
- **Qt Integration**: QVTKWidget (wrapped from QVTKRenderWindowInteractor)

### Custom Classes:
- **CameraController**: Pure camera math (rotate, pan, zoom)
- **CustomCameraInteractor**: Our Rhino-compatible interactor style

### Factory Function:
- **create_interactor_style(renderer)**: Returns configured CustomCameraInteractor

## Testing

Run the test to verify camera controls work:
```bash
python3 test_camera_controls.py
```

You should see:
- Debug output showing CustomCameraInteractor is created
- Mouse events logged to console
- Camera responds to RIGHT drag (rotate), Shift+RIGHT (pan), wheel (zoom)
- LEFT click does NOT move camera

## Next Steps

If camera controls work in test, they'll work in main app because:
1. Same vtk_bridge module
2. Same CustomCameraInteractor class
3. Same create_interactor_style() function
4. No other VTK imports to interfere

---

**Key Rule**: If you need VTK, `from app import vtk_bridge as vtk`. Never `import vtk` directly.
