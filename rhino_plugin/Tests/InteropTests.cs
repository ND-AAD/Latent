// rhino_plugin/Tests/InteropTests.cs
using System;
using System.Collections.Generic;
using NUnit.Framework;
using Rhino.Geometry;
using Latent.Interop;

namespace Latent.Tests
{
    [TestFixture]
    public class InteropTests
    {
        // Note: These tests require the native library to be available.
        // They may be skipped in CI if the library isn't built.

        private static bool NativeLibraryAvailable()
        {
            try
            {
                var handle = NativeCore.latent_evaluator_create();
                if (handle != IntPtr.Zero)
                {
                    NativeCore.latent_evaluator_destroy(handle);
                    return true;
                }
            }
            catch (DllNotFoundException)
            {
            }
            return false;
        }

        [Test]
        public void Evaluator_CreateAndDestroy()
        {
            if (!NativeLibraryAvailable())
            {
                Assert.Ignore("Native library not available");
            }

            using var evaluator = new SubDEvaluator();
            Assert.IsFalse(evaluator.IsInitialized);
        }

        [Test]
        public void Evaluator_Initialize_WithTestSubD()
        {
            if (!NativeLibraryAvailable())
            {
                Assert.Ignore("Native library not available");
            }

            // Create a simple box SubD
            var box = new Box(Plane.WorldXY, new Interval(-1, 1), new Interval(-1, 1), new Interval(-1, 1));
            var mesh = Mesh.CreateFromBox(box, 1, 1, 1);
            var subd = SubD.CreateFromMesh(mesh);

            using var evaluator = new SubDEvaluator();
            evaluator.Initialize(subd);

            Assert.IsTrue(evaluator.IsInitialized);
            Assert.AreEqual(6, evaluator.FaceCount);
        }

        [Test]
        public void Evaluator_EvaluatePoint()
        {
            if (!NativeLibraryAvailable())
            {
                Assert.Ignore("Native library not available");
            }

            var box = new Box(Plane.WorldXY, new Interval(-1, 1), new Interval(-1, 1), new Interval(-1, 1));
            var mesh = Mesh.CreateFromBox(box, 1, 1, 1);
            var subd = SubD.CreateFromMesh(mesh);

            using var evaluator = new SubDEvaluator();
            evaluator.Initialize(subd);

            var point = evaluator.EvaluatePoint(0, 0.5, 0.5);

            Assert.IsFalse(double.IsNaN(point.X));
            Assert.IsFalse(double.IsNaN(point.Y));
            Assert.IsFalse(double.IsNaN(point.Z));
        }

        [Test]
        public void Evaluator_EvaluatePointAndNormal()
        {
            if (!NativeLibraryAvailable())
            {
                Assert.Ignore("Native library not available");
            }

            var box = new Box(Plane.WorldXY, new Interval(-1, 1), new Interval(-1, 1), new Interval(-1, 1));
            var mesh = Mesh.CreateFromBox(box, 1, 1, 1);
            var subd = SubD.CreateFromMesh(mesh);

            using var evaluator = new SubDEvaluator();
            evaluator.Initialize(subd);

            var (point, normal) = evaluator.EvaluatePointAndNormal(0, 0.5, 0.5);

            Assert.IsFalse(double.IsNaN(point.X));
            Assert.IsFalse(double.IsNaN(normal.X));
            Assert.Greater(normal.Length, 0.9); // Should be normalized
        }

        [Test]
        public void Evaluator_ProjectPoint_RoundTrip()
        {
            if (!NativeLibraryAvailable())
            {
                Assert.Ignore("Native library not available");
            }

            var box = new Box(Plane.WorldXY, new Interval(-1, 1), new Interval(-1, 1), new Interval(-1, 1));
            var mesh = Mesh.CreateFromBox(box, 1, 1, 1);
            var subd = SubD.CreateFromMesh(mesh);

            using var evaluator = new SubDEvaluator();
            evaluator.Initialize(subd);

            // Evaluate a known point
            var point = evaluator.EvaluatePoint(0, 0.5, 0.5);

            // Project it back
            var param = evaluator.ProjectPoint(point);

            Assert.IsTrue(param.IsValid);
            Assert.AreEqual(0, param.FaceId);
            Assert.AreEqual(0.5, param.U, 0.01);
            Assert.AreEqual(0.5, param.V, 0.01);
        }

        [Test]
        public void SurfaceCurve_CreateAndDestroy()
        {
            if (!NativeLibraryAvailable())
            {
                Assert.Ignore("Native library not available");
            }

            var controlPoints = new List<ParametricPoint>
            {
                new ParametricPoint(0, 0.0, 0.5),
                new ParametricPoint(0, 1.0, 0.5)
            };

            using var curve = new SurfaceCurve(controlPoints, CurveType.Linear, 1);

            Assert.AreEqual(2, curve.PointCount);
            Assert.AreEqual(CurveType.Linear, curve.Type);
            Assert.AreEqual(1, curve.Degree);
        }

        [Test]
        public void SurfaceCurve_Sample()
        {
            if (!NativeLibraryAvailable())
            {
                Assert.Ignore("Native library not available");
            }

            var box = new Box(Plane.WorldXY, new Interval(-1, 1), new Interval(-1, 1), new Interval(-1, 1));
            var mesh = Mesh.CreateFromBox(box, 1, 1, 1);
            var subd = SubD.CreateFromMesh(mesh);

            using var evaluator = new SubDEvaluator();
            evaluator.Initialize(subd);

            var controlPoints = new List<ParametricPoint>
            {
                new ParametricPoint(0, 0.0, 0.5),
                new ParametricPoint(0, 1.0, 0.5)
            };

            using var curve = new SurfaceCurve(controlPoints, CurveType.Linear, 1);

            var samples = curve.Sample(10, evaluator);

            Assert.AreEqual(10, samples.Count);
            foreach (var pt in samples)
            {
                Assert.IsFalse(double.IsNaN(pt.X));
            }
        }

        [Test]
        public void SurfaceCurve_ToPolylineCurve()
        {
            if (!NativeLibraryAvailable())
            {
                Assert.Ignore("Native library not available");
            }

            var box = new Box(Plane.WorldXY, new Interval(-1, 1), new Interval(-1, 1), new Interval(-1, 1));
            var mesh = Mesh.CreateFromBox(box, 1, 1, 1);
            var subd = SubD.CreateFromMesh(mesh);

            using var evaluator = new SubDEvaluator();
            evaluator.Initialize(subd);

            var controlPoints = new List<ParametricPoint>
            {
                new ParametricPoint(0, 0.0, 0.5),
                new ParametricPoint(0, 1.0, 0.5)
            };

            using var curve = new SurfaceCurve(controlPoints, CurveType.Linear, 1);

            var polyline = curve.ToPolylineCurve(10, evaluator);

            Assert.IsNotNull(polyline);
            Assert.AreEqual(10, polyline.PointCount);
        }

        [Test]
        public void CurvatureAnalyzer_ComputeCurvature()
        {
            if (!NativeLibraryAvailable())
            {
                Assert.Ignore("Native library not available");
            }

            var box = new Box(Plane.WorldXY, new Interval(-1, 1), new Interval(-1, 1), new Interval(-1, 1));
            var mesh = Mesh.CreateFromBox(box, 1, 1, 1);
            var subd = SubD.CreateFromMesh(mesh);

            using var evaluator = new SubDEvaluator();
            evaluator.Initialize(subd);

            var analyzer = new CurvatureAnalyzer(evaluator);
            var data = analyzer.ComputeCurvature(0, 0.5, 0.5);

            Assert.IsFalse(double.IsNaN(data.K1));
            Assert.IsFalse(double.IsNaN(data.K2));
            Assert.AreEqual((data.K1 + data.K2) / 2, data.MeanH, 0.001);
            Assert.AreEqual(data.K1 * data.K2, data.GaussianK, 0.001);
        }

        [Test]
        public void CurvatureAnalyzer_ComputeCurvatureWithDirections()
        {
            if (!NativeLibraryAvailable())
            {
                Assert.Ignore("Native library not available");
            }

            var box = new Box(Plane.WorldXY, new Interval(-1, 1), new Interval(-1, 1), new Interval(-1, 1));
            var mesh = Mesh.CreateFromBox(box, 1, 1, 1);
            var subd = SubD.CreateFromMesh(mesh);

            using var evaluator = new SubDEvaluator();
            evaluator.Initialize(subd);

            var analyzer = new CurvatureAnalyzer(evaluator);
            var data = analyzer.ComputeCurvatureWithDirections(0, 0.5, 0.5);

            Assert.IsFalse(double.IsNaN(data.K1));
            Assert.IsFalse(double.IsNaN(data.Dir1.X));
            Assert.IsFalse(double.IsNaN(data.Dir2.X));
        }

        [Test]
        public void CurvatureAnalyzer_SampleGrid()
        {
            if (!NativeLibraryAvailable())
            {
                Assert.Ignore("Native library not available");
            }

            var box = new Box(Plane.WorldXY, new Interval(-1, 1), new Interval(-1, 1), new Interval(-1, 1));
            var mesh = Mesh.CreateFromBox(box, 1, 1, 1);
            var subd = SubD.CreateFromMesh(mesh);

            using var evaluator = new SubDEvaluator();
            evaluator.Initialize(subd);

            var analyzer = new CurvatureAnalyzer(evaluator);
            var (meanH, gaussianK) = analyzer.SampleCurvatureGrid(0, 5);

            Assert.AreEqual(5, meanH.GetLength(0));
            Assert.AreEqual(5, meanH.GetLength(1));
            Assert.IsFalse(double.IsNaN(meanH[2, 2]));
        }
    }
}
