// rhino_plugin/Interop/NativeCore.cs
using System;
using System.Runtime.InteropServices;

namespace Latent.Interop
{
    /// <summary>
    /// P/Invoke declarations for the latent_core native library.
    /// </summary>
    public static class NativeCore
    {
        private const string DllName = "latent_core";

        #region Evaluator Lifecycle

        [DllImport(DllName, CallingConvention = CallingConvention.Cdecl)]
        public static extern IntPtr latent_evaluator_create();

        [DllImport(DllName, CallingConvention = CallingConvention.Cdecl)]
        public static extern void latent_evaluator_destroy(IntPtr handle);

        [DllImport(DllName, CallingConvention = CallingConvention.Cdecl)]
        public static extern bool latent_evaluator_initialize(
            IntPtr handle,
            [MarshalAs(UnmanagedType.LPArray)] float[] vertices, int vertexCount,
            [MarshalAs(UnmanagedType.LPArray)] int[] faces,
            [MarshalAs(UnmanagedType.LPArray)] int[] faceSizes, int faceCount,
            [MarshalAs(UnmanagedType.LPArray)] int[] creaseEdges,
            [MarshalAs(UnmanagedType.LPArray)] float[] creaseSharpness, int creaseCount);

        [DllImport(DllName, CallingConvention = CallingConvention.Cdecl)]
        public static extern bool latent_evaluator_is_initialized(IntPtr handle);

        [DllImport(DllName, CallingConvention = CallingConvention.Cdecl)]
        public static extern int latent_evaluator_get_face_count(IntPtr handle);

        #endregion

        #region Forward Evaluation

        [DllImport(DllName, CallingConvention = CallingConvention.Cdecl)]
        public static extern bool latent_evaluate_point(
            IntPtr handle,
            int faceId, float u, float v,
            out float x, out float y, out float z);

        [DllImport(DllName, CallingConvention = CallingConvention.Cdecl)]
        public static extern bool latent_evaluate_normal(
            IntPtr handle,
            int faceId, float u, float v,
            out float nx, out float ny, out float nz);

        [DllImport(DllName, CallingConvention = CallingConvention.Cdecl)]
        public static extern bool latent_evaluate_point_and_normal(
            IntPtr handle,
            int faceId, float u, float v,
            out float x, out float y, out float z,
            out float nx, out float ny, out float nz);

        [DllImport(DllName, CallingConvention = CallingConvention.Cdecl)]
        public static extern bool latent_evaluate_full(
            IntPtr handle,
            int faceId, float u, float v,
            [MarshalAs(UnmanagedType.LPArray, SizeConst = 3)] float[] point,
            [MarshalAs(UnmanagedType.LPArray, SizeConst = 3)] float[] normal,
            [MarshalAs(UnmanagedType.LPArray, SizeConst = 3)] float[] du,
            [MarshalAs(UnmanagedType.LPArray, SizeConst = 3)] float[] dv);

        #endregion

        #region Inverse Evaluation

        [DllImport(DllName, CallingConvention = CallingConvention.Cdecl)]
        public static extern bool latent_project_point(
            IntPtr handle,
            float px, float py, float pz,
            out int faceId, out float u, out float v);

        #endregion

        #region Tessellation

        [DllImport(DllName, CallingConvention = CallingConvention.Cdecl)]
        public static extern bool latent_tessellate(
            IntPtr handle,
            int subdivisionLevel,
            [MarshalAs(UnmanagedType.LPArray)] float[] outVertices,
            [MarshalAs(UnmanagedType.LPArray)] float[] outNormals,
            [MarshalAs(UnmanagedType.LPArray)] int[] outTriangles,
            out int outVertexCount,
            out int outTriangleCount);

        #endregion

        #region Curves

        [DllImport(DllName, CallingConvention = CallingConvention.Cdecl)]
        public static extern IntPtr latent_curve_create(
            [MarshalAs(UnmanagedType.LPArray)] int[] faceIds,
            [MarshalAs(UnmanagedType.LPArray)] float[] us,
            [MarshalAs(UnmanagedType.LPArray)] float[] vs,
            int pointCount,
            int curveType,
            int degree);

        [DllImport(DllName, CallingConvention = CallingConvention.Cdecl)]
        public static extern void latent_curve_destroy(IntPtr handle);

        [DllImport(DllName, CallingConvention = CallingConvention.Cdecl)]
        public static extern bool latent_curve_evaluate(
            IntPtr curveHandle,
            IntPtr evaluatorHandle,
            float t,
            out float x, out float y, out float z);

        [DllImport(DllName, CallingConvention = CallingConvention.Cdecl)]
        public static extern bool latent_curve_evaluate_parametric(
            IntPtr handle,
            float t,
            out int faceId, out float u, out float v);

        [DllImport(DllName, CallingConvention = CallingConvention.Cdecl)]
        public static extern bool latent_curve_sample(
            IntPtr curveHandle,
            IntPtr evaluatorHandle,
            int numSamples,
            [MarshalAs(UnmanagedType.LPArray)] float[] outPoints);

        [DllImport(DllName, CallingConvention = CallingConvention.Cdecl)]
        public static extern bool latent_curve_arc_length(
            IntPtr curveHandle,
            IntPtr evaluatorHandle,
            out float outLength);

        [DllImport(DllName, CallingConvention = CallingConvention.Cdecl)]
        public static extern int latent_curve_get_point_count(IntPtr handle);

        [DllImport(DllName, CallingConvention = CallingConvention.Cdecl)]
        public static extern int latent_curve_get_type(IntPtr handle);

        [DllImport(DllName, CallingConvention = CallingConvention.Cdecl)]
        public static extern int latent_curve_get_degree(IntPtr handle);

        #endregion

        #region Curvature

        [DllImport(DllName, CallingConvention = CallingConvention.Cdecl)]
        public static extern bool latent_compute_curvature(
            IntPtr handle,
            int faceId, float u, float v,
            out float k1, out float k2, out float H, out float K);

        [DllImport(DllName, CallingConvention = CallingConvention.Cdecl)]
        public static extern bool latent_compute_curvature_directions(
            IntPtr handle,
            int faceId, float u, float v,
            [MarshalAs(UnmanagedType.LPArray, SizeConst = 3)] float[] dir1,
            [MarshalAs(UnmanagedType.LPArray, SizeConst = 3)] float[] dir2);

        [DllImport(DllName, CallingConvention = CallingConvention.Cdecl)]
        public static extern bool latent_sample_curvature_grid(
            IntPtr handle,
            int faceId,
            int resolution,
            [MarshalAs(UnmanagedType.LPArray)] float[] outH,
            [MarshalAs(UnmanagedType.LPArray)] float[] outK);

        #endregion

        #region Error Handling

        [DllImport(DllName, CallingConvention = CallingConvention.Cdecl)]
        public static extern IntPtr latent_get_last_error();

        public static string GetLastError()
        {
            IntPtr ptr = latent_get_last_error();
            return Marshal.PtrToStringAnsi(ptr) ?? "";
        }

        #endregion
    }
}
