// rhino_plugin/Interop/SurfaceCurve.cs
using System;
using System.Collections.Generic;
using Rhino.Geometry;

namespace Latent.Interop
{
    /// <summary>
    /// Managed wrapper for a curve on the SubD limit surface.
    /// </summary>
    public class SurfaceCurve : IDisposable
    {
        private IntPtr _handle;
        private bool _disposed;
        private readonly List<ParametricPoint> _controlPoints;
        private readonly CurveType _type;
        private readonly int _degree;

        public SurfaceCurve(
            List<ParametricPoint> controlPoints,
            CurveType type = CurveType.Bezier,
            int degree = 3)
        {
            _controlPoints = controlPoints;
            _type = type;
            _degree = degree;

            // Convert to native arrays
            var faceIds = new int[controlPoints.Count];
            var us = new float[controlPoints.Count];
            var vs = new float[controlPoints.Count];

            for (int i = 0; i < controlPoints.Count; i++)
            {
                faceIds[i] = controlPoints[i].FaceId;
                us[i] = (float)controlPoints[i].U;
                vs[i] = (float)controlPoints[i].V;
            }

            _handle = NativeCore.latent_curve_create(
                faceIds, us, vs, controlPoints.Count,
                (int)type, degree
            );

            if (_handle == IntPtr.Zero)
            {
                throw new InvalidOperationException("Failed to create surface curve");
            }
        }

        public IReadOnlyList<ParametricPoint> ControlPoints => _controlPoints;
        public CurveType Type => _type;
        public int Degree => _degree;
        public int PointCount => NativeCore.latent_curve_get_point_count(_handle);

        /// <summary>
        /// Evaluate the curve at parameter t.
        /// </summary>
        public Point3d Evaluate(double t, SubDEvaluator evaluator)
        {
            if (!NativeCore.latent_curve_evaluate(
                    _handle, evaluator.Handle, (float)t,
                    out float x, out float y, out float z))
            {
                throw new InvalidOperationException("Curve evaluation failed");
            }
            return new Point3d(x, y, z);
        }

        /// <summary>
        /// Evaluate the parametric position at parameter t.
        /// </summary>
        public ParametricPoint EvaluateParametric(double t)
        {
            if (!NativeCore.latent_curve_evaluate_parametric(
                    _handle, (float)t,
                    out int faceId, out float u, out float v))
            {
                return new ParametricPoint(-1, 0, 0);
            }
            return new ParametricPoint(faceId, u, v);
        }

        /// <summary>
        /// Sample the curve for display.
        /// </summary>
        public List<Point3d> Sample(int numSamples, SubDEvaluator evaluator)
        {
            var points = new float[numSamples * 3];

            if (!NativeCore.latent_curve_sample(_handle, evaluator.Handle, numSamples, points))
            {
                throw new InvalidOperationException("Curve sampling failed");
            }

            var result = new List<Point3d>(numSamples);
            for (int i = 0; i < numSamples; i++)
            {
                result.Add(new Point3d(
                    points[i * 3],
                    points[i * 3 + 1],
                    points[i * 3 + 2]
                ));
            }
            return result;
        }

        /// <summary>
        /// Get the arc length of the curve.
        /// </summary>
        public double GetArcLength(SubDEvaluator evaluator)
        {
            if (!NativeCore.latent_curve_arc_length(_handle, evaluator.Handle, out float length))
            {
                throw new InvalidOperationException("Arc length computation failed");
            }
            return length;
        }

        /// <summary>
        /// Convert sampled curve to a Rhino polyline curve.
        /// </summary>
        public PolylineCurve ToPolylineCurve(int numSamples, SubDEvaluator evaluator)
        {
            var points = Sample(numSamples, evaluator);
            return new PolylineCurve(points);
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
                    NativeCore.latent_curve_destroy(_handle);
                    _handle = IntPtr.Zero;
                }
                _disposed = true;
            }
        }

        ~SurfaceCurve()
        {
            Dispose(false);
        }
    }
}
