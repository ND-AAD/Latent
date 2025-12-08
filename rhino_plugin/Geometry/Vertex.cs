// rhino_plugin/Geometry/Vertex.cs
using System;
using Latent.Interop;

namespace Latent.Geometry
{
    /// <summary>
    /// How this vertex was created.
    /// </summary>
    public enum VertexOrigin
    {
        Lens,              // Created by lens analysis
        CurveModification, // Added when changing curve degree
        UserAdded          // Explicitly added by user
    }

    /// <summary>
    /// A vertex in the region graph.
    /// </summary>
    public class Vertex : IGeometryElement
    {
        public string Id { get; }
        public ParametricPoint Position { get; set; }
        public ParametricPoint? ImplicitPosition { get; }
        public VertexOrigin CreatedBy { get; }
        public bool IsPinned { get; set; }
        public bool IsSelected { get; set; }

        public Vertex(
            string id,
            ParametricPoint position,
            ParametricPoint? implicitPosition = null,
            VertexOrigin createdBy = VertexOrigin.Lens)
        {
            Id = id ?? throw new ArgumentNullException(nameof(id));
            Position = position;
            ImplicitPosition = implicitPosition ?? position;
            CreatedBy = createdBy;
        }

        /// <summary>
        /// Whether the vertex is at its implicit position.
        /// </summary>
        public bool IsImplicit
        {
            get
            {
                if (!ImplicitPosition.HasValue)
                    return false;

                var imp = ImplicitPosition.Value;
                return Position.FaceId == imp.FaceId &&
                       Math.Abs(Position.U - imp.U) < 1e-6 &&
                       Math.Abs(Position.V - imp.V) < 1e-6;
            }
        }

        /// <summary>
        /// Whether this vertex can be reverted.
        /// </summary>
        public bool CanRevert
        {
            get
            {
                if (IsPinned) return false;
                if (CreatedBy == VertexOrigin.CurveModification) return false;
                if (!ImplicitPosition.HasValue) return false;
                return !IsImplicit;
            }
        }

        /// <summary>
        /// Revert this vertex to its implicit position.
        /// </summary>
        public void Revert()
        {
            if (!CanRevert || !ImplicitPosition.HasValue)
                throw new InvalidOperationException("Cannot revert this vertex");

            Position = ImplicitPosition.Value;
        }

        /// <summary>
        /// Create from analysis data.
        /// </summary>
        public static Vertex FromData(Analysis.VertexData data)
        {
            var origin = data.CreatedBy switch
            {
                "lens" => VertexOrigin.Lens,
                "curve_modification" => VertexOrigin.CurveModification,
                "user_added" => VertexOrigin.UserAdded,
                _ => VertexOrigin.Lens
            };

            return new Vertex(
                data.Id,
                data.GetPosition(),
                data.GetImplicitPosition(),
                origin
            )
            {
                IsPinned = data.IsPinned
            };
        }
    }
}
