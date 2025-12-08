// rhino_plugin/Interop/CurveType.cs
namespace Latent.Interop
{
    /// <summary>
    /// Type of boundary curve.
    /// Values 0-2 match the C API (LATENT_CURVE_*).
    /// </summary>
    public enum CurveType
    {
        Linear = 0,    // LATENT_CURVE_LINEAR
        Bezier = 1,    // LATENT_CURVE_BEZIER
        BSpline = 2,   // LATENT_CURVE_BSPLINE
        Geodesic = 3,  // C++ only (not in C API yet)
        Implicit = 4   // C++ only (not in C API yet)
    }
}
