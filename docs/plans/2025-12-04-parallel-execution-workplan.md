# Parallel Execution Workplan

**Date**: 2025-12-04
**Purpose**: Enable 2-6 agents to work in parallel per phase with clear objectives and testing gates.

---

## Agent Command Files

Each agent has a dedicated command file in `.claude/commands/phase-X/`. This keeps agent prompts isolated and prevents context bloat.

| Phase | Launch File | Agents |
|-------|-------------|--------|
| Phase 0 | `.claude/commands/phase-0/launch.md` | 2 agents (0A, 0B) |
| Phase 1 | `.claude/commands/phase-1/launch.md` | 4 agents (1A, 1B, 1C, 1D) |
| Phase 2 | `.claude/commands/phase-2/launch.md` | 3 agents (2A, 2B, 2C) |
| Phase 3 | `.claude/commands/phase-3/launch.md` | 4 agents (3A, 3B, 3C, 3D) |

**To launch a phase**: Read the launch file and follow its instructions.

---

## Execution Model

```
Phase Start
    ↓
Launch Parallel Agents (2-6 per phase)
    ↓
Agents work independently on non-overlapping files
    ↓
Consolidation (merge all changes)
    ↓
Integration Tests (must pass to proceed)
    ↓
Next Phase
```

**Key Principle**: Agents work on SEPARATE files to avoid merge conflicts.

---

## Phase 0: Prerequisites & Setup

**Duration**: 1 day
**Agents**: 2 parallel

### Agent 0A: C++ Build System Setup

**Objective**: Configure CMake to build shared library with C bindings

**Files to create/modify**:
- `cpp_core/CMakeLists.txt` (modify)
- `cpp_core/c_bindings/CMakeLists.txt` (new)

**Tasks**:
1. Add shared library target `latent_core` alongside static library
2. Configure export macros for Windows/macOS/Linux
3. Add c_bindings subdirectory to build
4. Set up installation rules for .dll/.dylib

**Success Criteria**:
- `cmake .. && make` produces both `libcpp_core.a` and `liblatent_core.dylib`
- Library exports are properly defined

---

### Agent 0B: Project Structure Setup

**Objective**: Create directory structure for new components

**Files to create**:
- `cpp_core/c_bindings/` directory
- `cpp_core/c_bindings/exports.h` (export macro definitions)
- `rhino_plugin/` directory structure
- `rhino_plugin/LatentPlugin.csproj` (template)
- `analysis_service/` directory
- `analysis_service/__init__.py`
- `analysis_service/requirements.txt`

**Tasks**:
1. Create all new directories
2. Create placeholder files with proper headers
3. Set up .csproj with RhinoCommon references
4. Set up Python package structure

**Success Criteria**:
- All directories exist
- Placeholder files compile/import without errors

---

### Phase 0 Tests

```bash
# Test 0.1: CMake configuration succeeds
cd cpp_core/build && cmake ..

# Test 0.2: Build produces shared library
make && ls -la liblatent_core.*

# Test 0.3: Directory structure exists
test -d rhino_plugin && test -d analysis_service && test -d cpp_core/c_bindings

# Test 0.4: Python package imports
python3 -c "import analysis_service"
```

---

## Phase 1: C++ Core Extensions

**Duration**: 3-4 days
**Agents**: 4 parallel

### Agent 1A: Inverse Surface Evaluation

**Objective**: Implement 3D point → (face_id, u, v) projection

**Files to create/modify**:
- `cpp_core/geometry/subd_evaluator.h` (add method declarations)
- `cpp_core/geometry/subd_evaluator.cpp` (add implementations)
- `cpp_core/tests/test_inverse_eval.cpp` (new)

**Tasks**:
1. Add `project_point_onto_surface()` method declaration
2. Implement Newton-Raphson iteration using existing derivatives
3. Handle multiple faces (find minimum distance)
4. Add tolerance parameter
5. Write unit tests

**Algorithm**:
```cpp
bool project_point_onto_surface(const Point3D& point, int& face_id, float& u, float& v) {
    float min_dist = FLT_MAX;
    for (int f = 0; f < get_control_face_count(); f++) {
        // Newton-Raphson: minimize ||evaluate_limit(f, u, v) - point||²
        // Use evaluate_limit_with_derivatives() for Jacobian
        // Update u, v iteratively
    }
    return min_dist < tolerance;
}
```

**Success Criteria**:
- Unit tests pass for known points on surface
- Projection accuracy < 1e-6 for exact surface points
- Handles off-surface points gracefully

**Skills Required**: `superpowers:test-driven-development`

---

### Agent 1B: Surface Curve Implementation

**Objective**: Implement parametric curves on SubD limit surface

**Files to create**:
- `cpp_core/geometry/surface_curve.h` (new)
- `cpp_core/geometry/surface_curve.cpp` (new)
- `cpp_core/tests/test_surface_curve.cpp` (new)

**Tasks**:
1. Define `ParametricPoint` struct (face_id, u, v)
2. Define `SurfaceCurve` class with control points
3. Implement Bezier evaluation in parameter space
4. Implement B-spline evaluation
5. Implement curve sampling for display
6. Write unit tests

**Data Structures**:
```cpp
struct ParametricPoint {
    int face_id;
    float u, v;
};

enum class CurveType { BEZIER, BSPLINE, LINEAR };

class SurfaceCurve {
    std::vector<ParametricPoint> control_points;
    CurveType type;
    int degree;

    Point3D evaluate(float t, const SubDEvaluator& eval) const;
    std::vector<Point3D> sample(int num_points, const SubDEvaluator& eval) const;
};
```

**Success Criteria**:
- Bezier curves interpolate endpoints
- B-spline curves approximate control polygon
- Sampling produces smooth 3D curves on surface

**Skills Required**: `superpowers:test-driven-development`

---

### Agent 1C: C Bindings - Core Functions

**Objective**: Create C-compatible wrapper for core evaluation functions

**Files to create**:
- `cpp_core/c_bindings/rhino_wrapper.h` (new)
- `cpp_core/c_bindings/rhino_wrapper.cpp` (new - evaluator functions only)

**Tasks**:
1. Define export macros (LATENT_API)
2. Implement handle-based lifecycle (create/destroy)
3. Wrap `initialize()` with flat arrays
4. Wrap `evaluate_limit_point()`
5. Wrap `evaluate_limit()` (point + normal)
6. Wrap `project_point_onto_surface()` (depends on Agent 1A)

**Interface**:
```cpp
extern "C" {
    LATENT_API SubDEvaluatorHandle latent_evaluator_create();
    LATENT_API void latent_evaluator_destroy(SubDEvaluatorHandle h);
    LATENT_API bool latent_evaluator_initialize(SubDEvaluatorHandle h,
        const float* vertices, int vertex_count,
        const int* faces, const int* face_sizes, int face_count,
        const int* creases, const float* crease_sharpness, int crease_count);
    LATENT_API bool latent_evaluate_point(SubDEvaluatorHandle h,
        int face_id, float u, float v, float* x, float* y, float* z);
    LATENT_API bool latent_evaluate_normal(SubDEvaluatorHandle h,
        int face_id, float u, float v, float* nx, float* ny, float* nz);
    LATENT_API bool latent_project_point(SubDEvaluatorHandle h,
        float px, float py, float pz, int* face_id, float* u, float* v);
}
```

**Success Criteria**:
- Functions callable from C
- Memory safety (no leaks in create/destroy cycle)
- Results match C++ API exactly

**Skills Required**: `superpowers:test-driven-development`

---

### Agent 1D: C Bindings - Curve & Analysis Functions

**Objective**: Create C-compatible wrapper for curves and curvature

**Files to create**:
- `cpp_core/c_bindings/rhino_wrapper_curves.cpp` (new)
- `cpp_core/c_bindings/rhino_wrapper_analysis.cpp` (new)
- `cpp_core/tests/test_c_bindings.cpp` (new)

**Tasks**:
1. Wrap SurfaceCurve class (depends on Agent 1B)
2. Wrap curvature computation
3. Create comprehensive C binding tests
4. Document all functions

**Interface**:
```cpp
extern "C" {
    // Curves
    LATENT_API SurfaceCurveHandle latent_curve_create(
        const int* face_ids, const float* us, const float* vs, int point_count,
        int curve_type, int degree);
    LATENT_API void latent_curve_destroy(SurfaceCurveHandle h);
    LATENT_API bool latent_curve_evaluate(SurfaceCurveHandle h, SubDEvaluatorHandle eval,
        float t, float* x, float* y, float* z);
    LATENT_API bool latent_curve_sample(SurfaceCurveHandle h, SubDEvaluatorHandle eval,
        int num_samples, float* out_points);

    // Curvature
    LATENT_API bool latent_compute_curvature(SubDEvaluatorHandle h,
        int face_id, float u, float v,
        float* k1, float* k2, float* H, float* K);
}
```

**Success Criteria**:
- All functions callable from C
- Test verifies round-trip accuracy
- Memory safety verified

**Skills Required**: `superpowers:test-driven-development`

---

### Phase 1 Consolidation & Tests

**After all agents complete**:

```bash
# Build everything
cd cpp_core/build && cmake .. && make -j4

# Run unit tests
ctest --output-on-failure

# Integration test: C bindings work end-to-end
./test_c_bindings

# Verify shared library exports
nm -gU liblatent_core.dylib | grep latent_
```

**Integration Test Script** (`cpp_core/tests/integration_phase1.cpp`):
```cpp
// Test full workflow: create evaluator → initialize → project → curve
int main() {
    auto eval = latent_evaluator_create();
    // ... initialize with test cube ...

    // Test inverse evaluation
    int face; float u, v;
    latent_project_point(eval, 0.5, 0.5, 0.5, &face, &u, &v);
    assert(face >= 0);

    // Test curve
    int faces[] = {0, 0};
    float us[] = {0.0, 1.0};
    float vs[] = {0.5, 0.5};
    auto curve = latent_curve_create(faces, us, vs, 2, 0/*BEZIER*/, 1);

    float points[30]; // 10 points × 3 coords
    latent_curve_sample(curve, eval, 10, points);

    latent_curve_destroy(curve);
    latent_evaluator_destroy(eval);
    return 0;
}
```

---

## Phase 2: Python Analysis Service

**Duration**: 2-3 days
**Agents**: 3 parallel

### Agent 2A: JSON-RPC Protocol & Server

**Objective**: Create JSON-RPC server infrastructure

**Files to create**:
- `analysis_service/protocol.py` (new)
- `analysis_service/server.py` (new)
- `analysis_service/exceptions.py` (new)
- `tests/test_analysis_protocol.py` (new)

**Tasks**:
1. Define request/response schemas
2. Implement JSON-RPC 2.0 server (using zmq or http)
3. Add request validation
4. Add error handling
5. Write protocol tests

**Protocol Schema**:
```python
REQUEST_SCHEMA = {
    "jsonrpc": "2.0",
    "method": str,  # "initialize", "analyze", "get_boundaries"
    "params": {
        "cage": {"vertices": [...], "faces": [...], "creases": [...]},
        "lens": str,
        "params": dict,
        "pinned_regions": list
    },
    "id": str
}

RESPONSE_SCHEMA = {
    "jsonrpc": "2.0",
    "result": {
        "regions": [...],
        "vertices": [...],
        "edges": [...]
    },
    "id": str
}
```

**Success Criteria**:
- Server starts and accepts connections
- Invalid requests return proper JSON-RPC errors
- Valid requests route to handlers

**Skills Required**: `superpowers:test-driven-development`

---

### Agent 2B: Boundary Curve Extraction - Differential Lens

**Objective**: Extract boundary curves from curvature analysis

**Files to modify**:
- `app/analysis/differential_lens.py` (modify)
- `app/analysis/boundary_extraction.py` (new)
- `tests/test_boundary_extraction.py` (new)

**Tasks**:
1. Implement marching squares for curvature contours
2. Extract ridge lines (|κ₁| local maxima)
3. Extract valley lines (|κ₁| local minima)
4. Convert to parametric curves (face_id, u, v)
5. Connect curve segments into continuous boundaries
6. Write tests

**Algorithm**:
```python
def extract_curvature_contour(evaluator, threshold, face_id):
    """Extract contour where H(u,v) = threshold using marching squares."""
    grid = sample_curvature_grid(evaluator, face_id, resolution=10)
    segments = marching_squares(grid, threshold)
    return convert_to_parametric(segments, face_id)

def extract_ridges(evaluator, percentile=90):
    """Extract ridge lines where |κ₁| is in top percentile."""
    # Sample curvature across all faces
    # Find local maxima of |κ₁|
    # Trace ridge paths
    pass
```

**Success Criteria**:
- Contours form closed loops on each face
- Ridge/valley lines connect across face boundaries
- Curves are smooth and properly ordered

**Skills Required**: `superpowers:test-driven-development`

---

### Agent 2C: Boundary Curve Extraction - Spectral Lens

**Objective**: Extract nodal lines from eigenfunction analysis

**Files to modify**:
- `app/analysis/spectral_lens.py` (modify)
- `app/analysis/spectral_decomposition.py` (modify)
- `tests/test_nodal_extraction.py` (new)

**Tasks**:
1. Implement zero-crossing detection on tessellation
2. Interpolate exact crossing positions
3. Connect crossings into continuous curves
4. Convert to parametric space (face_id, u, v)
5. Handle multiple connected components
6. Write tests

**Algorithm**:
```python
def extract_nodal_lines(eigenfunction, tessellation):
    """Extract curves where eigenfunction = 0."""
    crossings = []
    for triangle in tessellation.triangles:
        # Find edges where eigenfunction changes sign
        for edge in triangle.edges:
            v0_val = eigenfunction[edge.v0]
            v1_val = eigenfunction[edge.v1]
            if v0_val * v1_val < 0:
                # Linear interpolation of zero crossing
                t = abs(v0_val) / (abs(v0_val) + abs(v1_val))
                crossing_point = lerp(edge.v0_pos, edge.v1_pos, t)
                crossings.append(crossing_point)

    # Connect crossings into continuous curves
    return connect_crossings(crossings)
```

**Success Criteria**:
- Nodal lines form closed curves (or terminate at boundary)
- Zero-crossings accurately interpolated
- Multiple nodal components handled

**Skills Required**: `superpowers:test-driven-development`

---

### Phase 2 Consolidation & Tests

**Integration Test** (`tests/integration_phase2.py`):
```python
import subprocess
import json
import time

def test_analysis_service():
    # Start server
    server = subprocess.Popen(["python", "-m", "analysis_service"])
    time.sleep(2)

    try:
        # Test differential lens
        request = {
            "jsonrpc": "2.0",
            "method": "analyze",
            "params": {
                "cage": TEST_CUBE_CAGE,
                "lens": "differential",
                "params": {"curvature_tolerance": 0.3}
            },
            "id": "1"
        }
        response = send_request(request)
        assert "result" in response
        assert "regions" in response["result"]
        assert len(response["result"]["regions"]) > 0

        # Verify boundary curves present
        region = response["result"]["regions"][0]
        assert "boundary_curves" in region
        assert len(region["boundary_curves"]) > 0

        # Test spectral lens
        request["params"]["lens"] = "spectral"
        response = send_request(request)
        assert "result" in response

    finally:
        server.terminate()

if __name__ == "__main__":
    test_analysis_service()
```

---

## Phase 3: Rhino Plugin Foundation

**Duration**: 4-5 days
**Agents**: 4 parallel

### Agent 3A: P/Invoke Bindings

**Objective**: Create C# managed wrappers for C bindings

**Files to create**:
- `rhino_plugin/Interop/NativeCore.cs` (new)
- `rhino_plugin/Interop/SubDEvaluator.cs` (new)
- `rhino_plugin/Interop/SurfaceCurve.cs` (new)
- `rhino_plugin/Tests/InteropTests.cs` (new)

**Tasks**:
1. Define P/Invoke signatures matching C API
2. Create managed wrapper classes with IDisposable
3. Marshal arrays correctly
4. Handle errors from native code
5. Write unit tests

**Code**:
```csharp
public static class NativeCore
{
    private const string DllName = "latent_core";

    [DllImport(DllName, CallingConvention = CallingConvention.Cdecl)]
    public static extern IntPtr latent_evaluator_create();

    [DllImport(DllName, CallingConvention = CallingConvention.Cdecl)]
    public static extern void latent_evaluator_destroy(IntPtr handle);

    [DllImport(DllName, CallingConvention = CallingConvention.Cdecl)]
    public static extern bool latent_evaluator_initialize(
        IntPtr handle,
        [MarshalAs(UnmanagedType.LPArray)] float[] vertices, int vertexCount,
        [MarshalAs(UnmanagedType.LPArray)] int[] faces,
        [MarshalAs(UnmanagedType.LPArray)] int[] faceSizes, int faceCount,
        [MarshalAs(UnmanagedType.LPArray)] int[] creases,
        [MarshalAs(UnmanagedType.LPArray)] float[] creaseSharpness, int creaseCount);

    // ... etc
}

public class SubDEvaluator : IDisposable
{
    private IntPtr _handle;
    private bool _disposed;

    public SubDEvaluator()
    {
        _handle = NativeCore.latent_evaluator_create();
    }

    public void Initialize(Rhino.Geometry.SubD subd)
    {
        var (vertices, faces, faceSizes, creases, sharpness) = ExtractCage(subd);
        if (!NativeCore.latent_evaluator_initialize(_handle, ...))
            throw new InvalidOperationException("Failed to initialize evaluator");
    }

    public Point3d EvaluatePoint(int faceId, double u, double v)
    {
        if (!NativeCore.latent_evaluate_point(_handle, faceId, (float)u, (float)v,
            out float x, out float y, out float z))
            throw new InvalidOperationException("Evaluation failed");
        return new Point3d(x, y, z);
    }

    public void Dispose()
    {
        if (!_disposed)
        {
            NativeCore.latent_evaluator_destroy(_handle);
            _disposed = true;
        }
    }
}
```

**Success Criteria**:
- P/Invoke calls succeed without crashes
- Managed wrapper lifecycle correct
- Results match Python API

**Skills Required**: None specific

---

### Agent 3B: Analysis Service Client

**Objective**: Create C# client for Python analysis service

**Files to create**:
- `rhino_plugin/Analysis/LensClient.cs` (new)
- `rhino_plugin/Analysis/AnalysisResult.cs` (new)
- `rhino_plugin/Analysis/Protocol.cs` (new)
- `rhino_plugin/Tests/LensClientTests.cs` (new)

**Tasks**:
1. Implement JSON-RPC client (HTTP or ZMQ)
2. Define C# data classes matching protocol
3. Implement async analysis methods
4. Handle connection errors gracefully
5. Write tests with mock server

**Code**:
```csharp
public class LensClient : IDisposable
{
    private readonly HttpClient _httpClient;
    private Process _pythonProcess;

    public async Task StartServiceAsync()
    {
        _pythonProcess = Process.Start(new ProcessStartInfo
        {
            FileName = "python",
            Arguments = "-m analysis_service",
            UseShellExecute = false,
            RedirectStandardOutput = true
        });
        await WaitForServiceReady();
    }

    public async Task<AnalysisResult> AnalyzeAsync(
        string lensType,
        SubD subd,
        Dictionary<string, object> parameters)
    {
        var request = new JsonRpcRequest
        {
            Method = "analyze",
            Params = new {
                cage = ExtractCage(subd),
                lens = lensType,
                @params = parameters
            }
        };

        var response = await _httpClient.PostAsJsonAsync(
            "http://localhost:5555/", request);
        var result = await response.Content.ReadFromJsonAsync<JsonRpcResponse>();

        return ParseAnalysisResult(result);
    }
}

public class AnalysisResult
{
    public List<Region> Regions { get; set; }
    public List<Vertex> Vertices { get; set; }
    public List<Edge> Edges { get; set; }
}
```

**Success Criteria**:
- Client connects to running service
- Analysis results deserialize correctly
- Errors propagate as exceptions

**Skills Required**: None specific

---

### Agent 3C: Plugin Entry Point & Commands

**Objective**: Create Rhino plugin infrastructure

**Files to create**:
- `rhino_plugin/LatentPlugin.cs` (new)
- `rhino_plugin/Commands/LatentAnalyzeCommand.cs` (new)
- `rhino_plugin/Commands/LatentSelectRegionCommand.cs` (new)

**Tasks**:
1. Implement RhinoPlugin class
2. Create main analysis command
3. Create region selection command
4. Register commands with Rhino
5. Handle plugin lifecycle

**Code**:
```csharp
public class LatentPlugin : Rhino.PlugIns.PlugIn
{
    public static LatentPlugin Instance { get; private set; }

    public LatentPlugin()
    {
        Instance = this;
    }

    protected override LoadReturnCode OnLoad(ref string errorMessage)
    {
        // Initialize services
        RegionManager = new RegionManager();
        LensClient = new LensClient();

        return LoadReturnCode.Success;
    }

    public RegionManager RegionManager { get; private set; }
    public LensClient LensClient { get; private set; }
}

[CommandStyle(Style.ScriptRunner)]
public class LatentAnalyzeCommand : Command
{
    public override string EnglishName => "LatentAnalyze";

    protected override Result RunCommand(RhinoDoc doc, RunMode mode)
    {
        // Get SubD selection
        var go = new GetObject();
        go.SetCommandPrompt("Select SubD to analyze");
        go.GeometryFilter = ObjectType.SubD;
        if (go.Get() != GetResult.Object)
            return Result.Cancel;

        var subd = go.Object(0).SubD();

        // Run analysis
        var result = await LatentPlugin.Instance.LensClient.AnalyzeAsync(
            "differential", subd, new Dictionary<string, object>());

        // Update region manager
        LatentPlugin.Instance.RegionManager.UpdateFromAnalysis(result);

        doc.Views.Redraw();
        return Result.Success;
    }
}
```

**Success Criteria**:
- Plugin loads in Rhino without errors
- Commands appear in command list
- Basic analyze command executes

**Skills Required**: None specific

---

### Agent 3D: Data Model & State Management

**Objective**: Create region/vertex/edge data model and state management

**Files to create**:
- `rhino_plugin/Geometry/Vertex.cs` (new)
- `rhino_plugin/Geometry/Edge.cs` (new)
- `rhino_plugin/Geometry/Region.cs` (new)
- `rhino_plugin/Geometry/RegionManager.cs` (new)
- `rhino_plugin/Geometry/UndoStack.cs` (new)
- `rhino_plugin/Tests/RegionManagerTests.cs` (new)

**Tasks**:
1. Implement Vertex class with state tracking
2. Implement Edge class with curve representation
3. Implement Region class with boundary edges
4. Implement RegionManager with collections
5. Implement undo/redo system
6. Write comprehensive tests

**Code**:
```csharp
public class Vertex
{
    public string Id { get; }
    public ParametricPoint Position { get; set; }
    public ParametricPoint? ImplicitPosition { get; }
    public VertexOrigin CreatedBy { get; }
    public bool IsPinned { get; set; }
    public bool IsExplicit => Position != ImplicitPosition;

    public bool CanRevert => ImplicitPosition.HasValue && !IsPinned;
}

public class Edge
{
    public string Id { get; }
    public List<Vertex> Vertices { get; }
    public CurveType Type { get; set; }
    public int Degree { get; set; }
    public CurveDefinition? ImplicitDefinition { get; }
    public bool IsPinned { get; set; }

    public List<Point3d> Sample(SubDEvaluator evaluator, int numPoints);
}

public class Region
{
    public string Id { get; }
    public List<Edge> BoundaryEdges { get; }
    public string UnityPrinciple { get; }
    public double ResonanceScore { get; }
    public bool IsPinned { get; set; }

    public Point3d Centroid { get; }
    public BoundingBox BoundingBox { get; }
}

public class RegionManager
{
    public ObservableCollection<Region> Regions { get; }
    public ObservableCollection<Vertex> Vertices { get; }
    public ObservableCollection<Edge> Edges { get; }

    private readonly UndoStack _undoStack;

    public void MoveVertex(Vertex vertex, ParametricPoint newPosition);
    public void MoveEdge(Edge edge, Vector3d displacement);
    public void Pin(IGeometryElement element);
    public void Unpin(IGeometryElement element);
    public void RevertVertex(Vertex vertex);
    public void RevertEdgeCurveType(Edge edge);
    public void RevertEdgeFully(Edge edge);
    public void RevertRegion(Region region);

    public void Undo();
    public void Redo();
}
```

**Success Criteria**:
- All state transitions work correctly
- Undo/redo reverses operations
- Revert hierarchy enforced

**Skills Required**: `superpowers:test-driven-development`

---

### Phase 3 Consolidation & Tests

**Integration Test**:
```csharp
[TestFixture]
public class Phase3IntegrationTests
{
    [Test]
    public void FullWorkflow_SubDToRegions()
    {
        // Create test SubD
        var subd = CreateTestCube();

        // Initialize evaluator
        using var evaluator = new SubDEvaluator();
        evaluator.Initialize(subd);

        // Verify forward evaluation
        var point = evaluator.EvaluatePoint(0, 0.5, 0.5);
        Assert.That(point.IsValid);

        // Verify inverse evaluation
        var (faceId, u, v) = evaluator.ProjectPoint(point);
        Assert.That(faceId, Is.EqualTo(0));
        Assert.That(u, Is.EqualTo(0.5).Within(0.001));

        // Start analysis service
        using var client = new LensClient();
        await client.StartServiceAsync();

        // Run analysis
        var result = await client.AnalyzeAsync("differential", subd, new());
        Assert.That(result.Regions.Count, Is.GreaterThan(0));

        // Update region manager
        var manager = new RegionManager();
        manager.UpdateFromAnalysis(result);
        Assert.That(manager.Regions.Count, Is.EqualTo(result.Regions.Count));
    }
}
```

---

## Phase 4: Display & Visualization

**Duration**: 3-4 days
**Agents**: 3 parallel

### Agent 4A: Region Display Conduit

**Objective**: Implement DisplayConduit for region visualization

**Files to create**:
- `rhino_plugin/Display/RegionConduit.cs` (new)
- `rhino_plugin/Display/VisualizationSettings.cs` (new)

**Tasks**:
1. Extend DisplayConduit
2. Implement CalculateBoundingBox
3. Implement PostDrawObjects for curves
4. Implement DrawForeground for fills
5. Handle selection highlighting

**Code**: See implementation plan document

**Success Criteria**:
- Curves render on SubD surface
- Selection highlighting works
- Fill transparency displays correctly

---

### Agent 4B: Curve Sampling & Rendering

**Objective**: Implement efficient curve sampling for display

**Files to create**:
- `rhino_plugin/Display/CurveSampler.cs` (new)
- `rhino_plugin/Display/CurveCache.cs` (new)

**Tasks**:
1. Sample parametric curves to polylines
2. Cache sampled curves for performance
3. Invalidate cache on changes
4. Adaptive sampling based on curvature

**Success Criteria**:
- Curves appear smooth at all zoom levels
- Cache improves redraw performance
- Memory usage bounded

---

### Agent 4C: Centroid & Region Fill

**Objective**: Implement region centroid markers and fills

**Files to create**:
- `rhino_plugin/Display/RegionFill.cs` (new)
- `rhino_plugin/Display/CentroidMarker.cs` (new)

**Tasks**:
1. Compute region centroid on surface
2. Create hatch patterns for region fills
3. Implement transparent fill rendering
4. Create dot markers for centroids

**Success Criteria**:
- Centroids appear at region centers
- Fills render with correct transparency
- Performance acceptable with many regions

---

### Phase 4 Tests

```csharp
[Test]
public void RegionConduit_DrawsCurvesCorrectly()
{
    // Setup
    var conduit = new RegionConduit(regionManager, settings);
    conduit.Enabled = true;

    // Add test region
    regionManager.AddRegion(testRegion);

    // Verify conduit is drawing
    // (Visual verification in Rhino viewport)

    // Verify bounding box includes region
    var bbox = conduit.GetBoundingBox();
    Assert.That(bbox.Contains(testRegion.BoundingBox));
}
```

---

## Phase 5: Interaction & Selection

**Duration**: 3-4 days
**Agents**: 3 parallel

### Agent 5A: Surface-Constrained GetPoint

**Objective**: Implement custom GetPoint for surface-constrained picking

**Files to create**:
- `rhino_plugin/Interaction/SurfaceConstrainedGetPoint.cs` (new)
- `rhino_plugin/Interaction/ParametricPoint.cs` (new)

**Tasks**:
1. Extend GetPoint class
2. Constrain to SubD surface
3. Track parametric coordinates
4. Provide visual feedback
5. Handle edge cases

---

### Agent 5B: Vertex & Edge Drag Handlers

**Objective**: Implement drag operations for vertices and edges

**Files to create**:
- `rhino_plugin/Interaction/VertexDragHandler.cs` (new)
- `rhino_plugin/Interaction/EdgeDragHandler.cs` (new)
- `rhino_plugin/Interaction/DragPreview.cs` (new)

**Tasks**:
1. Implement vertex dragging with preview
2. Implement edge dragging (all vertices move)
3. Project movements to surface
4. Integrate with undo system

---

### Agent 5C: Region & Element Picking

**Objective**: Implement picking for regions, edges, and vertices

**Files to create**:
- `rhino_plugin/Interaction/RegionPicker.cs` (new)
- `rhino_plugin/Interaction/ElementPicker.cs` (new)
- `rhino_plugin/Interaction/PickResult.cs` (new)

**Tasks**:
1. Implement region picking (point-in-region test)
2. Implement edge picking (proximity test)
3. Implement vertex picking (proximity test)
4. Handle mode-based picking

---

### Phase 5 Tests

```csharp
[Test]
public void VertexDrag_UpdatesPositionOnSurface()
{
    var vertex = manager.Vertices[0];
    var originalPos = vertex.Position;

    // Simulate drag
    var newPos3d = originalPos.ToPoint3d() + new Vector3d(0.1, 0, 0);
    var handler = new VertexDragHandler(manager, evaluator);
    handler.ApplyDrag(vertex, newPos3d);

    // Verify position updated
    Assert.That(vertex.Position, Is.Not.EqualTo(originalPos));

    // Verify still on surface
    var surfacePoint = evaluator.EvaluatePoint(
        vertex.Position.FaceId,
        vertex.Position.U,
        vertex.Position.V);
    Assert.That(surfacePoint.DistanceTo(vertex.ToPoint3d()), Is.LessThan(0.001));

    // Verify explicit flag set
    Assert.That(vertex.IsExplicit, Is.True);
}
```

---

## Phase 6: UI Panels

**Duration**: 3-4 days
**Agents**: 3 parallel

### Agent 6A: Geometry List Panel

**Objective**: Implement Eto.Forms panel for geometry list

**Files to create**:
- `rhino_plugin/UI/GeometryListPanel.cs` (new)
- `rhino_plugin/UI/GeometryListItem.cs` (new)

**Tasks**:
1. Create panel with mode selector (Vertex/Edge/Region)
2. Implement grid view with columns
3. Add pin/unpin buttons
4. Add revert buttons with validation
5. Handle selection synchronization

---

### Agent 6B: Lens Control Panel

**Objective**: Implement lens selection and parameter UI

**Files to create**:
- `rhino_plugin/UI/LensPanel.cs` (new)
- `rhino_plugin/UI/ParameterControl.cs` (new)

**Tasks**:
1. Create lens selector dropdown
2. Generate parameter controls dynamically
3. Implement analyze button
4. Show progress during analysis
5. Handle errors gracefully

---

### Agent 6C: Visualization Settings Panel

**Objective**: Implement visualization settings UI

**Files to create**:
- `rhino_plugin/UI/VisualizationPanel.cs` (new)
- `rhino_plugin/UI/ColorPicker.cs` (new)

**Tasks**:
1. Create checkboxes for fill/centroid display
2. Add color pickers for states
3. Persist settings
4. Update conduit on changes

---

### Phase 6 Tests

```csharp
[Test]
public void GeometryListPanel_ShowsCorrectItems()
{
    var panel = new GeometryListPanel(manager);

    // Add test data
    manager.AddRegion(testRegion);

    // Verify panel shows region
    Assert.That(panel.Items.Count, Is.EqualTo(1));

    // Switch to edge mode
    panel.CurrentMode = EditMode.Edge;

    // Verify shows edges
    Assert.That(panel.Items.Count, Is.EqualTo(testRegion.BoundaryEdges.Count));
}
```

---

## Phase 7: Final Integration

**Duration**: 2-3 days
**Agents**: 2 parallel

### Agent 7A: End-to-End Workflow Testing

**Objective**: Comprehensive integration testing

**Files to create**:
- `rhino_plugin/Tests/IntegrationTests.cs` (new)
- `rhino_plugin/Tests/TestHelpers.cs` (new)

**Tasks**:
1. Test full workflow: load → analyze → edit → revert
2. Test all lens types
3. Test undo/redo chains
4. Test edge cases and error handling
5. Performance profiling

---

### Agent 7B: Documentation & Cleanup

**Objective**: Final documentation and code cleanup

**Files to create/modify**:
- `rhino_plugin/README.md` (new)
- `docs/RHINO_PLUGIN_USER_GUIDE.md` (new)
- Various code cleanup

**Tasks**:
1. Write user documentation
2. Add XML documentation to public APIs
3. Remove dead code
4. Final code review
5. Update PROJECT_STATUS.md

---

## Launch Commands

Each phase has a single command that launches all agents for that phase.

---

## Phase Launch Command Template

The following sections contain the actual prompts to launch each phase.
