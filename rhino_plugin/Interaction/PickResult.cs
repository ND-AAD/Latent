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
