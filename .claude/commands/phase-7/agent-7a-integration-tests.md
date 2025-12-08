# Agent 7A: End-to-End Integration Tests

## Objective

Create comprehensive integration tests that verify the complete workflow from SubD selection through analysis, editing, and revert operations.

## Working Directory

`/Users/NickDuch/Desktop/Ind Designs/NDAAD/RhinoProjects/Latent`

## Read First

- `rhino_plugin/Geometry/RegionManager.cs` - state management
- `rhino_plugin/Interop/SubDEvaluator.cs` - native wrapper
- `rhino_plugin/Interop/ParametricPoint.cs` - coordinate type
- `rhino_plugin/Analysis/LensClient.cs` - analysis service client
- `rhino_plugin/Display/VisualizationSettings.cs` - display settings
- `docs/plans/2025-12-04-rhino-plugin-architecture-design.md` - data model

## Files to Create

1. `rhino_plugin/Tests/TestHelpers.cs` - reusable test utilities
2. `rhino_plugin/Tests/IntegrationTests.cs` - component integration tests
3. `rhino_plugin/Tests/WorkflowTests.cs` - complete workflow tests

## Tasks

### 1. Create TestHelpers.cs

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

            // Create vertices - 4 per region forming a quad boundary
            for (int i = 0; i < regionCount * 4; i++)
            {
                result.Vertices.Add(new VertexData
                {
                    Id = $"v{i}",
                    Position = new List<double> { 0, (i % 4) * 0.25, (i / 4) * 0.25 },
                    ImplicitPosition = new List<double> { 0, (i % 4) * 0.25, (i / 4) * 0.25 },
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
                    ImplicitCurveType = "bezier",
                    ImplicitDegree = 3,
                    IsPinned = false
                });
            }

            // Create regions with boundaries
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
        /// Verify that a parametric point is valid and within bounds.
        /// </summary>
        public static bool IsValidParametricPoint(ParametricPoint point)
        {
            return point.IsValid &&
                   point.FaceId >= 0 &&
                   point.U >= 0.0 && point.U <= 1.0 &&
                   point.V >= 0.0 && point.V <= 1.0;
        }

        /// <summary>
        /// Assert that two points are approximately equal within tolerance.
        /// </summary>
        public static void AssertPointsEqual(Point3d a, Point3d b, double tolerance = 1e-6)
        {
            var dist = a.DistanceTo(b);
            if (dist > tolerance)
            {
                throw new AssertionException(
                    $"Points differ by {dist}: ({a.X:F6}, {a.Y:F6}, {a.Z:F6}) vs ({b.X:F6}, {b.Y:F6}, {b.Z:F6})");
            }
        }

        /// <summary>
        /// Assert that two parametric points are approximately equal.
        /// </summary>
        public static void AssertParametricPointsEqual(
            ParametricPoint a, ParametricPoint b, double tolerance = 1e-4)
        {
            if (a.FaceId != b.FaceId)
            {
                throw new AssertionException(
                    $"Face IDs differ: {a.FaceId} vs {b.FaceId}");
            }
            if (Math.Abs(a.U - b.U) > tolerance || Math.Abs(a.V - b.V) > tolerance)
            {
                throw new AssertionException(
                    $"Parameters differ: ({a.U:F6}, {a.V:F6}) vs ({b.U:F6}, {b.V:F6})");
            }
        }

        /// <summary>
        /// Create a RegionManager populated with mock data.
        /// </summary>
        public static RegionManager CreatePopulatedRegionManager(int regionCount = 3)
        {
            var manager = new RegionManager();
            var result = CreateMockAnalysisResult(regionCount);
            manager.UpdateFromAnalysis(result);
            return manager;
        }

        /// <summary>
        /// Exception for test assertions.
        /// </summary>
        public class AssertionException : Exception
        {
            public AssertionException(string message) : base(message) { }
        }
    }

    /// <summary>
    /// Data transfer object for analysis vertex data.
    /// </summary>
    public class VertexData
    {
        public string Id { get; set; } = "";
        public List<double> Position { get; set; } = new();
        public List<double>? ImplicitPosition { get; set; }
        public string CreatedBy { get; set; } = "lens";
        public bool IsPinned { get; set; }
    }

    /// <summary>
    /// Data transfer object for analysis edge data.
    /// </summary>
    public class EdgeData
    {
        public string Id { get; set; } = "";
        public List<string> VertexIds { get; set; } = new();
        public string CurveType { get; set; } = "bezier";
        public int Degree { get; set; } = 3;
        public string? ImplicitCurveType { get; set; }
        public int? ImplicitDegree { get; set; }
        public bool IsPinned { get; set; }
    }

    /// <summary>
    /// Data transfer object for analysis region data.
    /// </summary>
    public class RegionData
    {
        public string Id { get; set; } = "";
        public List<string> BoundaryEdgeIds { get; set; } = new();
        public string UnityPrinciple { get; set; } = "";
        public double ResonanceScore { get; set; }
        public bool IsPinned { get; set; }
    }

    /// <summary>
    /// Container for complete analysis result data.
    /// </summary>
    public class AnalysisResultData
    {
        public List<VertexData> Vertices { get; set; } = new();
        public List<EdgeData> Edges { get; set; } = new();
        public List<RegionData> Regions { get; set; } = new();
    }
}
```

### 2. Create IntegrationTests.cs

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
    /// <summary>
    /// Integration tests verifying component interactions.
    /// </summary>
    [TestFixture]
    public class IntegrationTests
    {
        private SubDEvaluator? _evaluator;
        private RegionManager? _regionManager;
        private SubD? _testSubD;

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
            _evaluator = null;
            _regionManager = null;
            _testSubD = null;
        }

        #region Evaluator Integration

        [Test]
        public void Evaluator_InitializeWithSubD_Succeeds()
        {
            _evaluator!.Initialize(_testSubD!);

            Assert.That(_evaluator.IsInitialized, Is.True);
            Assert.That(_evaluator.FaceCount, Is.GreaterThan(0));
        }

        [Test]
        public void Evaluator_ForwardAndInverseEvaluation_RoundTrips()
        {
            _evaluator!.Initialize(_testSubD!);

            // Forward evaluation at face center
            var point3d = _evaluator.EvaluatePoint(0, 0.5, 0.5);
            Assert.That(point3d.IsValid, Is.True, "Forward evaluation should return valid point");

            // Inverse evaluation (project back)
            var param = _evaluator.ProjectPoint(point3d);
            Assert.That(param.IsValid, Is.True, "Projection should return valid parametric point");

            // Re-evaluate and compare
            var reprojected = _evaluator.EvaluatePoint(param.FaceId, param.U, param.V);
            TestHelpers.AssertPointsEqual(point3d, reprojected, 0.001);
        }

        [Test]
        public void Evaluator_MultiplePointsRoundTrip_AllSucceed()
        {
            _evaluator!.Initialize(_testSubD!);

            var testParams = new[]
            {
                (0, 0.25, 0.25),
                (0, 0.75, 0.25),
                (0, 0.25, 0.75),
                (0, 0.75, 0.75),
                (0, 0.5, 0.5)
            };

            foreach (var (faceId, u, v) in testParams)
            {
                var point3d = _evaluator.EvaluatePoint(faceId, u, v);
                var param = _evaluator.ProjectPoint(point3d);

                Assert.That(param.IsValid, Is.True,
                    $"Projection failed for ({faceId}, {u}, {v})");

                var reprojected = _evaluator.EvaluatePoint(param.FaceId, param.U, param.V);
                TestHelpers.AssertPointsEqual(point3d, reprojected, 0.01);
            }
        }

        [Test]
        public void Evaluator_NormalEvaluation_ReturnsUnitVector()
        {
            _evaluator!.Initialize(_testSubD!);

            var normal = _evaluator.EvaluateNormal(0, 0.5, 0.5);

            Assert.That(normal.IsValid, Is.True);
            Assert.That(normal.Length, Is.EqualTo(1.0).Within(0.001),
                "Normal should be unit length");
        }

        [Test]
        public void Evaluator_CurvatureComputation_ReturnsValidValues()
        {
            _evaluator!.Initialize(_testSubD!);

            var curvature = _evaluator.ComputeCurvature(0, 0.5, 0.5);

            Assert.That(double.IsNaN(curvature.K1), Is.False, "K1 should not be NaN");
            Assert.That(double.IsNaN(curvature.K2), Is.False, "K2 should not be NaN");
            Assert.That(double.IsInfinity(curvature.K1), Is.False, "K1 should not be infinite");
            Assert.That(double.IsInfinity(curvature.K2), Is.False, "K2 should not be infinite");
        }

        #endregion

        #region RegionManager Integration

        [Test]
        public void RegionManager_UpdateFromAnalysis_PopulatesCorrectly()
        {
            var analysisResult = TestHelpers.CreateMockAnalysisResult(3);

            _regionManager!.UpdateFromAnalysis(analysisResult);

            Assert.That(_regionManager.Regions.Count, Is.EqualTo(3));
            Assert.That(_regionManager.Vertices.Count, Is.EqualTo(12));
            Assert.That(_regionManager.Edges.Count, Is.EqualTo(12));
        }

        [Test]
        public void RegionManager_GetById_ReturnsCorrectElements()
        {
            var analysisResult = TestHelpers.CreateMockAnalysisResult(2);
            _regionManager!.UpdateFromAnalysis(analysisResult);

            var vertex = _regionManager.GetVertex("v0");
            var edge = _regionManager.GetEdge("e0");
            var region = _regionManager.GetRegion("r0");

            Assert.That(vertex, Is.Not.Null);
            Assert.That(vertex!.Id, Is.EqualTo("v0"));

            Assert.That(edge, Is.Not.Null);
            Assert.That(edge!.Id, Is.EqualTo("e0"));

            Assert.That(region, Is.Not.Null);
            Assert.That(region!.Id, Is.EqualTo("r0"));
        }

        [Test]
        public void RegionManager_GetByInvalidId_ReturnsNull()
        {
            var analysisResult = TestHelpers.CreateMockAnalysisResult(1);
            _regionManager!.UpdateFromAnalysis(analysisResult);

            var vertex = _regionManager.GetVertex("nonexistent");
            var edge = _regionManager.GetEdge("nonexistent");
            var region = _regionManager.GetRegion("nonexistent");

            Assert.That(vertex, Is.Null);
            Assert.That(edge, Is.Null);
            Assert.That(region, Is.Null);
        }

        [Test]
        public void RegionManager_PinnedElementsPreservedOnReanalysis()
        {
            // Initial analysis
            var result1 = TestHelpers.CreateMockAnalysisResult(3);
            _regionManager!.UpdateFromAnalysis(result1);

            // Pin a vertex and record position
            var vertex = _regionManager.GetVertex("v0");
            Assert.That(vertex, Is.Not.Null);
            _regionManager.SetPinned("v0", true);
            var originalPosition = vertex!.Position;

            // Re-analyze with modified data
            var result2 = TestHelpers.CreateMockAnalysisResult(3);
            result2.Vertices[0].Position = new List<double> { 0, 0.99, 0.99 }; // Changed
            _regionManager.UpdateFromAnalysis(result2);

            // Pinned vertex should retain original position
            var pinnedVertex = _regionManager.GetVertex("v0");
            Assert.That(pinnedVertex, Is.Not.Null);
            Assert.That(pinnedVertex!.IsPinned, Is.True);
            Assert.That(pinnedVertex.Position.FaceId, Is.EqualTo(originalPosition.FaceId));
        }

        [Test]
        public void RegionManager_Selection_WorksAcrossTypes()
        {
            var result = TestHelpers.CreateMockAnalysisResult(2);
            _regionManager!.UpdateFromAnalysis(result);

            // Select region
            _regionManager.SelectRegion("r0");
            Assert.That(_regionManager.GetRegion("r0")!.IsSelected, Is.True);

            // Select edge (should clear previous selection)
            _regionManager.SelectEdge("e0");
            Assert.That(_regionManager.GetRegion("r0")!.IsSelected, Is.False);
            Assert.That(_regionManager.GetEdge("e0")!.IsSelected, Is.True);

            // Select vertex (should clear previous selection)
            _regionManager.SelectVertex("v0");
            Assert.That(_regionManager.GetEdge("e0")!.IsSelected, Is.False);
            Assert.That(_regionManager.GetVertex("v0")!.IsSelected, Is.True);
        }

        [Test]
        public void RegionManager_ClearSelection_ClearsAll()
        {
            var result = TestHelpers.CreateMockAnalysisResult(2);
            _regionManager!.UpdateFromAnalysis(result);

            _regionManager.SelectVertex("v0");
            Assert.That(_regionManager.GetVertex("v0")!.IsSelected, Is.True);

            _regionManager.ClearSelection();
            Assert.That(_regionManager.GetVertex("v0")!.IsSelected, Is.False);
        }

        [Test]
        public void RegionManager_ChangedEvent_FiresOnMutation()
        {
            var result = TestHelpers.CreateMockAnalysisResult(1);
            _regionManager!.UpdateFromAnalysis(result);

            var eventFired = false;
            _regionManager.Changed += (s, e) => eventFired = true;

            // Mutate
            _regionManager.SetPinned("v0", true);

            Assert.That(eventFired, Is.True, "Changed event should fire on mutation");
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
        public void VisualizationSettings_ColorPriority_PinnedOverNormal()
        {
            var settings = new VisualizationSettings();

            var pinnedColor = settings.GetElementColor(isSelected: false, isPinned: true);
            var normalColor = settings.GetElementColor(isSelected: false, isPinned: false);

            Assert.That(pinnedColor, Is.EqualTo(settings.PinnedColor));
            Assert.That(normalColor, Is.EqualTo(settings.NormalColor));
            Assert.That(pinnedColor, Is.Not.EqualTo(normalColor));
        }

        [Test]
        public void VisualizationSettings_DefaultValues_AreReasonable()
        {
            var settings = new VisualizationSettings();

            Assert.That(settings.ShowRegionFill, Is.False, "Fill should be off by default");
            Assert.That(settings.ShowCentroidMarkers, Is.False, "Centroids should be off by default");
            Assert.That(settings.CurveSampleCount, Is.GreaterThan(10), "Sample count should be reasonable");
        }

        [Test]
        public void RegionConduit_ConstructsWithValidDependencies()
        {
            var settings = new VisualizationSettings();
            var conduit = new RegionConduit(_regionManager!, settings);

            Assert.That(conduit, Is.Not.Null);
            Assert.That(conduit.Enabled, Is.False, "Should not be enabled by default");
        }

        #endregion

        #region CurveSampler Integration

        [Test]
        public void CurveSampler_SamplesEdgeCorrectly()
        {
            _evaluator!.Initialize(_testSubD!);

            var result = TestHelpers.CreateMockAnalysisResult(1);
            _regionManager!.UpdateFromAnalysis(result);

            var sampler = new CurveSampler(_evaluator);
            var edge = _regionManager.GetEdge("e0");

            var points = sampler.SampleEdge(edge!, 10);

            Assert.That(points, Is.Not.Null);
            Assert.That(points.Count, Is.EqualTo(10));
            foreach (var pt in points)
            {
                Assert.That(pt.IsValid, Is.True, "All sampled points should be valid");
            }
        }

        [Test]
        public void CurveSampler_EndpointsMatchVertices()
        {
            _evaluator!.Initialize(_testSubD!);

            var result = TestHelpers.CreateMockAnalysisResult(1);
            _regionManager!.UpdateFromAnalysis(result);

            var sampler = new CurveSampler(_evaluator);
            var edge = _regionManager.GetEdge("e0");

            var points = sampler.SampleEdge(edge!, 10);

            // First and last points should be close to vertex positions
            var startVertex = _regionManager.GetVertex(edge!.VertexIds[0]);
            var endVertex = _regionManager.GetVertex(edge.VertexIds[^1]);

            var startPos = _evaluator.EvaluatePoint(
                startVertex!.Position.FaceId,
                startVertex.Position.U,
                startVertex.Position.V);

            Assert.That(points[0].DistanceTo(startPos), Is.LessThan(0.1),
                "First sample should be near start vertex");
        }

        #endregion

        #region ParametricPoint Integration

        [Test]
        public void ParametricPoint_Unset_IsNotValid()
        {
            var unset = ParametricPoint.Unset;

            Assert.That(unset.IsValid, Is.False);
            Assert.That(unset.FaceId, Is.LessThan(0));
        }

        [Test]
        public void ParametricPoint_ValidConstruction_IsValid()
        {
            var point = new ParametricPoint(0, 0.5, 0.5);

            Assert.That(point.IsValid, Is.True);
            Assert.That(point.FaceId, Is.EqualTo(0));
            Assert.That(point.U, Is.EqualTo(0.5));
            Assert.That(point.V, Is.EqualTo(0.5));
        }

        [Test]
        public void ParametricPoint_Equality_WorksCorrectly()
        {
            var p1 = new ParametricPoint(0, 0.5, 0.5);
            var p2 = new ParametricPoint(0, 0.5, 0.5);
            var p3 = new ParametricPoint(1, 0.5, 0.5);

            Assert.That(p1, Is.EqualTo(p2));
            Assert.That(p1, Is.Not.EqualTo(p3));
        }

        #endregion
    }
}
```

### 3. Create WorkflowTests.cs

Test complete user workflows:

```csharp
// rhino_plugin/Tests/WorkflowTests.cs
using System;
using System.Collections.Generic;
using System.Diagnostics;
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
        private SubDEvaluator? _evaluator;
        private RegionManager? _regionManager;
        private SubD? _testSubD;

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
            _evaluator = null;
            _regionManager = null;
            _testSubD = null;
        }

        #region Workflow: Analyze -> Select -> Edit -> Revert

        [Test]
        public void Workflow_AnalyzeSelectEditRevert_CompletesSuccessfully()
        {
            // Step 1: Load analysis results
            var analysisResult = TestHelpers.CreateMockAnalysisResult(2);
            _regionManager!.UpdateFromAnalysis(analysisResult);
            Assert.That(_regionManager.Regions.Count, Is.EqualTo(2), "Should have 2 regions");

            // Step 2: Select a vertex
            var vertex = _regionManager.Vertices.First();
            _regionManager.SelectVertex(vertex.Id);
            Assert.That(vertex.IsSelected, Is.True, "Vertex should be selected");

            // Step 3: Move the vertex (explicit edit)
            var originalPosition = vertex.Position;
            var newPosition = new ParametricPoint(
                originalPosition.FaceId,
                Math.Min(originalPosition.U + 0.1, 1.0),
                originalPosition.V
            );
            _regionManager.MoveVertex(vertex.Id, newPosition);

            // Verify vertex is now explicit
            Assert.That(vertex.IsImplicit, Is.False, "Edited vertex should be explicit");
            Assert.That(vertex.CanRevert, Is.True, "Edited vertex should be revertable");

            // Step 4: Revert the vertex
            _regionManager.Revert(vertex.Id);

            // Verify vertex is back to implicit state
            Assert.That(vertex.IsImplicit, Is.True, "Reverted vertex should be implicit");
        }

        [Test]
        public void Workflow_PinPreventsDrag()
        {
            var analysisResult = TestHelpers.CreateMockAnalysisResult(1);
            _regionManager!.UpdateFromAnalysis(analysisResult);

            var vertex = _regionManager.Vertices.First();

            // Pin the vertex
            _regionManager.SetPinned(vertex.Id, true);
            Assert.That(vertex.IsPinned, Is.True, "Vertex should be pinned");

            // Verify that CanRevert is false for pinned element
            Assert.That(vertex.CanRevert, Is.False, "Pinned vertex should not be revertable");
        }

        [Test]
        public void Workflow_UnpinAllowsRevert()
        {
            var analysisResult = TestHelpers.CreateMockAnalysisResult(1);
            _regionManager!.UpdateFromAnalysis(analysisResult);

            var vertex = _regionManager.Vertices.First();
            var originalPosition = vertex.Position;

            // Edit vertex
            var newPosition = new ParametricPoint(
                originalPosition.FaceId,
                originalPosition.U + 0.1,
                originalPosition.V
            );
            _regionManager.MoveVertex(vertex.Id, newPosition);

            // Pin it
            _regionManager.SetPinned(vertex.Id, true);
            Assert.That(vertex.CanRevert, Is.False, "Pinned vertex cannot revert");

            // Unpin it
            _regionManager.SetPinned(vertex.Id, false);
            Assert.That(vertex.CanRevert, Is.True, "Unpinned explicit vertex can revert");

            // Now revert should work
            _regionManager.Revert(vertex.Id);
            Assert.That(vertex.IsImplicit, Is.True, "Should be back to implicit");
        }

        [Test]
        public void Workflow_RevertHierarchy_RegionRevertsEdgesAndVertices()
        {
            var analysisResult = TestHelpers.CreateMockAnalysisResult(1);
            _regionManager!.UpdateFromAnalysis(analysisResult);

            // Move multiple vertices in the region
            var region = _regionManager.Regions.First();
            var modifiedVertexIds = new List<string>();

            foreach (var edgeId in region.BoundaryEdgeIds)
            {
                var edge = _regionManager.GetEdge(edgeId);
                if (edge == null) continue;

                foreach (var vertexId in edge.VertexIds)
                {
                    var vertex = _regionManager.GetVertex(vertexId);
                    if (vertex == null || !vertex.CanRevert) continue;

                    var newPos = new ParametricPoint(
                        vertex.Position.FaceId,
                        Math.Min(vertex.Position.U + 0.05, 1.0),
                        Math.Min(vertex.Position.V + 0.05, 1.0)
                    );
                    _regionManager.MoveVertex(vertex.Id, newPos);
                    modifiedVertexIds.Add(vertex.Id);
                }
            }

            // Verify region is now explicit
            Assert.That(region.IsImplicit, Is.False, "Region should be explicit after vertex edits");
            Assert.That(modifiedVertexIds.Count, Is.GreaterThan(0), "Should have modified some vertices");

            // Revert the entire region
            _regionManager.Revert(region.Id);

            // Verify all vertices are back to implicit
            foreach (var vertexId in modifiedVertexIds)
            {
                var vertex = _regionManager.GetVertex(vertexId);
                if (vertex?.ImplicitPosition != null)
                {
                    Assert.That(vertex.IsImplicit, Is.True,
                        $"Vertex {vertexId} should be implicit after region revert");
                }
            }
        }

        #endregion

        #region Workflow: Multi-Lens Analysis

        [Test]
        public void Workflow_ChangeLens_PreservesPinnedElements()
        {
            // First analysis (differential lens simulation)
            var result1 = TestHelpers.CreateMockAnalysisResult(2);
            result1.Regions[0].UnityPrinciple = "curvature_continuity";
            _regionManager!.UpdateFromAnalysis(result1);

            // Pin first region and record state
            var pinnedRegionId = result1.Regions[0].Id;
            _regionManager.SetPinned(pinnedRegionId, true);
            var originalPrinciple = _regionManager.GetRegion(pinnedRegionId)!.UnityPrinciple;

            // Second analysis (spectral lens simulation) - different regions
            var result2 = TestHelpers.CreateMockAnalysisResult(3);
            result2.Regions[0].Id = pinnedRegionId; // Same ID, different content
            result2.Regions[0].UnityPrinciple = "eigenfunction_nodal";
            _regionManager.UpdateFromAnalysis(result2);

            // Pinned region should be preserved with original principle
            var pinnedRegion = _regionManager.GetRegion(pinnedRegionId);
            Assert.That(pinnedRegion, Is.Not.Null, "Pinned region should still exist");
            Assert.That(pinnedRegion!.IsPinned, Is.True, "Region should still be pinned");
            Assert.That(pinnedRegion.UnityPrinciple, Is.EqualTo(originalPrinciple),
                "Pinned region should preserve original unity principle");
        }

        [Test]
        public void Workflow_UnpinnedElementsUpdateOnReanalysis()
        {
            var result1 = TestHelpers.CreateMockAnalysisResult(2);
            _regionManager!.UpdateFromAnalysis(result1);

            // Don't pin anything
            var region = _regionManager.GetRegion("r0");
            var originalScore = region!.ResonanceScore;

            // Re-analyze with different score
            var result2 = TestHelpers.CreateMockAnalysisResult(2);
            result2.Regions[0].ResonanceScore = 0.99;
            _regionManager.UpdateFromAnalysis(result2);

            // Unpinned region should update
            var updatedRegion = _regionManager.GetRegion("r0");
            Assert.That(updatedRegion!.ResonanceScore, Is.EqualTo(0.99).Within(0.001),
                "Unpinned region should update on reanalysis");
        }

        #endregion

        #region Workflow: Edge Curve Type Changes

        [Test]
        public void Workflow_ChangeCurveType_MarksEdgeExplicit()
        {
            var analysisResult = TestHelpers.CreateMockAnalysisResult(1);
            _regionManager!.UpdateFromAnalysis(analysisResult);

            var edge = _regionManager.Edges.First();
            Assert.That(edge.IsImplicit, Is.True, "Edge should start implicit");

            // Change curve type
            _regionManager.SetEdgeCurveType(edge.Id, CurveType.BSpline, 4);

            Assert.That(edge.IsImplicit, Is.False, "Edge should be explicit after type change");
            Assert.That(edge.CurveType, Is.EqualTo(CurveType.BSpline));
            Assert.That(edge.Degree, Is.EqualTo(4));
        }

        [Test]
        public void Workflow_RevertEdgeCurveType_PreservesVertexPositions()
        {
            var analysisResult = TestHelpers.CreateMockAnalysisResult(1);
            _regionManager!.UpdateFromAnalysis(analysisResult);

            var edge = _regionManager.Edges.First();
            var vertexId = edge.VertexIds.First();
            var vertex = _regionManager.GetVertex(vertexId)!;

            // Move vertex
            var newPos = new ParametricPoint(
                vertex.Position.FaceId,
                vertex.Position.U + 0.1,
                vertex.Position.V
            );
            _regionManager.MoveVertex(vertex.Id, newPos);

            // Change curve type
            _regionManager.SetEdgeCurveType(edge.Id, CurveType.BSpline, 4);

            // Revert only curve type (not positions)
            _regionManager.RevertEdgeCurveType(edge.Id);

            // Curve type should be reverted
            Assert.That(edge.CurveType, Is.EqualTo(edge.ImplicitCurveType),
                "Curve type should be reverted");

            // Vertex position should NOT be reverted
            Assert.That(vertex.IsImplicit, Is.False,
                "Vertex should still be explicit after curve-type-only revert");
        }

        [Test]
        public void Workflow_RevertEdgeFully_RevertsEverything()
        {
            var analysisResult = TestHelpers.CreateMockAnalysisResult(1);
            _regionManager!.UpdateFromAnalysis(analysisResult);

            var edge = _regionManager.Edges.First();
            var vertexId = edge.VertexIds.First();
            var vertex = _regionManager.GetVertex(vertexId)!;

            // Move vertex
            var newPos = new ParametricPoint(
                vertex.Position.FaceId,
                vertex.Position.U + 0.1,
                vertex.Position.V
            );
            _regionManager.MoveVertex(vertex.Id, newPos);

            // Change curve type
            _regionManager.SetEdgeCurveType(edge.Id, CurveType.BSpline, 4);

            // Fully revert edge
            _regionManager.RevertEdgeFully(edge.Id);

            // Both should be reverted
            Assert.That(edge.IsImplicit, Is.True, "Edge should be implicit");
            Assert.That(vertex.IsImplicit, Is.True, "Vertex should be implicit");
        }

        #endregion

        #region Performance Tests

        [Test]
        public void Performance_LargeAnalysisResult_LoadsQuickly()
        {
            var watch = Stopwatch.StartNew();

            // Create large analysis result (100 regions)
            var analysisResult = TestHelpers.CreateMockAnalysisResult(100);
            _regionManager!.UpdateFromAnalysis(analysisResult);

            watch.Stop();

            Assert.That(watch.ElapsedMilliseconds, Is.LessThan(1000),
                $"Loading 100 regions should complete in under 1 second (took {watch.ElapsedMilliseconds}ms)");
            Assert.That(_regionManager.Regions.Count, Is.EqualTo(100));
        }

        [Test]
        public void Performance_SelectionChange_IsImmediate()
        {
            var analysisResult = TestHelpers.CreateMockAnalysisResult(50);
            _regionManager!.UpdateFromAnalysis(analysisResult);

            var watch = Stopwatch.StartNew();

            // Perform 100 selection changes
            for (int i = 0; i < 100; i++)
            {
                _regionManager.SelectRegion($"r{i % 50}");
            }

            watch.Stop();

            Assert.That(watch.ElapsedMilliseconds, Is.LessThan(100),
                $"100 selection changes should complete in under 100ms (took {watch.ElapsedMilliseconds}ms)");
        }

        [Test]
        public void Performance_ManyPinOperations_AreEfficient()
        {
            var analysisResult = TestHelpers.CreateMockAnalysisResult(50);
            _regionManager!.UpdateFromAnalysis(analysisResult);

            var watch = Stopwatch.StartNew();

            // Pin/unpin all vertices
            foreach (var vertex in _regionManager.Vertices)
            {
                _regionManager.SetPinned(vertex.Id, true);
                _regionManager.SetPinned(vertex.Id, false);
            }

            watch.Stop();

            Assert.That(watch.ElapsedMilliseconds, Is.LessThan(500),
                $"Pin/unpin operations should be efficient (took {watch.ElapsedMilliseconds}ms)");
        }

        #endregion

        #region State Consistency Tests

        [Test]
        public void StateConsistency_ImplicitVertex_HasMatchingPosition()
        {
            var analysisResult = TestHelpers.CreateMockAnalysisResult(1);
            _regionManager!.UpdateFromAnalysis(analysisResult);

            foreach (var vertex in _regionManager.Vertices)
            {
                if (vertex.IsImplicit && vertex.ImplicitPosition != null)
                {
                    Assert.That(vertex.Position.FaceId, Is.EqualTo(vertex.ImplicitPosition.Value.FaceId));
                    Assert.That(vertex.Position.U, Is.EqualTo(vertex.ImplicitPosition.Value.U).Within(0.0001));
                    Assert.That(vertex.Position.V, Is.EqualTo(vertex.ImplicitPosition.Value.V).Within(0.0001));
                }
            }
        }

        [Test]
        public void StateConsistency_ExplicitVertex_HasDifferentPosition()
        {
            var analysisResult = TestHelpers.CreateMockAnalysisResult(1);
            _regionManager!.UpdateFromAnalysis(analysisResult);

            var vertex = _regionManager.Vertices.First();
            var originalPos = vertex.Position;

            // Move it
            var newPos = new ParametricPoint(
                originalPos.FaceId,
                originalPos.U + 0.2,
                originalPos.V
            );
            _regionManager.MoveVertex(vertex.Id, newPos);

            Assert.That(vertex.IsImplicit, Is.False);
            Assert.That(vertex.Position.U, Is.Not.EqualTo(vertex.ImplicitPosition!.Value.U).Within(0.0001));
        }

        [Test]
        public void StateConsistency_RegionImplicitness_DependsOnEdges()
        {
            var analysisResult = TestHelpers.CreateMockAnalysisResult(1);
            _regionManager!.UpdateFromAnalysis(analysisResult);

            var region = _regionManager.Regions.First();
            Assert.That(region.IsImplicit, Is.True, "Fresh region should be implicit");

            // Modify an edge's curve type
            var edgeId = region.BoundaryEdgeIds.First();
            _regionManager.SetEdgeCurveType(edgeId, CurveType.BSpline, 4);

            Assert.That(region.IsImplicit, Is.False, "Region with modified edge should be explicit");
        }

        #endregion

        #region Edge Cases

        [Test]
        public void EdgeCase_MoveVertexToSamePosition_RemainsImplicit()
        {
            var analysisResult = TestHelpers.CreateMockAnalysisResult(1);
            _regionManager!.UpdateFromAnalysis(analysisResult);

            var vertex = _regionManager.Vertices.First();
            var originalPos = vertex.Position;

            // "Move" to same position
            _regionManager.MoveVertex(vertex.Id, originalPos);

            // Should still be implicit since position didn't actually change
            Assert.That(vertex.IsImplicit, Is.True);
        }

        [Test]
        public void EdgeCase_PinUnpinCycle_PreservesState()
        {
            var analysisResult = TestHelpers.CreateMockAnalysisResult(1);
            _regionManager!.UpdateFromAnalysis(analysisResult);

            var vertex = _regionManager.Vertices.First();
            var originalImplicit = vertex.IsImplicit;
            var originalPosition = vertex.Position;

            // Pin/unpin cycle
            _regionManager.SetPinned(vertex.Id, true);
            _regionManager.SetPinned(vertex.Id, false);

            Assert.That(vertex.IsImplicit, Is.EqualTo(originalImplicit));
            Assert.That(vertex.Position, Is.EqualTo(originalPosition));
        }

        [Test]
        public void EdgeCase_RevertAlreadyImplicit_NoChange()
        {
            var analysisResult = TestHelpers.CreateMockAnalysisResult(1);
            _regionManager!.UpdateFromAnalysis(analysisResult);

            var vertex = _regionManager.Vertices.First();
            Assert.That(vertex.IsImplicit, Is.True);
            Assert.That(vertex.CanRevert, Is.False, "Implicit vertex should not be revertable");

            // Attempting revert on implicit vertex should not throw
            Assert.DoesNotThrow(() => _regionManager.Revert(vertex.Id));
        }

        [Test]
        public void EdgeCase_SelectNonexistent_NoException()
        {
            var analysisResult = TestHelpers.CreateMockAnalysisResult(1);
            _regionManager!.UpdateFromAnalysis(analysisResult);

            // Should not throw
            Assert.DoesNotThrow(() => _regionManager.SelectVertex("nonexistent"));
            Assert.DoesNotThrow(() => _regionManager.SelectEdge("nonexistent"));
            Assert.DoesNotThrow(() => _regionManager.SelectRegion("nonexistent"));
        }

        #endregion
    }
}
```

## Success Criteria

- [ ] All integration tests pass
- [ ] Workflow tests cover analyze -> select -> edit -> revert cycle
- [ ] Workflow tests cover multi-lens analysis with pinning
- [ ] Workflow tests cover edge curve type changes and revert options
- [ ] Performance tests pass (100 regions < 1s, 100 selections < 100ms)
- [ ] State consistency tests verify implicit/explicit logic
- [ ] Edge case tests handle boundary conditions gracefully
- [ ] Round-trip evaluation accuracy < 0.001 units
- [ ] Build succeeds with no errors or warnings

## Verification Commands

```bash
cd /Users/NickDuch/Desktop/Ind\ Designs/NDAAD/RhinoProjects/Latent/rhino_plugin

# Build
dotnet build

# Run all new tests
dotnet test --filter "FullyQualifiedName~IntegrationTests|FullyQualifiedName~WorkflowTests"

# Run with verbose output
dotnet test --filter "FullyQualifiedName~IntegrationTests" --logger "console;verbosity=detailed"

# Verify test files exist
ls Tests/TestHelpers.cs
ls Tests/IntegrationTests.cs
ls Tests/WorkflowTests.cs
```

## Do Not Modify

- Files in `Geometry/` (except adding test mocks if needed)
- Files in `Display/`
- Files in `Interaction/`
- Files in `UI/`
- Documentation files (Agent 7B's domain)

## Skills to Use

- `superpowers:test-driven-development` - write tests with clear assertions
- `superpowers:verification-before-completion` - run all tests before reporting

## Notes

- Tests should not require Rhino to be running (mock dependencies)
- Use `TestHelpers.CreateMockAnalysisResult()` for consistent test data
- Performance tests use `Stopwatch` for timing
- If certain classes don't exist yet, create minimal stubs to make tests compile
- Add `using` statements as needed for the actual namespace structure

## Report

When complete, provide:
1. Build output showing no errors
2. Test output showing all tests pass (or clear list of what's failing and why)
3. Performance test results with actual timings
4. Any missing dependencies or stubs that were needed
5. Count of total tests added
