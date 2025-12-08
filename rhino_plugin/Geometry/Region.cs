// rhino_plugin/Geometry/Region.cs
using System;
using System.Collections.Generic;
using Rhino.Geometry;

namespace Latent.Geometry
{
    /// <summary>
    /// A region bounded by edges.
    /// </summary>
    public class Region : IGeometryElement
    {
        public string Id { get; }
        public List<string> BoundaryEdgeIds { get; }
        public string UnityPrinciple { get; }
        public double ResonanceScore { get; }
        public bool IsPinned { get; set; }
        public bool IsSelected { get; set; }

        // Reference to edges (populated by RegionManager)
        public List<Edge> BoundaryEdges { get; internal set; } = new();

        // Cached geometry
        private Point3d? _centroid;
        private BoundingBox? _boundingBox;

        public Region(
            string id,
            List<string> boundaryEdgeIds,
            string unityPrinciple,
            double resonanceScore)
        {
            Id = id ?? throw new ArgumentNullException(nameof(id));
            BoundaryEdgeIds = boundaryEdgeIds ?? throw new ArgumentNullException(nameof(boundaryEdgeIds));
            UnityPrinciple = unityPrinciple ?? "";
            ResonanceScore = resonanceScore;
        }

        /// <summary>
        /// Whether all boundary elements are implicit.
        /// </summary>
        public bool IsImplicit =>
            BoundaryEdges.TrueForAll(e => e.IsImplicit);

        /// <summary>
        /// Whether this region can be reverted.
        /// </summary>
        public bool CanRevert => !IsPinned && !IsImplicit;

        /// <summary>
        /// Get or compute the region centroid.
        /// </summary>
        public Point3d Centroid
        {
            get => _centroid ?? Point3d.Origin;
            internal set => _centroid = value;
        }

        /// <summary>
        /// Get or compute the bounding box.
        /// </summary>
        public BoundingBox BoundingBox
        {
            get => _boundingBox ?? BoundingBox.Empty;
            internal set => _boundingBox = value;
        }

        /// <summary>
        /// Invalidate cached geometry (call after changes).
        /// </summary>
        public void InvalidateCache()
        {
            _centroid = null;
            _boundingBox = null;
        }

        /// <summary>
        /// Create from analysis data.
        /// </summary>
        public static Region FromData(Analysis.RegionData data)
        {
            return new Region(
                data.Id,
                data.BoundaryEdgeIds,
                data.UnityPrinciple,
                data.ResonanceScore
            )
            {
                IsPinned = data.IsPinned
            };
        }
    }
}
