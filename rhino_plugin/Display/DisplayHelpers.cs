// rhino_plugin/Display/DisplayHelpers.cs
// Display helper classes - RegionFill and CentroidMarker implementations by Agent 4C
// CurveSampler implemented by Agent 4B, CurveCache already complete

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
        public Mesh GetFillMesh(Latent.Geometry.Region region, int sampleCount = 50)
        {
            if (region == null)
                throw new ArgumentNullException(nameof(region));

            var key = GetCacheKey(region);

            // Check cache (using hash of boundary edges as version proxy)
            lock (_lock)
            {
                if (_fillCache.TryGetValue(key, out var cached) &&
                    cached.BoundaryHash == GetBoundaryHash(region))
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
                    BoundaryHash = GetBoundaryHash(region)
                };
            }

            return mesh;
        }

        /// <summary>
        /// Build a mesh from region boundary curves.
        /// </summary>
        private Mesh BuildFillMesh(Latent.Geometry.Region region, int sampleCount)
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
        private Mesh CreateTriangulatedMesh(List<Point3d> boundaryPoints, Latent.Geometry.Region region)
        {
            var mesh = new Mesh();

            // Use region centroid if available, otherwise compute from boundary
            var centroid = region.Centroid;
            if (!centroid.IsValid || centroid == Point3d.Origin)
            {
                centroid = CalculateCentroid3d(boundaryPoints);
            }

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
        /// Get a hash of the boundary to detect changes.
        /// </summary>
        private int GetBoundaryHash(Latent.Geometry.Region region)
        {
            unchecked
            {
                int hash = 17;
                foreach (var edge in region.BoundaryEdges)
                {
                    hash = hash * 31 + edge.Id.GetHashCode();
                    hash = hash * 31 + edge.CurveType.GetHashCode();
                    hash = hash * 31 + edge.Degree.GetHashCode();
                    hash = hash * 31 + edge.Version;
                }
                return hash;
            }
        }

        /// <summary>
        /// Invalidate cache for a region.
        /// </summary>
        public void Invalidate(Latent.Geometry.Region region)
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

        private string GetCacheKey(Latent.Geometry.Region region)
        {
            return region.Id;
        }

        private class FillCache
        {
            public Mesh Mesh { get; set; }
            public int BoundaryHash { get; set; }
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
        public static BoundingBox GetDisplayBoundingBox(this Latent.Geometry.Region region, SubDEvaluator evaluator)
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
        public Point3d? GetCentroid3d(Latent.Geometry.Region region)
        {
            if (region == null)
                throw new ArgumentNullException(nameof(region));

            var key = region.Id;

            // Check cache using boundary hash as version proxy
            lock (_lock)
            {
                if (_cache.TryGetValue(key, out var cached) &&
                    cached.BoundaryHash == GetBoundaryHash(region))
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
                    BoundaryHash = GetBoundaryHash(region)
                };
            }

            return centroid;
        }

        /// <summary>
        /// Compute the 3D centroid from the region.
        /// </summary>
        private Point3d? ComputeCentroid3d(Latent.Geometry.Region region)
        {
            // Use region's cached centroid if available and valid
            var cachedCentroid = region.Centroid;
            if (cachedCentroid.IsValid && cachedCentroid != Point3d.Origin)
            {
                return cachedCentroid;
            }

            // Fallback: compute from boundary vertices
            return ComputeFromBoundary(region);
        }

        /// <summary>
        /// Compute centroid from boundary edge midpoints.
        /// </summary>
        private Point3d? ComputeFromBoundary(Latent.Geometry.Region region)
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
        public Point3d? GetCentroidWithOffset(Latent.Geometry.Region region, double offset)
        {
            var centroid = GetCentroid3d(region);
            if (!centroid.HasValue)
                return null;

            // Try to get normal at centroid if we have parametric position
            // For now, compute average normal from boundary vertices
            var normal = ComputeAverageNormal(region);

            if (normal.HasValue && normal.Value.Length > 0)
            {
                var unitNormal = normal.Value;
                unitNormal.Unitize();
                return centroid.Value + unitNormal * offset;
            }

            return centroid;
        }

        /// <summary>
        /// Compute average normal from boundary vertices.
        /// </summary>
        private Vector3d? ComputeAverageNormal(Latent.Geometry.Region region)
        {
            var normals = new List<Vector3d>();

            foreach (var edge in region.BoundaryEdges)
            {
                foreach (var vertex in edge.Vertices)
                {
                    var pos = vertex.Position;
                    var normal = _evaluator.EvaluateNormal(pos.FaceId, pos.U, pos.V);
                    normals.Add(normal);
                }
            }

            if (normals.Count == 0)
                return null;

            // Average normals
            double x = 0, y = 0, z = 0;
            foreach (var n in normals)
            {
                x += n.X;
                y += n.Y;
                z += n.Z;
            }

            int count = normals.Count;
            return new Vector3d(x / count, y / count, z / count);
        }

        /// <summary>
        /// Get a hash of the boundary to detect changes.
        /// </summary>
        private int GetBoundaryHash(Latent.Geometry.Region region)
        {
            unchecked
            {
                int hash = 17;
                foreach (var edge in region.BoundaryEdges)
                {
                    hash = hash * 31 + edge.Id.GetHashCode();
                    hash = hash * 31 + edge.Version;
                }
                return hash;
            }
        }

        /// <summary>
        /// Invalidate cache for a region.
        /// </summary>
        public void Invalidate(Latent.Geometry.Region region)
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
            public int BoundaryHash { get; set; }
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
