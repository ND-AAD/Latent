// rhino_plugin/Interop/ParametricPoint.cs
namespace Latent.Interop
{
    /// <summary>
    /// A point in SubD parametric space (face_id, u, v).
    /// </summary>
    public struct ParametricPoint
    {
        public int FaceId { get; set; }
        public double U { get; set; }
        public double V { get; set; }

        public ParametricPoint(int faceId, double u, double v)
        {
            FaceId = faceId;
            U = u;
            V = v;
        }

        public bool IsValid => FaceId >= 0;

        /// <summary>
        /// An invalid/unset parametric point.
        /// </summary>
        public static ParametricPoint Unset => new ParametricPoint(-1, 0, 0);

        public override string ToString()
        {
            return $"ParametricPoint({FaceId}, {U:F4}, {V:F4})";
        }
    }
}
