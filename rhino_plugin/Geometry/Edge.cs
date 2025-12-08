// rhino_plugin/Geometry/Edge.cs
using System;
using System.Collections.Generic;
using System.Linq;
using Latent.Interop;

namespace Latent.Geometry
{
    /// <summary>
    /// An edge (boundary curve) in the region graph.
    /// </summary>
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
