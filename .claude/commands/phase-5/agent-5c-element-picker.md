# Agent 5C: Region & Element Picking

## Objective

Implement picking for regions (point-in-region), edges (proximity), and vertices (proximity) with mode-based selection.

## Working Directory

`/Users/NickDuch/Desktop/Ind Designs/NDAAD/RhinoProjects/Latent`

## Read First

- `docs/plans/2025-12-04-rhino-plugin-implementation-plan.md` - picker examples
- `rhino_plugin/Geometry/RegionManager.cs` - FindRegionContaining method
- `rhino_plugin/Geometry/Region.cs` - region with boundary edges
- `rhino_plugin/Geometry/Edge.cs` - edge with vertices
- `rhino_plugin/Geometry/Vertex.cs` - vertex with position

## Dependencies

**From Phase 3:**
- `RegionManager` - provides collections and search methods
- `Region` - provides `BoundaryEdges`, `Contains()` method
- `Edge` - provides `Vertices`
- `Vertex` - provides `Position`
- `SubDEvaluator` - provides `ProjectPoint()`, `EvaluatePoint()`

**From This Phase:**
- `SurfaceConstrainedGetPoint` (Agent 5A) - surface picking

**IMPORTANT**: Use `Latent.Interop.ParametricPoint` from Phase 3. Do NOT create a duplicate struct.

**RhinoCommon:**
- `Rhino.Geometry.SubD` - the surface
- `Rhino.Input.Custom.GetPoint` - point picking

## Files to Create

1. `rhino_plugin/Interaction/PickResult.cs` - unified pick result
2. `rhino_plugin/Interaction/ElementPicker.cs` - proximity-based picking
3. `rhino_plugin/Interaction/RegionPicker.cs` - point-in-region picking
4. `rhino_plugin/Tests/PickerTests.cs` - unit tests

## Tasks

### 1. Create PickResult.cs

```csharp
// rhino_plugin/Interaction/PickResult.cs
using System;
using Rhino.Geometry;
using Latent.Geometry;
using Latent.Interop;

namespace Latent.Interaction
{
    /// <summary>
    /// Type of element that was picked.
    /// </summary>
    public enum PickType
    {
        None,
        Vertex,
        Edge,
        Region
    }

    /// <summary>
    /// Result from a pick operation.
    /// Uses Latent.Interop.ParametricPoint throughout.
    /// </summary>
    public class PickResult
    {
        /// <summary>
        /// Type of element picked.
        /// </summary>
        public PickType Type { get; }

        /// <summary>
        /// The picked vertex (if Type == Vertex).
        /// </summary>
        public Vertex Vertex { get; }

        /// <summary>
        /// The picked edge (if Type == Edge).
        /// </summary>
        public Edge Edge { get; }

        /// <summary>
        /// The picked region (if Type == Region).
        /// </summary>
        public Region Region { get; }

        /// <summary>
        /// The parametric pick point on the surface (Latent.Interop.ParametricPoint).
        /// </summary>
        public ParametricPoint PickPoint { get; }

        /// <summary>
        /// The 3D pick point.
        /// </summary>
        public Point3d PickPoint3d { get; }

        /// <summary>
        /// Distance to the picked element (for proximity picks).
        /// </summary>
        public double Distance { get; }

        /// <summary>
        /// Whether the pick was successful.
        /// </summary>
        public bool Success => Type != PickType.None;

        /// <summary>
        /// No pick result.
        /// </summary>
        public static PickResult Empty => new PickResult();

        private PickResult()
        {
            Type = PickType.None;
            PickPoint = ParametricPoint.Unset;
            PickPoint3d = Point3d.Unset;
            Distance = double.MaxValue;
        }

        /// <summary>
        /// Create a vertex pick result.
        /// </summary>
        public static PickResult ForVertex(Vertex vertex, ParametricPoint pickPoint, Point3d pickPoint3d, double distance)
        {
            return new PickResult(PickType.Vertex, vertex, null, null, pickPoint, pickPoint3d, distance);
        }

        /// <summary>
        /// Create an edge pick result.
        /// </summary>
        public static PickResult ForEdge(Edge edge, ParametricPoint pickPoint, Point3d pickPoint3d, double distance)
        {
            return new PickResult(PickType.Edge, null, edge, null, pickPoint, pickPoint3d, distance);
        }

        /// <summary>
        /// Create a region pick result.
        /// </summary>
        public static PickResult ForRegion(Region region, ParametricPoint pickPoint, Point3d pickPoint3d)
        {
            return new PickResult(PickType.Region, null, null, region, pickPoint, pickPoint3d, 0);
        }

        private PickResult(
            PickType type,
            Vertex vertex,
            Edge edge,
            Region region,
            ParametricPoint pickPoint,
            Point3d pickPoint3d,
            double distance)
        {
            Type = type;
            Vertex = vertex;
            Edge = edge;
            Region = region;
            PickPoint = pickPoint;
            PickPoint3d = pickPoint3d;
            Distance = distance;
        }

        public override string ToString()
        {
            return Type switch
            {
                PickType.Vertex => $"Vertex: {Vertex?.Id} (dist: {Distance:F4})",
                PickType.Edge => $"Edge: {Edge?.Id} (dist: {Distance:F4})",
                PickType.Region => $"Region: {Region?.Id}",
                _ => "None"
            };
        }
    }
}
```

### 2. Create ElementPicker.cs

```csharp
// rhino_plugin/Interaction/ElementPicker.cs
using System;
using System.Collections.Generic;
using Rhino.Geometry;
using Latent.Geometry;
using Latent.Interop;

namespace Latent.Interaction
{
    /// <summary>
    /// Picking mode determines what can be selected.
    /// </summary>
    [Flags]
    public enum PickMode
    {
        None = 0,
        Vertices = 1,
        Edges = 2,
        Regions = 4,
        All = Vertices | Edges | Regions
    }

    /// <summary>
    /// Configuration for element picking.
    /// </summary>
    public class PickSettings
    {
        /// <summary>
        /// Maximum distance (in model units) to pick vertices.
        /// </summary>
        public double VertexTolerance { get; set; } = 0.1;

        /// <summary>
        /// Maximum distance (in model units) to pick edges.
        /// </summary>
        public double EdgeTolerance { get; set; } = 0.05;

        /// <summary>
        /// What types of elements can be picked.
        /// </summary>
        public PickMode Mode { get; set; } = PickMode.All;

        /// <summary>
        /// Whether to prefer smaller elements (vertex over edge over region).
        /// </summary>
        public bool PreferSmaller { get; set; } = true;
    }

    /// <summary>
    /// Picks elements based on proximity to a point.
    /// </summary>
    public class ElementPicker
    {
        private readonly RegionManager _regionManager;
        private readonly SubDEvaluator _evaluator;
        private readonly PickSettings _settings;

        public ElementPicker(RegionManager regionManager, SubDEvaluator evaluator)
            : this(regionManager, evaluator, new PickSettings())
        {
        }

        public ElementPicker(RegionManager regionManager, SubDEvaluator evaluator, PickSettings settings)
        {
            _regionManager = regionManager ?? throw new ArgumentNullException(nameof(regionManager));
            _evaluator = evaluator ?? throw new ArgumentNullException(nameof(evaluator));
            _settings = settings ?? throw new ArgumentNullException(nameof(settings));
        }

        /// <summary>
        /// Pick the nearest element to a 3D point.
        /// </summary>
        public PickResult PickAtPoint(Point3d point3d)
        {
            // Project to surface
            if (!_evaluator.ProjectPoint(point3d, out int faceId, out float u, out float v))
            {
                return PickResult.Empty;
            }

            var param = new ParametricPoint(faceId, u, v);
            var surfacePoint = _evaluator.EvaluatePoint(faceId, u, v);

            return PickAtPoint(param, surfacePoint);
        }

        /// <summary>
        /// Pick the nearest element to a parametric point.
        /// </summary>
        public PickResult PickAtPoint(ParametricPoint param)
        {
            if (!param.IsValid)
                return PickResult.Empty;

            var point3d = _evaluator.EvaluatePoint(param.FaceId, (float)param.U, (float)param.V);
            return PickAtPoint(param, point3d);
        }

        /// <summary>
        /// Pick the nearest element given both parametric and 3D points.
        /// </summary>
        public PickResult PickAtPoint(ParametricPoint param, Point3d point3d)
        {
            if (!param.IsValid)
                return PickResult.Empty;

            PickResult vertexResult = null;
            PickResult edgeResult = null;
            PickResult regionResult = null;

            // Try vertex picking
            if (_settings.Mode.HasFlag(PickMode.Vertices))
            {
                vertexResult = FindNearestVertex(param, point3d);
            }

            // Try edge picking
            if (_settings.Mode.HasFlag(PickMode.Edges))
            {
                edgeResult = FindNearestEdge(param, point3d);
            }

            // Try region picking
            if (_settings.Mode.HasFlag(PickMode.Regions))
            {
                regionResult = FindContainingRegion(param, point3d);
            }

            // Determine best result based on preference
            return SelectBestResult(vertexResult, edgeResult, regionResult);
        }

        /// <summary>
        /// Find the nearest vertex within tolerance.
        /// </summary>
        private PickResult FindNearestVertex(ParametricPoint param, Point3d point3d)
        {
            Vertex nearestVertex = null;
            double nearestDist = _settings.VertexTolerance;

            foreach (var vertex in _regionManager.Vertices)
            {
                var vertexPos = _evaluator.EvaluatePoint(
                    vertex.Position.FaceId,
                    vertex.Position.U,
                    vertex.Position.V);

                double dist = point3d.DistanceTo(vertexPos);
                if (dist < nearestDist)
                {
                    nearestDist = dist;
                    nearestVertex = vertex;
                }
            }

            if (nearestVertex != null)
            {
                return PickResult.ForVertex(nearestVertex, param, point3d, nearestDist);
            }

            return null;
        }

        /// <summary>
        /// Find the nearest edge within tolerance.
        /// </summary>
        private PickResult FindNearestEdge(ParametricPoint param, Point3d point3d)
        {
            Edge nearestEdge = null;
            double nearestDist = _settings.EdgeTolerance;

            foreach (var edge in _regionManager.Edges)
            {
                double dist = DistanceToEdge(edge, point3d);
                if (dist < nearestDist)
                {
                    nearestDist = dist;
                    nearestEdge = edge;
                }
            }

            if (nearestEdge != null)
            {
                return PickResult.ForEdge(nearestEdge, param, point3d, nearestDist);
            }

            return null;
        }

        /// <summary>
        /// Find the region containing the point.
        /// </summary>
        private PickResult FindContainingRegion(ParametricPoint param, Point3d point3d)
        {
            // Use RegionManager's built-in search
            var region = _regionManager.FindRegionContaining(param.FaceId, (float)param.U, (float)param.V);

            if (region != null)
            {
                return PickResult.ForRegion(region, param, point3d);
            }

            return null;
        }

        /// <summary>
        /// Calculate distance from point to edge (approximated).
        /// </summary>
        private double DistanceToEdge(Edge edge, Point3d point3d)
        {
            if (edge.Vertices == null || edge.Vertices.Count < 2)
                return double.MaxValue;

            // Sample points along edge and find minimum distance
            double minDist = double.MaxValue;
            int numSamples = 10;

            var vertices = edge.Vertices;
            for (int i = 0; i < vertices.Count - 1; i++)
            {
                var p0 = _evaluator.EvaluatePoint(
                    vertices[i].Position.FaceId,
                    vertices[i].Position.U,
                    vertices[i].Position.V);
                var p1 = _evaluator.EvaluatePoint(
                    vertices[i + 1].Position.FaceId,
                    vertices[i + 1].Position.U,
                    vertices[i + 1].Position.V);

                // Check distance to line segment
                double dist = DistanceToLineSegment(point3d, p0, p1);
                minDist = Math.Min(minDist, dist);
            }

            return minDist;
        }

        /// <summary>
        /// Calculate distance from point to line segment.
        /// </summary>
        private double DistanceToLineSegment(Point3d point, Point3d lineStart, Point3d lineEnd)
        {
            var line = lineEnd - lineStart;
            double lengthSq = line.SquareLength;

            if (lengthSq < 1e-10)
            {
                return point.DistanceTo(lineStart);
            }

            // Project point onto line
            double t = Math.Clamp(((point - lineStart) * line) / lengthSq, 0.0, 1.0);
            var projection = lineStart + t * line;

            return point.DistanceTo(projection);
        }

        /// <summary>
        /// Select the best result based on settings.
        /// </summary>
        private PickResult SelectBestResult(PickResult vertex, PickResult edge, PickResult region)
        {
            if (_settings.PreferSmaller)
            {
                // Prefer vertex over edge over region
                if (vertex != null && vertex.Success)
                    return vertex;
                if (edge != null && edge.Success)
                    return edge;
                if (region != null && region.Success)
                    return region;
            }
            else
            {
                // Return closest by distance
                var results = new List<PickResult>();
                if (vertex?.Success == true) results.Add(vertex);
                if (edge?.Success == true) results.Add(edge);
                if (region?.Success == true) results.Add(region);

                PickResult best = null;
                double bestDist = double.MaxValue;

                foreach (var r in results)
                {
                    if (r.Distance < bestDist)
                    {
                        bestDist = r.Distance;
                        best = r;
                    }
                }

                if (best != null)
                    return best;
            }

            return PickResult.Empty;
        }
    }
}
```

### 3. Create RegionPicker.cs

```csharp
// rhino_plugin/Interaction/RegionPicker.cs
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
    /// Interactive picker for selecting regions on the SubD surface.
    /// </summary>
    public class RegionPicker
    {
        private readonly RegionManager _regionManager;
        private readonly SubDEvaluator _evaluator;
        private readonly SubD _subd;
        private readonly ElementPicker _elementPicker;

        /// <summary>
        /// Color to highlight regions during hover.
        /// </summary>
        public Color HoverColor { get; set; } = Color.FromArgb(128, Color.Yellow);

        /// <summary>
        /// Whether to highlight regions on hover.
        /// </summary>
        public bool HighlightOnHover { get; set; } = true;

        public RegionPicker(RegionManager regionManager, SubDEvaluator evaluator, SubD subd)
        {
            _regionManager = regionManager ?? throw new ArgumentNullException(nameof(regionManager));
            _evaluator = evaluator ?? throw new ArgumentNullException(nameof(evaluator));
            _subd = subd ?? throw new ArgumentNullException(nameof(subd));

            // Create element picker with region-only mode
            var settings = new PickSettings
            {
                Mode = PickMode.Regions
            };
            _elementPicker = new ElementPicker(regionManager, evaluator, settings);
        }

        /// <summary>
        /// Interactively pick a region.
        /// </summary>
        /// <returns>The picked region, or null if canceled</returns>
        public Region PickRegion()
        {
            return PickRegion("Pick point on region");
        }

        /// <summary>
        /// Interactively pick a region with custom prompt.
        /// </summary>
        public Region PickRegion(string prompt)
        {
            var gp = new SurfaceConstrainedGetPoint(_subd, _evaluator);
            gp.SetCommandPrompt(prompt);

            Region hoveredRegion = null;

            // Add hover highlighting
            if (HighlightOnHover)
            {
                gp.DynamicDraw += (sender, e) =>
                {
                    var param = gp.CurrentParametricPosition;
                    if (!param.IsValid) return;

                    // Find region at current point
                    var region = _regionManager.FindRegionContaining(
                        param.FaceId, (float)param.U, (float)param.V);

                    hoveredRegion = region;

                    if (region != null)
                    {
                        DrawRegionHighlight(e.Display, region);
                    }
                };
            }

            var result = gp.Get();

            if (result == GetResult.Point)
            {
                var param = gp.CurrentParametricPosition;
                if (param.IsValid)
                {
                    return _regionManager.FindRegionContaining(
                        param.FaceId, (float)param.U, (float)param.V);
                }
            }

            return null;
        }

        /// <summary>
        /// Interactively pick multiple regions.
        /// </summary>
        public Region[] PickMultipleRegions(string prompt = "Pick regions (Enter to finish)")
        {
            var selected = new System.Collections.Generic.List<Region>();

            while (true)
            {
                var gp = new SurfaceConstrainedGetPoint(_subd, _evaluator);
                gp.SetCommandPrompt($"{prompt} [{selected.Count} selected]");
                gp.AcceptNothing(true);

                Region hoveredRegion = null;

                if (HighlightOnHover)
                {
                    gp.DynamicDraw += (sender, e) =>
                    {
                        // Draw already selected regions
                        foreach (var r in selected)
                        {
                            DrawRegionHighlight(e.Display, r, Color.Green);
                        }

                        // Draw hovered region
                        var param = gp.CurrentParametricPosition;
                        if (param.IsValid)
                        {
                            var region = _regionManager.FindRegionContaining(
                                param.FaceId, (float)param.U, (float)param.V);

                            if (region != null && !selected.Contains(region))
                            {
                                hoveredRegion = region;
                                DrawRegionHighlight(e.Display, region, HoverColor);
                            }
                        }
                    };
                }

                var result = gp.Get();

                if (result == GetResult.Nothing)
                {
                    // User pressed Enter - done
                    break;
                }

                if (result == GetResult.Point)
                {
                    var param = gp.CurrentParametricPosition;
                    if (param.IsValid)
                    {
                        var region = _regionManager.FindRegionContaining(
                            param.FaceId, (float)param.U, (float)param.V);

                        if (region != null)
                        {
                            if (selected.Contains(region))
                            {
                                // Toggle off
                                selected.Remove(region);
                                RhinoApp.WriteLine($"Deselected region {region.Id}");
                            }
                            else
                            {
                                // Toggle on
                                selected.Add(region);
                                RhinoApp.WriteLine($"Selected region {region.Id}");
                            }
                        }
                    }
                }
                else
                {
                    // Cancel
                    break;
                }
            }

            return selected.ToArray();
        }

        /// <summary>
        /// Draw a highlight around a region's boundary.
        /// </summary>
        private void DrawRegionHighlight(DisplayPipeline display, Region region, Color? color = null)
        {
            var highlightColor = color ?? HoverColor;

            // Draw boundary edges with thick lines
            foreach (var edge in region.BoundaryEdges)
            {
                var points = new System.Collections.Generic.List<Point3d>();

                foreach (var vertex in edge.Vertices)
                {
                    var pt = _evaluator.EvaluatePoint(
                        vertex.Position.FaceId,
                        vertex.Position.U,
                        vertex.Position.V);
                    points.Add(pt);
                }

                if (points.Count >= 2)
                {
                    display.DrawPolyline(points, highlightColor, 3);
                }
            }
        }
    }

    /// <summary>
    /// Interactive picker for any element type.
    /// </summary>
    public class InteractiveElementPicker
    {
        private readonly RegionManager _regionManager;
        private readonly SubDEvaluator _evaluator;
        private readonly SubD _subd;
        private readonly ElementPicker _picker;
        private readonly PickSettings _settings;

        public InteractiveElementPicker(
            RegionManager regionManager,
            SubDEvaluator evaluator,
            SubD subd,
            PickSettings settings = null)
        {
            _regionManager = regionManager ?? throw new ArgumentNullException(nameof(regionManager));
            _evaluator = evaluator ?? throw new ArgumentNullException(nameof(evaluator));
            _subd = subd ?? throw new ArgumentNullException(nameof(subd));
            _settings = settings ?? new PickSettings();
            _picker = new ElementPicker(regionManager, evaluator, _settings);
        }

        /// <summary>
        /// Interactively pick an element.
        /// </summary>
        public PickResult Pick(string prompt = "Pick element")
        {
            var gp = new SurfaceConstrainedGetPoint(_subd, _evaluator);
            gp.SetCommandPrompt(prompt);

            PickResult currentResult = null;

            gp.DynamicDraw += (sender, e) =>
            {
                var param = gp.CurrentParametricPosition;
                if (!param.IsValid) return;

                var point3d = gp.CurrentSurfacePoint;
                currentResult = _picker.PickAtPoint(param, point3d);

                // Draw highlight based on pick type
                if (currentResult.Success)
                {
                    DrawPickHighlight(e.Display, currentResult);
                }
            };

            var result = gp.Get();

            if (result == GetResult.Point && currentResult?.Success == true)
            {
                return currentResult;
            }

            return PickResult.Empty;
        }

        private void DrawPickHighlight(DisplayPipeline display, PickResult result)
        {
            switch (result.Type)
            {
                case PickType.Vertex:
                    display.DrawPoint(result.PickPoint3d, PointStyle.RoundControlPoint, 10, Color.Yellow);
                    break;

                case PickType.Edge:
                    if (result.Edge != null)
                    {
                        var points = new System.Collections.Generic.List<Point3d>();
                        foreach (var v in result.Edge.Vertices)
                        {
                            points.Add(_evaluator.EvaluatePoint(v.Position.FaceId, v.Position.U, v.Position.V));
                        }
                        if (points.Count >= 2)
                        {
                            display.DrawPolyline(points, Color.Yellow, 3);
                        }
                    }
                    break;

                case PickType.Region:
                    if (result.Region != null)
                    {
                        foreach (var edge in result.Region.BoundaryEdges)
                        {
                            var points = new System.Collections.Generic.List<Point3d>();
                            foreach (var v in edge.Vertices)
                            {
                                points.Add(_evaluator.EvaluatePoint(v.Position.FaceId, v.Position.U, v.Position.V));
                            }
                            if (points.Count >= 2)
                            {
                                display.DrawPolyline(points, Color.FromArgb(128, Color.Yellow), 2);
                            }
                        }
                    }
                    break;
            }
        }
    }
}
```

### 4. Create Unit Tests

**NOTE**: All tests use `Latent.Interop.ParametricPoint`. Edge constructor takes `List<string>` (vertex IDs), and Region constructor takes `List<string>` (edge IDs).

```csharp
// rhino_plugin/Tests/PickerTests.cs
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
    public class PickResultTests
    {
        [Test]
        public void Empty_HasTypeNone()
        {
            Assert.That(PickResult.Empty.Type, Is.EqualTo(PickType.None));
        }

        [Test]
        public void Empty_IsNotSuccessful()
        {
            Assert.That(PickResult.Empty.Success, Is.False);
        }

        [Test]
        public void ForVertex_CreatesVertexResult()
        {
            // Use Latent.Interop.ParametricPoint
            var vertex = new Vertex("v1", new ParametricPoint(0, 0.5, 0.5));
            var param = new ParametricPoint(0, 0.5, 0.5);
            var point3d = new Point3d(1, 2, 3);

            var result = PickResult.ForVertex(vertex, param, point3d, 0.01);

            Assert.That(result.Type, Is.EqualTo(PickType.Vertex));
            Assert.That(result.Vertex, Is.SameAs(vertex));
            Assert.That(result.Success, Is.True);
            Assert.That(result.Distance, Is.EqualTo(0.01));
        }

        [Test]
        public void ForEdge_CreatesEdgeResult()
        {
            // Edge constructor takes List<string> (vertex IDs)
            var edge = new Edge("e1", new List<string> { "v1", "v2" });
            var param = new ParametricPoint(0, 0.5, 0.0);
            var point3d = new Point3d(1, 2, 3);

            var result = PickResult.ForEdge(edge, param, point3d, 0.02);

            Assert.That(result.Type, Is.EqualTo(PickType.Edge));
            Assert.That(result.Edge, Is.SameAs(edge));
            Assert.That(result.Success, Is.True);
        }

        [Test]
        public void ForRegion_CreatesRegionResult()
        {
            // Region constructor takes List<string> (edge IDs)
            var region = new Region("r1", new List<string>());
            var param = new ParametricPoint(0, 0.5, 0.5);
            var point3d = new Point3d(1, 2, 3);

            var result = PickResult.ForRegion(region, param, point3d);

            Assert.That(result.Type, Is.EqualTo(PickType.Region));
            Assert.That(result.Region, Is.SameAs(region));
            Assert.That(result.Success, Is.True);
            Assert.That(result.Distance, Is.EqualTo(0));  // Regions have 0 distance
        }

        [Test]
        public void ToString_ReturnsReadableFormat()
        {
            var vertex = new Vertex("v1", new ParametricPoint(0, 0.5, 0.5));
            var result = PickResult.ForVertex(vertex, new ParametricPoint(0, 0.5, 0.5), Point3d.Origin, 0.01);

            var str = result.ToString();
            Assert.That(str, Does.Contain("Vertex"));
            Assert.That(str, Does.Contain("v1"));
        }
    }

    [TestFixture]
    public class PickSettingsTests
    {
        [Test]
        public void DefaultSettings_HaveReasonableValues()
        {
            var settings = new PickSettings();

            Assert.That(settings.VertexTolerance, Is.GreaterThan(0));
            Assert.That(settings.EdgeTolerance, Is.GreaterThan(0));
            Assert.That(settings.Mode, Is.EqualTo(PickMode.All));
            Assert.That(settings.PreferSmaller, Is.True);
        }

        [Test]
        public void PickMode_FlagsWorkCorrectly()
        {
            var mode = PickMode.Vertices | PickMode.Edges;

            Assert.That(mode.HasFlag(PickMode.Vertices), Is.True);
            Assert.That(mode.HasFlag(PickMode.Edges), Is.True);
            Assert.That(mode.HasFlag(PickMode.Regions), Is.False);
        }

        [Test]
        public void PickMode_All_IncludesAllTypes()
        {
            Assert.That(PickMode.All.HasFlag(PickMode.Vertices), Is.True);
            Assert.That(PickMode.All.HasFlag(PickMode.Edges), Is.True);
            Assert.That(PickMode.All.HasFlag(PickMode.Regions), Is.True);
        }
    }

    [TestFixture]
    public class ElementPickerTests
    {
        [Test]
        public void Constructor_WithNullRegionManager_ThrowsArgumentNull()
        {
            var evaluator = new SubDEvaluator();
            Assert.Throws<ArgumentNullException>(() =>
                new ElementPicker(null, evaluator));
        }

        [Test]
        public void Constructor_WithNullEvaluator_ThrowsArgumentNull()
        {
            var manager = new RegionManager();
            Assert.Throws<ArgumentNullException>(() =>
                new ElementPicker(manager, null));
        }

        [Test]
        public void PickAtPoint_WithInvalidParam_ReturnsEmpty()
        {
            var manager = new RegionManager();
            var evaluator = new SubDEvaluator();
            var picker = new ElementPicker(manager, evaluator);

            // Create invalid ParametricPoint
            var invalidParam = ParametricPoint.Unset;
            var result = picker.PickAtPoint(invalidParam);

            Assert.That(result.Success, Is.False);
        }
    }

    [TestFixture]
    public class RegionPickerTests
    {
        [Test]
        public void Constructor_WithNullRegionManager_ThrowsArgumentNull()
        {
            var evaluator = new SubDEvaluator();
            var subd = CreateTestSubD();

            Assert.Throws<ArgumentNullException>(() =>
                new RegionPicker(null, evaluator, subd));
        }

        [Test]
        public void Constructor_WithNullEvaluator_ThrowsArgumentNull()
        {
            var manager = new RegionManager();
            var subd = CreateTestSubD();

            Assert.Throws<ArgumentNullException>(() =>
                new RegionPicker(manager, null, subd));
        }

        [Test]
        public void Constructor_WithNullSubD_ThrowsArgumentNull()
        {
            var manager = new RegionManager();
            var evaluator = new SubDEvaluator();

            Assert.Throws<ArgumentNullException>(() =>
                new RegionPicker(manager, evaluator, null));
        }

        [Test]
        public void DefaultSettings_HighlightOnHoverIsTrue()
        {
            var picker = CreatePicker();
            Assert.That(picker.HighlightOnHover, Is.True);
        }

        private RegionPicker CreatePicker()
        {
            var manager = new RegionManager();
            var evaluator = new SubDEvaluator();
            var subd = CreateTestSubD();
            return new RegionPicker(manager, evaluator, subd);
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
    public class InteractiveElementPickerTests
    {
        [Test]
        public void Constructor_WithNullRegionManager_ThrowsArgumentNull()
        {
            var evaluator = new SubDEvaluator();
            var subd = CreateTestSubD();

            Assert.Throws<ArgumentNullException>(() =>
                new InteractiveElementPicker(null, evaluator, subd));
        }

        [Test]
        public void Constructor_WithNullEvaluator_ThrowsArgumentNull()
        {
            var manager = new RegionManager();
            var subd = CreateTestSubD();

            Assert.Throws<ArgumentNullException>(() =>
                new InteractiveElementPicker(manager, null, subd));
        }

        [Test]
        public void Constructor_WithNullSubD_ThrowsArgumentNull()
        {
            var manager = new RegionManager();
            var evaluator = new SubDEvaluator();

            Assert.Throws<ArgumentNullException>(() =>
                new InteractiveElementPicker(manager, evaluator, null));
        }

        private SubD CreateTestSubD()
        {
            var mesh = Mesh.CreateFromBox(
                new BoundingBox(Point3d.Origin, new Point3d(1, 1, 1)),
                1, 1, 1);
            return SubD.CreateFromMesh(mesh, SubDCreationOptions.FromNgons);
        }
    }
}
```

## Success Criteria

- [ ] `PickResult` properly represents vertex, edge, and region picks
- [ ] `ElementPicker` finds nearest vertex within tolerance
- [ ] `ElementPicker` finds nearest edge within tolerance
- [ ] `ElementPicker` finds containing region
- [ ] `ElementPicker` respects `PickMode` settings
- [ ] `ElementPicker.PreferSmaller` prioritizes vertex > edge > region
- [ ] `RegionPicker` interactively picks regions
- [ ] `RegionPicker` highlights regions on hover
- [ ] `RegionPicker.PickMultipleRegions` supports toggle selection
- [ ] `InteractiveElementPicker` handles all element types
- [ ] All unit tests pass

## Verification Commands

```bash
cd /Users/NickDuch/Desktop/Ind Designs/NDAAD/RhinoProjects/Latent/rhino_plugin
dotnet build
dotnet test --filter "FullyQualifiedName~PickerTests|FullyQualifiedName~PickResultTests|FullyQualifiedName~PickSettingsTests"
```

## Do Not Modify

- Files in `Geometry/` (Phase 3 domain)
- Files in `Interop/` (Phase 3 domain)
- Files in `Display/` (Phase 4 domain)
- `SurfaceConstrainedGetPoint.cs` (Agent 5A's domain)
- `VertexDragHandler.cs` (Agent 5B's domain)

## Skills to Use

- `superpowers:test-driven-development` - write tests first
- `superpowers:verification-before-completion` - run tests before reporting

## Notes

- Proximity picking uses 3D distance, not parametric distance
- Edge distance is approximated using line segments
- Point-in-region test uses RegionManager.FindRegionContaining
- PreferSmaller helps avoid accidentally selecting regions when clicking vertices
- DynamicDraw provides hover feedback

## Report

When complete, provide:
1. Test output showing all tests pass
2. Build output showing no errors
3. Notes on proximity tolerance tuning
4. Any edge cases for overlapping elements
