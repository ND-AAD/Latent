# Agent 4C: Region Fill & Centroid Markers

## Objective

Implement transparent region fills and centroid marker rendering for visual region identification.

## Working Directory

`/Users/NickDuch/Desktop/Ind Designs/NDAAD/RhinoProjects/Latent`

## Read First

- `docs/plans/2025-12-04-rhino-plugin-implementation-plan.md` - fill rendering examples
- `rhino_plugin/Geometry/Region.cs` - region class with BoundaryEdges, Centroid
- `rhino_plugin/Display/CurveSampler.cs` - curve sampling (Agent 4B)

## Dependencies

**From Phase 3:**
- `Region` - provides `BoundaryEdges`, `Centroid`, `BoundingBox`, `Id`
- `Edge` - provides boundary curve data
- `Vertex` - provides endpoint positions
- `SubDEvaluator` - provides `EvaluatePoint(faceId, u, v)`

**From This Phase:**
- `CurveSampler` (Agent 4B) - samples curves to polylines for fill boundary

## Files to Create

1. `rhino_plugin/Display/RegionFill.cs` - region fill rendering
2. `rhino_plugin/Display/CentroidMarker.cs` - centroid marker rendering
3. `rhino_plugin/Tests/RegionFillTests.cs` - unit tests

## Tasks

### 1. Create RegionFill.cs

```csharp
// rhino_plugin/Display/RegionFill.cs
using System;
using System.Collections.Generic;
using System.Drawing;
using Rhino.Geometry;
using Latent.Geometry;
using Latent.Interop;

namespace Latent.Display
{
    /// <summary>
    /// Creates mesh fills for regions to render with transparency.
    /// </summary>
    public class RegionFill
    {
        private readonly CurveSampler _sampler;
        private readonly Dictionary<string, FillCache> _fillCache;
        private readonly object _lock = new object();

        public RegionFill(CurveSampler sampler)
        {
            _sampler = sampler ?? throw new ArgumentNullException(nameof(sampler));
            _fillCache = new Dictionary<string, FillCache>();
        }

        /// <summary>
        /// Get a mesh for filling a region.
        /// </summary>
        /// <param name="region">The region to fill</param>
        /// <param name="sampleCount">Samples per edge</param>
        /// <returns>Mesh suitable for transparent rendering, or null if failed</returns>
        public Mesh GetFillMesh(Region region, int sampleCount = 50)
        {
            if (region == null)
                throw new ArgumentNullException(nameof(region));

            var key = GetCacheKey(region);

            lock (_lock)
            {
                if (_fillCache.TryGetValue(key, out var cached) &&
                    cached.Version == region.Version)
                {
                    return cached.Mesh;
                }
            }

            // Build mesh outside lock
            var mesh = BuildFillMesh(region, sampleCount);

            lock (_lock)
            {
                _fillCache[key] = new FillCache
                {
                    Mesh = mesh,
                    Version = region.Version
                };
            }

            return mesh;
        }

        /// <summary>
        /// Build a mesh from region boundary curves.
        /// </summary>
        private Mesh BuildFillMesh(Region region, int sampleCount)
        {
            // Collect all boundary points
            var boundaryPoints = new List<Point3d>();

            foreach (var edge in region.BoundaryEdges)
            {
                var edgePoints = _sampler.SampleEdge(edge, sampleCount);

                // Add points, avoiding duplicates at vertices
                for (int i = 0; i < edgePoints.Count; i++)
                {
                    // Skip last point if not last edge (will be first of next)
                    if (i == edgePoints.Count - 1 &&
                        region.BoundaryEdges.IndexOf(edge) < region.BoundaryEdges.Count - 1)
                    {
                        continue;
                    }

                    boundaryPoints.Add(edgePoints[i]);
                }
            }

            if (boundaryPoints.Count < 3)
            {
                return null;
            }

            // Create mesh using triangulation
            var mesh = CreateTriangulatedMesh(boundaryPoints, region);
            return mesh;
        }

        /// <summary>
        /// Create a triangulated mesh from boundary points.
        /// Uses fan triangulation from centroid for simple regions.
        /// </summary>
        private Mesh CreateTriangulatedMesh(List<Point3d> boundaryPoints, Region region)
        {
            var mesh = new Mesh();

            // Calculate centroid
            var centroid = CalculateCentroid3d(boundaryPoints);

            // Add centroid as first vertex
            mesh.Vertices.Add(centroid);

            // Add boundary points
            foreach (var pt in boundaryPoints)
            {
                mesh.Vertices.Add(pt);
            }

            // Create fan triangles from centroid to boundary
            int n = boundaryPoints.Count;
            for (int i = 0; i < n; i++)
            {
                int v1 = 1 + i;           // boundary vertex
                int v2 = 1 + (i + 1) % n; // next boundary vertex
                mesh.Faces.AddFace(0, v1, v2);
            }

            // Compute normals for proper rendering
            mesh.Normals.ComputeNormals();
            mesh.Compact();

            return mesh;
        }

        /// <summary>
        /// Calculate 3D centroid of boundary points.
        /// </summary>
        private Point3d CalculateCentroid3d(List<Point3d> points)
        {
            if (points == null || points.Count == 0)
                return Point3d.Origin;

            double x = 0, y = 0, z = 0;
            foreach (var pt in points)
            {
                x += pt.X;
                y += pt.Y;
                z += pt.Z;
            }

            int n = points.Count;
            return new Point3d(x / n, y / n, z / n);
        }

        /// <summary>
        /// Invalidate cache for a region.
        /// </summary>
        public void Invalidate(Region region)
        {
            if (region == null) return;

            var key = GetCacheKey(region);
            lock (_lock)
            {
                _fillCache.Remove(key);
            }
        }

        /// <summary>
        /// Clear all cached fills.
        /// </summary>
        public void Clear()
        {
            lock (_lock)
            {
                _fillCache.Clear();
            }
        }

        private string GetCacheKey(Region region)
        {
            return region.Id;
        }

        private class FillCache
        {
            public Mesh Mesh { get; set; }
            public int Version { get; set; }
        }
    }

    /// <summary>
    /// Extension methods for Region fill operations.
    /// </summary>
    public static class RegionFillExtensions
    {
        /// <summary>
        /// Get the computed 3D bounding box for display.
        /// </summary>
        public static BoundingBox GetDisplayBoundingBox(this Region region, SubDEvaluator evaluator)
        {
            if (region == null || evaluator == null)
                return BoundingBox.Empty;

            var bbox = BoundingBox.Empty;

            foreach (var edge in region.BoundaryEdges)
            {
                foreach (var vertex in edge.Vertices)
                {
                    var pos = vertex.Position;
                    var point = evaluator.EvaluatePoint(pos.FaceId, pos.U, pos.V);
                    bbox.Union(point);
                }
            }

            return bbox;
        }
    }
}
```

### 2. Create CentroidMarker.cs

```csharp
// rhino_plugin/Display/CentroidMarker.cs
using System;
using System.Collections.Generic;
using System.Drawing;
using Rhino.Geometry;
using Latent.Geometry;
using Latent.Interop;

namespace Latent.Display
{
    /// <summary>
    /// Computes and caches 3D centroid positions for region markers.
    /// </summary>
    public class CentroidMarker
    {
        private readonly SubDEvaluator _evaluator;
        private readonly Dictionary<string, CentroidCache> _cache;
        private readonly object _lock = new object();

        public CentroidMarker(SubDEvaluator evaluator)
        {
            _evaluator = evaluator ?? throw new ArgumentNullException(nameof(evaluator));
            _cache = new Dictionary<string, CentroidCache>();
        }

        /// <summary>
        /// Get the 3D centroid position for a region.
        /// </summary>
        /// <param name="region">The region</param>
        /// <returns>3D point at centroid, or null if cannot compute</returns>
        public Point3d? GetCentroid3d(Region region)
        {
            if (region == null)
                throw new ArgumentNullException(nameof(region));

            var key = region.Id;

            lock (_lock)
            {
                if (_cache.TryGetValue(key, out var cached) &&
                    cached.Version == region.Version)
                {
                    return cached.Centroid;
                }
            }

            // Compute centroid outside lock
            var centroid = ComputeCentroid3d(region);

            lock (_lock)
            {
                _cache[key] = new CentroidCache
                {
                    Centroid = centroid,
                    Version = region.Version
                };
            }

            return centroid;
        }

        /// <summary>
        /// Compute the 3D centroid from the parametric centroid.
        /// </summary>
        private Point3d? ComputeCentroid3d(Region region)
        {
            // Use region's parametric centroid if available
            var paramCentroid = region.Centroid;
            if (paramCentroid != null)
            {
                return _evaluator.EvaluatePoint(
                    paramCentroid.FaceId,
                    paramCentroid.U,
                    paramCentroid.V);
            }

            // Fallback: compute from boundary vertices
            return ComputeFromBoundary(region);
        }

        /// <summary>
        /// Compute centroid from boundary edge midpoints.
        /// </summary>
        private Point3d? ComputeFromBoundary(Region region)
        {
            var points = new List<Point3d>();

            foreach (var edge in region.BoundaryEdges)
            {
                foreach (var vertex in edge.Vertices)
                {
                    var pos = vertex.Position;
                    var pt = _evaluator.EvaluatePoint(pos.FaceId, pos.U, pos.V);
                    points.Add(pt);
                }
            }

            if (points.Count == 0)
                return null;

            // Average all points
            double x = 0, y = 0, z = 0;
            foreach (var pt in points)
            {
                x += pt.X;
                y += pt.Y;
                z += pt.Z;
            }

            int n = points.Count;
            return new Point3d(x / n, y / n, z / n);
        }

        /// <summary>
        /// Get centroid with offset along surface normal.
        /// Useful for markers that should float above the surface.
        /// </summary>
        /// <param name="region">The region</param>
        /// <param name="offset">Offset distance along normal</param>
        /// <returns>Offset centroid point</returns>
        public Point3d? GetCentroidWithOffset(Region region, double offset)
        {
            var centroid = GetCentroid3d(region);
            if (!centroid.HasValue)
                return null;

            var paramCentroid = region.Centroid;
            if (paramCentroid == null)
                return centroid;

            // Get surface normal at centroid
            var normal = _evaluator.GetNormal(
                paramCentroid.FaceId,
                paramCentroid.U,
                paramCentroid.V);

            if (normal.HasValue)
            {
                return centroid.Value + normal.Value * offset;
            }

            return centroid;
        }

        /// <summary>
        /// Invalidate cache for a region.
        /// </summary>
        public void Invalidate(Region region)
        {
            if (region == null) return;

            lock (_lock)
            {
                _cache.Remove(region.Id);
            }
        }

        /// <summary>
        /// Clear all cached centroids.
        /// </summary>
        public void Clear()
        {
            lock (_lock)
            {
                _cache.Clear();
            }
        }

        /// <summary>
        /// Get all cached centroid positions (for batch drawing).
        /// </summary>
        public IEnumerable<KeyValuePair<string, Point3d>> GetAllCentroids()
        {
            lock (_lock)
            {
                foreach (var kvp in _cache)
                {
                    if (kvp.Value.Centroid.HasValue)
                    {
                        yield return new KeyValuePair<string, Point3d>(
                            kvp.Key, kvp.Value.Centroid.Value);
                    }
                }
            }
        }

        private class CentroidCache
        {
            public Point3d? Centroid { get; set; }
            public int Version { get; set; }
        }
    }

    /// <summary>
    /// Marker style options for centroid display.
    /// </summary>
    public enum CentroidMarkerStyle
    {
        Dot,       // Simple dot with text
        Circle,    // Circle outline
        Diamond,   // Diamond shape
        Cross      // Cross/plus shape
    }

    /// <summary>
    /// Configuration for centroid marker appearance.
    /// </summary>
    public class CentroidMarkerSettings
    {
        public CentroidMarkerStyle Style { get; set; } = CentroidMarkerStyle.Dot;
        public Color TextColor { get; set; } = Color.Black;
        public Color BackgroundColor { get; set; } = Color.White;
        public Color BorderColor { get; set; } = Color.Gray;
        public int FontSize { get; set; } = 10;
        public bool ShowRegionId { get; set; } = true;
        public bool ShowRegionNumber { get; set; } = false;
        public double NormalOffset { get; set; } = 0.0;  // Offset above surface
    }
}
```

### 3. Create Unit Tests

```csharp
// rhino_plugin/Tests/RegionFillTests.cs
using System;
using System.Collections.Generic;
using NUnit.Framework;
using Rhino.Geometry;
using Latent.Display;
using Latent.Geometry;
using Latent.Interop;

namespace Latent.Tests
{
    [TestFixture]
    public class RegionFillTests
    {
        [Test]
        public void Constructor_WithNullSampler_ThrowsArgumentNull()
        {
            Assert.Throws<ArgumentNullException>(() => new RegionFill(null));
        }

        [Test]
        public void GetFillMesh_WithNullRegion_ThrowsArgumentNull()
        {
            var sampler = CreateMockSampler();
            var fill = new RegionFill(sampler);

            Assert.Throws<ArgumentNullException>(() => fill.GetFillMesh(null));
        }

        [Test]
        public void Clear_DoesNotThrow()
        {
            var sampler = CreateMockSampler();
            var fill = new RegionFill(sampler);

            Assert.DoesNotThrow(() => fill.Clear());
        }

        [Test]
        public void Invalidate_WithNullRegion_DoesNotThrow()
        {
            var sampler = CreateMockSampler();
            var fill = new RegionFill(sampler);

            Assert.DoesNotThrow(() => fill.Invalidate(null));
        }

        private CurveSampler CreateMockSampler()
        {
            // Would need proper mocking in production
            return new CurveSampler(new SubDEvaluator());
        }
    }

    [TestFixture]
    public class CentroidMarkerTests
    {
        [Test]
        public void Constructor_WithNullEvaluator_ThrowsArgumentNull()
        {
            Assert.Throws<ArgumentNullException>(() => new CentroidMarker(null));
        }

        [Test]
        public void GetCentroid3d_WithNullRegion_ThrowsArgumentNull()
        {
            var evaluator = new SubDEvaluator();
            var marker = new CentroidMarker(evaluator);

            Assert.Throws<ArgumentNullException>(() => marker.GetCentroid3d(null));
        }

        [Test]
        public void Clear_DoesNotThrow()
        {
            var evaluator = new SubDEvaluator();
            var marker = new CentroidMarker(evaluator);

            Assert.DoesNotThrow(() => marker.Clear());
        }

        [Test]
        public void Invalidate_WithNullRegion_DoesNotThrow()
        {
            var evaluator = new SubDEvaluator();
            var marker = new CentroidMarker(evaluator);

            Assert.DoesNotThrow(() => marker.Invalidate(null));
        }

        [Test]
        public void GetAllCentroids_InitiallyEmpty()
        {
            var evaluator = new SubDEvaluator();
            var marker = new CentroidMarker(evaluator);

            var centroids = new List<KeyValuePair<string, Point3d>>(marker.GetAllCentroids());
            Assert.That(centroids, Is.Empty);
        }
    }

    [TestFixture]
    public class CentroidMarkerSettingsTests
    {
        [Test]
        public void DefaultSettings_HaveReasonableValues()
        {
            var settings = new CentroidMarkerSettings();

            Assert.That(settings.Style, Is.EqualTo(CentroidMarkerStyle.Dot));
            Assert.That(settings.FontSize, Is.GreaterThan(0));
            Assert.That(settings.ShowRegionId, Is.True);
        }
    }
}
```

## Success Criteria

- [ ] `RegionFill` creates mesh from boundary curves
- [ ] Fill mesh uses fan triangulation from centroid
- [ ] `CentroidMarker` computes 3D centroid from parametric centroid
- [ ] Fallback centroid calculation from boundary points works
- [ ] Cache invalidation works per-region
- [ ] Thread-safe cache operations
- [ ] Mesh normals computed correctly for rendering
- [ ] All unit tests pass

## Verification Commands

```bash
cd /Users/NickDuch/Desktop/Ind Designs/NDAAD/RhinoProjects/Latent/rhino_plugin
dotnet build
dotnet test --filter "FullyQualifiedName~RegionFillTests|FullyQualifiedName~CentroidMarkerTests"
```

## Do Not Modify

- Files in `Geometry/` (Phase 3 domain)
- Files in `Interop/` (Phase 3 domain)
- `RegionConduit.cs` (Agent 4A's domain)
- `CurveSampler.cs` (Agent 4B's domain)
- `CurveCache.cs` (Agent 4B's domain)

## Skills to Use

- `superpowers:test-driven-development` - write tests first
- `superpowers:verification-before-completion` - run tests before reporting

## Notes

- Fan triangulation works well for convex regions
- Complex/concave regions may need more sophisticated triangulation
- Centroid offset along normal helps visibility when overlapping
- Version tracking enables efficient cache invalidation
- Consider level-of-detail for regions with many edges

## Report

When complete, provide:
1. Test output showing all tests pass
2. Build output showing no errors
3. Notes on triangulation approach and limitations
4. Performance observations for mesh generation
