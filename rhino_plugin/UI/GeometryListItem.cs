// rhino_plugin/UI/GeometryListItem.cs
using System;
using Latent.Geometry;

namespace Latent.UI
{
    /// <summary>
    /// Display mode for the geometry list.
    /// </summary>
    public enum GeometryListMode
    {
        Regions,
        Edges,
        Vertices
    }

    /// <summary>
    /// Adapter for displaying geometry elements in a grid view.
    /// Wraps IGeometryElement with display-friendly properties.
    /// </summary>
    public class GeometryListItem
    {
        private readonly IGeometryElement _element;

        public GeometryListItem(IGeometryElement element)
        {
            _element = element ?? throw new ArgumentNullException(nameof(element));
        }

        /// <summary>
        /// The underlying geometry element.
        /// </summary>
        public IGeometryElement Element => _element;

        /// <summary>
        /// Element ID for display.
        /// </summary>
        public string Id => _element.Id;

        /// <summary>
        /// Whether the element is pinned.
        /// </summary>
        public bool IsPinned
        {
            get => _element.IsPinned;
            set => _element.IsPinned = value;
        }

        /// <summary>
        /// State string for display: "implicit", "explicit", or "pinned".
        /// </summary>
        public string State
        {
            get
            {
                if (IsPinned) return "📌 pinned";
                if (_element.IsImplicit) return "implicit";
                return "explicit";
            }
        }

        /// <summary>
        /// Whether revert is available.
        /// </summary>
        public bool CanRevert => _element.CanRevert;

        /// <summary>
        /// Additional info based on element type.
        /// </summary>
        public string Details
        {
            get
            {
                return _element switch
                {
                    Vertex v => $"Origin: {v.CreatedBy}",
                    Edge e => $"{e.CurveType} °{e.Degree}",
                    Region r => $"Score: {r.ResonanceScore:F2}",
                    _ => ""
                };
            }
        }

        /// <summary>
        /// Tooltip with full element information.
        /// </summary>
        public string Tooltip
        {
            get
            {
                return _element switch
                {
                    Vertex v => $"Vertex {v.Id}\nOrigin: {v.CreatedBy}\nImplicit: {v.IsImplicit}\nPinned: {v.IsPinned}",
                    Edge e => $"Edge {e.Id}\nType: {e.CurveType} degree {e.Degree}\nVertices: {e.VertexIds.Count}\nPinned: {e.IsPinned}",
                    Region r => $"Region {r.Id}\nPrinciple: {r.UnityPrinciple}\nResonance: {r.ResonanceScore:F3}\nEdges: {r.BoundaryEdgeIds.Count}",
                    _ => ""
                };
            }
        }

        /// <summary>
        /// Get the element type name.
        /// </summary>
        public string TypeName
        {
            get
            {
                return _element switch
                {
                    Vertex => "Vertex",
                    Edge => "Edge",
                    Region => "Region",
                    _ => "Unknown"
                };
            }
        }

        /// <summary>
        /// For vertices created by curve modification, get the parent edge ID.
        /// </summary>
        public string? ParentEdgeId
        {
            get
            {
                if (_element is Vertex v && v.CreatedBy == VertexOrigin.CurveModification)
                {
                    return v.ParentEdgeId;
                }
                return null;
            }
        }
    }
}
