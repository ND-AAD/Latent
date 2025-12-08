// rhino_plugin/Interop/ParametricPoint.cs
namespace Latent.Interop
{
    /// <summary>
    /// Represents a point in SubD parametric space as (face_id, u, v).
    /// </summary>
    /// <remarks>
    /// <para>
    /// Parametric points are the fundamental coordinate type for positions on
    /// the SubD limit surface. They consist of:
    /// </para>
    /// <list type="bullet">
    /// <item><description>FaceId: Index of the control cage face</description></item>
    /// <item><description>U: Parameter in [0,1] within the face</description></item>
    /// <item><description>V: Parameter in [0,1] within the face</description></item>
    /// </list>
    /// <para>
    /// Use <see cref="Unset"/> to represent an invalid or uninitialized point.
    /// Check <see cref="IsValid"/> before using a parametric point.
    /// </para>
    /// </remarks>
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
