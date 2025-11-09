# Agent 7: Complete Tessellation & Display

**Day**: 1
**Phase**: Phase 0 - C++ Core Foundation
**Duration**: 5-6 hours
**Estimated Cost**: $6-10 (80K tokens, Sonnet)

---

## Mission

Implement complete tessellation pipeline with VTK visualization for the desktop application, integrating C++ SubDEvaluator with PyQt6 UI.

---

## Context

You are creating the bridge between C++ geometry evaluation and Python VTK visualization. This module:
- Fetches SubD control cage from Grasshopper server
- Calls C++ SubDEvaluator to tessellate
- Converts result to VTK actors for display
- Handles viewport rendering with proper camera controls
- Maintains triangle→face mapping for selection

**Critical**: Tessellation is for **display only**. All analysis queries exact limit surface via C++ bindings.

**Dependencies**:
- Agent 5's pybind11 bindings (latent_core module)
- Agent 6's Grasshopper HTTP server
- Existing PyQt6 viewport infrastructure (app/ui/viewport_3d.py)

---

## Deliverables

**Files to Create**:
1. `app/geometry/subd_display.py` - VTK conversion utilities
2. `app/bridge/subd_fetcher.py` - HTTP bridge to Grasshopper
3. Update `main.py` - Add "Load from Rhino" menu item

---

## Requirements

### 1. SubD Fetcher (HTTP Bridge)

**File**: `app/bridge/subd_fetcher.py`

```python
"""Fetch SubD geometry from Grasshopper HTTP server."""

import requests
import latent_core
from typing import Optional, Dict, Any

class SubDFetcher:
    """Fetch SubD control cage from Grasshopper server."""

    def __init__(self, host='localhost', port=8888):
        """Initialize fetcher.

        Args:
            host: Server hostname
            port: Server port
        """
        self.host = host
        self.port = port
        self.base_url = f'http://{host}:{port}'

    def is_server_available(self) -> bool:
        """Check if server is running."""
        try:
            response = requests.get(
                f'{self.base_url}/status',
                timeout=1
            )
            return response.status_code == 200
        except:
            return False

    def fetch_control_cage(self) -> Optional[latent_core.SubDControlCage]:
        """Fetch SubD control cage from server.

        Returns:
            SubDControlCage if successful, None otherwise
        """
        try:
            response = requests.get(
                f'{self.base_url}/geometry',
                timeout=5
            )
            response.raise_for_status()

            data = response.json()

            # Convert JSON to SubDControlCage
            cage = latent_core.SubDControlCage()

            # Add vertices
            for v in data['vertices']:
                cage.vertices.append(
                    latent_core.Point3D(v[0], v[1], v[2])
                )

            # Add faces
            cage.faces = data['faces']

            # Add creases if present
            if 'creases' in data:
                for c in data['creases']:
                    cage.creases.append((c[0], c[1], c[2]))

            return cage

        except Exception as e:
            print(f"Failed to fetch geometry: {e}")
            return None

    def get_metadata(self) -> Optional[Dict[str, Any]]:
        """Get geometry metadata without full download."""
        try:
            response = requests.get(
                f'{self.base_url}/geometry',
                timeout=2
            )
            data = response.json()
            return data.get('metadata', {})
        except:
            return None
```

### 2. VTK Display Utilities

**File**: `app/geometry/subd_display.py`

```python
"""Convert C++ tessellation results to VTK actors for display."""

import vtk
import numpy as np
import latent_core
from typing import Tuple

class SubDDisplayManager:
    """Manage VTK visualization of SubD geometry."""

    @staticmethod
    def create_mesh_actor(result: latent_core.TessellationResult,
                         color: Tuple[float, float, float] = (0.8, 0.8, 0.8),
                         show_edges: bool = False) -> vtk.vtkActor:
        """Create VTK actor from tessellation result.

        Args:
            result: Tessellation from SubDEvaluator
            color: RGB color (0-1)
            show_edges: Show edge wireframe

        Returns:
            vtkActor ready for rendering
        """
        # Get numpy arrays (zero-copy!)
        vertices = result.vertices  # (N, 3) array
        normals = result.normals    # (N, 3) array
        triangles = result.triangles  # (M, 3) array

        # Create VTK points
        vtk_points = vtk.vtkPoints()
        for v in vertices:
            vtk_points.InsertNextPoint(v[0], v[1], v[2])

        # Create VTK normals
        vtk_normals = vtk.vtkFloatArray()
        vtk_normals.SetNumberOfComponents(3)
        vtk_normals.SetName("Normals")
        for n in normals:
            vtk_normals.InsertNextTuple3(n[0], n[1], n[2])

        # Create VTK triangles
        vtk_cells = vtk.vtkCellArray()
        for tri in triangles:
            triangle = vtk.vtkTriangle()
            triangle.GetPointIds().SetId(0, tri[0])
            triangle.GetPointIds().SetId(1, tri[1])
            triangle.GetPointIds().SetId(2, tri[2])
            vtk_cells.InsertNextCell(triangle)

        # Create polydata
        poly_data = vtk.vtkPolyData()
        poly_data.SetPoints(vtk_points)
        poly_data.SetPolys(vtk_cells)
        poly_data.GetPointData().SetNormals(vtk_normals)

        # Create mapper
        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInputData(poly_data)

        # Create actor
        actor = vtk.vtkActor()
        actor.SetMapper(mapper)
        actor.GetProperty().SetColor(*color)

        if show_edges:
            actor.GetProperty().EdgeVisibilityOn()
            actor.GetProperty().SetEdgeColor(0.2, 0.2, 0.2)

        return actor

    @staticmethod
    def create_control_cage_actor(cage: latent_core.SubDControlCage,
                                  color: Tuple[float, float, float] = (1.0, 0.0, 0.0),
                                  point_size: float = 5.0) -> vtk.vtkActor:
        """Create VTK actor for control cage wireframe.

        Args:
            cage: SubD control cage
            color: RGB color
            point_size: Control point size

        Returns:
            vtkActor showing control net
        """
        # Create points
        vtk_points = vtk.vtkPoints()
        for v in cage.vertices:
            vtk_points.InsertNextPoint(v.x, v.y, v.z)

        # Create lines for edges
        vtk_lines = vtk.vtkCellArray()

        for face in cage.faces:
            # Draw face edges
            for i in range(len(face)):
                line = vtk.vtkLine()
                line.GetPointIds().SetId(0, face[i])
                line.GetPointIds().SetId(1, face[(i + 1) % len(face)])
                vtk_lines.InsertNextCell(line)

        # Create polydata
        poly_data = vtk.vtkPolyData()
        poly_data.SetPoints(vtk_points)
        poly_data.SetLines(vtk_lines)

        # Create mapper
        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInputData(poly_data)

        # Create actor
        actor = vtk.vtkActor()
        actor.SetMapper(mapper)
        actor.GetProperty().SetColor(*color)
        actor.GetProperty().SetLineWidth(2.0)
        actor.GetProperty().SetPointSize(point_size)
        actor.GetProperty().SetRenderPointsAsSpheres(True)

        return actor

    @staticmethod
    def compute_bounding_box(result: latent_core.TessellationResult) -> Tuple[np.ndarray, np.ndarray]:
        """Compute axis-aligned bounding box.

        Returns:
            (min_corner, max_corner) as numpy arrays
        """
        vertices = result.vertices
        min_corner = vertices.min(axis=0)
        max_corner = vertices.max(axis=0)
        return min_corner, max_corner
```

### 3. Integration with Main Window

**Update**: `main.py`

Add import:
```python
from app.bridge.subd_fetcher import SubDFetcher
from app.geometry.subd_display import SubDDisplayManager
import latent_core
```

Add to MainWindow class:
```python
def __init__(self):
    # ... existing code ...

    # Add SubD components
    self.subd_fetcher = SubDFetcher()
    self.subd_evaluator = latent_core.SubDEvaluator()
    self.current_cage = None

    # ... rest of initialization ...
```

Add menu item to File menu:
```python
def create_menu_bar(self):
    # ... existing menu code ...

    # File menu
    file_menu = menubar.addMenu('&File')

    # Load from Rhino
    load_rhino = QAction('Load from &Rhino', self)
    load_rhino.setShortcut('Ctrl+R')
    load_rhino.triggered.connect(self.load_from_rhino)
    file_menu.addAction(load_rhino)

    # ... rest of menu ...
```

Add load handler:
```python
def load_from_rhino(self):
    """Load SubD geometry from Grasshopper server."""
    # Check server availability
    if not self.subd_fetcher.is_server_available():
        print("❌ Grasshopper server not available on localhost:8888")
        print("   Start server in Grasshopper first")
        return

    # Fetch control cage
    cage = self.subd_fetcher.fetch_control_cage()
    if cage is None:
        print("❌ Failed to fetch geometry from Rhino")
        return

    self.current_cage = cage

    # Initialize evaluator
    self.subd_evaluator.initialize(cage)

    # Tessellate for display
    print(f"Tessellating {cage.vertex_count()} control vertices...")
    result = self.subd_evaluator.tessellate(subdivision_level=3)

    print(f"✅ Generated {result.vertex_count()} vertices, "
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
```

---

## Testing

### Test 1: End-to-End Workflow

**Setup**:
1. Start Grasshopper server (Agent 6) with SubD sphere
2. Launch desktop app: `python3 launch.py`
3. File → Load from Rhino (Ctrl+R)

**Expected**:
- Console shows: "Tessellating 386 control vertices..."
- Console shows: "✅ Generated [N] vertices, [M] triangles"
- Console shows: "✅ Geometry displayed in viewport"
- Viewport shows smooth subdivided sphere
- Camera controls work (right-drag rotate, shift+right pan, wheel zoom)

### Test 2: Different Subdivision Levels

**Test File**: `tests/test_tessellation_levels.py`

```python
#!/usr/bin/env python3
"""Test tessellation at different subdivision levels."""

import sys
sys.path.insert(0, 'cpp_core/build')

import latent_core
from app.bridge.subd_fetcher import SubDFetcher

def main():
    print("Testing tessellation levels...")

    # Fetch geometry
    fetcher = SubDFetcher()

    if not fetcher.is_server_available():
        print("❌ Server not available")
        return 1

    cage = fetcher.fetch_control_cage()
    if cage is None:
        print("❌ Failed to fetch cage")
        return 1

    print(f"\nControl cage: {cage.vertex_count()} vertices, "
          f"{cage.face_count()} faces\n")

    # Test subdivision levels
    evaluator = latent_core.SubDEvaluator()
    evaluator.initialize(cage)

    for level in range(1, 5):
        result = evaluator.tessellate(level)
        print(f"Level {level}: {result.vertex_count():6d} vertices, "
              f"{result.triangle_count():6d} triangles")

        # Verify data integrity
        assert result.vertices.shape[0] == result.vertex_count()
        assert result.triangles.shape[0] == result.triangle_count()
        assert len(result.face_parents) == result.triangle_count()

    print("\n✅ All levels working correctly")
    return 0

if __name__ == '__main__':
    sys.exit(main())
```

**Run**:
```bash
python3 tests/test_tessellation_levels.py
```

### Test 3: Performance Benchmark

**Test File**: `tests/test_tessellation_perf.py`

```python
#!/usr/bin/env python3
"""Benchmark tessellation performance."""

import sys
import time
sys.path.insert(0, 'cpp_core/build')

import latent_core
from app.bridge.subd_fetcher import SubDFetcher

def main():
    print("Benchmarking tessellation performance...")

    fetcher = SubDFetcher()
    cage = fetcher.fetch_control_cage()

    if cage is None:
        print("❌ No geometry available")
        return 1

    evaluator = latent_core.SubDEvaluator()

    # Benchmark initialization
    start = time.time()
    evaluator.initialize(cage)
    init_time = time.time() - start

    print(f"\nInitialization: {init_time*1000:.2f} ms")

    # Benchmark tessellation at different levels
    for level in [1, 2, 3, 4]:
        times = []
        for _ in range(5):  # 5 runs
            start = time.time()
            result = evaluator.tessellate(level)
            times.append(time.time() - start)

        avg_time = sum(times) / len(times) * 1000
        print(f"Level {level}: {avg_time:6.2f} ms avg "
              f"({result.triangle_count()} triangles)")

    # Benchmark limit evaluation
    n_points = 10000
    start = time.time()
    for i in range(n_points):
        u = (i % 100) / 100.0
        v = (i // 100) / 100.0
        pt = evaluator.evaluate_limit_point(0, u, v)
    eval_time = time.time() - start

    print(f"\nLimit evaluation: {n_points} points in "
          f"{eval_time*1000:.2f} ms")
    print(f"  ({n_points/eval_time:.0f} points/sec)")

    print("\n✅ Performance tests complete")
    return 0

if __name__ == '__main__':
    sys.exit(main())
```

---

## Success Criteria

- [ ] SubDFetcher successfully fetches control cage from server
- [ ] Control cage converts to latent_core.SubDControlCage correctly
- [ ] SubDEvaluator initializes without errors
- [ ] Tessellation produces valid mesh at all levels (1-4)
- [ ] VTK actors created successfully from tessellation
- [ ] Geometry displays in viewport with proper shading
- [ ] Camera controls work correctly
- [ ] All tests pass
- [ ] Performance meets targets:
  - Initialization: <20ms
  - Level 3 tessellation: <100ms
  - Limit evaluation: >10K points/sec

---

## Integration Notes

**Connects**:
- Agent 6 (Grasshopper server) → SubDFetcher → latent_core
- latent_core.SubDEvaluator → SubDDisplayManager → VTK viewport
- Existing MainWindow → New load_from_rhino() method

**File Structure**:
```
app/
├── bridge/
│   └── subd_fetcher.py          (You create) ← HERE
└── geometry/
    └── subd_display.py          (You create) ← HERE
├── main.py                          (You update) ← HERE
├── test_tessellation_levels.py      (You create) ← HERE
└── test_tessellation_perf.py        (You create) ← HERE
```

---

## Common Issues and Solutions

**Issue**: "latent_core module not found"
- **Fix**: Ensure C++ module built: `cd cpp_core/build && cmake .. && make`
- **Fix**: Add to PYTHONPATH: `export PYTHONPATH=cpp_core/build:$PYTHONPATH`

**Issue**: "Server not available"
- **Fix**: Start Grasshopper server first with Agent 6's component
- **Fix**: Check port 8888 not blocked by firewall

**Issue**: "Geometry appears faceted, not smooth"
- **Fix**: Increase subdivision level (try level 4)
- **Fix**: Ensure normals are being set in VTK actor

**Issue**: "Viewport is blank after loading"
- **Fix**: Check renderer.ResetCamera() is called
- **Fix**: Verify actor was added to renderer
- **Fix**: Call render_window.Render() to refresh

---

## Output Format

Provide:
1. Complete `subd_fetcher.py` implementation
2. Complete `subd_display.py` implementation
3. Updated `main.py` with load_from_rhino integration
4. Both test scripts (levels and performance)
5. Test output showing successful geometry loading
6. Screenshot or description of viewport display (if possible)
7. Performance benchmark results
8. Integration notes

---

**Ready to begin!**
