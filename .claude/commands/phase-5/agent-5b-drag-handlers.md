# Agent 5B: Vertex & Edge Drag Handlers

## Objective

Implement drag operations for vertices and edges with visual preview, surface constraint, and undo integration.

## Working Directory

`/Users/NickDuch/Desktop/Ind Designs/NDAAD/RhinoProjects/Latent`

## Read First

- `docs/plans/2025-12-04-rhino-plugin-implementation-plan.md` - drag handler examples
- `rhino_plugin/Geometry/RegionManager.cs` - MoveVertex, MoveEdge methods
- `rhino_plugin/Geometry/Vertex.cs` - vertex with Position property
- `rhino_plugin/Geometry/Edge.cs` - edge with Vertices collection
- `rhino_plugin/Interaction/SurfaceConstrainedGetPoint.cs` - surface picking (Agent 5A)

## Dependencies

**From Phase 3:**
- `RegionManager` - provides `MoveVertex()`, `MoveEdge()` with undo
- `Vertex` - provides `Position`, `IsPinned`
- `Edge` - provides `Vertices`, `IsPinned`
- `SubDEvaluator` - provides `ProjectPoint()`, `EvaluatePoint()`

**From This Phase:**
- `SurfaceConstrainedGetPoint` (Agent 5A) - surface-constrained picking

**IMPORTANT**: Use `Latent.Interop.ParametricPoint` from Phase 3. Do NOT create a duplicate struct.

**RhinoCommon:**
- `Rhino.Geometry.SubD` - the surface for constraints
- `Rhino.Input.Custom.GetPoint` - base picking class

## Files to Create

1. `rhino_plugin/Interaction/VertexDragHandler.cs` - vertex drag operations
2. `rhino_plugin/Interaction/EdgeDragHandler.cs` - edge drag operations
3. `rhino_plugin/Interaction/DragPreview.cs` - visual preview during drag
4. `rhino_plugin/Tests/DragHandlerTests.cs` - unit tests

## Tasks

### 1. Create DragPreview.cs

```csharp
// rhino_plugin/Interaction/DragPreview.cs
using System;
using System.Collections.Generic;
using System.Drawing;
using Rhino.Display;
using Rhino.Geometry;
using Latent.Geometry;
using Latent.Interop;

namespace Latent.Interaction
{
    /// <summary>
    /// Provides visual preview during drag operations.
    /// Uses Latent.Interop.ParametricPoint for all parametric coordinates.
    /// </summary>
    public class DragPreview
    {
        private readonly SubDEvaluator _evaluator;

        /// <summary>
        /// Color for preview points.
        /// </summary>
        public Color PreviewPointColor { get; set; } = Color.Yellow;

        /// <summary>
        /// Color for preview lines.
        /// </summary>
        public Color PreviewLineColor { get; set; } = Color.FromArgb(128, Color.Yellow);

        /// <summary>
        /// Size for preview points.
        /// </summary>
        public int PreviewPointSize { get; set; } = 8;

        /// <summary>
        /// Line thickness for preview curves.
        /// </summary>
        public int PreviewLineThickness { get; set; } = 2;

        /// <summary>
        /// Whether to show connection lines to original position.
        /// </summary>
        public bool ShowDisplacementLines { get; set; } = true;

        public DragPreview(SubDEvaluator evaluator)
        {
            _evaluator = evaluator ?? throw new ArgumentNullException(nameof(evaluator));
        }

        /// <summary>
        /// Draw a vertex preview at new position.
        /// </summary>
        public void DrawVertexPreview(DisplayPipeline display, Vertex vertex, ParametricPoint newPosition)
        {
            if (display == null || vertex == null || !newPosition.IsValid)
                return;

            // Get 3D positions
            var originalPos = GetPoint3d(vertex.Position);
            var newPos = GetPoint3d(newPosition);

            // Draw preview point at new position
            display.DrawPoint(newPos, PointStyle.RoundControlPoint, PreviewPointSize, PreviewPointColor);

            // Draw displacement line
            if (ShowDisplacementLines)
            {
                display.DrawLine(originalPos, newPos, PreviewLineColor, PreviewLineThickness);
            }

            // Draw ghost at original position
            display.DrawPoint(originalPos, PointStyle.Circle, PreviewPointSize - 2, Color.FromArgb(128, Color.Gray));
        }

        /// <summary>
        /// Draw an edge preview at displaced positions.
        /// </summary>
        public void DrawEdgePreview(
            DisplayPipeline display,
            Edge edge,
            IReadOnlyList<ParametricPoint> newVertexPositions)
        {
            if (display == null || edge == null || newVertexPositions == null)
                return;

            var vertices = edge.Vertices;
            if (vertices.Count != newVertexPositions.Count)
                return;

            // Draw preview vertices
            for (int i = 0; i < vertices.Count; i++)
            {
                DrawVertexPreview(display, vertices[i], newVertexPositions[i]);
            }

            // Draw preview edge curve (polyline through new positions)
            if (newVertexPositions.Count >= 2)
            {
                var points = new List<Point3d>();
                foreach (var param in newVertexPositions)
                {
                    if (param.IsValid)
                    {
                        points.Add(GetPoint3d(param));
                    }
                }

                if (points.Count >= 2)
                {
                    display.DrawPolyline(points, PreviewPointColor, PreviewLineThickness);
                }
            }
        }

        /// <summary>
        /// Draw multiple vertices at displaced positions.
        /// </summary>
        public void DrawMultiVertexPreview(
            DisplayPipeline display,
            IReadOnlyList<Vertex> vertices,
            IReadOnlyList<ParametricPoint> newPositions)
        {
            if (display == null || vertices == null || newPositions == null)
                return;

            int count = Math.Min(vertices.Count, newPositions.Count);
            for (int i = 0; i < count; i++)
            {
                DrawVertexPreview(display, vertices[i], newPositions[i]);
            }
        }

        /// <summary>
        /// Get 3D point from parametric coordinates.
        /// </summary>
        private Point3d GetPoint3d(ParametricPoint param)
        {
            if (!param.IsValid)
                return Point3d.Unset;

            return _evaluator.EvaluatePoint(param.FaceId, param.U, param.V);
        }
    }
}
```

### 2. Create VertexDragHandler.cs

```csharp
// rhino_plugin/Interaction/VertexDragHandler.cs
using System;
using System.Drawing;
using Rhino;
using Rhino.Display;
using Rhino.Geometry;
using Rhino.Input;
using Rhino.Input.Custom;
using Latent.Geometry;
using Latent.Interop;

namespace Latent.Interaction
{
    /// <summary>
    /// Result from a vertex drag operation.
    /// </summary>
    public enum DragResult
    {
        Success,
        Canceled,
        Failed,
        Pinned   // Cannot drag pinned element
    }

    /// <summary>
    /// Handles vertex drag operations with surface constraint.
    /// Uses Latent.Interop.ParametricPoint throughout.
    /// </summary>
    public class VertexDragHandler
    {
        private readonly RegionManager _regionManager;
        private readonly SubDEvaluator _evaluator;
        private readonly SubD _subd;
        private readonly DragPreview _preview;

        /// <summary>
        /// Event raised when drag starts.
        /// </summary>
        public event EventHandler<VertexDragEventArgs> DragStarted;

        /// <summary>
        /// Event raised when drag completes.
        /// </summary>
        public event EventHandler<VertexDragEventArgs> DragCompleted;

        /// <summary>
        /// Event raised when drag is canceled.
        /// </summary>
        public event EventHandler<VertexDragEventArgs> DragCanceled;

        public VertexDragHandler(RegionManager regionManager, SubDEvaluator evaluator, SubD subd)
        {
            _regionManager = regionManager ?? throw new ArgumentNullException(nameof(regionManager));
            _evaluator = evaluator ?? throw new ArgumentNullException(nameof(evaluator));
            _subd = subd ?? throw new ArgumentNullException(nameof(subd));
            _preview = new DragPreview(evaluator);
        }

        /// <summary>
        /// Start an interactive drag operation for a vertex.
        /// </summary>
        /// <param name="vertex">The vertex to drag</param>
        /// <returns>Result of the drag operation</returns>
        public DragResult StartDrag(Vertex vertex)
        {
            if (vertex == null)
                throw new ArgumentNullException(nameof(vertex));

            // Check if vertex is pinned
            if (vertex.IsPinned)
            {
                RhinoApp.WriteLine("Cannot drag pinned vertex. Unpin first.");
                return DragResult.Pinned;
            }

            // Get original position
            var originalParam = vertex.Position;
            var originalPos3d = _evaluator.EvaluatePoint(
                originalParam.FaceId,
                originalParam.U,
                originalParam.V);

            // Raise start event
            DragStarted?.Invoke(this, new VertexDragEventArgs(vertex, originalParam));

            // Create surface-constrained GetPoint
            var gp = new SurfaceConstrainedGetPoint(_subd, _evaluator);
            gp.SetCommandPrompt("Drag vertex to new position (ESC to cancel)");
            gp.SetBasePoint(originalPos3d, showDistanceInStatusBar: true);

            // Track the current preview position
            ParametricPoint previewParam = originalParam;

            // Add dynamic draw for preview
            gp.DynamicDraw += (sender, e) =>
            {
                previewParam = gp.CurrentParametricPosition;
                _preview.DrawVertexPreview(e.Display, vertex, previewParam);
            };

            // Run the interaction
            var result = gp.Get();

            if (result == GetResult.Point)
            {
                var newParam = gp.CurrentParametricPosition;

                if (newParam.IsValid)
                {
                    // Apply the move through RegionManager (creates undo record)
                    _regionManager.MoveVertex(vertex, newParam);

                    // Raise completion event
                    DragCompleted?.Invoke(this, new VertexDragEventArgs(vertex, newParam));

                    return DragResult.Success;
                }
            }

            // Canceled or failed
            DragCanceled?.Invoke(this, new VertexDragEventArgs(vertex, originalParam));
            return DragResult.Canceled;
        }

        /// <summary>
        /// Apply a drag programmatically (for testing or scripted operations).
        /// </summary>
        public DragResult ApplyDrag(Vertex vertex, Point3d newPosition3d)
        {
            if (vertex == null)
                throw new ArgumentNullException(nameof(vertex));

            if (vertex.IsPinned)
                return DragResult.Pinned;

            // Project 3D position to surface
            var newParam = _evaluator.ProjectPoint(newPosition3d);
            if (newParam.IsValid)
            {
                _regionManager.MoveVertex(vertex, newParam);
                return DragResult.Success;
            }

            return DragResult.Failed;
        }
    }

    /// <summary>
    /// Event args for vertex drag operations.
    /// </summary>
    public class VertexDragEventArgs : EventArgs
    {
        public Vertex Vertex { get; }
        public ParametricPoint Position { get; }

        public VertexDragEventArgs(Vertex vertex, ParametricPoint position)
        {
            Vertex = vertex;
            Position = position;
        }
    }
}
```

### 3. Create EdgeDragHandler.cs

```csharp
// rhino_plugin/Interaction/EdgeDragHandler.cs
using System;
using System.Collections.Generic;
using System.Drawing;
using Rhino;
using Rhino.Display;
using Rhino.Geometry;
using Rhino.Input;
using Rhino.Input.Custom;
using Latent.Geometry;
using Latent.Interop;

namespace Latent.Interaction
{
    /// <summary>
    /// Handles edge drag operations (moves all vertices together).
    /// Uses Latent.Interop.ParametricPoint throughout.
    /// </summary>
    public class EdgeDragHandler
    {
        private readonly RegionManager _regionManager;
        private readonly SubDEvaluator _evaluator;
        private readonly SubD _subd;
        private readonly DragPreview _preview;

        /// <summary>
        /// Event raised when drag starts.
        /// </summary>
        public event EventHandler<EdgeDragEventArgs> DragStarted;

        /// <summary>
        /// Event raised when drag completes.
        /// </summary>
        public event EventHandler<EdgeDragEventArgs> DragCompleted;

        /// <summary>
        /// Event raised when drag is canceled.
        /// </summary>
        public event EventHandler<EdgeDragEventArgs> DragCanceled;

        public EdgeDragHandler(RegionManager regionManager, SubDEvaluator evaluator, SubD subd)
        {
            _regionManager = regionManager ?? throw new ArgumentNullException(nameof(regionManager));
            _evaluator = evaluator ?? throw new ArgumentNullException(nameof(evaluator));
            _subd = subd ?? throw new ArgumentNullException(nameof(subd));
            _preview = new DragPreview(evaluator);
        }

        /// <summary>
        /// Start an interactive drag operation for an edge.
        /// </summary>
        /// <param name="edge">The edge to drag</param>
        /// <returns>Result of the drag operation</returns>
        public DragResult StartDrag(Edge edge)
        {
            if (edge == null)
                throw new ArgumentNullException(nameof(edge));

            // Check if edge is pinned
            if (edge.IsPinned)
            {
                RhinoApp.WriteLine("Cannot drag pinned edge. Unpin first.");
                return DragResult.Pinned;
            }

            // Check if any vertex is pinned
            foreach (var vertex in edge.Vertices)
            {
                if (vertex.IsPinned)
                {
                    RhinoApp.WriteLine($"Cannot drag: vertex {vertex.Id} is pinned.");
                    return DragResult.Pinned;
                }
            }

            // Calculate edge centroid in 3D
            var centroid = CalculateCentroid(edge);

            // Store original positions
            var originalPositions = new List<ParametricPoint>();
            foreach (var v in edge.Vertices)
            {
                originalPositions.Add(v.Position);
            }

            // Raise start event
            DragStarted?.Invoke(this, new EdgeDragEventArgs(edge, originalPositions));

            // Create GetPoint for drag
            var gp = new GetPoint();
            gp.SetCommandPrompt("Drag edge to new position (ESC to cancel)");
            gp.SetBasePoint(centroid, showDistanceInStatusBar: true);
            gp.Constrain(_subd, allowPickingPointOffObject: false);

            // Track preview positions
            var previewPositions = new List<ParametricPoint>(originalPositions);

            // Add dynamic draw for preview
            gp.DynamicDraw += (sender, e) =>
            {
                // Calculate displacement
                var displacement = e.CurrentPoint - centroid;

                // Project each vertex to new position
                previewPositions.Clear();
                foreach (var vertex in edge.Vertices)
                {
                    var original3d = _evaluator.EvaluatePoint(
                        vertex.Position.FaceId,
                        vertex.Position.U,
                        vertex.Position.V);
                    var new3d = original3d + displacement;

                    // Project back to surface
                    var newParam = _evaluator.ProjectPoint(new3d);
                    previewPositions.Add(newParam);  // May be invalid if projection fails
                }

                // Draw preview
                _preview.DrawEdgePreview(e.Display, edge, previewPositions);
            };

            // Run the interaction
            var result = gp.Get();

            if (result == GetResult.Point)
            {
                var displacement = gp.Point() - centroid;

                // Apply moves to all vertices
                bool allSucceeded = true;
                for (int i = 0; i < edge.Vertices.Count; i++)
                {
                    var vertex = edge.Vertices[i];
                    var original3d = _evaluator.EvaluatePoint(
                        vertex.Position.FaceId,
                        vertex.Position.U,
                        vertex.Position.V);
                    var new3d = original3d + displacement;

                    var newParam = _evaluator.ProjectPoint(new3d);
                    if (newParam.IsValid)
                    {
                        _regionManager.MoveVertex(vertex, newParam);
                    }
                    else
                    {
                        allSucceeded = false;
                    }
                }

                // Raise completion event
                DragCompleted?.Invoke(this, new EdgeDragEventArgs(edge, previewPositions));

                return allSucceeded ? DragResult.Success : DragResult.Failed;
            }

            // Canceled
            DragCanceled?.Invoke(this, new EdgeDragEventArgs(edge, originalPositions));
            return DragResult.Canceled;
        }

        /// <summary>
        /// Apply an edge drag programmatically.
        /// </summary>
        public DragResult ApplyDrag(Edge edge, Vector3d displacement)
        {
            if (edge == null)
                throw new ArgumentNullException(nameof(edge));

            if (edge.IsPinned)
                return DragResult.Pinned;

            foreach (var vertex in edge.Vertices)
            {
                if (vertex.IsPinned)
                    return DragResult.Pinned;
            }

            bool allSucceeded = true;
            foreach (var vertex in edge.Vertices)
            {
                var original3d = _evaluator.EvaluatePoint(
                    vertex.Position.FaceId,
                    vertex.Position.U,
                    vertex.Position.V);
                var new3d = original3d + displacement;

                var newParam = _evaluator.ProjectPoint(new3d);
                if (newParam.IsValid)
                {
                    _regionManager.MoveVertex(vertex, newParam);
                }
                else
                {
                    allSucceeded = false;
                }
            }

            return allSucceeded ? DragResult.Success : DragResult.Failed;
        }

        /// <summary>
        /// Calculate the 3D centroid of an edge's vertices.
        /// </summary>
        private Point3d CalculateCentroid(Edge edge)
        {
            var sum = Point3d.Origin;
            int count = 0;

            foreach (var vertex in edge.Vertices)
            {
                var pt = _evaluator.EvaluatePoint(
                    vertex.Position.FaceId,
                    vertex.Position.U,
                    vertex.Position.V);
                sum += pt;
                count++;
            }

            if (count == 0)
                return Point3d.Origin;

            return sum / count;
        }
    }

    /// <summary>
    /// Event args for edge drag operations.
    /// </summary>
    public class EdgeDragEventArgs : EventArgs
    {
        public Edge Edge { get; }
        public IReadOnlyList<ParametricPoint> VertexPositions { get; }

        public EdgeDragEventArgs(Edge edge, IReadOnlyList<ParametricPoint> positions)
        {
            Edge = edge;
            VertexPositions = positions;
        }
    }
}
```

### 4. Create Unit Tests

**NOTE**: All tests use `Latent.Interop.ParametricPoint`. Edge constructor takes `List<string>` (vertex IDs), and vertices are populated by RegionManager.

```csharp
// rhino_plugin/Tests/DragHandlerTests.cs
using System;
using System.Collections.Generic;
using NUnit.Framework;
using Rhino.Geometry;
using Latent.Interaction;
using Latent.Geometry;
using Latent.Interop;

namespace Latent.Tests
{
    [TestFixture]
    public class DragPreviewTests
    {
        [Test]
        public void Constructor_WithNullEvaluator_ThrowsArgumentNull()
        {
            Assert.Throws<ArgumentNullException>(() => new DragPreview(null));
        }

        [Test]
        public void DefaultSettings_HaveReasonableValues()
        {
            var evaluator = new SubDEvaluator();
            var preview = new DragPreview(evaluator);

            Assert.That(preview.PreviewPointSize, Is.GreaterThan(0));
            Assert.That(preview.PreviewLineThickness, Is.GreaterThan(0));
            Assert.That(preview.ShowDisplacementLines, Is.True);
        }
    }

    [TestFixture]
    public class VertexDragHandlerTests
    {
        [Test]
        public void Constructor_WithNullRegionManager_ThrowsArgumentNull()
        {
            var evaluator = new SubDEvaluator();
            var subd = CreateTestSubD();

            Assert.Throws<ArgumentNullException>(() =>
                new VertexDragHandler(null, evaluator, subd));
        }

        [Test]
        public void Constructor_WithNullEvaluator_ThrowsArgumentNull()
        {
            var manager = new RegionManager();
            var subd = CreateTestSubD();

            Assert.Throws<ArgumentNullException>(() =>
                new VertexDragHandler(manager, null, subd));
        }

        [Test]
        public void Constructor_WithNullSubD_ThrowsArgumentNull()
        {
            var manager = new RegionManager();
            var evaluator = new SubDEvaluator();

            Assert.Throws<ArgumentNullException>(() =>
                new VertexDragHandler(manager, evaluator, null));
        }

        [Test]
        public void StartDrag_WithNullVertex_ThrowsArgumentNull()
        {
            var handler = CreateHandler();
            Assert.Throws<ArgumentNullException>(() => handler.StartDrag(null));
        }

        [Test]
        public void ApplyDrag_WithNullVertex_ThrowsArgumentNull()
        {
            var handler = CreateHandler();
            Assert.Throws<ArgumentNullException>(() =>
                handler.ApplyDrag(null, Point3d.Origin));
        }

        [Test]
        public void ApplyDrag_WithPinnedVertex_ReturnsPinned()
        {
            var handler = CreateHandler();
            // Use Latent.Interop.ParametricPoint
            var vertex = new Vertex("v1", new ParametricPoint(0, 0.5, 0.5))
            {
                IsPinned = true
            };

            var result = handler.ApplyDrag(vertex, Point3d.Origin);
            Assert.That(result, Is.EqualTo(DragResult.Pinned));
        }

        private VertexDragHandler CreateHandler()
        {
            var manager = new RegionManager();
            var evaluator = new SubDEvaluator();
            var subd = CreateTestSubD();
            return new VertexDragHandler(manager, evaluator, subd);
        }

        private SubD CreateTestSubD()
        {
            var mesh = Mesh.CreateFromBox(
                new BoundingBox(Point3d.Origin, new Point3d(1, 1, 1)),
                1, 1, 1);
            return SubD.CreateFromMesh(mesh, SubDCreationOptions.FromNgons);
        }
    }

    [TestFixture]
    public class EdgeDragHandlerTests
    {
        [Test]
        public void Constructor_WithNullRegionManager_ThrowsArgumentNull()
        {
            var evaluator = new SubDEvaluator();
            var subd = CreateTestSubD();

            Assert.Throws<ArgumentNullException>(() =>
                new EdgeDragHandler(null, evaluator, subd));
        }

        [Test]
        public void Constructor_WithNullEvaluator_ThrowsArgumentNull()
        {
            var manager = new RegionManager();
            var subd = CreateTestSubD();

            Assert.Throws<ArgumentNullException>(() =>
                new EdgeDragHandler(manager, null, subd));
        }

        [Test]
        public void Constructor_WithNullSubD_ThrowsArgumentNull()
        {
            var manager = new RegionManager();
            var evaluator = new SubDEvaluator();

            Assert.Throws<ArgumentNullException>(() =>
                new EdgeDragHandler(manager, evaluator, null));
        }

        [Test]
        public void StartDrag_WithNullEdge_ThrowsArgumentNull()
        {
            var handler = CreateHandler();
            Assert.Throws<ArgumentNullException>(() => handler.StartDrag(null));
        }

        [Test]
        public void ApplyDrag_WithNullEdge_ThrowsArgumentNull()
        {
            var handler = CreateHandler();
            Assert.Throws<ArgumentNullException>(() =>
                handler.ApplyDrag(null, Vector3d.Zero));
        }

        [Test]
        public void ApplyDrag_WithPinnedEdge_ReturnsPinned()
        {
            var handler = CreateHandler();
            // Edge constructor takes List<string> (vertex IDs)
            // Vertices list is populated separately by RegionManager
            var edge = new Edge("e1", new List<string> { "v1", "v2" })
            {
                IsPinned = true
            };

            var result = handler.ApplyDrag(edge, Vector3d.Zero);
            Assert.That(result, Is.EqualTo(DragResult.Pinned));
        }

        private EdgeDragHandler CreateHandler()
        {
            var manager = new RegionManager();
            var evaluator = new SubDEvaluator();
            var subd = CreateTestSubD();
            return new EdgeDragHandler(manager, evaluator, subd);
        }

        private SubD CreateTestSubD()
        {
            var mesh = Mesh.CreateFromBox(
                new BoundingBox(Point3d.Origin, new Point3d(1, 1, 1)),
                1, 1, 1);
            return SubD.CreateFromMesh(mesh, SubDCreationOptions.FromNgons);
        }
    }

    [TestFixture]
    public class DragResultTests
    {
        [Test]
        public void DragResult_HasExpectedValues()
        {
            Assert.That(Enum.IsDefined(typeof(DragResult), DragResult.Success), Is.True);
            Assert.That(Enum.IsDefined(typeof(DragResult), DragResult.Canceled), Is.True);
            Assert.That(Enum.IsDefined(typeof(DragResult), DragResult.Failed), Is.True);
            Assert.That(Enum.IsDefined(typeof(DragResult), DragResult.Pinned), Is.True);
        }
    }

    [TestFixture]
    public class VertexDragEventArgsTests
    {
        [Test]
        public void Constructor_SetsProperties()
        {
            // Use Latent.Interop.ParametricPoint
            var vertex = new Vertex("v1", new ParametricPoint(0, 0.5, 0.5));
            var position = new ParametricPoint(0, 0.6, 0.6);

            var args = new VertexDragEventArgs(vertex, position);

            Assert.That(args.Vertex, Is.SameAs(vertex));
            Assert.That(args.Position.FaceId, Is.EqualTo(position.FaceId));
        }
    }

    [TestFixture]
    public class EdgeDragEventArgsTests
    {
        [Test]
        public void Constructor_SetsProperties()
        {
            // Edge constructor takes List<string> (vertex IDs)
            var edge = new Edge("e1", new List<string> { "v1", "v2" });
            var positions = new List<ParametricPoint>
            {
                new ParametricPoint(0, 0.1, 0.1),
                new ParametricPoint(0, 1.1, 0.1)
            };

            var args = new EdgeDragEventArgs(edge, positions);

            Assert.That(args.Edge, Is.SameAs(edge));
            Assert.That(args.VertexPositions.Count, Is.EqualTo(positions.Count));
        }
    }
}
```

## Success Criteria

- [ ] `DragPreview` shows vertex position preview during drag
- [ ] `DragPreview` shows displacement line from original to new position
- [ ] `VertexDragHandler.StartDrag()` constrains to surface
- [ ] `VertexDragHandler` prevents dragging pinned vertices
- [ ] `VertexDragHandler` creates undo record via RegionManager
- [ ] `EdgeDragHandler.StartDrag()` moves all vertices together
- [ ] `EdgeDragHandler` shows preview for entire edge
- [ ] `EdgeDragHandler` prevents dragging when any vertex is pinned
- [ ] Events fire correctly (DragStarted, DragCompleted, DragCanceled)
- [ ] All unit tests pass

## Verification Commands

```bash
cd /Users/NickDuch/Desktop/Ind Designs/NDAAD/RhinoProjects/Latent/rhino_plugin
dotnet build
dotnet test --filter "FullyQualifiedName~DragHandlerTests|FullyQualifiedName~DragPreviewTests|FullyQualifiedName~DragResultTests|FullyQualifiedName~VertexDragEventArgsTests|FullyQualifiedName~EdgeDragEventArgsTests"
```

## Do Not Modify

- Files in `Geometry/` (Phase 3 domain)
- Files in `Interop/` (Phase 3 domain)
- Files in `Display/` (Phase 4 domain)
- `SurfaceConstrainedGetPoint.cs` (Agent 5A's domain)
- `RegionPicker.cs` (Agent 5C's domain)

## Skills to Use

- `superpowers:test-driven-development` - write tests first
- `superpowers:verification-before-completion` - run tests before reporting

## Notes

- DynamicDraw event is key for visual feedback during interaction
- RegionManager.MoveVertex should handle undo internally
- Displacement is applied in 3D then projected back to surface
- Edge drag applies same displacement to all vertices
- Must check both edge and vertex pinned status

## Report

When complete, provide:
1. Test output showing all tests pass
2. Build output showing no errors
3. Notes on projection accuracy during drag
4. Any edge cases for vertices at face boundaries
