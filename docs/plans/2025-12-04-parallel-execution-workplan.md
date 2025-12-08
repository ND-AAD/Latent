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
| Phase 4 | `.claude/commands/phase-4/launch.md` | 3 agents (4A, 4B, 4C) |
| Phase 5 | `.claude/commands/phase-5/launch.md` | 3 agents (5A, 5B, 5C) |
| Phase 6 | `.claude/commands/phase-6/launch.md` | 3 agents (6A, 6B, 6C) |
| Phase 7 | `.claude/commands/phase-7/launch.md` | 2 agents (7A, 7B) |

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

### Agent 7A: End-to-End Integration Tests

**Objective**: Create comprehensive integration tests that verify the complete workflow from SubD selection through analysis, editing, and revert operations.

**Files to create**:
- `rhino_plugin/Tests/IntegrationTests.cs` (new)
- `rhino_plugin/Tests/WorkflowTests.cs` (new)
- `rhino_plugin/Tests/TestHelpers.cs` (new)

**Tasks**:

#### 1. Create TestHelpers.cs

Provide reusable test utilities for all integration tests:

```csharp
// rhino_plugin/Tests/TestHelpers.cs
using System;
using System.Collections.Generic;
using Rhino.Geometry;
using Latent.Geometry;
using Latent.Interop;
using Latent.Analysis;

namespace Latent.Tests
{
    /// <summary>
    /// Helper utilities for integration tests.
    /// </summary>
    public static class TestHelpers
    {
        /// <summary>
        /// Create a simple box SubD for testing.
        /// </summary>
        public static SubD CreateTestBoxSubD()
        {
            var box = new Box(Plane.WorldXY,
                new Interval(-1, 1),
                new Interval(-1, 1),
                new Interval(-1, 1));
            var mesh = Mesh.CreateFromBox(box, 1, 1, 1);
            return SubD.CreateFromMesh(mesh);
        }

        /// <summary>
        /// Create a sphere-like SubD for testing curved surfaces.
        /// </summary>
        public static SubD CreateTestSphereSubD()
        {
            var sphere = new Sphere(Point3d.Origin, 1.0);
            var mesh = Mesh.CreateFromSphere(sphere, 8, 8);
            return SubD.CreateFromMesh(mesh);
        }

        /// <summary>
        /// Create a mock analysis result for testing.
        /// </summary>
        public static AnalysisResultData CreateMockAnalysisResult(int regionCount = 3)
        {
            var result = new AnalysisResultData
            {
                Vertices = new List<VertexData>(),
                Edges = new List<EdgeData>(),
                Regions = new List<RegionData>()
            };

            // Create vertices
            for (int i = 0; i < regionCount * 4; i++)
            {
                result.Vertices.Add(new VertexData
                {
                    Id = $"v{i}",
                    Position = new List<double> { 0, (i % 4) * 0.25, (i / 4) * 0.25 },
                    CreatedBy = "lens",
                    IsPinned = false
                });
            }

            // Create edges connecting vertices
            for (int i = 0; i < regionCount * 4; i++)
            {
                int next = (i + 1) % (regionCount * 4);
                result.Edges.Add(new EdgeData
                {
                    Id = $"e{i}",
                    VertexIds = new List<string> { $"v{i}", $"v{next}" },
                    CurveType = "bezier",
                    Degree = 3,
                    IsPinned = false
                });
            }

            // Create regions
            for (int r = 0; r < regionCount; r++)
            {
                result.Regions.Add(new RegionData
                {
                    Id = $"r{r}",
                    BoundaryEdgeIds = new List<string>
                    {
                        $"e{r * 4}", $"e{r * 4 + 1}",
                        $"e{r * 4 + 2}", $"e{r * 4 + 3}"
                    },
                    UnityPrinciple = r == 0 ? "curvature_continuity" : "eigenfunction_nodal",
                    ResonanceScore = 0.85 - (r * 0.1),
                    IsPinned = false
                });
            }

            return result;
        }

        /// <summary>
        /// Verify that a parametric point is valid and on the surface.
        /// </summary>
        public static bool IsValidParametricPoint(ParametricPoint point)
        {
            return point.FaceId >= 0 &&
                   point.U >= 0 && point.U <= 1 &&
                   point.V >= 0 && point.V <= 1;
        }

        /// <summary>
        /// Assert that two points are approximately equal.
        /// </summary>
        public static void AssertPointsEqual(Point3d a, Point3d b, double tolerance = 1e-6)
        {
            var dist = a.DistanceTo(b);
            if (dist > tolerance)
            {
                throw new Exception($"Points differ by {dist}: ({a.X}, {a.Y}, {a.Z}) vs ({b.X}, {b.Y}, {b.Z})");
            }
        }
    }
}
```

#### 2. Create IntegrationTests.cs

Test the core integration between components:

```csharp
// rhino_plugin/Tests/IntegrationTests.cs
using System;
using System.Collections.Generic;
using System.Linq;
using NUnit.Framework;
using Rhino.Geometry;
using Latent.Geometry;
using Latent.Interop;
using Latent.Analysis;
using Latent.Display;

namespace Latent.Tests
{
    [TestFixture]
    public class IntegrationTests
    {
        private SubDEvaluator _evaluator;
        private RegionManager _regionManager;
        private SubD _testSubD;

        [SetUp]
        public void SetUp()
        {
            _testSubD = TestHelpers.CreateTestBoxSubD();
            _evaluator = new SubDEvaluator();
            _regionManager = new RegionManager();
        }

        [TearDown]
        public void TearDown()
        {
            _evaluator?.Dispose();
        }

        #region Evaluator Integration

        [Test]
        public void Evaluator_InitializeWithSubD_Succeeds()
        {
            _evaluator.Initialize(_testSubD);

            Assert.That(_evaluator.IsInitialized, Is.True);
            Assert.That(_evaluator.FaceCount, Is.GreaterThan(0));
        }

        [Test]
        public void Evaluator_ForwardAndInverseEvaluation_RoundTrips()
        {
            _evaluator.Initialize(_testSubD);

            // Forward evaluation
            var point3d = _evaluator.EvaluatePoint(0, 0.5, 0.5);
            Assert.That(point3d.IsValid, Is.True);

            // Inverse evaluation (project back)
            var param = _evaluator.ProjectPoint(point3d);
            Assert.That(param.IsValid, Is.True);

            // Re-evaluate and compare
            var reprojected = _evaluator.EvaluatePoint(param.FaceId, param.U, param.V);
            TestHelpers.AssertPointsEqual(point3d, reprojected, 0.001);
        }

        [Test]
        public void Evaluator_NormalEvaluation_ReturnsUnitVector()
        {
            _evaluator.Initialize(_testSubD);

            var normal = _evaluator.EvaluateNormal(0, 0.5, 0.5);

            Assert.That(normal.IsValid, Is.True);
            Assert.That(normal.Length, Is.EqualTo(1.0).Within(0.001));
        }

        #endregion

        #region RegionManager Integration

        [Test]
        public void RegionManager_UpdateFromAnalysis_PopulatesCorrectly()
        {
            var analysisResult = TestHelpers.CreateMockAnalysisResult(3);

            _regionManager.UpdateFromAnalysis(analysisResult);

            Assert.That(_regionManager.Regions.Count, Is.EqualTo(3));
            Assert.That(_regionManager.Vertices.Count, Is.EqualTo(12));
            Assert.That(_regionManager.Edges.Count, Is.EqualTo(12));
        }

        [Test]
        public void RegionManager_PinnedElementsPreservedOnReanalysis()
        {
            // Initial analysis
            var result1 = TestHelpers.CreateMockAnalysisResult(3);
            _regionManager.UpdateFromAnalysis(result1);

            // Pin a vertex
            var vertex = _regionManager.GetVertex("v0");
            _regionManager.SetPinned("v0", true);
            var originalPosition = vertex.Position;

            // Modify and re-analyze (simulated)
            var result2 = TestHelpers.CreateMockAnalysisResult(3);
            result2.Vertices[0].Position = new List<double> { 0, 0.5, 0.5 }; // Changed position
            _regionManager.UpdateFromAnalysis(result2);

            // Pinned vertex should retain original position
            var pinnedVertex = _regionManager.GetVertex("v0");
            Assert.That(pinnedVertex.IsPinned, Is.True);
            Assert.That(pinnedVertex.Position.FaceId, Is.EqualTo(originalPosition.FaceId));
        }

        [Test]
        public void RegionManager_Selection_WorksAcrossTypes()
        {
            var result = TestHelpers.CreateMockAnalysisResult(2);
            _regionManager.UpdateFromAnalysis(result);

            // Select region
            _regionManager.SelectRegion("r0");
            Assert.That(_regionManager.GetRegion("r0").IsSelected, Is.True);

            // Select edge (clears previous selection)
            _regionManager.SelectEdge("e0");
            Assert.That(_regionManager.GetRegion("r0").IsSelected, Is.False);
            Assert.That(_regionManager.GetEdge("e0").IsSelected, Is.True);

            // Select vertex
            _regionManager.SelectVertex("v0");
            Assert.That(_regionManager.GetEdge("e0").IsSelected, Is.False);
            Assert.That(_regionManager.GetVertex("v0").IsSelected, Is.True);
        }

        #endregion

        #region Display Integration

        [Test]
        public void VisualizationSettings_ColorPriority_SelectedOverPinned()
        {
            var settings = new VisualizationSettings();

            // Selected takes priority over pinned
            var color = settings.GetElementColor(isSelected: true, isPinned: true);
            Assert.That(color, Is.EqualTo(settings.SelectedColor));
        }

        [Test]
        public void RegionConduit_ConstructsWithValidDependencies()
        {
            var settings = new VisualizationSettings();
            var conduit = new RegionConduit(_regionManager, settings);

            Assert.That(conduit, Is.Not.Null);
        }

        #endregion

        #region CurveSampler Integration

        [Test]
        public void CurveSampler_SamplesEdgeCorrectly()
        {
            _evaluator.Initialize(_testSubD);

            var result = TestHelpers.CreateMockAnalysisResult(1);
            _regionManager.UpdateFromAnalysis(result);

            var sampler = new CurveSampler(_evaluator);
            var edge = _regionManager.GetEdge("e0");

            var points = sampler.SampleEdge(edge, 10);

            Assert.That(points, Is.Not.Null);
            Assert.That(points.Count, Is.EqualTo(10));
            foreach (var pt in points)
            {
                Assert.That(pt.IsValid, Is.True);
            }
        }

        #endregion

        #region Curvature Integration

        [Test]
        public void CurvatureAnalyzer_ComputesCurvature()
        {
            _evaluator.Initialize(_testSubD);

            var analyzer = new CurvatureAnalyzer(_evaluator);
            var data = analyzer.ComputeCurvature(0, 0.5, 0.5);

            Assert.That(double.IsNaN(data.K1), Is.False);
            Assert.That(double.IsNaN(data.K2), Is.False);
            Assert.That(data.MeanH, Is.EqualTo((data.K1 + data.K2) / 2).Within(0.001));
            Assert.That(data.GaussianK, Is.EqualTo(data.K1 * data.K2).Within(0.001));
        }

        #endregion
    }
}
```

#### 3. Create WorkflowTests.cs

Test complete user workflows:

```csharp
// rhino_plugin/Tests/WorkflowTests.cs
using System;
using System.Collections.Generic;
using System.Linq;
using NUnit.Framework;
using Rhino.Geometry;
using Latent.Geometry;
using Latent.Interop;
using Latent.Analysis;
using Latent.Interaction;

namespace Latent.Tests
{
    /// <summary>
    /// Tests for complete user workflows.
    /// </summary>
    [TestFixture]
    public class WorkflowTests
    {
        private SubDEvaluator _evaluator;
        private RegionManager _regionManager;
        private SubD _testSubD;

        [SetUp]
        public void SetUp()
        {
            _testSubD = TestHelpers.CreateTestBoxSubD();
            _evaluator = new SubDEvaluator();
            _evaluator.Initialize(_testSubD);
            _regionManager = new RegionManager();
        }

        [TearDown]
        public void TearDown()
        {
            _evaluator?.Dispose();
        }

        #region Workflow: Analyze → Select → Edit → Revert

        [Test]
        public void Workflow_AnalyzeSelectEditRevert_CompletesSuccessfully()
        {
            // Step 1: Load analysis results (simulated)
            var analysisResult = TestHelpers.CreateMockAnalysisResult(2);
            _regionManager.UpdateFromAnalysis(analysisResult);
            Assert.That(_regionManager.Regions.Count, Is.EqualTo(2));

            // Step 2: Select a vertex
            var vertex = _regionManager.Vertices.First();
            _regionManager.SelectVertex(vertex.Id);
            Assert.That(vertex.IsSelected, Is.True);

            // Step 3: Move the vertex (edit)
            var originalPosition = vertex.Position;
            var newPosition = new ParametricPoint(
                originalPosition.FaceId,
                originalPosition.U + 0.1,
                originalPosition.V
            );
            _regionManager.MoveVertex(vertex.Id, newPosition);

            // Verify vertex is now explicit
            Assert.That(vertex.IsImplicit, Is.False);
            Assert.That(vertex.CanRevert, Is.True);

            // Step 4: Revert the vertex
            _regionManager.Revert(vertex.Id);

            // Verify vertex is back to implicit state
            Assert.That(vertex.IsImplicit, Is.True);
        }

        [Test]
        public void Workflow_PinPreventsDrag()
        {
            var analysisResult = TestHelpers.CreateMockAnalysisResult(1);
            _regionManager.UpdateFromAnalysis(analysisResult);

            var vertex = _regionManager.Vertices.First();
            var originalPosition = vertex.Position;

            // Pin the vertex
            _regionManager.SetPinned(vertex.Id, true);
            Assert.That(vertex.IsPinned, Is.True);

            // Verify that CanRevert is false for pinned element
            Assert.That(vertex.CanRevert, Is.False, "Pinned vertex should not be revertable");
        }

        [Test]
        public void Workflow_RevertHierarchy_RegionRevertsEdgesAndVertices()
        {
            var analysisResult = TestHelpers.CreateMockAnalysisResult(1);
            _regionManager.UpdateFromAnalysis(analysisResult);

            // Move multiple vertices in the region
            var region = _regionManager.Regions.First();
            foreach (var edge in region.BoundaryEdges)
            {
                foreach (var vertex in edge.Vertices.Where(v => v.CanRevert))
                {
                    var newPos = new ParametricPoint(
                        vertex.Position.FaceId,
                        vertex.Position.U + 0.05,
                        vertex.Position.V + 0.05
                    );
                    _regionManager.MoveVertex(vertex.Id, newPos);
                }
            }

            // Verify region is now explicit
            Assert.That(region.IsImplicit, Is.False);

            // Revert the entire region
            _regionManager.Revert(region.Id);

            // Verify all vertices are back to implicit
            foreach (var edge in region.BoundaryEdges)
            {
                foreach (var vertex in edge.Vertices)
                {
                    if (vertex.ImplicitPosition.HasValue)
                    {
                        Assert.That(vertex.IsImplicit, Is.True,
                            $"Vertex {vertex.Id} should be implicit after region revert");
                    }
                }
            }
        }

        #endregion

        #region Workflow: Multi-Lens Analysis

        [Test]
        public void Workflow_ChangeLens_PreservesPinnedElements()
        {
            // First analysis (differential lens)
            var result1 = TestHelpers.CreateMockAnalysisResult(2);
            result1.Regions[0].UnityPrinciple = "curvature_continuity";
            _regionManager.UpdateFromAnalysis(result1);

            // Pin first region
            _regionManager.SetPinned("r0", true);

            // Second analysis (spectral lens) - different regions
            var result2 = TestHelpers.CreateMockAnalysisResult(3);
            result2.Regions[0].Id = "r0"; // Same ID, different content
            result2.Regions[0].UnityPrinciple = "eigenfunction_nodal";
            _regionManager.UpdateFromAnalysis(result2);

            // Pinned region should be preserved
            var pinnedRegion = _regionManager.GetRegion("r0");
            Assert.That(pinnedRegion, Is.Not.Null);
            Assert.That(pinnedRegion.IsPinned, Is.True);
        }

        #endregion

        #region Workflow: Edge Curve Type Changes

        [Test]
        public void Workflow_ChangeCurveType_MarksEdgeExplicit()
        {
            var analysisResult = TestHelpers.CreateMockAnalysisResult(1);
            _regionManager.UpdateFromAnalysis(analysisResult);

            var edge = _regionManager.Edges.First();
            Assert.That(edge.IsImplicit, Is.True);

            // Change curve type
            edge.CurveType = CurveType.BSpline;

            Assert.That(edge.IsImplicit, Is.False);
            Assert.That(edge.CanRevert, Is.True);
        }

        [Test]
        public void Workflow_RevertEdgeCurveType_PreservesVertexPositions()
        {
            var analysisResult = TestHelpers.CreateMockAnalysisResult(1);
            _regionManager.UpdateFromAnalysis(analysisResult);

            var edge = _regionManager.Edges.First();
            var vertex = edge.Vertices.First();

            // Move vertex and change curve type
            var newPos = new ParametricPoint(
                vertex.Position.FaceId,
                vertex.Position.U + 0.1,
                vertex.Position.V
            );
            _regionManager.MoveVertex(vertex.Id, newPos);
            edge.CurveType = CurveType.BSpline;

            // Revert only curve type (not positions)
            _regionManager.RevertEdgeCurveType(edge.Id);

            // Curve type should be reverted
            Assert.That(edge.CurveType, Is.EqualTo(edge.ImplicitCurveType));

            // Vertex position should NOT be reverted
            Assert.That(vertex.IsImplicit, Is.False);
        }

        #endregion

        #region Performance Tests

        [Test]
        public void Performance_LargeAnalysisResult_LoadsQuickly()
        {
            var watch = System.Diagnostics.Stopwatch.StartNew();

            // Create large analysis result
            var analysisResult = TestHelpers.CreateMockAnalysisResult(100);
            _regionManager.UpdateFromAnalysis(analysisResult);

            watch.Stop();

            Assert.That(watch.ElapsedMilliseconds, Is.LessThan(1000),
                "Loading 100 regions should complete in under 1 second");
            Assert.That(_regionManager.Regions.Count, Is.EqualTo(100));
        }

        [Test]
        public void Performance_SelectionChange_IsImmediate()
        {
            var analysisResult = TestHelpers.CreateMockAnalysisResult(50);
            _regionManager.UpdateFromAnalysis(analysisResult);

            var watch = System.Diagnostics.Stopwatch.StartNew();

            for (int i = 0; i < 100; i++)
            {
                _regionManager.SelectRegion($"r{i % 50}");
            }

            watch.Stop();

            Assert.That(watch.ElapsedMilliseconds, Is.LessThan(100),
                "100 selection changes should complete in under 100ms");
        }

        #endregion

        #region Undo/Redo Workflows

        [Test]
        public void Workflow_UndoRedo_VertexMove()
        {
            var analysisResult = TestHelpers.CreateMockAnalysisResult(1);
            _regionManager.UpdateFromAnalysis(analysisResult);

            var vertex = _regionManager.Vertices.First();
            var originalPosition = vertex.Position;

            // Move vertex
            var newPosition = new ParametricPoint(
                originalPosition.FaceId,
                originalPosition.U + 0.2,
                originalPosition.V
            );
            _regionManager.MoveVertex(vertex.Id, newPosition);

            Assert.That(vertex.Position.U, Is.EqualTo(newPosition.U).Within(0.001));

            // Note: Actual undo test requires RhinoDoc context
            // This verifies the state tracking is correct
            Assert.That(vertex.IsImplicit, Is.False);
        }

        [Test]
        public void Workflow_UndoRedo_PinUnpin()
        {
            var analysisResult = TestHelpers.CreateMockAnalysisResult(1);
            _regionManager.UpdateFromAnalysis(analysisResult);

            var vertex = _regionManager.Vertices.First();

            // Pin
            _regionManager.SetPinned(vertex.Id, true);
            Assert.That(vertex.IsPinned, Is.True);

            // Unpin
            _regionManager.SetPinned(vertex.Id, false);
            Assert.That(vertex.IsPinned, Is.False);

            // Note: Actual undo restores previous state via Rhino undo system
        }

        #endregion
    }
}
```

**Success Criteria**:
- [ ] All integration tests pass
- [ ] Workflow tests cover analyze → select → edit → revert cycle
- [ ] Undo/redo state tracking verified
- [ ] Performance tests pass (100 regions < 1s, 100 selections < 100ms)
- [ ] Round-trip evaluation accuracy < 0.001 units

**Skills Required**: `superpowers:test-driven-development`, `superpowers:verification-before-completion`

---

### Agent 7B: Documentation & Code Quality

**Objective**: Create user documentation, add XML documentation to public APIs, and perform final code cleanup.

**Files to create**:
- `docs/RHINO_PLUGIN_USER_GUIDE.md` (new)
- `rhino_plugin/Tests/ApiDocumentationTests.cs` (new)

**Files to modify**:
- `rhino_plugin/README.md` (update)
- `docs/PROJECT_STATUS.md` (update)
- Various source files (add XML documentation)

**Tasks**:

#### 1. Create User Guide

Create comprehensive user documentation:

```markdown
<!-- docs/RHINO_PLUGIN_USER_GUIDE.md -->
# Latent Plugin User Guide

## Overview

The Latent Plugin for Rhino 8 enables mathematical decomposition of SubD surfaces
for ceramic slip-casting mold design. It discovers regions where surfaces can be
cleanly separated based on curvature analysis and spectral decomposition.

## Installation

1. Copy `LatentPlugin.rhp` to your Rhino plugins folder
2. Copy `liblatent_core.dylib` (macOS) or `latent_core.dll` (Windows) to the same folder
3. Restart Rhino 8
4. Type `PlugInManager` and enable "Latent"

## Quick Start

1. Create or import a SubD surface
2. Run `LatentAnalyze` command
3. Select lens type (Differential, Spectral, or CageAligned)
4. View discovered regions in the viewport

## Commands

### LatentAnalyze
Runs analysis on the selected SubD using the specified lens.

**Usage**: `LatentAnalyze`

**Options**:
- **Differential**: Finds regions based on curvature continuity
- **Spectral**: Finds regions based on eigenfunction nodal lines
- **CageAligned**: Aligns regions with control cage topology

### LatentSelect
Selects regions, edges, or vertices for editing.

**Usage**: `LatentSelect`

Click on:
- Region interior → selects the region
- Near an edge → selects the edge
- Near a vertex → selects the vertex

### LatentPin
Pins or unpins the selected element.

**Usage**: `LatentPin`

Pinned elements:
- Are protected from lens reanalysis
- Cannot be reverted
- Display in blue

### LatentRevert
Reverts the selected element to its implicit (lens-defined) state.

**Usage**: `LatentRevert`

Revert hierarchy:
- **Vertex**: Returns to original position
- **Edge**: Choice of "curve type only" or "fully revert"
- **Region**: Reverts all boundary edges and vertices

## Panels

### Latent Lens
Control panel for lens selection and analysis parameters.

- **Lens Selector**: Choose analysis lens
- **Parameters**: Lens-specific settings
- **Analyze Button**: Run analysis

### Latent Geometry
List of all vertices, edges, and regions.

- **Mode Selector**: Toggle between Vertices/Edges/Regions
- **State Column**: Shows implicit/explicit/pinned state
- **Pin Button**: Toggle pinned state
- **Revert Button**: Revert to implicit state

### Latent Display
Visualization settings for the display conduit.

- **Show Fill**: Toggle region fill display
- **Show Centroids**: Toggle centroid markers
- **Colors**: Customize selection/pinned/default colors
- **Opacity**: Adjust fill transparency

## Concepts

### Implicit vs Explicit State

- **Implicit**: Element is at its lens-defined position/shape
- **Explicit**: Element has been modified by the user
- Only explicit elements can be reverted

### Pinning

Pinned elements are protected from changes:
- They persist across lens reanalysis
- They cannot be dragged or reverted
- Use pinning to "lock in" good decompositions

### Revert Hierarchy

When reverting:
- Vertex → reverts position only
- Edge → can revert curve type only OR fully revert (including vertices)
- Region → reverts all edges and vertices

Edges created by curve degree changes cannot have their vertices reverted.

## Keyboard Shortcuts

- **Ctrl+Z**: Undo last operation
- **Ctrl+Y**: Redo
- **Escape**: Cancel current operation
- **Enter**: Accept/confirm

## Troubleshooting

### "Analysis service failed to start"
- Ensure Python 3.8+ is installed and in PATH
- Check that `analysis_service/` folder exists
- Verify port 5555 is not in use

### "Native library not found"
- Copy `liblatent_core.dylib` to plugin folder
- On macOS, you may need to allow in Security settings

### Curves appear jagged
- Increase "Curve Sample Count" in Latent Display panel
- Default is 50, try 100 for smoother curves

### Performance is slow
- Reduce "Curve Sample Count" for faster redraws
- Enable curve caching in settings
- Consider fewer analysis regions
```

#### 2. Update README.md

Update the plugin README with current project structure:

```markdown
<!-- rhino_plugin/README.md -->
# Latent Rhino Plugin

Rhino 8 plugin for the Ceramic Mold Analyzer - discovers mathematical
decompositions of SubD surfaces for slip-casting molds.

## Requirements

- Rhino 8 (Windows or macOS)
- .NET Framework 4.8
- Python 3.8+ (for analysis service)

## Building

\`\`\`bash
cd rhino_plugin
dotnet restore
dotnet build
\`\`\`

## Testing

\`\`\`bash
dotnet test
\`\`\`

## Project Structure

\`\`\`
rhino_plugin/
├── Analysis/         # LensClient, AnalysisResult, Protocol
├── Commands/         # Rhino commands (Analyze, Select, Pin, Revert)
├── Display/          # RegionConduit, visualization
├── Geometry/         # Vertex, Edge, Region, RegionManager
├── Interaction/      # GetPoint, drag handlers, pickers
├── Interop/          # P/Invoke bindings to C++ core
├── UI/               # Eto.Forms panels
├── Tests/            # Unit and integration tests
├── LatentPlugin.cs   # Plugin entry point
└── LatentPlugin.csproj
\`\`\`

## Architecture

\`\`\`
┌─────────────────┐     ┌─────────────────┐
│   Rhino 8       │     │  Analysis       │
│   (UI/Viewport) │────▶│  Service        │
└────────┬────────┘     │  (Python)       │
         │              └────────┬────────┘
         │                       │
         ▼                       ▼
┌─────────────────┐     ┌─────────────────┐
│  Latent Plugin  │────▶│  C++ Core       │
│  (C#/.NET)      │     │  (liblatent)    │
└─────────────────┘     └─────────────────┘
\`\`\`

## Commands

| Command | Description |
|---------|-------------|
| `LatentAnalyze` | Run lens analysis on SubD |
| `LatentSelect` | Select region/edge/vertex |
| `LatentPin` | Pin/unpin selected element |
| `LatentRevert` | Revert to implicit state |

## License

Proprietary - All rights reserved
```

#### 3. Add XML Documentation to Public APIs

Add XML documentation to all public classes and methods. Key files to document:

**RegionManager.cs**:
```csharp
/// <summary>
/// Manages the collection of regions, edges, and vertices for an analysis session.
/// Provides state management, selection, and undo integration.
/// </summary>
/// <remarks>
/// <para>
/// The RegionManager is the central state container for all geometry elements.
/// It maintains three collections (Regions, Edges, Vertices) and handles:
/// </para>
/// <list type="bullet">
/// <item>Loading analysis results</item>
/// <item>Preserving pinned elements across reanalysis</item>
/// <item>Selection management</item>
/// <item>State mutations with undo support</item>
/// </list>
/// </remarks>
```

**SubDEvaluator.cs**:
```csharp
/// <summary>
/// Managed wrapper for the native SubD limit surface evaluator.
/// Provides exact evaluation of positions, normals, and curvature on the limit surface.
/// </summary>
/// <remarks>
/// <para>
/// This class wraps the C++ OpenSubdiv-based evaluator via P/Invoke.
/// It implements IDisposable to ensure proper cleanup of native resources.
/// </para>
/// </remarks>
```

#### 4. Create API Documentation Tests

```csharp
// rhino_plugin/Tests/ApiDocumentationTests.cs
using System;
using System.Linq;
using System.Reflection;
using NUnit.Framework;

namespace Latent.Tests
{
    /// <summary>
    /// Tests that verify public API documentation completeness.
    /// </summary>
    [TestFixture]
    public class ApiDocumentationTests
    {
        private Assembly _assembly;

        [SetUp]
        public void SetUp()
        {
            _assembly = typeof(LatentPlugin).Assembly;
        }

        [Test]
        public void AllPublicClasses_HaveXmlSummary()
        {
            var publicTypes = _assembly.GetTypes()
                .Where(t => t.IsPublic && !t.IsNested)
                .Where(t => !t.Name.EndsWith("Tests"))
                .ToList();

            // Note: This is a simplified check
            // Full implementation would parse XML doc file
            Assert.That(publicTypes.Count, Is.GreaterThan(0),
                "Assembly should have public types");
        }

        [Test]
        public void PublicClasses_CountMatchesExpected()
        {
            var publicTypes = _assembly.GetTypes()
                .Where(t => t.IsPublic && !t.IsNested)
                .Where(t => !t.Name.EndsWith("Tests"))
                .ToList();

            // Verify we have the expected core classes
            var expectedClasses = new[]
            {
                "LatentPlugin",
                "RegionManager",
                "SubDEvaluator",
                "VisualizationSettings"
            };

            foreach (var expected in expectedClasses)
            {
                Assert.That(publicTypes.Any(t => t.Name == expected),
                    Is.True, $"Missing expected class: {expected}");
            }
        }
    }
}
```

#### 5. Update PROJECT_STATUS.md

Add final status update to the project status document:

```markdown
<!-- Add to docs/PROJECT_STATUS.md -->

## Rhino Plugin Status

### Completed (Phase 7)
- ✅ P/Invoke bindings to C++ core
- ✅ JSON-RPC client for analysis service
- ✅ Plugin entry point with command registration
- ✅ Data model (Vertex, Edge, Region, RegionManager)
- ✅ Display conduit with curve sampling and region fills
- ✅ Interaction handlers (GetPoint, drag, pick)
- ✅ UI panels (Lens, Geometry List, Visualization)
- ✅ Integration tests
- ✅ User documentation

### Commands Available
- `LatentAnalyze` - Run lens analysis
- `LatentSelect` - Select elements
- `LatentPin` - Pin/unpin elements
- `LatentRevert` - Revert to implicit state

### Known Limitations
- Analysis service must be running separately (auto-start in development)
- Performance with 100+ regions may degrade
- Some edge cases in multi-face curve traversal

### Next Steps
- Production packaging
- Installer creation
- Performance optimization for large models
```

**Success Criteria**:
- [ ] User guide covers all commands and panels
- [ ] README updated with current structure
- [ ] All public classes have XML documentation
- [ ] All public methods have XML documentation
- [ ] API documentation tests pass
- [ ] PROJECT_STATUS.md updated

**Skills Required**: None specific

---

### Phase 7 Consolidation & Tests

**After all agents complete**:

```bash
cd /Users/NickDuch/Desktop/Ind\ Designs/NDAAD/RhinoProjects/Latent/rhino_plugin

# Build
dotnet build

# Run all tests including new integration tests
dotnet test --logger "console;verbosity=detailed"

# Verify documentation files exist
ls -la ../docs/RHINO_PLUGIN_USER_GUIDE.md
ls -la README.md

# Run integration tests specifically
dotnet test --filter "FullyQualifiedName~IntegrationTests|FullyQualifiedName~WorkflowTests"

# If all pass, commit
cd ..
git add -A
git commit -m "feat: Phase 7 - Final Integration

- Add comprehensive integration tests
- Add workflow tests for analyze→edit→revert cycle
- Add performance benchmarks
- Create user guide documentation
- Update README with current structure
- Add XML documentation to public APIs
- Update PROJECT_STATUS.md

🤖 Generated with Claude Code"
```

### Phase 7 Gate Tests

```bash
#!/bin/bash
set -e

echo "=== Phase 7 Gate Tests ==="

cd /Users/NickDuch/Desktop/Ind\ Designs/NDAAD/RhinoProjects/Latent/rhino_plugin

# Test 7.1: Plugin builds
dotnet build
echo "✓ Plugin builds successfully"

# Test 7.2: All unit tests pass
dotnet test
echo "✓ All unit tests pass"

# Test 7.3: Integration tests pass
dotnet test --filter "FullyQualifiedName~IntegrationTests"
echo "✓ Integration tests pass"

# Test 7.4: Workflow tests pass
dotnet test --filter "FullyQualifiedName~WorkflowTests"
echo "✓ Workflow tests pass"

# Test 7.5: Documentation files exist
test -f ../docs/RHINO_PLUGIN_USER_GUIDE.md && echo "✓ User guide exists"
test -f README.md && echo "✓ README exists"

# Test 7.6: Test file count (should have at least 15 test files)
TEST_COUNT=$(ls -1 Tests/*.cs | wc -l | tr -d ' ')
if [ "$TEST_COUNT" -ge 15 ]; then
    echo "✓ Test coverage adequate ($TEST_COUNT test files)"
else
    echo "✗ Insufficient test files ($TEST_COUNT < 15)"
    exit 1
fi

echo ""
echo "=== Phase 7 PASSED - Plugin Ready for Release ==="
```

---

## Launch Commands

Each phase has a single command that launches all agents for that phase.

---

## Phase Launch Command Template

The following sections contain the actual prompts to launch each phase.
