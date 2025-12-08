// rhino_plugin/Geometry/Edge.cs
using System;
using System.Collections.Generic;
using System.Linq;
using Latent.Interop;

namespace Latent.Geometry
{
    /// <summary>
    /// A boundary curve edge in the region graph.
    /// Edges connect vertices and define region boundaries on the SubD limit surface.
    /// </summary>
    /// <remarks>
    /// <para>
    /// Each edge maintains:
    /// </para>
    /// <list type="bullet">
    /// <item><description>Ordered list of control vertex IDs</description></item>
    /// <item><description>Curve type (Linear, Bezier, BSpline)</description></item>
    /// <item><description>Curve degree (determines number of control points)</description></item>
    /// <item><description>Implicit curve type (original from lens analysis)</description></item>
    /// </list>
    /// <para>
    /// Edges support two revert modes:
    /// </para>
    /// <list type="bullet">
    /// <item><description>RevertCurveType: Restore original curve type/degree, keep vertex positions</description></item>
    /// <item><description>Full revert: Restore both curve type and all vertex positions</description></item>
    /// </list>
    /// <para>
    /// Version tracking enables cache invalidation when the edge geometry changes.
    /// </para>
    /// </remarks>
    public class Edge : IGeometryElement
    {
        public string Id { get; }
        public List<string> VertexIds { get; }
        public CurveType CurveType { get; set; }
        public int Degree { get; set; }
        public CurveType? ImplicitCurveType { get; }
        public int? ImplicitDegree { get; }
        public bool IsPinned { get; set; }
        public bool IsSelected { get; set; }

        // Reference to vertices (populated by RegionManager)
        public List<Vertex> Vertices { get; internal set; } = new();

        // Version tracking for cache invalidation
        private int _version = 0;
        public int Version => _version;

        public Edge(
            string id,
            List<string> vertexIds,
            CurveType curveType = CurveType.Bezier,
            int degree = 3,
            CurveType? implicitCurveType = null,
            int? implicitDegree = null)
        {
            Id = id ?? throw new ArgumentNullException(nameof(id));
            VertexIds = vertexIds ?? throw new ArgumentNullException(nameof(vertexIds));
            CurveType = curveType;
            Degree = degree;
            ImplicitCurveType = implicitCurveType ?? curveType;
            ImplicitDegree = implicitDegree ?? degree;
        }

        /// <summary>
        /// Whether the edge is at its implicit curve type.
        /// </summary>
        public bool IsImplicit =>
            CurveType == ImplicitCurveType && Degree == ImplicitDegree;

        /// <summary>
        /// Whether this edge can be reverted.
        /// </summary>
        public bool CanRevert => !IsPinned && !IsImplicit;

        /// <summary>
        /// Revert only the curve type (keep vertex positions).
        /// </summary>
        public void RevertCurveType()
        {
            if (IsPinned)
                throw new InvalidOperationException("Cannot revert: edge is pinned");

            if (ImplicitCurveType.HasValue)
                CurveType = ImplicitCurveType.Value;

            if (ImplicitDegree.HasValue)
                Degree = ImplicitDegree.Value;

            IncrementVersion();
        }

        /// <summary>
        /// Increment version for cache invalidation.
        /// Call this whenever the edge geometry changes.
        /// </summary>
        public void IncrementVersion()
        {
            _version++;
        }

        /// <summary>
        /// Get control points for curve creation.
        /// </summary>
        public List<ParametricPoint> GetControlPoints()
        {
            return Vertices.Select(v => v.Position).ToList();
        }

        /// <summary>
        /// Create from analysis data.
        /// </summary>
        public static Edge FromData(Analysis.EdgeData data)
        {
            var curveType = data.CurveType switch
            {
                "linear" => CurveType.Linear,
                "bezier" => CurveType.Bezier,
                "bspline" => CurveType.BSpline,
                _ => CurveType.Bezier
            };

            return new Edge(
                data.Id,
                data.VertexIds,
                curveType,
                data.Degree
            )
            {
                IsPinned = data.IsPinned
            };
        }
    }
}
