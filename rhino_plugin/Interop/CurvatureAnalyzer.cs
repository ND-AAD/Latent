// rhino_plugin/Interop/CurvatureAnalyzer.cs
using System;
using Rhino.Geometry;

namespace Latent.Interop
{
    /// <summary>
    /// Curvature data at a surface point.
    /// </summary>
    public struct CurvatureData
    {
        public double K1;          // Maximum principal curvature
        public double K2;          // Minimum principal curvature
        public double MeanH;       // Mean curvature (K1 + K2) / 2
        public double GaussianK;   // Gaussian curvature (K1 * K2)
        public Vector3d Dir1;      // Direction of maximum curvature
        public Vector3d Dir2;      // Direction of minimum curvature
    }

    /// <summary>
    /// Managed wrapper for curvature analysis functions.
    /// </summary>
    public class CurvatureAnalyzer
    {
        private readonly SubDEvaluator _evaluator;

        public CurvatureAnalyzer(SubDEvaluator evaluator)
        {
            _evaluator = evaluator ?? throw new ArgumentNullException(nameof(evaluator));
        }

        /// <summary>
        /// Compute curvature at a parametric point.
        /// </summary>
        public CurvatureData ComputeCurvature(int faceId, double u, double v)
        {
            if (!NativeCore.latent_compute_curvature(
                    _evaluator.Handle, faceId, (float)u, (float)v,
                    out float k1, out float k2, out float H, out float K))
            {
                throw new InvalidOperationException("Curvature computation failed");
            }

            return new CurvatureData
            {
                K1 = k1,
                K2 = k2,
                MeanH = H,
                GaussianK = K
            };
        }

        /// <summary>
        /// Compute curvature including principal directions.
        /// </summary>
        public CurvatureData ComputeCurvatureWithDirections(int faceId, double u, double v)
        {
            var data = ComputeCurvature(faceId, u, v);

            var dir1 = new float[3];
            var dir2 = new float[3];

            if (NativeCore.latent_compute_curvature_directions(
                    _evaluator.Handle, faceId, (float)u, (float)v, dir1, dir2))
            {
                data.Dir1 = new Vector3d(dir1[0], dir1[1], dir1[2]);
                data.Dir2 = new Vector3d(dir2[0], dir2[1], dir2[2]);
            }

            return data;
        }

        /// <summary>
        /// Sample curvature across a grid on one face.
        /// </summary>
        public (double[,] MeanH, double[,] GaussianK) SampleCurvatureGrid(
            int faceId, int resolution)
        {
            var outH = new float[resolution * resolution];
            var outK = new float[resolution * resolution];

            if (!NativeCore.latent_sample_curvature_grid(
                    _evaluator.Handle, faceId, resolution, outH, outK))
            {
                throw new InvalidOperationException("Curvature grid sampling failed");
            }

            var meanH = new double[resolution, resolution];
            var gaussianK = new double[resolution, resolution];

            for (int j = 0; j < resolution; j++)
            {
                for (int i = 0; i < resolution; i++)
                {
                    int idx = j * resolution + i;
                    meanH[i, j] = outH[idx];
                    gaussianK[i, j] = outK[idx];
                }
            }

            return (meanH, gaussianK);
        }
    }
}
