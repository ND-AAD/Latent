// rhino_plugin/Tests/TestHelpers.cs
using System;
using System.Collections.Generic;
using Rhino.Geometry;
using Latent.Geometry;
using Latent.Interop;
using Latent.Analysis;

namespace Latent.Tests
{
    /// <summary>
    /// Helper utilities for integration tests.
    /// </summary>
    public static class TestHelpers
    {
        /// <summary>
        /// Create a simple box SubD for testing.
        /// </summary>
        public static SubD CreateTestBoxSubD()
        {
            var box = new Box(Plane.WorldXY,
                new Interval(-1, 1),
                new Interval(-1, 1),
                new Interval(-1, 1));
            var mesh = Mesh.CreateFromBox(box, 1, 1, 1);
            return SubD.CreateFromMesh(mesh);
        }

        /// <summary>
        /// Create a sphere-like SubD for testing curved surfaces.
        /// </summary>
        public static SubD CreateTestSphereSubD()
        {
            var sphere = new Sphere(Point3d.Origin, 1.0);
            var mesh = Mesh.CreateFromSphere(sphere, 8, 8);
            return SubD.CreateFromMesh(mesh);
        }

        /// <summary>
        /// Create a mock analysis result for testing.
        /// </summary>
        public static AnalysisResultData CreateMockAnalysisResult(int regionCount = 3)
        {
            var result = new AnalysisResultData
            {
                Vertices = new List<VertexData>(),
                Edges = new List<EdgeData>(),
                Regions = new List<RegionData>()
            };

            // Create vertices - 4 per region forming a quad boundary
            for (int i = 0; i < regionCount * 4; i++)
            {
                result.Vertices.Add(new VertexData
                {
                    Id = $"v{i}",
                    Position = new List<double> { 0, (i % 4) * 0.25, (i / 4) * 0.25 },
                    ImplicitPosition = new List<double> { 0, (i % 4) * 0.25, (i / 4) * 0.25 },
                    CreatedBy = "lens",
                    IsPinned = false
                });
            }

            // Create edges connecting vertices
            for (int i = 0; i < regionCount * 4; i++)
            {
                int next = (i + 1) % (regionCount * 4);
                result.Edges.Add(new EdgeData
                {
                    Id = $"e{i}",
                    VertexIds = new List<string> { $"v{i}", $"v{next}" },
                    CurveType = "bezier",
                    Degree = 3,
                    IsPinned = false
                });
            }

            // Create regions with boundaries
            for (int r = 0; r < regionCount; r++)
            {
                result.Regions.Add(new RegionData
                {
                    Id = $"r{r}",
                    BoundaryEdgeIds = new List<string>
                    {
                        $"e{r * 4}", $"e{r * 4 + 1}",
                        $"e{r * 4 + 2}", $"e{r * 4 + 3}"
                    },
                    UnityPrinciple = r == 0 ? "curvature_continuity" : "eigenfunction_nodal",
                    ResonanceScore = 0.85 - (r * 0.1),
                    IsPinned = false
                });
            }

            return result;
        }

        /// <summary>
        /// Verify that a parametric point is valid and within bounds.
        /// </summary>
        public static bool IsValidParametricPoint(ParametricPoint point)
        {
            return point.IsValid &&
                   point.FaceId >= 0 &&
                   point.U >= 0.0 && point.U <= 1.0 &&
                   point.V >= 0.0 && point.V <= 1.0;
        }

        /// <summary>
        /// Assert that two points are approximately equal within tolerance.
        /// </summary>
        public static void AssertPointsEqual(Point3d a, Point3d b, double tolerance = 1e-6)
        {
            var dist = a.DistanceTo(b);
            if (dist > tolerance)
            {
                throw new AssertionException(
                    $"Points differ by {dist}: ({a.X:F6}, {a.Y:F6}, {a.Z:F6}) vs ({b.X:F6}, {b.Y:F6}, {b.Z:F6})");
            }
        }

        /// <summary>
        /// Assert that two parametric points are approximately equal.
        /// </summary>
        public static void AssertParametricPointsEqual(
            ParametricPoint a, ParametricPoint b, double tolerance = 1e-4)
        {
            if (a.FaceId != b.FaceId)
            {
                throw new AssertionException(
                    $"Face IDs differ: {a.FaceId} vs {b.FaceId}");
            }
            if (Math.Abs(a.U - b.U) > tolerance || Math.Abs(a.V - b.V) > tolerance)
            {
                throw new AssertionException(
                    $"Parameters differ: ({a.U:F6}, {a.V:F6}) vs ({b.U:F6}, {b.V:F6})");
            }
        }

        /// <summary>
        /// Create a RegionManager populated with mock data.
        /// </summary>
        public static RegionManager CreatePopulatedRegionManager(int regionCount = 3)
        {
            var manager = new RegionManager();
            var result = CreateMockAnalysisResult(regionCount);
            manager.UpdateFromAnalysis(result);
            return manager;
        }

        /// <summary>
        /// Exception for test assertions.
        /// </summary>
        public class AssertionException : Exception
        {
            public AssertionException(string message) : base(message) { }
        }
    }
}
