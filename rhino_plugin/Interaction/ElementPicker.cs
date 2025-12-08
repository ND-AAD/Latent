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
            double t = Math.Max(0.0, Math.Min(1.0, ((point - lineStart) * line) / lengthSq));
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
