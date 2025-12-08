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
        /// This extracts the control net vertices, face topology, and crease information
        /// using RhinoCommon's SubD API - NO mesh conversion, maintaining exact representation.
        ///
        /// Note: RhinoCommon SubD uses linked-list iteration (.First/.Next pattern),
        /// not array-based access like meshes.
        /// </summary>
        private static (float[] vertices, int[] faces, int[] faceSizes,
                        int[]? creaseEdges, float[]? creaseSharpness) ExtractCage(SubD subd)
        {
            if (subd == null)
                throw new ArgumentNullException(nameof(subd));

            // Build vertex index mapping: SubD vertex ID -> sequential index
            // SubD vertices use linked-list iteration: .First, then .Next
            var vertexMap = new Dictionary<uint, int>();
            var vertices = new List<float>();

            int idx = 0;
            var vertex = subd.Vertices.First;
            while (vertex != null)
            {
                // Use ControlNetPoint - the exact control cage position (NOT limit surface)
                var pt = vertex.ControlNetPoint;
                vertices.Add((float)pt.X);
                vertices.Add((float)pt.Y);
                vertices.Add((float)pt.Z);
                vertexMap[vertex.Id] = idx++;
                vertex = vertex.Next;
            }

            // Extract face topology from control net
            // Use foreach which works with SubDFaceList's IEnumerable implementation
            var faceIndices = new List<int>();
            var faceSizes = new List<int>();

            foreach (SubDFace face in subd.Faces)
            {
                // Get vertices around this face using VertexAt(index)
                int edgeCount = face.EdgeCount;
                faceSizes.Add(edgeCount);

                // Collect vertex IDs using the proper VertexAt API
                for (int i = 0; i < edgeCount; i++)
                {
                    var faceVertex = face.VertexAt(i);
                    if (faceVertex != null && vertexMap.TryGetValue(faceVertex.Id, out int vertexIndex))
                    {
                        faceIndices.Add(vertexIndex);
                    }
                }
            }

            // Extract crease edges
            // Use foreach which works with SubDEdgeList's IEnumerable implementation
            var creaseEdgeIndices = new List<int>();
            var creaseSharpnessValues = new List<float>();

            foreach (SubDEdge edge in subd.Edges)
            {
                // Check if edge is a crease using Tag property
                // SubDEdgeTag.Crease indicates a crease edge
                if (edge.Tag == SubDEdgeTag.Crease)
                {
                    // Get vertices at ends of edge using VertexFrom/VertexTo properties
                    var v0 = edge.VertexFrom;
                    var v1 = edge.VertexTo;

                    if (v0 != null && v1 != null &&
                        vertexMap.TryGetValue(v0.Id, out int idx0) &&
                        vertexMap.TryGetValue(v1.Id, out int idx1))
                    {
                        creaseEdgeIndices.Add(idx0);
                        creaseEdgeIndices.Add(idx1);
                        // Crease edges are sharp (weight 1.0)
                        creaseSharpnessValues.Add(1.0f);
                    }
                }
            }

            return (
                vertices.ToArray(),
                faceIndices.ToArray(),
                faceSizes.ToArray(),
                creaseEdgeIndices.Count > 0 ? creaseEdgeIndices.ToArray() : null,
                creaseSharpnessValues.Count > 0 ? creaseSharpnessValues.ToArray() : null
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
