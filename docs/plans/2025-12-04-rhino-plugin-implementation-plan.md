# Rhino Plugin Implementation Plan

**Date**: 2025-12-04
**Companion Doc**: `2025-12-04-rhino-plugin-architecture-design.md`

---

## Overview

This plan details the implementation path for migrating from the standalone desktop app to a Rhino plugin with parametric region support.

**Estimated Total Effort**: 6-8 weeks (1 developer)

---

## Phase 0: Prerequisites & Setup (Week 1)

### 0.1 Development Environment

- [ ] Install Visual Studio 2022 with C# workload
- [ ] Install Rhino 8 (required for Python 3 support)
- [ ] Install RhinoCommon SDK / Rhino.Inside if needed
- [ ] Set up Rhino plugin project template (C#)
- [ ] Verify OpenCASCADE is installed (for NURBS features)
- [ ] Set up cross-platform build for cpp_core (macOS .dylib, Windows .dll)

### 0.2 Project Structure

```
Latent/
├── cpp_core/                    # Existing - add C bindings
│   ├── c_bindings/              # NEW: P/Invoke compatible layer
│   │   ├── rhino_wrapper.h
│   │   └── rhino_wrapper.cpp
│   └── ...
├── rhino_plugin/                # NEW: C# Rhino plugin
│   ├── LatentPlugin.cs          # Plugin entry point
│   ├── Commands/                # Rhino commands
│   ├── UI/                      # Eto.Forms panels
│   ├── Display/                 # DisplayConduit implementations
│   ├── Geometry/                # Parametric region logic
│   ├── Analysis/                # Lens integration
│   └── Interop/                 # P/Invoke to cpp_core
├── analysis_service/            # NEW: Python lens service
│   ├── service.py               # JSON-RPC server
│   ├── protocol.py              # Request/response schemas
│   └── ...
└── ...
```

### 0.3 Decision: C# vs Python Plugin

**Recommendation: C# for plugin, Python for analysis**

| Component | Language | Reason |
|-----------|----------|--------|
| Plugin UI & interaction | C# | Best RhinoCommon integration, DisplayConduit, Eto.Forms |
| C++ core bindings | C (P/Invoke) | Cross-language compatibility |
| Lens analysis | Python | Keep existing scipy/numpy, run as subprocess |

---

## Phase 1: C++ Core Extensions (Week 1-2)

### 1.1 Inverse Surface Evaluation

**Location**: `cpp_core/geometry/subd_evaluator.h/.cpp`

**Add methods:**
```cpp
// Project 3D point onto limit surface
bool project_point_onto_surface(
    const Point3D& point,
    int& out_face_id,
    float& out_u,
    float& out_v,
    float tolerance = 1e-6f
);

// Find parametric coords from 3D point (assuming point IS on surface)
bool invert_surface_point(
    const Point3D& surface_point,
    int& out_face_id,
    float& out_u,
    float& out_v
);
```

**Algorithm**:
1. For each face, use Newton-Raphson iteration
2. Minimize `||evaluate_limit(face, u, v) - target||²`
3. Use derivatives from `evaluate_limit_with_derivatives()` for Jacobian
4. Return face with minimum residual

**Estimated**: 200-300 LOC, 2 days

### 1.2 Curve-on-Surface Evaluation

**Location**: NEW `cpp_core/geometry/surface_curve.h/.cpp`

```cpp
struct ParametricPoint {
    int face_id;
    float u, v;
};

class SurfaceCurve {
public:
    std::vector<ParametricPoint> control_points;
    CurveType type;  // BEZIER, BSPLINE, GEODESIC
    int degree;

    // Evaluate curve at parameter t ∈ [0,1]
    Point3D evaluate(float t, const SubDEvaluator& evaluator) const;

    // Get tangent at parameter t
    Vector3 tangent(float t, const SubDEvaluator& evaluator) const;

    // Sample curve for display
    std::vector<Point3D> sample(int num_points, const SubDEvaluator& evaluator) const;
};

// Project 3D curve onto surface
SurfaceCurve project_curve_to_surface(
    const std::vector<Point3D>& curve_3d,
    const SubDEvaluator& evaluator
);
```

**Estimated**: 250-300 LOC, 2 days

### 1.3 C-Binding Wrapper for P/Invoke

**Location**: NEW `cpp_core/c_bindings/rhino_wrapper.h/.cpp`

```cpp
extern "C" {
    // Handle types
    typedef void* SubDEvaluatorHandle;
    typedef void* SurfaceCurveHandle;

    // Lifecycle
    EXPORT SubDEvaluatorHandle latent_evaluator_create();
    EXPORT void latent_evaluator_destroy(SubDEvaluatorHandle h);
    EXPORT bool latent_evaluator_initialize(SubDEvaluatorHandle h,
        const float* vertices, int vertex_count,
        const int* faces, const int* face_sizes, int face_count,
        const int* creases, const float* crease_sharpness, int crease_count);

    // Forward evaluation
    EXPORT bool latent_evaluate_point(SubDEvaluatorHandle h,
        int face_id, float u, float v,
        float* out_x, float* out_y, float* out_z);

    // Inverse evaluation (NEW)
    EXPORT bool latent_project_point(SubDEvaluatorHandle h,
        float px, float py, float pz,
        int* out_face_id, float* out_u, float* out_v);

    // Curve evaluation (NEW)
    EXPORT SurfaceCurveHandle latent_curve_create(
        const int* face_ids, const float* us, const float* vs, int point_count,
        int curve_type, int degree);
    EXPORT void latent_curve_destroy(SurfaceCurveHandle h);
    EXPORT bool latent_curve_sample(SurfaceCurveHandle h, SubDEvaluatorHandle eval,
        int num_samples, float* out_points);

    // Curvature
    EXPORT bool latent_compute_curvature(SubDEvaluatorHandle h,
        int face_id, float u, float v,
        float* out_k1, float* out_k2, float* out_H, float* out_K);
}
```

**CMake update**: Build `latent_core.dll` / `liblatent_core.dylib`

**Estimated**: 300-400 LOC, 2 days

### 1.4 Build & Test

- [ ] Update CMakeLists.txt for shared library output
- [ ] Add C-binding unit tests
- [ ] Cross-compile for Windows (.dll) and macOS (.dylib)
- [ ] Verify P/Invoke works from simple C# test

---

## Phase 2: Python Analysis Service (Week 2)

### 2.1 JSON-RPC Protocol

**Location**: NEW `analysis_service/protocol.py`

```python
# Request schema
{
    "jsonrpc": "2.0",
    "method": "analyze",
    "params": {
        "lens": "differential" | "spectral",
        "cage": {
            "vertices": [[x,y,z], ...],
            "faces": [[i,j,k,...], ...],
            "creases": [[i,j,sharpness], ...]
        },
        "params": { ... lens-specific ... },
        "pinned_regions": [region_id, ...]
    },
    "id": 1
}

# Response schema
{
    "jsonrpc": "2.0",
    "result": {
        "regions": [
            {
                "id": "uuid",
                "boundary_curves": [
                    {
                        "control_points": [[face_id, u, v], ...],
                        "type": "bezier",
                        "degree": 3
                    }
                ],
                "unity_principle": "Convex: κ₁κ₂ > 0",
                "resonance_score": 0.87,
                "is_implicit": true
            }
        ],
        "vertices": [
            {
                "id": "uuid",
                "position": [face_id, u, v],
                "implicit_position": [face_id, u, v],
                "created_by": "lens"
            }
        ]
    },
    "id": 1
}
```

### 2.2 Lens Service Implementation

**Location**: NEW `analysis_service/service.py`

```python
class LensService:
    def __init__(self, port=5555):
        self.evaluator = None

    def handle_request(self, request: dict) -> dict:
        method = request["method"]
        params = request["params"]

        if method == "initialize":
            return self._initialize(params["cage"])
        elif method == "analyze":
            return self._analyze(params["lens"], params["params"])
        elif method == "get_boundary_curves":
            return self._extract_boundaries(params["regions"])
        ...

    def _analyze(self, lens_type, params):
        if lens_type == "differential":
            lens = DifferentialLens(self.evaluator)
            regions = lens.discover_regions(**params)
        elif lens_type == "spectral":
            lens = SpectralLens(self.evaluator)
            regions = lens.discover_regions(**params)

        # Extract boundary curves (NEW - must implement)
        for region in regions:
            region.boundary_curves = self._extract_boundary(region)

        return {"regions": [r.to_json() for r in regions]}
```

### 2.3 Boundary Curve Extraction (Critical New Feature)

**Location**: Update `app/analysis/differential_lens.py` and `spectral_lens.py`

**For Differential Lens**:
```python
def extract_boundary_curves(self, region: ParametricRegion) -> List[ParametricCurve]:
    """
    Extract boundary as curves where curvature crosses threshold.
    Uses marching squares on face grid to find contour.
    """
    # 1. For each face in region, sample curvature on fine grid
    # 2. Find edges where curvature crosses threshold
    # 3. Connect edges into curves
    # 4. Convert to parametric (face_id, u, v) representation
    pass
```

**For Spectral Lens**:
```python
def extract_nodal_curves(self, eigenfunction, threshold=0.0) -> List[ParametricCurve]:
    """
    Extract nodal lines where eigenfunction crosses zero.
    """
    # 1. For each triangle in tessellation
    # 2. Find edges where eigenfunction changes sign
    # 3. Interpolate zero-crossing position
    # 4. Connect into curves
    # 5. Project to parametric space
    pass
```

**Estimated**: 400-500 LOC, 3 days

### 2.4 Service Launcher

```python
# analysis_service/__main__.py
if __name__ == "__main__":
    import zmq  # or use HTTP
    service = LensService()

    context = zmq.Context()
    socket = context.socket(zmq.REP)
    socket.bind("tcp://*:5555")

    while True:
        request = socket.recv_json()
        response = service.handle_request(request)
        socket.send_json(response)
```

---

## Phase 3: Rhino Plugin Foundation (Week 3-4)

### 3.1 Plugin Project Setup

**Location**: NEW `rhino_plugin/`

```
rhino_plugin/
├── LatentPlugin.csproj
├── LatentPlugin.cs              # RhinoPlugin entry
├── LatentPluginCommand.cs       # Main command
├── Properties/
│   └── AssemblyInfo.cs
└── packages.config               # NuGet: RhinoCommon, Eto.Forms
```

### 3.2 P/Invoke Bindings

**Location**: `rhino_plugin/Interop/NativeCore.cs`

```csharp
public static class NativeCore
{
    private const string DllName = "latent_core";

    [DllImport(DllName)]
    public static extern IntPtr latent_evaluator_create();

    [DllImport(DllName)]
    public static extern void latent_evaluator_destroy(IntPtr handle);

    [DllImport(DllName)]
    public static extern bool latent_evaluator_initialize(
        IntPtr handle,
        [MarshalAs(UnmanagedType.LPArray)] float[] vertices, int vertexCount,
        [MarshalAs(UnmanagedType.LPArray)] int[] faces,
        [MarshalAs(UnmanagedType.LPArray)] int[] faceSizes, int faceCount,
        [MarshalAs(UnmanagedType.LPArray)] int[] creases,
        [MarshalAs(UnmanagedType.LPArray)] float[] creaseSharpness, int creaseCount);

    [DllImport(DllName)]
    public static extern bool latent_evaluate_point(
        IntPtr handle, int faceId, float u, float v,
        out float x, out float y, out float z);

    [DllImport(DllName)]
    public static extern bool latent_project_point(
        IntPtr handle, float px, float py, float pz,
        out int faceId, out float u, out float v);
}
```

### 3.3 Managed Wrapper

**Location**: `rhino_plugin/Interop/SubDEvaluator.cs`

```csharp
public class SubDEvaluator : IDisposable
{
    private IntPtr _handle;

    public SubDEvaluator()
    {
        _handle = NativeCore.latent_evaluator_create();
    }

    public void Initialize(SubD subd)
    {
        // Extract control cage from Rhino SubD (using ControlNetPoint, not limit surface)
        var (vertices, faces, faceSizes, creaseEdges, creaseSharpness) = ExtractCage(subd);
        NativeCore.latent_evaluator_initialize(_handle, ...);
    }

    public Point3d EvaluatePoint(int faceId, double u, double v)
    {
        NativeCore.latent_evaluate_point(_handle, faceId, (float)u, (float)v,
            out float x, out float y, out float z);
        return new Point3d(x, y, z);
    }

    /// <summary>
    /// Project a 3D point onto the limit surface.
    /// Returns ParametricPoint with IsValid=false if projection fails.
    /// </summary>
    public ParametricPoint ProjectPoint(Point3d point)
    {
        if (!NativeCore.latent_project_point(_handle,
                (float)point.X, (float)point.Y, (float)point.Z,
                out int faceId, out float u, out float v))
        {
            return ParametricPoint.Unset;  // Invalid point
        }
        return new ParametricPoint(faceId, u, v);
    }

    /// <summary>
    /// Project a 3D point onto the limit surface with out parameters.
    /// </summary>
    public bool ProjectPoint(Point3d point, out int faceId, out float u, out float v)
    {
        return NativeCore.latent_project_point(_handle,
            (float)point.X, (float)point.Y, (float)point.Z,
            out faceId, out u, out v);
    }

    /// <summary>
    /// Get the surface normal at a parametric point.
    /// Returns null if evaluation fails.
    /// </summary>
    public Vector3d? GetNormal(int faceId, float u, float v)
    {
        if (!NativeCore.latent_evaluate_normal(_handle, faceId, u, v,
                out float nx, out float ny, out float nz))
        {
            return null;
        }
        return new Vector3d(nx, ny, nz);
    }

    public void Dispose()
    {
        if (_handle != IntPtr.Zero)
        {
            NativeCore.latent_evaluator_destroy(_handle);
            _handle = IntPtr.Zero;
        }
    }
}
```

### 3.4 Analysis Service Client

**Location**: `rhino_plugin/Analysis/LensClient.cs`

```csharp
public class LensClient
{
    private readonly Process _pythonProcess;
    private readonly ZmqSocket _socket;  // or HttpClient

    public async Task<AnalysisResult> AnalyzeAsync(
        string lensType,
        SubD subd,
        Dictionary<string, object> parameters)
    {
        var request = new {
            jsonrpc = "2.0",
            method = "analyze",
            @params = new {
                lens = lensType,
                cage = ExtractCage(subd),
                @params = parameters
            },
            id = Guid.NewGuid().ToString()
        };

        var response = await SendRequestAsync(request);
        return ParseAnalysisResult(response);
    }
}
```

---

## Phase 4: Display & Visualization (Week 4-5)

### 4.1 Region Display Conduit

**Location**: `rhino_plugin/Display/RegionConduit.cs`

```csharp
public class RegionConduit : DisplayConduit
{
    private readonly RegionManager _regionManager;
    private readonly VisualizationSettings _settings;

    protected override void CalculateBoundingBox(CalculateBoundingBoxEventArgs e)
    {
        // Include all region geometry
        foreach (var region in _regionManager.Regions)
        {
            e.IncludeBoundingBox(region.BoundingBox);
        }
    }

    protected override void PostDrawObjects(DrawEventArgs e)
    {
        // Draw boundary curves
        foreach (var region in _regionManager.Regions)
        {
            var color = GetRegionColor(region);
            var thickness = region.IsSelected ? 3.0f : 1.5f;

            foreach (var curve in region.BoundaryCurves)
            {
                var points = SampleCurve(curve, 50);
                e.Display.DrawPolyline(points, color, (int)thickness);
            }
        }

        // Draw vertices (region intersection points)
        foreach (var vertex in _regionManager.Vertices)
        {
            var style = vertex.IsPinned ? PointStyle.Pin : PointStyle.Circle;
            var color = vertex.IsSelected ? Color.Yellow : Color.White;
            e.Display.DrawPoint(vertex.Position, style, 5, color);
        }
    }

    protected override void DrawForeground(DrawEventArgs e)
    {
        // Draw region fills (transparent) if enabled
        if (_settings.ShowRegionFill)
        {
            foreach (var region in _regionManager.Regions)
            {
                var color = GetRegionColor(region);
                var fillColor = Color.FromArgb(64, color);  // 25% opacity

                // Draw as hatch or transparent mesh
                e.Display.DrawHatch(region.FillHatch, fillColor, Color.Empty);
            }
        }

        // Draw centroid markers if enabled
        if (_settings.ShowCentroidMarkers)
        {
            foreach (var region in _regionManager.Regions)
            {
                var centroid = region.Centroid;
                e.Display.DrawDot(centroid, region.Id, Color.Black, Color.White);
            }
        }
    }

    private Color GetRegionColor(Region region)
    {
        if (region.IsSelected) return Color.Yellow;
        if (region.IsPinned) return Color.FromArgb(100, 150, 255);  // Blue
        return Color.FromArgb(200, 200, 200);  // Gray
    }
}
```

### 4.2 Curve Sampling on Surface

**Location**: `rhino_plugin/Geometry/CurveSampler.cs`

```csharp
public class CurveSampler
{
    private readonly SubDEvaluator _evaluator;

    public List<Point3d> SampleCurve(ParametricCurve curve, int numSamples)
    {
        var points = new List<Point3d>();

        for (int i = 0; i <= numSamples; i++)
        {
            double t = i / (double)numSamples;
            var (faceId, u, v) = curve.Evaluate(t);
            var point = _evaluator.EvaluatePoint(faceId, u, v);
            points.Add(point);
        }

        return points;
    }
}
```

---

## Phase 5: Interaction & Selection (Week 5-6)

### 5.1 Surface-Constrained GetPoint

**Location**: `rhino_plugin/Interaction/SurfaceConstrainedGetPoint.cs`

**Uses**: `Latent.Interop.ParametricPoint` (shared struct with `Unset` property)

```csharp
public class SurfaceConstrainedGetPoint : GetPoint
{
    private readonly SubD _subd;
    private readonly SubDEvaluator _evaluator;
    private ParametricPoint _currentParam;  // Uses Latent.Interop.ParametricPoint
    private Point3d _currentPoint3d = Point3d.Unset;
    private Vector3d _currentNormal = Vector3d.Unset;

    /// <summary>
    /// The current parametric position on the surface.
    /// Updated during mouse move. Check IsValid before using.
    /// </summary>
    public ParametricPoint CurrentParametricPosition => _currentParam;

    /// <summary>
    /// Whether the current parametric position is valid.
    /// </summary>
    public bool HasValidPosition => _currentParam.IsValid;

    /// <summary>
    /// The current 3D point on the surface.
    /// </summary>
    public Point3d CurrentSurfacePoint => _currentPoint3d;

    /// <summary>
    /// The surface normal at the current point.
    /// </summary>
    public Vector3d CurrentNormal => _currentNormal;

    public SurfaceConstrainedGetPoint(SubD subd, SubDEvaluator evaluator)
    {
        _subd = subd ?? throw new ArgumentNullException(nameof(subd));
        _evaluator = evaluator ?? throw new ArgumentNullException(nameof(evaluator));

        // Constrain to SubD surface
        Constrain(_subd, allowPickingPointOffObject: false);

        // Enable dynamic drawing for visual feedback
        DynamicDraw += OnDynamicDraw;
    }

    protected override void OnMouseMove(GetPointMouseEventArgs e)
    {
        base.OnMouseMove(e);

        // Project current point to surface parametric space
        if (_evaluator.ProjectPoint(e.Point, out int faceId, out float u, out float v))
        {
            _currentParam = new ParametricPoint(faceId, u, v);
            _currentPoint3d = _evaluator.EvaluatePoint(faceId, u, v);
        }
        else
        {
            _currentParam = ParametricPoint.Unset;
            _currentPoint3d = Point3d.Unset;
        }
    }
}
```

### 5.2 Vertex Drag Operation

**Location**: `rhino_plugin/Interaction/VertexDragHandler.cs`

**Uses**: `Latent.Interop.ParametricPoint`, `RegionManager.MoveVertex(Vertex, ParametricPoint)`

```csharp
public class VertexDragHandler
{
    private readonly RegionManager _regionManager;
    private readonly SubDEvaluator _evaluator;
    private readonly SubD _subd;
    private readonly DragPreview _preview;

    public VertexDragHandler(RegionManager regionManager, SubDEvaluator evaluator, SubD subd)
    {
        _regionManager = regionManager ?? throw new ArgumentNullException(nameof(regionManager));
        _evaluator = evaluator ?? throw new ArgumentNullException(nameof(evaluator));
        _subd = subd ?? throw new ArgumentNullException(nameof(subd));
        _preview = new DragPreview(evaluator);
    }

    public DragResult StartDrag(Vertex vertex)
    {
        if (vertex == null) throw new ArgumentNullException(nameof(vertex));

        // Check if vertex is pinned
        if (vertex.IsPinned)
        {
            RhinoApp.WriteLine("Cannot drag pinned vertex. Unpin first.");
            return DragResult.Pinned;
        }

        var originalParam = vertex.Position;
        var originalPos3d = _evaluator.EvaluatePoint(
            originalParam.FaceId, originalParam.U, originalParam.V);

        var gp = new SurfaceConstrainedGetPoint(_subd, _evaluator);
        gp.SetCommandPrompt("Drag vertex to new position (ESC to cancel)");
        gp.SetBasePoint(originalPos3d, showDistanceInStatusBar: true);

        // Add dynamic draw for preview
        gp.DynamicDraw += (sender, e) => {
            var previewParam = gp.CurrentParametricPosition;
            _preview.DrawVertexPreview(e.Display, vertex, previewParam);
        };

        var result = gp.Get();

        if (result == GetResult.Point)
        {
            var newParam = gp.CurrentParametricPosition;
            if (newParam.IsValid)
            {
                // Apply the move through RegionManager (creates undo record)
                _regionManager.MoveVertex(vertex, newParam);
                return DragResult.Success;
            }
        }

        return DragResult.Canceled;
    }
}
```

### 5.3 Edge Drag Operation

**Location**: `rhino_plugin/Interaction/EdgeDragHandler.cs`

```csharp
public class EdgeDragHandler
{
    public void StartDrag(Edge edge)
    {
        // Get all vertices on this edge
        var vertices = edge.Vertices;

        var gp = new SurfaceConstrainedGetPoint(_subd, _evaluator);
        gp.SetCommandPrompt("Drag edge to new position");

        // Calculate initial centroid
        var centroid = CalculateCentroid(vertices);
        gp.SetBasePoint(centroid, showDistanceInStatusBar: true);

        gp.DynamicDraw += (sender, e) => {
            // Calculate displacement vector
            var displacement = gp.Point() - centroid;

            // Preview all vertices moved by same vector
            foreach (var v in vertices)
            {
                var newPos3d = v.Position + displacement;
                // Project back to surface
                var (faceId, u, v_param) = _evaluator.ProjectPoint(newPos3d);
                var projectedPos = _evaluator.EvaluatePoint(faceId, u, v_param);
                e.Display.DrawPoint(projectedPos, PointStyle.Circle, 6, Color.Yellow);
            }
        };

        if (gp.Get() == GetResult.Point)
        {
            var displacement = gp.Point() - centroid;
            _regionManager.MoveEdge(edge, displacement);
        }
    }
}
```

### 5.4 Region Selection

**Location**: `rhino_plugin/Interaction/RegionPicker.cs`

**Uses**: `RegionManager.FindRegionContaining(int faceId, float u, float v)` with winding number algorithm

```csharp
public class RegionPicker
{
    private readonly RegionManager _regionManager;
    private readonly SubDEvaluator _evaluator;
    private readonly SubD _subd;

    public RegionPicker(RegionManager regionManager, SubDEvaluator evaluator, SubD subd)
    {
        _regionManager = regionManager ?? throw new ArgumentNullException(nameof(regionManager));
        _evaluator = evaluator ?? throw new ArgumentNullException(nameof(evaluator));
        _subd = subd ?? throw new ArgumentNullException(nameof(subd));
    }

    public Region PickRegion()
    {
        var gp = new SurfaceConstrainedGetPoint(_subd, _evaluator);
        gp.SetCommandPrompt("Pick point on region");

        // Add hover highlighting
        gp.DynamicDraw += (sender, e) => {
            var param = gp.CurrentParametricPosition;
            if (!param.IsValid) return;

            var region = _regionManager.FindRegionContaining(
                param.FaceId, (float)param.U, (float)param.V);

            if (region != null)
            {
                DrawRegionHighlight(e.Display, region);
            }
        };

        if (gp.Get() == GetResult.Point)
        {
            var param = gp.CurrentParametricPosition;
            if (param.IsValid)
            {
                // Find which region contains this parametric point
                // Uses winding number algorithm for point-in-polygon test
                return _regionManager.FindRegionContaining(
                    param.FaceId, (float)param.U, (float)param.V);
            }
        }

        return null;
    }
}
```

---

## Phase 6: UI Panels (Week 6-7)

### 6.1 Geometry List Panel

**Location**: `rhino_plugin/UI/GeometryListPanel.cs`

```csharp
public class GeometryListPanel : Panel
{
    private readonly GridView _gridView;
    private readonly DropDown _modeSelector;

    public GeometryListPanel()
    {
        _modeSelector = new DropDown {
            Items = { "Vertices", "Edges", "Regions" }
        };
        _modeSelector.SelectedIndexChanged += OnModeChanged;

        _gridView = new GridView {
            Columns = {
                new GridColumn { HeaderText = "ID", DataCell = new TextBoxCell("Id") },
                new GridColumn { HeaderText = "State", DataCell = new TextBoxCell("State") },
                new GridColumn { HeaderText = "Pinned", DataCell = new CheckBoxCell("IsPinned") },
                new GridColumn { HeaderText = "", DataCell = new ButtonCell("Revert") }
            }
        };

        Content = new StackLayout {
            Items = { _modeSelector, _gridView }
        };
    }

    private void OnRevertClicked(object sender, GridViewCellEventArgs e)
    {
        var item = e.Item as GeometryListItem;

        if (item.IsPinned)
        {
            MessageBox.Show("Unpin before reverting");
            return;
        }

        if (item.Type == "Vertex" && item.CreatedBy == "curve_modification")
        {
            var result = MessageBox.Show(
                "This vertex was added during curve modification. Revert curve type first?",
                MessageBoxButtons.YesNo);

            if (result == DialogResult.Yes)
            {
                _regionManager.RevertEdgeCurveType(item.ParentEdge);
            }
            return;
        }

        if (item.Type == "Edge")
        {
            var dialog = new EdgeRevertDialog();
            if (dialog.ShowModal() == DialogResult.Ok)
            {
                if (dialog.RevertTypeOnly)
                    _regionManager.RevertEdgeCurveType(item.Edge);
                else
                    _regionManager.RevertEdgeFully(item.Edge);
            }
            return;
        }

        _regionManager.Revert(item);
    }
}
```

### 6.2 Lens Control Panel

**Location**: `rhino_plugin/UI/LensPanel.cs`

```csharp
public class LensPanel : Panel
{
    private readonly DropDown _lensSelector;
    private readonly DynamicLayout _parameterPanel;

    public LensPanel()
    {
        _lensSelector = new DropDown {
            Items = { "Differential (Curvature)", "Spectral (Eigenfunction)" }
        };
        _lensSelector.SelectedIndexChanged += OnLensChanged;

        _parameterPanel = new DynamicLayout();

        var analyzeButton = new Button { Text = "Analyze" };
        analyzeButton.Click += OnAnalyzeClicked;

        Content = new StackLayout {
            Items = { _lensSelector, _parameterPanel, analyzeButton }
        };
    }

    private async void OnAnalyzeClicked(object sender, EventArgs e)
    {
        var lens = _lensSelector.SelectedKey;
        var parameters = GetParameters();

        var result = await _lensClient.AnalyzeAsync(lens, _subd, parameters);
        _regionManager.UpdateFromAnalysis(result);
    }
}
```

### 6.3 Visualization Settings Panel

**Location**: `rhino_plugin/UI/VisualizationPanel.cs`

```csharp
public class VisualizationPanel : Panel
{
    public VisualizationPanel()
    {
        var fillCheck = new CheckBox { Text = "Show region fill" };
        fillCheck.CheckedChanged += (s, e) =>
            _settings.ShowRegionFill = fillCheck.Checked ?? false;

        var centroidCheck = new CheckBox { Text = "Show centroid markers" };
        centroidCheck.CheckedChanged += (s, e) =>
            _settings.ShowCentroidMarkers = centroidCheck.Checked ?? false;

        var selectedColorPicker = new ColorPicker { Value = Colors.Yellow };
        var pinnedColorPicker = new ColorPicker { Value = Colors.LightBlue };

        Content = new StackLayout {
            Items = {
                fillCheck,
                centroidCheck,
                new Label { Text = "Selected color:" }, selectedColorPicker,
                new Label { Text = "Pinned color:" }, pinnedColorPicker
            }
        };
    }
}
```

---

## Phase 7: State Management (Week 7)

### 7.1 Region Manager

**Location**: `rhino_plugin/Geometry/RegionManager.cs`

**Key APIs** (implemented in Phase 3):
- `MoveVertex(string vertexId, ParametricPoint)` - by ID
- `MoveVertex(Vertex vertex, ParametricPoint)` - by reference (for Phase 5 drag handlers)
- `FindRegionContaining(int faceId, float u, float v)` - winding number algorithm
- `FindRegionContaining(ParametricPoint)` - overload

```csharp
public class RegionManager
{
    private readonly Dictionary<string, Region> _regions = new();
    private readonly Dictionary<string, Edge> _edges = new();
    private readonly Dictionary<string, Vertex> _vertices = new();

    public IReadOnlyCollection<Region> Regions => _regions.Values;
    public IReadOnlyCollection<Edge> Edges => _edges.Values;
    public IReadOnlyCollection<Vertex> Vertices => _vertices.Values;

    public event EventHandler? Changed;

    /// <summary>
    /// Move a vertex to a new position by vertex ID.
    /// </summary>
    public void MoveVertex(string vertexId, ParametricPoint newPosition)
    {
        var vertex = GetVertex(vertexId);
        if (vertex == null) return;
        MoveVertexInternal(vertex, newPosition);
    }

    /// <summary>
    /// Move a vertex to a new position (for drag handlers).
    /// </summary>
    public void MoveVertex(Vertex vertex, ParametricPoint newPosition)
    {
        if (vertex == null) throw new ArgumentNullException(nameof(vertex));
        if (!_vertices.ContainsKey(vertex.Id))
            throw new ArgumentException("Vertex is not managed by this RegionManager");
        MoveVertexInternal(vertex, newPosition);
    }

    private void MoveVertexInternal(Vertex vertex, ParametricPoint newPosition)
    {
        var oldPosition = vertex.Position;

        // Register undo with Rhino's undo system
        var undoEvent = new MoveVertexUndoEvent(vertex.Id, oldPosition, newPosition);
        RhinoUndoHelper.RegisterUndo(RhinoDoc.ActiveDoc, undoEvent, this);

        vertex.Position = newPosition;
        InvalidateGeometry();
        OnChanged();
    }

    /// <summary>
    /// Find the region containing the given parametric point.
    /// Uses winding number algorithm for point-in-polygon test in parametric space.
    /// </summary>
    public Region? FindRegionContaining(int faceId, float u, float v)
    {
        var testPoint = new ParametricPoint(faceId, u, v);
        return FindRegionContaining(testPoint);
    }

    public Region? FindRegionContaining(ParametricPoint param)
    {
        if (!param.IsValid) return null;

        foreach (var region in _regions.Values)
        {
            if (RegionContainsPoint(region, param))
                return region;
        }
        return null;
    }

    // Winding number algorithm implementation...
}
```

### 7.2 Undo/Redo System

**Location**: `rhino_plugin/Geometry/UndoStack.cs`

```csharp
public interface IUndoAction
{
    void Undo();
    void Redo();
    string Description { get; }
}

public class UndoStack
{
    private readonly Stack<IUndoAction> _undoStack = new();
    private readonly Stack<IUndoAction> _redoStack = new();

    public void Push(IUndoAction action)
    {
        _undoStack.Push(action);
        _redoStack.Clear();
    }

    public void Undo()
    {
        if (_undoStack.Count == 0) return;
        var action = _undoStack.Pop();
        action.Undo();
        _redoStack.Push(action);
    }

    public void Redo()
    {
        if (_redoStack.Count == 0) return;
        var action = _redoStack.Pop();
        action.Redo();
        _undoStack.Push(action);
    }
}
```

---

## Phase 8: Integration & Testing (Week 8)

### 8.1 Integration Tests

- [ ] C++ → C# P/Invoke round-trip
- [ ] Python analysis service JSON protocol
- [ ] Full analysis workflow: SubD → Lens → Regions
- [ ] Vertex/edge/region manipulation
- [ ] Undo/redo all operations
- [ ] Pin/unpin/revert workflows
- [ ] Display conduit rendering
- [ ] Surface-constrained picking

### 8.2 Performance Testing

- [ ] Large SubD (1000+ faces) analysis time
- [ ] Display conduit frame rate with many regions
- [ ] Python service latency

### 8.3 User Acceptance Testing

- [ ] Load SubD, run differential lens, pin regions
- [ ] Edit curve degree, add control points
- [ ] Revert operations at all levels
- [ ] Switch lenses, compare results
- [ ] Export workflow (future phase)

---

## Deliverables Summary

| Phase | Duration | Key Deliverables |
|-------|----------|------------------|
| 0. Setup | 1 week | Dev environment, project structure |
| 1. C++ Core | 1 week | Inverse eval, curves, C bindings |
| 2. Python Service | 1 week | JSON-RPC server, boundary extraction |
| 3. Plugin Foundation | 1.5 weeks | P/Invoke, managed wrappers, lens client |
| 4. Display | 1 week | RegionConduit, curve sampling |
| 5. Interaction | 1 week | Constrained GetPoint, drag handlers |
| 6. UI Panels | 1 week | Geometry list, lens panel, settings |
| 7. State | 0.5 weeks | RegionManager, undo/redo |
| 8. Testing | 1 week | Integration, performance, UAT |

**Total: 8 weeks**

---

## Risk Mitigation

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| P/Invoke marshaling issues | Medium | High | Early prototype in Phase 1 |
| Python service latency | Low | Medium | Use ZMQ, optimize serialization |
| DisplayConduit performance | Medium | Medium | Culling, LOD, caching |
| Boundary extraction complexity | Medium | High | Start with simple contour, iterate |
| Cross-platform builds | Medium | Medium | CI/CD for Windows + macOS early |

---

## Future Phases (Not in Scope)

- NURBS mold generation export
- Constraint validation visualization
- Multi-SubD support
- Rhino document persistence
- Material/thermal lenses
