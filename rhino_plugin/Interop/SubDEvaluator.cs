// rhino_plugin/Interop/SubDEvaluator.cs
using System;
using System.Collections.Generic;
using Rhino.Geometry;

namespace Latent.Interop
{
    /// <summary>
    /// Managed wrapper for the native SubD evaluator.
    /// </summary>
    public class SubDEvaluator : IDisposable
    {
        private IntPtr _handle;
        private bool _disposed;

        public SubDEvaluator()
        {
            _handle = NativeCore.latent_evaluator_create();
            if (_handle == IntPtr.Zero)
            {
                throw new InvalidOperationException("Failed to create evaluator");
            }
        }

        public bool IsInitialized => NativeCore.latent_evaluator_is_initialized(_handle);
        public int FaceCount => NativeCore.latent_evaluator_get_face_count(_handle);

        /// <summary>
        /// Initialize the evaluator with a Rhino SubD.
        /// </summary>
        public void Initialize(SubD subd)
        {
            var (vertices, faces, faceSizes, creaseEdges, creaseSharpness) = ExtractCage(subd);

            bool success = NativeCore.latent_evaluator_initialize(
                _handle,
                vertices, vertices.Length / 3,
                faces, faceSizes, faceSizes.Length,
                creaseEdges, creaseSharpness, creaseEdges?.Length / 2 ?? 0
            );

            if (!success)
            {
                throw new InvalidOperationException(
                    $"Failed to initialize evaluator: {NativeCore.GetLastError()}"
                );
            }
        }

        /// <summary>
        /// Evaluate a point on the limit surface.
        /// </summary>
        public Point3d EvaluatePoint(int faceId, double u, double v)
        {
            if (!NativeCore.latent_evaluate_point(
                    _handle, faceId, (float)u, (float)v,
                    out float x, out float y, out float z))
            {
                throw new InvalidOperationException(
                    $"Evaluation failed: {NativeCore.GetLastError()}"
                );
            }
            return new Point3d(x, y, z);
        }

        /// <summary>
        /// Evaluate the normal at a point on the limit surface.
        /// </summary>
        public Vector3d EvaluateNormal(int faceId, double u, double v)
        {
            if (!NativeCore.latent_evaluate_normal(
                    _handle, faceId, (float)u, (float)v,
                    out float nx, out float ny, out float nz))
            {
                throw new InvalidOperationException(
                    $"Normal evaluation failed: {NativeCore.GetLastError()}"
                );
            }
            return new Vector3d(nx, ny, nz);
        }

        /// <summary>
        /// Evaluate point and normal together (more efficient than separate calls).
        /// </summary>
        public (Point3d point, Vector3d normal) EvaluatePointAndNormal(int faceId, double u, double v)
        {
            if (!NativeCore.latent_evaluate_point_and_normal(
                    _handle, faceId, (float)u, (float)v,
                    out float x, out float y, out float z,
                    out float nx, out float ny, out float nz))
            {
                throw new InvalidOperationException(
                    $"Evaluation failed: {NativeCore.GetLastError()}"
                );
            }
            return (new Point3d(x, y, z), new Vector3d(nx, ny, nz));
        }

        /// <summary>
        /// Project a 3D point onto the limit surface.
        /// </summary>
        public ParametricPoint ProjectPoint(Point3d point)
        {
            if (!NativeCore.latent_project_point(
                    _handle,
                    (float)point.X, (float)point.Y, (float)point.Z,
                    out int faceId, out float u, out float v))
            {
                return new ParametricPoint(-1, 0, 0);
            }
            return new ParametricPoint(faceId, u, v);
        }

        /// <summary>
        /// Extract control cage from Rhino SubD.
        /// NOTE: This is a stub implementation. RhinoCommon 8 SubD API access to control cage
        /// requires using ComponentIndex and direct mesh extraction. For now, we create a
        /// simple mesh approximation.
        /// TODO: Implement proper control cage extraction when RhinoCommon API is clarified.
        /// </summary>
        private static (float[] vertices, int[] faces, int[] faceSizes,
                        int[]? creaseEdges, float[]? creaseSharpness) ExtractCage(SubD subd)
        {
            // For now, create a simple test cage from a mesh
            // This is a placeholder until proper SubD control cage API is available
            var mesh = new Mesh();
            mesh.Vertices.Add(new Point3d(0, 0, 0));
            mesh.Vertices.Add(new Point3d(1, 0, 0));
            mesh.Vertices.Add(new Point3d(1, 1, 0));
            mesh.Vertices.Add(new Point3d(0, 1, 0));
            mesh.Faces.AddFace(0, 1, 2, 3);

            // Extract vertices from mesh
            var vertices = new List<float>();
            for (int i = 0; i < mesh.Vertices.Count; i++)
            {
                var v = mesh.Vertices[i];
                vertices.Add((float)v.X);
                vertices.Add((float)v.Y);
                vertices.Add((float)v.Z);
            }

            // Extract faces
            var faces = new List<int>();
            var faceSizes = new List<int>();

            for (int i = 0; i < mesh.Faces.Count; i++)
            {
                var f = mesh.Faces[i];
                if (f.IsQuad)
                {
                    faceSizes.Add(4);
                    faces.Add(f.A);
                    faces.Add(f.B);
                    faces.Add(f.C);
                    faces.Add(f.D);
                }
                else
                {
                    faceSizes.Add(3);
                    faces.Add(f.A);
                    faces.Add(f.B);
                    faces.Add(f.C);
                }
            }

            // No creases in this stub implementation
            return (
                vertices.ToArray(),
                faces.ToArray(),
                faceSizes.ToArray(),
                null,
                null
            );
        }

        public void Dispose()
        {
            Dispose(true);
            GC.SuppressFinalize(this);
        }

        protected virtual void Dispose(bool disposing)
        {
            if (!_disposed)
            {
                if (_handle != IntPtr.Zero)
                {
                    NativeCore.latent_evaluator_destroy(_handle);
                    _handle = IntPtr.Zero;
                }
                _disposed = true;
            }
        }

        ~SubDEvaluator()
        {
            Dispose(false);
        }

        internal IntPtr Handle => _handle;
    }
}
