// rhino_plugin/Display/CurveSampler.cs
using System;
using System.Collections.Generic;
using Rhino.Geometry;
using Latent.Geometry;
using Latent.Interop;

namespace Latent.Display
{
    /// <summary>
    /// Samples parametric curves on SubD limit surfaces for display.
    /// </summary>
    public class CurveSampler
    {
        private readonly SubDEvaluator _evaluator;

        // Adaptive sampling thresholds
        private const double AngleThresholdDegrees = 5.0;
        private const int MinSamples = 10;
        private const int MaxSamples = 200;
        private const int AdaptiveDepth = 4;

        public CurveSampler(SubDEvaluator evaluator)
        {
            _evaluator = evaluator ?? throw new ArgumentNullException(nameof(evaluator));
        }

        /// <summary>
        /// Clamp a value to a range (for .NET Framework 4.8 compatibility).
        /// </summary>
        private static int Clamp(int value, int min, int max)
        {
            if (value < min) return min;
            if (value > max) return max;
            return value;
        }

        /// <summary>
        /// Clamp a double value to a range.
        /// </summary>
        private static double Clamp(double value, double min, double max)
        {
            if (value < min) return min;
            if (value > max) return max;
            return value;
        }

        /// <summary>
        /// Sample an edge to a polyline of 3D points.
        /// </summary>
        /// <param name="edge">The edge to sample</param>
        /// <param name="numSamples">Number of samples (uniform)</param>
        /// <returns>List of 3D points on the surface</returns>
        public List<Point3d> SampleEdge(Edge edge, int numSamples)
        {
            if (edge == null)
                throw new ArgumentNullException(nameof(edge));

            numSamples = Clamp(numSamples, MinSamples, MaxSamples);

            // Get control points from the edge
            var controlPoints = edge.GetControlPoints();
            if (controlPoints == null || controlPoints.Count < 2)
            {
                return new List<Point3d>();
            }

            // Try to create a SurfaceCurve for proper parametric sampling
            try
            {
                using (var curve = new SurfaceCurve(controlPoints, edge.CurveType, edge.Degree))
                {
                    return curve.Sample(numSamples, _evaluator);
                }
            }
            catch
            {
                // Fallback to linear interpolation if curve creation fails
                return SampleLinear(edge, numSamples);
            }
        }

        /// <summary>
        /// Sample an edge adaptively based on curvature.
        /// </summary>
        /// <param name="edge">The edge to sample</param>
        /// <param name="baseSamples">Base number of samples</param>
        /// <returns>List of 3D points with adaptive refinement</returns>
        public List<Point3d> SampleEdgeAdaptive(Edge edge, int baseSamples = 20)
        {
            if (edge == null)
                throw new ArgumentNullException(nameof(edge));

            var controlPoints = edge.GetControlPoints();
            if (controlPoints == null || controlPoints.Count < 2)
            {
                return new List<Point3d>();
            }

            // Try to create a SurfaceCurve for parametric evaluation
            SurfaceCurve curve;
            try
            {
                curve = new SurfaceCurve(controlPoints, edge.CurveType, edge.Degree);
            }
            catch
            {
                // Fallback to linear sampling
                return SampleLinear(edge, baseSamples);
            }

            try
            {
                // Start with uniform parameter samples
                var parameters = new List<double>();
                for (int i = 0; i <= baseSamples; i++)
                {
                    parameters.Add(i / (double)baseSamples);
                }

                // Adaptively refine based on curvature
                parameters = RefineAdaptive(curve, parameters, AdaptiveDepth);

                // Evaluate all parameters to 3D points
                var points = new List<Point3d>(parameters.Count);
                foreach (var t in parameters)
                {
                    var point = curve.Evaluate(t, _evaluator);
                    points.Add(point);
                }

                return points;
            }
            finally
            {
                curve.Dispose();
            }
        }

        /// <summary>
        /// Sample a parametric curve directly.
        /// </summary>
        public List<Point3d> SampleCurve(SurfaceCurve curve, int numSamples)
        {
            if (curve == null)
                throw new ArgumentNullException(nameof(curve));

            numSamples = Clamp(numSamples, MinSamples, MaxSamples);

            // Use the native sampling method
            return curve.Sample(numSamples, _evaluator);
        }

        /// <summary>
        /// Sample a linear edge between two vertices by interpolating in parameter space.
        /// </summary>
        private List<Point3d> SampleLinear(Edge edge, int numSamples)
        {
            var vertices = edge.Vertices;
            if (vertices == null || vertices.Count < 2)
            {
                return new List<Point3d>();
            }

            var start = vertices[0].Position;
            var end = vertices[vertices.Count - 1].Position;

            var points = new List<Point3d>(numSamples + 1);

            // Handle same-face case (simple interpolation)
            if (start.FaceId == end.FaceId)
            {
                for (int i = 0; i <= numSamples; i++)
                {
                    double t = i / (double)numSamples;
                    double u = start.U + t * (end.U - start.U);
                    double v = start.V + t * (end.V - start.V);

                    try
                    {
                        var point = _evaluator.EvaluatePoint(start.FaceId, u, v);
                        points.Add(point);
                    }
                    catch
                    {
                        // Skip invalid evaluation points
                    }
                }
            }
            else
            {
                // Face-crossing case: sample in two segments
                // First half on start face, second half on end face
                int midSample = numSamples / 2;

                // First segment: start face
                for (int i = 0; i <= midSample; i++)
                {
                    double t = i / (double)midSample;
                    // Interpolate from start toward face boundary (0.5, 0.5 is typical)
                    double u = start.U + t * (0.5 - start.U);
                    double v = start.V + t * (0.5 - start.V);

                    try
                    {
                        var point = _evaluator.EvaluatePoint(start.FaceId, u, v);
                        points.Add(point);
                    }
                    catch
                    {
                        // Skip invalid points
                    }
                }

                // Second segment: end face
                for (int i = 1; i <= numSamples - midSample; i++)
                {
                    double t = i / (double)(numSamples - midSample);
                    // Interpolate from face boundary toward end
                    double u = 0.5 + t * (end.U - 0.5);
                    double v = 0.5 + t * (end.V - 0.5);

                    try
                    {
                        var point = _evaluator.EvaluatePoint(end.FaceId, u, v);
                        points.Add(point);
                    }
                    catch
                    {
                        // Skip invalid points
                    }
                }
            }

            return points;
        }

        /// <summary>
        /// Refine parameter list adaptively based on angle deviation.
        /// </summary>
        private List<double> RefineAdaptive(SurfaceCurve curve, List<double> parameters, int depth)
        {
            if (depth <= 0 || parameters.Count >= MaxSamples)
                return parameters;

            var refined = new List<double>();
            refined.Add(parameters[0]);

            bool addedPoints = false;

            for (int i = 0; i < parameters.Count - 1; i++)
            {
                double t0 = parameters[i];
                double t1 = parameters[i + 1];
                double tMid = (t0 + t1) / 2.0;

                var p0 = curve.Evaluate(t0, _evaluator);
                var p1 = curve.Evaluate(t1, _evaluator);
                var pMid = curve.Evaluate(tMid, _evaluator);

                // Check if midpoint deviates significantly from line
                if (ShouldRefine(p0, pMid, p1))
                {
                    refined.Add(tMid);
                    addedPoints = true;
                }

                refined.Add(t1);
            }

            // Recurse if we added points and haven't reached max depth
            if (addedPoints && refined.Count < MaxSamples)
            {
                return RefineAdaptive(curve, refined, depth - 1);
            }

            return refined;
        }

        /// <summary>
        /// Determine if a segment needs refinement based on angle at midpoint.
        /// </summary>
        private bool ShouldRefine(Point3d p0, Point3d pMid, Point3d p1)
        {
            // Calculate vectors from p0->pMid and pMid->p1
            var v1 = pMid - p0;
            var v2 = p1 - pMid;

            // Skip if either segment is too short
            if (v1.Length < 1e-10 || v2.Length < 1e-10)
                return false;

            // Normalize vectors
            v1.Unitize();
            v2.Unitize();

            // Calculate angle between segments via dot product
            double dot = v1 * v2;
            dot = Clamp(dot, -1.0, 1.0);
            double angleDegrees = Math.Acos(dot) * 180.0 / Math.PI;

            // Refine if angle exceeds threshold (indicates curvature)
            return angleDegrees > AngleThresholdDegrees;
        }
    }
}
