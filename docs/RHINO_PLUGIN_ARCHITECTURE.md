# Rhino Plugin Architecture: SubD Editor

## Overview

A RhinoCommon plugin that enables direct manipulation of SubD boundary curves
constrained to the Form surface. The plugin handles viewport interaction while
the existing C++/Python engine handles geometry and analysis.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              RHINO 8                                         │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌────────────────────────────────────────────────────────────────────────┐ │
│  │                     SubDEditorPlugin (C#)                              │ │
│  │                                                                        │ │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐                 │ │
│  │  │ Commands     │  │ EditMode     │  │ Display      │                 │ │
│  │  │              │  │              │  │ Conduit      │                 │ │
│  │  │ • Analyze    │  │ • OnMouseDown│  │              │                 │ │
│  │  │ • EditSubD   │  │ • OnMouseMove│  │ • DrawCurves │                 │ │
│  │  │ • PinRegion  │  │ • OnMouseUp  │  │ • DrawPoints │                 │ │
│  │  │ • Export     │  │ • Constraints│  │ • Highlights │                 │ │
│  │  └──────────────┘  └──────────────┘  └──────────────┘                 │ │
│  │         │                 │                 ▲                          │ │
│  │         │                 │                 │                          │ │
│  │         ▼                 ▼                 │                          │ │
│  │  ┌─────────────────────────────────────────────────────────────────┐  │ │
│  │  │                    SubDState (in plugin)                        │  │ │
│  │  │                                                                 │  │ │
│  │  │  • Form reference (Rhino SubD object GUID)                      │  │ │
│  │  │  • Boundary curves (parametric: face_id, u, v points)           │  │ │
│  │  │  • Regions (face assignments, pin states)                       │  │ │
│  │  │  • Selection state                                              │  │ │
│  │  └─────────────────────────────────────────────────────────────────┘  │ │
│  │         │                                                              │ │
│  │         │ HTTP/WebSocket                                               │ │
│  │         ▼                                                              │ │
│  └─────────┼──────────────────────────────────────────────────────────────┘ │
│            │                                                                 │
└────────────┼─────────────────────────────────────────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                        ANALYSIS ENGINE (Python + C++)                        │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐          │
│  │ HTTP Server     │    │ SubDEvaluator   │    │ Analysis Lenses │          │
│  │                 │    │ (C++/OpenSubdiv)│    │                 │          │
│  │ /analyze        │───▶│                 │───▶│ • Differential  │          │
│  │ /evaluate       │    │ • evaluate_limit│    │ • Spectral      │          │
│  │ /project        │    │ • derivatives   │    │ • Flow          │          │
│  └─────────────────┘    └─────────────────┘    └─────────────────┘          │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Plugin Components

### 1. Commands

```csharp
// SubDAnalyzeCommand.cs
[CommandStyle(Style.ScriptRunner)]
public class SubDAnalyzeCommand : Command
{
    public override string EnglishName => "SubDAnalyze";

    protected override Result RunCommand(RhinoDoc doc, RunMode mode)
    {
        // 1. Get Form SubD from user selection
        var go = new GetObject();
        go.SetCommandPrompt("Select Form (SubD)");
        go.GeometryFilter = ObjectType.SubD;
        go.Get();

        if (go.CommandResult() != Result.Success)
            return go.CommandResult();

        var formId = go.Object(0).ObjectId;
        var formSubD = go.Object(0).SubD();

        // 2. Extract control cage
        var controlCage = ExtractControlCage(formSubD);

        // 3. Send to analysis engine
        var response = await AnalysisClient.Analyze(controlCage, "differential");

        // 4. Create boundary curves from response
        var boundaries = CreateBoundaryCurves(formSubD, response.Boundaries);

        // 5. Add to document in SubD layer
        var layer = GetOrCreateLayer(doc, "SubD_Boundaries");
        foreach (var curve in boundaries)
        {
            doc.Objects.AddCurve(curve, new ObjectAttributes { LayerIndex = layer.Index });
        }

        // 6. Store state
        SubDState.Instance.SetForm(formId);
        SubDState.Instance.SetBoundaries(response.Boundaries);

        doc.Views.Redraw();
        return Result.Success;
    }
}
```

### 2. Edit Mode (Constrained Manipulation)

```csharp
// SubDEditMode.cs
public class SubDEditMode : MouseCallback
{
    private Guid _selectedCurve;
    private Point3d _dragStart;
    private bool _isDragging;

    protected override void OnMouseDown(MouseCallbackEventArgs e)
    {
        if (e.Button != MouseButtons.Left) return;

        // Pick test against boundary curves
        var picked = PickBoundaryCurve(e.View, e.ViewportPoint);
        if (picked != Guid.Empty)
        {
            _selectedCurve = picked;
            _dragStart = e.Point;
            _isDragging = true;

            // Highlight selection
            SubDState.Instance.SetSelected(_selectedCurve);
            e.View.Redraw();
        }
    }

    protected override void OnMouseMove(MouseCallbackEventArgs e)
    {
        if (!_isDragging) return;

        // Get Form surface
        var form = SubDState.Instance.GetForm();
        if (form == null) return;

        // Ray-cast to Form surface
        var ray = e.View.ActiveViewport.ClientToWorld(e.ViewportPoint);

        Point3d hitPoint;
        ComponentIndex ci;
        double u, v;

        if (form.ClosestPoint(ray.PointAt(0), ray.Direction,
                              out hitPoint, out ci, out u, out v))
        {
            // Get face_id from ComponentIndex
            int faceId = ci.Index;

            // Update boundary curve in parametric space
            var boundary = SubDState.Instance.GetSelectedBoundary();
            boundary.MoveToParameter(faceId, u, v);

            // Regenerate display curve
            var displayCurve = EvaluateBoundaryOnSurface(form, boundary);
            SubDState.Instance.SetDisplayCurve(_selectedCurve, displayCurve);

            // Redraw
            e.View.Redraw();
        }
    }

    protected override void OnMouseUp(MouseCallbackEventArgs e)
    {
        if (!_isDragging) return;

        _isDragging = false;

        // Commit the change
        var boundary = SubDState.Instance.GetSelectedBoundary();

        // Send updated boundary to analysis engine for validation
        var response = await AnalysisClient.ValidateBoundary(boundary);

        if (!response.Valid)
        {
            // Revert or show warning
            RhinoApp.WriteLine($"Warning: {response.Message}");
        }

        // Update Rhino curve object
        UpdateCurveInDocument(_selectedCurve, boundary);
    }
}
```

### 3. Display Conduit (Real-time Visualization)

```csharp
// SubDDisplayConduit.cs
public class SubDDisplayConduit : DisplayConduit
{
    protected override void DrawOverlay(DrawEventArgs e)
    {
        var state = SubDState.Instance;
        if (!state.HasForm) return;

        // Draw boundary curves
        foreach (var boundary in state.GetBoundaries())
        {
            var color = GetBoundaryColor(boundary);
            var curve = state.GetDisplayCurve(boundary.Id);

            if (curve != null)
            {
                e.Display.DrawCurve(curve, color, 2);
            }
        }

        // Draw selection highlight
        if (state.HasSelection)
        {
            var selected = state.GetSelectedDisplayCurve();
            e.Display.DrawCurve(selected, Color.Yellow, 4);

            // Draw control points
            foreach (var pt in state.GetSelectedControlPoints())
            {
                e.Display.DrawPoint(pt, PointStyle.ControlPoint, 5, Color.Yellow);
            }
        }

        // Draw region colors (semi-transparent fills)
        foreach (var region in state.GetRegions())
        {
            var mesh = state.GetRegionDisplayMesh(region.Id);
            var color = GetRegionColor(region);

            e.Display.DrawMeshShaded(mesh, new DisplayMaterial(color, 0.3));
        }
    }

    private Color GetBoundaryColor(Boundary b)
    {
        if (b.IsPinned) return Color.Cyan;      // Pinned
        if (b.IsSelected) return Color.Yellow;  // Selected
        return Color.White;                      // Default
    }

    private Color GetRegionColor(Region r)
    {
        if (r.IsPinned) return Color.FromArgb(50, 0, 200, 255);   // Pinned: blue tint
        if (r.IsSelected) return Color.FromArgb(50, 255, 255, 0); // Selected: yellow tint
        return Color.FromArgb(30, 128, 128, 128);                  // Default: gray tint
    }
}
```

---

## Communication Protocol

### HTTP Endpoints (Analysis Engine)

```
POST /analyze
  Request:  { control_cage: {...}, lens: "differential" }
  Response: { boundaries: [...], regions: [...] }

POST /evaluate
  Request:  { face_id: int, u: float, v: float }
  Response: { point: [x,y,z], normal: [x,y,z] }

POST /project
  Request:  { point: [x,y,z], direction: [x,y,z] }
  Response: { face_id: int, u: float, v: float }

POST /validate_boundary
  Request:  { boundary: {...} }
  Response: { valid: bool, message: string }

POST /update_boundary
  Request:  { boundary_id: string, new_params: [...] }
  Response: { success: bool, affected_regions: [...] }
```

### Data Structures

```csharp
// Parametric boundary (the truth)
public class ParametricBoundary
{
    public string Id { get; set; }
    public List<ParametricPoint> Points { get; set; }  // (face_id, u, v)
    public bool IsClosed { get; set; }
    public bool IsPinned { get; set; }
}

public class ParametricPoint
{
    public int FaceId { get; set; }
    public double U { get; set; }
    public double V { get; set; }
}

// Region (collection of faces)
public class Region
{
    public string Id { get; set; }
    public List<int> FaceIds { get; set; }
    public bool IsPinned { get; set; }
    public string UnityPrinciple { get; set; }  // Which lens created this
    public double UnityStrength { get; set; }    // Resonance score
}
```

---

## User Workflow

```
1. SETUP
   ┌─────────────────────────────────────────────────────────────┐
   │ User has Form (SubD) in Rhino                               │
   │ > SubDAnalyze                                                │
   │ Select Form: [clicks SubD]                                   │
   │ Lens: [Differential/Spectral/Flow]                          │
   │                                                              │
   │ → Analysis runs                                              │
   │ → Boundary curves appear on Form                             │
   │ → Regions shown with subtle color tints                      │
   └─────────────────────────────────────────────────────────────┘

2. EDIT
   ┌─────────────────────────────────────────────────────────────┐
   │ > SubDEdit                                                   │
   │ [Edit mode active - cursor changes]                          │
   │                                                              │
   │ Click boundary curve → highlights yellow                     │
   │ Drag curve → slides along Form surface                       │
   │ Release → curve snaps to new position                        │
   │                                                              │
   │ Click region → highlights yellow                             │
   │ Right-click → context menu:                                  │
   │   • Pin Region (locks it)                                    │
   │   • Merge with Adjacent                                      │
   │   • Split at Point                                           │
   │   • Delete Boundary                                          │
   │                                                              │
   │ ESC or Enter → exit edit mode                                │
   └─────────────────────────────────────────────────────────────┘

3. ITERATE
   ┌─────────────────────────────────────────────────────────────┐
   │ > SubDAnalyze (run again with different lens)               │
   │                                                              │
   │ Pinned regions/boundaries are preserved                      │
   │ Unpinned elements are recalculated                           │
   │                                                              │
   │ User can mix: analyze with Differential, pin some regions,   │
   │ then analyze with Spectral for remaining areas               │
   └─────────────────────────────────────────────────────────────┘

4. EXPORT
   ┌─────────────────────────────────────────────────────────────┐
   │ > SubDExport                                                 │
   │                                                              │
   │ → Boundaries become parting surfaces                         │
   │ → Regions become mold pieces                                 │
   │ → NURBS surfaces generated                                   │
   │ → Mold solids created                                        │
   │ → G-code/STL output (SINGLE APPROXIMATION)                   │
   └─────────────────────────────────────────────────────────────┘
```

---

## Project Structure

```
RhinoSubDEditor/
├── RhinoSubDEditor.sln
├── RhinoSubDEditor/
│   ├── RhinoSubDEditor.csproj
│   ├── Plugin.cs                 # Plugin entry point
│   ├── Commands/
│   │   ├── SubDAnalyzeCommand.cs
│   │   ├── SubDEditCommand.cs
│   │   ├── SubDPinCommand.cs
│   │   └── SubDExportCommand.cs
│   ├── EditMode/
│   │   ├── SubDEditMode.cs       # Mouse callback for manipulation
│   │   ├── BoundaryDragger.cs    # Constrained curve dragging
│   │   └── RegionPicker.cs       # Region selection
│   ├── Display/
│   │   ├── SubDDisplayConduit.cs # Real-time overlay drawing
│   │   └── ColorScheme.cs        # Consistent coloring
│   ├── State/
│   │   ├── SubDState.cs          # Singleton state manager
│   │   ├── ParametricBoundary.cs
│   │   └── Region.cs
│   ├── Communication/
│   │   ├── AnalysisClient.cs     # HTTP client to Python engine
│   │   └── ControlCageExtractor.cs
│   └── Utilities/
│       ├── SurfaceProjection.cs  # Project points to SubD surface
│       └── CurveEvaluator.cs     # Evaluate parametric curves on surface
│
└── AnalysisEngine/               # Existing Python + C++ code
    ├── server.py                 # HTTP server wrapper
    ├── app/
    │   ├── analysis/
    │   └── ...
    └── cpp_core/
        └── ...
```

---

## Key Implementation Details

### Constrained Dragging

The critical piece is projecting mouse movement onto the Form surface:

```csharp
public class SurfaceProjection
{
    /// <summary>
    /// Project a screen point onto the Form SubD surface.
    /// Returns parametric coordinates (face_id, u, v).
    /// </summary>
    public static bool ProjectToSurface(
        RhinoViewport viewport,
        Point2d screenPoint,
        SubD formSubD,
        out int faceId,
        out double u,
        out double v)
    {
        // Get world ray from screen point
        Line worldRay;
        viewport.GetFrustumLine(screenPoint.X, screenPoint.Y, out worldRay);

        // Find closest point on SubD to ray
        Point3d closestPoint;
        ComponentIndex ci;
        double s, t;

        // SubD.ClosestPoint returns parametric coordinates
        if (formSubD.ClosestPoint(
                worldRay.From,
                worldRay.Direction,
                out closestPoint,
                out ci,
                out s, out t))
        {
            // ci.Index gives us the face index
            // s, t are the parametric coordinates on that face
            faceId = ci.Index;
            u = s;
            v = t;
            return true;
        }

        faceId = -1;
        u = v = 0;
        return false;
    }
}
```

### Boundary Curve Evaluation

Evaluating a parametric boundary on the exact surface:

```csharp
public class CurveEvaluator
{
    /// <summary>
    /// Evaluate a parametric boundary curve on the Form surface.
    /// Returns a Rhino NurbsCurve for display.
    /// </summary>
    public static NurbsCurve EvaluateOnSurface(
        SubD formSubD,
        ParametricBoundary boundary,
        int sampleCount = 50)
    {
        var points = new List<Point3d>();

        for (int i = 0; i < sampleCount; i++)
        {
            double t = (double)i / (sampleCount - 1);

            // Interpolate along parametric boundary
            var param = boundary.EvaluateAt(t);

            // Get face and evaluate limit surface
            var face = formSubD.Faces[param.FaceId];
            var point = face.LimitSurfacePointAt(param.U, param.V);

            points.Add(point);
        }

        // Create interpolated curve through points
        return NurbsCurve.Create(
            periodic: boundary.IsClosed,
            degree: 3,
            points: points);
    }
}
```

---

## Next Steps

1. **Set up RhinoCommon project** - Create Visual Studio solution with Rhino 8 SDK
2. **Implement basic commands** - SubDAnalyze, SubDEdit
3. **Build communication layer** - HTTP client to existing Python engine
4. **Implement edit mode** - Mouse callbacks with surface constraint
5. **Add display conduit** - Real-time visualization overlay
6. **Test with existing analysis** - Connect to DifferentialLens
